# Задание №1: Разработать эмулятор для языка оболочки ОС

## 1. Общее описание
Этот проект представляет собой эмулятор оболочки языка UNIX-подобной ОС, реализованный на Python. 
Все действия пользователя логируются в формате JSON с временными метками. 
Эмулятор поддерживает базовые команды ls, cd и exit, а также следующие команды:
1. tail.
2. uniq.

Эмулятор принимает образ виртуальной файловой системы в виде файла формата
zip. 

Ключами командной строки задаются:
+ Имя пользователя для показа в приглашении к вводу.
+ Путь к архиву виртуальной файловой системы

Все функции эмулятора покрыты тестами, а для каждой из
поддерживаемых команд написано 2 теста.

---

---

## 2. Описание всех функций и настроек
### Класс `VirtualShellEmulator`

#### `__init__(self, username, fs_path)`
```Python
    def __init__(self, username, fs_path):
        self.username = username
        self.fs_path = fs_path 
        self.current_dir = '/' 
        self.vfs = []
        self.files_data = {}
        self.load_filesystem()
```
- **Описание**: Инициализирует эмулятор оболочки.
- **Параметры**:
  - `username`: Имя пользователя для эмулятора.
  - `fs_path`: Путь к архиву tar с виртуальной файловой системой.
- **Поля**:
  - `username`: Имя пользователя для эмулятора.
  - `fs_path`: Путь к архиву tar с виртуальной файловой системой.
  - `current_dir`: корневая директория
  - `vfs`: хранит все возможные абсолютные пути
  - `files_data`: хранит содержимое файлов

---

#### `load_filesystem(self)`
```Python
    def load_filesystem(self):
        with zipfile.ZipFile(self.fs_path, 'r') as zip_file:
            for filename in zip_file.namelist():
                if not filename.endswith('/'):  # дошли до папки
                    self.files_data["/" + filename] = zip_file.read(filename).decode('utf-8')

                self.vfs.append('/' + filename)
```
- **Описание**: Загружает виртуальную файловую систему (архив zip)

---

#### `get_absolute_path(self, path)`
```Python
    def get_absolute_path(self, path):
        if path == "." or path == "./":
            return self.current_dir

        elif path == ".." or path == "../":
            parent = "/".join(self.current_dir.strip("/").split("/")[:-1]) + '/'
            return "/" + parent if parent else "/"

        elif path.startswith("/"):
            return path

        else:
            return self.current_dir + path.strip('/') + '/'
```
- **Описание**: Преобразует путь в абсолютный относительно текущей директории (для команды cd)
- **Параметры**:
  - `path`: Путь к директории/файлу

---

#### `get_abs_path_by_dir(self, dir_name)`
```Python
    def get_abs_path_by_dir(self, dir_name):
        if dir_name == "/":  
            return '/'

        else:
            if dir_name[0] != '/':
                dir_name = self.current_dir + dir_name

            dir_name = '/' + dir_name.strip('/') + '/'
            for path in self.vfs: 
                if dir_name == path:
                    return path

        return ''
```
- **Описание**: Находит абсолютный путь до директории от текущей
- **Параметры**:
  - `dir_name`: Название директории

---

#### `get_dir_contents(self, path)`
```Python
    def get_dir_contents(self, path):
        dir_contents = set()

        for filename in self.vfs:
            if filename.startswith(path):
                if path == '/':
                    dir_contents.add(filename.split('/')[1])

                else:
                    data = filename[len(path):].split('/')
                    if data[0] != '':
                        dir_contents.add(data[0])

        return dir_contents
```
- **Описание**: Ищет директории и файлы в данной директории
- **Параметры**:
  - `path`: путь к директории, в которой ищутся директории и файлы

---

#### `find_file_by_path(self, path)`
```Python
   def find_file_by_path(self, path):
          if not path.startswith('/'):
              path = self.current_dir + path
  
          for p in self.files_data.keys():
              if path == p:
                  return p
          else:
              return -1
```
- **Описание**: Ищет файл по указанному пути, если не находит - возвращает -1
- **Параметры**:
  - `path`: путь к файлу

---

#### `ls(self, path=None)`
```Python
    def ls(self, path=None) -> str:
        if path is None:
            p = self.current_dir
        else:
            p = self.get_abs_path_by_dir(path)

        if len(p) > 0:
            contents = self.get_dir_contents(p)
            ans = "\t".join(contents)
        else:
            ans = f"bash: ls: {path}: No such file or directory"

        return ans
```
- **Описание**: Реализация функции ls - вывод директорий и файлов, хранящихся в текущей директории
                или директории по заданному пути
- **Параметры**:
  - `path`: путь к директории, в которой выводятся директории и файлы. Если аргумент отсутствует,
            используется поле current_dir

---

#### `cd(self, path)`
```Python
    def cd(self, path) -> str:
        absolute_path = self.get_absolute_path(path)
        if absolute_path in self.vfs or absolute_path == '/':
            self.current_dir = absolute_path
            ans = f"Changed directory to {self.current_dir}"
        else:
            ans = f"bash: cd: {path}: No such file or directory"

        return ans
```
- **Описание**: Меняет текущую директорию
- **Параметры**:
  - `path`: путь к директории

---

#### `tail(self, path)`
```Python
    def tail(self, path) -> str:
        key = self.find_file_by_path(path)
        if key != -1:
            data = self.files_data[key].strip().split('\n')[::-1][:10]
            ans = "\n".join(data[::-1])
        else:
            ans = f"File not found: {path}"
        return ans
```
- **Описание**: Реализация команды tail - выводит последние 10 строк файла
- **Параметры**:
  - `path`: путь к файлу

---

#### `uniq(self, path)`
```Python
    def uniq(self, path) -> str:
        key = self.find_file_by_path(path)
        if key != -1:
            data = []
            for elem in self.files_data[key].strip().split('\n'):
                if len(data) == 0: data.append(elem)

                if data[-1] == elem:
                    continue
                else:
                    data.append(elem)
            ans = '\n'.join(data)
        else:
            ans = f"File not found: {path}"

        return ans
```
- **Описание**: Реализация команды uniq - удаляет идущие подряд одинаковые строки в файле
- **Параметры**:
  - `path`: путь к файлу

---

#### `exit(self)`
```Python
    def exit(self):
        print("Выход из эмулятора оболочки.")
        exit(0)
```
- **Описание**: Завершает работу эмулятора

---

#### `run(self)`
```Python
    def run(self):
        while True:
            cmd = input(f"{self.username}@emulator:~{self.current_dir}$ ").strip()
            args = cmd.split()
            command = args[0]

            if not command:
                continue

            if command == "ls":
                if len(args) == 1:
                    ans = self.ls()
                else:
                    ans = self.ls(args[1])
                print(ans)

            elif command == "cd":
                if len(args) == 1:
                    ans = self.current_dir = "/"
                else:
                    ans = self.cd(args[1])
                print(ans)

            elif command == "tail":
                ans = self.tail(args[1])
                print(ans)

            elif command == "uniq":
                ans = self.uniq(args[1])
                print(ans)

            elif command == "exit":
                self.exit()
            else:
                print("Неизвестная команда")
```
- **Описание**: Реализует основной цикл работы эмулятора

---

---
## 3. Описание команд для сборки проекта

## 4. Примеры использования в виде скриншотов 

## 5. Результаты прогона тестов.
