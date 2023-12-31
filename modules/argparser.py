import os, argparse

def is_file(str):
    if len(str) == 0:
        return str
    if os.path.isfile(str):
        return str
    else:
        raise RuntimeError(f"Error: path \"{str}\" doesn't exist.")

parser = argparse.ArgumentParser(prog="main.py", description="yet another simple search engine, a uni project.")
parser.add_argument('files',action="extend", nargs="*", type=is_file, default=[])
parser.add_argument('-j', '--json', action="store", type=is_file, default="")
parser.add_argument('-q', '--query', action="append", type=str, default=[])
parser.add_argument('-c', '--doc-count', action="store", type=int, default=0)
parser.add_argument('-s', '--sentences', action="store_true", default=False)
parser.add_argument('-C', '--clusters', action="store", type=int, default=10)
