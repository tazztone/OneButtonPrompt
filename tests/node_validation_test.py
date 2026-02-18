import sys
import os
import unittest
from unittest.mock import MagicMock

# conftest.py handles mock setup when run via pytest.
# For direct execution, ensure path is set up:
if 'folder_paths' not in sys.modules:
    for mod in ['torch', 'transformers', 'folder_paths', 'server', 'aiohttp']:
        sys.modules[mod] = MagicMock()
    sys.modules['folder_paths'].base_path = os.getcwd()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(current_dir)))

# Import the module
from OneButtonPrompt import OneButtonPromptNodes

class TestNodeValidation(unittest.TestCase):
    
    def test_all_node_defaults_in_lists(self):
        """Verifies that for every node, every COMBO input's default value exists in its choices list."""
        mappings = OneButtonPromptNodes.NODE_CLASS_MAPPINGS
        errors = []
        
        for node_name, node_class in mappings.items():
            if not hasattr(node_class, "INPUT_TYPES"):
                continue
                
            input_types = node_class.INPUT_TYPES()
            for group_name in ["required", "optional"]:
                if group_name not in input_types:
                    continue
                
                for param_name, param_def in input_types[group_name].items():
                    # param_def is usually (type, {config}) or (list, {config})
                    if isinstance(param_def, tuple) and len(param_def) >= 2:
                        choices = param_def[0]
                        config = param_def[1]
                        
                        # Only check if it's a list (COMBO widget)
                        if isinstance(choices, list):
                            default_val = config.get("default")
                            if default_val is not None:
                                if default_val not in choices:
                                    errors.append(
                                        f"Node '{node_name}', Param '{param_name}': "
                                        f"Default value '{default_val}' NOT FOUND in choices list (size {len(choices)}). "
                                        f"First 5 choices: {choices[:5]}"
                                    )
        
        if errors:
            self.fail("\n" + "\n".join(errors))

if __name__ == '__main__':
    unittest.main()
