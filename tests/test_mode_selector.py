import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from OneButtonPrompt.mode_selector import ModeSelector, ModeSelection
from OneButtonPrompt.prompt_config import PromptConfig
from OneButtonPrompt.list_manager import ListManager

class TestModeSelector(unittest.TestCase):
    
    def setUp(self):
        self.lm = MagicMock(spec=ListManager)
        self.imagetypemodelist = ["art blaster mode", "unique art mode", "the tokinator"]
        
    def test_calculate_basic_mode(self):
        cfg = PromptConfig(imagetype="unique art mode")
        res = ModeSelector.calculate(cfg, self.lm, self.imagetypemodelist, False, False)
        
        self.assertTrue(res.specialmode)
        self.assertTrue(res.uniqueartmode)
        self.assertEqual(res.generationmode, "unique art")
        self.assertEqual(res.imagetype, "unique art mode")

    def test_calculate_tokinator(self):
        cfg = PromptConfig(imagetype="the tokinator")
        self.lm.get_list.return_value = ["token1", "token2"]
        
        res = ModeSelector.calculate(cfg, self.lm, self.imagetypemodelist, False, False)
        
        self.assertTrue(res.specialmode)
        self.assertTrue(res.thetokinatormode)
        self.assertEqual(res.token_list, ["token1", "token2"])
        self.lm.get_list.assert_called_with("tokens", skipheader=True)

    @patch('random.randint')
    def test_calculate_random_chance(self, mock_randint):
        # Force random choice to happen
        mock_randint.return_value = 1
        cfg = PromptConfig(imagetype="all", imagemodechance=1)
        
        with patch('random.choice') as mock_choice:
            mock_choice.return_value = "art blaster mode"
            res = ModeSelector.calculate(cfg, self.lm, self.imagetypemodelist, False, False)
            
            self.assertEqual(res.imagetype, "art blaster mode")
            self.assertTrue(res.specialmode)

    def test_calculate_custom_mode_inline(self):
        custom_cfg = {"insanitylevel": 10, "prompt": "custom"}
        cfg = PromptConfig(imagetype="all", custom_mode_config=custom_cfg)
        
        res = ModeSelector.calculate(cfg, self.lm, self.imagetypemodelist, False, False)
        
        self.assertTrue(res.specialmode)
        self.assertTrue(res.custommodeactive)
        self.assertEqual(res.custom_mode_config, custom_cfg)

if __name__ == '__main__':
    unittest.main()
