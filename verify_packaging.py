
import sys
import os
import types

# 1. Setup Mock Environment for ComfyUI internals
# ComfyUI nodes often import 'server' and 'folder_paths' which only exist in the running app.
module_mock = types.ModuleType("server")
class MockPromptServer:
    class instance:
        class routes:
            @staticmethod
            def get(path):
                def decorator(func):
                    return func
                return decorator
module_mock.PromptServer = MockPromptServer
sys.modules["server"] = module_mock

folder_paths_mock = types.ModuleType("folder_paths")
folder_paths_mock.base_path = os.getcwd()
sys.modules["folder_paths"] = folder_paths_mock

aiohttp_mock = types.ModuleType("aiohttp")
aiohttp_mock.web = types.ModuleType("web")
sys.modules["aiohttp"] = aiohttp_mock

# Add PARENT directory to sys.path so we can import 'OneButtonPrompt' as a package
current_dir = os.getcwd()
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

print(f"Verifying imports for OneButtonPrompt in {current_dir}...")

try:
    # Importing 'OneButtonPrompt' will execute __init__.py with correct package context
    import OneButtonPrompt as obp_init
    print("SUCCESS: OneButtonPrompt package imported correctly.")
    
    if hasattr(obp_init, "NODE_CLASS_MAPPINGS"):
        print(f"SUCCESS: NODE_CLASS_MAPPINGS found with {len(obp_init.NODE_CLASS_MAPPINGS)} nodes.")
    else:
        print("FAILURE: NODE_CLASS_MAPPINGS not found in OneButtonPrompt package")
        sys.exit(1)

except ImportError as e:
    print(f"FAILURE: ImportError during verification: {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAILURE: Unexpected error during verification: {e}")
    sys.exit(1)

print("Verification Passed.")
sys.exit(0)
