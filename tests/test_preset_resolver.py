import pytest
from unittest.mock import MagicMock, patch
from preset_resolver import PresetResolver
from prompt_config import PromptConfig
from list_manager import ListManager
from one_button_presets import OneButtonPresets

@pytest.fixture
def cfg():
    return PromptConfig()

@pytest.fixture
def lm():
    mock_lm = MagicMock(spec=ListManager)
    mock_lm.antilist = []
    # Mock get_list to return something if needed
    mock_lm.get_list.return_value = []
    return mock_lm

def test_apply_named_preset(cfg, lm):
    # Mock OneButtonPresets.get_obp_preset
    preset_data = {
        "insanitylevel": "3",
        "subject": "dog",
        "artist": "picasso",
        "antistring": "bad,ugly"
    }
    
    with patch("one_button_presets.OneButtonPresets.get_obp_preset", return_value=preset_data):
        PresetResolver.apply(cfg, lm, "TestPreset")
        
        assert cfg.insanitylevel == 3
        assert cfg.forcesubject == "dog"
        assert cfg.artists == "picasso"
        assert cfg.antivalues == "bad,ugly"
        
        # Verify ListManager antilist updated
        assert set(lm.antilist) == {"bad", "ugly"}

def test_apply_no_preset(cfg, lm):
    # Should do nothing
    PresetResolver.apply(cfg, lm, "")
    assert cfg.insanitylevel == 5 # default

def test_apply_random_preset(cfg, lm):
    preset_data = {
        "insanitylevel": "7",
        "subject": "cat"
    }
    
    with patch("one_button_presets.OneButtonPresets.load_obp_presets", return_value={"RandomKey": {}}), \
         patch("one_button_presets.OneButtonPresets.get_obp_preset", return_value=preset_data), \
         patch("random.choice", return_value="RandomKey"):
         
         PresetResolver.apply(cfg, lm, OneButtonPresets.RANDOM_PRESET_OBP)
         
         assert cfg.insanitylevel == 7
         assert cfg.forcesubject == "cat"

def test_antistring_cumulative(cfg, lm):
    cfg.antivalues = "existing"
    lm.antilist = ["existing"]
    
    preset_data = {"antistring": "new"}
    
    with patch("one_button_presets.OneButtonPresets.get_obp_preset", return_value=preset_data):
        PresetResolver.apply(cfg, lm, "TestPreset")
        
        assert cfg.antivalues == "existing,new"
        assert "existing" in lm.antilist
        assert "new" in lm.antilist
