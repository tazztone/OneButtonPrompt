import sys
import os
import unittest
from unittest.mock import MagicMock

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock ComfyUI modules if they are imported via __init__.py or others
import sys
from unittest.mock import MagicMock
sys.modules['folder_paths'] = MagicMock()
sys.modules['server'] = MagicMock()

from subject_selector import SubjectSelector, SubjectSelection
from prompt_config import PromptConfig
from list_manager import ListManager

class TestSubjectSelector(unittest.TestCase):
    
    def setUp(self):
        self.lm = MagicMock(spec=ListManager)
        # Mock get_list to return a non-empty list for common items
        self.lm.get_list.side_effect = lambda name, **kwargs: ["item1"] if name in ["vehicles", "objects", "animals", "locations"] else []
        # Mock list_exists to match the logic used in subject_selector
        self.lm.list_exists.side_effect = lambda name, **kwargs: name in [
            "vehicles", "objects", "foods", "buildings", "space", "flora", "occult",
            "animals", "birds", "cats", "dogs", "insects", "pokemon", "marinelife",
            "locations", "locations_fantasy", "locations_scifi", "locations_videogame", "locations_biome", "locations_city",
            "fictional characters", "nonfictional characters", "humanoids", "manwoman", "manwomanrelations", "manwomanmultiples", "jobs", "firstnames",
            "events", "concept_prefix", "concept_suffix", "poemlines", "songlines", "card_names", "episodetitles"
        ]
        
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
