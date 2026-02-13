# OneButtonPrompt Architecture Guide

## Quick Technical Overview

OneButtonPrompt builds prompts by randomly selecting keywords from 130+ CSV files (3,500+ artists, subjects, styles, descriptors) and combining them with comma separators. The "insanity level" (1-10) controls selection probability for each element.

**Core Mechanism:**
- **CSV Data Layer**: Text files containing all possible prompt elements
- **Probability Engine**: Each element has a chance of being included (e.g., 50% at level 5 for "normal" elements)
- **Pipeline**: Subject selection → Element rolling → Keyword concatenation → Model formatting
- **Model Adaptation**: 
  - SD1.5/Anime: Keywords only (`portrait, woman, red hair`)
  - SDXL: Adds filler words (`portrait, the woman is red haired`)
  - Stable Cascade: Strips weight syntax `(keyword:1.2)` → `keyword`

**Example at insanity 5:**
```
Subject: "Warrior" (always) ✓
Artist: "Frank Frazetta" (27% chance) ✓
Art movement: "Fantasy Art" (16% chance) ✓
Lighting: "dramatic lighting" (50% chance) ✓
Camera: "wide shot" (16% chance) ✗

Result: "by Frank Frazetta, fantasy art, fierce Warrior, dramatic lighting, detailed"
```

For detailed technical documentation, see sections below.

---

## Overview

OneButtonPrompt is a sophisticated AI prompt generation system designed for Stable Diffusion image generation. It provides automated, controlled randomness to create diverse and interesting prompts for beginners and advanced users alike. The system supports multiple platforms including Automatic1111 WebUI, ComfyUI, and RuinedFooocus.

## Core Architecture

### 1. Multi-Platform Design

The system is architected to work across different AI image generation platforms:

- **Automatic1111 WebUI**: Script-based integration via `scripts/` directory
- **ComfyUI**: Custom node integration via `OneButtonPromptNodes.py`
- **RuinedFooocus**: Built-in integration
- **Web Interface**: Standalone web version at airjen.pythonanywhere.com

### 2. Modular Component Structure

```
OneButtonPrompt/
├── Core Engine
│   ├── build_dynamic_prompt.py    # Main prompt generation logic
│   ├── csv_reader.py              # Data loading and management
│   ├── random_functions.py        # Probability distribution functions
│   └── one_button_presets.py      # Preset management system
├── Platform Integrations
│   ├── OneButtonPromptNodes.py    # ComfyUI custom nodes
│   ├── scripts/                   # A1111 WebUI scripts
│   └── main.py                    # Standalone execution
├── API Interfaces
│   ├── call_txt2img.py           # Text-to-image API calls
│   ├── call_img2img.py           # Image-to-image API calls
│   └── call_extras.py            # Additional processing APIs
├── Data Layer
│   ├── csvfiles/                 # Core data definitions
│   ├── userfiles/                # User customizations
│   └── presets/                  # Preset configurations
└── Enhancement Modules
    ├── superprompter/            # AI prompt enhancement
    └── example_workflows/        # Usage examples
```

## Core Systems

### 1. Prompt Generation Engine (`build_dynamic_prompt.py`)

The heart of the system is a sophisticated prompt builder that constructs prompts through a multi-stage pipeline:

**Key Features:**
- **Controlled Randomness**: Uses probability distributions (common, normal, uncommon, rare, legendary, unique, extraordinary, novel)
- **Subject-Based Generation**: Supports objects, animals, humanoids, landscapes, and concepts
- **Multi-Model Support**: Adapts output for SD1.5, SDXL, Stable Cascade, and Anime models
- **Advanced Prompting**: Supports prompt weighting, switching, and hybrid techniques
- **Smart Subject Logic**: Automatically adjusts generation based on user input

**How It Works:**

The prompt generation follows a structured pipeline:

1. **Initialization Phase:**
   - Loads configuration based on base model (SD1.5, SDXL, Stable Cascade, Anime)
   - Sets verbosity level (`less_verbose` for SD1.5/Anime, full for SDXL)
   - Determines if weights should be removed (Stable Cascade)
   - Applies preset overrides if specified

2. **Subject Selection:**
   - Chooses main category: object, animal, humanoid, landscape, or concept
   - Selects specific subtype based on configuration and user preferences
   - Applies gender filtering for humanoid subjects
   - Respects user-provided custom subjects with smart detection

