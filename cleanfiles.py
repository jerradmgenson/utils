import os
import sys
import re
import shutil
import json
import argparse
import logging
from pathlib import Path

RULES_DEFAULT = 'rules.json'
TMP_PATH_ROOT = Path('/tmp/cleanfiles')

logger = logging.getLogger(__name__)


def get_clargs():
    description = 'Clean filenames using regular expressions.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('target', type=Path, help='Path to the target directory.')
    parser.add_argument('--rules', type=Path, default=RULES_DEFAULT,
                        help='Path to the rules file.')
    
    parser.add_argument('--silent', action='store_true',
                        help='Silence all output and user prompts.')
    
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
        renamed = []
        for filename in filenames:
            new_name = rename_file(filename, rules)
            if new_name != filename:
                logger.info("Renaming '{}' to '{}'".format(filename, new_name))
                renamed.append(full_path_old)
                full_path_old = os.path.join(dirpath, filename)
                full_path_new = os.path.join(dirpath, new_name)
                shutil.copy2(full_path_old, full_path_new)
                os.remove(full_path_old)

        return renamed

                
def get_rules(path):
    with path.open() as rules_file:
        rules = json.load(rules_file)

    return rules


def configure_logging(clargs):
    if clargs.silent:
        logger.setLevel(logging.ERROR)

    else:
        logger.setLevel(logging.INFO)
        
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

                
def main():
    clargs = get_clargs()
    configure_logging(clargs)    
    rules = get_rules(clargs.rules)
    tmp_path = TMP_PATH_ROOT / clargs.target.name
    logger.info('Copying files to tmp')
    try:
        shutil.copytree(clargs.target, tmp_path)
        renamed = rename_files(tmp_path, rules)
        if not clargs.silent and renamed:
            acceptable = input("Are the above changes acceptable? Enter 'y' or 'n': ")

        if not renamed:
            logger.info('No files to rename')

        elif clargs.silent or acceptable == 'y':
            logger.info('Deleting original files')            
            logger.info('Moving new files from tmp')
            shutil.copytree(tmp_path, clargs.target)
            logger.info('Done')

        else:
            logger.info('Aborting file rename')
            logger.info('Aborted')

    finally:
        shutil.rmtree(tmp_path)

        
if __name__ == '__main__':
    main()
