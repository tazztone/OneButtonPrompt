# OneButtonPrompt Analysis Guide

## 1. Quick Start

**Goal**: Identify and reduce repetition in generated prompts.

**Step 1: Run Analysis (3 minutes)**
```bash
python3 run_full_analysis.py
```
This will generate 1000 test prompts, analyze them, and output:
*   `csv_architecture_analysis.json`
*   `obp_analysis_results.json`
*   Console report with recommendations.

**Step 2: Create Improvements (5 minutes)**
```bash
python3 create_addon_template.py
```
This generates template files in `userfiles/`:
*   `artists_addon_template.csv`
*   `descriptors_addon_template.csv`
*   `concepts_addon_template.csv`

**Step 3: Activate & Verify**
1.  Edit the templates in `userfiles/`.
2.  Rename them (remove `_template` suffix) to activate.
3.  Re-run analysis to verify improvements.

---

## 2. Design Philosophy & Methodology

This system was built to address repetition issues using a **data-driven approach** rather than complex history tracking.

### Why This Approach Works
1.  **Data Beats Guessing**: Analysis reveals the *real* distribution of artists and subjects, often exposing biases (e.g., "Red" matching inside "Dark Red") that aren't obvious from just looking at code.
2.  **Strategic Expansion > Random Addition**: Instead of adding 1000 random items, we use analysis to identify the 10 most overused items and add 50 specific alternatives to them. This provides 10x the variety improvement with 1/10th the effort.
3.  **Architectural Awareness**: The tools understand OBP's probability distributions, ensuring that expanding a "Rare" category has a precise impact on generation.

### Design Decisions: Why Not History Tracking?
We explicitly chose **not** to implement a history tracking system (preventing "last 5 prompts" from repeating) for several reasons:
*   **Complexity**: State management across sessions is fragile and hard to debug.
*   **Root Cause**: Repetition is usually a data distribution problem (too few items in a "Common" category), not a random number generator problem.
*   **Performance**: Simple list expansion adds zero runtime overhead, whereas history checking adds latency.

---

## 3. Analysis Tools Reference

### `analyze_csv_architecture.py`
**Purpose**: Audits the CSV data layer.
*   Identifying files with <100 entries (candidates for expansion).
*   Detecting huge files (>1000 entries).
*   Checking for gender support and multi-column structures.
*   **Run time**: ~5 seconds.

### `analyze_obp_generations.py`
**Purpose**: Analyzes actual generation patterns.
*   Generates 1000 prompts.
*   Tracks frequency of Artists, Subject Types, Image Types, and Styles.
*   Identifies overused elements (>2% frequency).
*   **Run time**: ~2-3 minutes.

### `run_full_analysis.py`
**Purpose**: Orchestrator.
*   Runs both architecture and generation analysis.
*   Merges findings into actionable High/Medium/Low priority recommendations.

---

## 4. Interpreting Reports & Fixing Issues

### High Priority: Overused Artists
*   **Issue**: An artist appearing in >2% of generations.
*   **Fix**: Create `userfiles/artists_addon.csv` with 10-20 alternative artists. This dilutes the pool and reduces the frequency of the top artists.

### High Priority: Subject Types Imbalance
*   **Issue**: e.g., "Humanoids" appearing 45% of the time, while "Concepts" appear only 5%.
*   **Fix**: Expand the `concepts.csv` (via `concepts_addon.csv`) to increase its pool size and selection probability. The analysis revealed that small subject lists are selected less frequently in specific modes.

### Medium Priority: Small Descriptor Files
*   **Issue**: Core files with <200 entries lead to repetitive descriptions (e.g., "detailed" appearing in 15% of prompts).
*   **Fix**: Double the size with distinct synonyms in an addon file (e.g., `userfiles/descriptors_addon.csv`).

---

## 5. Customization

### Analysis Parameters
Edit `run_full_analysis.py`:
```python
NUM_ITERATIONS = 1000  # Default. Increase to 5000 for high precision.
INSANITY_LEVEL = 5     # Test how higher insanity levels affect variety.
```

### Advanced Testing (`analyze_obp_generations.py`)
You can test specific categories or models:
```python
analyzer.run_analysis(
    num_iterations=500,
    artists="sci-fi",      # Only test sci-fi artists
    base_model="SDXL"      # Test SDXL prompt structure
)
```

---

## 6. Troubleshooting

*   **"Error importing OBP modules"**: Run scripts from the root `OneButtonPrompt` directory.
*   **"Analysis takes too long"**: Reduce `NUM_ITERATIONS` to 100 in the script.
*   **"No improvements after adding files"**:
    *   Ensure files are in `userfiles/`.
    *   Ensure files match the naming convention: `filename_addon.csv`.
    *   **Crucial**: Ensure no empty lines in CSV files (this can cause crashes or silent failures).
    *   Restart ComfyUI/WebUI if running as a node (though CLI tools don't need restart).
