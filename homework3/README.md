# Задание №3: Разработать инструмент командной строки для для учебного конфигурационного языка

## 1. Общее описание
Этот проект представляет собой инструмент командной строки для учебного конфигурационного
языка, синтаксис которого приведен далее. Этот инструмент преобразует текст из
входного формата в выходной. Синтаксические ошибки выявляются с выдачей
сообщений.

Входной текст на учебном конфигурационном языке принимается из
стандартного ввода. Выходной текст на языке yaml попадает в стандартный вывод.

### Синтаксис языка
+ **Однострочные комментарии:** `REM Это однострочный комментарий`

+ **Многострочные комментарии:** `/+ Это многострочный комментарий +/`
+ **Массивы:** `[ значение, значение, значение, ... ]`
+ **Имена:** `[_a-z]+`
+ **Значения:**
  - Числа.
  - Массивы.

+ **Объявление константы на этапе трансляции:** `var имя значение;`
+ **Вычисление константы на этапе трансляции:** `${имя}`
Результатом вычисления константного выражения является значение.


Все конструкции учебного конфигурационного языка (с учетом их
возможной вложенности) покрыты тестами.

### Архитектура
`homework3`
+ `src`
  + `tests`
      + test_converter.py
  + converter.py


---

---

## 2. Описание всех функций и настроек
### Класс Parser

#### `Parser __init__`
```Python
    def __init__(self, text):
      self.text = text
      self.res_dict = {}
```
- **Описание**: Конструктор класса, инициализирует входной текст и словарь, для хранения данных
- **Параметры**:
  - `text`: входной текст языка
---

#### `parse(self)`
```Python
    def parse(self):
        
        try:
            self.delete_comments()
            self.find_all_constants()
            self.constant_decl()
            self.const_expr()
            self.get_arrays()

            if len(re.findall(r"\S+", self.text)) > 0:
                raise SyntaxError("В тексте обнаружен неверный синтаксис или значения")

        except Exception as e:
            return str(e)
        else:
            print("+" * 20)
            print("Текст преобразован!")
            print("+" * 20)
            return self.make_yaml()
```
- **Описание**: Основная функция обработки (вызывает необходимые методы для обработки текста, обрабатывает ошибки)
---

#### `delete_comments(self)`
```Python
    def delete_comments(self):
        comments = []
        pattern1 = r"/\+(.*?)\+/"
        pattern2 = r"REM(.*?)\n"
        matches1 = re.findall(pattern1, self.text, re.DOTALL)
        matches2 = re.findall(pattern2, self.text)
        if matches1 is not None:
            comments.extend(matches1)
            while len(comments) > 0:
                s = "/+" + comments.pop(0) + "+/"
                self.text = self.text.replace(s, "")

        if matches2 is not None:
            comments.extend(matches2)
            while len(comments) > 0:
                s = "REM" + comments.pop(0) + "\n"
                self.text = self.text.replace(s, "")
```
- **Описание**: Метод для удаления комментариев в тексте языка
---

#### `find_all_constants(self)`
```Python
    def find_all_constants(self):
        pattern = r"var [_a-zA-Z]+"
        matches = re.findall(pattern, self.text)
        for m in matches:
            const = m.split(" ")[1]
            self.res_dict[const] = None
```
- **Описание**: Метод для нахождения всех объявленных констант
---

#### `constant_decl(self)`
```Python
    def constant_decl(self):
        pattern = r"var [_a-zA-Z]+ \d+"
        matches = re.findall(pattern, self.text)
        for m in matches:
            const = m.split(" ")[1]
            val = m.split(" ")[2]
            if self.res_dict[const] is not None:
                raise NameError("Переменная с таким именем была уже объявлена")
            else:
                self.text = self.text.replace(m, "")
                self.res_dict[const] = int(val)
```
- **Описание**: Метод, который сопоставляет объявленным константам значения-числа
---

#### `const_expr(self)`
```Python
    def const_expr(self):
        pattern = r"var [_a-zA-Z]+ \$\{[a-zA-Z_]+\}"
        matches = re.findall(pattern, self.text)
        for m in matches:
            const = m.split(" ")[1]
            val = m.split(" ")[2][2:-1]
            if val in self.res_dict.keys():
                self.text = self.text.replace(m, "")
                self.res_dict[const] = self.res_dict[val]
            else:
                raise NameError("Переменная с таким именем не была объявлена")
```
- **Описание**: Метод, который сопоставляет значения констант со значениями объявленных констант
---

#### `get_arrays(self)`
```Python
    def get_arrays(self):
        pattern = r"var [_a-zA-Z]+ \[.*\]"
        matches = re.findall(pattern, self.text)
        for m in matches:
            array_string = self.validate_values(m)
            evaluated_list = list(ast.literal_eval(array_string))

            const = m.split(" ")[1]
            if self.res_dict[const] is None:
                self.text = self.text.replace(m, "")
                self.res_dict[const] = evaluated_list
            else:
                raise NameError("Переменная с таким именем была уже объявлена")
```
- **Описание**: Метод, который ищет и обрабатывает все массивы
---

#### `validate_values(self, m_string)`
```Python
    def validate_values(self, m_string):
        array_string = m_string[m_string.index("["):]
        if array_string.count("[") != array_string.count("]"):
            raise SyntaxError(f"Некорректный синтаксис в массиве {array_string}")

        val_pattern = r"\$\{[a-zA-Z_]+\}"
        val_matches = re.findall(val_pattern, array_string)
        for v_m in val_matches:
            if v_m[2:-1] not in self.res_dict.keys():
                raise NameError(f"{v_m}: Переменная с таким именем не была объявлена")
            else:
                value = self.res_dict[v_m[2:-1]]
                array_string = array_string.replace(v_m, str(value))

        return array_string
```
- **Описание**: Метод, который валидирует массивы
- **Параметры**:
  - `m_string`: строка-массив, найденная вов входном тексте
---

#### `make_yaml(self)`
```Python
    def make_yaml(self):
        yaml_output = yaml.dump(self.res_dict, sort_keys=True)
        return yaml_output
```
- **Описание**: Метод, который из полученного словаря, получает строку в представлении yaml

---

---

## 3. Описание команд для сборки проекта
Для работы с проектом необходимо иметь установленный Python 3.12

### Запуск проекта
Сначала необходимо перейти в рабочую директорию ```homework2```.
```bash
cd homework3
```

Далее выполняем команду для запуска программы
```bash
python src/converter.py
```

---

---

## 4. Пример использования в виде скриншотов
Пример конфигурации базы данных
![img_1](https://github.com/Ira11111/Configuration_project/blob/images/db_example.bmp)
Пример конфигурации сервера
![img_2](https://github.com/Ira11111/Configuration_project/blob/images/server_example.bmp)

## 5. Результаты прогона тестов
![img_3](https://github.com/Ira11111/Configuration_project/blob/images/tests3.bmp)
