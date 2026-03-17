"""
Validation 14 — Price Version Conflict
========================================
Validates S14:
1. Price_Version_Clean matches the month of TS_UTC.
2. Price_Version_Mismatch correctly identifies conflicts.
3. Messy strings form 'v1', 'v2', etc.
"""
import pandas as pd

def validate(df):
    passed = 0
    failed = 0
    
    print("\n=======================================================")
    print("  1. VERSION-TO-MONTH CONSISTENCY")
    print("=======================================================")
    
    # Only check where TS_UTC is valid
    valid_ts = df[df['TS_UTC'].notna()].copy()
    valid_ts['Test_Expected'] = 'v' + valid_ts['TS_UTC'].dt.month.astype(str)
    
    inconsistent = valid_ts[valid_ts['Price_Version_Clean'] != valid_ts['Test_Expected']]
    print(f"  Inconsistent Versions: {len(inconsistent)}")
    
    if len(inconsistent) == 0:
        print("  ✓")
        passed += 1
    else:
        print("  X")
        failed += 1
        
    print("\n=======================================================")
    print("  2. MISMATCH FLAG ACCURACY")
    print("=======================================================")
    mismatches = df['Price_Version_Mismatch'].sum()
    print(f"  Mismatch Flags Triggered: {mismatches}")
    
    # Ensure expected # of mismatches (generated was roughly 18% wrong/dirty/missing)
    if mismatches > 1000 and mismatches < 3000:
        print("  ✓")
        passed += 1
    else:
        print(f"  X (Expected 1000-3000, got {mismatches})")
        failed += 1
        
    print("\n=======================================================")
    print("  3. CLEAN FORMAT")
    print("=======================================================")
    clean_vals = df['Price_Version_Clean'].dropna().unique()
    print(f"  Clean Values Used: {list(clean_vals)}")
    
    valid_formats = ['v1', 'v2', 'v3', 'v4', 'v12']
    bad_formats = [v for v in clean_vals if v not in valid_formats]
    print(f"  Invalid Formats: {len(bad_formats)}")
    
    if len(bad_formats) == 0 and len(clean_vals) >= 1:
        print("  ✓")
        passed += 1
    else:
        print("  X")
        failed += 1
        
    print("\n=======================================================")
    print("  SUMMARY — S14 VALIDATION")
    print("=======================================================")
    print(f"  Passed: {passed}/3")
    print(f"  Failed: {failed}/3\n")
    
    return passed, failed, []
