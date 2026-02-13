# How OneButtonPrompt Works - Technical Overview

## Core Concept

OneButtonPrompt is an intelligent prompt generation system that creates complete, coherent prompts for Stable Diffusion through controlled randomness. Instead of requiring users to manually craft prompts, it automatically combines elements from a vast database of subjects, artists, styles, and descriptors using probability-based selection.

## Architecture

### 1. CSV-Based Data Layer

The system is built on a flexible, text-based data architecture using CSV files:

**Core Data Files (130+ CSV files):**
- **Artists** (`artists.csv`): 3,591 artists across 40+ categories (fantasy, sci-fi, portrait, etc.)
- **Subjects**: Objects, animals, humanoids, landscapes, and concepts
- **Styles**: Art movements, image types, quality descriptors
- **Technical**: Camera settings, lighting, composition terms
- **Descriptors**: Adjectives, moods, colors, materials

**Hierarchical Loading System:**
```
1. Load base CSV file (csvfiles/artists.csv)
2. Check for user addon (userfiles/artists_addon.csv) → Append if exists
3. Check for user replace (userfiles/artists_replace.csv) → Use exclusively if exists
4. Apply filters (gender, insanity level, antilist)
5. Return deduplicated list
```

This allows easy customization without modifying core files.

### 2. Probability Distribution System

Elements are added to prompts based on probability distributions controlled by the "insanity level" (1-10):

**Distribution Functions:**
- `common_dist()` - 1/5 chance base (20% at level 1)
- `normal_dist()` - 1/10 chance base (10% at level 1)
- `uncommon_dist()` - 1/18 chance base (5.5% at level 1)
- `rare_dist()` - 1/30 chance base (3.3% at level 1)
- `legendary_dist()` - 1/50 chance base (2% at level 1)
- `unique_dist()` - 1/75 chance base (1.3% at level 1)

**How It Works:**
```python
def rare_dist(insanitylevel):
    roll = (random.randint(1, 30) < insanitylevel or insanitylevel >= 10)
    return roll
```

At insanity level 5:
- Common elements: 100% chance (always added)
- Normal elements: 50% chance
- Rare elements: 16.7% chance
- Legendary elements: 10% chance

At insanity level 10:
- All distributions up to rare: 100% (maximum chaos mode)
- Legendary and above: Still probabilistic

This creates predictable variety at low levels and maximum creativity at high levels.

### 3. Prompt Generation Pipeline

The system builds prompts through a multi-stage pipeline:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. INITIALIZATION                                           │
│    - Load configuration (SD1.5/SDXL/Cascade/Anime)         │
│    - Set verbosity level                                    │
│    - Apply preset overrides                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. SUBJECT SELECTION                                        │
│    - Choose main category (object/animal/humanoid/etc.)    │
│    - Select specific subtype                                │
│    - Apply gender filtering                                 │
│    - Respect user-provided custom subjects                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. PROMPT BUILDING                                          │
│    [Artist] → [Image Type] → [Shot Size] → @@@             │
│    → [Descriptors] → [Subject] → [Details]                 │
│    → [Location] → [Technical] → [Quality]                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. WILDCARD REPLACEMENT                                     │
│    -artist- → Selected artist name                          │
│    -subject- → Generated subject                            │
│    -outfit- → Clothing selection                            │
│    -location- → Background/setting                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. ADVANCED PROMPTING                                       │
│    (artist:1.2) → Emphasis weighting                        │
│    [artist1:artist2:10] → Switching at step 10             │
│    [artist1|artist2] → Hybrid blending                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. CLEANUP & FINALIZATION                                   │
│    - Remove extra commas/spaces                             │
│    - Apply prefix/suffix                                    │
│    - Return final prompt                                    │
└─────────────────────────────────────────────────────────────┘
```

### 4. Generation Modes

Different modes modify the generation pipeline for specific use cases:

**Standard Mode** - Balanced random generation
- Uses all probability distributions normally
- Includes artists, subjects, and style elements
- Respects insanity level for complexity

**Template Mode** - Uses predefined prompt templates
- Loads from `templates.csv`
- Format: `[prefix]-subject-[suffix]`
- Replaces subject placeholder with generated content

**Art Blaster Mode** - Focuses on artistic styles
- Generates 1 to insanitylevel iterations
- Each iteration adds: artist, art movement, style terms
- Heavy emphasis on artistic terminology

**Photo Fantasy Mode** - Optimized for photographic styles
- Forces "photograph" as image type
- Adds photo-specific terms (lighting, camera, lens)
- Includes technical photography vocabulary

**Subject Only Mode** - Minimal generation around core subject
- Skips most decorative elements
- Focuses purely on subject description
- Often used with Artify mode for post-processing

### 5. Smart Subject Logic

When a custom subject is provided, the system intelligently disables conflicting generation:

```python
if "wearing" in givensubject.lower():
    # User specified clothing, don't generate outfit
    skip_outfit_generation = True

