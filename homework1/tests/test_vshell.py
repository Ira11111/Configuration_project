import unittest
from ..src import vshell_emulator


class TestVirtualShell(unittest.TestCase):
    # создаем тестируемый объект эмулятора
    emulator = vshell_emulator.VirtualShellEmulator("test_user", "../config/vfs.zip")

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

