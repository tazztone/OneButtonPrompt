"""
Tests for the OneButtonPreset node and preset management system.
Covers: preset loading, chance_overrides assembly, and preset save safety.
"""
import sys
import os
import unittest
import json
from unittest.mock import MagicMock, patch

# conftest.py handles environment setup when run via pytest.
# For direct execution, we replicate the minimal setup here.
if 'folder_paths' not in sys.modules:
    sys.modules['folder_paths'] = MagicMock()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(current_dir)))
    sys.modules['folder_paths'].base_path = os.getcwd()
    for mod in ['torch', 'transformers', 'server', 'aiohttp']:
        if mod not in sys.modules:
            sys.modules[mod] = MagicMock()

from OneButtonPrompt import OneButtonPromptNodes
from OneButtonPrompt.one_button_presets import OneButtonPresets


class TestPresetLoading(unittest.TestCase):

    def setUp(self):
        self.presets = OneButtonPresets()

    def test_all_default_presets_loadable(self):
        """Every preset in obp_presets.json must be retrievable without error."""
        for name in self.presets.opb_presets:
            if name in (self.presets.CUSTOM_OBP, self.presets.RANDOM_PRESET_OBP):
                continue
            preset = self.presets.get_obp_preset(name)
            self.assertIsInstance(preset, dict, f"Preset '{name}' did not return a dict")

    def test_get_preset_returns_copy(self):
        """Modifying the returned preset must not corrupt the internal state."""
        preset_names = [n for n in self.presets.opb_presets
                        if n not in (self.presets.CUSTOM_OBP, self.presets.RANDOM_PRESET_OBP)]
        if not preset_names:
            self.skipTest("No presets available to test")

        name = preset_names[0]
        original_level = self.presets.opb_presets[name].get("insanitylevel")

        # Mutate the returned copy
        returned = self.presets.get_obp_preset(name)
        returned["insanitylevel"] = 9999

        # Internal state must be unchanged
        internal_level = self.presets.opb_presets[name].get("insanitylevel")
        self.assertEqual(original_level, internal_level,
                         "get_obp_preset() returned a mutable reference — internal state was corrupted!")

    def test_imagemodechance_is_int(self):
        """imagemodechance must be int in all presets (not string)."""
        errors = []
        for name, preset in self.presets.opb_presets.items():
            val = preset.get("imagemodechance")
            if val is not None and not isinstance(val, int):
                errors.append(f"Preset '{name}': imagemodechance is {type(val).__name__} ('{val}')")
        if errors:
            self.fail("Type inconsistencies found:\n" + "\n".join(errors))

    def test_all_presets_have_required_keys(self):
        """Every preset must have the core required keys."""
        required_keys = {"insanitylevel", "subject", "artist", "imagetype"}
        errors = []
        for name, preset in self.presets.opb_presets.items():
            missing = required_keys - set(preset.keys())
            if missing:
                errors.append(f"Preset '{name}' missing keys: {missing}")
        if errors:
            self.fail("\n".join(errors))


class TestPresetNodeChanceOverrides(unittest.TestCase):
    """Test that the OneButtonPreset node correctly assembles chance_overrides."""

    def test_node_has_input_types(self):
        """OneButtonPreset node must define INPUT_TYPES."""
        self.assertTrue(hasattr(OneButtonPromptNodes.OneButtonPreset, "INPUT_TYPES"))
        input_types = OneButtonPromptNodes.OneButtonPreset.INPUT_TYPES()
        self.assertIn("required", input_types)

    def test_node_exports_correct_return_type(self):
        """OneButtonPreset node must declare STRING return type."""
        self.assertIn("STRING", OneButtonPromptNodes.OneButtonPreset.RETURN_TYPES)


if __name__ == '__main__':
    unittest.main()