if any(body_type in givensubject.lower() for body_type in body_types):
    # User specified body type, don't generate another
    skip_body_type_generation = True
```

This prevents redundancy like: "muscular man" + generated "athletic" descriptor.

### 6. Model-Specific Adaptation

The system adapts output based on target model:

**SD1.5 / Anime Models:**
- Concise, keyword-focused prompts
- `less_verbose = True`
- Example: `portrait, woman, red hair, fantasy art, detailed`

**SDXL Models:**
- Adds connecting words between keywords
- `less_verbose = False`
- Example: `portrait, the woman is red haired, fantasy art style, highly detailed`

**Stable Cascade:**
- Removes prompt weights
- `remove_weights = True`
- Simplified syntax for compatibility

### 7. Preset System

Presets are JSON-based configurations that override default settings:

```json
{
  "Fantasy Portrait": {
    "insanitylevel": 5,
    "subject": "humanoid",
    "artist": "fantasy",
    "imagetype": "digital art",
    "prefixprompt": "epic fantasy",
    "suffixprompt": "detailed, masterpiece"
  }
}
```

**Preset Loading:**
1. Load default presets from `presets/obp_presets.default`
2. Load user presets from `userfiles/obp_presets.json`
3. Merge (user presets take precedence)
4. Apply selected preset parameters to generation

### 8. Customization System

Users can customize without modifying core files:

**Addon Files** (`*_addon.csv`):
```csv
# userfiles/artists_addon.csv
My Favorite Artist
Another Great Artist
```
→ Appended to base artist list

**Replace Files** (`*_replace.csv`):
```csv
# userfiles/artists_replace.csv
Only Artist 1
Only Artist 2
```
→ Completely replaces base artist list

**Antilist** (`antilist.csv`):
```csv
unwanted_term
banned_artist
```
→ Globally excludes items from all lists

## Key Technical Features

### Controlled Randomness
- Not purely random - uses weighted probability distributions
- Insanity level provides user control over complexity
- Probability functions ensure variety while maintaining coherence

### Modular Architecture
- CSV-based data layer separates content from logic
- Easy to add new subjects/artists without code changes
- Community can contribute via addon files

### Platform Agnostic
- Works with Automatic1111 WebUI (script integration)
- Works with ComfyUI (custom nodes)
- Works with RuinedFooocus (built-in)
- Standalone web version available

### Extensible Design
- Wildcard system allows template-based generation
- Advanced prompting techniques (weighting, switching, hybrids)
- Multiple generation modes for different use cases
- Preset system for reusable configurations

## Performance Characteristics

**Generation Speed:**
- Single prompt: ~0.1 seconds
- Batch of 10: ~1 second
- CSV loading: One-time cost at startup (~2 seconds)

**Memory Usage:**
- ~50MB for full CSV dataset
- Cached in memory for fast access
- Scales with number of loaded CSV files

**Scalability:**
- Handles 1,000+ entries per CSV file efficiently
- 3,591 artists with no performance impact
- Deduplication reduces memory footprint

## Why This Architecture Works

1. **Separation of Concerns**: Data (CSV) separate from logic (Python)
2. **Easy Customization**: Users modify CSV files, not code
3. **Controlled Randomness**: Probability distributions prevent chaos
4. **Hierarchical Loading**: Base → Addon → Replace allows flexibility
5. **Model Adaptation**: Automatically adjusts for different SD models
6. **Community Friendly**: CSV format enables easy contributions

## Example Generation Flow

```
User clicks "Generate" with insanity level 5
    ↓
System loads configuration (SD1.5 mode)
    ↓
Selects main subject type: "humanoid" (random choice)
    ↓
Selects subtype: "job" → "Warrior"
    ↓
Adds descriptors (50% chance each): "fierce", "battle-worn"
    ↓
Selects artist (uncommon_dist): "Frank Frazetta"
    ↓
Adds art movement (rare_dist): "Fantasy Art"
    ↓
Adds technical details: "detailed", "dramatic lighting"
    ↓
Builds final prompt:
"by Frank Frazetta, fantasy art, fierce battle-worn Warrior, 
dramatic lighting, detailed, masterpiece"
    ↓
Returns to user for image generation
```

## Technical Requirements

**Python Dependencies:**
- `random` (built-in)
- `re` (built-in)
- `csv` (built-in)
- Optional: `torch` + `transformers` (for SuperPrompt feature)

**File Structure:**
```
OneButtonPrompt/
├── build_dynamic_prompt.py    # Main generation logic
├── csv_reader.py               # CSV loading and management
├── random_functions.py         # Probability distributions
├── one_button_presets.py       # Preset management
├── csvfiles/                   # Core data (130+ CSV files)
├── userfiles/                  # User customizations
└── presets/                    # Preset configurations
```

This architecture enables OneButtonPrompt to generate diverse, coherent prompts with minimal user input while remaining highly customizable and extensible.
