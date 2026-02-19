import sys
import os
from unittest.mock import MagicMock

# Calculate project root (parent of tests directory)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Add project root to sys.path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Mock ComfyUI dependencies to allow unit tests to run without full environment
for mod in ['torch', 'transformers', 'folder_paths', 'server', 'aiohttp', 'nodes', 'app', 'app.frontend_management', 'utils', 'utils.install_util']:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

# Explicitly mock folder_paths structure
if 'folder_paths' in sys.modules:
    sys.modules['folder_paths'].base_path = os.getcwd()
