# Задание №2: Разработать инструмент командной строки для визуализации графа зависимостей

## 1. Общее описание
Этот проект реализует инструмент командной строки для визуализации графа
зависимостей, включая транзитивные зависимости. Зависимости определяются по имени 
пакета языка JavaScript (npm). Для описания графа зависимостей используется 
представление Mermaid. Визуализатор выводит результат в виде сообщения об
успешном выполнении и сохраняет граф в файле формата png.
---
Конфигурационный файл имеет формат json и содержит:
+ Путь к программе для визуализации графов.
+ Имя анализируемого пакета.
+ Путь к файлу с изображением графа зависимостей.
+ Максимальную глубину анализа зависимостей.

Все функции визуализатора зависимостей покрыты тестами

### Архитектура
`homework2`
+ `config`
  + config.json
+ `result` 
  + graph.png
+ `src`
  + `tests`
      + test_dependencies_viz.py
  + dependencies_viz.py
  + get_graph.py
  + install_requirements.py


---

---

## 2. Описание всех функций и настроек

### Программа для нахождения зависимостей и написания файла с разметкой

#### `get_dependencies_current(package_name: str) -> Dict`
```Python
    def get_dependencies_current(package_name: str) -> Dict:
    
      url = f"https://registry.npmjs.org/{package_name}"
      response = requests.get(url=url)
      if response.status_code != 200:
          raise Exception(f"Нет данных о пакете {package_name}")
      else:
          data = response.json()
          latest_version = data['dist-tags']['latest']  # находим последнюю версию
          dependencies = data['versions'][latest_version].get('dependencies', {})  # находим зависимости
          return dependencies
```
- **Описание**: Ищет зависимости (без транзитивных) по имени пакета
- **Параметры**:
  - `package_name`: Название пакета

---

#### `get_all_dependencies(package_name: str, depth: int, dep_dict) -> Optional[Callable]`
```Python
    def get_all_dependencies(package_name: str, depth: int, dep_dict) -> Optional[Callable]:
    
      if depth == 0:
          return None
  
      try:
          packages = get_dependencies_current(package_name)
      except Exception as e:
          print(e)
          return None  # если ошибка в данных заканчиваем рекурсию
  
      else:
          dep_dict[package_name] = packages
          for p in dep_dict[package_name]:
              res = get_all_dependencies(p, depth - 1, dep_dict)
  
              if res is None:
                  continue
```
- **Описание**: Находит рекурсивно все зависимости включая транзитивные
- **Параметры**:
  - `package_name`: Название пакета
  - `depth`: максимальная глубина поиска зависимостей
  - `dep_dict`: словарь, в который записываются данные о зависимостях

---

#### `is_node_in_list(name: str, nodes: List) -> bool`
```Python
    def is_node_in_list(name: str, nodes: List) -> bool:
      for n in nodes:
          if n.content == name:
              return True
      return False
```
- **Описание**: проверяет есть ли вершина(узел) в списке по имени
- **Параметры**:
  - `name`: Название вершины(узла)
  - `nodes`: список всех вершин в графе

---

#### `find_node_by_name(name: str, nodes: List) -> Node`
```Python
    def find_node_by_name(name: str, nodes: List) -> Node:
      for n in nodes:
          if n.content == name:
              return n
```
- **Описание**: находит вершину(узел) графа по ее названию в списке
- **Параметры**:
  - `name`: Название вершины(узла)
  - `nodes`: список всех вершин в графе

---

#### `get_mermaid_str(dependencies: Dict) -> str`
```Python
    def get_mermaid_str(dependencies: Dict) -> str:
   
      nodes: list[Node] = []
      links: list[Link] = []
  
      for package in dependencies.keys():
          if not is_node_in_list(package, nodes):
              nodes.append(Node(package))
          parent = find_node_by_name(package, nodes)
  
          deps = dependencies[package]
          for dep in deps:
              if not is_node_in_list(dep, nodes):
                  nodes.append(Node(dep))
              child = find_node_by_name(dep, nodes)
  
              links.append(Link(parent, child))
  
      script = MermaidDiagram(title="Dependencies graph", nodes=nodes, links=links)
      return str(script)
```
- **Описание**: создает скрипт-строку для создания графа Mermaid
- **Параметры**:
  - `dependencies`: словарь, хранящий данные о зависимостях

