# OneButtonPrompt Architecture Guide

## 1. Quick Technical Overview

OneButtonPrompt (OBP) is an AI prompt generation system designed for Stable Diffusion. It builds diverse prompts by randomly selecting keywords from a database of 130+ CSV files (containing over 3,500 artists, subjects, styles, and descriptors).

**Core Mechanism:**
*   **CSV Data Layer**: Text files define all possible prompt elements.
*   **Probability Engine**: "Insanity Level" (1-10) controls the probability of including optional elements.
*   **Pipeline**: Subject selection -> Element rolling -> Keyword concatenation -> Model formatting.

**Model Adaptation:**
*   **SD1.5/Anime**: Keywords only (e.g., `portrait, woman, red hair`).
*   **SDXL**: Natural language injection (e.g., `portrait, the woman is red haired`).
*   **Stable Cascade**: Strips weight syntax (converts `(keyword:1.2)` to `keyword`).

---

## 2. System Architecture

### Component Structure
```
OneButtonPrompt/
├── Core Engine
│   ├── build_dynamic_prompt.py    # Main generation logic
│   ├── csv_reader.py              # Data loading & caching
│   ├── random_functions.py        # Probability distribution
│   └── one_button_presets.py      # Preset management
├── Platforms
│   ├── OneButtonPromptNodes.py    # ComfyUI Nodes
│   ├── scripts/                   # A1111 WebUI integration
│   └── main.py                    # Standalone/CLI
├── API Interfaces
│   ├── call_txt2img.py            # Text-to-image logic
│   ├── call_img2img.py            # Image-to-image logic
├── Data Layer
│   ├── csvfiles/                  # Core data definitions
│   ├── userfiles/                 # User customizations (addons/overrides)
│   └── presets/                   # Preset configurations
└── Analysis & Tools
    ├── run_full_analysis.py       # Analysis orchestrator
    ├── analyze_obp_generations.py # Pattern analyzer
    └── create_addon_template.py   # Expansion generator
```

---

## 3. Core Engine Details

### Prompt Generation Pipeline (`build_dynamic_prompt.py`)
1.  **Initialization**: Loads configuration based on the target `base_model` (SD1.5, SDXL, Cascade, Anime).
2.  **Subject Selection**: Chooses a main category (Object, Animal, Humanoid, Landscape, Concept).
    *   *Smart Subject*: Auto-detects keywords in user input to disable conflicting generation (e.g., if user types "robot", disables human body generation).
3.  **Construction**: Builds the prompt structure:
    `[Artist] -> [Image Type] -> [Shot Size] -> [Subject Descriptors] -> [Main Subject] -> [Details] -> [Location] -> [Technical] -> [Quality]`
4.  **Wildcard Processing**: Replaces placeholders like `-artist-`, `-subject-`, `-outfit-`.
    *   Supports advanced logic: `OR(opt1;opt2)`, nested wildcards, and weight syntax.
5.  **Refinement**: Applies weighting, switching, and model-specific formatting.

### Generation Modes
OBP supports multiple generation modes, triggered randomly or via presets:

| Mode | Description |
| :--- | :--- |
| **Standard** | Balanced random generation. Uses all probability distributions normally. |
| **Template** | Uses predefined templates (`[prefix]-subject-[suffix]`) from `csvfiles/templates/styles.csv`. |
| **Art Blaster** | Focuses on artistic styles. Generates 1 to *insanitylevel* iterations of Artist + Movement + Colors. |
| **Quality Vomit** | Stacks multiple quality descriptors and modifiers ("masterpiece, best quality..."). |
| **Color Cannon** | Emphasizes color schemes, lighting, and mood. |
| **Photo Fantasy** | Forces "photograph" image type and adds specific camera/lens/lighting terms. |
| **Massive Madness** | Maximum chaos. Generates multiple iterations adding ANY element type without restriction. |
| **Subject Only** | Minimal generation. Skips decorative elements to focus purely on the subject. |
| **Fixed Styles** | Uses curated style definitions from `styles.csv` for consistent artistic direction. |
| **The Tokinator** | Completely random words from `tokens.csv` (5000+ words). No grammar or logic. |
| **Dynamic Templates** | Adaptive system that combines `prefix` and `suffix` templates based on artist/subject. |

### Probability System (`random_functions.py`)
The system uses rarity-based distribution functions controlled by the Insanity Level.

