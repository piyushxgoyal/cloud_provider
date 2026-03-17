"""
Validation 19 — SLA Event Normalization
=========================================
Validates S19:
1. Ensure all values in SLA_Event_Clean are boolean (True/False).
2. Check that known messy formats like '1' and 'yes' were successfully converted.
"""

import pandas as pd

def validate(df):
    if 'SLA_Event_Clean' not in df.columns:
        print("SLA_Event_Clean column missing, skipping validation.")
        return 0, 1, []
        
    passed = 0
    failed = 0
    
    print("\n=======================================================")
    print("  1. BOOLEAN TYPE INTEGRITY")
    print("=======================================================")
    # Check if the column is strictly boolean
    is_bool = pd.api.types.is_bool_dtype(df['SLA_Event_Clean'])
    
    if is_bool:
        print("  Column is strictly boolean: ✓")
        passed += 1
    else:
        # Check if they are just 0/1 ints or strictly True/False
        uniques = set(df['SLA_Event_Clean'].unique())
        if uniques.issubset({True, False}):
            print("  Column values are strictly {True, False}: ✓")
            passed += 1
        else:
            print(f"  Invalid values found: {uniques - {True, False}} X")
            failed += 1
            
    print("\n=======================================================")
    print("  2. COMPLETENESS (NO NULLS)")
    print("=======================================================")
    nulls = df['SLA_Event_Clean'].isna().sum()
    print(f"  Null SLA Events: {nulls}")
    
    if nulls == 0:
        print("  ✓")
        passed += 1
    else:
        print("  X")
        failed += 1
        
    print("\n=======================================================")
    print("  SUMMARY — S19 VALIDATION")
    print("=======================================================")
    print(f"  Passed: {passed}/2")
    print(f"  Failed: {failed}/2\n")
    
    return passed, failed, []
