# OneButtonPrompt Architecture Guide

## Overview
AI prompt generation system for Stable Diffusion with automated, controlled randomness. Supports Automatic1111 WebUI, ComfyUI, RuinedFooocus, and web interface (airjen.pythonanywhere.com).

## Core Architecture

### Component Structure
```
OneButtonPrompt/
├── Core: build_dynamic_prompt.py, csv_reader.py, random_functions.py, one_button_presets.py
├── Platforms: OneButtonPromptNodes.py (ComfyUI), scripts/ (A1111), main.py
├── API: call_txt2img.py, call_img2img.py, call_extras.py
├── Data: csvfiles/ (core), userfiles/ (custom), presets/
└── Enhancement: superprompter/, example_workflows/
```

## 1. Prompt Generation Engine (`build_dynamic_prompt.py`)

### Pipeline Stages
1. **Init**: Load config by model (SD1.5/SDXL/Cascade/Anime), set verbosity, apply presets
2. **Subject**: Choose category (object/animal/humanoid/landscape/concept), apply filters
3. **Build**: `[Artist] → [Type] → [Shot] → @@@ → [Descriptors] → [Subject] → [Details] → [Location] → [Technical] → [Quality]`
4. **Wildcards**: Replace `-artist-`, `-subject-`, `-outfit-`, `-location-`, `-descriptor-`
5. **Advanced**: Weighting `(x:1.2)`, Switching `[x:y:10]`, Hybrid `[x|y]`, Stopping `[x::15]`, Adding `[x:10]`
6. **Finalize**: Clean, validate, apply prefix/suffix, return prompts

### Generation Modes
- **Standard**: Balanced random, respects insanity level
- **Template**: Uses `csvfiles/templates/styles.csv`, format `[prefix]-subject-[suffix]`
- **Art Blaster**: 1-insanitylevel iterations of artist/movement/vomit/imagetype/colorscheme
- **Quality Vomit**: Multiple quality terms, stacked modifiers
- **Color Cannon**: Mood/color/lighting/movement emphasis
- **Photo Fantasy**: Forces "photograph", adds camera/lens/lighting
- **Massive Madness**: 1-insanitylevel iterations, ANY elements, no restrictions
- **Subject Only**: Minimal decorative elements, subject focus
- **Fixed Styles**: Curated `styles.csv` templates, minimal randomization
- **Tokinator**: Random tokens from `tokens.csv` (5000+ words), no logic
- **Dynamic Templates**: Adaptive prefix/suffix from `dynamic_templates_*.csv`

Mode trigger: `if random.randint(1, imagemodechance) == 1: mode = random.choice(imagetypemodelist)`

## 2. Data Management (`csv_reader.py`)

### Loading Priority
1. Check `userfiles/{file}_replace.csv` → use exclusively
2. Load `csvfiles/{file}.csv` → base
3. Check `userfiles/{file}_addon.csv` → append
4. Apply insanity filtering: <4=light, <7=medium, ≥7=full
5. Filter gender, remove antilist, deduplicate

### Key Features
- **Gender Filter**: male/female/genderless/both logic
- **Artist Categories**: `artists_and_category.csv` with multi-category classification
- **Customization**: addon (append), replace (override), antilist (exclude)
- **Performance**: Load once, cache in memory, ~50MB dataset

### Data Organization
- **Artists**: 3483 across 40+ categories
- **Subjects**: animals, objects, humanoids, locations, concepts
- **Styles**: movements, types, quality descriptors
- **Technical**: cameras, lenses, lighting, composition
- **Descriptors**: adjectives, moods, colors, materials

## 3. Probability System (`random_functions.py`)

### Distribution Functions
```python
# Formula: random.randint(1, threshold) < insanitylevel OR insanitylevel >= 10
common_dist(level)        # threshold=5   (20% at L1, 100% at L5+)
normal_dist(level)        # threshold=10  (10% at L1, 100% at L10)
uncommon_dist(level)      # threshold=18  (5.5% at L1)
rare_dist(level)          # threshold=30  (3.3% at L1)
legendary_dist(level)     # threshold=50  (2% at L1)
unique_dist(level)        # threshold=75  (1.3% at L1)
extraordinary_dist(level) # threshold=200 (0.5% at L1)
novel_dist(level)         # threshold=500 (0.2% at L1)
```

### Insanity Levels
- **1-3**: Conservative (common only)
- **4-6**: Balanced (recommended 5-7)
- **7-9**: High creativity
- **10**: Max chaos (common-rare=100%, use at risk)

### chance_roll() Mapping
```python
chance_mapping = {
    'never': 0, 'novel': 500, 'extraordinary': 200, 'unique': 75,
    'legendary': 50, 'rare': 30, 'uncommon': 18, 'normal': 10,
    'common': 5, 'always': 1
}
```

