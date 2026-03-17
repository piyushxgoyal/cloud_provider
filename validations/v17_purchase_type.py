"""
Validation 17 — Purchase Type Normalization
=============================================
Validates S17:
1. Purchase_Type_Clean contains only allowed canonical values.
2. Missing or messy types are successfully standardized.
"""

import pandas as pd

def validate(df):
    passed = 0
    failed = 0
    
    print("\n=======================================================")
    print("  1. ALLOWED CANONICAL VALUES")
    print("=======================================================")
    valid_types = {'on-demand', 'reserved', 'spot'}
    found_types = set(df['Purchase_Type_Clean'].dropna().unique())
    
    invalid_found = found_types - valid_types
    print(f"  Types found: {found_types}")
    print(f"  Invalid types: {invalid_found}")
    
    if len(invalid_found) == 0:
        print("  ✓")
        passed += 1
    else:
        print("  X")
        failed += 1
        
    print("\n=======================================================")
    print("  2. COMPLETENESS (NO NULLS)")
    print("=======================================================")
    nulls = df['Purchase_Type_Clean'].isna().sum()
    print(f"  Null Purchase Types: {nulls}")
    
    if nulls == 0:
        print("  ✓")
        passed += 1
    else:
        print("  X")
        failed += 1
        
    print("\n=======================================================")
    print("  SUMMARY — S17 VALIDATION")
    print("=======================================================")
    print(f"  Passed: {passed}/2")
    print(f"  Failed: {failed}/2\n")
    
    return passed, failed, []
