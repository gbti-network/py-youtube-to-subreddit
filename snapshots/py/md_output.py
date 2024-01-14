import os
import json
import chardet

from snapshots.py.obfuscate_json import obfuscate_sensitive_data

# Define whether to obfuscate sensitive data in JSON files
OBFUSCATE_SENSITIVE_DATA = True

def add_file_blocks(hierarchy, md_file, base_dir):
    """
    Given a hierarchical array of files and folders and an action to perform, this function loops through all the files
    in the hierarchy, starting from the topmost level, and performs the specified action on each file.
    :param hierarchy: The hierarchical array to loop through
    :param action: The action to perform on each file
    :param base_dir: The base directory for the hierarchy
    """
    for item in hierarchy:
        if isinstance(item, str):
            # Perform the action on the file
            file_path = os.path.join(base_dir, item)
            add_file_to_md(file_path, md_file)
        elif isinstance(item, dict):
            folder_name = list(item.keys())[0]
            # Loop through the files in the folder
            for file_item in item[folder_name]:
                if isinstance(file_item, str):
                    # Perform the action on the file
                    #file_path = os.path.join(base_dir, folder_name, file_item)
                    add_file_to_md(file_item, md_file)
                elif isinstance(file_item, dict):
                    # Recursively loop through subfolders
                    add_file_blocks([file_item], md_file, os.path.join(base_dir, folder_name))






def add_file_to_md(file_path, md_file):
    """
    Given a file path and an open markdown file object, this function reads the contents of the file
    and writes it to the markdown file as a code block with syntax highlighting based on the file extension.

    :param file_path: The path to the file to add to the markdown file
    :param md_file: An open markdown file object to write to
    """

    # Get the file or folder name without the path
    name = os.path.basename(file_path)

    # Check if the file or folder exists
    if not os.path.exists(file_path):
        print(f"File or folder not found: {file_path}")
        return

    # Write the file or folder name as a markdown heading
    md_file.write(f"\n## {name}\n")

    # If the item is a folder, write the folder contents recursively
    if os.path.isdir(file_path):
        for item in os.listdir(file_path):
            add_file_to_md(os.path.join(file_path, item), md_file)
    # If the item is a file, write the file contents as a code block
    elif os.path.isfile(file_path):
        # Detect file encoding
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            encoding = chardet.detect(raw_data)['encoding']

        # Read file with detected encoding
        with open(file_path, 'r', encoding=encoding) as f:
            contents = f.read()

            md_file.write("```\n")
            md_file.write(contents)
            md_file.write("\n```\n")