## 4. Preset System (`one_button_presets.py`)

### Files
- `presets/obp_presets.default` (shipped)
- `userfiles/obp_presets.json` (user, auto-created)

### Merging Logic
1. Load defaults
2. Load user (or create from default)
3. Add missing defaults to user
4. Save merged to user file

### Preset Parameters
```json
{
  "insanitylevel": 5, "subject": "human - generic", "artist": "fantasy",
  "imagetype": "digital art", "givensubject": "", "smartsubject": true,
  "giventypeofimage": "", "antistring": "", "prefixprompt": "",
  "suffixprompt": "", "promptcompounderlevel": "1", "seperator": "comma",
  "givenoutfit": "", "base_model": "SD1.5", "OBP_preset": "",
  "prompt_g_and_l": false
}
```

### Key Presets
- **Standard**: insanity=5, all enabled, balanced
- **Consistent Results**: insanity=3, limited types, predictable
- **Greg Mode**: gregmode.csv artists, photorealistic
- **Waifu's/Husbando's**: base_model=Anime, character focus
- **D&D Portraits**: subject=humanoid, artist=fantasy
- **Cyberpunk**: artist=sci-fi, futuristic

### Inheritance
Presets can chain via `OBP_preset` parameter (child overrides parent).

## 5. API Integration

### call_txt2img.py
Quality gate, multi-run, upscaling, model switching, aspect ratio handling

### call_img2img.py
SD Upscale, Ultimate SD Upscale, ControlNet tile resampling, batch processing

## Platform Implementations

### ComfyUI Nodes
OneButtonPrompt, OneButtonPreset, CreatePromptVariant, OneButtonArtify, OneButtonFlufferize, AutoNegativePrompt, SavePromptToFile, OneButtonSuperPrompt

### A1111 WebUI
Scripts in `scripts/`, integrates txt2img/img2img tabs, API-based automation

## Configuration

### Config Files
- `csvfiles/config/default_config.csv`: subject control, probability tuning, feature toggles
- `csvfiles/config/default_config_anime.csv`: anime-specific settings

### User Customization
- `personal_artists_*.csv`, `custom_subjects.csv`, `custom_outfits.csv`
- `styles_ti_lora.csv` (LoRA/TI), `negativewords_addon.csv`, `antilist.csv`
- Naming: `*_addon.csv` (append), `*_replace.csv` (override), `*_sample.csv` (examples)

## Advanced Features

### Smart Subject Logic
Auto-detects keywords in custom subject to disable conflicting generation (clothing→no outfit, body type→no body gen, hair→no hair gen, location→no background)

### Wildcard System
- Basic: `-artist-`, `-subject-`, `-outfit-`, `-location-`, `-descriptor-`
- Advanced: `OR(opt1;opt2;opt3)`, `OR(;rare;rare)`, nested wildcards

### Model Adaptation
- SD1.5: concise keywords
- SDXL: natural language
- Stable Cascade: no weights
- Anime: specialized tags

### Quality Control
Aesthetic scoring, multi-candidate selection, quality thresholds, retry logic

## Extension Points

### Add Subjects
CSV: `subject_name,gender,category` → add to `csvfiles/` or `userfiles/` → update config → test

### Add Presets
JSON structure → add to `userfiles/obp_presets.json` → save

### Add Generation Modes
Add to `imagetypemodelist` → implement logic → test across insanity levels

### Platform Integration
1. Implement prompt interface
2. Handle platform parameters
3. Integrate API/plugin
4. Optimize
5. Document

## Performance

### Optimization
- CSV: load once, cache, lazy load, deduplicate
- Generation: pre-computed tables, efficient selection, minimal strings, batch processing
- Memory: ~50MB dataset, configurable sizes, garbage collection, optional pruning

## Testing

### Categories
Unit (functions), Integration (components), Regression (consistency), Performance (speed)

### Metrics
Diversity, coherence, platform compatibility, user satisfaction

## Troubleshooting

### Common Issues
1. **Empty prompts**: Check CSV integrity, config, wildcards, insanity level
2. **Performance**: Monitor CSV load, memory, probability calc, list sizes
3. **Platform**: Verify API, parameters, logs, minimal config

### Diagnostics
Verbose logging, step tracking, CSV validation, profiling

## Future Development

### Planned
- AI: GPT enhancement, style detection, semantic analysis, quality prediction
- UX: web config, real-time preview, preset sharing, advanced filters
- Technical: database backend, distributed gen, cloud API, mobile support

### Contributing
1. Fork → feature branch
2. Implement with tests
3. Update docs
4. PR with description
5. Code review

### Standards
PEP 8, docstrings, backward compatibility, error handling
