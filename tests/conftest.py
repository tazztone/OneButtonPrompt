"""
Shared pytest fixtures for OneButtonPrompt test suite.
This conftest.py is automatically loaded by pytest for all tests in this directory.
It mocks all heavy ComfyUI/ML dependencies so tests can run standalone.
"""
import sys
import os
import pytest
from unittest.mock import MagicMock

def _setup_obp_environment():
    """Mock heavy dependencies and configure sys.path for OBP imports."""
    mock_modules = ['torch', 'transformers', 'folder_paths', 'server', 'aiohttp']
    for mod in mock_modules:
        if mod not in sys.modules:
            sys.modules[mod] = MagicMock()

    # folder_paths needs a real base_path for CSV loading
    sys.modules['folder_paths'].base_path = os.getcwd()

    # Add the custom_nodes parent dir so `from OneButtonPrompt import ...` works
    current_dir = os.path.dirname(os.path.abspath(__file__))  # .../tests
    obp_root = os.path.dirname(current_dir)                    # .../OneButtonPrompt
    parent_dir = os.path.dirname(obp_root)                     # .../custom_nodes
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    return obp_root, parent_dir

# Run setup at import time so it's available for all collection phases
_OBP_ROOT, _PARENT_DIR = _setup_obp_environment()
