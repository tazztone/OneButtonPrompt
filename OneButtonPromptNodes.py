import sys
import os
import json
import folder_paths
from datetime import datetime
import uuid
import platform
 
custom_nodes_path = os.path.join(folder_paths.base_path, "custom_nodes")
onebuttonprompt_path = os.path.join(custom_nodes_path, "OneButtonPrompt")

sys.path.append(onebuttonprompt_path)

from .build_dynamic_prompt import build_dynamic_prompt, build_dynamic_negative, artify_prompt, flufferizer, SUPPORTED_WILDCARDS
from .csv_reader import *

from .one_button_presets import OneButtonPresets
OBPresets = OneButtonPresets()
custom_modes = {}
allpresets = [OBPresets.RANDOM_PRESET_OBP] + list(OBPresets.opb_presets.keys())

BASE_ARTIST_CATEGORIES = ["popular", "greg mode", "3D",	"abstract",	"angular", "anime"	,"architecture",	"art nouveau",	"art deco",	"baroque",	"bauhaus", 	"cartoon",	"character",	"children's illustration", 	"cityscape", "cinema", 	"clean",	"cloudscape",	"collage",	"colorful",	"comics",	"cubism",	"dark",	"detailed", 	"digital",	"expressionism",	"fantasy",	"fashion",	"fauvism",	"figurativism",	"gore",	"graffiti",	"graphic design",	"high contrast",	"horror",	"impressionism",	"installation",	"landscape",	"light",	"line drawing",	"low contrast",	"luminism",	"magical realism",	"manga",	"melanin",	"messy",	"monochromatic",	"nature",	"nudity",	"photography",	"pop art",	"portrait",	"primitivism",	"psychedelic",	"realism",	"renaissance",	"romanticism",	"scene",	"sci-fi",	"sculpture",	"seascape",	"space",	"stained glass",	"still life",	"storybook realism",	"street art",	"streetscape",	"surrealism",	"symbolism",	"textile",	"ukiyo-e",	"vibrant",	"watercolor",	"whimsical"]
artists = ["all", "all (wild)", "none"] + BASE_ARTIST_CATEGORIES
artifyartists = ["all", "all (wild)"] + BASE_ARTIST_CATEGORIES
# Load imagetypes dynamically
imagetypes = ["all", "all - force multiple", "all - anime", "none"]
# imagetypes += csv_to_list("imagetypes")  # REMOVED legacy simple addon system
imagetypes += ["only other types"]
imagetypes += csv_to_list("imagetypemodes", directory="./csvfiles/special_lists/")
# Load custom modes from JSON
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, "userfiles", "custom_modes.json")
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            custom_modes = json.load(f)
            imagetypes += list(custom_modes.keys())
except Exception as e:
    print(f"OneButtonPrompt: Error loading custom modes for UI: {e}")

all_modes = sorted(list(set(allpresets + list(custom_modes.keys()))))
imagetypes += ["the tokinator"]
subjects =["all", "object", "animal", "humanoid", "landscape", "concept"]
genders = ["all", "male", "female"]
emojis = [False, True]

PROBABILITY_TIERS = ["never", "novel", "extraordinary", "unique", "legendary", "rare", "uncommon", "normal", "common", "always"]

models = ["SD1.5", "SDXL", "Stable Cascade", "Anime Model"]
prompt_enhancers = ["none", "superprompt-v1"]
subjects =["------ all"]
subjectsubtypesobject = ["all"]
subjectsubtypeshumanoid = ["all"]
subjectsubtypesconcept = ["all"]
#subjectsubtypesobject = ["all", "generic objects", "vehicles", "food", "buildings", "space", "flora"]
#subjectsubtypeshumanoid = ["all", "generic humans", "generic human relations", "celebrities e.a.", "fictional characters", "humanoids", "based on job or title", "based on first name"]
#subjectsubtypesconcept = ["all", "event", "the X of Y concepts", "lines from poems", "lines from songs"]

amountofflufflist = ["none", "dynamic", "short", "medium", "long"]
fluff_reverse_polarity = [False,True]

artifymodeslist = ["standard", "remix", "super remix turbo"]
artifyamountofartistslist = ["random", "0", "1", "2", "3", "4", "5"]

superprompterstyleslist = ['all']
superprompterstyleslist += csv_to_list("superprompter_styles")


# Load up stuff for personal artists list, if any
# find all artist files starting with personal_artits in userfiles
script_dir = os.path.dirname(os.path.abspath(__file__))  # Script directory
userfilesfolder = os.path.join(script_dir, "./userfiles/" )
for filename in os.listdir(userfilesfolder):
    if(filename.endswith(".csv") and filename.startswith("personal_artists") and filename != "personal_artists_sample.csv"):
        name = os.path.splitext(filename)[0]
        name = name.replace("_"," ",-1).lower()
        # directly insert into the artists list
        artists.insert(2, name)

# on startup, check if we have a config file, or else create it
config = load_config_csv()  


# load subjects stuff from config
generatevehicle = True
generateobject = True
generatefood = True
generatebuilding = True
generatespace = True
generateflora = True

generateanimal = True
generatebird = True
generatecat = True
generatedog = True
generateinsect = True
generatepokemon = True
generatemarinelife = True

generatemanwoman = True
generatemanwomanrelation = True
generatemanwomanmultiple = True
generatefictionalcharacter = True
generatenonfictionalcharacter = True
generatehumanoids = True
generatejob = True
generatefirstnames = True

generatelandscape = True
generatelocation = True
generatelocationfantasy = True
generatelocationscifi = True
generatelocationvideogame = True
generatelocationbiome = True
generatelocationcity = True

generateevent = True
generateconcepts = True
generatepoemline = True
generatesongline = True
generatecardname = True
generateepisodetitle = True
generateconceptmixer = True