3. **Prompt Building Stages:**
   ```
   [Artist Prefix] → [Image Type] → [Shot Size] → @@@ → 
   [Subject Descriptors] → [Main Subject] → [Subject Details] → 
   [Location/Background] → [Technical Details] → [Quality/Style]
   ```

4. **Wildcard Replacement:**
   - Replaces `-artist-` with selected artists from filtered lists
   - Substitutes `-subject-` with generated subject
   - Processes `-outfit-`, `-location-`, `-descriptor-` wildcards
   - Handles nested wildcards and OR() statements

5. **Advanced Prompting Techniques:**
   - **Weighting**: `(artist:1.2)` for emphasis control
   - **Switching**: `[artist1:artist2:10]` changes at step 10
   - **Hybrid**: `[artist1|artist2]` blends both
   - **Stopping**: `[element::15]` stops influence at step 15
   - **Adding**: `[element:10]` starts influence at step 10

6. **Cleanup and Finalization:**
   - Removes extra commas and spaces
   - Validates prompt structure
   - Applies prefix/suffix from presets
   - Returns final prompt (and prompt_g/prompt_l for SDXL)

**Generation Modes:**

Each mode modifies the generation pipeline differently:

- **Standard Mode**: Balanced random generation
  - Uses all probability distributions normally
  - Includes artists, subjects, and style elements
  - Respects insanity level for complexity

- **Template Mode**: Uses predefined prompt templates
  - Loads from `csvfiles/templates/styles.csv`
  - Format: `[prefix]-subject-[suffix]`
  - Replaces subject placeholder with generated content

- **Art Blaster Mode**: Focuses on artistic styles and artists
  - Generates 1 to insanitylevel iterations
  - Each iteration adds: artist, art movement, vomit, imagetype, colorscheme
  - Heavy emphasis on artistic terminology

- **Quality Vomit Mode**: Emphasizes quality descriptors
  - Adds multiple quality terms from `quality.csv`
  - Includes fluff descriptors for enhancement
  - Stacks quality modifiers for emphasis

- **Color Cannon Mode**: Emphasizes color and mood
  - Prioritizes mood and color scheme selection
  - Adds lighting and art movement for atmosphere
  - Uses style suffix combinations

- **Photo Fantasy Mode**: Optimized for photographic styles
  - Forces "photograph" as image type
  - Adds photo-specific additions (lighting, camera, lens)
  - Includes technical photography terms

- **Massive Madness Mode**: Maximum randomness and complexity
  - Generates 1 to insanitylevel iterations
  - Each iteration can add ANY element type
  - No restrictions on combinations
  - Highest chance of unusual results

- **Subject Only Mode**: Minimal generation around core subject
  - Skips most decorative elements
  - Focuses purely on subject description
  - Often used with Artify mode for post-processing

- **Fixed Styles Mode**: Uses curated style templates
  - Loads complete style definitions from `styles.csv`
  - Applies consistent artistic direction
  - Minimal randomization for predictable results

- **The Tokinator**: Completely random token generation
  - Loads from `tokens.csv` (5000+ random words)
  - Replaces ALL wildcards with random tokens
  - No logic or coherence checking
  - Maximum chaos mode

- **Dynamic Templates Mode**: Adaptive template system
  - Uses `dynamic_templates_prefix.csv` and `dynamic_templates_suffix.csv`
  - Intelligently combines prefix and suffix templates
  - Adapts based on artist selection and subject type
  - More flexible than fixed templates

**Mode Selection Logic:**
```python
if random.randint(1, imagemodechance) == 1:
    # Special mode triggered
    mode = random.choice(imagetypemodelist)
else:
    # Standard generation
    mode = "standard"
```

### 2. Data Management System (`csv_reader.py`)

**CSV-Based Architecture:**
- **Core Data**: 130+ CSV files containing subjects, artists, styles, etc.
- **User Customization**: Support for user-defined additions and replacements
- **Hierarchical Loading**: Default → User Addon → User Replace priority
- **Gender-Aware**: Supports gender-specific content filtering
- **Insanity-Level Filtering**: Adjusts content complexity based on settings

**How It Works:**

The CSV system provides a flexible, text-based data layer that's easy to modify without code changes:

