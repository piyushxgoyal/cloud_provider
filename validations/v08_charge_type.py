"""
Validation 08 — Charge Type Validation
=======================================
Validates the output of S08 (Charge Type Normalization).
Checks: canonical mapping completeness, contradiction correctness, coverage.
"""

import pandas as pd


def validate(df):
    """
    Run all validation checks for S08.
    
    Returns:
        (passed, failed, results) tuple
    """
    sep = "=" * 55
    results = {}
    
    # ── 1. Canonical Mapping Completeness ─────────────────────
    print(f"\n{sep}")
    print("  1. CANONICAL CHARGE TYPES")
    print(sep)
    
    valid_types = {'Usage', 'Free_Tier', 'Credit', 'Refund', 'Unknown'}
    bad_types = df[~df['Charge_Type_Clean'].isin(valid_types)]
    
    print(f"  Invalid charge types found: {len(bad_types)}")
    print(f"  Distribution: {df['Charge_Type_Clean'].value_counts().to_dict()}")
    
    results['All types canonical'] = len(bad_types) == 0
    _status(results, 'All types canonical')
    
    # ── 2. Unknown Rate ───────────────────────────────────────
    print(f"\n{sep}")
    print("  2. UNKNOWN RATE")
    print(sep)
    
    unknowns = (df['Charge_Type_Clean'] == 'Unknown').sum()
    print(f"  Rows mapped to Unknown: {unknowns}")
    
    # Expect 0 unknowns based on generator, but allow small < 1% buffer
    results['Unknown rate < 1%'] = unknowns / len(df) < 0.01
    _status(results, 'Unknown rate < 1%')
    
    # ── 3. Spot-check mapping ─────────────────────────────────
    print(f"\n{sep}")
    print("  3. SPOT-CHECK MAPPING")
    print(sep)
    
    from scenarios.s08_charge_type import clean_charge_type
    
    tests = [
        ('billable', 'Usage'),
        ('TRUE', 'Usage'),
        ('free', 'Free_Tier'),
        ('FREE_TIER', 'Free_Tier'),
        ('refund', 'Refund'),
        ('CREDIT', 'Credit'),
    ]
    
    all_ok = True
    for dirty, expected in tests:
        res = clean_charge_type(dirty)
        ok = res == expected
        sym = "✓" if ok else "✗"
        if not ok: all_ok = False
        print(f"  {sym}  {dirty!r:15s} → {res!r:10s}  (expected {expected!r})")
        
    results['All spot-checks pass'] = all_ok
    _status(results, 'All spot-checks pass')
    
    # ── 4. Contradiction Flag Verification ────────────────────
    print(f"\n{sep}")
    print("  4. CONTRADICTION ACCURACY")
    print(sep)
    
    contra = df['Charge_Cost_Contradiction'].sum()
    actually_contra = ((df['Charge_Type_Clean'] == 'Free_Tier') & (df['Cost_Clean'] > 0.01)).sum()
    
    print(f"  Flagged contradictions: {contra}")
    print(f"  Actual Free_Tier w/ Cost: {actually_contra}")
    
    results['Contradiction flags matched'] = contra == actually_contra
    _status(results, 'Contradiction flags matched')
    results['Detected ~1600 anomalies'] = 1400 <= contra <= 1900
    _status(results, 'Detected ~1600 anomalies')
    
    # ── Summary ───────────────────────────────────────────────
    print(f"\n{sep}")
    print("  SUMMARY — S08 VALIDATION")
    print(sep)
    
    passed = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if not v)
    
    for check, ok in results.items():
        sym = "✅ PASS" if ok else "❌ FAIL"
        print(f"  {sym}  {check}")
    
    print(f"\n  Passed: {passed}/{len(results)}")
    print(f"  Failed: {failed}/{len(results)}")
    
    return passed, failed, results


def _status(results, key):
    sym = "✓" if results[key] else "✗ FAIL"
    print(f"  {sym}")

if __name__ == '__main__':
    import sys
    sys.path.insert(0, '.')
    from scenarios.s05_cost import run as s05_run
    from scenarios.s08_charge_type import run as s08_run
    
    billing = pd.read_csv('data/raw/usage_billing.csv')
    billing = s05_run(billing)
    billing = s08_run(billing)
    validate(billing)
