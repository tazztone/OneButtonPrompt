"""Tests for the PromptConfig dataclass."""
import pytest
from OneButtonPrompt.prompt_config import PromptConfig


class TestPromptConfigDefaults:
    """Verify defaults match the legacy build_dynamic_prompt signature."""

    def test_default_insanitylevel(self):
        cfg = PromptConfig()
        assert cfg.insanitylevel == 5

    def test_default_seed(self):
        cfg = PromptConfig()
        assert cfg.seed == -1

    def test_default_forcesubject(self):
        cfg = PromptConfig()
        assert cfg.forcesubject == "all"

    def test_default_base_model(self):
        cfg = PromptConfig()
        assert cfg.base_model == "SD1.5"

    def test_default_chance_overrides_is_none(self):
        cfg = PromptConfig()
        assert cfg.chance_overrides is None

    def test_default_custom_mode_config_is_none(self):
        cfg = PromptConfig()
        assert cfg.custom_mode_config is None


class TestPromptConfigFromKwargs:
    """Test the from_kwargs classmethod."""

    def test_known_keys_accepted(self):
        cfg = PromptConfig.from_kwargs(insanitylevel=8, seed=42, artists="none")
        assert cfg.insanitylevel == 8
        assert cfg.seed == 42
        assert cfg.artists == "none"

    def test_unknown_keys_ignored(self):
        cfg = PromptConfig.from_kwargs(insanitylevel=3, totally_fake_key="nope")
        assert cfg.insanitylevel == 3
        assert not hasattr(cfg, "totally_fake_key")

    def test_empty_kwargs_gives_defaults(self):
        cfg = PromptConfig.from_kwargs()
        default = PromptConfig()
        assert cfg == default

    def test_partial_override(self):
        cfg = PromptConfig.from_kwargs(base_model="SDXL")
        assert cfg.base_model == "SDXL"
        # Everything else should be default
        assert cfg.insanitylevel == 5
        assert cfg.prompt_enhancer == "none"


class TestPromptConfigEquality:
    """Test dataclass equality and copying."""

    def test_identical_configs_are_equal(self):
        a = PromptConfig(insanitylevel=7)
        b = PromptConfig(insanitylevel=7)
        assert a == b

    def test_different_configs_are_not_equal(self):
        a = PromptConfig(insanitylevel=7)
        b = PromptConfig(insanitylevel=3)
        assert a != b
