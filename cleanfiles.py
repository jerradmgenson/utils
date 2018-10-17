import os
import sys
import re
import shutil


def stripspecials(directory):
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            split_name = filename.split('.')
            base_name = '.'.join(split_name[:-1])
            extension = split_name[-1]
            new_name = re.sub('[^\w\s]', '', base_name)
            if new_name != base_name:
                full_path_old = os.path.join(dirpath, filename)
                full_path_new = '.'.join((new_name, extension))
                full_path_new = os.path.join(dirpath, full_path_new)
                shutil.copy2(full_path_old, full_path_new)
                os.remove(full_path_old)


if __name__ == '__main__':
    stripspecials(sys.argv[1])
