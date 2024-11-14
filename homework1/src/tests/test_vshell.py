import unittest
from homework1.src import vshell_emulator


class TestVirtualShell(unittest.TestCase):
    # создаем тестируемый объект эмулятора
    emulator = vshell_emulator.VirtualShellEmulator("test_user", "../../config/vfs.zip")

    @classmethod
    def setUpClass(cls):
        # создаем тестовую файловую систему
        cls.emulator.vfs = ["/test_users/", "/test_users/data", "/test_users/test_tail1.txt",
                            "/test_users/test_tail2.txt", "/test_users/test_uniq1.txt", "/test_users/test_uniq2.txt"]

        cls.emulator.files_data = {
            "/test_users/test_tail1.txt": "1. cat\n2. dog\n3. bird\n4. elephant",

            "/test_users/test_tail2.txt": "1. cat\n2. dog\n3. bird\n4. elephant\n5. cat\n6. dog\n "
                                          "7. bird\n8. elephant\n9. cat\n10. dog\n11. bird\n12. elephant",

            "/test_users/test_uniq1.txt": "banana\napple\nbanana\npear",

            "/test_users/test_uniq2.txt": "banana\nbanana\napple\npear"
        }

    def test_get_absolute_path(self):
        with self.subTest("with path"):
            path = "test/data"
            res = self.emulator.get_absolute_path(path)
            self.assertEqual(res, "/test/data/")

        with self.subTest("stay"):
            path = "."
            res = self.emulator.get_absolute_path(path)
            self.assertEqual(res, self.emulator.current_dir)

        with self.subTest("back"):
            self.emulator.current_dir = "/test_users/data"
            res = self.emulator.get_absolute_path("..")
            self.assertEqual(res, '/test_users/')

        with self.subTest("root"):
            self.emulator.current_dir = "/test_users/"
            res = self.emulator.get_absolute_path("/")
            self.assertEqual(res, '/')

    def test_get_abs_path_by_dir(self):
        with self.subTest("relative path"):
            path = "test_users/data"
            res = self.emulator.get_absolute_path(path)
            self.assertEqual(res, "/test_users/data/")

        with self.subTest("abs path"):
            path = "/test_users/data/"
            res = self.emulator.get_absolute_path(path)
            self.assertEqual(res, "/test_users/data/")

    def test_get_dir_contents(self):
        with self.subTest():
            res = self.emulator.get_dir_contents("/")
            ans = set()
            ans.add("test_users")
            self.assertEqual(res, ans)

        with self.subTest():
            res = self.emulator.get_dir_contents("/test_users/")
            ans = set()
            for item in ["data", "test_tail1.txt", "test_tail2.txt", "test_uniq1.txt", "test_uniq2.txt"]:
                ans.add(item)
            self.assertEqual(res, ans)

    def test_find_file_by_path(self):
        with self.subTest("wrong file"):
            res = self.emulator.find_file_by_path("/test/data.txt")
            self.assertEqual(res, -1)

        with self.subTest("wrong file"):
            res = self.emulator.find_file_by_path("test_users/test_tail1.txt")
            self.assertEqual(res, "/test_users/test_tail1.txt")
