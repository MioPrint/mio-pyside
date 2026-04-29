
from setuptools import setup, find_packages
from __version__ import __version__

"""def read_version():
    with open('__version__.py') as file:
        code = compile(file.read(), '__version__.py', 'exec')
        ns = {}
        exec(code, ns)
        return ns['__version__']
"""

setup(

    name= 'miopyside',
    version= __version__,
    author= 'Miodrag Ignjatovic',
    author_email= '',
    description="A collection of reusable PySide6 widgets.",
    url="https://github.com/MioPrint/mio-pyside",

    python_requires=">=3.12",

    install_requires= [
        "PySide6>=6.5",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
    ],

    packages= find_packages(), #(where='src'),
    include_package_data= True,  
    #package_dir= {'': 'src'},

)
