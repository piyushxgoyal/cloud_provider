"""
Validation 20 — Log Time Skew Normalization
=============================================
Validates S20:
1. Log_Skew_Clean contains no nulls and is numeric.
2. Is_High_Skew accurately tags |skew| > 60.
"""

import pandas as pd

def validate(df):
    if 'Log_Skew_Clean' not in df.columns:
        print("Log_Skew_Clean column missing, skipping validation.")
        return 0, 2, []
        
    passed = 0
    failed = 0
    
    print("\n=======================================================")
    print("  1. COMPLETENESS & TYPE")
    print("=======================================================")
    nulls = df['Log_Skew_Clean'].isna().sum()
    is_numeric = pd.api.types.is_numeric_dtype(df['Log_Skew_Clean'])
    
    print(f"  Null Log Skews: {nulls}")
    print(f"  Is Numeric:     {is_numeric}")
    
    if nulls == 0 and is_numeric:
        print("  ✓")
        passed += 1
    else:
        print("  X")
        failed += 1
        
    print("\n=======================================================")
    print("  2. SKEW FLAG ACCURACY")
    print("=======================================================")
    # Recalculate manually
    expected_high = df['Log_Skew_Clean'].abs() > 60.0
    errors = (df['Is_High_Skew'] != expected_high).sum()
    
    print(f"  Flag Calculation Errors: {errors}")
    
    if errors == 0:
        print("  ✓")
        passed += 1
    else:
        print("  X")
        failed += 1
        
    print("\n=======================================================")
    print("  SUMMARY — S20 VALIDATION")
    print("=======================================================")
    print(f"  Passed: {passed}/2")
    print(f"  Failed: {failed}/2\n")
    
    return passed, failed, []
