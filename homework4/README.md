# Задание №4: Разработать ассемблер и интерпретатор для учебной виртуальной машины (УВМ)

Для ассемблера необходимо разработать читаемое представление команд УВМ.

Ассемблер принимает на вход файл с текстом исходной программы, путь к
которой задается из командной строки. Результатом работы ассемблера является
бинарный файл в виде последовательности байт, путь к которому задается из
командной строки. Дополнительный ключ командной строки задает путь к файлу-
логу, в котором хранятся ассемблированные инструкции в духе списков
“ключ=значение”, как в приведенных далее тестах.


Интерпретатор принимает на вход бинарный файл, выполняет команды УВМ
и сохраняет в файле-результате значения из диапазона памяти УВМ. Диапазон
также указывается из командной строки.


Форматом для файла-лога и файла-результата является xml.
Необходимо реализовать приведенные тесты для всех команд, а также
написать и отладить тестовую программу.

---

### Загрузка константы

| A        | B         | C          | 
|----------|-----------|------------|
| Биты 0—6 | Биты 7—19 | Биты 20—47 | 
| 36       | Адрес     | Константа  |

Размер команды: 6 байт. 

Операнд: поле C. 

Результат: значение в памяти по адресу, которым является поле B.

Тест (A=36, B=736, C=12):

0x24, 0x70, 0xC1, 0x00, 0x00, 0x00

---

### Чтение значения из памяти

| A        | B         | C          | D          |
|----------|-----------|------------|------------| 
| Биты 0—6 | Биты 7—19 | Биты 20—32 | Биты 33—38 |
| 58       | Адрес     | Адрес      | Смещение   |

Размер команды: 6 байт. 

Операнд: значение в памяти по адресу, которым является сумма адреса (значение в памяти по адресу, которым является поле C) и
смещения (поле D). 

Результат: значение в памяти по адресу, которым является поле B.

Тест (A=58, B=405, C=198, D=36):

0xBA, 0xCA, 0x60, 0x0C, 0x48, 0x00

---

### Запись значения в память

| A        | B         | C          | 
|----------|-----------|------------|
| Биты 0—6 | Биты 7—19 | Биты 20—32 | 
| 25       | Адрес     | Адрес      |

Размер команды: 6 байт. 

Операнд: значение в памяти по адресу, которым является поле B. 

Результат: значение в памяти по адресу, которым является поле C.

Тест (A=25, B=919, C=959):

0x99, 0xCB, 0xF1, 0x3B, 0x00, 0x00

---

### Бинарная операция: умножение


| A        | B         | C          | D          |
|----------|-----------|------------|------------| 
| Биты 0—6 | Биты 7—19 | Биты 20—32 | Биты 33—45 |
| 32       | Адрес     | Адрес      | Адрес      |

Размер команды: 6 байт. 

Первый операнд: значение в памяти по адресу, которым является поле D.

Второй операнд: значение в памяти по адресу, которым является поле C.

Результат: значение в памяти по адресу, которым является поле B.

Тест (A=32, B=866, C=372, D=368):

0x20, 0xB1, 0x41, 0x17, 0xE0, 0x02

### Тестовая программа
Выполнить поэлементно операцию умножение над двумя векторами длины 7.
Результат записать в первый вектор.

## 2. Описание всех функций и настроек
### Класс Assembler

#### `Assembler __init__(self, path_to_code, path_to_binary_file, path_to_log)
```Python
    def __init__(self, path_to_code, path_to_binary_file, path_to_log):
        self.binary_file_path = path_to_binary_file
        self.code_path = path_to_code
        self.log_path = path_to_log

        self.bytes = []
        self.log_root = ET.Element("log")
```
- **Описание**: Конструктор класса, инициализирует пути до входного, выходного файлов и логов;
массив для сохранения кодов команд; корень дерева логов
- **Параметры**:
  - `path_to_code`: путь до кода программы
  - `path_to_binary_file`: путь до выходного бинарного файла
  - `path_to_log`: путь до файла с логами
---

