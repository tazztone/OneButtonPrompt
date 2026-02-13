#!/usr/bin/env python3
"""
Addon CSV Template Creator
Helps create addon CSV files based on analysis recommendations
"""

import json
import sys
from pathlib import Path


def load_analysis_results():
    """Load the analysis results JSON"""
    results_file = Path("analysis_results/obp_analysis_results.json")
    
    if not results_file.exists():
        print("✗ Analysis results not found!")
        print("  Run 'python3 analyze_obp_generations.py' first")
        return None
        
    with open(results_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_core_file_stats():
    """Estimate core file entries based on size"""
    csv_dir = Path("csvfiles")
    stats = {}
    if csv_dir.exists():
        for f in csv_dir.glob("*.csv"):
            # Estimate: ~50 bytes per line for typical OBP CSVs
            stats[f.stem] = max(1, f.stat().st_size // 50)
    return stats


def create_artists_addon(results, num_suggestions=50):
    """Create template for artists_addon.csv"""
    
    print(f"\n{'='*60}")
    print("ARTISTS ADDON TEMPLATE")
    print(f"{'='*60}\n")
    
    if 'artists' not in results or not results['artists']:
        print("No artist data in analysis results")
        return
        
    total_prompts = results['total_prompts']
    overuse_threshold = total_prompts * 0.02
    
    # Find overused artists
    overused = [(artist, count) for artist, count in results['artists'].items() 
                if count > overuse_threshold]
    
    if not overused:
        print("✓ No overused artists detected!")
        return
        
    print(f"Found {len(overused)} overused artists (appearing in >2% of prompts)\n")
    print("Top overused artists:")
    for artist, count in sorted(overused, key=lambda x: x[1], reverse=True)[:10]:
        percentage = (count / total_prompts) * 100
        print(f"  {percentage:5.1f}% - {artist}")
        
    print(f"\nRecommendation: Add {num_suggestions} alternative artists")
    print("\nTemplate for userfiles/artists_addon.csv:")
    print("-" * 60)
    
    template = """# Artists Addon - Add alternatives to reduce repetition
# Format: Artist Name (one per line)
# These will be added to the main artists list

# Fantasy/Digital Art alternatives
Karla Ortiz
Bastien Lecouffe-Deharme
Ruan Jia
Wlop
Guweiz
Sakimichan
Ilya Kuvshinov
Loish
Ross Draws
Zeronis

# Concept Art alternatives
Feng Zhu
Ryan Church
Syd Mead
John Park
Maciej Kuciara
Sparth
Craig Mullins
Jaime Jones
Eytan Zana
Jama Jurabaev

# Portrait alternatives
Ilya Repin
John Singer Sargent
Anders Zorn
Joaquín Sorolla
Diego Velázquez
Rembrandt van Rijn
Johannes Vermeer
Thomas Eakins
Mary Cassatt
Cecilia Beaux

# Landscape alternatives
Albert Bierstadt
Thomas Moran
Frederic Edwin Church
Ivan Aivazovsky
J.M.W. Turner
Claude Monet
Caspar David Friedrich
Thomas Cole
Asher Brown Durand
Sanford Robinson Gifford

# Modern/Contemporary alternatives
Banksy
Takashi Murakami
Yayoi Kusama
Jeff Koons
Damien Hirst
Anselm Kiefer
Gerhard Richter
David Hockney
Kehinde Wiley
Jenny Saville

# Add your own artists below:
"""
    
    print(template)
    
    # Offer to save
    save_path = Path("userfiles/artists_addon_template.csv")
    save_path.parent.mkdir(exist_ok=True)
    
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(template)
        
    print(f"\n✓ Template saved to: {save_path}")
    print(f"  Edit this file and rename to 'artists_addon.csv' to activate")


def create_descriptors_addon(results):
    """Create template for descriptors_addon.csv"""
    
    print(f"\n{'='*60}")
    print("DESCRIPTORS ADDON TEMPLATE")
    print(f"{'='*60}\n")
    
    print("Adding distinctive descriptors increases prompt variety")
    print("\nTemplate for userfiles/descriptors_addon.csv:")
    print("-" * 60)
    
    template = """# Descriptors Addon - Distinctive adjectives
# Format: descriptor,gender
# Gender: male, female, both, genderless

# Visual qualities
bioluminescent,both
crystalline,both
ethereal,both
weathered-by-time,both
impossibly-geometric,both
art-deco-inspired,both
biomechanical,both
holographic,both
iridescent,both
translucent,both

# Atmospheric
otherworldly,both
dreamlike,both
haunting,both
serene,both
chaotic,both
melancholic,both
euphoric,both
ominous,both
tranquil,both
turbulent,both

# Stylistic
minimalist,both
maximalist,both
brutalist,both
ornate,both
austere,both
baroque-inspired,both
neo-classical,both
avant-garde,both
retro-futuristic,both
post-apocalyptic,both

# Textural
gossamer,both
rugged,both
polished,both
corroded,both
pristine,both
weathered,both
smooth,both
rough-hewn,both
delicate,both
robust,both

# Add your own descriptors below:
"""
    
    print(template)
    
    save_path = Path("userfiles/descriptors_addon_template.csv")
    save_path.parent.mkdir(exist_ok=True)
    
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(template)
        
    print(f"\n✓ Template saved to: {save_path}")


def create_concepts_addon(results):
    """Create template for concepts_addon.csv"""
    
    print(f"\n{'='*60}")
    print("CONCEPTS ADDON TEMPLATE")
    print(f"{'='*60}\n")
    
    # Check if concepts are underused
    if 'main_subject_types' in results:
        subject_dist = results['main_subject_types']
        total = sum(subject_dist.values())
        
        if 'concept' in subject_dist:
            concept_pct = (subject_dist['concept'] / total) * 100
            print(f"Current concept usage: {concept_pct:.1f}%")
            
            if concept_pct < 10:
                print("⚠ Concepts are underused - expansion recommended\n")
    
    print("Template for userfiles/concepts_addon.csv:")
    print("-" * 60)
    
    template = """# Concepts Addon - Abstract ideas and themes
# Format: concept,gender
# Gender: genderless (concepts are typically genderless)

# Philosophical
existential dread,genderless
collective consciousness,genderless
temporal paradox,genderless
quantum entanglement,genderless
infinite recursion,genderless
cosmic insignificance,genderless
transcendent awareness,genderless
metaphysical uncertainty,genderless
ontological crisis,genderless
epistemological doubt,genderless

# Emotional/Psychological
cognitive dissonance,genderless
emotional catharsis,genderless
psychological fragmentation,genderless
inner turmoil,genderless
spiritual awakening,genderless
mental clarity,genderless
emotional resonance,genderless
psychological depth,genderless
existential joy,genderless
profound melancholy,genderless

# Scientific/Technical
technological singularity,genderless
artificial consciousness,genderless
genetic evolution,genderless
quantum superposition,genderless
dimensional shift,genderless
entropy reversal,genderless
information theory,genderless
chaos theory,genderless
emergence,genderless
complexity,genderless

# Social/Cultural
cultural zeitgeist,genderless
social paradigm shift,genderless
collective memory,genderless
cultural synthesis,genderless
societal transformation,genderless
generational divide,genderless
cultural renaissance,genderless
social upheaval,genderless
paradigm shift,genderless
cultural evolution,genderless

# Add your own concepts below:
"""
    
    print(template)
    
    save_path = Path("userfiles/concepts_addon_template.csv")
    save_path.parent.mkdir(exist_ok=True)
    
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(template)
        
    print(f"\n✓ Template saved to: {save_path}")

def create_weighted_report(results):
    """Generate a report on 'Effective Weights' and dilution"""
    print(f"\n{'='*60}")
    print("EFFECTIVE WEIGHT & DILUTION REPORT")
    print(f"{'='*60}\n")
    
    core_stats = get_core_file_stats()
    
    print(f"{'CATEGORY':<20} | {'CORE SIZE':<10} | {'SENSITIVITY'}")
    print("-" * 60)
    
    # Categories to check
    categories = [
        ('artists', 'artists'),
        ('imagetypes', 'imagetypes'),
        ('colors', 'colors'),
        ('lighting', 'lighting')
    ]
    
    for label, core_key in categories:
        core_size = core_stats.get(core_key, 100)
        
        # Sensitivity: how much "weight" a single new entry would have
        # If core is 1000, 1 new entry is 0.1% of the list.
        sensitivity = 1.0 / (core_size + 1.0)
        
        print(f"{label:<20} | {core_size:<10} | {sensitivity:>8.4f}")

    print("\n[!] Expansion Strategy:")
    print("  • High Sensitivity categories require fewer additions to see impact.")
    print("  • Adding to small lists (high sensitivity) has more immediate visual impact.")

def main():
    """Main execution"""
    
    print("OneButtonPrompt Addon Template Creator")
    print("=" * 60)
    
    # Load analysis results
    results = load_analysis_results()
    
    if not results:
        return
        
    print(f"\nLoaded analysis results:")
    print(f"  Total prompts analyzed: {results['total_prompts']}")
    print(f"  Unique artists found: {len(results.get('artists', {}))}")
    
    # Create templates
    create_artists_addon(results)
    create_descriptors_addon(results)
    create_concepts_addon(results)
    create_weighted_report(results)
    
    # Final instructions
    print(f"\n{'='*60}")
    print("NEXT STEPS")
    print(f"{'='*60}\n")
    
    print("1. Review the template files in userfiles/")
    print("2. Edit templates to add your own entries")
    print("3. Rename files (remove '_template' suffix):")
    print("   • artists_addon_template.csv → artists_addon.csv")
    print("   • descriptors_addon_template.csv → descriptors_addon.csv")
    print("   • concepts_addon_template.csv → concepts_addon.csv")
    print("4. Test with sample generations")
    print("5. Re-run analysis to verify improvements")
    print()


if __name__ == "__main__":
    main()