---

#### `make_mermaid_file(path:str, script_mermaid: str)`
```Python
   def make_mermaid_file(path:str, script_mermaid: str):
    with open(path, 'w') as file:
        file.write(script_mermaid)
```
- **Описание**: записывает строку с разметкой в файл 
- **Параметры**:
  - `path`: путь до файла с разметкой *.mmd
  - `sript_mermaid`: строка скрипт

---

#### `main()`
```Python
    def main():
         with open("config/config.json", 'r') as conf_data:
        data = json.load(conf_data)

    dependencies = {}
    get_all_dependencies(package_name=data["package_name"], depth=data["max_depth"], dep_dict=dependencies)

    mermaid_script = get_mermaid_str(dependencies)

    mermaid_path = "src/mermaid.mmd"
    output_path = data["graph_output_path"]

    make_mermaid_file(mermaid_path, mermaid_script)

    p_path = data["program_path"]
    os.system(f"python {p_path} --mf {mermaid_path} --of {output_path}")

    print("Программа выполнилась без ошибок!")
```
- **Описание**: Основная функция. Осуществляет вызовы остальных функций и оперирует полученными данными.
- **Параметры**: все параметры получает из файла конфигурации `./config/config.json`

---

### Проргамма для получения изображения графа

#### `get_graph_png(mermaid_str: str, output_path: str) -> None`
```Python
    def get_graph_png(mermaid_path: str, output_file: str) -> None:
      os.system(f"mmdc -i {mermaid_path} output -o {output_file}")
  
      if os.path.exists("src/mermaid.mmd"):
          os.remove("src/mermaid.mmd")
```
- **Описание**: Преобразует файл разметки Mermaid в изображение
- **Параметры**:
  - `mermaid_path`: путь до файла с разметкой mermaid
  - `output_path`: путь к файлу с рисунком графа

---

---

## 3. Описание команд для сборки проекта
Для работы с проектом необходимо иметь установленный Python 3.12

### Запуск проекта
Сначала необходимо перейти в рабочую директорию ```homework2```.
```bash
cd homework2
```

#### Установка зависимостей
В данном проекте используются сторонние библиотеки python, поэтому перед запуском проекта
необходимо запустить скрипт из файла `install_requirements.py`
```bash
python src/install_requirements.py
```


#### Настройки для работы программы
В файле ```./config/config.json``` находиться файл с настройками проекта.
В нем можно поменять:
1. ```prgram_path``` - путь до программы получения изображения
2. ```package_name``` - название пакета менеджера npm, для которого ищутся зависимости
3. ```graph_output_path``` - путь к файлу с расширением .png, в котором будет хранить рисунок полученного графа
4. ```max_depth``` - максимальная глубина зависимостей (текущий пакет считается нулевым уровнем)

Далее запускаем python-скрипт для запуска программы
```bash
python src\dependencies_vis.py
```

---

---

## 4. Пример использования в виде скриншотов
![picture](https://github.com/Ira11111/Configuration_project/blob/images/homework2/cong2(1).jpg)
![picture](https://github.com/Ira11111/Configuration_project/blob/images/homework2/conf2(2).png)
![picture](https://github.com/Ira11111/Configuration_project/blob/images/homework2/conf2(3).png)
![picture](https://github.com/Ira11111/Configuration_project/blob/images/homework2/conf2(4).png)

## 5. Результаты прогона тестов
![test](https://github.com/Ira11111/Configuration_project/blob/images/homework2/conf2(5).png)
![test](https://github.com/Ira11111/Configuration_project/blob/images/homework2/conf2(6).png)
