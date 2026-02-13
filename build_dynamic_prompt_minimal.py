"""
Minimal wrapper for build_dynamic_prompt that avoids torch dependency
Only imports what's needed for analysis
"""

import random
import re
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from csv_reader import *
from random_functions import *
from one_button_presets import OneButtonPresets

OBPresets = OneButtonPresets()

# Mock the superprompter functions to avoid torch import
def one_button_superprompt(*args, **kwargs):
    """Mock function - superprompter disabled for analysis"""
    return ""

def remove_superprompt_bias(*args, **kwargs):
    """Mock function - superprompter disabled for analysis"""
    return args[0] if args else ""

# Now import the main function by executing the file
# We'll read and exec it, skipping the superprompter import
with open('build_dynamic_prompt.py', 'r', encoding='utf-8') as f:
    code = f.read()
    
# Remove the superprompter import lines
code = code.replace('from superprompter.superprompter import *', '# superprompter disabled for analysis')
code = code.replace('from .superprompter.superprompter import *', '# superprompter disabled for analysis')

# Execute the modified code
exec(code, globals())
