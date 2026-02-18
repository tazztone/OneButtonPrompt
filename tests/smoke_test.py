import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
obp_root = os.path.dirname(current_dir)

# conftest.py handles mock setup when run via pytest.
# For direct execution, ensure path is set up:
if 'folder_paths' not in sys.modules:
    from unittest.mock import MagicMock
    for mod in ['torch', 'transformers', 'folder_paths', 'server', 'aiohttp']:
        sys.modules[mod] = MagicMock()
    sys.modules['folder_paths'].base_path = os.getcwd()
    sys.path.insert(0, os.path.dirname(obp_root))

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
