import os
import sys
import re
import shutil
import json
import argparse
from pathlib import Path

RULES_DEFAULT = 'rules.json'


def get_clargs():
    description = 'Clean filenames using regular expressions.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('target', type=Path, help='Path to the target directory.')
    parser.add_argument('--rules', type=Path, default=RULES_DEFAULT,
                        help='Path to the rules file.')

    return parser.parse_args()


def rename_file(filename, rules):
    if rules['keep-extension']:
        split_name = filename.split('.')
        filename = '.'.join(split_name[:-1])
        extension = split_name[-1]

    for pattern, repl in rules['patterns'].items():
        filename = re.sub(pattern, repl, filename)
        
    if rules['keep-extension']:
        filename = '.'.join([filename, extension])

    return filename


def rename_files(target, rules):
    for dirpath, _, filenames in os.walk(target):
        for filename in filenames:
            new_name = rename_file(filename, rules)
            if new_name != filename:
                full_path_old = os.path.join(dirpath, filename)
                full_path_new = os.path.join(dirpath, new_name)
                shutil.copy2(full_path_old, full_path_new)
                os.remove(full_path_old)

                
def get_rules(path):
    with path.open() as rules_file:
        rules = json.load(rules_file)

    return rules

                
def main():
    clargs = get_clargs()
    rules = get_rules(clargs.rules)
    rename_files(clargs.target, rules)

if __name__ == '__main__':
    main()
