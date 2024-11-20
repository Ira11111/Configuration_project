import os
from typing import Dict, Optional, Callable, List
import json
import requests
from python_mermaid.diagram import MermaidDiagram, Node, Link


def get_dependencies_current(package_name: str) -> Dict:
    """Ищет зависимости (без транзитивных) по имени пакета"""
    url = f"https://registry.npmjs.org/{package_name}"
    response = requests.get(url=url)
    if response.status_code != 200:
        raise Exception(f"Нет данных о пакете {package_name}")
    else:
        data = response.json()
        latest_version = data['dist-tags']['latest']  # находим последнюю версию
        dependencies = data['versions'][latest_version].get('dependencies', {})  # находим зависимости
        return dependencies


def get_all_dependencies(package_name: str, depth: int, dep_dict) -> Optional[Callable]:
    """Находит рекурсивно все зависимости включая транзитивные
    """

    # если дошли до максимальной глубины - останавливаем рекурсию
    if depth == 0:
        return None

    try:
        packages = get_dependencies_current(package_name)
    except Exception as e:
        print(e)
        return None  # если ошибка в данных заканчиваем рекурсию

    else:
        dep_dict[package_name] = packages
        for p in dep_dict[package_name]:
            res = get_all_dependencies(p, depth - 1, dep_dict)

            # если нет данных о зависимостях или превышена глубина - продолжаем перебирать зависимости на том же уровне
            if res is None:
                continue


def is_node_in_list(name: str, nodes: List) -> bool:
    for n in nodes:
        if n.content == name:
            return True
    return False


def find_node_by_name(name: str, nodes: List) -> Node:
    for n in nodes:
        if n.content == name:
            return n


def get_mermaid_str(dependencies: Dict) -> str:
    """Создаёт строку разметки для графа"""
    nodes: list[Node] = []
    links: list[Link] = []

    for package in dependencies.keys():
        if not is_node_in_list(package, nodes):
            nodes.append(Node(package))
        parent = find_node_by_name(package, nodes)

        deps = dependencies[package]
        for dep in deps:
            if not is_node_in_list(dep, nodes):
                nodes.append(Node(dep))
            child = find_node_by_name(dep, nodes)

            links.append(Link(parent, child))

    script = MermaidDiagram(title="Dependencies graph", nodes=nodes, links=links)
    return str(script)


def make_mermaid_file(path:str, script_mermaid: str):
    with open(path, 'w') as file:
        file.write(script_mermaid)


def main():
    # загружаем конфигурационные данные
    with open("config/config.json", 'r') as conf_data:
        data = json.load(conf_data)

    dependencies = {}
    get_all_dependencies(package_name=data["package_name"], depth=data["max_depth"], dep_dict=dependencies)

    mermaid_script = get_mermaid_str(dependencies)

    mermaid_path = "src/mermaid.mmd"
    output_path = data["graph_output_path"]

    make_mermaid_file(mermaid_path, mermaid_script)

    p_path = data["program_path"]
    os.system(f"python {p_path} --mf {mermaid_path} --of {output_path}")

    print("Программа выполнилась без ошибок!")


if __name__ == "__main__":
    main()