#### `load_constant`
```Python
    def load_constant(self, A, B, C):
        # Кодирует команду LOAD_CONSTANT в байты
        if (A != 36):
            raise ValueError("Параметр А должен быть равен 36")
        if not (0 <= B < (1 << 13)):
            raise ValueError("Адрес B должен быть в пределах от 0 до 2^13-1")
        if not (0 <= C < (1 << 28)):
            raise ValueError("Константа C должна быть в пределах от 0 до 2^28-1")

        bits = (C << 20) | (B << 7) | A
        bits = bits.to_bytes(6, byteorder="little")

        element = ET.SubElement(self.log_root, 'LOAD_CONSTANT')
        element.attrib['A'] = str(A)
        element.attrib['B'] = str(B)
        element.attrib['C'] = str(C)
        element.text = bits.hex()

        return bits

```
- **Описание**: функция для кодирования операции загрузки константы в память
- - **Параметры**:
  - `А`: код команды
  - `В`: адрес в памяти
  - `С`: значение константы
---

#### `read_memory`
```Python
    def read_memory(self, A, B, C, D):
        # Кодирует команду READ_MEMORY в байты
        if (A != 58):
            raise ValueError("Параметр А должен быть равен 58")
        if not (0 <= B < (1 << 13)):
            raise ValueError("Адрес B должен быть в пределах от 0 до 2^13-1")
        if not (0 <= C < (1 << 13)):
            raise ValueError("Адрес C должен быть в пределах от 0 до 2^13-1")
        if not (0 <= D < (1 << 6)):
            raise ValueError("Адрес D должен быть в пределах от 0 до 2^6-1")

        bits = (D << 33) | (C << 20) | (B << 7) | A
        bits = bits.to_bytes(6, byteorder="little")

        element = ET.SubElement(self.log_root, 'READ_MEMORY')
        element.attrib['A'] = str(A)
        element.attrib['B'] = str(B)
        element.attrib['C'] = str(C)
        element.attrib['D'] = str(D)
        element.text = bits.hex()

        return bits

```
- **Описание**: функция для кодирования операции чтения константы из памяти
- - **Параметры**:
  - `А`: код команды
  - `В`: адрес памяти
  - `С`: адрес памяти
  - `D`: смещение для адреса
  - 
---

#### `write_memory`
```Python
    def write_memory(self, A, B, C):
        # Кодирует команду WRITE_MEMORY в байты
        if (A != 25):
            raise ValueError("Параметр А должен быть равен 25")
        if not (0 <= B < (1 << 13)):
            raise ValueError("Адрес B должен быть в пределах от 0 до 2^13-1")
        if not (0 <= C < (1 << 13)):
            raise ValueError("Адрес C должен быть в пределах от 0 до 2^13-1")

        bits = (C << 20) | (B << 7) | A
        bits = bits.to_bytes(6, byteorder="little")

        element = ET.SubElement(self.log_root, 'WRITE_MEMORY')
        element.attrib['A'] = str(A)
        element.attrib['B'] = str(B)
        element.attrib['C'] = str(C)
        element.text = bits.hex()

        return bits

```
- **Описание**: функция для кодирования операции записи константы в память
- - **Параметры**:
  - `А`: код команды
  - `В`: адрес в памяти
  - `С`: адрес в памяти
---

#### `multiply`
```Python
    def multiply(self, A, B, C, D):
        # Кодирует команду MUL в байты
        if (A != 32):
            raise ValueError("Параметр А должен быть равен 32")
        if not (0 <= B < (1 << 13)):
            raise ValueError("Адрес B должен быть в пределах от 0 до 2^13-1")
        if not (0 <= C < (1 << 13)):
            raise ValueError("Адрес C должен быть в пределах от 0 до 2^13-1")
        if not (0 <= D < (1 << 13)):
            raise ValueError("Адрес D должен быть в пределах от 0 до 2^13-1")

        bits = (D << 33) | (C << 20) | (B << 7) | A
        bits = bits.to_bytes(6, byteorder="little")

        element = ET.SubElement(self.log_root, 'MUL')
        element.attrib['A'] = str(A)
        element.attrib['B'] = str(B)
        element.attrib['C'] = str(C)
        element.attrib['D'] = str(D)
        element.text = bits.hex()

        return bits
```
- **Описание**: функция для кодирования операции умножения констант
- - **Параметры**:
  - `А`: код команды
  - `В`: адрес в памяти результата
  - `С`: адрес первого операнда
  - `D`: адрес второго операнда
---

