#!/usr/bin/env python3
"""
Addon CSV Template Creator
Helps create addon CSV files based on analysis recommendations
"""

import json
import sys
import csv
import argparse
from pathlib import Path
from collections import Counter, defaultdict


class CategoryMapper:
    """Maps artists to tags based on artists_and_category.csv"""
    def __init__(self):
        self.tag_to_artists = defaultdict(set)
        self.artist_tags = defaultdict(set)
        self.tags_list = []
        self._load()

    def _load(self):
        csv_path = Path("csvfiles/artists_and_category.csv")
        if not csv_path.exists():
            return

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            
            # Boolean tag columns start after 'Description' (index 3)
            # 0: Artist, 1: Tags, 2: Medium, 3: Description, 4: popular, 5: greg mode, 6: 3D...
            self.tags_list = header[4:] 
            
            for row in reader:
                if not row: continue
                artist = row[0]
                
                # 1. Parse comma-separated tags from column 1
                if len(row) > 1 and row[1]:
                    tags = [t.strip().lower() for t in row[1].split(',')]
                    for t in tags:
                        if t:
                            self.tag_to_artists[t].add(artist)
                            self.artist_tags[artist].add(t)
                
                # 2. Parse boolean columns
                for i, val in enumerate(row[4:], start=4):
                    if val == '1':
                        tag = header[i].lower()
                        self.tag_to_artists[tag].add(artist)
                        self.artist_tags[artist].add(tag)

    def get_artists_for_tag(self, tag):
        return self.tag_to_artists.get(tag.lower(), set())

    def get_tags_for_artist(self, artist):
        return self.artist_tags.get(artist, set())

    def get_all_tags(self):
        return sorted(list(self.tag_to_artists.keys()))


class TechnicalTermMapper:
    """Loads terms from various technical CSV files"""
    def __init__(self):
        self.categories = {
            'lighting': 'csvfiles/lighting.csv',
            'lenses': 'csvfiles/lenses.csv',
            'cameras': 'csvfiles/cameras.csv',
            'moods': 'csvfiles/moods.csv'
        }
        self.category_terms = {}
        self._load()

    def _load(self):
        for cat, path in self.categories.items():
            full_path = Path(path)
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    # Simple line-by-line loader for list CSVs
                    self.category_terms[cat] = set(
                        line.strip() for line in f 
                        if line.strip() and not line.startswith('#')
                    )
            else:
                self.category_terms[cat] = set()

    def get_terms(self, category):
        return self.category_terms.get(category, set())


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


