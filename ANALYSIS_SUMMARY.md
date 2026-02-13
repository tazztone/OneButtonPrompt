# Analysis Tools Summary

## What We Built

Three Python scripts that work together to identify and solve the repetition problem in OneButtonPrompt:

### 1. `analyze_csv_architecture.py`
**What it does:** Examines all CSV files to understand data structure
- Counts entries in each file
- Identifies files with gender support
- Detects multi-column complex files
- Categorizes content (fantasy/sci-fi/portrait/etc.)
- Finds small files that need expansion

**Run time:** ~5 seconds

### 2. `analyze_obp_generations.py`
**What it does:** Generates 1000 prompts and analyzes patterns
- Tracks which artists appear most frequently
- Measures subject type distribution
- Identifies overused image types, colors, lighting
- Calculates prompt length statistics
- Detects imbalances in generation

**Run time:** ~2-3 minutes for 1000 generations

### 3. `run_full_analysis.py`
**What it does:** Runs both analyses and combines insights
- Executes CSV architecture analysis
- Runs generation pattern analysis
- Merges findings into actionable recommendations
- Prioritizes by impact (HIGH/MEDIUM/LOW)
- Saves detailed JSON results

**Run time:** ~3-4 minutes total

## Quick Start

```bash
# Run everything
python3 run_full_analysis.py

# Or run individually
python3 analyze_csv_architecture.py
python3 analyze_obp_generations.py
```

## What You'll Learn

### From CSV Architecture Analysis:
- Which files are too small (<100 entries)
- Which files are huge (>1000 entries)
- Files with gender filtering capability
- Content distribution across categories
- Missing user customization files

### From Generation Analysis:
- Top 20 most common artists (with percentages)
- Subject type balance (humanoid/animal/object/landscape/concept)
- Most frequent image types
- Overused descriptors and quality terms
- Average prompt length and complexity

### From Combined Recommendations:
- **Immediate actions** - Fix critical repetition issues
- **Short-term improvements** - Expand key files
- **Long-term enhancements** - Set up better customization

## Example Output

```
TOP 20 MOST COMMON ARTISTS
============================================================
  5.2% - Greg Rutkowski                           ( 52 times)
  3.8% - Artgerm                                  ( 38 times)
  2.9% - Charlie Bowater                          ( 29 times)
  2.1% - Ross Tran                                ( 21 times)
  ...

MAIN SUBJECT TYPE DISTRIBUTION
============================================================
humanoid    : 42.3% ████████████████████████ (423)
object      : 28.1% ██████████████ (281)
animal      : 15.6% ████████ (156)
landscape   :  9.2% █████ (92)
concept     :  4.8% ██ (48)

RECOMMENDATIONS
============================================================
[HIGH IMPACT] Reduce Artist Repetition
  Issue:  5 artists appear in >2% of generations
  Action: Create userfiles/artists_addon.csv with 50-100 alternatives
```

## How to Fix Repetition

Based on analysis results:

### 1. Add Artist Alternatives
```csv
# userfiles/artists_addon.csv
Karla Ortiz
Bastien Lecouffe-Deharme
Ruan Jia
Wlop
Guweiz
```

### 2. Expand Small Categories
```csv
# userfiles/concepts_addon.csv (if concepts are underused)
quantum entanglement
temporal paradox
collective consciousness
```

### 3. Add Distinctive Descriptors
```csv
# userfiles/descriptors_addon.csv
bioluminescent
art-deco-inspired
weathered-by-time
impossibly-geometric
```

### 4. Test and Verify
```bash
# Re-run analysis after changes
python3 run_full_analysis.py

# Compare results to see improvement
```

## Key Insights

### Why This Approach Works

1. **Data-driven** - Based on actual generation patterns, not guesses
2. **Architectural awareness** - Understands OBP's probability system
3. **Actionable** - Provides specific files and entries to add
4. **Measurable** - Can re-run to verify improvements

### Why NOT to Add History Tracking

- Adds complexity to core generation logic
- Requires state management across generations
- Harder to maintain and debug
- The real issue is data distribution, not randomness

### Strategic Expansion > Random Addition

Instead of adding 1000 random entries:
- Add 50 alternatives to top 10 overused items
- Double the size of underused categories
- Focus on distinctive, visually-different entries

**Result:** 10x improvement in variety with 1/10th the effort

## Files Created

1. `analyze_csv_architecture.py` - CSV structure analyzer
2. `analyze_obp_generations.py` - Generation pattern analyzer
3. `run_full_analysis.py` - Combined analysis runner
4. `ANALYSIS_README.md` - Detailed documentation
5. `ANALYSIS_SUMMARY.md` - This quick reference

## Output Files

After running analysis:
- `csv_architecture_analysis.json` - CSV statistics
- `obp_analysis_results.json` - Generation patterns
- Console output with recommendations

## Next Steps

1. ✅ Run `python3 run_full_analysis.py`
2. ✅ Review console output for insights
3. ✅ Check JSON files for detailed data
4. ✅ Create addon CSV files based on recommendations
5. ✅ Re-run analysis to verify improvements
6. ✅ Consider adding tooltips to ComfyUI nodes (separate PR)

## For the Tooltips PR

After analysis is complete, we can create a separate PR for ComfyUI tooltips:

**Changes needed in `OneButtonPromptNodes.py`:**
- Add `tooltip` parameter to each input in `INPUT_TYPES`
- Provide clear, concise explanations
- Include practical guidance (e.g., "5-7 recommended for balanced results")

**Example:**
```python
"insanitylevel": ("INT", {
    "default": 5,
    "min": 1,
    "max": 10,
    "tooltip": "Controls randomness: 1-3 conservative, 4-6 balanced, 7-9 creative, 10 chaos"
})
```

This can be a quick, high-value PR that improves UX without changing functionality.