1. **File Loading Process:**
   ```python
   def csv_to_list(csvfilename, antilist=[], directory="./csvfiles/", 
                   lowerandstrip=0, delimiter=";", listoflistmode=False, 
                   skipheader=False, gender="all", insanitylevel=-1):
   ```

   **Loading Priority:**
   - Check for `userfiles/{filename}_replace.csv` → Use exclusively if found
   - Load `csvfiles/{filename}.csv` → Base data
   - Check for `userfiles/{filename}_addon.csv` → Append if found
   - Apply insanity-level filtering (light/medium/full lists)
   - Filter by gender if applicable
   - Remove items in antilist
   - Deduplicate while preserving case

2. **Insanity-Level Filtering:**
   ```
   insanitylevel < 4:  Use {filename}_light.csv (if exists)
   insanitylevel < 7:  Use {filename}_medium.csv (if exists) 
   insanitylevel >= 7: Use full {filename}.csv
   ```
   
   This allows curated subsets for lower insanity levels:
   - Light: ~20-30% of full list, most common/safe items
   - Medium: ~50-60% of full list, balanced selection
   - Full: Complete list, all items available

3. **Gender-Aware Filtering:**
   
   CSV files can include gender column:
   ```csv
   item_name,gender,category
   "Warrior Princess",female,fictional
   "Space Marine",male,fictional
   "Robot",genderless,humanoid
   "Adventurer",both,job
   ```
   
   Filtering logic:
   - `gender="male"`: Returns male + genderless + both
   - `gender="female"`: Returns female + genderless + both
   - `gender="all"`: Returns everything

4. **Artist Category System:**
   
   Special handling for `artists_and_category.csv`:
   ```python
   def artist_category_csv_to_list(csvfilename, category):
       # Returns artists where category column = "1"
   ```
   
   Structure:
   ```csv
   Artist,Tags,Medium,Description,fantasy,sci-fi,portrait,...
   "Greg Rutkowski","digital,fantasy","digital art","...",1,0,1,...
   ```
   
   This enables:
   - Multi-category artist classification
   - Style-based artist filtering
   - Medium-specific selections
   - Description-based enhancements

5. **User Customization System:**

   **Addon Files** (`*_addon.csv`):
   - Appends to existing lists
   - Same format as base files
   - Merged after base loading
   - Duplicates automatically removed
   
   Example `vehicles_addon.csv`:
   ```csv
   Cybertruck,genderless
   Flying DeLorean,genderless
   Hoverbike,genderless
   ```

   **Replace Files** (`*_replace.csv`):
   - Completely overrides base file
   - Useful for total customization
   - Must include all desired items
   - Checked first in loading priority
   
   Example `artists_replace.csv`:
   ```csv
   My Favorite Artist
   Another Great Artist
   Local Artist Name
   ```

   **Antilist System** (`antilist.csv`):
   - Global exclusion list
   - Items never appear in generation
   - Case-insensitive matching
   - Applied to all CSV loads
   
   Example:
   ```csv
   unwanted_term
   another_excluded_item
   banned_artist
   ```

6. **Special List Types:**

   **List of Lists Mode:**
   - Returns nested structure for complex data
   - Used for templates and multi-part definitions
   - Preserves row structure
   
   **Delimiter Variations:**
   - Default: `;` (semicolon)
   - Alternative: `?` for special lists
   - Allows commas within items
   - Flexible parsing for complex data

7. **Caching and Performance:**
   
   - CSV files loaded once at module initialization
   - Lists stored in memory for fast access
   - No disk I/O during generation
   - Deduplication reduces memory footprint
   - Typical memory usage: ~50MB for full dataset

**Key Data Categories:**
- **Artists**: 3483 artists across 40+ categories
- **Subjects**: Objects, animals, humanoids, landscapes, concepts
- **Styles**: Art movements, image types, quality descriptors
- **Technical**: Camera settings, lighting, composition
- **Descriptors**: Adjectives, moods, colors, materials

