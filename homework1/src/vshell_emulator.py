import argparse
import zipfile


class ShellEmulator:
    def __init__(self, username, fs_path):
        self.username = username
        self.fs_path = fs_path  # путь к файловой системе
        self.current_dir = '/'  # корневая директория
        self.vfs = []
        self.files_data = {}
        self.load_filesystem()  # вызываем метод для загрузки файловой системы

    def load_filesystem(self):
        """Загружает виртуальную файловую систему (архив tar)"""
        with zipfile.ZipFile(self.fs_path, 'r') as zip_file:
            for filename in zip_file.namelist():
                if not filename.endswith('/'):  # дошли до папки
                    self.files_data["/" + filename] = zip_file.read(filename).decode('utf-8')

                self.vfs.append('/'+filename)

    def get_absolute_path(self, path):
        """Преобразует путь в абсолютный относительно текущей директории"""
        if path == "." or path == "./":
            return self.current_dir

        elif path == ".." or path == "../":
            parent = "/".join(self.current_dir.strip("/").split("/")[:-1]) + '/'
            return "/" + parent if parent else "/"

        elif path.startswith("/"):
            return path

        else:
            return self.current_dir + path.strip('/') + '/'

    def get_abs_path_by_dir(self, dir_name):
        """Находит абсолютный путь до директории от текущей"""

        if dir_name == "/":  # если корневая директория возвращаем ее
            return '/'

        else:
            if dir_name[0] != '/':  # если не абсолютный путь
                dir_name = self.current_dir + dir_name  # делаем абсолютный

            dir_name = '/' + dir_name.strip('/') + '/'
            for path in self.vfs:  # проверяем на наличие
                if dir_name == path:
                    return path

        return ''

    def get_dir_contents(self, path):
        """Ищет директории и файлы в данной директории"""
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

    def find_file_by_path(self, path):
        if not path.startswith('/'):
            path = self.current_dir + path

        for p in self.files_data.keys():
            if path == p:
                return p
        else:
            return -1

    def ls(self, path=None):
        """Реализация функции ls - вывод директорий и файлов, хранящихся в текущей директории
         или директории по заданному пути"""
        if path is None:
            p = self.current_dir
        else:
            p = self.get_abs_path_by_dir(path)

        if len(p) > 0:
            contents = self.get_dir_contents(p)

            for elem in contents:
                print(elem)
        else:
            print(f"bash: ls: {path}: No such file or directory")

    def cd(self, path):
        """Меняет текущую директорию"""
        absolute_path = self.get_absolute_path(path)
        print(absolute_path)
        if absolute_path in self.vfs or absolute_path == '/':
            self.current_dir = absolute_path
            print(f"Changed directory to {self.current_dir}")
        else:
            print(f"bash: cd: {path}: No such file or directory")

    def tail(self, path):
        key = self.find_file_by_path(path)
        if key != -1:
            data = self.files_data[key].strip().split('\n')[::-1][:10]

            for elem in data[::-1]:
                print(elem)

        else:
            print(f"File not found: {path}")

    def uniq(self, path):
        key = self.find_file_by_path(path)
        if key != -1:
            data = []
            for elem in self.files_data[key].strip().split('\n'):
                if len(data) == 0: data.append(elem)

                if data[-1] == elem:
                    continue
                else:
                    data.append(elem)

            for elem in data:
                print(elem)

        else:
            print(f"File not found: {path}")

    def exit(self):
        """Завершает работу эмулятора и записывает логи"""
        print("Выход из эмулятора оболочки.")
        exit(0)

    def run(self):
        """Основной цикл работы эмулятора"""
        while True:
            cmd = input(f"{self.username}@emulator:~{self.current_dir}$ ").strip()
            args = cmd.split()
            command = args[0]

            if not command:
                continue

            if command == "ls":
                if len(args) == 1:
                    self.ls()
                else:
                    self.ls(args[1])

            elif command == "cd":
                if len(args) == 1:
                    self.current_dir = "/"
                else:
                    self.cd(args[1])

            elif command == "tail":
                self.tail(args[1])

            elif command == "uniq":
                self.uniq(args[1])

            elif command == "exit":
                self.exit()
            else:
                print("Неизвестная команда")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Эмулятор оболочки")
    parser.add_argument("--username", required=True, help="Имя пользователя для оболочки")
    parser.add_argument("--fs", required=True, help="Путь к виртуальной файловой системе (файл zip)")
    args = parser.parse_args()

    emulator = ShellEmulator(args.username, args.fs)
    emulator.run()
