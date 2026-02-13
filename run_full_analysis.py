#!/usr/bin/env python3
"""
OneButtonPrompt Full Analysis Suite
Runs both generation analysis and CSV architecture analysis,
then combines insights for actionable recommendations
"""

import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")


def run_csv_architecture_analysis():
    """Run CSV architecture analysis"""
    print_header("STEP 1: CSV ARCHITECTURE ANALYSIS")
    print("Analyzing CSV file structure and content distribution...\n")
    
    try:
        print("[DEBUG] Importing CSVArchitectureAnalyzer...")
        from analyze_csv_architecture import CSVArchitectureAnalyzer
        
        print("[DEBUG] Creating analyzer instance...")
        analyzer = CSVArchitectureAnalyzer()
        
        print("[DEBUG] Running analyze_all_csvs()...")
        analyzer.analyze_all_csvs()
        
        print("[DEBUG] Generating architecture report...")
        analyzer.generate_architecture_report()
        
        print("[DEBUG] Identifying expansion opportunities...")
        analyzer.identify_expansion_opportunities()
        
        print("[DEBUG] Saving analysis...")
        analyzer.save_analysis()
        
        print("[DEBUG] CSV analysis complete!")
        return analyzer.analysis
        
    except Exception as e:
        print(f"✗ Error running CSV architecture analysis: {e}")
        import traceback
        traceback.print_exc()
        return None


def run_generation_analysis(num_iterations=1000, insanity_level=5):
    """Run generation pattern analysis"""
    print_header("STEP 2: GENERATION PATTERN ANALYSIS")
    print(f"Generating and analyzing {num_iterations} prompts...\n")
    
    try:
        print("[DEBUG] Importing OBPAnalyzer...")
        from analyze_obp_generations import OBPAnalyzer
        
        print("[DEBUG] Creating analyzer instance...")
        analyzer = OBPAnalyzer()
        
        print("[DEBUG] Running analysis (this may take a few minutes)...")
        analyzer.run_analysis(
            num_iterations=num_iterations,
            insanitylevel=insanity_level
        )
        
        print("[DEBUG] Generating report...")
        analyzer.generate_report()
        
        print("[DEBUG] Saving results...")
        analyzer.save_results()
        
        print("[DEBUG] Generation analysis complete!")
        return analyzer.results
        
    except Exception as e:
        print(f"✗ Error running generation analysis: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_combined_recommendations(csv_analysis, gen_results):
    """Generate combined recommendations from both analyses"""
    
    print_header("STEP 3: COMBINED INSIGHTS & RECOMMENDATIONS")
    
    if not csv_analysis or not gen_results:
        print("⚠ Incomplete analysis data - skipping combined recommendations")
        return
        
    print("Combining architectural knowledge with generation patterns...\n")
    
    recommendations = {
        'immediate': [],
        'short_term': [],
        'long_term': []
    }
    
    # Analyze artist usage vs availability
    total_prompts = len(gen_results.get('all_prompts', []))
    if total_prompts > 0:
        
        # Check for overused artists
        top_artists = gen_results.get('artists', {}).most_common(10)
        if top_artists:
            overuse_threshold = total_prompts * 0.02
            overused = [(a, c) for a, c in top_artists if c > overuse_threshold]
            
            if overused:
                recommendations['immediate'].append({
                    'title': 'Reduce Artist Repetition',
                    'issue': f'{len(overused)} artists appear in >2% of generations',
                    'details': [f"{a}: {(c/total_prompts)*100:.1f}%" for a, c in overused[:5]],
                    'action': 'Create userfiles/artists_addon.csv with 50-100 alternative artists',
                    'impact': 'HIGH - Artists have major visual impact'
                })
                
        # Check subject type balance
        subject_dist = gen_results.get('main_subject_types', {})
        if subject_dist:
            counts = list(subject_dist.values())
            if counts:
                max_count = max(counts)
                min_count = min(counts)
                
                if max_count > min_count * 2:
                    underused = [s for s, c in subject_dist.items() if c < max_count / 2]
                    
                    recommendations['immediate'].append({
                        'title': 'Balance Subject Type Distribution',
                        'issue': f'Subject types are imbalanced (ratio: {max_count/min_count:.1f}:1)',
                        'details': [f"{s}: {c} ({(c/total_prompts)*100:.1f}%)" for s, c in subject_dist.items()],
                        'action': f'Expand CSV files for underused types: {", ".join(underused)}',
                        'impact': 'HIGH - Affects generation variety'
                    })
                    
        # Check for overused image types
        top_imagetypes = gen_results.get('imagetypes', {}).most_common(5)
        if top_imagetypes:
            overused_it = [(it, c) for it, c in top_imagetypes if c > total_prompts * 0.03]
            
            if overused_it:
                recommendations['short_term'].append({
                    'title': 'Diversify Image Types',
                    'issue': f'{len(overused_it)} image types dominate generations',
                    'details': [f"{it}: {(c/total_prompts)*100:.1f}%" for it, c in overused_it],
                    'action': 'Add 20-30 alternative image types to imagetypes.csv',
                    'impact': 'MEDIUM - Affects style variety'
                })
                
    # Check CSV architecture for expansion opportunities
    if csv_analysis:
        
        # Find small but important files
        small_important = []
        important_files = ['descriptors', 'colors', 'lighting', 'quality', 'artmovements']
        
        for filepath, stats in csv_analysis.items():
            filename = Path(filepath).stem
            if any(imp in filename for imp in important_files):
                if stats['total_entries'] < 200:
                    small_important.append((filename, stats['total_entries']))
                    
        if small_important:
            recommendations['short_term'].append({
                'title': 'Expand Core Descriptor Files',
                'issue': f'{len(small_important)} important files have <200 entries',
                'details': [f"{name}.csv: {count} entries" for name, count in small_important],
                'action': 'Double the size of these files with distinctive alternatives',
                'impact': 'MEDIUM - Improves prompt diversity'
            })
            
        # Check for missing user customization
        user_addon_exists = any('userfiles' in str(path) and '_addon' in str(path) 
                               for path in csv_analysis.keys())
        
        if not user_addon_exists:
            recommendations['long_term'].append({
                'title': 'Set Up User Customization System',
                'issue': 'No user addon files detected',
                'details': ['User customization allows easy expansion without modifying core files'],
                'action': 'Create template addon files in userfiles/ directory',
                'impact': 'LOW - Enables easier future customization'
            })
            
    # Print recommendations
    for priority, recs in [('IMMEDIATE ACTION', 'immediate'), 
                           ('SHORT-TERM IMPROVEMENTS', 'short_term'),
                           ('LONG-TERM ENHANCEMENTS', 'long_term')]:
        
        rec_list = recommendations[recs]
        if rec_list:
            print(f"\n{priority}:")
            print("-" * 70)
            
            for i, rec in enumerate(rec_list, 1):
                print(f"\n{i}. {rec['title']} [{rec['impact']} IMPACT]")
                print(f"   Issue:  {rec['issue']}")
                
                if rec['details']:
                    print(f"   Details:")
                    for detail in rec['details'][:5]:
                        print(f"     • {detail}")
                    if len(rec['details']) > 5:
                        print(f"     ... and {len(rec['details']) - 5} more")
                        
                print(f"   Action: {rec['action']}")
                
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}\n")
    
    total_recs = sum(len(recs) for recs in recommendations.values())
    print(f"Total recommendations: {total_recs}")
    print(f"  • Immediate action items: {len(recommendations['immediate'])}")
    print(f"  • Short-term improvements: {len(recommendations['short_term'])}")
    print(f"  • Long-term enhancements: {len(recommendations['long_term'])}")
    
    print("\nNext Steps:")
    print("  1. Review immediate action items and prioritize")
    print("  2. Create addon CSV files for high-impact expansions")
    print("  3. Test new additions with sample generations")
    print("  4. Re-run this analysis after changes to measure improvement")


