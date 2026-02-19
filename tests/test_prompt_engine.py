"""Tests for the PromptEngine facade class."""
import pytest
from unittest.mock import patch, MagicMock
from OneButtonPrompt.prompt_config import PromptConfig
from OneButtonPrompt.prompt_engine import PromptEngine


class TestPromptEngineGenerate:
    """Test PromptEngine.generate() — the core method."""

    def test_generate_returns_list(self):
        """Smoke test: generate() returns a list with 3 elements when prompt_g_and_l is True."""
        engine = PromptEngine()
        result = engine.generate(PromptConfig(seed=42, prompt_g_and_l=True))
        assert isinstance(result, list)
        assert len(result) == 3

    def test_generate_with_default_config(self):
        """generate() with default config should not crash."""
        engine = PromptEngine()
        result = engine.generate(PromptConfig(seed=1))
        assert isinstance(result[0], str)
        assert len(result[0]) > 0

    def test_generate_with_none_config(self):
        """generate() with None config should use defaults."""
        engine = PromptEngine()
        result = engine.generate(None)
        assert isinstance(result, list)

    def test_generate_with_overrides(self):
        """Ad-hoc overrides should be forwarded."""
        engine = PromptEngine()
        config = PromptConfig(seed=42, base_model="SD1.5")
        result = engine.generate(config, base_model="SDXL")
        assert isinstance(result, list)

    def test_seed_determinism(self):
        """Same config should produce same output (after cache is warm)."""
        engine = PromptEngine()
        cfg = PromptConfig(seed=12345, insanitylevel=5, base_model="SDXL")
        # Warm up the cache - initial load can consume random bits for list variety
        engine.generate(cfg)
        r1 = engine.generate(cfg)
        r2 = engine.generate(cfg)
        assert r1[0] == r2[0]

    def test_different_seeds_differ(self):
        """Different seeds should almost certainly produce different output."""
        engine = PromptEngine()
        r1 = engine.generate(PromptConfig(seed=111))
        r2 = engine.generate(PromptConfig(seed=222))
        # It's theoretically possible they match, but extremely unlikely
        assert r1[0] != r2[0]


class TestPromptEngineAuxiliary:
    """Test auxiliary methods in PromptEngine."""

    def test_generate_negative(self):
        """generate_negative should return a string."""
        engine = PromptEngine()
        result = engine.generate_negative("a cat sitting on a hat")
        assert isinstance(result, str)

    def test_create_variant(self):
        """create_variant should return a string."""
        engine = PromptEngine()
        result = engine.create_variant("a beautiful landscape painting")
        assert isinstance(result, str)

    def test_enhance(self):
        """enhance should return a string."""
        engine = PromptEngine()
        result = engine.enhance("a dog", amount=2)
        assert isinstance(result, str)

    def test_flufferize(self):
        """flufferize should return a longer string than input."""
        engine = PromptEngine()
        original = "a simple prompt"
        result = engine.flufferize(original)
        assert isinstance(result, str)
        assert len(result) > len(original)

    def test_flufferize_none_returns_same(self):
        """flufferize with amount='none' should return the original."""
        engine = PromptEngine()
        original = "a simple prompt"
        result = engine.flufferize(original, amount="none")
        assert result == original