def create_artists_addon(results, mapper, top_gaps=10):
    """Create template for artists_addon.csv using data-driven gap detection"""
    
    print(f"\n{'='*60}")
    print("ARTISTS ADDON TEMPLATE (Data-Driven)")
    print(f"{'='*60}\n")
    
    if 'artists' not in results or not results['artists']:
        print("No artist data in analysis results")
        return
        
    total_prompts = results['total_prompts']
    overuse_threshold = total_prompts * 0.02
    appeared_artists = set(results['artists'].keys())
    
    # Step A: Detect overused artists
    overused = [(artist, count) for artist, count in results['artists'].items() 
                if count > overuse_threshold]
    
    if overused:
        print(f"Detected {len(overused)} overused artists (appearing in >2% of prompts):")
        for artist, count in sorted(overused, key=lambda x: x[1], reverse=True)[:5]:
            percentage = (count / total_prompts) * 100
            print(f"  {percentage:5.1f}% - {artist}")
    else:
        print("✓ No overused artists detected.")

    # Step B: Compute tag coverage gaps
    tag_stats = []
    for tag in mapper.get_all_tags():
        all_artists_with_tag = mapper.get_artists_for_tag(tag)
        if not all_artists_with_tag: continue
        
        appeared_with_tag = all_artists_with_tag.intersection(appeared_artists)
        appeared_count = len(appeared_with_tag)
        total_in_tag = len(all_artists_with_tag)
        
        # Gap score: 1.0 = nothing appeared, 0.0 = everything appeared
        gap_score = (total_in_tag - appeared_count) / total_in_tag
        
        tag_stats.append({
            'tag': tag,
            'appeared': appeared_count,
            'total': total_in_tag,
            'gap_score': gap_score,
            'unseen': list(all_artists_with_tag - appeared_artists)
        })

    # Rank tags by gap score (prioritize tags that have at least N artists so we don't get tiny niche noise)
    # Also prioritize tags that actually have artists we haven't seen yet
    top_tags = sorted([t for t in tag_stats if t['total'] >= 5 and t['unseen']], 
                      key=lambda x: (x['gap_score'], x['total']), reverse=True)[:top_gaps]

    print(f"\nDetected top {len(top_tags)} style blind spots (Underrepresented tags):")
    for t in top_tags[:5]:
        print(f"  Gap {t['gap_score']:.2f} | {t['tag']:<15} ({t['appeared']}/{t['total']} appeared)")

    # Step C: Generate targeted suggestions
    template_lines = [
        "# Artists Addon - Data-Driven Suggestions",
        "# Based on detected blind spots and style gaps",
        "# Format: Artist Name (one per line)",
        ""
    ]

    for t in top_tags:
        template_lines.append(f"# ── UNDERREPRESENTED: {t['tag']} ({t['appeared']} of {t['total']} artists appeared) ──")
        template_lines.append(f"# Gap Score: {t['gap_score']:.2f} | Priority: {'HIGH' if t['gap_score'] > 0.8 else 'MEDIUM'}")
        
        # Suggest up to 10 artists from this tag that didn't appear
        suggestions = sorted(t['unseen'])[:10]
        for s in suggestions:
            template_lines.append(s)
        template_lines.append("")

    template = "\n".join(template_lines)
    
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


def create_technical_addon(results, tech_mapper):
    """Create template for technical_addon_template.csv using gap detection"""
    
    print(f"\n{'='*60}")
    print("TECHNICAL ADDON TEMPLATE (Data-Driven)")
    print(f"{'='*60}\n")
    
    # Map analysis keys to technical categories
    key_map = {
        'lighting': 'lighting',
        'lenses': 'lens',
        'cameras': 'camera',
        'moods': 'lighting'  # Fallback: moods often appear in lighting or generic descriptors
    }
    
    ground_truth = results.get('ground_truth', {})
    template_lines = [
        "# Technical Addon - Data-Driven Suggestions",
        "# Based on detected blind spots in technical categories",
        "# Format: One entry per line",
        ""
    ]
    
    found_any = False
    
    for cat_name, csv_path in tech_mapper.categories.items():
        all_terms = tech_mapper.get_terms(cat_name)
        if not all_terms: continue
        
        # Get appeared terms from analysis
        analysis_key = key_map.get(cat_name)
        appeared = set()
        
        # Priority 1: Ground Truth
        if analysis_key in ground_truth:
            appeared = set(ground_truth[analysis_key].keys())
        # Priority 2: Regex analysis
        elif cat_name in results:
            appeared = set(results[cat_name].keys())
        # Priority 3: Special case for cameras
        elif cat_name == 'cameras' and 'camera_terms' in results:
            appeared = set(results['camera_terms'].keys())
            
        unseen = all_terms - appeared
        total = len(all_terms)
        appeared_count = len(appeared)
        
        if unseen:
            found_any = True
            gap_score = (total - appeared_count) / total
            template_lines.append(f"# ── UNUSED {cat_name.upper()} ({appeared_count} of {total} appeared) ──")
            template_lines.append(f"# Gap Score: {gap_score:.2f} | Priority: {'HIGH' if total < 50 else 'MEDIUM'}")
            
            # Suggest up to 15 items
            suggestions = sorted(list(unseen))[:15]
            for s in suggestions:
                template_lines.append(s)
            template_lines.append("")

    if not found_any:
        print("✓ All technical categories are well-represented!")
        return

    template = "\n".join(template_lines)
    print(template)
    
    save_path = Path("userfiles/technical_addon_template.csv")
    save_path.parent.mkdir(exist_ok=True)
    
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(template)
        
    print(f"\n✓ Template saved to: {save_path}")


