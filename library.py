import os
import shutil
import re

def make_folder(folder, empty=False):
    if os.path.exists(folder) and empty: shutil.rmtree(folder)
    if not os.path.exists(folder): os.makedirs(folder)


def get_files(folder):
    contents = os.listdir(folder)
    files = []
    for entry in contents:
        full_path = os.path.join(folder, entry)
        if os.path.isfile(full_path): files.append(entry)
    return files


def extract_numbers(file_list):
    numbers = []
    pattern = '\d+'
    for file_name in file_list:
        matches = re.findall(pattern, file_name)
        match = matches[-1]
        match = int(match)
        numbers.append(match)
    if numbers == []: numbers = [-1]
    numbers.sort()
    return numbers