for item in config:
        # objects
        if item[0] == 'subject_vehicle' and item[1] != 'on':
            generatevehicle = False
        if item[0] == 'subject_object' and item[1] != 'on':
            generateobject = False
        if item[0] == 'subject_food' and item[1] != 'on':
            generatefood = False
        if item[0] == 'subject_building' and item[1] != 'on':
            generatebuilding = False
        if item[0] == 'subject_space' and item[1] != 'on':
            generatespace = False
        if item[0] == 'subject_flora' and item[1] != 'on':
            generateflora = False
        # animals
        if item[0] == 'subject_animal' and item[1] != 'on':
            generateanimal = False
        if item[0] == 'subject_bird' and item[1] != 'on':
            generatebird = False
        if item[0] == 'subject_cat' and item[1] != 'on':
            generatecat = False
        if item[0] == 'subject_dog' and item[1] != 'on':
            generatedog = False
        if item[0] == 'subject_insect' and item[1] != 'on':
            generateinsect = False
        if item[0] == 'subject_pokemon' and item[1] != 'on':
            generatepokemon = False
        if item[0] == 'subject_marinelife' and item[1] != 'on':
            generatemarinelife = False
        # humanoids
        if item[0] == 'subject_manwoman' and item[1] != 'on':
            generatemanwoman = False
        if item[0] == 'subject_manwomanrelation' and item[1] != 'on':
            generatemanwomanrelation = False
        if item[0] == 'subject_manwomanmultiple' and item[1] != 'on':
            generatemanwomanmultiple = False
        if item[0] == 'subject_fictional' and item[1] != 'on':
            generatefictionalcharacter = False
        if item[0] == 'subject_nonfictional' and item[1] != 'on':
            generatenonfictionalcharacter = False
        if item[0] == 'subject_humanoid' and item[1] != 'on':
            generatehumanoids = False
        if item[0] == 'subject_job' and item[1] != 'on':
            generatejob = False
        if item[0] == 'subject_firstnames' and item[1] != 'on':
            generatefirstnames = False
        # landscape
        if item[0] == 'subject_location' and item[1] != 'on':
            generatelocation = False
        if item[0] == 'subject_location_fantasy' and item[1] != 'on':
            generatelocationfantasy = False
        if item[0] == 'subject_location_scifi' and item[1] != 'on':
            generatelocationscifi = False
        if item[0] == 'subject_location_videogame' and item[1] != 'on':
            generatelocationvideogame = False
        if item[0] == 'subject_location_biome' and item[1] != 'on':
            generatelocationbiome = False
        if item[0] == 'subject_location_city' and item[1] != 'on':
            generatelocationcity = False
        # concept
        if item[0] == 'subject_event' and item[1] != 'on':
            generateevent = False
        if item[0] == 'subject_concept' and item[1] != 'on':
            generateconcepts = False
        if item[0] == 'subject_poemline' and item[1] != 'on':
            generatepoemline = False
        if item[0] == 'subject_songline' and item[1] != 'on':
            generatesongline = False
        if item[0] == 'subject_cardname' and item[1] != 'on':
            generatecardname = False
        if item[0] == 'subject_episodetitle' and item[1] != 'on':
            generateepisodetitle = False
        if item[0] == 'subject_conceptmixer' and item[1] != 'on':
            generateconceptmixer = False

# build up all subjects we can choose based on the loaded config file
if(generatevehicle or generateobject or generatefood or generatebuilding or generatespace or generateflora):
    subjects.append("--- object - all")
    if(generateobject):
          subjects.append("object - generic")
    if(generatevehicle):
          subjects.append("object - vehicle")
    if(generatefood):
          subjects.append("object - food")
    if(generatebuilding):
          subjects.append("object - building")
    if(generatespace):
          subjects.append("object - space")
    if(generateflora):
          subjects.append("object - flora")
          
if(generateanimal or generatebird or generatecat or generatedog or generateinsect or generatepokemon or generatemarinelife):
    subjects.append("--- animal - all")
    if(generateanimal):
        subjects.append("animal - generic")
    if(generatebird):
        subjects.append("animal - bird")
    if(generatecat):
        subjects.append("animal - cat")
    if(generatedog):
        subjects.append("animal - dog")
    if(generateinsect):
        subjects.append("animal - insect")
    if(generatemarinelife):
        subjects.append("animal - marine life")
    if(generatepokemon):
        subjects.append("animal - pokémon")

if(generatemanwoman or generatemanwomanrelation or generatefictionalcharacter or generatenonfictionalcharacter or generatehumanoids or generatejob or generatemanwomanmultiple):
    subjects.append("--- human - all")
    if(generatemanwoman):
        subjects.append("human - generic")
    if(generatemanwomanrelation):
        subjects.append("human - relations")
    if(generatenonfictionalcharacter):
        subjects.append("human - celebrity")
    if(generatefictionalcharacter):
        subjects.append("human - fictional")
    if(generatehumanoids):
        subjects.append("human - humanoids")
    if(generatejob):
        subjects.append("human - job/title")
    if(generatefirstnames):
        subjects.append("human - first name")
    if(generatemanwomanmultiple):
        subjects.append("human - multiple")

if(generatelandscape or generatelocation or generatelocationfantasy or generatelocationscifi or generatelocationvideogame or generatelocationbiome or generatelocationcity):
    subjects.append("--- landscape - all")
    if(generatelocation):
        subjects.append("landscape - generic")
    if(generatelocationfantasy):
        subjects.append("landscape - fantasy")
    if(generatelocationscifi):
        subjects.append("landscape - sci-fi")
    if(generatelocationvideogame):
        subjects.append("landscape - videogame")
    if(generatelocationbiome):
        subjects.append("landscape - biome")
    if(generatelocationcity):
        subjects.append("landscape - city")

if(generateevent or generateconcepts or generatepoemline or generatesongline or generatecardname or generateepisodetitle or generateconceptmixer):
    subjects.append("--- concept - all")
    if(generateevent):
        subjects.append("concept - event")
    if(generateconcepts):
        subjects.append("concept - the x of y")
    if(generatepoemline):
        subjects.append("concept - poem lines")
    if(generatesongline):
        subjects.append("concept - song lines")
    if(generatecardname):
        subjects.append("concept - card names")
    if(generateepisodetitle):
        subjects.append("concept - episode titles")
    if(generateconceptmixer):
        subjects.append("concept - mixer")


# do the same for the subtype subjects
# subjectsubtypesobject = ["all"]
# subjectsubtypeshumanoid = ["all"]
# subjectsubtypesconcept = ["all"]

# objects first
if(generateobject):
     subjectsubtypesobject.append("generic objects")
if(generatevehicle):
     subjectsubtypesobject.append("vehicles")
if(generatefood):
     subjectsubtypesobject.append("food")
if(generatebuilding):
     subjectsubtypesobject.append("buildings")