**CSV File Organization:**
```
csvfiles/
├── Core Subjects
│   ├── animals.csv, birds.csv, cats.csv, dogs.csv
│   ├── objects.csv, vehicles.csv, buildings.csv
│   ├── humanoids.csv, jobs.csv, firstnames.csv
│   └── locations.csv, locationsfantasy.csv, etc.
├── Artists & Styles
│   ├── artists.csv (3483 artists)
│   ├── artists_and_category.csv (categorized)
│   ├── artmovements.csv
│   └── gregmode.csv (popular artists)
├── Descriptors
│   ├── descriptors.csv (general)
│   ├── humandescriptors.csv
│   ├── animaldescriptors.csv
│   ├── outfitdescriptors.csv
│   └── locationdescriptors.csv
├── Technical
│   ├── cameras.csv, lenses.csv
│   ├── lighting.csv, focus.csv
│   ├── shotsizes.csv, directions.csv
│   └── colorscheme.csv, moods.csv
├── Quality & Enhancement
│   ├── quality.csv, vomit.csv
│   ├── fluff.csv, minivomit.csv
│   └── imagetypequality.csv
└── Special Lists (csvfiles/special_lists/)
    ├── buildhair.csv, buildoutfit.csv
    ├── buildface.csv, buildaccessorie.csv
    ├── humanadditions.csv, objectadditions.csv
    └── negativewords.csv
```

### 3. Probability System (`random_functions.py`)

The probability system controls when optional elements are added to prompts using a sophisticated rarity-based distribution system. Each distribution function determines whether an element should be included based on the insanity level.

**How Distribution Functions Work:**

Each distribution function uses a simple but effective algorithm:
```python
def rare_dist(insanitylevel):
    roll = (random.randint(1, 30) < insanitylevel or insanitylevel >= 10)
    if(roll):
        print("adding something rare to the prompt")
    return roll
```

**The Core Logic:**
1. Generate a random number between 1 and the rarity threshold (e.g., 30 for rare)
2. Compare it to the insanity level
3. Return True if random number < insanitylevel OR insanitylevel >= 10
4. This creates a probability of `insanitylevel / threshold`

**Distribution Functions and Their Thresholds:**
```python
common_dist(insanitylevel)      # 1/5 chance base   (20% at level 1)
normal_dist(insanitylevel)      # 1/10 chance base  (10% at level 1)
uncommon_dist(insanitylevel)    # 1/18 chance base  (5.5% at level 1)
rare_dist(insanitylevel)        # 1/30 chance base  (3.3% at level 1)
legendary_dist(insanitylevel)   # 1/50 chance base  (2% at level 1)
unique_dist(insanitylevel)      # 1/75 chance base  (1.3% at level 1)
extraordinary_dist(insanitylevel) # 1/200 chance base (0.5% at level 1)
novel_dist(insanitylevel)       # 1/500 chance base (0.2% at level 1)
```

**Probability Calculation Examples:**

At insanity level 5:
- `common_dist(5)`: 5/5 = 100% chance (always triggers)
- `normal_dist(5)`: 5/10 = 50% chance
- `uncommon_dist(5)`: 5/18 = 27.8% chance
- `rare_dist(5)`: 5/30 = 16.7% chance
- `legendary_dist(5)`: 5/50 = 10% chance
- `unique_dist(5)`: 5/75 = 6.7% chance
- `extraordinary_dist(5)`: 5/200 = 2.5% chance
- `novel_dist(5)`: 5/500 = 1% chance

At insanity level 10:
- ALL distributions from common to rare: 100% (special override)
- `legendary_dist(10)`: 10/50 = 20% chance
- `unique_dist(10)`: 10/75 = 13.3% chance
- `extraordinary_dist(10)`: 10/200 = 5% chance
- `novel_dist(10)`: 10/500 = 2% chance

**The `chance_roll()` Function:**

A unified function that handles all probability checks with string-based rarity names:

```python
def chance_roll(insanitylevel, chance):
    chance_mapping = {
        'never': {'set_number': 0, 'message': ""},
        'novel': {'set_number': 500, 'message': "Uh, something novel..."},
        'extraordinary': {'set_number': 200, 'message': "Extraordinary!..."},
        'unique': {'set_number': 75, 'message': "Critical hit!..."},
        'legendary': {'set_number': 50, 'message': "Nice! adding legendary..."},
        'rare': {'set_number': 30, 'message': "adding something rare..."},
        'uncommon': {'set_number': 18, 'message': ""},
        'normal': {'set_number': 10, 'message': ""},
        'common': {'set_number': 5, 'message': ""},
        'always': {'set_number': 1, 'message': ""},
    }
```

**Usage in Configuration:**

The config CSV files use these string values to control element probabilities:
```csv
element_name,chance
add_artist,common
add_art_movement,uncommon
add_lighting,normal
add_camera_angle,rare
add_special_effect,legendary
```

