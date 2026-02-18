import sys
import os
import unittest
from unittest.mock import MagicMock

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from OneButtonPrompt.enhancer_selector import EnhancerSelector, EnhancerSelection
from OneButtonPrompt.list_manager import ListManager
from OneButtonPrompt.mode_selector import ModeSelection

class TestEnhancerSelector(unittest.TestCase):
    
    def setUp(self):
        self.lm = MagicMock(spec=ListManager)
        # Default mock: all lists exist
        self.lm.get_list.return_value = ["item1"]
        
    def test_calculate_normal_mode(self):
        mode = ModeSelection(imagetype="all", specialmode=False, templatemode=False)
        res = EnhancerSelector.calculate(self.lm, mode)
        
        self.assertTrue(res.generate_artist)
        self.assertTrue(res.generate_outfit)
        self.assertTrue(res.generate_lighting)
        self.assertTrue(res.generate_face)

    def test_calculate_special_mode(self):
        mode = ModeSelection(imagetype="unique art mode", specialmode=True, templatemode=False)
        res = EnhancerSelector.calculate(self.lm, mode)
        
        self.assertFalse(res.generate_artist)
        self.assertFalse(res.generate_lighting)
        self.assertTrue(res.generate_outfit) # Outfits still generate in unique art mode unless templatemode

    def test_calculate_template_mode(self):
        mode = ModeSelection(imagetype="only templates mode", specialmode=True, templatemode=True)
        res = EnhancerSelector.calculate(self.lm, mode)
        
        self.assertFalse(res.generate_artist)
        self.assertFalse(res.generate_outfit)
        self.assertFalse(res.generate_bodytype)

    def test_calculate_tokinator(self):
        mode = ModeSelection(imagetype="the tokinator", specialmode=True, thetokinatormode=True)
        res = EnhancerSelector.calculate(self.lm, mode)
        
        self.assertTrue(res.generate_artist) # Artist is special in tokinator
        self.assertFalse(res.generate_lighting)

if __name__ == '__main__':
    unittest.main()