if(generatespace):
     subjectsubtypesobject.append("space")
if(generateflora):
     subjectsubtypesobject.append("flora")

# humanoids (should I review descriptions??)
if(generatemanwoman):
     subjectsubtypeshumanoid.append("generic humans")
if(generatemanwomanrelation):
     subjectsubtypeshumanoid.append("generic human relations")
if(generatenonfictionalcharacter):
     subjectsubtypeshumanoid.append("celebrities e.a.")
if(generatefictionalcharacter):
     subjectsubtypeshumanoid.append("fictional characters")
if(generatehumanoids):
     subjectsubtypeshumanoid.append("humanoids")
if(generatejob):
     subjectsubtypeshumanoid.append("based on job or title")
if(generatefirstnames):
     subjectsubtypeshumanoid.append("based on first name")
if(generatemanwomanmultiple):
     subjectsubtypeshumanoid.append("multiple humans")

# concepts
if(generateevent):
     subjectsubtypesconcept.append("event")
if(generateconcepts):
     subjectsubtypesconcept.append("the X of Y concepts")
if(generatepoemline):
     subjectsubtypesconcept.append("lines from poems")
if(generatesongline):
     subjectsubtypesconcept.append("lines from songs")
if(generatecardname):
     subjectsubtypesconcept.append("names from card based games")
if(generateepisodetitle):
     subjectsubtypesconcept.append("episode titles from tv shows")
if(generateconceptmixer):
     subjectsubtypesconcept.append("concept mixer")
     

class OneButtonPrompt:


    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
               
        return {
            "required": {
                "insanitylevel": ("INT", {
                    "default": 5,
                    "min": 1,
                    "max": 10,
                    "step": 1,
                    "tooltip": "Controls randomness: 1-3 conservative, 4-6 balanced (recommended), 7-9 creative, 10 maximum chaos"
                }),
                },
            "optional": {
                "artist": (artists, {
                    "default": "all",
                    "tooltip": "Filter artists by category (e.g., 'fantasy', 'realism') or use 'all' for random selection from everything."
                }),
                "imagetype": (imagetypes, {
                    "default": "all",
                    "tooltip": "Choose a specific format (e.g., 'photograph', 'anime') or select a 'Mode' (e.g., 'Quality Vomit') for specialized prompt internal logic."
                }),
                "imagemodechance": ("INT", {
                    "default": 20,
                    "min": 1,
                    "max": 100,
                    "step": 1,
                    "tooltip": "The random 1-in-X chance to trigger a special 'Mode' (like Color Cannon or Massive Madness) when Image Type is set to 'all'. Lower values = higher chance."
                }),
                "subject": (subjects, {
                    "default": "------ all",
                    "tooltip": "Filter the primary subject category. Selecting a specific category (e.g., 'Animal - Bird') limits generation to that group."
                }),
                "custom_subject": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "tooltip": "Forces a specific subject. OBP will use its 'Smart Subject' logic to build descriptors and environments around it."
                }),
                "custom_outfit": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "tooltip": "Forces a specific outfit. Overrides the random clothing selection for humanoids."
                }),
                "prompt_prefix": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "tooltip": "Hardcoded text added to the very beginning of the prompt."
                }),
                "prompt_suffix": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "tooltip": "Hardcoded text added to the very end of the prompt."
                }),
                "humanoids_gender": (genders, {
                    "default": "all",
                    "tooltip": "Filters names, jobs, and outfits based on gender."
                }),
                "emojis":(emojis, {
                    "default": False,
                    "tooltip": "If enabled, injects relevant emojis into the generated prompt (best for some SDXL models and social media styles)."
                }),
                "base_model":(models, {
                    "default": "SDXL",
                    "tooltip": "Optimizes prompt structure: SD1.5 (heavy weighting), SDXL (natural language & blocks), Cascade (unweighted descriptive strings)."
                }),
                "prompt_enhancer":(prompt_enhancers, {
                    "default": "none",
                    "tooltip": "Uses a local AI (SuperPrompt) to intelligently expand your prompt with highly descriptive details while preserving the original theme."
                }),
                
                "seed": ("INT", {
                    "default": 0, 
                    "min": 0, 
                    "max": 0xFFFFFFFFFFFFFFFF,
                    "tooltip": "Controls the random seed for generation."
                }),
            },
        }

    RETURN_TYPES = ("STRING","STRING", "STRING")
    RETURN_NAMES = ("prompt","prompt_g", "prompt_l")

    FUNCTION = "Comfy_OBP"

    #OUTPUT_NODE = False

    CATEGORY = "OneButtonPrompt"
    
    def Comfy_OBP(self, insanitylevel, custom_subject, seed, artist, imagetype, subject, imagemodechance, humanoids_gender, emojis, custom_outfit, base_model, prompt_enhancer, prompt_prefix, prompt_suffix):
        generatedpromptlist = build_dynamic_prompt(insanitylevel,subject,artist,imagetype,False,"",prompt_prefix,prompt_suffix,1,"",custom_subject,True,"",imagemodechance, humanoids_gender,"all", "all", "all", False, emojis, seed, custom_outfit, True, base_model, "", prompt_enhancer)
        #print(generatedprompt)
        generatedprompt = generatedpromptlist[0]
        prompt_g = generatedpromptlist[1]
        prompt_l = generatedpromptlist[2]

        return (generatedprompt, prompt_g, prompt_l)


