"""
Validation 15 — FX Rate Normalization
=======================================
Validates S15:
1. FX_Rate_Clean is present and correct for all currencies.
2. Cost_USD is correctly calculated (Cost_Clean * FX_Rate_Clean).
3. Missing FX rates were successfully imputed.
"""
import pandas as pd
import numpy as np

# Canonical rates for cross-validation
CANONICAL_FX = {
    'USD': 1.00,
    'INR': 0.012,
    'EUR': 1.08,
    'GBP': 1.27
}

def validate(df):
    passed = 0
    failed = 0
    
    print("\n=======================================================")
    print("  1. FX RATE COMPLETENESS")
    print("=======================================================")
    null_fx = df['FX_Rate_Clean'].isna().sum()
    print(f"  Null FX Rates Output: {null_fx}")
    
    if null_fx == 0:
        print("  ✓")
        passed += 1
    else:
        print("  X")
        failed += 1
        
    print("\n=======================================================")
    print("  2. CANONICAL RATE CONSISTENCY")
    print("=======================================================")
    
    inconsistent_fx = 0
    for currency, expected_rate in CANONICAL_FX.items():
        subset = df[df['Currency_Clean'] == currency]
        if len(subset) > 0:
            deviations = sum(~np.isclose(subset['FX_Rate_Clean'], expected_rate, atol=1e-4))
            inconsistent_fx += deviations
            
    print(f"  Inconsistent Rates found: {inconsistent_fx}")
    
    if inconsistent_fx == 0:
        print("  ✓")
        passed += 1
    else:
        print("  X")
        failed += 1
        
    print("\n=======================================================")
    print("  3. COST_USD CALCULATION")
    print("=======================================================")
    calc_errors = sum(~np.isclose(df['Cost_USD'], df['Cost_Clean'] * df['FX_Rate_Clean'], atol=1e-2))
    print(f"  Rows with Cost_USD calc math errors: {calc_errors}")
    
    if calc_errors == 0:
        print("  ✓")
        passed += 1
    else:
        print("  X")
        failed += 1
        
    print("\n=======================================================")
    print("  SUMMARY — S15 VALIDATION")
    print("=======================================================")
    print(f"  Passed: {passed}/3")
    print(f"  Failed: {failed}/3\n")
    
    return passed, failed, []