#### `assemble`
```Python
        def assemble(self):
        with open(self.code_path, "rt") as code:
            for line in code:
                line = line.split('\n')[0].strip()
                if not line: continue

                command, *args = line.split(" ")

                if command == "LOAD_CONSTANT":
                    if len(args) != 3:
                        raise SyntaxError(
                            f"{line}\nУ операции загрузки константы должно быть 3 аргумента")

                    self.bytes.append(self.load_constant(int(args[0]), int(args[1]), int(args[2])))

                elif command == "READ_MEMORY":
                    if len(args) != 4:
                        raise SyntaxError(
                            f"{line}\nУ операции чтении из памяти должно быть 4 аргумента")

                    self.bytes.append(self.read_memory(int(args[0]), int(args[1]), int(args[2]), int(args[3])))

                elif command == "WRITE_MEMORY":
                    if len(args) != 3:
                        raise SyntaxError(
                            f"{line}\nУ операции чтении из памяти должно быть 3 аргумента")

                    self.bytes.append(self.write_memory(int(args[0]), int(args[1]), int(args[2])))

                elif command == "MUL":
                    if len(args) != 4:
                        raise SyntaxError(
                            f"{line}\nУ операции умножения должно быть 4 аргумента")

                    self.bytes.append(self.multiply(int(args[0]), int(args[1]), int(args[2]), int(args[3])))

                else:
                    raise SyntaxError(f"{line}\nНеизвестная команда")

        self.to_binary_file()

        log_data = ET.tostring(self.log_root, encoding="unicode", method="xml").encode()
        dom = xml.dom.minidom.parseString(log_data)
        log = f'<?xml version="1.0" encoding="utf-8"?>\n' + dom.toprettyxml(newl="\n")[23:]
        with open(self.log_path, 'w', encoding='utf-8') as f:
            f.write(log)

```
- **Описание**: Считывает входной файл с кодом и обрабатывает команды в байты
---

#### `to_binary_file`
```Python
    def to_binary_file(self):
        with open(self.binary_file_path, "wb") as binary:
            for byte in self.bytes:
                binary.write(byte)
```
- **Описание**: записывает результат кодирования в выходной файл
---

### Класс Interpreter

#### `__init__(self, path_to_binary_file, left_boundary, right_boundary, path_to_result_file)
```Python
    def __init__(self, path_to_binary_file, left_boundary, right_boundary, path_to_result_file):
        self.result_path = path_to_result_file
        self.boundaries = (left_boundary, right_boundary) # порядковые номера крайних левого и правого регистров
        # (адрес ячеек памяти)
        self.registers = [0] * (right_boundary - left_boundary + 1) # количество регистров для команды

        with open(path_to_binary_file, 'rb') as binary_file:
            self.byte_code = int.from_bytes(binary_file.read(), byteorder="little")
```
- **Описание**: Конструктор класса, инициализирует путь логов; границы ячеек памяти
и считывает кодировки команд для исполнения
- **Параметры**:
  - `path_to_binary_file`: путь до кода программы
  - `left_boundary`: крайняя правая граница памяти
  - `right_boundary`: крайняя левая граница файла
  - `path_to_result_file`: путь до файла с логами
---

#### `load_constant`
```Python
    def load_constant(self):
        B = self.byte_code & ((1 << 13) - 1)
        self.byte_code >>= 13
        C = self.byte_code & ((1 << 28) - 1)
        self.byte_code >>= 28 
        if not (self.boundaries[0] <= B <= self.boundaries[1]): 
            raise ValueError(
                "В бинарном файле присутствуют невалидные данные: обращение к ячейки памяти по адресу вне диапазона")

        self.registers[B] = C

```
- **Описание**: функция для выполнения операции загрузки константы в память
---

#### `read_memory`
```Python
    def read_memory(self):
       B = self.byte_code & ((1 << 13) - 1)
        self.byte_code >>= 13
        C = self.byte_code & ((1 << 13) - 1)
        self.byte_code >>= 13
        D = self.byte_code & ((1 << 6) - 1)
        self.byte_code >>= 15

        operand_address = C + D 

        if not (self.boundaries[0] <= B <= self.boundaries[1]):
            raise ValueError(
                "В бинарном файле присутствуют невалидные данные: обращение к ячейки памяти по адресу вне диапазона")
        if not (self.boundaries[0] <= operand_address <= self.boundaries[1]):
            raise ValueError(
                "В бинарном файле присутствуют невалидные данные: обращение к ячейки памяти по адресу вне диапазона")

        self.registers[B] = self.registers[operand_address]

```
- **Описание**: функция для выполнения операции чтения константы из памяти

