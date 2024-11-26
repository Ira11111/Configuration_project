import argparse
import xml.dom.minidom
import xml.etree.ElementTree as ET


class Assembler:
    def __init__(self, path_to_code, path_to_binary_file, path_to_log):
        self.binary_file_path = path_to_binary_file
        self.code_path = path_to_code
        self.log_path = path_to_log

        self.bytes = []
        self.log_root = ET.Element("log")

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

    def assemble(self):
        # Считывает входной файл с кодом и обрабатывает команды в байты
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


    def to_binary_file(self):
        with open(self.binary_file_path, "wb") as binary:
            for byte in self.bytes:
                binary.write(byte)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Входной файл (.asm)")
    parser.add_argument("output", help="Выходной файл (.bin)")
    parser.add_argument("-l", "--log", help="Файл лога (.xml)", default=None)
    args = parser.parse_args()

    assembler = Assembler(args.input, args.output, args.log)
    try:
        assembler.assemble()
    except ValueError as e:
        print(e)
    print(f"Ассемблирование выполнено успешно. Выходной файл: {args.output}")