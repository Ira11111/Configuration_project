from typing import List, Dict
from langchain_core.runnables.graph_mermaid import draw_mermaid_png
import json
import requests

# repository_url: "https://registry.npmjs.org/"


def get_dependencies_current(package_name: str) -> List:
    """Ищет зависимости (без транзитивных) по имени пакета"""
    ...


def get_all_dependencies(package_name: str) -> Dict:
    """Находит все зависимости включая транзитивные"""
    ...


def get_mermaid_str(dependencies: Dict) -> str:
    """Создаёт строку разметки для графа"""
    ...


def get_graph_png(mermaid_str: str, output_path: str) -> None:
    """Преобразует строку разметки в изображение
    """
    draw_mermaid_png(mermaid_syntax=mermaid_str, output_file_path=output_path)


def main():
    # загружаем конфигурационные данные
    with open("../config/config.json", 'r') as conf_data:
        data = json.load(conf_data)

    get_all_dependencies(data["package_name"])


if __name__ == "__main__":
    main()
