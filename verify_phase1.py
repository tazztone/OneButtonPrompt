
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.abspath('.'))

try:
    from build_dynamic_prompt_minimal import build_dynamic_prompt
    print("✓ Successfully imported build_dynamic_prompt (minimal version)")
    
    # Run a few generations forcing a special mode to check generationmode tracking
    for mode in ["art blaster mode", "quality vomit mode", "massive madness mode"]:
        result = build_dynamic_prompt(insanitylevel=5, imagetype=mode, _return_metadata=True)
        prompt, metadata = result[0], result[-1]
        
        print(f"\nMode Test: {mode}")
        print(f"Metadata Generation Mode: {metadata.get('generationmode')}")
        print(f"Tracked Attributes: {metadata.keys()}")
    
    print("\n✓ Verification successful!")
except Exception as e:
    print(f"✗ Verification failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
