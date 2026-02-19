import pytest, random
from wildcard_resolver import WildcardResolver

@pytest.fixture(autouse=True)
def fixed_seed():
    random.seed(42)

def test_resolve_simple():
    result = WildcardResolver.resolve("-color-", 5, "-color-", ["red","blue","green"],
                                     False, True)
    assert "-color-" not in result
    assert result in ["red", "blue", "green"]

def test_resolve_empty_list_removes_wildcard():
    result = WildcardResolver.resolve("a -color- b", 5, "-color-", [], False, True)
    assert result == "a  b"
    assert "-color-" not in result

def test_resolve_no_double_consumption():
    """Hybrid path must not consume extra items from list."""
    random.seed(0)  # Ensure unique chance fires
    lst = ["red", "blue", "green", "yellow", "purple"]
    
    import unittest.mock as mock
    original_choice = random.choice
    with mock.patch("wildcard_resolver.chance_roll", return_value=True):
        # Patching random.choice to return "hybrid"
        with mock.patch("random.choice", side_effect=lambda x: "hybrid" if x == ["hybrid", "swap"] else original_choice(x)):
             result = WildcardResolver.resolve("-color-", 10, "-color-", lst,
                                             True, True)
    # Hybrid replaces ONE wildcard — list should lose 2 items (for [A|B] syntax)
    # since we have the fix, it should not consume any extra
    assert "-color-" not in result
    # We started with 5, hybrid consumes 2, total remaining should be 3
    assert len(lst) == 3

def test_resolve_metadata_capture():
    meta = {}
    WildcardResolver.resolve("-lighting-", 5, "-lighting-",
                             ["golden hour", "neon", "soft"],
                             False, False, _metadata=meta, metadata_key="chosen_lighting")
    assert "chosen_lighting" in meta
    assert meta["chosen_lighting"] in ["golden hour", "neon", "soft"]

def test_resolve_samehumansubject_reference():
    lst = ["a wizard"]
    result = WildcardResolver.resolve(
        "-manwoman-, -samehumansubject- standing", 5, "-manwoman-", lst, False, False
    )
    assert "-samehumansubject-" not in result
    assert "wizard" in result

def test_resolve_artist_style_expansion():
    """Artist wildcard should expand -artiststyle- sub-wildcards."""
    from unittest.mock import patch
    fake_artist_data = [["fantasy, detailed"], ["oil painting"], ["dark"]]
    with patch("wildcard_resolver.artist_category_by_category_csv_to_list",
               return_value=fake_artist_data):
        result = WildcardResolver.resolve(
            "art by -artist-, in -artiststyle- style", 5, "-artist-",
            ["Greg Rutkowski"], False, False
        )
    assert "-artist-" not in result
    assert "-artiststyle-" not in result
