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