**Special Insanity Level 10 Behavior:**

When insanity level reaches 10, the system enters "maximum chaos" mode:
- All distributions with threshold ≤ 35 (common through rare) become 100%
- This ensures maximum variety and complexity
- Only legendary and above remain probabilistic
- Overrides most generation restrictions

**Insanity Level Impact Summary:**
- **Level 1-3**: Conservative, predictable results
  - Only common elements trigger reliably
  - Rare+ elements almost never appear
  - Suitable for consistent, simple prompts
  
- **Level 4-6**: Balanced randomness (recommended default range)
  - Common and normal elements trigger frequently
  - Uncommon and rare elements appear occasionally
  - Good mix of variety and coherence
  - Most users run between 5-7 for best results
  
- **Level 7-9**: High creativity and complexity
  - Most elements trigger frequently
  - Legendary and unique elements become viable
  - Prompts become more experimental
  
- **Level 10**: Maximum chaos (use at your own risk)
  - Common through rare: 100% trigger rate
  - Legendary+: Still probabilistic but higher chance
  - Overrides most restrictions
  - Maximum variety and unpredictability

**When Each Distribution Is Used:**

Throughout `build_dynamic_prompt.py`, different elements use appropriate distributions:
- **Artists**: `uncommon_dist()` - Not every prompt needs an artist
- **Art Movements**: `rare_dist()` - Special artistic styles
- **Lighting**: `normal_dist()` - Fairly common addition
- **Camera Settings**: `uncommon_dist()` - Technical details
- **Special Effects**: `legendary_dist()` - Unusual additions
- **Experimental Elements**: `extraordinary_dist()` or `novel_dist()` - Very rare

This system allows fine-grained control over prompt complexity while maintaining coherence at lower insanity levels and enabling maximum creativity at higher levels.

### 4. Preset System (`one_button_presets.py`)

The preset system provides a flexible way to save and load complete generation configurations, allowing users to create reusable prompt generation profiles. It uses a JSON-based architecture with inheritance and merging capabilities.

**How the Preset System Works:**

**1. File Structure:**
```
presets/
  └── obp_presets.default      # Default presets (shipped with OBP)
userfiles/
  └── obp_presets.json         # User presets (created on first run)
```

**2. Preset Loading and Merging Process:**

```python
def load_obp_presets(self):
    # Step 1: Load default presets
    default_data = self._load_data(self.DEFAULT_OBP_FILE)
    
    # Step 2: Load user presets (or create from default if missing)
    data = self._load_data(self.OBP_FILE)
    
    # Step 3: Merge - add any missing defaults to user file
    for name, settings in default_data.items():
        if name not in data:
            data[name] = settings
    
    # Step 4: Save merged result back to user file
    self._save_data(self.OBP_FILE, data)
    
    return data
```

**Merging Logic:**
- Default presets are loaded first as the base
- User presets are loaded and take precedence
- Any default presets NOT in user file are added
- This ensures new default presets appear after updates
- User modifications are never overwritten
- Result is saved back to user file for persistence

**3. Preset Structure and Parameters:**

A preset is a JSON object containing generation parameters:

```json
{
  "Preset Name": {
    "insanitylevel": 5,
    "subject": "human - generic",
    "artist": "fantasy",
    "imagetype": "digital art",
    "givensubject": "",
    "smartsubject": true,
    "giventypeofimage": "",
    "antistring": "",
    "prefixprompt": "epic fantasy",
    "suffixprompt": "detailed, masterpiece",
    "promptcompounderlevel": "1",
    "seperator": "comma",
    "givenoutfit": "",
    "base_model": "SD1.5",
    "OBP_preset": "",
    "prompt_g_and_l": false
  }
}
```

**4. Parameter Mapping to Generation Settings:**

When a preset is loaded, its parameters override the default generation settings:

