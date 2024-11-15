import unittest
from homework1.src import vshell_emulator


class TestVirtualShell(unittest.TestCase):
    # создаем тестируемый объект эмулятора
    emulator = vshell_emulator.VirtualShellEmulator("test_user", "../../config/vfs.zip")

    @classmethod
    def setUpClass(cls):
        # cls.emulator = vshell_emulator.VirtualShellEmulator("test_user", "../../config/vfs.zip")
        # создаем тестовую файловую систему
        cls.emulator.vfs = ["/test_users/", "/test_users/data/", "/test_users/test_tail1.txt",
                            "/test_users/test_tail2.txt", "/test_users/test_uniq1.txt", "/test_users/test_uniq2.txt"]

        cls.emulator.files_data = {
            "/test_users/test_tail1.txt": "1. cat\n2. dog\n3. bird\n4. elephant",

            "/test_users/test_tail2.txt": "1. cat\n2. dog\n3. bird\n4. elephant\n5. cat\n6. dog\n"
                                          "7. bird\n8. elephant\n9. cat\n10. dog\n11. bird\n12. elephant",

            "/test_users/test_uniq1.txt": "banana\napple\nbanana\npear",

            "/test_users/test_uniq2.txt": "banana\nbanana\napple\npear"
        }

    def setUp(self):
        self.emulator.current_dir = '/'

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
            self.emulator.current_dir = "/test_users/data/"
            res = self.emulator.get_absolute_path("..")
            self.assertEqual(res, '/test_users/')

        with self.subTest("back to root"):
            self.emulator.current_dir = "/test_users/"
            res = self.emulator.get_absolute_path("..")
            self.assertEqual(res, '/')

        with self.subTest("can not back"):
            self.emulator.current_dir = "/"
            res = self.emulator.get_absolute_path("..")
            self.assertEqual(res, '/')

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

    def test_ls(self):
        with self.subTest("with wrong path"):
            path = "data/"
            res = self.emulator.ls(path)
            self.assertEqual(res, f"bash: ls: data/: No such file or directory")

        with self.subTest("with right path"):
            path = "test_users/"
            res = self.emulator.ls(path).split('\t')
            ans = ["data", "test_tail1.txt", "test_tail2.txt", "test_uniq1.txt", "test_uniq2.txt"]
            self.assertEqual(set(res), set(ans))

        with self.subTest("current directory"):
            res = self.emulator.ls(self.emulator.current_dir)
            self.assertEqual(res, "test_users")

    def test_cd(self):
        with self.subTest("with wrong path"):
            path = "data/"
            res = self.emulator.cd(path)

            self.assertEqual(res, f"bash: cd: /data/: No such file or directory")
            self.assertEqual('/', self.emulator.current_dir)

        with self.subTest("with right path"):
            path = "test_users/data/"
            res = self.emulator.cd(path)

            self.assertEqual(res, f"Changed directory to /test_users/data/")
            self.assertEqual("/test_users/data/", self.emulator.current_dir)

        with self.subTest("dots"):
            self.emulator.current_dir = '/test_users/'
            path = ".."
            res = self.emulator.cd(path)

            self.assertEqual(res, f"Changed directory to /")
            self.assertEqual("/", self.emulator.current_dir)

    def test_tail(self):
        with self.subTest("with wrong path"):
            path = "data/test_tail1.txt"
            ans = self.emulator.tail(path)
            self.assertEqual(ans, "File not found: data/test_tail1.txt")

        with self.subTest("nothing to do"):
            path = "test_users/test_tail1.txt"
            ans = self.emulator.tail(path)
            self.assertEqual(ans, "1. cat\n2. dog\n3. bird\n4. elephant")

        with self.subTest("with changes"):
            path = "test_users/test_tail2.txt"
            ans = self.emulator.tail(path)
            self.assertEqual(ans,
                             "3. bird\n4. elephant\n5. cat\n6. dog\n7. bird\n8. elephant\n9. cat\n10. dog\n11. "
                             "bird\n12. elephant")

    def test_uniq(self):
        with self.subTest("with wrong path"):
            path = "data/test_tail1.txt"
            ans = self.emulator.uniq(path)
            self.assertEqual(ans, "File not found: data/test_tail1.txt")

        with self.subTest("nothing to do"):
            path = "test_users/test_uniq1.txt"
            ans = self.emulator.uniq(path)
            self.assertEqual(ans, "banana\napple\nbanana\npear")

        with self.subTest("with changes"):
            path = "test_users/test_uniq2.txt"
            ans = self.emulator.uniq(path)
            self.assertEqual(ans, "banana\napple\npear")
