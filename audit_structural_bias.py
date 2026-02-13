#!/usr/bin/env python3
"""
OneButtonPrompt Structural Bias Audit
Simulates the list-pruning logic to uncover hidden probability biases.
"""

import random
import collections
import json

def simulate_chooser(insanitylevel, artiststyleselector="none", artists="all", anime_mode=False, forcesubject="all"):
    """
    Exact replay of the list-pruning logic from build_dynamic_prompt.py (~lines 1460-1605)
    """
    mainchooserlist = ["object", "animal", "humanoid", "landscape", "concept"]
    
    # 1. Art Category Based Biasing (Humanoids)
    artiststylelistforchecking_humanoid = ["popular", "3D", "anime", "art nouveau", "art deco", "character", "fantasy", "fashion", "manga", "photography", "portrait", "sci-fi"]
    if ((artiststyleselector in artiststylelistforchecking_humanoid or artists in artiststylelistforchecking_humanoid)
       and (forcesubject == "all" or forcesubject == "")):
        
        if(random.randint(0,6) > max(2, insanitylevel - 2) and "concept" in mainchooserlist):
            mainchooserlist.remove("concept")
        if(random.randint(0,6) > max(2, insanitylevel - 2) and "landscape" in mainchooserlist):
            mainchooserlist.remove("landscape")
        if(random.randint(0,6) > max(2, insanitylevel - 2) and "object" in mainchooserlist):
            mainchooserlist.remove("object")
        if(random.randint(0,6) > max(2, insanitylevel - 2) and "animal" in mainchooserlist):
            mainchooserlist.remove("animal")

    # 2. Art Category Based Biasing (Landscapes)
    artiststylelistforchecking_landscape = ["architecture", "bauhaus", "cityscape", "cinema", "cloudscape", "impressionism", "installation", "landscape", "magical realism", "nature", "romanticism", "seascape", "space", "streetscape"]
    if ((artiststyleselector in artiststylelistforchecking_landscape or artists in artiststylelistforchecking_landscape)
       and (forcesubject == "all" or forcesubject == "")):
        
        if(random.randint(0,6) > max(2, insanitylevel - 2) and "concept" in mainchooserlist):
            mainchooserlist.remove("concept")
        if(random.randint(0,6) > max(2, insanitylevel - 2) and "animal" in mainchooserlist):
            mainchooserlist.remove("animal")
        if(random.randint(0,6) > max(2, insanitylevel - 2) and "object" in mainchooserlist):
            mainchooserlist.remove("object")
        if(random.randint(0,8) > max(2, insanitylevel - 2) and "humanoid" in mainchooserlist):
            mainchooserlist.remove("humanoid")

    # 3. Anime Mode Biasing
    if (anime_mode and (forcesubject == "all" or forcesubject == "")):
        if(random.randint(0,11) > max(2, insanitylevel - 2) and "concept" in mainchooserlist):
            mainchooserlist.remove("concept")
        if(random.randint(0,11) > max(2, insanitylevel - 2) and "landscape" in mainchooserlist):
            mainchooserlist.remove("landscape")
        if(random.randint(0,11) > max(2, insanitylevel - 2) and "object" in mainchooserlist):
            mainchooserlist.remove("object")
        if(random.randint(0,8) > max(2, insanitylevel - 2) and "animal" in mainchooserlist):
            mainchooserlist.remove("animal")

    # Choose
    mainchooser = random.choice(mainchooserlist)
    return mainchooser

def run_audit(iterations=10000):
    print(f"Running Structural Bias Audit ({iterations} iterations per condition)...")
    
    scenarios = [
        {"name": "Default (Level 5)", "insanity": 5, "style": "none"},
        {"name": "Level 1 (Conservative)", "insanity": 1, "style": "none"},
        {"name": "Level 10 (Insane)", "insanity": 10, "style": "none"},
        {"name": "Portrait Style (Level 5)", "insanity": 5, "style": "portrait"},
        {"name": "Landscape Style (Level 5)", "insanity": 5, "style": "landscape"},
        {"name": "Anime Mode (Level 5)", "insanity": 5, "style": "none", "anime": True},
    ]
    
    results = {}
    
    for s in scenarios:
        counts = collections.Counter()
        for _ in range(iterations):
            choice = simulate_chooser(
                s["insanity"], 
                artiststyleselector=s["style"], 
                anime_mode=s.get("anime", False)
            )
            counts[choice] += 1
        
        # Convert to percentages
        results[s["name"]] = {k: (v/iterations)*100 for k, v in counts.items()}

    # Print Report
    print("\n" + "="*80)
    print(f"{'SCENARIO':<30} | {'OBJ %':<7} | {'ANI %':<7} | {'HUM %':<7} | {'LAN %':<7} | {'CON %':<7}")
    print("-" * 80)
    
    for name, dist in results.items():
        print(f"{name:<30} | "
              f"{dist.get('object', 0):>6.1f}% | "
              f"{dist.get('animal', 0):>6.1f}% | "
              f"{dist.get('humanoid', 0):>6.1f}% | "
              f"{dist.get('landscape', 0):>6.1f}% | "
              f"{dist.get('concept', 0):>6.1f}%")
    
    with open("analysis_results/structural_bias_audit.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\n✓ Audit data saved to analysis_results/structural_bias_audit.json")

if __name__ == "__main__":
    run_audit()
