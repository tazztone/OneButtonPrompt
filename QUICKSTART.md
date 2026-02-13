# Quick Start Guide - OBP Analysis & Improvement

## 3-Step Process to Reduce Repetition

### Step 1: Run Analysis (3 minutes)

```bash
python3 run_full_analysis.py
```

This will:
- Analyze your CSV files
- Generate 1000 test prompts
- Identify repetition patterns
- Create recommendations

**Output files:**
- `csv_architecture_analysis.json`
- `obp_analysis_results.json`
- Console report with recommendations

### Step 2: Create Addon Files (5 minutes)

```bash
python3 create_addon_template.py
```

This creates template files in `userfiles/`:
- `artists_addon_template.csv` - 50 alternative artists
- `descriptors_addon_template.csv` - 40 distinctive descriptors
- `concepts_addon_template.csv` - 40 abstract concepts

**Edit and activate:**
1. Open template files
2. Review/modify entries
3. Rename (remove `_template` suffix)
4. Files are now active!

### Step 3: Verify Improvement (3 minutes)

```bash
python3 run_full_analysis.py
```

Compare results:
- Artist repetition should decrease
- Subject balance should improve
- Overall variety should increase

## Expected Results

### Before Expansion
```
TOP ARTISTS:
  5.2% - Greg Rutkowski (52 times)
  3.8% - Artgerm (38 times)
  2.9% - Charlie Bowater (29 times)
```

### After Expansion
```
TOP ARTISTS:
  1.8% - Greg Rutkowski (18 times)
  1.5% - Karla Ortiz (15 times)
  1.3% - Artgerm (13 times)
```

**Result:** 3x reduction in repetition!

## Troubleshooting

### "Error importing OBP modules"
Make sure you're in the OneButtonPrompt directory:
```bash
cd /path/to/OneButtonPrompt
ls build_dynamic_prompt.py  # Should exist
```

### "Analysis takes too long"
Edit `run_full_analysis.py` and reduce iterations:
```python
NUM_ITERATIONS = 100  # Quick test
```

### "No improvements after adding files"
1. Check file names (must be exact: `artists_addon.csv`)
2. Verify file format (semicolon or comma separated)
3. Check for syntax errors in CSV
4. Restart ComfyUI if using custom nodes

## What Each File Does

| File | Purpose | Run Time |
|------|---------|----------|
| `run_full_analysis.py` | Complete analysis suite | 3-4 min |
| `analyze_csv_architecture.py` | CSV structure analysis | 5 sec |
| `analyze_obp_generations.py` | Generation patterns | 2-3 min |
| `create_addon_template.py` | Create addon templates | Instant |

## Customization

### Test Different Insanity Levels

Edit `run_full_analysis.py`:
```python
INSANITY_LEVEL = 7  # Test higher chaos
```

### Test Specific Artist Categories

Edit `analyze_obp_generations.py`:
```python
analyzer.run_analysis(
    num_iterations=1000,
    insanitylevel=5,
    artists="fantasy"  # Test specific category
)
```

### Add More Iterations for Accuracy

```python
NUM_ITERATIONS = 5000  # More accurate (15-20 min)
```

## Best Practices

1. ✅ Run analysis BEFORE making changes (baseline)
2. ✅ Focus on HIGH impact items first
3. ✅ Add distinctive alternatives (not near-duplicates)
4. ✅ Test with actual image generation
5. ✅ Re-run analysis to verify improvements

## Common Mistakes

❌ Adding 1000 random entries
✅ Adding 50 strategic alternatives to overused items

❌ Modifying core CSV files directly
✅ Using addon files in userfiles/

❌ Adding similar/duplicate entries
✅ Adding visually distinctive alternatives

❌ Ignoring analysis recommendations
✅ Following data-driven insights

## Next Steps

After improving variety:

1. **Add tooltips to ComfyUI nodes** (separate PR)
   - Improve user experience
   - Explain parameters clearly
   - Provide practical guidance

2. **Share your addon files** (optional)
   - Help the community
   - Contribute to OBP repository
   - Get feedback on additions

3. **Monitor long-term patterns**
   - Run analysis monthly
   - Track variety metrics
   - Adjust as needed

## Questions?

- Check `ANALYSIS_README.md` for detailed docs
- Review `ANALYSIS_SUMMARY.md` for overview
- Read `AGENTS.md` for architecture details
- Open an issue with analysis results

---

**Time Investment:** ~15 minutes total
**Expected Improvement:** 3-5x reduction in repetition
**Maintenance:** Re-analyze monthly or after major changes
