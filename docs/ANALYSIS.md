# OneButtonPrompt Analysis Guide

## 1. Quick Start

**Goal**: Identify and reduce repetition in generated prompts.

**Step 1: Run Analysis (3 minutes)**
```bash
# From the OneButtonPrompt root directory:
../../venv/bin/python3 run_full_analysis.py --iterations 1000 --timestamp
```
This will generate 1000 test prompts, analyze them using **Ground Truth Tracking**, and output:
*   `csv_architecture_analysis.json`
*   `obp_analysis_results.json`
*   Console report with **Tag Coverage Matrix** and recommendations.

**Step 2: Create Improvements (5 minutes)**
```bash
python3 create_addon_template.py
```
This generates data-driven template files in `userfiles/`:
*   `artists_addon_template.csv` (Targeted to fill style blind spots)
*   `technical_addon_template.csv` (Lenses, Lighting, Cameras, Moods)
*   `descriptors_addon_template.csv`
*   `concepts_addon_template.csv`

**Step 3: Activate & Verify**
1.  Edit the templates in `userfiles/`.
2.  Rename them (remove `_template` suffix) to activate.
3.  Re-run analysis to verify improvements.

---

## 2. Design Philosophy & Methodology

This system uses a **data-driven approach** to solve variety problems at the source.

### Key Innovations
1.  **Ground Truth Tracking**: Unlike regex-based analysis, the engine now logs exactly which items it selected through the `_metadata` system. This results in 100% accuracy for artist, lighting, and camera tracking.
2.  **Tag Coverage Matrix**: The analyzer performs a reverse-lookup against `artists_and_category.csv` to identify "Blind Spots"—style categories (like `ukiyo-e` or `brutalist`) where you have data but it's never being selected.
3.  **High Sensitivity Expansion**: Small lists (like Lenses or Moods) have the highest "sensitivity." Adding just 10 items to a 25-item list changes your variety faster than adding 1000 artists to a 3000-artist list.

---

## 3. Analysis Tools Reference

### `analyze_csv_architecture.py`
**Purpose**: Audits the CSV data layer.
*   Identifying files with <100 entries (candidates for expansion).
*   Checking for header consistency and multi-column support.

### `analyze_obp_generations.py`
**Purpose**: Analyzes actual generation patterns with ground truth accuracy.
*   Uses `_metadata` interception to track engine choices.
*   Tracks frequency of Artists, Subject Types, Lighting, Cameras, and Moods.
*   Identifies overused elements (>2% frequency).

### `run_insanity_sweep.py`
**Purpose**: Compare variety across insanity levels.
*   Runs analysis at levels 1, 3, 5, 7, 10 (configurable).
*   Outputs comparison table showing diversity score, artist count, subject distribution.
*   Helps understand how insanity level affects prompt complexity.

### `audit_structural_bias.py`
**Purpose**: Simulates the list-pruning logic to uncover hidden probability biases.
*   Replays the subject chooser logic from `build_dynamic_prompt.py`.
*   Identifies how artist style selection biases subject type distribution.
*   Useful for understanding why certain subjects appear more often.

### `compare_analyses.py`
**Purpose**: Compare two analysis JSON files to measure improvement or regression.
*   Side-by-side comparison of diversity scores, subject distribution, artist variety.
*   Useful for validating that CSV changes had the intended effect.

### `create_addon_template.py`
**Purpose**: Smart Advisor for content expansion.
*   **Artist Gaps**: Suggests specific artists from underrepresented style tags.
*   **Technical Gaps**: Identifies unused Lenses, Cameras, and Lighting modes.
*   **Actionable Templates**: Outputs pre-formatted CSV rows ready for your `userfiles/`.

---

## 4. Interpreting Reports & Fixing Issues

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

## 6. Testing

The analysis tools have smoke tests to catch regressions:

```bash
../../venv/bin/python3 -m pytest tests/test_analysis_tools.py -v
```

This runs 5 tests covering `OBPAnalyzer`, `run_full_analysis`, and `run_insanity_sweep`.

## 7. Troubleshooting

*   **"Error importing OBP modules"**: Run scripts from the root `OneButtonPrompt` directory, using the venv Python (`../../venv/bin/python3`).
*   **"Analysis takes too long"**: Reduce `--iterations` to 100 or use `run_full_analysis.py --count 100`.
*   **"No improvements after adding files"**:
    *   Ensure files are in `userfiles/`.
    *   Ensure files match the naming convention: `filename_addon.csv`.
    *   **Crucial**: Ensure no empty lines in CSV files (this can cause crashes or silent failures).
    *   Restart ComfyUI/WebUI if running as a node (though CLI tools don't need restart).

---

## 8. Current Baseline (Feb 2026)

Last fresh baseline run (1000 iterations, insanity 5):

| Metric | Value |
|--------|-------|
| Diversity Score | 12.96 |
| Subject Distribution | humanoid 23%, landscape 22%, animal 18%, object 19%, concept 18% |
| Mode Distribution | standard 95%, special modes ~1% each |

Insanity sweep (levels 1→10):
- Diversity scales from 10.3 → 11.9
- Artist variety scales from 119 → 402 unique artists
- Image type variety scales from 14 → 37 unique types

---

## 9. Known Gaps & Future Work

While the current suite covers distribution frequency well, several architectural blind spots remain:

### Missing Capabilities

| Gap | Impact | Plan |
|---|---|---|
| **CSV Call-Graph** | Cannot detect "dead code" (CSVs that are never called). | Create static analysis tool to map `csv_reader` calls. |
| **Tier Verification** | No automated check that `_light` subsets are representative of parent. | Add `verify_tier_coverage.py`. |
| **Weight Syntax Audit** | `(word:1.2)` syntax breaks Stable Cascade. | Add regex search for weights in all CSVs. |
| **Vocabulary Overlap** | Identical terms in different files reduce effective variety. | Add cross-file duplicate detection. |
| **Output Traceability** | Cannot tell *which* CSV a word came from in final prompt. | Add reverse-lookup tool for generated prompts. |

### Healthy Metrics Targets

When analyzing a healthy CSV distribution, aim for:
- **Max Frequency**: No single item > 2.0% (except `comma`, `break`).
- **Artist Distribution**: Top 10 artists should sum to < 15% of total artist calls.
- **Subject Variety**: Standard deviation between subject types should be < 5%.

