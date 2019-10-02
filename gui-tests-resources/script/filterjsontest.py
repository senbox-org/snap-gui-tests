"""
Simply extracts the list of json files in

@author: Martino Ferrari
@email: manda.mgf@gmail.com
"""
import os
import argparse


def __list_json_files__(path):
    for f in os.listdir(path):
        f = os.path.join(path, f)
        if os.path.isfile(f):
            if f.endswith('.json'):
                print(f)
        else:
            __list_json_files__(f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("testspath", help="JSON tests directory path")
    args = parser.parse_args()
    __list_json_files__(args.testspath)
