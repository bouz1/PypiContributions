
import os
from datetime import datetime


######################### INPUTS #######################################
name_of_package = "mltoarduino"
filePackage = "../ML-Model-To-Arduino-Cpp/package/mltoarduino.py"
ReadMeFile ="../ML-Model-To-Arduino-Cpp/package/README.md"
version = "0.0.5"

######################### STRUCTURE ####################################
paths = [
"package",
"package/LICENSE.txt",
"package/README.md",
"package/setup.py",
"package/app",
"package/app/package",
"package/app/__init__.py",
"package/app/README.md",
"package/app/package/src",
"package/app/package/test",
"package/app/package/__init__.py",
"package/app/package/src/__init__.py",
"package/app/package/src/package.py",
"package/app/package/test/__init__.py",
"package/app/package/test/test_package.py",
"package/build",
"package/dist",
"package/run"

]
##########################################################################

try:
    with open (filePackage) as f:
        packageCode= f.read()
except:
    packageCode=""
    
try:
    with open (ReadMeFile) as f:
        ReadMeTxt= f.read()
except:
    ReadMeTxt=""


FUNCS=[]
for l  in packageCode.split('\n'):
    if "def " in l:
        func=l.replace("def ","").split("(")[0]
        if not (ord(func[0])==32 or ord(func[0])==ord('\t')):
            # Avoid "local func"
            
            FUNCS.append(func)



# "package/app/package/__init__.py",
ImportFunctionInit="""
from .src."""+name_of_package+""" import (
"""+\
",".join(FUNCS)+\
"""
)
"""



current_year = str(datetime.now().year)


txtLicence="""MIT License

Copyright (c) 2024 bouz1.github.io

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""".replace("2024",current_year)



txtSetup="""
from setuptools import find_packages, setup

with open("app/README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='"""+name_of_package+"""',
    version='"""+version+"""',
    description="See readMe.ma",
    package_dir={"": "app"},
    packages=find_packages(where="app"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/bouz1/PypiContributions/tree/main/"""+name_of_package+"""',
    author="bouz1.github.io",
    author_email="bozzabb1@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    

    #install_requires=[],
    extras_require={
        "dev": ['pyperclip','pandas','numpy'],

    },
    python_requires=">=3.1",
)
"""



for path in paths:
    oldpath= path
    path=path.replace("package", name_of_package )

    # Check if the path is a directory or a file
    if path.endswith('/'):  # For directories (optional convention)
        os.makedirs(path, exist_ok=True)
    elif '.' in os.path.basename(path):  # Likely a file if it has an extension
        txt=""
        # Ensure the parent directories exist
        if "LICENSE.txt" in path: 
            path=path.replace("LICENSE.txt", "LICENSE" )
            txt=txtLicence
        if "setup.py" in path:
            txt=txtSetup
        if oldpath=="package/app/package/src/package.py" :
            txt = packageCode
        if oldpath=="package/app/package/__init__.py" :
            txt = ImportFunctionInit
        if "README.md" in path:
            txt = ReadMeTxt


                
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # Create the file
        with open(path, 'w') as file:
            file.write(txt)
    else:  # If no trailing '/' or '.' in basename, assume it's a directory
        os.makedirs(path, exist_ok=True)

print("All files and folders created.")

