from dataclasses import dataclass, field
from .list_manager import ListManager
from .mode_selector import ModeSelection

@dataclass
class EnhancerSelection:
    generate_artist: bool = False
    generate_outfit: bool = False
    generate_bodytype: bool = False
    generate_accessorie: bool = False
    generate_artmovement: bool = False
    generate_background: bool = False
    generate_colorscheme: bool = False
    generate_mood: bool = False
    generate_lighting: bool = False
    generate_camera: bool = False
    generate_timeperiod: bool = False
    generate_pose: bool = False
    generate_fashion_designer: bool = False
    generate_eyecolor: bool = False
    generate_age: bool = False
    generate_age_calculator: bool = False
    generate_haircolor: bool = False
    generate_hairstyle: bool = False
    generate_gender_description: bool = False
    generate_fantasy_artist: bool = False
    generate_popular_artist: bool = False
    generate_photography_artist: bool = False
    generate_romanticism_artist: bool = False
    generate_portrait_artist: bool = False
    generate_character_artist: bool = False
    generate_landscape_artist: bool = False
    generate_scifi_artist: bool = False
    generate_architect_artist: bool = False
    generate_digital_artist: bool = False
    generate_graphic_design_artist: bool = False
    generate_cinema_artist: bool = False
    generate_basic_bitch_descriptor: bool = False
    generate_color_combination: bool = False
    generate_material_combination: bool = False
    generate_face: bool = False
    generate_hair: bool = False
    generate_outfit_detailed: bool = False
    generate_object_additions: bool = False
    generate_human_additions: bool = False
    generate_animal_additions: bool = False
    generate_build_accessorie: bool = False
    generate_minilocation_additions: bool = False
    generate_overall_additions: bool = False
    generate_miniactivity: bool = False
    generate_element: bool = False
    generate_setting: bool = False
    generate_charactertype: bool = False
    generate_objectstohold: bool = False
    
    # New flags from thorough review
    generate_vomit: bool = False
    generate_quality: bool = False
    generate_emoji: bool = False
    generate_human_expression: bool = False
    generate_human_vomit: bool = False
    generate_inside_shot: bool = False
    generate_photo_addition: bool = False
    generate_great_work: bool = False
    generate_poem_line: bool = False
    generate_song_line: bool = False
    generate_card_name: bool = False
    generate_episode_title: bool = False
    generate_imagetype_quality: bool = False
    generate_imagetype: bool = False
    generate_descriptors: bool = False
    generate_direction: bool = False
    generate_focus: bool = False
    generate_lens: bool = False
    generate_shot: bool = False
    generate_accessories_legacy: bool = False # maps to generateaccessories (L1251)

