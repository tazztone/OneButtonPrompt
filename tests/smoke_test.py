import sys
import os
from unittest.mock import MagicMock

# Create mocks for all heavy dependencies
mock_modules = [
    'torch',
    'transformers',
    'folder_paths',
    'server',
    'aiohttp'
]

for mod in mock_modules:
    sys.modules[mod] = MagicMock()

# Stub for folder_paths specifically as it's used for path building
sys.modules['folder_paths'].base_path = os.getcwd()

# Add parent of 'OneButtonPrompt' to sys.path and treat this dir as a package
# Script is now in tests/, so we need to go up one level to get to OBP root, 
# and one more to get to the package container.
current_dir = os.path.dirname(os.path.abspath(__file__)) # .../OneButtonPrompt/tests
obp_root = os.path.dirname(current_dir)                 # .../OneButtonPrompt
parent_dir = os.path.dirname(obp_root)                  # .../custom_nodes
sys.path.append(parent_dir)

print(f"Running import smoke test in {obp_root}...")

try:
    # Import using the full package path to respect relative imports
    from OneButtonPrompt import OneButtonPromptNodes
    print("SUCCESS: OneButtonPromptNodes imported successfully.")
except Exception as e:
    print(f"FAILURE: OneButtonPromptNodes failed to import: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from OneButtonPrompt import build_dynamic_prompt
    print("SUCCESS: build_dynamic_prompt imported successfully.")
except Exception as e:
    print(f"FAILURE: build_dynamic_prompt failed to import: {e}")
    sys.exit(1)
