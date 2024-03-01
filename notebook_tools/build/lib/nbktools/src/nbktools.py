import os
import re
import json 
import numpy as np
import json

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

               
def merge_ntks(inp_paths, out_path):
    """
    Merges Jupyter notebook files from input paths into a single notebook file and saves it to the output path.

    Args:
        inp_paths (list): List of input paths to the Jupyter notebook files.
        out_path (str): Output path the merged notebook file will be saved.

    Returns:
        None
    """
    # List to store JSON contents of input notebooks
    json_list=[]

    # Iterate over input paths and read JSON contents
    for inp in inp_paths:
        with open(inp, encoding="utf-8") as f:
            # Append JSON contents to the list
            json_list.append(json.loads(f.read()))
            f.close()

    # List to store cells from all input notebooks
    cells=[]

    # Extract cells from each JSON object in the list
    for x in json_list:
        cells+=x['cells']

    # Metadata from the first input notebook
    metadata0=json_list[0]['metadata']

    # Create a new JSON object with merged cells
    new_json=json_list[0]
    new_json['cells']=cells

    # Write the new JSON object to the output file
    with open(out_path, 'w') as f: 
        f.write(json.dumps(new_json))
        f.close()

    # Print 'Done' after successful merging
    print('Done')


def auto_tab_conten(ntk_inp_name, ntk_out_name, update=False, level=3):
    """
    Automatically generates a table of contents (TOC) for a Jupyter notebook and updates or creates it in the notebook file.

    Args:
        ntk_inp_name (str): Input path to the Jupyter notebook file.
        ntk_out_name (str): Output path where the modified notebook file will be saved.
        update (bool, optional): If True, updates the existing TOC in the notebook file. If False, creates a new TOC. Default is False.
        level (int): The title level to be taked in account for the table of contents. Default is 3. 

    Returns:
        None
    """
    # Read the input notebook JSON
    with open(ntk_inp_name, encoding="utf-8") as f:
        notb_js=json.loads(f.read())
        f.close()

    # Remove any existing <a> tags from the notebook cells
    pattern = r'<a class="title_class" id=".*?"></a>'
    for i,x in enumerate(notb_js['cells']):
        try:
            if x['cell_type']=='markdown':
                string=x['source'][0]
                new_string = re.sub(pattern, '', string)
                notb_js['cells'][i]['source'][0]=new_string 
        except : pass

    # Initialize variables for TOC generation
    titile1_id=0
    table=[]

    # Iterate over notebook cells to find titles and generate TOC entries
    for i,x in enumerate(notb_js['cells']):
        hash_level=''

        # Iterate over different heading levels to find titles
        for k in range(level):
            hash_level+='#'
            try:
                if x['cell_type']=='markdown':
                    # Split the source into lines and extract the first word (hash)
                    hash_=x['source'][0].split(' ')[0]
                    if hash_==hash_level:
                        titile1_id+=1
                        id_='title_'+str(titile1_id)
                        title_=x['source'][0]
                        title_=title_.split('\n')[0]
                        title_2=title_+ ' <a class="title_class" id="'+id_+'"></a>'
                        title_without_hash=' '.join(title_.split(' ')[1:])
                        # Generate TOC entry for the title
                        table.append(k*'  '+'* [' +  title_without_hash+']'+ '(#'+ id_+')')
                        notb_js['cells'][i]['source'][0]=title_2
            except: pass

    # Construct the table of contents content
    Table_contents='# Table of contents\n '+'\n '.join(table)

    # Update or create the table of contents in the notebook
    if update:
        # Find and update existing Table of Contents cell
        for i,x in enumerate(notb_js['cells']):
                try:
                    if x['cell_type']=='markdown' and '# Table of contents' in x['source'][0]:
                        notb_js['cells'][i]['source']=[Table_contents]
                except: pass
    else:
        # Create new Table of Contents cell at the top of the notebook
        cell_id=''.join(np.random.choice(np.arange(0,16), size=37, replace=True).astype(str))
        notb_js['cells']=[{'cell_type': 'markdown',
          'id': cell_id,
          'metadata': {},
          'source': [Table_contents]}]+notb_js['cells']

    # Write the modified notebook JSON to the output file
    with open(ntk_out_name, 'w') as f: 
        f.write(json.dumps(notb_js))
        f.close()
    print('Done')




import time
import types
import pandas as pd
import subprocess

def library_versions(disVersions=True, SaveFile=True,all_lib=True):
    """
    Function to retrieve the versions of imported libraries and optionally display them and/or save them to a file.

    Parameters:
    - disVersions (bool): If True, displays the library versions. Default is True.
    - SaveFile (bool): If True, saves the library versions to a file. Default is True.

    Returns:
    - None
    """

   # Get the current time in seconds since the epoch
    current_time = time.time()

    # Convert the current time to the desired string format
    formatted_time = time.strftime("%y_%m_%d_%H_%M_%S", time.localtime(current_time))

    # Create the directory if it doesn't exist
    directory="library_versions"
    if not os.path.exists("library_versions"):
        os.makedirs("library_versions")

    # File name with the actual time as part of the name 
    file_name=r"library_versions/Lib_Vers_"+formatted_time+".txt"
        
    if all_lib:
        # Execute the command and save the output to the file
        subprocess.run(['pip', 'list'], stdout=open(file_name, 'w'))
        print('Done')
        return None 

    # get libraries and version as pandas series
    dic={}
    for name, val in list(globals().items()):
        if isinstance(val, types.ModuleType):
            try:
                dic[val.__name__]=val.__version__
            except: 
                dic[val.__name__]='NaN'
    # dictionary to pd.Series
    dic=pd.Series(dic).sort_values()
    
    if disVersions: 
        display(dic)
                
    if SaveFile:
        
        # Save file
        dic.to_csv(file_name,header=False)
