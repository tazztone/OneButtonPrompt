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
current_dir = os.path.dirname(os.path.abspath(__file__)) # .../OneButtonPrompt/tests
obp_root = os.path.dirname(current_dir)                 # .../OneButtonPrompt
parent_dir = os.path.dirname(obp_root)                  # .../custom_nodes
sys.path.append(parent_dir)

print(f"Running execution tests in {obp_root}...")

try:
    from OneButtonPrompt.build_dynamic_prompt import build_dynamic_prompt
    
    # Test 1: Standard generation (previously failing due to NameError/UnboundLocalError)
    print("Test 1: Running standard generation...")
    result = build_dynamic_prompt(insanitylevel=5, forcesubject="all")
    print(f"  Result: {result[0][:50]}...")
    print("SUCCESS: Standard generation passed.")

    # Test 2: Custom Mode generation (inline)
    print("Test 2: Running inline custom mode...")
    custom_config = {
        "prompt_prefix": "Testing prefix",
        "prompt_parts": [{"wildcard": "-color-", "chance": "always"}]
    }
    result = build_dynamic_prompt(custom_mode_config=custom_config)
    print(f"  Result: {result[0][:50]}...")
    print("SUCCESS: Inline custom mode passed.")

except Exception as e:
    print(f"FAILURE during execution test: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("All execution tests passed successfully.")
