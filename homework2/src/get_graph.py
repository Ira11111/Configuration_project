import argparse
import os


def get_graph_png(mermaid_path: str, output_file: str) -> None:
    """Преобразует строку разметки в изображение
    """
    os.system(f"/usr/local/bin/mmdc -i {mermaid_path} output -o {output_file} --puppeteerConfigFile config/graph_config.json")

    if os.path.exists("src/mermaid.mmd"):
        os.remove("src/mermaid.mmd")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Эмулятор оболочки")
    parser.add_argument("--mf", required=True, help="путь до файла с разметкой")
    parser.add_argument("--of", required=True, help="путь до файла  с изображением")
    args = parser.parse_args()
    get_graph_png(args.mf, args.of)
