# How It Works

OneButtonPrompt builds prompts by randomly selecting keywords from 130+ CSV files (3,500+ artists, subjects, styles, descriptors) and combining them with comma separators. The "insanity level" (1-10) controls selection probability:

- **Level 1**: 20% chance per optional element → simple prompts (5-10 keywords)
- **Level 5**: 50% chance per optional element → balanced (10-20 keywords)  
- **Level 10**: 100% chance for most elements → complex (20-40 keywords)

**Generation Process:**
1. Pick subject type (object/animal/humanoid/landscape/concept)
2. Roll dice for each optional element based on insanity level
3. Concatenate selected keywords with commas
4. Add model-specific formatting:
   - **SD1.5/Anime**: Keywords only (`portrait, woman, red hair`)
   - **SDXL**: Inserts filler words (`portrait, the woman is red haired`)
   - **Stable Cascade**: Strips weight syntax `(keyword:1.2)` → `keyword`

**Example at insanity 5:**
```
Subject: "Warrior" (always included)
Artist: "Frank Frazetta" (27% chance) ✓ added
Art movement: "Fantasy Art" (16% chance) ✓ added  
Lighting: "dramatic lighting" (50% chance) ✓ added
Camera angle: "wide shot" (16% chance) ✗ skipped

Result: "by Frank Frazetta, fantasy art, fierce Warrior, dramatic lighting, detailed"
```

Filler words for SDXL are hardcoded patterns like `"the [subject] is [descriptor]"` or `"[descriptor] and [descriptor]"` inserted between keywords when `less_verbose=False`.
