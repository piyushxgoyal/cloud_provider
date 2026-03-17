"""
Validation 13 — Incident Normalization
========================================
Validates S13:
1. Incident Start/End timestamps are UTC datetime64.
2. SLA_Breach is strictly boolean.
"""
import pandas as pd

def validate(df):
    passed = 0
    failed = 0
    
    print("\n=======================================================")
    print("  1. TIMESTAMP NORMALIZATION")
    print("=======================================================")
    
    valid_starts = df['Incident_Start_UTC'].notna().sum()
    valid_ends = df['Incident_End_UTC'].notna().sum()
    start_type = df['Incident_Start_UTC'].dtype
    end_type = df['Incident_End_UTC'].dtype
    print(f"  Valid starts: {valid_starts}")
    print(f"  Valid ends:   {valid_ends}")
    print(f"  Start dtype:  {start_type}")
    print(f"  End dtype:    {end_type}")
    
    if valid_starts > 0 and 'datetime64[us, UTC]' in str(start_type) and 'datetime64[us, UTC]' in str(end_type):
        print("  ✓")
        passed += 1
    else:
        print("  X")
        failed += 1
        
    print("\n=======================================================")
    print("  2. SLA BREACH BOOLEAN")
    print("=======================================================")
    sla_nulls = df['SLA_Breach_Clean'].isna().sum()
    print(f"  SLA Nulls: {sla_nulls}")
    
    boolean_values = df['SLA_Breach_Clean'].dropna().apply(type).unique()
    print(f"  Types found: {[t.__name__ for t in boolean_values]}")
    if len(boolean_values) == 1 and bool in boolean_values:
        print("  ✓")
        passed += 1
    else:
        print("  X")
        failed += 1
        
    print("\n=======================================================")
    print("  3. INCIDENT DURATION SANITY")
    print("=======================================================")
    df['Duration'] = df['Incident_End_UTC'] - df['Incident_Start_UTC']
    negative_duration = (df['Duration'].dt.total_seconds() < 0).sum()
    print(f"  Incidents ending before starting: {negative_duration}")
    if negative_duration == 0:
        print("  ✓")
        passed += 1
    else:
        print("  X")
        failed += 1
        
    print("\n=======================================================")
    print("  SUMMARY — S13 VALIDATION")
    print("=======================================================")
    print(f"  Passed: {passed}/3")
    print(f"  Failed: {failed}/3\n")
    return passed, failed, []
