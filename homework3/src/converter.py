from lark import Lark, Transformer, v_args
import sys
import yaml

grammar = """
    ?start: expr

    ?expr: const_decl
         | COMMENT
         | COMMENTS

    const_decl: "var " NAME " " value 

    const_expr: "${" NAME "}"

    array: "[" [value ("," value)*] "]"

    ?value: NUMBER
          | const_expr
          | array
    
    COMMENT: "REM" /./
    COMMENTS: "/+" /*/ "+/"
    NAME: /[_a-z]+/
    NUMBER: /[0-9]+/

    %import common.WS
    %import common.NL
    %ignore WS
    %ignore COMMENT
    %ignore COMMENTS
"""


@v_args(inline=True)
class TreeToDict(Transformer):
    """Класс, который трансформирует дерево разбора в словарь python"""
    from_lark = True

    def const_decl(self, name, value):
        return {name: value}

    def const_expr(self, name):
        return name

    def array(self, *items):
        return list(items)

    def value(self, item):
        return item

    def NUMBER(self, token):
        return int(token)

    def NAME(self, token):
        return token.value


parser = Lark(grammar)


# Функция для парсинга и обработки ошибок
def parse_config(text: str):
    try:
        text = "".join(sys.stdin)
        tree = parser.parse(text)
        data = TreeToDict().transform(tree)
        yaml_output = yaml.dump(data, default_flow_style=False, indent=2)
        return yaml_output

    except Exception as exp:
        return f"Ошибка при обработке:\n{str(exp)}"


if __name__ == "__main__":
    output = ""
    while True:
        line = sys.stdin.readline()
        if not line:  # Проверка на пустую строку (EOF)
            break
        output += line
        print(f"Получена строка: {line.strip()}")
        # Обработка строки line
    print(output)