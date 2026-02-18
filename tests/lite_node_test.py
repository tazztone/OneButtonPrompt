import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# conftest.py handles mock setup when run via pytest.
# For direct execution, ensure path is set up:
if 'folder_paths' not in sys.modules:
    for mod in ['torch', 'transformers', 'folder_paths', 'server', 'aiohttp']:
        sys.modules[mod] = MagicMock()
    sys.modules['folder_paths'].base_path = os.getcwd()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(current_dir)))

# Import the module under test
# We need to import OneButtonPromptNodes but mock build_dynamic_prompt inside it?
# Or we can just import the class if we can isolate it.
# OneButtonPromptNodes imports build_dynamic_prompt at top level.
# We can mock it in sys.modules before import? No, it's relative import.

# Strategy: Import OneButtonPromptNodes, then patch build_dynamic_prompt on the module.
from OneButtonPrompt import OneButtonPromptNodes

class TestLiteNode(unittest.TestCase):
    
    @patch('OneButtonPrompt.OneButtonPromptNodes.PromptEngine.generate')
    def test_generate_arguments(self, mock_engine):
        # Setup return value
        mock_engine.return_value = ["test_prompt"]
        
        node = OneButtonPromptNodes.OneButtonPrompt_Simple()
        
        # Test Case 1: All defaults
        node.generate(mode="Standard", insanitylevel=5, base_model="SD1.5", seed=123)
        
        # Verify call args
        # In the new architecture, generate() receives a PromptConfig object.
        args, kwargs = mock_engine.call_args
        cfg = args[0]
        self.assertEqual(cfg.insanitylevel, 5)
        self.assertEqual(cfg.base_model, "SD1.5")
        self.assertEqual(cfg.forcesubject, "all")     # Default from signature
        self.assertEqual(cfg.artists, "all")          # Default from signature
        self.assertEqual(cfg.imagetype, "all")        # Default
        
        # Test Case 2: Overrides
        node.generate(
            mode="Standard", 
            insanitylevel=7, 
            base_model="SDXL", 
            seed=456, 
            artist="Greg Rutkowski", 
            subject="animal", 
            imagetype="Photograph",
            prompt_enhancer="superprompt-v1"
        )
        
        args, kwargs = mock_engine.call_args
        cfg = args[0]
        self.assertEqual(cfg.insanitylevel, 7)
        self.assertEqual(cfg.base_model, "SDXL")
        self.assertEqual(cfg.artists, "Greg Rutkowski")
        self.assertEqual(cfg.forcesubject, "animal")
        self.assertEqual(cfg.imagetype, "Photograph") # Should override default
        self.assertEqual(cfg.prompt_enhancer, "superprompt-v1")

    @patch('OneButtonPrompt.OneButtonPromptNodes.PromptEngine.generate')
    def test_imagetype_override_logic(self, mock_engine):
        mock_engine.return_value = ["test_prompt"]
        node = OneButtonPromptNodes.OneButtonPrompt_Simple()
        
        # Test 3: Custom Mode + Override
        # Assuming "Cyberpunk" is a custom mode key (we can mock custom_modes if needed, 
        # but the node just checks `if mode in custom_modes`. 
        # We can inject a fake custom mode into the module.)
        
        OneButtonPromptNodes.custom_modes["TestMode"] = {"some_config": True}
        
        # Call with TestMode (which implies imagetype="TestMode") BUT override with "Photograph"
        node.generate(
            mode="TestMode", 
            insanitylevel=5, 
            base_model="SD1.5", 
            seed=0, 
            imagetype="Photograph"
        )
        
        args, kwargs = mock_engine.call_args
        cfg = args[0]
        # Assertion: The overridden type "Photograph" should be passed, NOT "TestMode"
        self.assertEqual(cfg.imagetype, "Photograph")
        
        # Also verify custom_mode_config is still passed
        self.assertIsNotNone(cfg.custom_mode_config)

if __name__ == '__main__':
    unittest.main()