| Preset Parameter | Effect on Generation |
|-----------------|---------------------|
| `insanitylevel` | Controls probability distributions (1-10) |
| `subject` | Sets subject category (e.g., "human - generic", "animal", "object") |
| `artist` | Filters artist selection (e.g., "fantasy", "sci-fi", "all") |
| `imagetype` | Sets image type (e.g., "digital art", "photograph", "all") |
| `givensubject` | Custom subject override (bypasses random selection) |
| `smartsubject` | Enables/disables smart subject detection |
| `giventypeofimage` | Custom image type override |
| `antistring` | Comma-separated list of terms to exclude |
| `prefixprompt` | Text added at the beginning of prompt |
| `suffixprompt` | Text added at the end of prompt |
| `promptcompounderlevel` | Number of prompt variations to generate |
| `seperator` | Delimiter between prompt elements ("comma" or "space") |
| `givenoutfit` | Custom outfit override for humanoid subjects |
| `base_model` | Target model (SD1.5, SDXL, Stable Cascade, Anime) |
| `OBP_preset` | Nested preset reference (for preset chaining) |
| `prompt_g_and_l` | Generate separate prompt_g and prompt_l for SDXL |

**5. Special Preset Types:**

**Random Preset Selection:**
```python
RANDOM_PRESET_OBP = "All (random)..."
```
When this special preset is selected, the system randomly chooses from all available presets, enabling variety across generations.

**Custom Preset:**
```python
CUSTOM_OBP = "Custom..."
```
This special value indicates user wants to manually specify all parameters rather than loading a preset.

**6. Creating and Managing Custom Presets:**

**Adding a New Preset:**
1. Load existing presets: `presets = OneButtonPresets()`
2. Add new preset to dictionary: `presets.opb_presets["My Preset"] = {...}`
3. Save: `presets.save_obp_preset(presets.opb_presets)`

**Modifying Existing Preset:**
1. Load presets: `presets = OneButtonPresets()`
2. Get preset: `preset = presets.get_obp_preset("Preset Name")`
3. Modify parameters: `preset["insanitylevel"] = 7`
4. Save: `presets.save_obp_preset(presets.opb_presets)`

**Deleting a Preset:**
1. Load presets: `presets = OneButtonPresets()`
2. Remove from dictionary: `del presets.opb_presets["Preset Name"]`
3. Save: `presets.save_obp_preset(presets.opb_presets)`

**7. Preset Inheritance and Composition:**

**Nested Presets:**
Presets can reference other presets via the `OBP_preset` parameter:
```json
{
  "Base Fantasy": {
    "artist": "fantasy",
    "imagetype": "digital art",
    "insanitylevel": 5
  },
  "Dark Fantasy Portrait": {
    "OBP_preset": "Base Fantasy",
    "subject": "human - generic",
    "prefixprompt": "dark, moody",
    "insanitylevel": 6
  }
}
```

When "Dark Fantasy Portrait" is loaded:
1. System first loads "Base Fantasy" settings
2. Then applies "Dark Fantasy Portrait" overrides
3. Result combines both presets with child taking precedence

**8. Key Default Presets:**

**Standard**: Default balanced generation
- `insanitylevel`: 5
- All subjects and artists enabled
- No prefix/suffix
- Balanced randomness

**Consistent Results**: Low-variance, reliable output
- `insanitylevel`: 3
- Limited subject types
- Specific artist categories
- Predictable, repeatable results

**Greg Mode**: Popular artist-focused generation
- Uses `gregmode.csv` artist list
- Higher quality descriptors
- Photorealistic emphasis

**Waifu's/Husbando's**: Anime character generation
- `base_model`: "Anime"
- Anime-specific subjects
- Character-focused generation

**D&D Style Portraits**: Fantasy character focus
- `subject`: "human - generic"
- `artist`: "fantasy"
- Character portrait emphasis

**Cyberpunk Characters**: Sci-fi themed generation
- `artist`: "sci-fi"
- Cyberpunk-specific descriptors
- Futuristic subject matter

**9. Preset Usage in Different Platforms:**

**ComfyUI:**
- `OneButtonPreset` node loads preset by name
- Dropdown populated with all available presets
- Parameters automatically applied to generation

**Automatic1111 WebUI:**
- Preset dropdown in script UI
- Selected preset overrides script parameters
- Can be combined with manual overrides

**Standalone/API:**
- Presets loaded programmatically
- Can be specified via command-line arguments
- Useful for batch processing with different styles

**10. Advanced Preset Techniques:**

**Preset Collections:**
Create themed preset groups for different projects:
```json
{
  "Project_A_Character": {...},
  "Project_A_Environment": {...},
  "Project_A_Props": {...}
}
```

**Conditional Presets:**
Use different presets based on generation context:
- Portrait presets for character work
- Landscape presets for environments
- Object presets for props and items