| Distribution | Base Chance (Lvl 1) | Behavior |
| :--- | :--- | :--- |
| `common_dist` | 20% | Always triggers at Lvl 5+ |
| `normal_dist` | 10% | ~50% at Lvl 5 |
| `uncommon_dist` | 5.5% | ~28% at Lvl 5 |
| `rare_dist` | 3.3% | ~17% at Lvl 5 |
| `legendary_dist` | 2.0% | ~10% at Lvl 5 |
| `unique_dist` | 1.3% | ~6% at Lvl 5 |
| `extraordinary_dist`| 0.5% | ~2.5% at Lvl 5 |
| `novel_dist` | 0.2% | ~1% at Lvl 5 |

**Insanity Level 10 (Chaos Mode)**:
When Insanity Level is 10, all distributions from `common` through `rare` become **100%**, ensuring maximum complexity and "kitchen sink" prompts.

### Data Management (`csv_reader.py`)

**Loading Priority**:
1.  `userfiles/{file}_replace.csv` **(Total Override)**: Replaces the core file entirely.
2.  `csvfiles/{file}.csv` **(Base Data)**: Loads the standard OBP dataset.
3.  `userfiles/{file}_addon.csv` **(Append)**: Adds new items to the list.

**Features**:
*   **Gender Logic**: CSVs can have a `gender` column (male/female/genderless/both). OBP filters these based on the generated subject (e.g., a "female" subject won't get a "beard").
*   **Insanity Filtering**: Loads smaller subsets (`_light.csv`, `_medium.csv`) for lower insanity levels to keep prompts simple and coherent.
*   **Artist Categories**: `artists_and_category.csv` allows filtering artist lists by genre (fantasy, sci-fi, anime, etc.).

---

## 4. Preset System (`one_button_presets.py`)

The preset system allows users to define reusable generation configurations.

**File Structure**:
*   `presets/obp_presets.default`: System defaults (ReadOnly).
*   `userfiles/obp_presets.json`: User presets (Read/Write).

**Preset Structure**:
```json
{
  "Dark Fantasy Portrait": {
    "insanitylevel": 6,
    "subject": "human - generic",
    "artist": "fantasy",
    "imagetype": "digital art",
    "prefixprompt": "dark, moody",
    "smartsubject": true,
    "base_model": "SDXL",
    "OBP_preset": "Standard" 
  }
}
```

*   **Inheritance**: `OBP_preset` allows a preset to inherit settings from another (parent) preset.
*   **Key Parameters**:
    *   `insanitylevel`: 1-10
    *   `artist`: Filter by category (e.g., "fantasy", "sci-fi", "all")
    *   `imagetype`: Filter style (e.g., "photograph", "digital art")
    *   `antistring`: Terms to exclude.

### Image Type Loading (Dynamic)
As of Feb 2026, the `imagetypes` list is no longer hardcoded in the node definitions.
*   **Loading Mechanism**:
    1.  Base types (`Photograph`, `Digital art`, etc.) load from `csvfiles/imagetypes.csv`.
    2.  Special modes load from `csvfiles/special_lists/imagetypemodes.csv`.
    3.  Custom additions load from `userfiles/imagetypes_addon.csv`.
*   **Expansion**: Users can add simple style suffixes by adding them to the addon CSV.

### Custom Modes Architecture (Planned)
The system is moving towards a JSON-driven custom logic engine (`custom_modes.json`). This will allow users to define:
*   **Forced Slots**: Forcing specific wildcards in the prompt construction phase.
*   **Looping Logic**: Setting explicit tag counts for multiple random keywords.
*   **Component Control**: Explicitly enabling or disabling engine features (like `Smart Subject`) per mode.

---

## 5. Platform Integration

### ComfyUI (`OneButtonPromptNodes.py`)
*   **Nodes**: `OneButtonPrompt`, `OneButtonPreset`, `CreatePromptVariant`, `OneButtonArtify`, `AutoNegativePrompt`.
*   **Integration**: Exposes core parameters as input widgets. Returns `prompt`, `prompt_g`, `prompt_l` for SDXL compatibility.

### Automatic1111 (`scripts/`)
*   **Integration**: Script-based UI in txt2img/img2img tabs. Supports batch generation and API usage.

---

## 6. Analysis Tools (New Feb 2026)

A suite of tools was added to analyze generation diversity and reduce repetition.

*   `analyze_obp_generations.py`: Generates balanced test batches to measure subject/artist frequency.
*   `analyze_csv_architecture.py`: Audits CSV structure for balance and format issues.
*   `create_addon_template.py`: Generates `userfiles/*_addon.csv` templates based on analysis data.

---

## 7. Development Environment

To run standalone scripts, tests, or analysis tools, use the established virtual environment for this ComfyUI installation. This ensures all heavyweight dependencies (torch, transformers, etc.) are correctly resolved.

**Python Path:**
`../../venv/bin/python3`

**Example Execution:**
```bash
../../venv/bin/python3 verify_overrides.py
```