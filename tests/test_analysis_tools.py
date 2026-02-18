"""
Regression tests for the OBP analysis pipeline.

These tests guard against the class of bug introduced in the Phase 11/12
refactoring (commit 5f36f85) where new modules (ListManager, SubjectSelector,
ModeSelector, EnhancerSelector) were only imported in the package branch of
build_dynamic_prompt.py, causing all analysis tools to crash with
  NameError: name 'ListManager' is not defined
when run in standalone mode (which is how every analysis script runs).

A single 5-iteration smoke run is enough to catch any import or runtime crash
in the generation pipeline without making the test suite slow.

Import strategy: analyze_obp_generations.py is a standalone script that uses
sys.path.insert + bare imports (not package imports). We must import it the
same way — by inserting the OBP root into sys.path and importing directly —
otherwise the package-relative import path in build_dynamic_prompt.py is taken
and the standalone branch (the one that was broken) is never exercised.
"""
import sys
import os
import importlib
import pytest

# Resolve the OBP root (one level up from this tests/ directory)
_OBP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Insert at position 0 so bare imports resolve to OBP modules, not installed packages.
# conftest.py already inserted the custom_nodes *parent* dir; we need the OBP root
# itself so that `import build_dynamic_prompt` finds the standalone copy.
if _OBP_ROOT not in sys.path:
    sys.path.insert(0, _OBP_ROOT)

# Import the analyzer module directly (standalone style, same as the script itself).
# We use importlib so we can control the import without triggering the package path.
_analyzer_spec = importlib.util.spec_from_file_location(
    "analyze_obp_generations_standalone",
    os.path.join(_OBP_ROOT, "analyze_obp_generations.py"),
)
_analyzer_mod = importlib.util.module_from_spec(_analyzer_spec)
_analyzer_spec.loader.exec_module(_analyzer_mod)
OBPAnalyzer = _analyzer_mod.OBPAnalyzer


class TestAnalysisPipelineSmoke:
    """Smoke tests: the analysis pipeline must not crash and must produce results."""

    def test_analyzer_imports_without_error(self):
        """OBPAnalyzer must be instantiable (catches standalone import regressions)."""
        analyzer = OBPAnalyzer()
        assert analyzer is not None

    def test_run_analysis_produces_prompts(self):
        """A minimal run must produce at least one prompt (catches zero-result failures)."""
        analyzer = OBPAnalyzer()
        analyzer.run_analysis(num_iterations=5, insanitylevel=5)
        assert len(analyzer.results['all_prompts']) > 0, (
            "run_analysis produced zero prompts — the generation pipeline likely crashed. "
            "Check for NameError on ListManager/SubjectSelector/ModeSelector/EnhancerSelector "
            "in the standalone import branch of build_dynamic_prompt.py."
        )

    def test_run_analysis_records_subject_types(self):
        """Subject type metadata must be recorded (catches metadata pipeline failures)."""
        analyzer = OBPAnalyzer()
        analyzer.run_analysis(num_iterations=5, insanitylevel=5)
        assert len(analyzer.results['main_subject_types']) > 0, (
            "No subject types were recorded — metadata is not flowing from "
            "build_dynamic_prompt into OBPAnalyzer.analyze_prompt."
        )

    def test_run_analysis_all_prompts_are_strings(self):
        """Every generated prompt must be a non-empty string (or a list containing one)."""
        analyzer = OBPAnalyzer()
        analyzer.run_analysis(num_iterations=5, insanitylevel=5)
        for i, prompt in enumerate(analyzer.results['all_prompts']):
            # build_dynamic_prompt returns [str], so OBPAnalyzer may store the list or
            # the unwrapped string depending on its analyze_prompt implementation.
            if isinstance(prompt, list):
                assert len(prompt) > 0, f"Prompt {i} is an empty list"
                prompt = prompt[0]
            assert isinstance(prompt, str), f"Prompt {i} is not a string: {type(prompt)}"
            assert len(prompt) > 0, f"Prompt {i} is an empty string"

    def test_run_analysis_with_forced_subject_types(self):
        """Analysis must work when forcesubject is set (exercises subject selector paths)."""
        for subject in ["humanoid", "animal", "landscape", "object", "concept"]:
            analyzer = OBPAnalyzer()
            analyzer.run_analysis(num_iterations=2, insanitylevel=5, forcesubject=subject)
            assert len(analyzer.results['all_prompts']) > 0, (
                f"run_analysis produced zero prompts for forcesubject='{subject}'"
            )
