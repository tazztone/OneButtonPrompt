import pytest
from unittest.mock import MagicMock, patch
from artist_selector import ArtistSelector, ArtistSelection
from prompt_config import PromptConfig

@pytest.fixture
def cfg():
    c = PromptConfig()
    c.insanitylevel = 5
    c.artists = "all"
    c.onlyartists = False
    return c

@pytest.fixture
def lm():
    m = MagicMock()
    m.get_list.return_value = ["artist_a", "artist_b"]
    m.get_artist_category_list.return_value = ["artist_a"]
    return m

def test_calculate_returns_selection(cfg, lm):
    result = ArtistSelector.calculate(cfg, lm)
    assert isinstance(result, ArtistSelection)

def test_wild_alias_normalised(cfg, lm):
    cfg.artists = "wild"
    result = ArtistSelector.calculate(cfg, lm)
    assert result.artists == "all (wild)"

def test_personal_artists_underscore_normalised(cfg, lm):
    cfg.artists = "personal artists my_list"
    ArtistSelector.calculate(cfg, lm)
    # Should have called get_list with underscored path
    # lm.get_list.call_args_list[0][0][0] is the first argument of the first call
    # But get_list is called multiple times (for artists, gregmode, etc.)
    underscored_call = False
    for call in lm.get_list.call_args_list:
        if "personal_artists" in str(call):
            underscored_call = True
            break
    assert underscored_call

def test_coherence_anchoring_calls_compatible_pools(cfg, lm):
    cfg.artists = "fantasy"   # forces a specific artiststyleselector
    with patch.object(ArtistSelector, 'get_compatible_pools', return_value=["locations_fantasy"]) as mock_compat:
        result = ArtistSelector.calculate(cfg, lm)
        assert mock_compat.called

def test_uses_lm_cache_for_special_lists(cfg, lm):
    # Direct artist_category_csv_to_list must NOT be called
    # Special lists must use lm cache (get_artist_category_list)
    with patch("artist_selector.artist_category_csv_to_list") as mock_csv:
        ArtistSelector.calculate(cfg, lm)
        assert mock_csv.call_count == 0, "Special lists must use lm cache, not raw CSV reader"
        # All 12 special list loads + potential artist selection load = many calls
        assert lm.get_artist_category_list.call_count >= 12