class CreatePromptVariant:


    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
               
        return {
            "required": {
                "prompt_input": ("STRING", {
                    "default": '', 
                    "multiline": True,
                    "tooltip": "The base prompt to create a variation from."
                }),
            },
            "optional": {
                "insanitylevel": ("INT", {
                    "default": 5,
                    "min": 1,
                    "max": 10,
                    "step": 1,
                    "tooltip": "Controls how much the variation deviates from the original prompt."
                }),
                "seed": ("INT", {
                    "default": 0, 
                    "min": 0, 
                    "max": 0xFFFFFFFFFFFFFFFF,
                    "tooltip": "Random seed for variation generation."
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)

    FUNCTION = "Comfy_OBP_PromptVariant"

    #OUTPUT_NODE = False

    CATEGORY = "OneButtonPrompt"
    
    def Comfy_OBP_PromptVariant(self, prompt_input, insanitylevel, seed):
        generatedprompt = createpromptvariant(prompt_input, insanitylevel)
        
        print(generatedprompt)
        
        return (generatedprompt,)

# Let us create our own prompt saver. Not everyone has WAS installed
class SavePromptToFile:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "filename_prefix": ("STRING", {
                    "default": "Prompt",
                    "tooltip": "Prefix for the filename. Supports date tags like %date:yyyy-MM-dd%."
                }),
                "positive_prompt": ("STRING", {
                    "multiline": True,
                    "tooltip": "The full positive prompt to save."
                }),
                "negative_prompt": ("STRING", {
                    "multiline": True,
                    "tooltip": "The negative prompt to save."
                }),
            },
            "optional": {
                "prompt_g": ("STRING", {
                    "multiline": True,
                    "tooltip": "SDXL Global prompt block (if applicable)."
                }),
                "prompt_l": ("STRING", {
                    "multiline": True,
                    "tooltip": "SDXL Local prompt block (if applicable)."
                }),
            },
        }

    OUTPUT_NODE = True
    RETURN_TYPES = ()
    FUNCTION = "saveprompttofile"

    CATEGORY = "OneButtonPrompt"

    def saveprompttofile(self, positive_prompt, prompt_g, prompt_l, negative_prompt, filename_prefix):
        # Some stuff for the prefix
        filename_prefix += self.prefix_append

        # turns out there is some hardcoded stuff on saveimage we have to kind of repeat here
        # Find the %date:yyyy-M-d% pattern using regular expression
        pattern = r'%date:([^\%]+)%'
        match = re.search(pattern, filename_prefix)

        if match:
            # Extract the date format from the match
            date_format = match.group(1)

            # Get the current date
            current_date = datetime.now()

            # convert the ComfyUI standard into Python standard format.
            # What a crazy way of doing this
            # first lol, I got to make sure it doesn't overlap things
            date_format = date_format.replace('M', 'X')
            date_format = date_format.replace('m', 'Z')
            
            # This is so bad

            # lets make it even worse, it work differently on windows than in Linux
            if(platform.system() == 'Windows'):

                date_format = date_format.replace('yyyy', '%Y')
                date_format = date_format.replace('yy', '%#y')
                date_format = date_format.replace('X', '%#m')
                date_format = date_format.replace('d', '%#d')
                date_format = date_format.replace('h', '%#H')
                date_format = date_format.replace('Z', '%#M')
                date_format = date_format.replace('s', '%#S')
            else:
                date_format = date_format.replace('yyyy', '%Y')
                date_format = date_format.replace('yy', '%-y')
                date_format = date_format.replace('X', '%-m')
                date_format = date_format.replace('d', '%-d')
                date_format = date_format.replace('h', '%-H')
                date_format = date_format.replace('Z', '%-M')
                date_format = date_format.replace('s', '%-S')


            # Format the date using the extracted format
            formatted_date = current_date.strftime(date_format)

            # Replace the matched pattern with the formatted date
            filename_prefix = re.sub(pattern, formatted_date, filename_prefix)
            

           

        full_output_folder, filename_short, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(filename_prefix, self.output_dir)

        # make the filename, from from a to the first comma
        # find the index of the first comma after "of a" or end of the prompt
        if(positive_prompt.find("of a ") != -1):
            start_index = positive_prompt.find("of a ") + len("of a ")
            end_index = positive_prompt.find(",", start_index)
            if(end_index == -1):
                end_index=len(positive_prompt)
        else:
            start_index = 0
            end_index = 128
  
        # extract the desired substring using slicing
        filename = positive_prompt[start_index:end_index]

        # cleanup some unsafe things in the filename
        filename = filename.replace("\"", "")
        filename = filename.replace("[", "")
        filename = filename.replace("|", "")
        filename = filename.replace("]", "")
        filename = filename.replace("<", "")
        filename = filename.replace(">", "")
        filename = filename.replace(":", "_")
        filename = filename.replace(".", "")
        filename = re.sub(r'[0-9]+', '', filename)

        safe_characters = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.")

        # Use regular expression to filter out any characters not in the whitelist
        filename = re.sub(r"[^{}]+".format(re.escape(''.join(safe_characters))), '', filename)
        

        if(filename==""):
            filename = str(uuid.uuid4())
        
        if(filename_prefix == ""):
        # create a datetime object for the current date and time
        # if there is no prefix
            now = datetime.now()
            filenamecomplete = now.strftime("%Y%m%d%H%M%S") + "_" + filename.replace(" ", "_").strip() + ".txt"
        
        else:
            # lol since we insert a file, the counter of the image goes up by 1.
            # So we add 1 here, so the prompt file matches the image file
            formatted_counter = str(counter + 1).zfill(5)
            filenamecomplete = filename_short + "_" + formatted_counter + "_" + filename.replace(" ", "_").strip() + ".txt"
    
        
        directoryandfilename = os.path.abspath(os.path.join(full_output_folder, filenamecomplete))
        

        with open(directoryandfilename, 'w', encoding="utf-8") as file:
            file.write("prompt: " + positive_prompt + "\n")
            
            if(len(prompt_g) > 0):
                file.write("prompt_g: " + prompt_g + "\n")
            if(len(prompt_l) > 0):
                file.write("prompt_l: " + prompt_l + "\n")
            
            file.write("negative prompt: " + negative_prompt + "\n")



        return ("done")

class OneButtonPreset:

    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
               
        return {
            "required": {
                "OneButtonPreset": (allpresets, {
                    "default": "Standard",
                    "tooltip": "Select a pre-defined generation profile. This will sync the values below."
                }),
                "insanitylevel": ("INT", {
                    "default": 5,
                    "min": 1,
                    "max": 10,
                    "step": 1,
                    "tooltip": "Controls randomness: 1-3 conservative, 4-6 balanced (recommended), 7-9 creative, 10 maximum chaos"
                }),
            },
            "optional": {
                "base_model":(models, {
                    "default": "SDXL",
                    "tooltip": "Optimizes prompt structure: SD1.5 (heavy weighting), SDXL (natural language & blocks), Cascade (unweighted descriptive strings)."
                }),
                "prompt_enhancer":(prompt_enhancers, {
                    "default": "none",
                    "tooltip": "Uses a local AI (SuperPrompt) to intelligently expand your prompt with highly descriptive details while preserving the original theme."
                }),
                "subject": (subjects, {
                    "default": "------ all",
                    "tooltip": "Filter the primary subject category. Selecting a specific category (e.g., 'Animal - Bird') limits generation to that group."
                }),
                "custom_subject": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "tooltip": "Forces a specific subject. OBP will use its 'Smart Subject' logic to build descriptors and environments around it."
                }),
                "custom_outfit": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "tooltip": "Forces a specific outfit. Overrides the random clothing selection for humanoids."
                }),
                "artist": (artists, {
                    "default": "all",
                    "tooltip": "Filter artists by category."
                }),
                "imagetype": (imagetypes, {
                    "default": "all",
                    "tooltip": "Forces a specific style or internal generation mode."
                }),
                "imagemodechance": ("INT", {
                    "default": 20,
                    "min": 1,
                    "max": 100,
                    "step": 1,
                    "tooltip": "The random 1-in-X chance to trigger a special 'Mode' when Image Type is set to 'all'."
                }),
                "humanoids_gender": (genders, {
                    "default": "all",
                    "tooltip": "Filter humanoids by gender or select 'all' for complete randomization."
                }),
                "emojis":(emojis, {
                    "default": False,
                    "tooltip": "If enabled, injects relevant emojis into the generated prompt (best for some SDXL models and social media styles)."
                }),
                "prompt_prefix": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "tooltip": "Hardcoded text added to the very beginning of the prompt."
                }),
                "prompt_suffix": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "tooltip": "Hardcoded text added to the very end of the prompt."
                }),   
                "seed": ("INT", {
                    "default": 0, 
                    "min": 0, 
                    "max": 0xFFFFFFFFFFFFFFFF,
                    "tooltip": "Random seed for the preset generation."
                }),
                "show_advanced": ("BOOLEAN", {
                    "default": False,
                    "label_on": "Show Advanced",
                    "label_off": "Hide Advanced",
                    "tooltip": "Toggle to show/hide advanced settings like probability overrides and custom wildcards."
                }),
                # -- ADVANCED SETTINGS (Hidden by default via JS) --
                "descriptor_density": ("INT", {"default": -1, "min": -1, "max": 9, "step": 1, "display": "slider", "tooltip": "Scale: -1 (Inherit from Global Config), 0 (Never) to 9 (Always). Controls the density of descriptive adjectives for the subject."}),
                "body_type_chance": ("INT", {"default": -1, "min": -1, "max": 9, "step": 1, "display": "slider", "tooltip": "Scale: -1 (Inherit from Global Config), 0 (Never) to 9 (Always). Odds of adding body type/build modifiers."}),
                "outfit_chance": ("INT", {"default": -1, "min": -1, "max": 9, "step": 1, "display": "slider", "tooltip": "Scale: -1 (Inherit from Global Config), 0 (Never) to 9 (Always). Odds of generating specific clothing/outfits."}),
                "hair_chance": ("INT", {"default": -1, "min": -1, "max": 9, "step": 1, "display": "slider", "tooltip": "Scale: -1 (Inherit from Global Config), 0 (Never) to 9 (Always). Odds of generating hair styles and colors."}),
                "accessory_chance": ("INT", {"default": -1, "min": -1, "max": 9, "step": 1, "display": "slider", "tooltip": "Scale: -1 (Inherit from Global Config), 0 (Never) to 9 (Always). Odds of adding items like glasses, jewelry, or tech."}),
                "face_detail_chance": ("INT", {"default": -1, "min": -1, "max": 9, "step": 1, "display": "slider", "tooltip": "Scale: -1 (Inherit from Global Config), 0 (Never) to 9 (Always). Odds of adding facial features like freckles, makeup, or scars."}),
                "expression_chance": ("INT", {"default": -1, "min": -1, "max": 9, "step": 1, "display": "slider", "tooltip": "Scale: -1 (Inherit from Global Config), 0 (Never) to 9 (Always). Odds of adding distinct emotions or expressions."}),
                "pose_chance": ("INT", {"default": -1, "min": -1, "max": 9, "step": 1, "display": "slider", "tooltip": "Scale: -1 (Inherit from Global Config), 0 (Never) to 9 (Always). Odds of choosing a specific physical stance or action pose."}),
                "background_chance": ("INT", {"default": -1, "min": -1, "max": 9, "step": 1, "display": "slider", "tooltip": "Scale: -1 (Inherit from Global Config), 0 (Never) to 9 (Always). Odds of adding setting details (interior, exterior, etc.)."}),
                "mood_chance": ("INT", {"default": -1, "min": -1, "max": 9, "step": 1, "display": "slider", "tooltip": "Scale: -1 (Inherit from Global Config), 0 (Never) to 9 (Always). Odds of adding atmospheric mood modifiers."}),
                "lighting_chance": ("INT", {"default": -1, "min": -1, "max": 9, "step": 1, "display": "slider", "tooltip": "Scale: -1 (Inherit from Global Config), 0 (Never) to 9 (Always). Odds of adding specific lighting setups (neon, god rays, etc.)."}),
                "color_scheme_chance": ("INT", {"default": -1, "min": -1, "max": 9, "step": 1, "display": "slider", "tooltip": "Scale: -1 (Inherit from Global Config), 0 (Never) to 9 (Always). Odds of enforcing a specific color palette."}),
                "lens_chance": ("INT", {"default": -1, "min": -1, "max": 9, "step": 1, "display": "slider", "tooltip": "Scale: -1 (Inherit from Global Config), 0 (Never) to 9 (Always). Odds of adding camera lens effects like bokeh or macro."}),
                "shot_size_chance": ("INT", {"default": -1, "min": -1, "max": 9, "step": 1, "display": "slider", "tooltip": "Scale: -1 (Inherit from Global Config), 0 (Never) to 9 (Always). Odds of adding framing descriptors (close-up, wide-shot)."}),
                "art_movement_chance": ("INT", {"default": -1, "min": -1, "max": 9, "step": 1, "display": "slider", "tooltip": "Scale: -1 (Inherit from Global Config), 0 (Never) to 9 (Always). Odds of adding historical or modern art movements."}),
                "quality_chance": ("INT", {"default": -1, "min": -1, "max": 9, "step": 1, "display": "slider", "tooltip": "Scale: -1 (Inherit from Global Config), 0 (Never) to 9 (Always). Odds of adding quality-enhancing tokens (masterpiece, 8k, etc.)."}),
                
                "save_preset_name": ("STRING", {"default": "", "tooltip": "Enter a name to save current sliders as a new preset. NOTE: You must restart ComfyUI for the new preset to appear in the dropdown list."}),
                
                "prompt_prefix_mode": ("STRING", {"default": "", "tooltip": "Custom Mode Prefix (added after standard prefix)"}),
                "prompt_suffix_mode": ("STRING", {"default": "", "tooltip": "Custom Mode Suffix (added before standard suffix)"}),
                "custom_wildcard_1": (SUPPORTED_WILDCARDS, {"default": "", "tooltip": "First custom wildcard to add to the loop"}),
                "custom_wildcard_1_chance": ("INT", {"default": 0, "min": 0, "max": 9, "step": 1, "display": "slider", "tooltip": "Chance (0-9) to include Wildcard 1"}),
                "custom_wildcard_2": (SUPPORTED_WILDCARDS, {"default": "", "tooltip": "Second custom wildcard"}),
                "custom_wildcard_2_chance": ("INT", {"default": 0, "min": 0, "max": 9, "step": 1, "display": "slider", "tooltip": "Chance (0-9) to include Wildcard 2"}),
                "custom_wildcard_3": (SUPPORTED_WILDCARDS, {"default": "", "tooltip": "Third custom wildcard"}),
                "custom_wildcard_3_chance": ("INT", {"default": 0, "min": 0, "max": 9, "step": 1, "display": "slider", "tooltip": "Chance (0-9) to include Wildcard 3"}),
                "custom_wildcard_4": (SUPPORTED_WILDCARDS, {"default": "", "tooltip": "Fourth custom wildcard"}),
                "custom_wildcard_4_chance": ("INT", {"default": 0, "min": 0, "max": 9, "step": 1, "display": "slider", "tooltip": "Chance (0-9) to include Wildcard 4"}),
            },
        }


    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)

    FUNCTION = "Comfy_OBP_OneButtonPreset"

    #OUTPUT_NODE = False

    CATEGORY = "OneButtonPrompt"
    
    def Comfy_OBP_OneButtonPreset(self, OneButtonPreset, insanitylevel, base_model, prompt_enhancer, subject, custom_subject, custom_outfit, artist, imagetype, imagemodechance, humanoids_gender, emojis, prompt_prefix, prompt_suffix, seed, descriptor_density, body_type_chance, outfit_chance, hair_chance, accessory_chance, face_detail_chance, expression_chance, pose_chance, background_chance, mood_chance, lighting_chance, color_scheme_chance, lens_chance, shot_size_chance, art_movement_chance, quality_chance, save_preset_name, prompt_prefix_mode, prompt_suffix_mode, custom_wildcard_1, custom_wildcard_1_chance, custom_wildcard_2, custom_wildcard_2_chance, custom_wildcard_3, custom_wildcard_3_chance, custom_wildcard_4, custom_wildcard_4_chance, show_advanced=False):
        # Build chance overrides
        mapping = {
            "descriptor_density": ["subjectdescriptor1chance", "subjectdescriptor2chance"],
            "body_type_chance": ["subjectbodytypechance"],
            "outfit_chance": ["outfitchance"],
            "hair_chance": ["hairchance"],
            "accessory_chance": ["accessorychance"],
            "face_detail_chance": ["buildfacechance"],
            "expression_chance": ["humanexpressionchance"],
            "pose_chance": ["posechance"],
            "background_chance": ["humanoidbackgroundchance"],
            "mood_chance": ["moodchance"],
            "lighting_chance": ["lightingchance"],
            "color_scheme_chance": ["colorschemechance"],
            "lens_chance": ["lenschance"],
            "shot_size_chance": ["shotsizechance"],
            "art_movement_chance": ["artmovementchance"],
            "quality_chance": ["quality1chance", "quality2chance"],
        }
        
        chance_overrides = {}
        # locals() logic to get slider values
        for slider, targets in mapping.items():
            val = locals().get(slider, -1)
            if val != -1:
                tier = PROBABILITY_TIERS[val]
                for target in targets:
                    chance_overrides[target] = tier

        # load the base preset
        if(OneButtonPreset == OBPresets.RANDOM_PRESET_OBP):
            selected_opb_preset = OBPresets.get_obp_preset("Standard")
        else:
            selected_opb_preset = OBPresets.get_obp_preset(OneButtonPreset)
        
        # Override preset dict with UI values
        # Since we are "syncing" the UI, these values ARE what the user wants.
        selected_opb_preset["insanitylevel"] = insanitylevel
        selected_opb_preset["subject"] = subject
        selected_opb_preset["artist"] = artist
        selected_opb_preset["imagetype"] = imagetype
        selected_opb_preset["imagemodechance"] = imagemodechance
        selected_opb_preset["chosengender"] = humanoids_gender
        selected_opb_preset["givensubject"] = custom_subject
        selected_opb_preset["givenoutfit"] = custom_outfit
        selected_opb_preset["prefixprompt"] = prompt_prefix
        selected_opb_preset["suffixprompt"] = prompt_suffix
        selected_opb_preset["base_model"] = base_model
        selected_opb_preset["prompt_enhancer"] = prompt_enhancer
        # emojis is inverted in the engine calls usually or handled separately
        
        # Build prompt_parts from UI inputs
        ui_prompt_parts = []
        for i in range(1, 5):
            wc = locals().get(f"custom_wildcard_{i}", "")
            ch = locals().get(f"custom_wildcard_{i}_chance", 0)
            if wc.strip() != "" and ch > 0:
                ui_prompt_parts.append({
                    "wildcard": wc.strip(), 
                    "chance": PROBABILITY_TIERS[ch]
                })

        # Logic Merge: Use UI custom mode settings if they exist, otherwise keep preset values
        has_ui_custom_mode = (prompt_prefix_mode.strip() != "" or prompt_suffix_mode.strip() != "" or len(ui_prompt_parts) > 0)
        
        current_prompt_parts = ui_prompt_parts if has_ui_custom_mode else selected_opb_preset.get("prompt_parts", [])
        current_prefix_mode = prompt_prefix_mode if has_ui_custom_mode else selected_opb_preset.get("prompt_prefix_mode", "")
        current_suffix_mode = prompt_suffix_mode if has_ui_custom_mode else selected_opb_preset.get("prompt_suffix_mode", "")

        # If saving, construct the dict and save
        if save_preset_name.strip() != "":
            save_dict = selected_opb_preset.copy()
            # update with our slider overrides
            for k, v in chance_overrides.items():
                save_dict[k] = v
            
            # Save the custom mode configuration
            save_dict["prompt_parts"] = current_prompt_parts
            save_dict["prompt_prefix_mode"] = current_prefix_mode
            save_dict["prompt_suffix_mode"] = current_suffix_mode
            
            OBPresets.add_custom_preset(save_preset_name.strip(), save_dict)
            print(f"Saved custom preset: {save_preset_name}")

        # Extract values for the engine call
        insanitylevel = selected_opb_preset["insanitylevel"]
        subject = selected_opb_preset["subject"]
        artist = selected_opb_preset["artist"]
        chosensubjectsubtypeobject = selected_opb_preset["chosensubjectsubtypeobject"]
        chosensubjectsubtypehumanoid = selected_opb_preset["chosensubjectsubtypehumanoid"]
        chosensubjectsubtypeconcept = selected_opb_preset["chosensubjectsubtypeconcept"]
        chosengender = selected_opb_preset["chosengender"]
        imagetype = selected_opb_preset["imagetype"]
        imagemodechance = selected_opb_preset["imagemodechance"]
        givensubject = selected_opb_preset["givensubject"]
        smartsubject = selected_opb_preset["smartsubject"]
        givenoutfit = selected_opb_preset["givenoutfit"]
        prefixprompt = selected_opb_preset["prefixprompt"]
        suffixprompt = selected_opb_preset["suffixprompt"]
        giventypeofimage = selected_opb_preset.get("giventypeofimage", "")
        antistring = selected_opb_preset.get("antistring", "")
        
        # Extract inline custom mode config
        preset_custom_mode_config = None
        if current_prompt_parts:
            preset_custom_mode_config = {
                "prompt_parts": current_prompt_parts,
                "prompt_prefix": current_prefix_mode,
                "prompt_suffix": current_suffix_mode,
            }

        generatedpromptlist = build_dynamic_prompt(insanitylevel=insanitylevel,
                                               forcesubject=subject,
                                               artists=artist,
                                               subtypeobject=chosensubjectsubtypeobject,
                                               subtypehumanoid=chosensubjectsubtypehumanoid,
                                               subtypeconcept=chosensubjectsubtypeconcept,
                                               gender=chosengender,
                                               imagetype=imagetype,
                                               imagemodechance=imagemodechance,
                                               givensubject=givensubject,
                                               smartsubject=smartsubject,
                                               overrideoutfit=givenoutfit,
                                               prefixprompt=prefixprompt,
                                               suffixprompt=suffixprompt,
                                               giventypeofimage=giventypeofimage,
                                               antivalues=antistring,
                                               advancedprompting=False,
                                               hardturnoffemojis=not emojis,
                                               seed=seed,
                                               base_model=base_model,
                                               OBP_preset="",
                                               prompt_enhancer=prompt_enhancer,
                                               chance_overrides=chance_overrides,
                                               custom_mode_config=preset_custom_mode_config,
                                               )
        
        generatedprompt = generatedpromptlist[0]
        return (generatedprompt,)

