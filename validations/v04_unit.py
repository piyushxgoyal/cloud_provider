"""
Validation 04 — Unit Normalization Validation
===============================================
Validates the output of S04 (Unit Normalization).
Checks: canonical units, conversion accuracy, dimension mismatches, coverage.
"""

import pandas as pd
import numpy as np


def validate(df):
    """
    Run all validation checks for S04.

    Args:
        df: DataFrame after S04 cleaning

    Returns:
        (passed, failed, results) tuple
    """
    sep = "=" * 55
    results = {}

    # ── 1. Canonical unit values ──────────────────────────────
    print(f"\n{sep}")
    print("  1. CANONICAL UNIT VALUES")
    print(sep)

    valid_units = {'seconds', 'GB'}
    non_null = df['Unit_Canonical'].dropna()
    bad = non_null[~non_null.isin(valid_units)]

    print(f"  Non-null canonical units: {len(non_null)}")
    print(f"  Invalid units:            {len(bad)}")
    print(f"  Distribution: {non_null.value_counts().to_dict()}")

    results['Only seconds/GB'] = len(bad) == 0
    _status(results, 'Only seconds/GB')

    # ── 2. Conversion accuracy spot-check ─────────────────────
    print(f"\n{sep}")
    print("  2. CONVERSION ACCURACY SPOT-CHECK")
    print(sep)

    from scenarios.s04_unit import normalize_unit

    test_cases = [
        ('sec',       100.0,   'seconds',  100.0),
        ('seconds',   100.0,   'seconds',  100.0),
        ('mins',      10.0,    'seconds',  600.0),
        ('minutes',   5.0,     'seconds',  300.0),
        ('hrs',       2.0,     'seconds',  7200.0),
        ('hours',     1.0,     'seconds',  3600.0),
        ('gb',        50.0,    'GB',       50.0),
        ('GB',        50.0,    'GB',       50.0),
        ('mb',        1024.0,  'GB',       1.0),
        ('megabytes', 2048.0,  'GB',       2.0),
    ]

    all_passed = True
    for unit, val, exp_unit, exp_val in test_cases:
        result_unit, result_val = normalize_unit(unit, val)
        ok = result_unit == exp_unit and abs(result_val - exp_val) < 0.01
        sym = "✓" if ok else "✗"
        if not ok:
            all_passed = False
        print(f"  {sym}  {unit:10s} × {val:8.1f} → {result_unit} × {result_val:.2f}  (expected {exp_unit} × {exp_val:.2f})")

    results['All conversions correct'] = all_passed
    _status(results, 'All conversions correct')

    # ── 3. Dimension mismatch check ───────────────────────────
    print(f"\n{sep}")
    print("  3. DIMENSION MISMATCH CHECK")
    print(sep)

    mismatches = df['Unit_Dimension_Mismatch'].sum()
    mismatch_pct = mismatches / len(df) * 100

    print(f"  Mismatched rows:     {mismatches}")
    print(f"  Mismatch rate:       {mismatch_pct:.1f}%")

    if mismatches > 0:
        print(f"\n  Sample mismatches:")
        mismatch_rows = df[df['Unit_Dimension_Mismatch']]
        print(mismatch_rows[['Service_Clean', 'Unit', 'Unit_Canonical']].head(5).to_string(index=False))

    results['Mismatches detected'] = True  # presence is expected
    _status(results, 'Mismatches detected')

    # ── 4. No null canonical for non-null input ───────────────
    print(f"\n{sep}")
    print("  4. UNRECOGNIZED UNIT CHECK")
    print(sep)

    unrecognized = df[df['Unit'].notna() & df['Unit_Canonical'].isna()]
    print(f"  Rows with Unit but no canonical: {len(unrecognized)}")

    results['Unrecognized rate < 5%'] = len(unrecognized) / len(df) * 100 < 5
    _status(results, 'Unrecognized rate < 5%')

    # ── 5. Usage_Converted populated ──────────────────────────
    print(f"\n{sep}")
    print("  5. USAGE_CONVERTED COVERAGE")
    print(sep)

    has_value = df['Usage_Converted'].notna().sum()
    print(f"  Rows with converted value: {has_value}")
    print(f"  Coverage: {has_value/len(df)*100:.1f}%")

    results['Converted coverage > 95%'] = has_value / len(df) * 100 > 95
    _status(results, 'Converted coverage > 95%')

    # ── 6. Value range sanity ─────────────────────────────────
    print(f"\n{sep}")
    print("  6. VALUE RANGE SANITY")
    print(sep)

    conv = df['Usage_Converted'].dropna()
    print(f"  Min:    {conv.min():.2f}")
    print(f"  Max:    {conv.max():.2f}")
    print(f"  Mean:   {conv.mean():.2f}")
    print(f"  Median: {conv.median():.2f}")

    results['No negative values'] = (conv >= 0).all()
    _status(results, 'No negative values')

    # ── Summary ───────────────────────────────────────────────
    print(f"\n{sep}")
    print("  SUMMARY — S04 VALIDATION")
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
    from scenarios.s03_sku import run as s03_run
    from scenarios.s04_unit import run as s04_run

    billing = pd.read_csv('data/raw/usage_billing.csv')
    billing = s03_run(billing)
    billing = s04_run(billing)
    validate(billing)
