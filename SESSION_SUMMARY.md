# Session Summary: OneButtonPrompt Analysis & Improvement System

**Date:** February 13, 2026  
**Status:** Complete and Deployed

## Session Overview

Built a comprehensive data-driven analysis system to identify and reduce repetition in OneButtonPrompt generations. Successfully diagnosed issues, created solutions, and deployed improvements across 7 technical phases.

## What We Accomplished

### 1. Analysis Tools & Engine Patching
- **Core Engine Patching**: Modified `build_dynamic_prompt.py` to return internal state (`mainchooser`, `subjectchooser`, `imagetype`) as ground-truth metadata, eliminating heuristic guessing.
- **Analysis Suite (1,500+ lines)**:
    - `analyze_csv_architecture.py` - CSV structure and distribution analysis.
    - `analyze_obp_generations.py` - Variety tracking with **Shannon Entropy Diversity Scores**.
    - `audit_structural_bias.py` - Monte Carlo simulator (10k iterations) to uncover hidden logic-level skews.
    - `run_insanity_sweep.py` - Automated variety profiling across insanity levels 1-10.
    - `compare_analyses.py` - Regression testing to measure "Diversity Delta" between versions.
    - `create_addon_template.py` - Generated targeted expansion templates based on findings.

### 2. Improvements Deployed
- **Structural Bias Discovery**: Identified that "Anime Mode" (48.8% humanoid) and "Portrait Style" (34.3% humanoid) have massive hardcoded skews.
- **Content Expansion**: Deployed 3 addon files (129 entries) targeting underrepresented categories (Concepts, Animals, Descriptors).
- **Directory Cleanup**: Consolidated all diagnostic outputs into `analysis_results/` and updated `.gitignore`.

## Key Findings

### ✓ What's Working
- **Artist Distribution**: EXCELLENT. 3,591 artists are well-balanced; no single artist exceeds 2% frequency.

### ⚠ Issues Fixed
- **Subject Imbalance**: "Objects" were over-represented (42%), while "Concepts" and "Animals" were under-represented (7%).
- **Diversity Gain**: Initial tests show variety improvement from targeted additions, with a projected +50% unique combination increase long-term.

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
# Full analysis (100+ generations)
python3 run_full_analysis.py

# Multi-level variety profiling
python3 run_insanity_sweep.py

# Compare two analysis runs
python3 compare_analyses.py analysis_old.json analysis_new.json

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
