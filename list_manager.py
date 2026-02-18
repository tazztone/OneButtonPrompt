import os
from .csv_reader import csv_to_list, load_config_csv, load_negative_list, load_all_artist_and_category

class ListManager:
    """Manages loading and caching of all CSV lists used in prompt generation."""
    
    def __init__(self, antivalues: str = "", gender: str = "all", insanitylevel: int = 5, configfilesuffix: str = ""):
        self.gender = gender
        self.insanitylevel = insanitylevel
        self.configfilesuffix = configfilesuffix
        
        # Build antilist
        emptylist = []
        self.antilist = csv_to_list("antilist", emptylist, "./userfiles/", 1)
        antivaluelist = antivalues.split(",")
        self.antilist += [s.strip().lower() for s in antivaluelist]
        self.antilist = list(set(self.antilist)) # Deduplicate
        
        # Config
        self.config = load_config_csv(configfilesuffix)
        
        # Cache for lazy loading
        self._cache = {}

    def get_list(self, name: str, **kwargs) -> list:
        """Get a list by name, using cache if available."""
        cache_key = (name, tuple(sorted(kwargs.items())))
        if cache_key not in self._cache:
            # Most lists use standard parameters
            params = {
                "csvfilename": name,
                "antilist": self.antilist,
                "gender": self.gender,
                "insanitylevel": self.insanitylevel
            }
            params.update(kwargs)
            self._cache[cache_key] = csv_to_list(**params)
        return self._cache[cache_key]

    def load_all_standard_lists(self):
        """Pre-load all commonly used lists."""
        standard_lists = [
            "colors", "animals", "materials", "objects", "buildings", 
            "vehicles", "outfits", "locations", "backgrounds", "accessories",
            "artmovements", "body_types", "cameras", "colorscheme", 
            "concept_prefix", "concept_suffix", "cultures", "descriptors", 
            "devmessages", "directions", "emojis", "events", "focus", 
            "greatworks", "haircolors", "hairstyles", "hairvomit", 
            "humanoids", "jobs", "lenses", "lighting", "malefemale", 
            "manwoman", "moods", "othertypes", "poses", "quality", 
            "shotsizes", "timeperiods", "vomit", "foods"
        ]
        for name in standard_lists:
            self.get_list(name)
            
    @property
    def vehicles(self): return self.get_list("vehicles")
    @property
    def objects(self): return self.get_list("objects")
    @property
    def foods(self): return self.get_list("foods")
    @property
    def buildings(self): return self.get_list("buildings")
    @property
    def space(self): return self.get_list("space")
    @property
    def flora(self): return self.get_list("flora")
    @property
    def occult(self): return self.get_list("occult")
    @property
    def fictional(self): return self.get_list("fictional characters", skipheader=True)
    @property
    def nonfictional(self): return self.get_list("nonfictional characters", skipheader=True)
    @property
    def humanoids(self): return self.get_list("humanoids")
    @property
    def manwoman(self): return self.get_list("manwoman", skipheader=True)
    @property
    def joblist(self): return self.get_list("jobs", skipheader=True)
    @property
    def firstnames(self): return self.get_list("firstnames", skipheader=True)
    @property
    def animals(self): return self.get_list("animals")
    @property
    def birds(self): return self.get_list("birds")
    @property
    def cats(self): return self.get_list("cats")
    @property
    def dogs(self): return self.get_list("dogs")
    @property
    def insects(self): return self.get_list("insects")
    @property
    def pokemon(self): return self.get_list("pokemon")
    @property
    def marinelife(self): return self.get_list("marinelife")
    @property
    def locations(self): return self.get_list("locations")
    @property
    def location_fantasy(self): return self.get_list("locations_fantasy")
    @property
    def location_scifi(self): return self.get_list("locations_scifi")
    @property
    def location_videogame(self): return self.get_list("locations_videogame")
    @property
    def location_biome(self): return self.get_list("locations_biome")
    @property
    def location_city(self): return self.get_list("locations_city")
    @property
    def landscapes(self): return self.get_list("landscapes")
    @property
    def events(self): return self.get_list("events")
    @property
    def concept_prefix(self): return self.get_list("concept_prefix")
    @property
    def concept_suffix(self): return self.get_list("concept_suffix")
    @property
    def poemlines(self): return self.get_list("poemlines")
    @property
    def songlines(self): return self.get_list("songlines")
    @property
    def cardnames(self): return self.get_list("cardnames")
    @property
    def episodetitles(self): return self.get_list("episodetitles")
