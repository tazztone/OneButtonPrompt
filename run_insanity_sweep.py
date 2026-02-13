#!/usr/bin/env python3
"""
OneButtonPrompt Insanity Sweep
Runs analysis across multiple insanity levels and compares variety.
"""

import sys
import os
import argparse
import collections
import json
from analyze_obp_generations import OBPAnalyzer

def run_sweep(iterations=200, levels=[1, 3, 5, 7, 10]):
    print(f"\n{'#'*80}")
    print(f"#  OneButtonPrompt Insanity Level Sweep")
    print(f"#  Testing variety profile across levels: {levels}")
    print(f"{'#'*80}\n")
    
    sweep_results = {}
    
    for level in levels:
        print(f"--- ANALYZING INSANITY LEVEL {level} ---")
        analyzer = OBPAnalyzer()
        analyzer.run_analysis(num_iterations=iterations, insanitylevel=level)
        analyzer.generate_report()
        
        # Capture key metrics
        sweep_results[level] = {
            "diversity_score": analyzer.results.get("diversity_score", 0),
            "subjects": dict(analyzer.results["main_subject_types"]),
            "imagetypes_count": len(analyzer.results["imagetypes"]),
            "artists_count": len(analyzer.results["artists"])
        }
    
    # Print Comparison Table
    print("\n" + "="*80)
    print(f"{'LEVEL':<6} | {'DIVERSITY':<10} | {'ARTISTS':<7} | {'IMG TYPES':<9} | {'SUBJECT DIST (H/L/A/O/C)'}")
    print("-" * 80)
    
    for level in levels:
        res = sweep_results[level]
        subj = res["subjects"]
        subj_str = f"{subj.get('humanoid',0):>2}/{subj.get('landscape',0):>2}/{subj.get('animal',0):>2}/{subj.get('object',0):>2}/{subj.get('concept',0):>2}"
        
        print(f"{level:<6} | "
              f"{res['diversity_score']:>9.4f} | "
              f"{res['artists_count']:>7} | "
              f"{res['imagetypes_count']:>9} | "
              f"{subj_str}")
    
    with open("analysis_results/insanity_sweep_results.json", "w") as f:
        json.dump(sweep_results, f, indent=2)
    print("\n✓ Sweep data saved to analysis_results/insanity_sweep_results.json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OBP Insanity Sweep")
    parser.add_argument("--iterations", type=int, default=200, help="Iterations per level")
    args = parser.parse_args()
    
    run_sweep(iterations=args.iterations)
