# OneButtonPrompt Analysis Tools

Comprehensive analysis suite to identify repetition patterns and strategically expand CSV files for better prompt variety.

## Overview

This analysis suite combines two approaches:

1. **Generation Pattern Analysis** - Runs OBP thousands of times to identify what actually gets generated
2. **CSV Architecture Analysis** - Examines the structure and content of CSV files
3. **Combined Recommendations** - Merges both analyses for actionable insights

## Quick Start

### Run Full Analysis (Recommended)

```bash
python run_full_analysis.py
```

This runs both analyses and generates combined recommendations. Takes ~2-3 minutes for 1000 generations.

**Output:**
- Console report with detailed findings
- `csv_architecture_analysis.json` - CSV file statistics
- `obp_analysis_results.json` - Generation pattern data

### Run Individual Analyses

**CSV Architecture Only:**
```bash
python analyze_csv_architecture.py
```

Analyzes CSV file structure, size distribution, and content categorization without running generations.

**Generation Patterns Only:**
```bash
python analyze_obp_generations.py
```

Generates 1000 prompts and analyzes what elements appear most frequently.

## What Gets Analyzed

### Generation Pattern Analysis

- **Artist frequency** - Which artists appear most often
- **Subject type distribution** - Balance between humanoid/animal/object/landscape/concept
- **Image type usage** - Most common image types (photograph, digital art, etc.)
- **Art movement frequency** - Which art movements appear
- **Color/lighting usage** - Common color and lighting terms
- **Technical terms** - Camera settings, quality descriptors
- **Prompt length statistics** - Average, min, max prompt lengths

### CSV Architecture Analysis

- **File size distribution** - Categorizes files by entry count
- **Gender support** - Identifies files with gender filtering
- **Multi-column files** - Complex structures like artists_and_category.csv
- **Content categorization** - Detects fantasy/sci-fi/portrait/etc. content
- **Key file identification** - Locates important files for expansion
- **User customization status** - Checks for addon/replace files

## Understanding the Results

### High Priority Issues

**Overused Artists (>2% appearance rate)**
- Indicates certain artists dominate generations
- Action: Add 5-10 alternatives for each overused artist

**Imbalanced Subject Types (>2:1 ratio)**
- Some subject types appear much more than others
- Action: Expand CSV files for underused categories

### Medium Priority Issues

**Overused Image Types (>3% appearance rate)**
- Certain image types dominate
- Action: Add 20-30 alternative image types

**Small Core Files (<200 entries)**
- Important descriptor files are too small
- Action: Double the size with distinctive alternatives

### Low Priority Issues

**Missing Gender Support**
- Files that could benefit from gender filtering
- Action: Add gender column to relevant files

**No User Customization**
- No addon files detected
- Action: Create template addon files

## Customization

### Adjust Analysis Parameters

Edit `run_full_analysis.py`:

```python
NUM_ITERATIONS = 1000  # Increase for more accurate results (2000-5000)
INSANITY_LEVEL = 5     # Test different insanity levels (1-10)
```

### Test Specific Configurations

Edit `analyze_obp_generations.py` in the `run_analysis()` call:

```python
analyzer.run_analysis(
    num_iterations=1000,
    insanitylevel=5,
    artists="fantasy",      # Test specific artist category
    imagetype="photograph", # Test specific image type
    base_model="SDXL"      # Test different model
)
```

## Acting on Recommendations

### 1. Create Addon Files

Based on analysis, create addon files in `userfiles/`:

```csv
# userfiles/artists_addon.csv
Alternative Artist 1
Alternative Artist 2
Alternative Artist 3
...
```

### 2. Expand Core Files

For small core files, add distinctive entries:

```csv
# csvfiles/descriptors.csv (or create addon)
bioluminescent
art-deco-inspired
weathered-by-time
impossibly-geometric
```

### 3. Balance Subject Types

If analysis shows imbalance, expand underused categories:

```csv
# userfiles/concepts_addon.csv (if concepts are underused)
quantum entanglement
temporal paradox
existential dread
collective consciousness
```

### 4. Test and Re-analyze

After making changes:

```bash
python run_full_analysis.py
```

