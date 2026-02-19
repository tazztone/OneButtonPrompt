import pytest, random
from list_manager import ListManager

@pytest.fixture
def lm():
    return ListManager()

# --- list_exists ---
def test_list_exists_real_file(lm):
    assert lm.list_exists("animals") is True

def test_list_exists_missing_file(lm):
    assert lm.list_exists("__nonexistent_xyz_abc__") is False

def test_list_exists_light_variant(lm, tmp_path, monkeypatch):
    # Mocking os.path.dirname to point to tmp_path
    import os
    (tmp_path / "test_light.csv").write_text("alpha\nbeta\n")
    
    # We need to mock the directory where ListManager looks for CSVs
    # In list_manager.py, it uses os.path.dirname(__file__) + "/csvfiles/"
    csv_dir = tmp_path / "csvfiles"
    csv_dir.mkdir()
    (csv_dir / "test_light.csv").write_text("alpha\nbeta\n")
    
    with monkeypatch.context() as m:
        m.setattr("list_manager.os.path.dirname", lambda _: str(tmp_path))
        # Now list_exists("test") should look in tmp_path/csvfiles/test_light.csv
        assert lm.list_exists("test") is True

# --- pick() cooldown ---
def test_pick_no_immediate_repeat(lm):
    """Same item must not appear twice in a row."""
    results = [lm.pick("animals") for _ in range(20)]
    consecutive = [(results[i], results[i+1]) for i in range(len(results)-1)
                   if results[i] == results[i+1]]
    assert len(consecutive) == 0, f"Consecutive repeats: {consecutive}"

def test_pick_cooldown_respects_window(lm):
    """Item should not repeat within the cooldown window (default=3)."""
    results = [lm.pick("moods") for _ in range(30)]
    for i in range(len(results) - 3):
        window = results[i:i+4]
        assert len(set(window)) >= min(4, len(window)), \
            f"Repeat within cooldown window at position {i}: {window}"

def test_pick_fallback_tiny_list(lm):
    """pick() must not raise when list is smaller than cooldown."""
    from collections import deque
    lm._pick_history["animals"] = deque(
        lm.get_list("animals", copy=False), maxlen=3
    )
    # Should not raise, should return something
    result = lm.pick("animals")
    assert isinstance(result, str) and len(result) > 0

# --- instance isolation ---
def test_pick_history_instance_isolated():
    lm1 = ListManager()
    lm2 = ListManager()
    lm1.pick("moods")
    assert lm2._pick_history == {}, "lm2 should not share lm1's cooldown history"
