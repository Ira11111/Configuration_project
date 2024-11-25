import ast
import sys
import yaml
import re



class Parser:
    def __init__(self, text):
        self.text = text
        self.res_dict = {}

    def parse(self):
        """Основная функция обработки"""
        try:
            self.delete_comments()

            self.find_all_constants()
            self.constant_decl()
            self.const_expr()
            self.get_arrays()

            if self.check_text():
                raise SyntaxError("В тексте языка были допущены синтаксические ошибки!")

        except Exception as e:
            return str(e)
        else:
            self.make_yaml()

    def delete_comments(self):
        """Метод для удаления комментариев в тексте языка"""
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
                s = "REM" + comments.pop(0)
                self.text = self.text.replace(s, "")

        if matches2 is not None:
            comments.extend(matches2)

    def find_all_constants(self):
        pattern = r"var [_a-zA-Z]+ .+"
        matches = re.findall(pattern, self.text)
        for m in matches:
            const = m.split(" ")[1]
            self.res_dict[const] = None

    def constant_decl(self):
        """Метод, который сопоставляет объявленным константам значения-числа"""
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

    def const_expr(self):
        """Метод, который сопоставляет значения констант со значениями объявленных констант"""
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

    def get_arrays(self):
        """Метод, который ищет все массивы"""
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



    def validate_values(self, m_string):
        """Метод, который подставляет на место вычисляемых констант значения"""
        array_string = m_string[m_string.index("["):]
        if array_string.count("[") != array_string.count("]"):
            raise SyntaxError(f"Некорректный синтаксис в массиве {array_string}")

        val_pattern = r"\$\{[a-zA-Z_]+\}"
        val_matches = re.findall(val_pattern, array_string)
        for v_m in val_matches:
            if v_m[2:-1] not in self.res_dict.keys():
                raise NameError("Переменная с таким именем не была объявлена")
            else:
                value = self.res_dict[v_m[2:-1]]
                array_string = array_string.replace(v_m, str(value))

        return array_string

    def check_text(self):
        return self.text is None

    def make_yaml(self):
        yaml_string = yaml.dump(self.res_dict, default_flow_style=False)  # default_flow_style=False делает вывод более читаемым
        return yaml_string


# var d 4
# var f ${d}
# var t [1, 2, [${f}, 3], ${d}]

if __name__ == "__main__":

    output = """var d 4\nvar f ${d}\nvar t [1, 2, [${f}, 3], ${d}] REM fds"""
    # while True:
    #     line = sys.stdin.readline()
    #     if not line:
    #         break
    #     output += line

    parser = Parser(output)
    res = parser.parse()
    print(parser.res_dict)
    print(res)