class EnhancerSelector:
    """Encapsulates the logic for enabling/disabling various prompt enhancers based on mode and data availability."""
    
    @staticmethod
    def calculate(lm: ListManager, mode: ModeSelection, 
                  add_vomit: bool = True, 
                  add_quality: bool = True,
                  gen_imagetype_quality: bool = True,
                  gen_imagetype: bool = True) -> EnhancerSelection:
        res = EnhancerSelection()
        
        sm = mode.specialmode
        tm = mode.templatemode
        tok = mode.thetokinatormode
        
        # Helper to check if a list exists in ListManager
        def has(name, **kwargs):
            return bool(lm.get_list(name, **kwargs))

        # 1. Artists
        res.generate_artist = has("artists") and (not sm or tok)
        res.generate_fantasy_artist = has("artists_and_category", category="fantasy") and not sm
        res.generate_popular_artist = has("artists_and_category", category="popular") and not sm
        res.generate_photography_artist = has("artists_and_category", category="photography") and not sm
        res.generate_romanticism_artist = has("artists_and_category", category="romanticism") and not sm
        res.generate_portrait_artist = has("artists_and_category", category="portrait") and not sm
        res.generate_character_artist = has("artists_and_category", category="character") and not sm
        res.generate_landscape_artist = has("artists_and_category", category="landscape") and not sm
        res.generate_scifi_artist = has("artists_and_category", category="sci-fi") and not sm
        res.generate_architect_artist = has("artists_and_category", category="architecture") and not sm
        res.generate_digital_artist = has("artists_and_category", category="digital") and not sm
        res.generate_graphic_design_artist = has("artists_and_category", category="graphic design") and not sm
        res.generate_cinema_artist = has("artists_and_category", category="cinema") and not sm

        # 2. Appearance & Outfits
        res.generate_outfit = (has("outfits") or has("buildoutfit")) and not tm
        res.generate_bodytype = has("bodytypes") and not tm
        res.generate_pose = has("poses") and not tm
        res.generate_fashion_designer = has("fashiondesigners") and not sm
        res.generate_eyecolor = has("eyecolors") and not sm
        res.generate_age = has("ages") and not sm
        res.generate_age_calculator = has("agecalculator") and not sm
        res.generate_haircolor = has("haircolors") and not sm
        res.generate_hairstyle = (has("hairstyles") or has("buildhair")) and not tm
        res.generate_gender_description = has("genderdescriptions") and not sm
        res.generate_face = has("buildface") and not sm
        res.generate_hair = has("buildhair") and not sm
        res.generate_outfit_detailed = has("buildoutfit") and not sm
        res.generate_build_accessorie = has("buildaccessorie") and not sm
        res.generate_miniactivity = has("miniactivity") and not sm
        res.generate_charactertype = has("charactertypes") and not sm
        res.generate_human_expression = has("humanexpressions") and not sm
        res.generate_human_vomit = has("humanvomit") and not sm

        # 3. Environment & Style
        res.generate_accessorie = has("accessories") and not sm
        res.generate_accessories_legacy = has("buildaccessorie") and not tm
        res.generate_artmovement = has("artmovements") and not sm
        res.generate_background = has("backgroundtypes") and not sm
        res.generate_colorscheme = has("colorschemes") and not sm
        res.generate_mood = has("moods") and not sm
        res.generate_lighting = has("lightings") and not sm
        res.generate_camera = has("cameras") and not sm
        res.generate_timeperiod = has("timeperiods") and not sm
        res.generate_basic_bitch_descriptor = has("basicbitchdescriptors") and not sm
        res.generate_color_combination = has("colorcombinations") and not sm
        res.generate_material_combination = has("materialcombinations") and not sm
        res.generate_minilocation_additions = has("minilocationadditions") and not sm
        res.generate_overall_additions = has("overalladditions") and not sm
        res.generate_element = has("elements") and not sm
        res.generate_setting = has("settings") and not sm
        res.generate_descriptors = has("descriptors") and not tm
        res.generate_direction = has("directions") and not sm
        res.generate_focus = has("focus") and not sm
        res.generate_lens = has("lenses") and not sm
        res.generate_shot = has("shotsizes") and not sm
        res.generate_inside_shot = has("insideshots") and not sm
        res.generate_photo_addition = has("photoadditions") and not sm

        # 4. Object/Animal/Human additions
        res.generate_object_additions = has("objectadditions") and not tm
        res.generate_human_additions = has("humanadditions") and not tm
        res.generate_animal_additions = has("animaladditions") and not tm
        res.generate_objectstohold = has("objectstohold") and not sm

        # 5. Quality & Others
        res.generate_vomit = has("vomit") and not sm and add_vomit
        res.generate_quality = has("quality") and not sm and add_quality
        res.generate_emoji = has("emojis") and not tm
        res.generate_great_work = has("greatworks") and not sm
        res.generate_poem_line = has("poemlines") and not sm
        res.generate_song_line = has("songlines") and not sm
        res.generate_card_name = has("card_names") and not sm
        res.generate_episode_title = has("episodetitles") and not sm
        res.generate_imagetype_quality = has("imagetypequality") and not sm and gen_imagetype_quality
        res.generate_imagetype = has("imagetypes") and not sm and gen_imagetype

        return res
