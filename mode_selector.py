import os
import json
import random
from dataclasses import dataclass, field
from .random_functions import uncommon_dist
from .list_manager import ListManager
from .prompt_config import PromptConfig

_CUSTOM_MODES_CACHE = None

@dataclass
class ModeSelection:
    imagetype: str
    specialmode: bool = False
    templatemode: bool = False
    artblastermode: bool = False
    qualityvomitmode: bool = False
    uniqueartmode: bool = False
    colorcannonmode: bool = False
    photofantasymode: bool = False
    massivemadnessmode: bool = False
    onlysubjectmode: bool = False
    stylesmode: bool = False
    thetokinatormode: bool = False
    dynamictemplatesmode: bool = False
    artifymode: bool = False
    custommodeactive: bool = False
    generationmode: str = ""
    token_list: list[str] = field(default_factory=list)
    custom_mode_config: dict = field(default_factory=dict, repr=False)

class ModeSelector:
    """Encapsulates the logic for selecting and configuring 'Special Modes' in prompt generation."""
    
    @staticmethod
    def load_custom_modes():
        global _CUSTOM_MODES_CACHE
        if _CUSTOM_MODES_CACHE is not None:
            return _CUSTOM_MODES_CACHE
        
        _CUSTOM_MODES_CACHE = {}
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(script_dir, "userfiles", "custom_modes.json")
        
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    _CUSTOM_MODES_CACHE = json.load(f)
            except Exception as e:
                print(f"OneButtonPrompt: Error loading custom modes: {e}")
        return _CUSTOM_MODES_CACHE

    @staticmethod
    def calculate(cfg: PromptConfig, lm: ListManager, imagetypemodelist: list[str], less_verbose: bool, anime_mode: bool) -> ModeSelection:
        current_imagetype = cfg.imagetype
        
        # 1. Random Mode Selection Chance (if imagetype is "all" or "all - anime")
        if (random.randint(1, int(cfg.imagemodechance)) == 1 and 
            (current_imagetype == "all" or current_imagetype == "all - anime") and 
            cfg.giventypeofimage == "" and 
            not cfg.onlyartists):
            
            # Filter available modes
            available_modes = [m for m in imagetypemodelist if m != "all"]
            if less_verbose and "dynamic templates mode" in available_modes:
                available_modes.remove("dynamic templates mode")
            
            if anime_mode:
                for m in ["only templates mode", "massive madness mode", "fixed styles mode", "unique art mode"]:
                    if m in available_modes:
                        available_modes.remove(m)
            
            if available_modes:
                current_imagetype = random.choice(available_modes)

        res = ModeSelection(imagetype=current_imagetype)
        
        # 2. Map imagetype to special flags
        if current_imagetype == "only templates mode":
            res.specialmode = True
            res.templatemode = True
            res.generationmode = "only templates"
        
        elif current_imagetype == "art blaster mode":
            res.specialmode = True
            res.generationmode = "art blaster"
            if uncommon_dist(cfg.insanitylevel):
                res.artblastermode = True
            elif lm.get_list("artists"):
                res.onlysubjectmode = True
                res.artifymode = True
            else:
                res.artblastermode = True

        elif current_imagetype == "unique art mode":
            res.specialmode = True
            res.uniqueartmode = True
            res.generationmode = "unique art"
            
        elif current_imagetype == "quality vomit mode":
            res.specialmode = True
            res.qualityvomitmode = True
            res.generationmode = "quality vomit"
            
        elif current_imagetype == "color cannon mode":
            res.specialmode = True
            res.colorcannonmode = True
            res.generationmode = "color cannon"
            
        elif current_imagetype == "photo fantasy mode":
            res.specialmode = True
            res.photofantasymode = True
            res.generationmode = "photo fantasy"
            
        elif current_imagetype == "massive madness mode":
            res.specialmode = True
            res.massivemadnessmode = True
            res.generationmode = "massive madness"
            
        elif current_imagetype == "subject only mode":
            res.specialmode = True
            res.onlysubjectmode = True
            res.generationmode = "subject only"
            
        elif current_imagetype == "fixed styles mode":
            res.specialmode = True
            res.stylesmode = True
            res.generationmode = "fixed styles"
            
        elif current_imagetype == "the tokinator":
            res.specialmode = True
            res.thetokinatormode = True
            res.generationmode = "tokinator"
            res.token_list = lm.get_list("tokens", skipheader=True)
            
        elif current_imagetype == "dynamic templates mode":
            res.specialmode = True
            res.dynamictemplatesmode = True
            
        elif current_imagetype == "artify mode":
            res.specialmode = True
            res.onlysubjectmode = True
            res.artifymode = True
            res.generationmode = "artify"

        # 3. Custom Mode Handling
        custom_modes = ModeSelector.load_custom_modes()
        
        # Priority 1: Config passed explicitly
        if cfg.custom_mode_config:
            res.specialmode = True
            res.custommodeactive = True
            res.generationmode = "custom mode: preset-inline"
            res.custom_mode_config = cfg.custom_mode_config
            
        # Priority 2: Named custom mode
        elif current_imagetype in custom_modes:
            res.specialmode = True
            res.custommodeactive = True
            res.generationmode = f"custom mode: {current_imagetype}"
            res.custom_mode_config = custom_modes[current_imagetype]
            
        return res
