#!/usr/bin/env python3
"""
OneButtonPrompt Comparison Tool
Compare two analysis JSON files to measure improvement or regression.
"""

import sys
import json
import argparse
from pathlib import Path

def compare_analyses(file1, file2):
    print(f"\n{'='*80}")
    print(f"  OneButtonPrompt Analysis Comparison")
    print(f"  Baseline: {file1}")
    print(f"  Current:  {file2}")
    print(f"{'='*80}\n")
    
    with open(file1, 'r') as f:
        data1 = json.load(f)
    with open(file2, 'r') as f:
        data2 = json.load(f)
        
    metrics = []
    
    # 1. Total Prompts
    metrics.append({
        "label": "Total Prompts",
        "v1": data1.get("total_prompts", 0),
        "v2": data2.get("total_prompts", 0),
        "format": "abs"
    })
    
    # 2. Diversity Score
    v1_div = data1.get("diversity_score", 0)
    v2_div = data2.get("diversity_score", 0)
    metrics.append({
        "label": "Diversity Score",
        "v1": v1_div,
        "v2": v2_div,
        "format": "score"
    })
    
    # 3. Artist / Image Type Count
    metrics.append({
        "label": "Artists Detected",
        "v1": len(data1.get("artists", {})),
        "v2": len(data2.get("artists", {})),
        "format": "abs"
    })
    
    # Print Metrics
    print(f"{'METRIC':<20} | {'BASELINE':<10} | {'CURRENT':<10} | {'DELTA':<10}")
    print("-" * 60)
    for m in metrics:
        v1, v2 = m["v1"], m["v2"]
        delta = v2 - v1
        delta_str = f"{delta:+.4f}" if m["format"] == "score" else f"{delta:+d}"
        
        v1_str = f"{v1:.4f}" if m["format"] == "score" else str(v1)
        v2_str = f"{v2:.4f}" if m["format"] == "score" else str(v2)
        
        print(f"{m['label']:<20} | {v1_str:<10} | {v2_str:<10} | {delta_str:<10}")
        
    # 4. Subject Distribution Deltas
    print(f"\n{'SUBJECT DISTRIBUTION DELTAS (%)':<40}")
    print("-" * 60)
    s1 = data1.get("main_subject_types", {})
    s2 = data2.get("main_subject_types", {})
    all_subjects = sorted(set(list(s1.keys()) + list(s2.keys())))
    
    t1 = sum(s1.values()) or 1
    t2 = sum(s2.values()) or 1
    
    for subj in all_subjects:
        p1 = (s1.get(subj, 0) / t1) * 100
        p2 = (s2.get(subj, 0) / t2) * 100
        delta = p2 - p1
        print(f"{subj:<20} | {p1:>6.1f}% -> {p2:>6.1f}% | Delta: {delta:>+6.1f}%")
        
    # Conclusion
    print("\n" + "="*80)
    if v2_div > v1_div:
        print(f"✓ IMPROVEMENT: Diversity score increased by {v2_div - v1_div:.4f}")
        return 0
    elif v2_div < v1_div:
        print(f"⚠ REGRESSION: Diversity score decreased by {v1_div - v2_div:.4f}")
        return 1
    else:
        print("= NO CHANGE: Diversity score remains the same")
        return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare OBP analysis files")
    parser.add_argument("file1", help="Baseline JSON file")
    parser.add_argument("file2", help="Current JSON file")
    args = parser.parse_args()
    
    if not (Path(args.file1).exists() and Path(args.file2).exists()):
        print("✗ Error: One or both files do not exist.")
        sys.exit(2)
        
    sys.exit(compare_analyses(args.file1, args.file2))
