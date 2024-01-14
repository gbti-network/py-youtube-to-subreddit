import os


def build_hierarchy(root_dir):
    """
    Given a directory location, this function iterates through all files and folders in that directory creating a
    hierarchical array of files and folders.
    :param root_dir: The directory to start building the hierarchy from
    :return: A list representing the hierarchy of files and folders in root_dir
    """
    hierarchy = []
    for item in os.listdir(root_dir):
        item_path = os.path.join(root_dir, item)
        if os.path.isfile(item_path):
            hierarchy.append(item)
        elif os.path.isdir(item_path):
            hierarchy.append({item: build_hierarchy(item_path)})
    return hierarchy


def filter_hierarchy(hierarchy, ignore_patterns=[], focus_patterns=[], base_path=""):
    """
    Given a hierarchical array of files and folders and two arrays of string patterns (ignore_patterns and focus_patterns),
    this function iterates through the hierarchy and removes any object whose file name or folder name matches one of the
    patterns in ignore_patterns, and/or adds any object whose file name or folder name matches one of the patterns in focus_patterns.

    :param hierarchy: The hierarchical array to filter
    :param ignore_patterns: An array of string patterns to exclude from the hierarchy
    :param focus_patterns: An array of string patterns to selectively include in the hierarchy
    :param base_path: The base path of the current hierarchy for constructing full file paths
    :return: A new hierarchical array with the filtered and/or focused items removed
    """

    filtered_hierarchy = []
    if not hierarchy:
        return filtered_hierarchy

    # Iterate over each item in the hierarchy
    for item in hierarchy:
        # If the item is a file (represented as a string), check if it matches any of the ignore_patterns or focus_patterns
        if isinstance(item, str):
            full_path = os.path.join(base_path, item)
            if not any(pattern in item for pattern in ignore_patterns):
                if not focus_patterns or any(pattern in item for pattern in focus_patterns):
                    filtered_hierarchy.append(full_path)
        # If the item is a folder (represented as a dictionary), recursively filter its contents
        elif isinstance(item, dict):
            for key in item.keys():
                if not any(pattern in key for pattern in ignore_patterns):
                    if not focus_patterns or any(pattern in key for pattern in focus_patterns):
                        # Include all children of this directory
                        filtered_dict = {key: filter_hierarchy(item[key], ignore_patterns, [], os.path.join(base_path, key))}
                        filtered_hierarchy.append(filtered_dict)

    return filtered_hierarchy






def print_hierarchy(hierarchy=[], indent=0):
    """
    Given a hierarchical array of files and folders, this function prints the hierarchy in the desired format and returns
    it as a string.
    :param hierarchy: The hierarchical array to print
    :param indent: The number of spaces to indent each level of the hierarchy
    :return: The hierarchical array as a string
    """
    output = ""
    for item in hierarchy:
        if isinstance(item, str):
            # Remove the path from the file before printing it
            file_name = os.path.basename(item)
            output += f"{' ' * indent}- {file_name}\n"
        elif isinstance(item, dict):
            folder_name = list(item.keys())[0]
            output += f"{' ' * indent}+ {folder_name}/\n"
            output += print_hierarchy(item[folder_name], indent=indent + 2)
    return output


