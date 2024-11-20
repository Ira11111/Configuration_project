import argparse
import json
import os
import subprocess
import shlex


def get_graph_png(mermaid_path: str, output_file: str) -> None:
    """Преобразует строку разметки в изображение
    """

    cmd = shlex.split(f"mmdc -i {mermaid_path} -o {output_file} -f png")
    proc = subprocess.Popen(cmd)
    proc.wait()

    # if os.path.exists("mermaid.mmd"):
    #     os.remove("mermaid.mmd")


def main(mermaid_path: str):
    with open("config/config.json", 'r') as conf_data:
        data = json.load(conf_data)

    output_file = data["graph_output_path"]
    get_graph_png(mermaid_path, output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Эмулятор оболочки")
    parser.add_argument("--mf", required=True, help="путь до файла с разметкой")
    args = parser.parse_args()

    main(args.mf)
