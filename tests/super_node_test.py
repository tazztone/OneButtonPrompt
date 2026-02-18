import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# sys.path is handled by conftest.py

# Import from the package structure to allow relative imports inside the module to work
try:
    from OneButtonPrompt.OneButtonPromptNodes import OneButtonSuperPrompt, CreatePromptVariant
except ImportError:
    # Fallback for direct execution if conftest hasn't run (though expected to run via pytest)
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(os.path.dirname(current_dir))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from OneButtonPrompt.OneButtonPromptNodes import OneButtonSuperPrompt, CreatePromptVariant

class TestSuperPromptNode(unittest.TestCase):
    def test_node_inputs(self):
        """Verify INPUT_TYPES exists and contains required keys."""
        inputs = OneButtonSuperPrompt.INPUT_TYPES()
        self.assertIn("required", inputs)
        self.assertIn("prompt", inputs["required"])
        self.assertIn("insanitylevel", inputs["required"])
        self.assertIn("superpromptstyle", inputs["required"])

    @patch('OneButtonPrompt.OneButtonPromptNodes.PromptEngine.superprompt')
    def test_execution_calls_engine(self, mock_super):
        """Verify the node calls the engine function correctly."""
        mock_super.return_value = "Super prompt content"
        node = OneButtonSuperPrompt()
        result = node.Comfy_OBP_SuperPrompt(insanitylevel=5, prompt="test prompt", superpromptstyle="all", seed=123)
        
        # Verify return structure
        self.assertEqual(result, ("Super prompt content",))
        
        # Verify call arguments
        mock_super.assert_called_once_with(
            insanitylevel=5, 
            prompt="test prompt", 
            seed=123, 
            superpromptstyle="all"
        )

class TestCreatePromptVariantNode(unittest.TestCase):
    def test_node_inputs(self):
        """Verify INPUT_TYPES exists and contains required keys."""
        inputs = CreatePromptVariant.INPUT_TYPES()
        self.assertIn("required", inputs)
        self.assertIn("prompt_input", inputs["required"])
        self.assertIn("optional", inputs)
        self.assertIn("insanitylevel", inputs["optional"])

    @patch('OneButtonPrompt.OneButtonPromptNodes.PromptEngine.create_variant')
    def test_execution_calls_engine(self, mock_variant):
        """Verify the node calls the engine function correctly."""
        mock_variant.return_value = "Varied prompt content"
        node = CreatePromptVariant()
        result = node.Comfy_OBP_PromptVariant(prompt_input="original", insanitylevel=7, seed=456)
        
        # Verify return structure
        self.assertEqual(result, ("Varied prompt content",))
        
        # Verify call arguments
        mock_variant.assert_called_once_with(prompt="original", insanitylevel=7)

if __name__ == '__main__':
    unittest.main()
