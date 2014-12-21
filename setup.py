# -*- coding: utf-8 -*-

from setuptools import setup
from codecs import open
from os import path

import sudoku

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
# with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
#     long_description = f.read()

setup(
    name='SudokuPuzzle',

    version=sudoku.__version__,

    description='Sudoku puzzle generator and solver',
    # long_description=long_description,
    long_description='Sudoku puzzle generator, solver and more.',

    url='https://github.com/pkobrien/sudoku',

    author="Patrick K. O'Brien",
    author_email='patrick.keith.obrien@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Games/Entertainment',
        'Topic :: Games/Entertainment :: Puzzle Games',
    ],

    keywords='sudoku',

    extras_require={
        'test': ['pytest'],
    },
)
