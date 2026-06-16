import os
import shutil


def remove_line_from_large_file(original_file_path, lines_to_remove_condition):
    """
    Copilot - Google wrote this
    Reads a large file line by line, skipping lines that meet a removal condition,
    and writes the rest to a new file.

    :param original_file_path: Path to the input file.
    :param lines_to_remove_condition: A function that takes a line (string)
                                      and returns True if the line should be removed,
                                      False otherwise.
    """
    if not os.path.exists(original_file_path):
        return False

    temp_file_path = original_file_path + '.temp'

    updated = False
    with open(original_file_path, 'r', encoding='utf-8') as in_file, \
            open(temp_file_path, 'w', encoding='utf-8') as out_file:
        for line in in_file:

            if not lines_to_remove_condition(line):
                out_file.write(line)
            else:
                updated = True

    # Replace the original file with the modified one
    shutil.move(temp_file_path, original_file_path)
    return updated

