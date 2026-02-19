from dataclasses import dataclass, field
try:
    from .list_manager import ListManager
    from .prompt_config import PromptConfig
except ImportError:
    from list_manager import ListManager
    from prompt_config import PromptConfig

@dataclass
class SubjectSelection:
    main_chooser: list[str] = field(default_factory=list)
    hybrid_list: list[str] = field(default_factory=list)
    hybrid_human_list: list[str] = field(default_factory=list)
    addon_location: list[str] = field(default_factory=list)
    addon_location_inside: list[str] = field(default_factory=list)
    object_wildcards: list[str] = field(default_factory=list)
    animal_wildcards: list[str] = field(default_factory=list)
    location_wildcards: list[str] = field(default_factory=list)
    humanoid_chooser: list[str] = field(default_factory=list)
    location_chooser: list[str] = field(default_factory=list)
    event_chooser: list[str] = field(default_factory=list)
    
    # Booleans for legacy compatibility
    generate_vehicle: bool = False
    generate_object: bool = False
    generate_food: bool = False
    generate_building: bool = False
    generate_space: bool = False
    generate_flora: bool = False
    generate_occult: bool = False
    generate_object_total: bool = False # maps to legacy 'generateobject' after sub-flags OR'ed
    
    generate_fictional: bool = False
    generate_nonfictional: bool = False
    generate_humanoids: bool = False
    generate_manwoman: bool = False
    generate_manwomanrelation: bool = False
    generate_manwomanmultiple: bool = False
    generate_job: bool = False
    generate_firstname: bool = False
    generate_humanoid_total: bool = False # maps to legacy 'generatehumanoid' after sub-flags OR'ed
    
    generate_animal: bool = False
    generate_bird: bool = False
    generate_cat: bool = False
    generate_dog: bool = False
    generate_insect: bool = False
    generate_pokemon: bool = False
    generate_marinelife: bool = False
    generate_animal_total: bool = False # maps to legacy 'generateanimaltotal'
    
    generate_location: bool = False
    generate_location_fantasy: bool = False
    generate_location_scifi: bool = False
    generate_location_videogame: bool = False
    generate_location_biome: bool = False
    generate_location_city: bool = False
    generate_landscape_total: bool = False # maps to legacy 'generatelandscape' after OR'ed
    
    generate_event: bool = False
    generate_concepts: bool = False
    generate_poemline: bool = False
    generate_songline: bool = False
    generate_cardname: bool = False
    generate_episodetitle: bool = False
    generate_concept_total: bool = False # maps to legacy 'generateconcept'

