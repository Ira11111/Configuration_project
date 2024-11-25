import unittest
from homework3.src.converter import Parser


class TestParser(unittest.TestCase):

    def test_delete_comments_single_line(self):
        parser = Parser("var x 10 REM This is a comment\n")
        parser.delete_comments()
        self.assertEqual(parser.text, "var x 10 ")

    def test_delete_comments_multi_line(self):
        parser = Parser("var x 10 /+ This is a\n multi-line\n comment +/\n var y 20")
        parser.delete_comments()
        self.assertEqual(parser.text, "var x 10 \n var y 20")

    def test_delete_comments_both(self):
        parser = Parser("REM This is a comment\n var x 10/+ This is a\n multi-line\n comment +/\n var y 20")
        parser.delete_comments()
        self.assertEqual(parser.text, " var x 10\n var y 20")

    def test_find_all_constants(self):
        parser = Parser("var x 10\nvar y 20\nvar z 30\n")
        parser.find_all_constants()
        self.assertEqual(set(parser.res_dict.keys()), {'x', 'y', 'z'})
        self.assertEqual(list(parser.res_dict.values()), [None, None, None])

    def test_constant_decl(self):
        parser = Parser("var x 10\nvar y 20")
        parser.find_all_constants()
        parser.constant_decl()
        self.assertEqual(parser.res_dict, {'x': 10, 'y': 20})

    def test_constant_decl_duplicate(self):
        parser = Parser("var x 10\nvar x 20")
        parser.find_all_constants()
        with self.assertRaises(NameError):
            parser.constant_decl()

    def test_const_expr(self):
        parser = Parser("var x 10\nvar y ${x}\n")
        parser.find_all_constants()
        parser.constant_decl()
        parser.const_expr()
        self.assertEqual(parser.res_dict, {'x': 10, 'y': 10})

    def test_const_expr_undefined(self):
        parser = Parser("var y ${x}")
        parser.find_all_constants()
        with self.assertRaises(NameError):
            parser.const_expr()

    def test_get_arrays(self):
        parser = Parser("var x [1, 2, 3]")
        parser.find_all_constants()
        parser.get_arrays()
        self.assertEqual(parser.res_dict, {'x': [1, 2, 3]})

    def test_get_arrays_with_variables(self):
        parser = Parser("var a 10\nvar x [1, ${a}, 3]")
        parser.find_all_constants()
        parser.constant_decl()
        parser.get_arrays()
        self.assertEqual(parser.res_dict, {'a': 10, 'x': [1, 10, 3]})

    def test_get_arrays_invalid_syntax(self):
      parser = Parser("var x [[1,2], [3,4]")
      parser.find_all_constants()
      with self.assertRaises(SyntaxError):
        parser.get_arrays()

    def test_get_arrays_undefined_variable(self):
        parser = Parser("var x [1, ${y}, 3]")
        parser.find_all_constants()
        with self.assertRaises(NameError):
            parser.get_arrays()
