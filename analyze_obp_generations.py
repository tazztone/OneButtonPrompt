#!/usr/bin/env python3
"""
OneButtonPrompt Generation Analysis Script
Runs OBP multiple times and analyzes patterns in generated prompts
"""

import sys
import os
import re
import json
import collections
from pathlib import Path

# Add current directory to path to import OBP modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Try minimal version first (avoids torch dependency)
    try:
        from build_dynamic_prompt_minimal import build_dynamic_prompt
        print("✓ Using minimal build_dynamic_prompt (superprompter disabled)")
    except:
        # Fall back to full version
        from build_dynamic_prompt import build_dynamic_prompt
        print("✓ Using full build_dynamic_prompt")
    
    from csv_reader import csv_to_list
    print("✓ Successfully imported OBP modules")
except ImportError as e:
    print(f"✗ Error importing OBP modules: {e}")
    print("Make sure this script is in the OneButtonPrompt directory")
    sys.exit(1)


class OBPAnalyzer:
    def __init__(self):
        self.results = {
            'artists': collections.Counter(),
            'subjects': collections.Counter(),
            'imagetypes': collections.Counter(),
            'descriptors': collections.Counter(),
            'art_movements': collections.Counter(),
            'colors': collections.Counter(),
            'lighting': collections.Counter(),
            'camera_terms': collections.Counter(),
            'quality_terms': collections.Counter(),
            'main_subject_types': collections.Counter(),
            'prompt_lengths': [],
            'all_prompts': []
        }
        
        # Load reference data from CSVs for matching
        self.load_reference_data()
        
    def load_reference_data(self):
        """Load CSV data to help identify elements in prompts"""
        print("\nLoading reference data from CSVs...")
        
        try:
            self.ref_artists = set(csv_to_list("artists", directory="./csvfiles/"))
            print(f"  ✓ Loaded {len(self.ref_artists)} artists")
        except:
            self.ref_artists = set()
            print("  ✗ Could not load artists.csv")
            
        try:
            self.ref_imagetypes = set(csv_to_list("imagetypes", directory="./csvfiles/"))
            print(f"  ✓ Loaded {len(self.ref_imagetypes)} image types")
        except:
            self.ref_imagetypes = set()
            print("  ✗ Could not load imagetypes.csv")
            
        try:
            self.ref_artmovements = set(csv_to_list("artmovements", directory="./csvfiles/"))
            print(f"  ✓ Loaded {len(self.ref_artmovements)} art movements")
        except:
            self.ref_artmovements = set()
            print("  ✗ Could not load artmovements.csv")
            
        try:
            self.ref_colors = set(csv_to_list("colors", directory="./csvfiles/"))
            print(f"  ✓ Loaded {len(self.ref_colors)} colors")
        except:
            self.ref_colors = set()
            print("  ✗ Could not load colors.csv")
            
        try:
            self.ref_lighting = set(csv_to_list("lighting", directory="./csvfiles/"))
            print(f"  ✓ Loaded {len(self.ref_lighting)} lighting terms")
        except:
            self.ref_lighting = set()
            print("  ✗ Could not load lighting.csv")
            
    def analyze_prompt(self, prompt):
        """Parse a prompt and extract identifiable elements"""
        
        # Store full prompt
        self.results['all_prompts'].append(prompt)
        self.results['prompt_lengths'].append(len(prompt))
        
        # Convert to lowercase for matching
        prompt_lower = prompt.lower()
        
        # Split into words/phrases (handle commas and special chars)
        words = re.split(r'[,\(\)\[\]:]', prompt_lower)
        words = [w.strip() for w in words if w.strip()]
        
        # Match artists (case-insensitive)
        for artist in self.ref_artists:
            if artist.lower() in prompt_lower:
                self.results['artists'][artist] += 1
                
        # Match image types
        for imagetype in self.ref_imagetypes:
            if imagetype.lower() in prompt_lower:
                self.results['imagetypes'][imagetype] += 1
                
        # Match art movements
        for movement in self.ref_artmovements:
            if movement.lower() in prompt_lower:
                self.results['art_movements'][movement] += 1
                
        # Match colors
        for color in self.ref_colors:
            if color.lower() in prompt_lower:
                self.results['colors'][color] += 1
                
        # Match lighting
        for light in self.ref_lighting:
            if light.lower() in prompt_lower:
                self.results['lighting'][light] += 1
        
        # Detect camera terms (common patterns)
        camera_patterns = [
            'camera', 'lens', 'mm', 'aperture', 'f/', 'iso', 
            'shutter', 'exposure', 'bokeh', 'depth of field'
        ]
        for pattern in camera_patterns:
            if pattern in prompt_lower:
                self.results['camera_terms'][pattern] += 1
                
        # Detect quality terms
        quality_patterns = [
            'detailed', 'masterpiece', 'high quality', 'best quality',
            '8k', '4k', 'hd', 'uhd', 'sharp', 'crisp'
        ]
        for pattern in quality_patterns:
            if pattern in prompt_lower:
                self.results['quality_terms'][pattern] += 1
                
        # Try to detect main subject type (heuristic)
        if any(word in prompt_lower for word in ['man', 'woman', 'person', 'character', 'portrait']):
            self.results['main_subject_types']['humanoid'] += 1
        elif any(word in prompt_lower for word in ['landscape', 'scenery', 'vista', 'view']):
            self.results['main_subject_types']['landscape'] += 1
        elif any(word in prompt_lower for word in ['animal', 'creature', 'beast', 'cat', 'dog', 'bird']):
            self.results['main_subject_types']['animal'] += 1
        elif any(word in prompt_lower for word in ['concept', 'abstract', 'idea']):
            self.results['main_subject_types']['concept'] += 1
        else:
            self.results['main_subject_types']['object'] += 1
            
    def run_analysis(self, num_iterations=1000, insanitylevel=5, **kwargs):
        """Run OBP multiple times and collect statistics"""
        
        print(f"\n{'='*60}")
        print(f"Running {num_iterations} generations with insanity level {insanitylevel}")
        print(f"{'='*60}\n")
        
        for i in range(num_iterations):
            if (i + 1) % 100 == 0:
                print(f"Progress: {i + 1}/{num_iterations} generations...")
                
            try:
                # Generate prompt
                result = build_dynamic_prompt(insanitylevel=insanitylevel, **kwargs)
                
                # Handle different return formats
                if isinstance(result, tuple):
                    prompt = result[0]  # Main prompt
                else:
                    prompt = result
                    
                # Analyze the prompt
                self.analyze_prompt(prompt)
                
            except Exception as e:
                print(f"Error on iteration {i + 1}: {e}")
                continue
                
        print(f"\n✓ Completed {num_iterations} generations\n")
        
    def generate_report(self):
        """Generate comprehensive analysis report"""
        
        total_prompts = len(self.results['all_prompts'])
        if total_prompts == 0:
            print("No prompts generated!")
            return
            
        print(f"\n{'='*60}")
        print(f"ONEBUTTONPROMPT GENERATION ANALYSIS REPORT")
        print(f"{'='*60}")
        print(f"Total prompts analyzed: {total_prompts}\n")
        
        # Average prompt length
        avg_length = sum(self.results['prompt_lengths']) / len(self.results['prompt_lengths'])
        print(f"Average prompt length: {avg_length:.1f} characters")
        print(f"Shortest: {min(self.results['prompt_lengths'])} | Longest: {max(self.results['prompt_lengths'])}\n")
        
        # Main subject type distribution
        print(f"{'='*60}")
        print("MAIN SUBJECT TYPE DISTRIBUTION")
        print(f"{'='*60}")
        for subject_type, count in self.results['main_subject_types'].most_common():
            percentage = (count / total_prompts) * 100
            bar = '█' * int(percentage / 2)
            print(f"{subject_type:12s}: {percentage:5.1f}% {bar} ({count})")
            
        # Top artists
        print(f"\n{'='*60}")
        print("TOP 20 MOST COMMON ARTISTS")
        print(f"{'='*60}")
        
        if self.results['artists']:
            for artist, count in self.results['artists'].most_common(20):
                percentage = (count / total_prompts) * 100
                print(f"{percentage:5.1f}% - {artist:40s} ({count:3d} times)")
        else:
            print("No artists detected in prompts")
            
        # Top image types
        print(f"\n{'='*60}")
        print("TOP 15 MOST COMMON IMAGE TYPES")
        print(f"{'='*60}")
        
        if self.results['imagetypes']:
            for imagetype, count in self.results['imagetypes'].most_common(15):
                percentage = (count / total_prompts) * 100
                print(f"{percentage:5.1f}% - {imagetype:40s} ({count:3d} times)")
        else:
            print("No image types detected in prompts")
            
        # Top art movements
        print(f"\n{'='*60}")
        print("TOP 15 MOST COMMON ART MOVEMENTS")
        print(f"{'='*60}")
        
        if self.results['art_movements']:
            for movement, count in self.results['art_movements'].most_common(15):
                percentage = (count / total_prompts) * 100
                print(f"{percentage:5.1f}% - {movement:40s} ({count:3d} times)")
        else:
            print("No art movements detected in prompts")
            
        # Top colors
        print(f"\n{'='*60}")
        print("TOP 15 MOST COMMON COLORS")
        print(f"{'='*60}")
        
        if self.results['colors']:
            for color, count in self.results['colors'].most_common(15):
                percentage = (count / total_prompts) * 100
                print(f"{percentage:5.1f}% - {color:40s} ({count:3d} times)")
        else:
            print("No colors detected in prompts")
            
        # Lighting terms
        print(f"\n{'='*60}")
        print("TOP 10 MOST COMMON LIGHTING TERMS")
        print(f"{'='*60}")
        
        if self.results['lighting']:
            for light, count in self.results['lighting'].most_common(10):
                percentage = (count / total_prompts) * 100
                print(f"{percentage:5.1f}% - {light:40s} ({count:3d} times)")
        else:
            print("No lighting terms detected in prompts")
            
        # Camera terms
        print(f"\n{'='*60}")
        print("CAMERA/TECHNICAL TERMS USAGE")
        print(f"{'='*60}")
        
        if self.results['camera_terms']:
            for term, count in self.results['camera_terms'].most_common():
                percentage = (count / total_prompts) * 100
                print(f"{percentage:5.1f}% - {term:40s} ({count:3d} times)")
        else:
            print("No camera terms detected in prompts")
            
        # Quality terms
        print(f"\n{'='*60}")
        print("QUALITY TERMS USAGE")
        print(f"{'='*60}")
        
        if self.results['quality_terms']:
            for term, count in self.results['quality_terms'].most_common():
                percentage = (count / total_prompts) * 100
                print(f"{percentage:5.1f}% - {term:40s} ({count:3d} times)")
        else:
            print("No quality terms detected in prompts")
            
        # Generate recommendations
        self.generate_recommendations()
        
    def generate_recommendations(self):
        """Generate actionable recommendations based on analysis"""
        
        total_prompts = len(self.results['all_prompts'])
        overuse_threshold = total_prompts * 0.02  # 2% threshold
        
        print(f"\n{'='*60}")
        print("RECOMMENDATIONS FOR EXPANSION")
        print(f"{'='*60}\n")
        
        recommendations = []
        
        # Check for overused artists
        overused_artists = [
            (artist, count) for artist, count in self.results['artists'].most_common(10)
            if count > overuse_threshold
        ]
        
        if overused_artists:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Artists',
                'issue': f'{len(overused_artists)} artists appear in >2% of prompts',
                'action': f'Add 5-10 alternatives for: {", ".join([a[0] for a in overused_artists[:3]])}...'
            })
            
        # Check for overused image types
        overused_imagetypes = [
            (it, count) for it, count in self.results['imagetypes'].most_common(5)
            if count > overuse_threshold
        ]
        
        if overused_imagetypes:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Image Types',
                'issue': f'{len(overused_imagetypes)} image types appear in >2% of prompts',
                'action': f'Add alternatives for: {", ".join([it[0] for it in overused_imagetypes[:3]])}'
            })
            
        # Check subject type balance
        subject_counts = self.results['main_subject_types']
        if subject_counts:
            max_count = max(subject_counts.values())
            min_count = min(subject_counts.values())
            
            if max_count > min_count * 3:  # If imbalance > 3x
                underused = [s for s, c in subject_counts.items() if c == min_count]
                recommendations.append({
                    'priority': 'HIGH',
                    'category': 'Subject Balance',
                    'issue': f'Subject types are imbalanced (max/min ratio: {max_count/min_count:.1f}x)',
                    'action': f'Expand CSV files for: {", ".join(underused)}'
                })
                
        # Print recommendations
        for priority in ['HIGH', 'MEDIUM', 'LOW']:
            priority_recs = [r for r in recommendations if r['priority'] == priority]
            if priority_recs:
                print(f"{priority} PRIORITY:")
                for rec in priority_recs:
                    print(f"  [{rec['category']}]")
                    print(f"    Issue:  {rec['issue']}")
                    print(f"    Action: {rec['action']}")
                    print()
                    
        if not recommendations:
            print("✓ No major issues detected! Distribution looks balanced.")
            
    def save_results(self, filename="obp_analysis_results.json"):
        """Save analysis results to JSON file"""
        
        # Convert Counter objects to dicts for JSON serialization
        output = {
            'total_prompts': len(self.results['all_prompts']),
            'avg_prompt_length': sum(self.results['prompt_lengths']) / len(self.results['prompt_lengths']),
            'artists': dict(self.results['artists'].most_common(50)),
            'imagetypes': dict(self.results['imagetypes'].most_common(30)),
            'art_movements': dict(self.results['art_movements'].most_common(30)),
            'colors': dict(self.results['colors'].most_common(30)),
            'lighting': dict(self.results['lighting'].most_common(20)),
            'camera_terms': dict(self.results['camera_terms']),
            'quality_terms': dict(self.results['quality_terms']),
            'main_subject_types': dict(self.results['main_subject_types']),
            'sample_prompts': self.results['all_prompts'][:20]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
            
        print(f"\n✓ Results saved to {filename}")


def main():
    """Main execution function"""
    
    print("OneButtonPrompt Generation Analyzer")
    print("=" * 60)
    
    # Configuration
    NUM_ITERATIONS = 1000
    INSANITY_LEVEL = 5
    
    # Create analyzer
    analyzer = OBPAnalyzer()
    
    # Run analysis
    analyzer.run_analysis(
        num_iterations=NUM_ITERATIONS,
        insanitylevel=INSANITY_LEVEL,
        # Add any other parameters you want to test
        # artists="all",
        # imagetype="all",
        # base_model="SD1.5"
    )
    
    # Generate report
    analyzer.generate_report()
    
    # Save results
    analyzer.save_results()
    
    print(f"\n{'='*60}")
    print("Analysis complete!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
