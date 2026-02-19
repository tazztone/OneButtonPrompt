import random
import logging
from dataclasses import dataclass, field
from typing import Optional, List, Dict

try:
    from .random_functions import chance_roll
    from .csv_reader import artist_category_csv_to_list
except ImportError:
    from random_functions import chance_roll
    from csv_reader import artist_category_csv_to_list

logger = logging.getLogger(__name__)

@dataclass
class ArtistSelection:
    artists: str = "all"
    artiststyleselector: str = ""
    artiststyleselectormode: str = "normal"
    generateartist: bool = True
    artistlist: List[str] = field(default_factory=list)
    fantasyartistlist: List[str] = field(default_factory=list)
    popularartistlist: List[str] = field(default_factory=list)
    romanticismartistlist: List[str] = field(default_factory=list)
    photographyartistlist: List[str] = field(default_factory=list)
    portraitartistlist: List[str] = field(default_factory=list)
    characterartistlist: List[str] = field(default_factory=list)
    landscapeartistlist: List[str] = field(default_factory=list)
    scifiartistlist: List[str] = field(default_factory=list)
    graphicdesignartistlist: List[str] = field(default_factory=list)
    digitalartistlist: List[str] = field(default_factory=list)
    architectartistlist: List[str] = field(default_factory=list)
    cinemaartistlist: List[str] = field(default_factory=list)
    gregmodelist: List[str] = field(default_factory=list)
    
    # Theme coherence overrides
    location_pool_override: Optional[List[str]] = None
    lighting_pool_override: Optional[List[str]] = None

class ArtistSelector:
    
    ARTIST_TYPES = [
        "popular", "3D", "abstract", "angular", "anime", "architecture", 
        "art nouveau", "art deco", "baroque", "bauhaus", "cartoon", "character", 
        "children's illustration", "cityscape", "cinema", "clean", "cloudscape", 
        "collage", "colorful", "comics", "cubism", "dark", "detailed", "digital", 
        "expressionism", "fantasy", "fashion", "fauvism", "figurativism", "graffiti", 
        "graphic design", "high contrast", "horror", "impressionism", "installation", 
        "landscape", "light", "line drawing", "low contrast", "luminism", 
        "magical realism", "manga", "melanin", "messy", "monochromatic", "nature", 
        "photography", "pop art", "portrait", "primitivism", "psychedelic", 
        "realism", "renaissance", "romanticism", "scene", "sci-fi", "sculpture", 
        "seascape", "space", "stained glass", "still life", "storybook realism", 
        "street art", "streetscape", "surrealism", "symbolism", "textile", 
        "ukiyo-e", "vibrant", "watercolor", "whimsical"
    ]

    @staticmethod
    def calculate(cfg, lm, get_compatible_pools_func) -> ArtistSelection:
        res = ArtistSelection(artists=cfg.artists)
        insanitylevel = cfg.insanitylevel
        
        # build artists list
        if res.artists == "wild":
            res.artists = "all (wild)"

        # lets maybe go wild "sometimes", based on insanitylevel
        if res.artists == "all" and chance_roll(insanitylevel, 'rare'):
            res.artists = "all (wild)"

        if res.artists == "all" and chance_roll(insanitylevel + 1, 'normal'):
            res.artiststyleselector = random.choice(ArtistSelector.ARTIST_TYPES)
            res.artists = res.artiststyleselector
        elif res.artists == "all":
            res.artiststyleselectormode = "custom"
            if random.randint(0, 6) == 0 and getattr(cfg, 'onlyartists', False) == False:
                res.generateartist = False
            elif chance_roll(max(3, insanitylevel), 'common'):
                res.artists = "popular"
            elif random.randint(0, 1) == 0:
                if insanitylevel < 6:
                    res.artists = "greg mode"
                else:
                    res.artists = "popular"
            else:
                res.artists = "none"
        else:
            res.artiststyleselectormode = "custom"

        # create artist list
        if res.artists != "all (wild)" and res.artists != "all" and res.artists != "none" and \
           not res.artists.startswith("personal_artists") and not res.artists.startswith("personal artists") and \
           res.artists in ArtistSelector.ARTIST_TYPES:
            res.artistlist = artist_category_csv_to_list("artists_and_category", res.artists)
        elif res.artists.startswith("personal_artists") or res.artists.startswith("personal artists"):
            artists_path = res.artists.replace(" ", "_", -1)
            res.artistlist = lm.get_list(artists_path, directory="./userfiles/")
        elif res.artists != "none":
            res.artistlist = lm.get_list("artists")

        # create special artists lists
        res.fantasyartistlist = artist_category_csv_to_list("artists_and_category", "fantasy")
        res.popularartistlist = artist_category_csv_to_list("artists_and_category", "popular")
        res.romanticismartistlist = artist_category_csv_to_list("artists_and_category", "romanticism")
        res.photographyartistlist = artist_category_csv_to_list("artists_and_category", "photography")
        res.portraitartistlist = artist_category_csv_to_list("artists_and_category", "portrait")
        res.characterartistlist = artist_category_csv_to_list("artists_and_category", "character")
        res.landscapeartistlist = artist_category_csv_to_list("artists_and_category", "landscape")
        res.scifiartistlist = artist_category_csv_to_list("artists_and_category", "sci-fi")
        res.graphicdesignartistlist = artist_category_csv_to_list("artists_and_category", "graphic design")
        res.digitalartistlist = artist_category_csv_to_list("artists_and_category", "digital")
        res.architectartistlist = artist_category_csv_to_list("artists_and_category", "architecture")
        res.cinemaartistlist = artist_category_csv_to_list("artists_and_category", "cinema")
        res.gregmodelist = lm.get_list("gregmode")

        # Theme Coherence Anchoring (Phase 7)
        if res.artiststyleselector:
            comp_loc_pools = get_compatible_pools_func(res.artiststyleselector, "locations", lm)
            if comp_loc_pools and comp_loc_pools != ["locations"]:
                res.location_pool_override = []
                for pool in comp_loc_pools:
                    res.location_pool_override.extend(lm.get_list(pool, copy=False))
            
            comp_light_pools = get_compatible_pools_func(res.artiststyleselector, "lighting", lm)
            if comp_light_pools and comp_light_pools != ["lighting"]:
                res.lighting_pool_override = []
                for pool in comp_light_pools:
                    res.lighting_pool_override.extend(lm.get_list(pool, copy=False))

        return res
