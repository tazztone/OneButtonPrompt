#!/usr/bin/env python3
"""
OneButtonPrompt CSV Architecture Analyzer
Analyzes the structure and content of CSV files to understand data distribution
"""

import csv
import os
import json
import collections
from pathlib import Path


class CSVArchitectureAnalyzer:
    def __init__(self, csvfiles_dir="./csvfiles", userfiles_dir="./userfiles"):
        self.csvfiles_dir = Path(csvfiles_dir)
        self.userfiles_dir = Path(userfiles_dir)
        self.analysis = {}
        
    def analyze_csv_file(self, filepath):
        """Analyze a single CSV file"""
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                # Try semicolon delimiter first (OBP standard)
                content = f.read()
                f.seek(0)
                
                delimiter = ';' if ';' in content else ','
                reader = csv.reader(f, delimiter=delimiter)
                rows = list(reader)
                
            if not rows:
                return None
                
            # Basic stats
            stats = {
                'total_entries': len(rows),
                'delimiter': delimiter,
                'columns': len(rows[0]) if rows else 0,
                'has_header': False,
                'sample_entries': [row[0] for row in rows[:5] if row],
                'categories': collections.Counter()
            }
            
            # Check for gender column (common in OBP)
            if stats['columns'] >= 2:
                gender_values = [row[1].lower() for row in rows if len(row) >= 2]
                if any(g in ['male', 'female', 'both', 'genderless'] for g in gender_values):
                    stats['has_gender_column'] = True
                    stats['gender_distribution'] = dict(collections.Counter(gender_values))
                else:
                    stats['has_gender_column'] = False
                    
            # Check for category columns (like artists_and_category.csv)
            if stats['columns'] > 3:
                stats['multi_column'] = True
                stats['column_count'] = stats['columns']
                
            # Analyze content patterns
            all_text = ' '.join([row[0].lower() for row in rows if row])
            
            # Categorize by keywords
            categories = {
                'fantasy': ['dragon', 'magic', 'fantasy', 'medieval', 'wizard', 'elf'],
                'sci-fi': ['cyber', 'robot', 'space', 'future', 'tech', 'sci-fi'],
                'portrait': ['portrait', 'face', 'person', 'character', 'human'],
                'landscape': ['landscape', 'scenery', 'nature', 'mountain', 'forest'],
                'abstract': ['abstract', 'surreal', 'conceptual'],
                'realistic': ['photo', 'realistic', 'real', 'photograph'],
                'artistic': ['painting', 'art', 'artistic', 'style', 'artist']
            }
            
            for category, keywords in categories.items():
                count = sum(1 for row in rows if row and any(kw in row[0].lower() for kw in keywords))
                if count > 0:
                    stats['categories'][category] = count
                    
            return stats
            
        except Exception as e:
            return {'error': str(e)}
            
    def analyze_all_csvs(self):
        """Analyze all CSV files in the csvfiles directory"""
        
        print(f"\n{'='*60}")
        print("ANALYZING CSV FILE ARCHITECTURE")
        print(f"{'='*60}\n")
        
        if not self.csvfiles_dir.exists():
            print(f"✗ Directory not found: {self.csvfiles_dir}")
            return
            
        # Get all CSV files
        csv_files = list(self.csvfiles_dir.glob("*.csv"))
        csv_files.extend(self.csvfiles_dir.glob("**/*.csv"))
        
        print(f"Found {len(csv_files)} CSV files\n")
        
        # Analyze each file
        for csv_file in sorted(csv_files):
            relative_path = csv_file.relative_to(self.csvfiles_dir.parent)
            stats = self.analyze_csv_file(csv_file)
            
            if stats and 'error' not in stats:
                self.analysis[str(relative_path)] = stats
                
        print(f"✓ Analyzed {len(self.analysis)} CSV files successfully\n")
        
    def generate_architecture_report(self):
        """Generate comprehensive architecture report"""
        
        if not self.analysis:
            print("No analysis data available!")
            return
            
        print(f"\n{'='*60}")
        print("CSV ARCHITECTURE REPORT")
        print(f"{'='*60}\n")
        
        # Overall statistics
        total_entries = sum(stats['total_entries'] for stats in self.analysis.values())
        print(f"Total entries across all CSVs: {total_entries:,}\n")
        
        # Categorize files by size
        print(f"{'='*60}")
        print("FILES BY SIZE")
        print(f"{'='*60}")
        
        size_categories = {
            'Very Large (>1000)': [],
            'Large (500-1000)': [],
            'Medium (100-500)': [],
            'Small (10-100)': [],
            'Tiny (<10)': []
        }
        
        for filepath, stats in self.analysis.items():
            count = stats['total_entries']
            filename = Path(filepath).name
            
            if count > 1000:
                size_categories['Very Large (>1000)'].append((filename, count))
            elif count > 500:
                size_categories['Large (500-1000)'].append((filename, count))
            elif count > 100:
                size_categories['Medium (100-500)'].append((filename, count))
            elif count > 10:
                size_categories['Small (10-100)'].append((filename, count))
            else:
                size_categories['Tiny (<10)'].append((filename, count))
                
        for category, files in size_categories.items():
            if files:
                print(f"\n{category}:")
                for filename, count in sorted(files, key=lambda x: x[1], reverse=True):
                    print(f"  {count:5d} - {filename}")
                    
        # Files with gender support
        print(f"\n{'='*60}")
        print("FILES WITH GENDER COLUMN")
        print(f"{'='*60}")
        
        gender_files = [
            (filepath, stats) for filepath, stats in self.analysis.items()
            if stats.get('has_gender_column', False)
        ]
        
        if gender_files:
            for filepath, stats in gender_files:
                filename = Path(filepath).name
                print(f"\n{filename} ({stats['total_entries']} entries)")
                if 'gender_distribution' in stats:
                    for gender, count in stats['gender_distribution'].items():
                        percentage = (count / stats['total_entries']) * 100
                        print(f"  {gender:12s}: {percentage:5.1f}% ({count})")
        else:
            print("No files with gender column detected")
            
        # Multi-column files (complex structure)
        print(f"\n{'='*60}")
        print("MULTI-COLUMN FILES (Complex Structure)")
        print(f"{'='*60}")
        
        multi_col_files = [
            (filepath, stats) for filepath, stats in self.analysis.items()
            if stats.get('multi_column', False)
        ]
        
        if multi_col_files:
            for filepath, stats in multi_col_files:
                filename = Path(filepath).name
                print(f"  {filename:40s} - {stats['column_count']} columns, {stats['total_entries']} entries")
        else:
            print("No multi-column files detected")
            
        # Content categorization
        print(f"\n{'='*60}")
        print("CONTENT CATEGORIZATION")
        print(f"{'='*60}")
        
        # Aggregate categories across all files
        all_categories = collections.Counter()
        for stats in self.analysis.values():
            all_categories.update(stats.get('categories', {}))
            
        if all_categories:
            print("\nTotal entries by detected category:")
            for category, count in all_categories.most_common():
                print(f"  {category:12s}: {count:5d} entries")
        else:
            print("No categories detected")
            
        # Identify key files
        print(f"\n{'='*60}")
        print("KEY FILES FOR EXPANSION")
        print(f"{'='*60}\n")
        
        key_files = {
            'artists': 'Core artist database',
            'descriptors': 'General descriptors',
            'humandescriptors': 'Human-specific descriptors',
            'objects': 'Object subjects',
            'animals': 'Animal subjects',
            'humanoids': 'Humanoid subjects',
            'locations': 'Location/background settings',
            'imagetypes': 'Image type definitions',
            'artmovements': 'Art movement styles',
            'quality': 'Quality descriptors',
            'colors': 'Color definitions',
            'lighting': 'Lighting terms'
        }
        
        for key_file, description in key_files.items():
            matching = [
                (filepath, stats) for filepath, stats in self.analysis.items()
                if key_file in Path(filepath).stem
            ]
            
            if matching:
                for filepath, stats in matching:
                    filename = Path(filepath).name
                    print(f"{filename:30s} - {stats['total_entries']:5d} entries - {description}")
            else:
                print(f"{key_file + '.csv':30s} - NOT FOUND - {description}")
                
    def identify_expansion_opportunities(self):
        """Identify specific opportunities for CSV expansion"""
        
        print(f"\n{'='*60}")
        print("EXPANSION OPPORTUNITIES")
        print(f"{'='*60}\n")
        
        opportunities = []
        
        # Find small files that could be expanded
        small_files = [
            (filepath, stats) for filepath, stats in self.analysis.items()
            if 10 < stats['total_entries'] < 100
        ]
        
        if small_files:
            opportunities.append({
                'priority': 'MEDIUM',
                'category': 'Small Files',
                'files': [Path(f[0]).name for f in small_files[:5]],
                'action': 'Consider expanding these files to 100+ entries for more variety'
            })
            
        # Find files without gender support that might benefit
        no_gender = [
            (filepath, stats) for filepath, stats in self.analysis.items()
            if not stats.get('has_gender_column', False) 
            and stats['total_entries'] > 50
            and any(keyword in Path(filepath).stem for keyword in ['human', 'character', 'job', 'outfit'])
        ]
        
        if no_gender:
            opportunities.append({
                'priority': 'LOW',
                'category': 'Gender Support',
                'files': [Path(f[0]).name for f in no_gender[:5]],
                'action': 'Consider adding gender column for better filtering'
            })
            
        # Check for missing addon/replace files
        print("USER CUSTOMIZATION STATUS:")
        print()
        
        if self.userfiles_dir.exists():
            user_files = list(self.userfiles_dir.glob("*.csv"))
            print(f"  Found {len(user_files)} user customization files")
            
            for user_file in user_files:
                if '_addon' in user_file.stem or '_replace' in user_file.stem:
                    print(f"    ✓ {user_file.name}")
        else:
            print(f"  ✗ User files directory not found: {self.userfiles_dir}")
            
        # Print opportunities
        print(f"\nIDENTIFIED OPPORTUNITIES:\n")
        
        for opp in opportunities:
            print(f"[{opp['priority']}] {opp['category']}")
            print(f"  Files: {', '.join(opp['files'][:3])}{'...' if len(opp['files']) > 3 else ''}")
            print(f"  Action: {opp['action']}")
            print()
            
    def save_analysis(self, filename="csv_architecture_analysis.json"):
        """Save analysis to JSON file"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.analysis, f, indent=2, ensure_ascii=False)
            
        print(f"\n✓ Architecture analysis saved to {filename}")


def main():
    """Main execution function"""
    
    print("OneButtonPrompt CSV Architecture Analyzer")
    print("=" * 60)
    
    # Create analyzer
    analyzer = CSVArchitectureAnalyzer()
    
    # Run analysis
    analyzer.analyze_all_csvs()
    
    # Generate reports
    analyzer.generate_architecture_report()
    analyzer.identify_expansion_opportunities()
    
    # Save results
    analyzer.save_analysis()
    
    print(f"\n{'='*60}")
    print("Architecture analysis complete!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
