import os
import tempfile
import shutil
import json
from pathlib import Path

# modfieid, from the Google search.... 
def remove_line_from_file(filename, type_to_remove, id_to_remove):
    """
    Removes lines containing a specific string from a file using a temporary file.

    Args:
        filename (str): The path to the original file.
        line_to_remove (str): The substring to search for and remove the containing line.
    """
    # Use tempfile.NamedTemporaryFile to create a temporary file
    # 'w+t' mode for reading/writing text; delete=False prevents immediate deletion
    with tempfile.NamedTemporaryFile(mode='w+t', delete=False, suffix='.tmp', dir=os.path.dirname(filename)) as temp_file:
        with open(filename, 'r') as src_file:
            for line in src_file:
                d = json.loads(line)
                if d["type"] != type_to_remove and d["id"] != id_to_remove:
                    temp_file.write(line)
    
    # Get the name of the temporary file for later use
    temp_filename = temp_file.name

    # After the 'with' blocks, both files are closed.
    # Replace the original file with the temporary file.
    try:
        shutil.replace(temp_filename, filename) # os.replace is also an option
        print(f"Lines containing '{line_to_remove}' have been removed from {filename}.")
    except OSError as e:
        print(f"Error replacing file: {e}")
        # Optionally, clean up the temp file if replacement fails
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

 