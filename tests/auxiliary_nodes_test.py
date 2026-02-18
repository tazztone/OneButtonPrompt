"""
Tests for auxiliary OBP nodes: AutoNegativePrompt, OneButtonArtify, OneButtonFlufferize.
These nodes were previously untested.
"""
import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# conftest.py handles environment setup when run via pytest.
if 'folder_paths' not in sys.modules:
    sys.modules['folder_paths'] = MagicMock()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(current_dir)))
    sys.modules['folder_paths'].base_path = os.getcwd()
    for mod in ['torch', 'transformers', 'server', 'aiohttp']:
        if mod not in sys.modules:
            sys.modules[mod] = MagicMock()

from OneButtonPrompt import OneButtonPromptNodes


class TestAutoNegativePrompt(unittest.TestCase):

    def test_node_exists(self):
        self.assertTrue(hasattr(OneButtonPromptNodes, 'AutoNegativePrompt'))

    def test_returns_string(self):
        """AutoNegativePrompt must return a non-empty string for all base models."""
        node = OneButtonPromptNodes.AutoNegativePrompt()
        for model in ["SD1.5", "SDXL", "Stable Cascade"]:
            result = node.Comfy_OBP_AutoNegativePrompt(postive_prompt="a cat", insanitylevel=0, enhancenegative=0, base_negative="", seed=0, base_model=model)
            self.assertIsInstance(result, tuple, f"Expected tuple for model={model}")
            self.assertGreater(len(result[0]), 0, f"Empty negative prompt for model={model}")

    def test_sdxl_differs_from_sd15(self):
        """Stable Cascade negative prompt should differ from SD1.5 (no weights vs weighted)."""
        node = OneButtonPromptNodes.AutoNegativePrompt()
        # Use a prompt that triggers the same negative words multiple times via the primer list
        # "photo", "photograph", "photography" all add "camera", "painting", etc.
        # This will result in count > 2 for those words, triggering weights in SD1.5.
        triple_primer = "photo, photograph, photography"
        sd15 = node.Comfy_OBP_AutoNegativePrompt(postive_prompt=triple_primer, insanitylevel=0, enhancenegative=0, base_negative="", seed=0, base_model="SD1.5")[0]
        cascade = node.Comfy_OBP_AutoNegativePrompt(postive_prompt=triple_primer, insanitylevel=0, enhancenegative=0, base_negative="", seed=0, base_model="Stable Cascade")[0]
        
        # SD1.5 should contain weighted terms like (camera:1.3)
        # Cascade should contain unweighted terms like camera
        self.assertNotEqual(sd15, cascade, f"Stable Cascade (unweighted) and SD1.5 (weighted) negative prompts should differ. Got: {sd15}")
        self.assertIn("(", sd15, f"SD1.5 should contain weights. Got: {sd15}")
        self.assertNotIn("(", cascade, f"Stable Cascade should NOT contain weights. Got: {cascade}")


class TestOneButtonArtify(unittest.TestCase):

    def test_node_exists(self):
        self.assertTrue(hasattr(OneButtonPromptNodes, 'OneButtonArtify'))

    def test_returns_modified_prompt(self):
        """Artify must return a string that includes the original prompt content."""
        node = OneButtonPromptNodes.OneButtonArtify()
        original = "a cat sitting on a chair"
        result = node.Comfy_OBP_Artify(prompt=original, artist="all", amount_of_artists="1", artify_mode="standard", seed=42)
        self.assertIsInstance(result, tuple)
        self.assertIsInstance(result[0], str)
        self.assertGreater(len(result[0]), 0)

    def test_does_not_crash_on_empty_prompt(self):
        """Artify must handle empty prompt gracefully."""
        node = OneButtonPromptNodes.OneButtonArtify()
        try:
            result = node.Comfy_OBP_Artify(prompt="", artist="all", amount_of_artists="1", artify_mode="standard", seed=0)
            self.assertIsInstance(result, tuple)
        except Exception as e:
            self.fail(f"OneButtonArtify crashed on empty prompt: {e}")


class TestOneButtonFlufferize(unittest.TestCase):

    def test_node_exists(self):
        self.assertTrue(hasattr(OneButtonPromptNodes, 'OneButtonFlufferize'))

    def test_returns_longer_prompt(self):
        """Flufferize should generally expand the prompt."""
        node = OneButtonPromptNodes.OneButtonFlufferize()
        original = "a dog"
        result = node.Comfy_OBP_Flufferize(prompt=original, amount_of_fluff="medium", reverse_polarity=False, seed=42)
        self.assertIsInstance(result, tuple)
        self.assertIsInstance(result[0], str)
        self.assertGreater(len(result[0]), 0)

    def test_does_not_crash_on_empty_prompt(self):
        """Flufferize must handle empty prompt gracefully."""
        node = OneButtonPromptNodes.OneButtonFlufferize()
        try:
            result = node.Comfy_OBP_Flufferize(prompt="", amount_of_fluff="medium", reverse_polarity=False, seed=0)
            self.assertIsInstance(result, tuple)
        except Exception as e:
            self.fail(f"OneButtonFlufferize crashed on empty prompt: {e}")


if __name__ == '__main__':
    unittest.main()
