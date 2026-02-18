import sys
import os
import unittest
from unittest.mock import MagicMock

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from OneButtonPrompt.subject_selector import SubjectSelector, SubjectSelection
from OneButtonPrompt.prompt_config import PromptConfig
from OneButtonPrompt.list_manager import ListManager

class TestSubjectSelector(unittest.TestCase):
    
    def setUp(self):
        self.lm = MagicMock(spec=ListManager)
        # Mock get_list to return a non-empty list for common items
        self.lm.get_list.side_effect = lambda name, **kwargs: ["item1"] if name in ["vehicles", "objects", "animals", "locations"] else []
        
    def test_calculate_objects(self):
        cfg = PromptConfig(generate_objects=True, generate_humanoids=False, generate_animals=False, generate_landscapes=False, generate_concepts=False)
        res = SubjectSelector.calculate(cfg, self.lm)
        
        self.assertIn("object", res.main_chooser)
        self.assertIn("-vehicle-", res.object_wildcards)
        self.assertIn("-object-", res.object_wildcards)
        self.assertNotIn("animal", res.main_chooser)
        
    def test_calculate_all_disabled(self):
        cfg = PromptConfig(
            generate_objects=False, 
            generate_humanoids=False, 
            generate_animals=False, 
            generate_landscapes=False, 
            generate_concepts=False
        )
        res = SubjectSelector.calculate(cfg, self.lm)
        self.assertEqual(len(res.main_chooser), 0)

    def test_calculate_landscapes(self):
        cfg = PromptConfig(generate_landscapes=True, generate_objects=False, generate_humanoids=False, generate_animals=False, generate_concepts=False)
        # Mock location lists
        self.lm.get_list.side_effect = lambda name, **kwargs: ["loc1"] if name.startswith("locations") else []
        
        res = SubjectSelector.calculate(cfg, self.lm)
        self.assertIn("landscape", res.main_chooser)
        self.assertIn("location", res.location_chooser)
        self.assertIn("-location-", res.location_wildcards)

if __name__ == '__main__':
    unittest.main()