class AutoNegativePrompt:


    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
               
        return {
            "required": {
                "postive_prompt": ("STRING", {
                    "default": '', 
                    "multiline": True,
                    "tooltip": "The positive prompt to generate a matching negative for."
                }),
            },
            "optional": {
                "base_negative": ("STRING", {
                    "multiline": True,
                    "default": "text, watermark",
                    "tooltip": "Static negative terms to always include."
                }),
                "enhancenegative": ("INT", {
                    "default": 0, 
                    "min": 0, 
                    "max": 1, 
                    "step": 1,
                    "tooltip": "Adds a standard suite of negative terms for common artifacts (e.g., 'low quality', 'text'). 1 = on, 0 = off."
                }),
                "insanitylevel": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 10,
                    "step": 1,
                    "tooltip": "Randomly chooses negative terms suited to the content of your positive prompt (e.g., adds 'water' to negative if prompt is about land)."
                }),
                "base_model":(models, {
                    "default": "SDXL",
                    "tooltip": "Format the negative prompt for a specific model architecture."
                }),
                
                "seed": ("INT", {
                    "default": 0, 
                    "min": 0, 
                    "max": 0xFFFFFFFFFFFFFFFF,
                    "tooltip": "Random seed for negative term selection."
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("negative_prompt",)

    FUNCTION = "Comfy_OBP_AutoNegativePrompt"

    #OUTPUT_NODE = False

    CATEGORY = "OneButtonPrompt"
    
    def Comfy_OBP_AutoNegativePrompt(self, postive_prompt, insanitylevel, enhancenegative,base_negative, seed, base_model):
        generatedprompt = build_dynamic_negative(postive_prompt, insanitylevel, enhancenegative, base_negative, base_model=base_model)
        
        print("Generated negative prompt: " + generatedprompt)
        
        return (generatedprompt,)
    
class OneButtonArtify:

    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
               
        return {
            "required": {
                "prompt": ("STRING", {
                    "default": '', 
                    "multiline": True,
                    "tooltip": "The base prompt to apply artistic styles onto."
                }),
                "artist": (artifyartists, {
                    "default": "all",
                    "tooltip": "Filter the artistic style by category."
                }),
                "amount_of_artists": (artifyamountofartistslist, {
                    "default": "1",
                    "tooltip": "Number of random artists to blend into the prompt."
                }),
                "artify_mode": (artifymodeslist, {
                    "default": "standard",
                    "tooltip": "Selection logic: Standard (appends artists), Remix (interweaves artists with [A|B] syntax), Super Remix (uses advanced switching)."
                })
            },
            "optional": {                
                "seed": ("INT", {
                    "default": 0, 
                    "min": 0, 
                    "max": 0xFFFFFFFFFFFFFFFF,
                    "tooltip": "Random seed for artist selection."
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("artified_prompt",)

    FUNCTION = "Comfy_OBP_Artify"

    #OUTPUT_NODE = False

    CATEGORY = "OneButtonPrompt"
    
    def Comfy_OBP_Artify(self, prompt, artist, amount_of_artists,artify_mode, seed):
        # artify here
        artified_prompt = artify_prompt(prompt=prompt, artists=artist, amountofartists=amount_of_artists, mode=artify_mode, seed=seed)
        
        print("Artified prompt: " + artified_prompt)
        
        return (artified_prompt,)

class OneButtonFlufferize:

    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
               
        return {
            "required": {
                "prompt": ("STRING", {
                    "default": '', 
                    "multiline": True,
                    "tooltip": "The base prompt to add descriptive 'fluff' to."
                }),
                "amount_of_fluff": (amountofflufflist, {
                    "default": "dynamic",
                    "tooltip": "How many extra descriptors to add (dynamic = based on input length)."
                }),
                "reverse_polarity": (fluff_reverse_polarity, {
                    "default": False,
                    "tooltip": "If enabled, uses 'negative' aesthetic fluff (e.g., 'gritty', 'noir', 'decaying') instead of high-quality/pristine descriptors."
                }),
            },
            "optional": {                
                "seed": ("INT", {
                    "default": 0, 
                    "min": 0, 
                    "max": 0xFFFFFFFFFFFFFFFF,
                    "tooltip": "Random seed for descriptor selection."
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("fluffed_prompt",)

    FUNCTION = "Comfy_OBP_Flufferize"

    #OUTPUT_NODE = False

    CATEGORY = "OneButtonPrompt"
    
    def Comfy_OBP_Flufferize(self, prompt, amount_of_fluff, reverse_polarity, seed):
        # artify here
        fluffed_prompt = flufferizer(prompt=prompt, amountoffluff=amount_of_fluff, reverse_polarity=reverse_polarity, seed=seed)
        
        print("Fluffed prompt: " + fluffed_prompt)
        
        return (fluffed_prompt,)

class OneButtonSuperPrompt:

    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
               
        return {
            "required": {
                "prompt": ("STRING", {
                    "default": '', 
                    "multiline": True,
                    "tooltip": "Short prompt to be expanded by AI."
                }),
                "insanitylevel": ("INT", {
                    "default": 5,
                    "min": 1,
                    "max": 10,
                    "step": 1,
                    "tooltip": "Higher levels allow the AI more creative freedom."
                }),
                "superpromptstyle": (superprompterstyleslist, {
                    "default": "all",
                    "tooltip": "Filter the expansion style (fantasy, sci-fi, etc.)."
                }),
            },
            "optional": {                
                "seed": ("INT", {
                    "default": 0, 
                    "min": 0, 
                    "max": 0xFFFFFFFFFFFFFFFF,
                    "tooltip": "Seed for AI generation."
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("super_prompt",)

    FUNCTION = "Comfy_OBP_SuperPrompt"

    #OUTPUT_NODE = False

    CATEGORY = "OneButtonPrompt"
    
    def Comfy_OBP_SuperPrompt(self, insanitylevel, prompt, superpromptstyle, seed):

        OBPsuperprompt = one_button_superprompt(insanitylevel=insanitylevel, prompt=prompt, seed=seed, superpromptstyle=superpromptstyle)
        
        print("Super prompt: " + OBPsuperprompt)
        
        return (OBPsuperprompt,)


class OneButtonPrompt_Simple:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "mode": (all_modes, {"default": "Standard"}),
                "insanitylevel": ("INT", {"default": 5, "min": 0, "max": 10, "step": 1}),
                "base_model": (models, {"default": "SD1.5"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "prompt_enhancer": (prompt_enhancers, {"default": "none"}),
                "subject": (subjects, {"default": "------ all"}),
                "artist": (artists, {"default": "all"}),
                "imagetype": (imagetypes, {"default": "all"}),
                "custom_subject": ("STRING", {"default": ""}),
                "prompt_prefix": ("STRING", {"default": ""}),
                "prompt_suffix": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "generate"
    CATEGORY = "OneButtonPrompt"

    def generate(self, mode, insanitylevel, base_model, seed, prompt_enhancer="none", subject="all", artist="all", imagetype="all", custom_subject="", prompt_prefix="", prompt_suffix=""):
        # Determine if it's a preset or a custom mode
        custom_mode_config = None
        preset_name = ""
        effective_imagetype = "all"
        
        if mode in custom_modes:
            custom_mode_config = custom_modes[mode]
            effective_imagetype = mode
        elif mode in OBPresets.opb_presets:
            preset_name = mode
        elif mode == OBPresets.RANDOM_PRESET_OBP:
            preset_name = mode

        # Logic Override: If user explicitly selects a type via dropdown, it overrides the mode-derived type
        if imagetype != "all":
            effective_imagetype = imagetype

        # Call engine
        generatedpromptlist = build_dynamic_prompt(
            insanitylevel=insanitylevel,
            seed=seed,
            base_model=base_model,
            prompt_enhancer=prompt_enhancer,
            forcesubject=subject,
            artists=artist,
            imagetype=effective_imagetype,
            OBP_preset=preset_name,
            custom_mode_config=custom_mode_config,
            givensubject=custom_subject,
            prefixprompt=prompt_prefix,
            suffixprompt=prompt_suffix
        )
        
        return (generatedpromptlist[0],)

# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "OneButtonPrompt": OneButtonPrompt,
    "OneButtonPreset": OneButtonPreset,
    "OneButtonPrompt_Simple": OneButtonPrompt_Simple,
    "OneButtonArtify": OneButtonArtify,
    "CreatePromptVariant": CreatePromptVariant,
    "SavePromptToFile": SavePromptToFile,
    "AutoNegativePrompt": AutoNegativePrompt,
    "OneButtonFlufferize": OneButtonFlufferize,
    "OneButtonSuperPrompt": OneButtonSuperPrompt,
    
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "OneButtonPrompt": "One Button Prompt",
    "OneButtonPreset": "One Button Preset",
    "OneButtonPrompt_Simple": "One Button Prompt Lite",
    "OneButtonArtify": "One Button Artify",
    "CreatePromptVariant": "Create Prompt Variant",
    "SavePromptToFile": "Save Prompt To File",
    "AutoNegativePrompt": "Auto Negative Prompt",
    "OneButtonFlufferize": "One Button Flufferize",
    "OneButtonSuperPrompt": "One Button SuperPrompt",
}