**Preset Chains:**
Build complex generation profiles through nested presets:
```
Base Style → Genre Modifier → Subject Specialization → Final Tweaks
```

This preset system provides a powerful way to create reusable, shareable generation profiles while maintaining flexibility for customization and experimentation.

### 5. API Integration Layer

**Text-to-Image (`call_txt2img.py`):**
- **Quality Gate System**: Automatic image scoring and selection
- **Multi-Run Support**: Generate multiple candidates
- **Upscaling Integration**: Built-in hi-res fix support
- **Model Management**: Automatic model switching
- **Size Management**: Intelligent aspect ratio handling

**Image-to-Image (`call_img2img.py`):**
- **Upscaling Methods**: SD Upscale, Ultimate SD Upscale, ControlNet
- **Batch Processing**: Sequential improvement workflows
- **Automatic Settings**: Smart parameter adjustment based on content
- **ControlNet Integration**: Tile resampling for upscaling

## Platform-Specific Implementations

### ComfyUI Integration (`OneButtonPromptNodes.py`)

**Custom Nodes:**
- **OneButtonPrompt**: Main generation node
- **OneButtonPreset**: Preset-based generation
- **CreatePromptVariant**: Prompt variation generation
- **OneButtonArtify**: Artist style application
- **OneButtonFlufferize**: Prompt enhancement
- **AutoNegativePrompt**: Automatic negative prompt generation
- **SavePromptToFile**: Prompt persistence
- **OneButtonSuperPrompt**: AI-enhanced prompting

**Node Architecture:**
```python
class OneButtonPrompt:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {"insanitylevel": ("INT", {...})},
            "optional": {
                "artist": (artists, {"default": "all"}),
                "imagetype": (imagetypes, {"default": "all"}),
                # ... additional parameters
            }
        }
    
    def Comfy_OBP(self, insanitylevel, ...):
        # Generation logic
        return (prompt, prompt_g, prompt_l)
```

### Automatic1111 WebUI Integration

**Script Integration:**
- Located in `scripts/` directory
- Integrates with txt2img and img2img tabs
- Supports all WebUI features (hi-res fix, batch processing, etc.)
- API-based communication for automation workflows

## Configuration System

### 1. Config Files (`csvfiles/config/`)

**Main Configuration (`default_config.csv`):**
- **Subject Control**: Enable/disable subject categories
- **Probability Tuning**: Adjust generation chances for all elements
- **Feature Toggles**: Control specific generation features

**Anime Configuration (`default_config_anime.csv`):**
- Specialized settings for anime/manga generation
- Modified probability distributions
- Anime-specific subject preferences

### 2. User Customization (`userfiles/`)

**Supported Customizations:**
- **Personal Artists**: `personal_artists_*.csv`
- **Custom Subjects**: `custom_subjects.csv`
- **Custom Outfits**: `custom_outfits.csv`
- **Style Additions**: `styles_ti_lora.csv` (LoRA/Textual Inversion)
- **Negative Prompts**: `negativewords_addon.csv`
- **Anti-Lists**: `antilist.csv` (content filtering)

**File Naming Conventions:**
- `*_addon.csv`: Adds to existing lists
- `*_replace.csv`: Completely replaces default lists
- `*_sample.csv`: Example files for user reference

## Advanced Features

### 1. Smart Subject Logic

**Automatic Adjustments:**
When a custom subject is provided, the system intelligently disables conflicting generation:
- Detects clothing keywords → disables outfit generation
- Detects body type descriptors → disables body type generation
- Detects hair descriptions → disables hair generation
- Detects location keywords → disables background generation

### 2. Wildcard System

**Dynamic Replacement:**
The system uses a sophisticated wildcard replacement system:
```
-artist- → Random artist from selected category
-subject- → Generated subject based on settings
-outfit- → Clothing/costume selection
-location- → Background/setting
-descriptor- → Adjective/quality descriptor
```

**Advanced Wildcards:**
- **OR() Statements**: `OR(option1;option2;option3)`
- **Conditional Logic**: `OR(;rare_option;rare)`
- **Nested Wildcards**: `-artist- in the style of -artmovement-`

### 3. Multi-Model Adaptation

