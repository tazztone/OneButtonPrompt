"""PromptEngine — clean, class-based API for One Button Prompt generation.

Usage::

    from prompt_engine import PromptEngine
    from prompt_config import PromptConfig

    engine = PromptEngine()
    config = PromptConfig(insanitylevel=7, base_model="SDXL", seed=42)
    prompt, prompt_g, prompt_l = engine.generate(config)
"""
from __future__ import annotations

from dataclasses import asdict

if __package__ is None or __package__ == '':
    from prompt_config import PromptConfig
    from build_dynamic_prompt import (
        build_dynamic_prompt,
        build_dynamic_negative,
        createpromptvariant,
        enhance_positive,
        artify_prompt,
        flufferizer,
    )
else:
    from .prompt_config import PromptConfig
    from .build_dynamic_prompt import (
        build_dynamic_prompt,
        build_dynamic_negative,
        createpromptvariant,
        enhance_positive,
        artify_prompt,
        flufferizer,
    )


class PromptEngine:
    """High-level, stateless prompt generator.

    Wraps the legacy ``build_dynamic_prompt`` function behind a typed
    ``PromptConfig`` interface.  All randomness is controlled by
    ``config.seed`` — identical configs produce identical output.
    """

    # ------------------------------------------------------------------
    # Core generation
    # ------------------------------------------------------------------
    @staticmethod
    def generate(config: PromptConfig | None = None, **overrides) -> list:
        """Generate a prompt from the given config.

        Parameters
        ----------
        config : PromptConfig, optional
            Typed config object. If *None*, a default is created.
        **overrides
            Ad-hoc overrides merged on top of *config*.

        Returns
        -------
        list
            ``[completeprompt, prompt_g, prompt_l]``
        """
        if config is None:
            config = PromptConfig()

        # Merge any ad-hoc overrides into a fresh config dict
        params = asdict(config)
        params.update(overrides)

        return build_dynamic_prompt(**params)

    # ------------------------------------------------------------------
    # Auxiliary prompt operations
    # ------------------------------------------------------------------
    @staticmethod
    def generate_negative(
        positive_prompt: str,
        insanitylevel: int = 0,
        enhance: bool = False,
        existing_negative_prompt: str = "",
        base_model: str = "SD1.5",
    ) -> str:
        """Build a negative prompt that complements *positive_prompt*."""
        return build_dynamic_negative(
            positive_prompt=positive_prompt,
            insanitylevel=insanitylevel,
            enhance=enhance,
            existing_negative_prompt=existing_negative_prompt,
            base_model=base_model,
        )

    @staticmethod
    def create_variant(
        prompt: str,
        insanitylevel: int = 5,
        antivalues: str = "",
        gender: str = "all",
        artists: str = "all",
        advancedprompting: bool = True,
    ) -> str:
        """Create a variation of an existing prompt."""
        return createpromptvariant(
            prompt, insanitylevel, antivalues, gender, artists, advancedprompting
        )

    @staticmethod
    def enhance(prompt: str, amount: int = 1) -> str:
        """Add random descriptive words to a prompt."""
        return enhance_positive(positive_prompt=prompt, amountofwords=amount)

    @staticmethod
    def artify(
        prompt: str,
        insanitylevel: int = 5,
        artists: str = "all",
        amountofartists: str = "1",
        mode: str = "standard",
        seed: int = -1,
    ) -> str:
        """Add artistic styling to a prompt."""
        return artify_prompt(
            insanitylevel=insanitylevel,
            prompt=prompt,
            artists=artists,
            amountofartists=amountofartists,
            mode=mode,
            seed=seed,
        )

    @staticmethod
    def flufferize(
        prompt: str,
        amount: str = "dynamic",
        seed: int = -1,
        reverse_polarity: bool = False,
    ) -> str:
        """Add descriptive 'fluff' to a prompt (Fooocus-style)."""
        return flufferizer(
            prompt=prompt,
            amountoffluff=amount,
            seed=seed,
            reverse_polarity=reverse_polarity,
        )
