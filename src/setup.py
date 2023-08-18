from setuptools import setup
import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import traceback
import re

APP = ['find_csv2xls_3.py']  # Replace with the actual name of your script
DATA_FILES = []  # Add any additional data files or resources here
OPTIONS = {
    'argv_emulation': True,
    # Add any additional packages your script uses
    'packages': ['pandas', 'tk'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
