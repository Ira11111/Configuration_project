import unittest
import os

from homework4.src.assembler import Assembler
from homework4.src.interpreter import Interpreter


class TestAssembler(unittest.TestCase):
    def test_load_const(self):
        filename = 'test_file.asm'
        binary_file = 'test_bin.bin'
        log_file = 'test_log.xml'

        with open(filename, 'w') as f:
            f.write("LOAD_CONSTANT 36 736 12")

        assembler = Assembler(filename, binary_file, log_file)
        assembler.assemble()

        os.remove(filename)
        os.remove(binary_file)
        os.remove(log_file)

        bit_res = int('110000010111000000100100', 2)
        bit_res = bit_res.to_bytes(6, byteorder="little")
        self.assertEqual(assembler.bytes[0], bit_res)

    def test_read_memory(self):
        filename = 'test_file.asm'
        binary_file = 'test_bin.bin'
        log_file = 'test_log.xml'

        with open(filename, 'w') as f:
            f.write("READ_MEMORY 58 405 198 36")

        assembler = Assembler(filename, binary_file, log_file)
        assembler.assemble()

        os.remove(filename)
        os.remove(binary_file)
        os.remove(log_file)

        bit_res = int('100100000001100011000001100101010111010', 2)
        bit_res = bit_res.to_bytes(6, byteorder="little")
        self.assertEqual(assembler.bytes[0], bit_res)

    def test_write_memory(self):
        filename = 'test_file.asm'
        binary_file = 'test_bin.bin'
        log_file = 'test_log.xml'

        with open(filename, 'w') as f:
            f.write("WRITE_MEMORY 25 919 959")

        assembler = Assembler(filename, binary_file, log_file)
        assembler.assemble()

        os.remove(filename)
        os.remove(binary_file)
        os.remove(log_file)

        bit_res = int('111011111100011100101110011001', 2)
        bit_res = bit_res.to_bytes(6, byteorder="little")
        self.assertEqual(assembler.bytes[0], bit_res)

    def test_multiply(self):
        filename = 'test_file.asm'
        binary_file = 'test_bin.bin'
        log_file = 'test_log.xml'

        with open(filename, 'w') as f:
            f.write("MUL 32 866 372 368")

        assembler = Assembler(filename, binary_file, log_file)
        assembler.assemble()

        os.remove(filename)
        os.remove(binary_file)
        os.remove(log_file)

        bit_res = int('101110000000010111010000011011000100100000', 2)
        bit_res = bit_res.to_bytes(6, byteorder="little")
        self.assertEqual(assembler.bytes[0], bit_res)

    def test_value_error(self):
        filename = 'test_file.asm'
        binary_file = 'test_bin.bin'
        log_file = 'test_log.xml'

        with open(filename, 'w') as f:
            f.write("LOAD_CONSTANT 10 10 10")

        assembler = Assembler(filename, binary_file, log_file)
        with self.assertRaisesRegex(ValueError, "Параметр А должен быть равен 36"):
            assembler.assemble()

        os.remove(filename)

    def test_syntax_error(self):
        filename = 'test_file.asm'
        binary_file = 'test_bin.bin'
        log_file = 'test_log.xml'

        with open(filename, 'w') as f:
            f.write("MOV 50")

        assembler = Assembler(filename, binary_file, log_file)
        with self.assertRaisesRegex(SyntaxError, "Неизвестная команда"):
            assembler.assemble()

        os.remove(filename)

class TestInterpreter(unittest.TestCase):
    def test_load_const(self):
        filename = 'test_file.bin'
        result_file = 'test_result.xml'

        bits = int('110000010111000000100100', 2)
        bits = bits.to_bytes(6, byteorder="little")
        with open(filename, 'wb') as f:
            f.write(bits)

        interpreter = Interpreter(filename, 0, 4096, result_file)
        interpreter.interpret()

        os.remove(filename)
        os.remove(result_file)

        self.assertEqual(interpreter.registers[736], 12)

    def test_read_memory(self):
        filename = 'test_file.bin'
        result_file = 'test_result.xml'

        bits = int('100100000001100011000001100101010111010', 2)
        bits = bits.to_bytes(6, byteorder="little")
        with open(filename, 'wb') as f:
            f.write(bits)

        interpreter = Interpreter(filename, 0, 9181, result_file)
        interpreter.interpret()

        os.remove(filename)
        os.remove(result_file)

        self.assertEqual(interpreter.registers[405], interpreter.registers[198+36])

    def test_write_memory(self):
        filename = 'test_file.bin'
        result_file = 'test_result.xml'

        bits = int('111011111100011100101110011001', 2)
        bits = bits.to_bytes(6, byteorder="little")
        with open(filename, 'wb') as f:
            f.write(bits)

        interpreter = Interpreter(filename, 0, 9181, result_file)
        interpreter.interpret()

        os.remove(filename)
        os.remove(result_file)

        self.assertEqual(interpreter.registers[959], interpreter.registers[919])

    def test_multiply(self):
        filename = 'test_file.bin'
        result_file = 'test_result.xml'

        bits = int('101110000000010111010000011011000100100000', 2)
        bits = bits.to_bytes(6, byteorder="little")
        with open(filename, 'wb') as f:
            f.write(bits)

        interpreter = Interpreter(filename, 0, 9181, result_file)
        interpreter.interpret()

        os.remove(filename)
        os.remove(result_file)

        self.assertEqual(interpreter.registers[68], 0)

    def test_value_error(self):
        filename = 'test_file.bin'
        result_file = 'test_result.xml'

        bits = int('101110000000010111010000011011000100000000', 2)
        bits = bits.to_bytes(6, byteorder="little")
        with open(filename, 'wb') as f:
            f.write(bits)

        interpreter = Interpreter(filename, 0, 9181, result_file)
        with self.assertRaisesRegex(ValueError, "В бинарном файле содержатся невалидные данные: неверный байт-код"):
            interpreter.interpret()

        os.remove(filename)

        self.assertEqual(interpreter.registers[919], 0)