def create_tag_coverage_matrix(results, mapper):
    """Calculate appearance rates for each tag"""
    appeared_artists = set(results.get('artists', {}).keys())
    matrix = []
    
    for tag in mapper.get_all_tags():
        all_artists = mapper.get_artists_for_tag(tag)
        if not all_artists: continue
        
        appeared = all_artists.intersection(appeared_artists)
        rate = len(appeared) / len(all_artists)
        
        matrix.append({
            'tag': tag,
            'appeared': len(appeared),
            'total': len(all_artists),
            'rate': rate
        })
    
    return sorted(matrix, key=lambda x: x['rate'])

def create_weighted_report(results, mapper):
    """Generate a report on 'Effective Weights' and tag coverage"""
    print(f"\n{'='*60}")
    print("EFFECTIVE WEIGHT & TAG COVERAGE REPORT")
    print(f"{'='*60}\n")
    
    core_stats = get_core_file_stats()
    
    print(f"{'CATEGORY':<20} | {'CORE SIZE':<10} | {'SENSITIVITY'}")
    print("-" * 60)
    
    categories = [
        ('artists', 'artists'),
        ('imagetypes', 'imagetypes'),
        ('colors', 'colors'),
        ('lighting', 'lighting')
    ]
    
    for label, core_key in categories:
        core_size = core_stats.get(core_key, 100)
        sensitivity = 1.0 / (core_size + 1.0)
        print(f"{label:<20} | {core_size:<10} | {sensitivity:>8.4f}")

    # Tag Coverage Matrix
    matrix = create_tag_coverage_matrix(results, mapper)
    
    print(f"\n{'TAG COVERAGE (STYLE GAPS)':<30} | {'APPEARED/TOTAL':<15} | {'RATE'}")
    print("-" * 60)
    
    # Show bottom 10 (blind spots)
    print("Top Blind Spots (Least Covered):")
    for item in [m for m in matrix if m['total'] >= 5][:10]:
        print(f"  {item['tag']:<28} | {item['appeared']:>7}/{item['total']:<7} | {item['rate']:>6.1%}")
        
    # Show top 5 (best covered)
    print("\nBest Covered Styles:")
    for item in sorted(matrix, key=lambda x: x['rate'], reverse=True)[:5]:
        print(f"  {item['tag']:<28} | {item['appeared']:>7}/{item['total']:<7} | {item['rate']:>6.1%}")

    print("\n[!] Expansion Strategy:")
    print("  • High Sensitivity categories require fewer additions to see impact.")
    print("  • Focus on Blind Spots with low coverage rates to improve diversity.")

def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description="OneButtonPrompt Addon Template Creator")
    parser.add_argument("--top-gaps", type=int, default=10, help="Number of style gaps to include (default: 10)")
    parser.add_argument("--results", type=str, default="analysis_results/obp_analysis_results.json", help="Path to analysis results JSON")
    args = parser.parse_args()
    
    print("OneButtonPrompt Addon Template Creator")
    print("=" * 60)
    
    # Load analysis results
    results = load_analysis_results()
    if not results:
        return

    # Initialize Category Mapper
    print("Loading artist categories from csvfiles/artists_and_category.csv...")
    mapper = CategoryMapper()
    
    print(f"\nLoaded analysis results:")
    print(f"  Total prompts analyzed: {results['total_prompts']}")
    print(f"  Unique artists found: {len(results.get('artists', {}))}")
    
    # Create templates
    create_artists_addon(results, mapper, top_gaps=args.top_gaps)
    create_descriptors_addon(results)
    create_concepts_addon(results)
    
    # Initialize Technical Mapper
    print("Loading technical categories...")
    tech_mapper = TechnicalTermMapper()
    create_technical_addon(results, tech_mapper)
    
    create_weighted_report(results, mapper)
    
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
    print("   • technical_addon_template.csv → technical_addon.csv")
    print("4. Test with sample generations")
    print("5. Re-run analysis to verify improvements")
    print()


if __name__ == "__main__":
    main()
