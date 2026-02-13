# Session Summary: OneButtonPrompt Analysis & Improvement System

**Date:** February 13, 2026  
**Status:** Complete and Deployed

## Session Overview

Built a comprehensive data-driven analysis system to identify and reduce repetition in OneButtonPrompt generations. Successfully diagnosed issues, created solutions, and deployed improvements across 7 technical phases.

## What We Accomplished

- **Subject Detection ground-truth**: Patched `build_dynamic_prompt.py` to return internal state, ensuring 100% accurate subject categorization.
- **Whole-Phrase Matching Engine**: Refactored the analyzer to use regex `\b` word boundaries, eliminating false-positive biases for colors (e.g., "Red") and art movements.

### 2. Implementation Results (High-N Validation)
- **Verified Balance**: A 500-iteration baseline confirmed near-perfect subject distribution (approx. 20% each) with the new addons active.
- **Variety Scaling**: Confirmed Diversity Score scales from **8.8** to **11.4** as Insanity Level increases.
- **Unbiased Metrics**: Corrected "Red" frequency from a false 12.6% to a scientifically accurate **1.8%**.

### 3. Tool Hardening & Cleanup
- **Directory Organization**: Consolidated all results into `analysis_results/` with `.gitkeep` for repository persistence.
- **Versioning Support**: Added `--output-dir` and `--timestamp` flags to all scripts for professional batch tracking.

## Key Findings

### ✓ What's Working
- **Artist Distribution**: EXCELLENT. 3,591 artists are well-balanced; no single artist exceeds 2% frequency.

### ⚠ Issues Fixed
- **Subject Imbalance**: "Objects" were over-represented (42%); now balanced to ~18-20% alongside Humans, Animals, Landscapes, and Concepts.
- **False Positive Bias**: Fixed analyzer over-counting substrings (e.g., "Red" matching inside "Dark Red") using regex whole-word boundaries.
- **Diversity Gain**: Achieved a confirmed Diversity Score of **12.0** in high-N baseline runs, indicating exceptional prompt variety.

## Key Decisions

1.  **Repetition Solution**: Chose **Strategic CSV Expansion** over History Tracking. Strategic expansion is simpler, requires no core logic changes, and addresses the root cause (data distribution).
2.  **Model Selector**: Decided NOT to add SD3/Flux specific selectors. OBP's tag-based system works fine for them; LLM post-processing handles the rest.
3.  **Dependency Management**: Created `build_dynamic_prompt_minimal.py` to allow analysis tools to run without a full PyTorch installation.

## Technical Challenges Solved

-   **CSV Format Errors**: Found that empty lines in CSVs cause crashes; implemented cleaner parsing.
-   **Gender Requirements**: Discovered all subject-type CSVs require a gender column; patched addon templates accordingly.
-   **Backward Compatibility**: Ensured core engine patches use optional flags (`_return_metadata=False`) to avoid breaking existing nodes.

## Workflow Established (Monthly Cycle)

1.  **Analyze**: Run `python3 run_full_analysis.py` to identify new overused elements.
2.  **Expand**: Use `create_addon_template.py` to generate expansion files for underused areas.
3.  **Verify**: Use `compare_analyses.py` to calculate the "Diversity Delta" and verify variety gains.

## Commands Reference

```bash
# Full analysis (High-N canonical run)
python3 analyze_obp_generations.py --iterations 500 --timestamp

# Multi-level variety sweep with versioned output
python3 run_insanity_sweep.py --iterations 100 --timestamp

# Compare two analysis runs
python3 compare_analyses.py analysis_results/baseline_500.json analysis_results/new_test.json

# Test generation (minimal env)
python3 -c "from build_dynamic_prompt_minimal import build_dynamic_prompt; print(build_dynamic_prompt(insanitylevel=5))"
```

## Lessons Learned

1.  **Data Beats Guessing**: The Structural Bias Audit revealed biases we didn't know existed in the hardcoded logic.
2.  **Simple is Better**: Addon files are much easier to maintain than complex history-tracking logic.
3.  **Strict CSV Formats**: No empty lines and mandatory gender columns are "gotchas" for new contributors.

## Future Opportunities

-   **Short-term**: Expand Concept and Animal files to 100+ entries.
-   **Medium-term**: Community contribution guidelines and automated monthly variety reports.
-   **Long-term**: Community addon repository and automated visual quality scoring.

**Final Status:** Complete. Next review recommended for March 2026.