class SubjectSelector:
    """Encapsulates the logic for selecting subjects and categories for prompt generation."""
    
    @staticmethod
    def calculate(cfg: PromptConfig, lm: ListManager) -> SubjectSelection:
        res = SubjectSelection()
        
        # Objects
        if cfg.generate_objects:
            res.generate_vehicle = lm.list_exists("vehicles")
            res.generate_object = lm.list_exists("objects")
            res.generate_food = lm.list_exists("foods")
            res.generate_building = lm.list_exists("buildings")
            res.generate_space = lm.list_exists("space")
            res.generate_flora = lm.list_exists("flora")
            res.generate_occult = lm.list_exists("occult")
            
            res.generate_object_total = res.generate_vehicle or res.generate_object or res.generate_food or res.generate_building or res.generate_space or res.generate_flora or res.generate_occult
            
            if res.generate_object_total:
                object_weight = sum([res.generate_vehicle, res.generate_object, res.generate_food, res.generate_building, res.generate_space, res.generate_flora, res.generate_occult])
                res.main_chooser.extend(["object"] * object_weight)

            if res.generate_vehicle:
                res.object_wildcards.append("-vehicle-")
                res.hybrid_list.append("-vehicle-")
                res.addon_location.append("-vehicle-")
            if res.generate_object:
                res.object_wildcards.append("-object-")
                res.hybrid_list.append("-object-")
            if res.generate_food:
                res.object_wildcards.append("-food-")
                res.hybrid_list.append("-food-")
            if res.generate_space:
                res.object_wildcards.append("-space-")
                res.hybrid_list.append("-space-")
                res.addon_location.append("-space-")
            if res.generate_building:
                res.object_wildcards.append("-building-")
                res.hybrid_list.append("-building-")
                res.addon_location.append("-building-")
                res.addon_location_inside.append("-building-")
            if res.generate_flora:
                res.object_wildcards.append("-flora-")
                res.hybrid_list.append("-flora-")
                res.addon_location.append("-flora-")
            if res.generate_occult:
                res.object_wildcards.append("-occult-")
                res.hybrid_list.append("-occult-")
                res.addon_location.append("-occult-")

        # Humanoids
        if cfg.generate_humanoids:
            res.generate_fictional = lm.list_exists("fictional characters")
            res.generate_nonfictional = lm.list_exists("nonfictional characters")
            res.generate_humanoids = lm.list_exists("humanoids")
            res.generate_manwoman = lm.list_exists("manwoman")
            res.generate_manwomanrelation = lm.list_exists("manwomanrelations")
            res.generate_manwomanmultiple = lm.list_exists("manwomanmultiples")
            res.generate_job = lm.list_exists("jobs")
            res.generate_firstname = lm.list_exists("firstnames")
            
            res.generate_humanoid_total = res.generate_fictional or res.generate_nonfictional or res.generate_humanoids or res.generate_manwoman or res.generate_job or res.generate_manwomanrelation or res.generate_firstname or res.generate_manwomanmultiple
            
            if res.generate_fictional:
                res.humanoid_chooser.append("fictional")
                res.hybrid_list.append("-fictional-")
                res.hybrid_human_list.append("-fictional-")
            if res.generate_nonfictional:
                res.humanoid_chooser.append("non fictional")
                res.hybrid_list.append("-nonfictional-")
                res.hybrid_human_list.append("-nonfictional-")
            if res.generate_humanoids:
                res.humanoid_chooser.append("humanoid")
                res.hybrid_list.append("-humanoid-")
                res.hybrid_human_list.append("-humanoid-")
            if res.generate_manwoman:
                res.humanoid_chooser.append("human")
            if res.generate_manwomanrelation:
                res.humanoid_chooser.append("manwomanrelation")
            if res.generate_manwomanmultiple:
                res.humanoid_chooser.append("manwomanmultiple")
            if res.generate_job:
                res.humanoid_chooser.append("job")
            if res.generate_firstname:
                res.humanoid_chooser.append("firstname")
            if res.generate_humanoid_total:
                humanoid_weight = sum([res.generate_fictional, res.generate_nonfictional, res.generate_humanoids, res.generate_manwoman, res.generate_job, res.generate_manwomanrelation, res.generate_firstname, res.generate_manwomanmultiple])
                res.main_chooser.extend(["humanoid"] * humanoid_weight)

        # Animals
        if cfg.generate_animals:
            res.generate_animal = lm.list_exists("animals")
            res.generate_bird = lm.list_exists("birds")
            res.generate_cat = lm.list_exists("cats")
            res.generate_dog = lm.list_exists("dogs")
            res.generate_insect = lm.list_exists("insects")
            res.generate_pokemon = lm.list_exists("pokemon")
            res.generate_marinelife = lm.list_exists("marinelife")
            
            res.generate_animal_total = res.generate_animal or res.generate_bird or res.generate_cat or res.generate_dog or res.generate_insect or res.generate_pokemon or res.generate_marinelife
            
            if res.generate_animal: res.animal_wildcards.append("-animal-"); res.hybrid_list.append("-animal-")
            if res.generate_bird: res.animal_wildcards.append("-bird-"); res.hybrid_list.append("-bird-")
            if res.generate_cat: res.animal_wildcards.append("-cat-"); res.hybrid_list.append("-cat-")
            if res.generate_dog: res.animal_wildcards.append("-dog-"); res.hybrid_list.append("-dog-")
            if res.generate_insect: res.animal_wildcards.append("-insect-"); res.hybrid_list.append("-insect-")
            if res.generate_pokemon: res.animal_wildcards.append("-pokemon-"); res.hybrid_list.append("-pokemon-")
            if res.generate_marinelife: res.animal_wildcards.append("-marinelife-"); res.hybrid_list.append("-marinelife-")
            if res.generate_animal_total:
                animal_weight = sum([res.generate_animal, res.generate_bird, res.generate_cat, res.generate_dog, res.generate_insect, res.generate_pokemon, res.generate_marinelife])
                res.main_chooser.extend(["animal"] * animal_weight)

        # Landscapes / Locations
        if cfg.generate_landscapes:
            res.generate_location = lm.list_exists("locations")
            res.generate_location_fantasy = lm.list_exists("locations_fantasy")
            res.generate_location_scifi = lm.list_exists("locations_scifi")
            res.generate_location_videogame = lm.list_exists("locations_videogame")
            res.generate_location_biome = lm.list_exists("locations_biome")
            res.generate_location_city = lm.list_exists("locations_city")
            res.generate_landscape_total = res.generate_location or res.generate_location_fantasy or res.generate_location_scifi or res.generate_location_videogame or res.generate_location_biome or res.generate_location_city
            
            if res.generate_landscape_total:
                landscape_weight = sum([res.generate_location, res.generate_location_fantasy, res.generate_location_scifi, res.generate_location_videogame, res.generate_location_biome, res.generate_location_city])
                res.main_chooser.extend(["landscape"] * landscape_weight)
                res.location_chooser.append("landscape")
                res.addon_location.append("-location-")
                res.addon_location.append("-background-")
                res.addon_location_inside.append("-location-")
                res.addon_location_inside.append("-background-")

            if res.generate_location:
                res.location_chooser.append("location")
                res.location_wildcards.append("-location-")
            if res.generate_location_fantasy:
                res.location_chooser.append("fantasy location")
                res.location_wildcards.append("-locationfantasy-")
            if res.generate_location_scifi:
                res.location_chooser.append("sci-fi location")
                res.location_wildcards.append("-locationscifi-")
            if res.generate_location_videogame:
                res.location_chooser.append("videogame location")
                res.location_wildcards.append("-locationvideogame-")
            if res.generate_location_biome:
                res.location_chooser.append("biome")
                res.location_wildcards.append("-locationbiome-")
            if res.generate_location_city:
                res.location_chooser.append("city")
                res.location_wildcards.append("-locationcity-")

        # Concepts
        if cfg.generate_concepts:
            res.generate_event = lm.list_exists("events")
            res.generate_concepts = lm.list_exists("concept_prefix") or lm.list_exists("concept_suffix")
            res.generate_poemline = lm.list_exists("poemlines")
            res.generate_songline = lm.list_exists("songlines")
            res.generate_cardname = lm.list_exists("card_names")
            res.generate_episodetitle = lm.list_exists("episodetitles")
            
            res.generate_concept_total = res.generate_event or res.generate_concepts or res.generate_poemline or res.generate_songline
            
            if res.generate_event: res.event_chooser.append("event")
            if res.generate_concepts: res.event_chooser.append("concept")
            if res.generate_poemline: res.event_chooser.append("poemline")
            if res.generate_songline: res.event_chooser.append("songline")
            if res.generate_cardname: res.event_chooser.append("cardname")
            if res.generate_episodetitle: res.event_chooser.append("episodetitle")
            
            if res.generate_concept_total:
                concept_weight = sum([res.generate_event, res.generate_concepts, res.generate_poemline, res.generate_songline, res.generate_cardname, res.generate_episodetitle])
                res.main_chooser.extend(["concept"] * concept_weight)
        
        return res