def main():
    """Main execution function"""
    
    print(f"\n{'#'*70}")
    print(f"#  OneButtonPrompt Full Analysis Suite")
    print(f"#  Comprehensive analysis of generation patterns and CSV architecture")
    print(f"{'#'*70}")
    
    # Configuration
    NUM_ITERATIONS = 100  # Reduced for faster testing
    INSANITY_LEVEL = 5     # Default insanity level for testing
    
    print(f"\nConfiguration:")
    print(f"  • Generations to analyze: {NUM_ITERATIONS}")
    print(f"  • Insanity level: {INSANITY_LEVEL}")
    print(f"  • This will take approximately {NUM_ITERATIONS * 0.1:.0f} seconds")
    
    print("\n[DEBUG] Starting analysis in 2 seconds...")
    import time
    time.sleep(2)
    
    # Step 1: CSV Architecture
    print("\n[DEBUG] Step 1: CSV Architecture Analysis")
    csv_analysis = run_csv_architecture_analysis()
    
    # Step 2: Generation Patterns
    print("\n[DEBUG] Step 2: Generation Pattern Analysis")
    gen_results = run_generation_analysis(
        num_iterations=NUM_ITERATIONS,
        insanity_level=INSANITY_LEVEL
    )
    
    # Step 3: Combined Recommendations
    print("\n[DEBUG] Step 3: Combined Recommendations")
    generate_combined_recommendations(csv_analysis, gen_results)
    
    # Final message
    print_header("ANALYSIS COMPLETE")
    print("Results saved to:")
    print("  • csv_architecture_analysis.json")
    print("  • analysis_results/obp_analysis_results.json")
    print("\nYou can now use these insights to strategically expand your CSV files.")
    print()


if __name__ == "__main__":
    main()
