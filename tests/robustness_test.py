import sys
import os
import unittest
import json
from unittest.mock import MagicMock, patch, mock_open

# Mock all heavy dependencies
mock_modules = [
    'torch',
    'transformers',
    'folder_paths',
    'server',
    'aiohttp'
]

for mod in mock_modules:
    sys.modules[mod] = MagicMock()

# Stub for folder_paths
sys.modules['folder_paths'].base_path = os.getcwd()

# Add parent of 'OneButtonPrompt' to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
obp_root = os.path.dirname(current_dir)
parent_dir = os.path.dirname(obp_root)
sys.path.append(parent_dir)

from OneButtonPrompt.build_dynamic_prompt import build_dynamic_prompt

class TestOBPRobustness(unittest.TestCase):

    def test_missing_custom_modes_file(self):
        """Verify the engine doesn't crash if custom_modes.json is missing."""
        # Use side_effect to only mock the specific JSON path
        original_exists = os.path.exists
        def side_effect(path):
            if "custom_modes.json" in path:
                return False
            return original_exists(path)

        with patch('os.path.exists', side_effect=side_effect):
            try:
                result = build_dynamic_prompt(insanitylevel=1)
                self.assertIsInstance(result, (list, tuple))
                self.assertTrue(len(result) > 0)
            except Exception as e:
                self.fail(f"build_dynamic_prompt crashed with missing JSON: {e}")

    def test_malformed_custom_modes_json(self):
        """Verify the engine handles malformed JSON safely."""
        original_open = open
        def side_effect(path, *args, **kwargs):
            if "custom_modes.json" in path:
                return mock_open(read_data='{invalid_json}')()
            return original_open(path, *args, **kwargs)

        with patch('builtins.open', side_effect=side_effect):
            with patch('os.path.exists', return_value=True):
                try:
                    # Logic should catch JSONDecodeError and continue
                    result = build_dynamic_prompt(insanitylevel=1)
                    self.assertIsInstance(result, (list, tuple))
                except Exception as e:
                    self.fail(f"build_dynamic_prompt crashed with malformed JSON: {e}")

    def test_exhaustive_deep_control_overrides(self):
        """Verify all deep control keys actually manifest."""
        custom_config = {
            "prompt_prefix": "PREFIX_MARKER",
            "prompt_suffix": "SUFFIX_MARKER",
            "imagetype": "cybernetic_neon",
            "artists": "futuristic",
            "generate_humanoids": False,
            "prompt_parts": [{"wildcard": "TEST_PART", "chance": "always"}]
        }
        
        result = build_dynamic_prompt(custom_mode_config=custom_config, insanitylevel=1)
        prompt = result[0]
        
        # Note: Depending on where prefix/suffix are added, they might have spaces
        self.assertIn("PREFIX_MARKER", prompt)
        self.assertIn("SUFFIX_MARKER", prompt)
        self.assertIn("TEST_PART", prompt)

    def test_weighting_syntax(self):
        """Verify (wildcard:weight) syntax is correctly applied."""
        custom_config = {
            "prompt_parts": [
                {"wildcard": "HeavyColor", "chance": "always", "weight": 1.75}
            ]
        }
        result = build_dynamic_prompt(custom_mode_config=custom_config, insanitylevel=1)
        self.assertIn("(HeavyColor:1.75)", result[0])

    def test_seed_idempotency(self):
        """Verify identical seed + settings = identical prompt."""
        seed = 42
        res1 = build_dynamic_prompt(seed=seed, insanitylevel=8)
        res2 = build_dynamic_prompt(seed=seed, insanitylevel=8)
        self.assertEqual(res1[0], res2[0], "Seed idempotency failed!")

if __name__ == '__main__':
    print(f"Running Robustness Suite in {obp_root}...")
    unittest.main()
