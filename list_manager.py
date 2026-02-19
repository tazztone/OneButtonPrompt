from collections import deque
import os
try:
    from .csv_reader import csv_to_list, load_config_csv, load_negative_list, load_all_artist_and_category, artist_category_csv_to_list, artist_descriptions_csv_to_list
except ImportError:
    from csv_reader import csv_to_list, load_config_csv, load_negative_list, load_all_artist_and_category, artist_category_csv_to_list, artist_descriptions_csv_to_list

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
        self.config_dict = {row[0]: row[1] for row in self.config if row and len(row) >= 2}
        
        # Cache for lazy loading
        self._cache = {}

        # History for anti-repeat cooldown (Phase 4)
        self._pick_history = {} # name -> deque

    # Valid kwargs for csv_to_list (beyond the defaults we always pass)
    _CSV_KWARGS = {"directory", "lowerandstrip", "delimiter", "listoflistmode", "skipheader"}

    def get_list(self, name: str = None, copy: bool = True, **kwargs) -> list:
        """Get a list by name, using cache if available."""
        # ... (implementation same as before, truncated for brevity in replacement)
        # Accept 'csvfilename' as an alias for 'name' (legacy compatibility)
        if name is None:
            name = kwargs.pop("csvfilename", None)
        if name is None:
            raise TypeError("get_list() requires 'name' or 'csvfilename' argument")
        # Convert list arguments to tuples to make them hashable for the cache key
        hashable_kwargs = {}
        for k, v in kwargs.items():
            if isinstance(v, list):
                hashable_kwargs[k] = tuple(v)
            else:
                hashable_kwargs[k] = v
        
        cache_key = (name, tuple(sorted(hashable_kwargs.items())))
        if cache_key not in self._cache:
            # Only forward kwargs that csv_to_list actually accepts
            csv_kwargs = {k: v for k, v in kwargs.items() if k in self._CSV_KWARGS}
            params = {
                "csvfilename": name,
                "antilist": self.antilist,
                "gender": kwargs.get("gender", self.gender),
                "insanitylevel": self.insanitylevel
            }
            params.update(csv_kwargs)
            self._cache[cache_key] = csv_to_list(**params)
        
        # Return a copy by default to prevent in-place mutations from corrupting the cache
        result = self._cache[cache_key]
        if isinstance(result, list):
            return result[:] if copy else result
        return result

    def list_exists(self, name: str, directory: str = "./csvfiles/") -> bool:
        """Checks if a list CSV file exists without loading it."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 1. Check for replacement in userfiles
        if os.path.isfile(os.path.join(script_dir, "./userfiles/", name + "_replace.csv")):
            return True
        # 2. Check for base file in target directory
        if os.path.isfile(os.path.join(script_dir, directory, name + ".csv")):
            return True
        # 3. Check for light/medium variants
        if os.path.isfile(os.path.join(script_dir, directory, name + "_light.csv")):
            return True
        if os.path.isfile(os.path.join(script_dir, directory, name + "_medium.csv")):
            return True
        
        return False

    def pick(self, name: str, cooldown: int = 3, **kwargs) -> str:
        """Picks a random item from a list, using anti-repeat cooldown (Phase 4)."""
        lst = self.get_list(name, copy=False, **kwargs)
        if not lst:
            return ""
            
        # Filter out recently picked items
        history = self._pick_history.get(name)
        if history is None:
            history = deque(maxlen=cooldown)
            self._pick_history[name] = history
            
        available = [item for item in lst if item not in history]
        
        if not available:
            # Fallback if everything is in cooldown (e.g. list too small)
            available = lst
            
        choice = random.choice(available)
        
        # Update history
        history.append(choice)
        
        return choice

    def get_all_artists_and_categories(self):
        """Get the full artist and category lists, cached."""
        cache_key = ("all_artists_and_categories",)
        if cache_key not in self._cache:
            self._cache[cache_key] = load_all_artist_and_category()
        return self._cache[cache_key]

    def get_artist_category_list(self, csvfilename, category):
        """Get artists by category, cached."""
        cache_key = ("artist_category_list", csvfilename, category)
        if cache_key not in self._cache:
            self._cache[cache_key] = artist_category_csv_to_list(csvfilename, category)
        return self._cache[cache_key]

    def get_artist_descriptions(self, csvfilename):
        """Get artist descriptions, cached."""
        cache_key = ("artist_descriptions", csvfilename)
        if cache_key not in self._cache:
            self._cache[cache_key] = artist_descriptions_csv_to_list(csvfilename)
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