---

#### `write_memory`
```Python
    def write_memory(self):
        B = self.byte_code & ((1 << 13) - 1)
        self.byte_code >>= 13

        C = self.byte_code & ((1 << 13) - 1)
        self.byte_code >>= 28

        if not (self.boundaries[0] <= B <= self.boundaries[1]):
            raise ValueError(
                "В бинарном файле присутствуют невалидные данные: обращение к ячейки памяти по адресу вне диапазона")
        if not (self.boundaries[0] <= C <= self.boundaries[1]):
            raise ValueError(
                "В бинарном файле присутствуют невалидные данные: обращение к ячейки памяти по адресу вне диапазона")

        self.registers[C] = self.registers[B]

```
- **Описание**: функция для выполнения операции записи константы в память
---

#### `mul
```Python
    def mul(self):
        B = self.byte_code & ((1 << 13) - 1)
        self.byte_code >>= 13

        C = self.byte_code & ((1 << 13) - 1)
        self.byte_code >>= 13

        D = self.byte_code & ((1 << 13) - 1)
        self.byte_code >>= 15

        if not (self.boundaries[0] <= B <= self.boundaries[1]):
            raise ValueError(
                "В бинарном файле присутствуют невалидные данные: обращение к ячейки памяти по адресу вне диапазона")
        if not (self.boundaries[0] <= C <= self.boundaries[1]):
            raise ValueError(
                "В бинарном файле присутствуют невалидные данные: обращение к ячейки памяти по адресу вне диапазона")
        if not (self.boundaries[0] <= D <= self.boundaries[1]):
            raise ValueError(
                "В бинарном файле присутствуют невалидные данные: обращение к ячейки памяти по адресу вне диапазона")

        self.registers[B] = self.registers[C] * self.registers[D]
```
- **Описание**: функция для выполнения операции умножения констант
---

#### `interpret`
```Python
    def interpret(self):
        while self.byte_code != 0:
            a = self.byte_code & ((1 << 7) - 1) # крайние справа 7 битов, соответствующие значению А
            self.byte_code >>= 7 # убираем значение А из битов

            match a:
                case 36:
                    self.load_constant()
                case 58:
                    self.read_memory()
                case 25:
                    self.write_memory()
                case 32:
                    self.mul()
                case _:
                    raise ValueError("В бинарном файле содержатся невалидные данные: неверный байт-код")

        self.make_result()
```
- **Описание**: Выборка команды по ее коду
---

#### `make_result`
```Python
    def make_result(self):
        result_root = ET.Element("result")
        for pos, register in enumerate(self.registers, self.boundaries[0]):
            if (register != 0):
                element = ET.SubElement(result_root, "register")
                element.attrib['address'] = str(pos)
                element.text = str(register)

        log_data = ET.tostring(result_root, encoding="unicode", method="xml").encode()
        dom = xml.dom.minidom.parseString(log_data)
        log = f'<?xml version="1.0" encoding="utf-8"?>\n' + dom.toprettyxml(newl="\n")[23:]
        with open(self.result_path, 'w', encoding='utf-8') as f:
            f.write(log)
```
- **Описание**: записывает результат выполнения команд в файл логов
---

---

## 3. Описание команд для сборки проекта
Для работы с проектом необходимо иметь установленный Python 3.12
Также необходимо написать файл *.asm с командами для выполнения

### Запуск проекта
Сначала необходимо перейти в рабочую директорию ```homework4```.
```bash
cd homework4
```

Выполняем команду для кодирования команд
```bash
python src/assembler.py --i <путь до входного файла> --o <путь до выходного бинарного файла> 
--log <путь до файла с логами>
```

Далее выполняем команду для интерпритирования команд
```bash
python src/interpreter.py --i <путь до входного бинарного файла> --o <путь до выходного файла с логами> 
--left_boundary <адрес крайней левой ячейки памяти> --right_boundary <адрес крайней правой ячейки памяти> 
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