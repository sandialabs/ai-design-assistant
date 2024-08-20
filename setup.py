from distutils.core import setup
from setuptools import find_packages
from pathlib import Path
import os
import shutil
import pathlib
import subprocess

home_dir = Path.home()
ada_hidden_dir = os.path.join(home_dir , '.ada')

if os.path.exists(ada_hidden_dir):
    if os.path.isdir(ada_hidden_dir):
        shutil.rmtree(ada_hidden_dir)
    else:
        os.remove(ada_hidden_dir)

shutil.copytree(os.path.join('ada','ui','UI_Files'), ada_hidden_dir)

from sys import platform
if platform == "linux" or platform == "linux2":
    raise ValueError('Linux not currently supported')
elif platform == "darwin":
    f = open(str(home_dir) + '/.zshenv', 'r')
    zshenvStr = f.read()
    f.close()
    if 'export PATH_TO_ADA' not in zshenvStr:
        f = open(str(home_dir) + '/.zshenv', 'a')
        f.write('\n')
        f.write('# Adding path to ADA\n')
        f.write('export PATH_TO_ADA="%s"\n'%(str(pathlib.Path(__file__).parent.resolve()) + os.sep))
        f.close()

    subprocess.call(['chmod 777 buildESP.sh'], shell=True)
    subprocess.call(['source buildESP.sh'], shell=True)

elif platform == "win32":
    raise ValueError('Windows not currently supported')


LONG_DESCRIPTION = """
This is an AI assisted design interface for airfoils
"""

LICENSE = """
No License
"""

setup(
    name="ada",
    description="Package AI assisted design of airfoils",
    author="Cody Karcher",
    author_email="cody.karcher@gmail.com",
    url="https://github.com/codykarcher",
    install_requires= ['numpy','scipy','pandas','openai','llama-index','matplotlib','pint','pypdf', 'natsort','PyICU','mpi4py'] , #["numpy", "scipy", "pandas", "matplotlib", "jsmin", "scikit-learn", "dill","cvxopt"],
    version="0.0.0",
    packages=find_packages(),
    license=LICENSE,
    long_description=LONG_DESCRIPTION,
)
