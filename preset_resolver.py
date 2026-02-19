import random
import logging
from typing import Optional, Dict, Any, List

# Local imports
try:
    from .prompt_config import PromptConfig
    from .one_button_presets import OneButtonPresets
    from .list_manager import ListManager
except ImportError:
    from prompt_config import PromptConfig
    from one_button_presets import OneButtonPresets
    from list_manager import ListManager

logger = logging.getLogger(__name__)

class PresetResolver:
    """Handles the application of One Button Presets to the PromptConfig."""

    @staticmethod
    def apply(cfg: PromptConfig, lm: ListManager, preset_name: str) -> None:
        """
        Applies a preset (by name) to the provided configuration and ListManager.
        
        Args:
            cfg: The PromptConfig object to update.
            lm: The ListManager, used to update antilist if needed.
            preset_name: The name of the preset to apply.
        """
        if not preset_name or preset_name == 'Custom...':
            return

        selected_preset = None

        # 1. Handle Random Preset
        if preset_name == OneButtonPresets.RANDOM_PRESET_OBP:
            obp_options = OneButtonPresets.load_obp_presets()
            random_key = random.choice(list(obp_options.keys()))
            logger.debug(f"Engaging randomized presets, locking on to: {random_key}")
            selected_preset = OneButtonPresets.get_obp_preset(random_key)
        else:
            # 2. Handle Named Preset
            selected_preset = OneButtonPresets.get_obp_preset(preset_name)

        if not selected_preset:
            return

        # 3. Apply preset values to config
        # Mapping from preset keys to config attributes
        # Note: keys in preset dict match legacy variable names mostly
        
        if "insanitylevel" in selected_preset:
            cfg.insanitylevel = int(selected_preset["insanitylevel"])
        
        if "subject" in selected_preset:
            cfg.forcesubject = selected_preset["subject"]
            
        if "artist" in selected_preset:
            cfg.artists = selected_preset["artist"]
            
        if "chosensubjectsubtypeobject" in selected_preset:
            cfg.subtypeobject = selected_preset["chosensubjectsubtypeobject"]
            
        if "chosensubjectsubtypehumanoid" in selected_preset:
            cfg.subtypehumanoid = selected_preset["chosensubjectsubtypehumanoid"]
            
        if "chosensubjectsubtypeconcept" in selected_preset:
            cfg.subtypeconcept = selected_preset["chosensubjectsubtypeconcept"]
            
        if "chosengender" in selected_preset:
            cfg.gender = selected_preset["chosengender"]
            
        if "imagetype" in selected_preset:
            cfg.imagetype = selected_preset["imagetype"]
            
        if "imagemodechance" in selected_preset:
            cfg.imagemodechance = int(selected_preset["imagemodechance"])
            
        if "givensubject" in selected_preset:
            cfg.givensubject = selected_preset["givensubject"]
            
        if "smartsubject" in selected_preset:
            cfg.smartsubject = bool(selected_preset["smartsubject"])
            
        if "givenoutfit" in selected_preset:
            cfg.overrideoutfit = selected_preset["givenoutfit"]
            
        if "prefixprompt" in selected_preset:
            cfg.prefixprompt = selected_preset["prefixprompt"]
            
        if "suffixprompt" in selected_preset:
            cfg.suffixprompt = selected_preset["suffixprompt"]
            
        if "giventypeofimage" in selected_preset:
            cfg.giventypeofimage = selected_preset["giventypeofimage"]
            
        # 4. Handle Antistring (Anti-values)
        # This was previously ignored/bugged in build_dynamic_prompt.py
        if "antistring" in selected_preset:
            antival_str = selected_preset["antistring"]
            if antival_str:
                # Update cfg.antivalues for completeness
                if cfg.antivalues:
                    cfg.antivalues += "," + antival_str
                else:
                    cfg.antivalues = antival_str
                
                # Update ListManager's actual antilist
                new_anti_items = [s.strip().lower() for s in antival_str.split(",")]
                lm.antilist.extend(new_anti_items)
                lm.antilist = list(set(lm.antilist)) # Deduplicate

        # 5. Handle Custom Mode Config (inline in preset)
        if "prompt_parts" in selected_preset:
            cfg.custom_mode_config = {
                "prompt_parts": selected_preset.get("prompt_parts", []),
                "prompt_prefix": selected_preset.get("prompt_prefix_mode", ""),
                "prompt_suffix": selected_preset.get("prompt_suffix_mode", ""),
            }

        # 6. Apply prefix/suffix from existing config (which might have been set by node inputs)
        # Wait, build_dynamic_prompt logic was:
        # prefixprompt = preset_prefix + ", " + prefixprompt
        # But here assignment overwrote cfg.prefixprompt?
        # In original code:
        # prefixprompt = selected_opb_preset["prefixprompt"]  (Overwrites arg)
        # Then later:
        # prefixprompt = preset_prefix + ", " + prefixprompt
        
        # So we should prepend cfg.preset_prefix to cfg.prefixprompt?
        # Yes, if preset_prefix is set.
        if cfg.preset_prefix:
            cfg.prefixprompt = f"{cfg.preset_prefix}, {cfg.prefixprompt}"
        
        if cfg.preset_suffix:
            cfg.suffixprompt = f"{cfg.suffixprompt}, {cfg.preset_suffix}"