Compare new results with previous analysis to measure improvement.

## Advanced Usage

### Analyze Multiple Insanity Levels

```python
# Create custom script
from analyze_obp_generations import OBPAnalyzer

for insanity in [3, 5, 7, 10]:
    print(f"\n=== Analyzing Insanity Level {insanity} ===")
    analyzer = OBPAnalyzer()
    analyzer.run_analysis(num_iterations=500, insanitylevel=insanity)
    analyzer.save_results(f"results_insanity_{insanity}.json")
```

### Compare Different Artist Categories

```python
from analyze_obp_generations import OBPAnalyzer

for category in ["fantasy", "sci-fi", "portrait", "all"]:
    print(f"\n=== Analyzing Artist Category: {category} ===")
    analyzer = OBPAnalyzer()
    analyzer.run_analysis(num_iterations=500, artists=category)
    analyzer.save_results(f"results_artists_{category}.json")
```

### Export for External Analysis

Results are saved as JSON for further processing:

```python
import json
import pandas as pd

# Load results
with open('obp_analysis_results.json', 'r') as f:
    data = json.load(f)

# Convert to DataFrame for analysis
df = pd.DataFrame([
    {'artist': k, 'count': v} 
    for k, v in data['artists'].items()
])

# Export to CSV
df.to_csv('artist_frequency.csv', index=False)
```

## Interpreting Recommendations

### "Add alternatives for overused elements"

When an element appears in >2% of generations, it creates noticeable repetition. Adding 5-10 alternatives distributes the probability more evenly.

**Example:**
- "Greg Rutkowski" appears in 5% of prompts
- Add: "Karla Ortiz", "Bastien Lecouffe-Deharme", "Ruan Jia", etc.
- New appearance rate: ~0.5% each (10x more variety)

### "Expand underused categories"

When subject types are imbalanced (e.g., 45% humanoid, 5% concept), expand the smaller categories to improve balance.

**Example:**
- concepts.csv has 50 entries
- Double to 100 entries with distinctive concepts
- Increases concept selection probability

### "Double the size of descriptor files"

Small descriptor files limit variety. Doubling size provides more combinations without changing generation logic.

**Example:**
- descriptors.csv has 150 entries
- Add 150 distinctive descriptors
- Exponentially increases possible combinations

## Troubleshooting

### "Error importing OBP modules"

Ensure scripts are in the OneButtonPrompt root directory:

```bash
ls -la
# Should see: build_dynamic_prompt.py, csv_reader.py, csvfiles/, etc.
```

### "No artists detected in prompts"

The analysis uses case-insensitive matching. If artists aren't detected:

1. Check that `csvfiles/artists.csv` exists
2. Verify prompts are being generated (check `all_prompts` in results)
3. Artists might be using different names/spellings

### "Analysis takes too long"

Reduce iterations for faster results:

```python
NUM_ITERATIONS = 100  # Quick test (30 seconds)
NUM_ITERATIONS = 500  # Balanced (2 minutes)
NUM_ITERATIONS = 1000 # Recommended (3-4 minutes)
NUM_ITERATIONS = 5000 # Comprehensive (15-20 minutes)
```

## Best Practices

1. **Run analysis before making changes** - Establish baseline
2. **Focus on high-impact items first** - Artists and subject balance
3. **Add distinctive alternatives** - Avoid near-duplicates
4. **Test changes with sample generations** - Verify visual variety
5. **Re-run analysis after changes** - Measure improvement
6. **Use addon files** - Easier to manage than modifying core files

## Contributing Analysis Improvements

If you improve these analysis tools:

1. Test with various OBP configurations
2. Document new metrics or insights
3. Add examples to this README
4. Submit PR with clear description

## Next Steps

After running analysis:

1. Review the console output for immediate insights
2. Check JSON files for detailed data
3. Prioritize high-impact recommendations
4. Create addon CSV files for expansions
5. Test with sample generations
6. Re-run analysis to verify improvements

---

**Questions or Issues?**

- Check existing OBP documentation in `user_guides/`
- Review AGENTS.md for architecture details
- Open an issue with analysis results attached
