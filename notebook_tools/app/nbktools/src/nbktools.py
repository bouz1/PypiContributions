import os

def creat_structure(directories):
    """
    This function creates directories for a given list of directory names.

    Parameters:
    directories (list): A list of directory names as strings.

    Returns:
    None
    """
    # Iterate over each directory in the directories list
    for f in directories:
        try:
            # Try to create the directory
            os.mkdir(f)
            # If successful, print a success message
            print(f, 'created successfully')
        except Exception as e:
            # If an error occurs (e.g., the directory already exists), print the error message
            print(e)

def remove_empty(root=None):
    """
    This function removes all empty directories under a given root directory.

    Parameters:
    root (str): The root directory as a string. If not provided, the current working directory is used.

    Returns:
    None
    """
    # If no root directory is provided, use the current working directory
    if root is None:
        root = os.getcwd()

    # Create a list of all directories under the root that do not contain a '.'
    walk_list = [x[0] for x in os.walk(root) if not('.' in x[0])]
    x0 = walk_list[0]

    try:
        # Determine the maximum depth of the directory structure
        level = max([len(x.replace(x0,'').split('/')) for i, x in enumerate(walk_list[1:])]) - 1
    except: 
        level = 0

    # Iterate over each level of the directory structure
    for i in range(level):
        # For each directory under the root
        for x in list(os.walk(root)):
            # If the directory is empty (i.e., it contains no subdirectories or files)
            if len(x[1]) == len(x[2]) == 0:
                # Remove the directory
                os.rmdir(x[0])
                # Print a message indicating the directory has been removed
                print(x[0].replace(root,''), '=> Removed')