**Model-Specific Optimizations:**
- **SD1.5**: Concise, keyword-focused prompts
- **SDXL**: Natural language, detailed descriptions
- **Stable Cascade**: Weight-free, simplified syntax
- **Anime Models**: Specialized tags and conventions

### 4. Quality Control Systems

**Quality Gate Integration:**
- Automatic image scoring using aesthetic models
- Multi-candidate generation with best selection
- Configurable quality thresholds
- Retry logic for improved results

## Extension Points

### 1. Adding New Subjects

**CSV Structure:**
```csv
subject_name,gender,category
"Cybernetic Warrior",both,humanoid
"Quantum Computer",genderless,object
```

**Integration Steps:**
1. Add CSV file to `csvfiles/` or `userfiles/`
2. Update configuration if needed
3. Add to appropriate subject category lists
4. Test generation and adjust probabilities

### 2. Creating Custom Presets

**Preset Structure:**
```json
{
  "Custom Preset Name": {
    "insanitylevel": 5,
    "subject": "human - generic",
    "artist": "fantasy",
    "imagetype": "digital art",
    "prefixprompt": "epic fantasy",
    "suffixprompt": "detailed, masterpiece"
  }
}
```

### 3. Adding New Generation Modes

**Implementation Pattern:**
1. Add mode to `imagetypemodelist` in `build_dynamic_prompt.py`
2. Implement mode-specific logic in generation loop
3. Add mode detection and parameter adjustment
4. Test across different insanity levels and subjects

### 4. Platform Integration

**New Platform Checklist:**
1. Implement prompt generation interface
2. Add platform-specific parameter handling
3. Integrate with platform's API/plugin system
4. Add platform-specific optimizations
5. Create documentation and examples

## Performance Considerations

### 1. CSV Loading Optimization

**Caching Strategy:**
- CSV files loaded once at startup
- Lists cached in memory for fast access
- Lazy loading for optional components
- Deduplication to reduce memory usage

### 2. Generation Performance

**Optimization Techniques:**
- Pre-computed probability tables
- Efficient random selection algorithms
- Minimal string operations during generation
- Batch processing for multiple prompts

### 3. Memory Management

**Resource Usage:**
- ~50MB for full CSV dataset
- Configurable list sizes based on insanity level
- Garbage collection for large generation batches
- Optional list pruning for memory-constrained environments

## Testing and Quality Assurance

### 1. Automated Testing

**Test Categories:**
- **Unit Tests**: Individual function validation
- **Integration Tests**: Cross-component functionality
- **Regression Tests**: Ensure consistent output
- **Performance Tests**: Generation speed benchmarks

### 2. Quality Metrics

**Evaluation Criteria:**
- **Prompt Diversity**: Uniqueness across generations
- **Coherence**: Logical prompt structure
- **Platform Compatibility**: Cross-platform consistency
- **User Satisfaction**: Community feedback integration

## Troubleshooting Guide

### Common Issues

**1. Empty/Broken Prompts:**
- Check CSV file integrity
- Verify configuration settings
- Ensure proper wildcard replacement
- Review insanity level settings

**2. Performance Issues:**
- Monitor CSV loading times
- Check memory usage patterns
- Optimize probability calculations
- Consider list size reduction

**3. Platform Integration Problems:**
- Verify API connectivity
- Check parameter compatibility
- Review error logs
- Test with minimal configurations

### Debugging Tools

**Built-in Diagnostics:**
- Verbose logging options
- Generation step tracking
- CSV validation utilities
- Performance profiling hooks

## Future Development

### Planned Enhancements

**1. AI Integration:**
- GPT-based prompt enhancement
- Automatic style detection
- Semantic prompt analysis
- Quality prediction models

**2. User Experience:**
- Web-based configuration interface
- Real-time preview generation
- Community preset sharing
- Advanced filtering options

**3. Technical Improvements:**
- Database backend option
- Distributed generation
- Cloud API integration
- Mobile platform support

### Contributing Guidelines

**Development Workflow:**
1. Fork repository and create feature branch
2. Implement changes with comprehensive tests
3. Update documentation and examples
4. Submit pull request with detailed description
5. Participate in code review process

**Code Standards:**
- Follow PEP 8 Python style guidelines
- Include docstrings for all public functions
- Maintain backward compatibility
- Add appropriate error handling

This architecture enables OneButtonPrompt to be a flexible, extensible, and powerful prompt generation system that can adapt to various use cases while maintaining high performance and reliability.