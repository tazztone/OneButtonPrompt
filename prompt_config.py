"""PromptConfig — typed, validated configuration for One Button Prompt.

This dataclass replaces the 33-parameter signature of build_dynamic_prompt
with a single, introspectable config object.
"""
from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Any, Dict, Optional


@dataclass
class PromptConfig:
    """All knobs that control One Button Prompt generation.

    Defaults mirror the legacy ``build_dynamic_prompt()`` signature exactly,
    so ``PromptConfig()`` is equivalent to calling the function with no args.
    """

    # --- core randomness ---
    insanitylevel: int = 5
    seed: int = -1

    # --- subject selection ---
    forcesubject: str = "all"
    givensubject: str = ""
    smartsubject: bool = True
    gender: str = "all"
    subtypeobject: str = "all"
    subtypehumanoid: str = "all"
    subtypeconcept: str = "all"
    subtypeanimal: str = "all"
    subtypelocation: str = "all"

    # --- image type ---
    imagetype: str = "all"
    giventypeofimage: str = ""
    imagemodechance: int = 20

    # --- artists ---
    artists: str = "all"
    onlyartists: bool = False

    # --- prompt text framing ---
    prefixprompt: str = ""
    suffixprompt: str = ""
    antivalues: str = ""
    overrideoutfit: str = ""
    promptcompounderlevel: str = "1"
    seperator: str = "comma"

    # --- feature toggles ---
    advancedprompting: bool = True
    hardturnoffemojis: bool = False
    prompt_g_and_l: bool = False

    # --- model / preset ---
    base_model: str = "SD1.5"
    OBP_preset: str = ""
    prompt_enhancer: str = "none"
    preset_prefix: str = ""
    preset_suffix: str = ""

    # --- advanced overrides ---
    chance_overrides: Optional[Dict[str, Any]] = None
    custom_mode_config: Optional[Dict[str, Any]] = None

    # --- internal / debug ---
    _return_metadata: bool = False

    # ------------------------------------------------------------------
    # Convenience constructors
    # ------------------------------------------------------------------
    @classmethod
    def from_kwargs(cls, **kwargs: Any) -> "PromptConfig":
        """Build a PromptConfig from arbitrary keyword arguments.

        Unknown keys are silently ignored so callers can forward
        ``**locals()`` without filtering.
        """
        valid = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in kwargs.items() if k in valid})
