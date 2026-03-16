"""
Validation 05 — Cost Cleaning Validation
==========================================
Validates the output of S05 (Cost & Currency Cleaning).
Checks: numeric conversion, currency canonical, negative/zero flags, coverage, spot-checks.
"""

import pandas as pd
import numpy as np


def validate(df):
    """
    Run all validation checks for S05.

    Returns:
        (passed, failed, results) tuple
    """
    sep = "=" * 55
    results = {}

    # ── 1. Cost_Clean is numeric ──────────────────────────────
    print(f"\n{sep}")
    print("  1. COST_CLEAN NUMERIC CHECK")
    print(sep)

    non_null = df['Cost_Clean'].dropna()
    print(f"  Non-null Cost_Clean:  {len(non_null)}")
    print(f"  Null Cost_Clean:      {df['Cost_Clean'].isna().sum()}")
    print(f"  dtype:                {df['Cost_Clean'].dtype}")

    results['Cost_Clean is float'] = df['Cost_Clean'].dtype in ('float64', 'float32')
    _status(results, 'Cost_Clean is float')

    # ── 2. Currency canonical ─────────────────────────────────
    print(f"\n{sep}")
    print("  2. CURRENCY CANONICAL CHECK")
    print(sep)

    valid_currencies = {'INR', 'USD', 'EUR', 'GBP', 'UNKNOWN'}
    bad_currency = df[~df['Currency_Clean'].isin(valid_currencies)]

    print(f"  Invalid currencies:   {len(bad_currency)}")
    print(f"  Distribution:         {df['Currency_Clean'].value_counts().to_dict()}")

    results['All currencies canonical'] = len(bad_currency) == 0
    _status(results, 'All currencies canonical')

    # ── 3. Spot-check: symbol stripping ───────────────────────
    print(f"\n{sep}")
    print("  3. SYMBOL STRIPPING SPOT-CHECK")
    print(sep)

    from scenarios.s05_cost import clean_cost, clean_currency

    cost_tests = [
        ('₹1,200.50', 1200.50),
        ('$500.00',    500.00),
        ('€2,000.00',  2000.00),
        ('£100.00',    100.00),
        ('1,200.50',   1200.50),
        ('-500.00',    -500.00),
        ('0',          0.0),
    ]

    all_ok = True
    for dirty, expected in cost_tests:
        result = clean_cost(dirty)
        ok = abs(result - expected) < 0.01
        sym = "✓" if ok else "✗"
        if not ok: all_ok = False
        print(f"  {sym}  {dirty!r:15s} → {result:.2f}  (expected {expected:.2f})")

    currency_tests = [
        ('inr', 'INR'), ('dollar', 'USD'), ('euro', 'EUR'),
        ('pound', 'GBP'), ('Indian Rupee', 'INR'), ('Us Dollar', 'USD'),
    ]
    for dirty, expected in currency_tests:
        result = clean_currency(dirty)
        ok = result == expected
        sym = "✓" if ok else "✗"
        if not ok: all_ok = False
        print(f"  {sym}  {dirty!r:15s} → {result!r:8s}  (expected {expected!r})")

    results['All spot-checks pass'] = all_ok
    _status(results, 'All spot-checks pass')

    # ── 4. Negative cost flags ────────────────────────────────
    print(f"\n{sep}")
    print("  4. NEGATIVE COST FLAGS")
    print(sep)

    neg_count = df['Is_Negative_Cost'].sum()
    neg_actual = (df['Cost_Clean'] < 0).sum()

    print(f"  Flagged negative:     {neg_count}")
    print(f"  Actual negative:      {neg_actual}")

    results['Negative flag correct'] = neg_count == neg_actual
    _status(results, 'Negative flag correct')

    # ── 5. Zero cost flags ────────────────────────────────────
    print(f"\n{sep}")
    print("  5. ZERO COST FLAGS")
    print(sep)

    zero_count = df['Is_Zero_Cost'].sum()
    zero_actual = (df['Cost_Clean'] == 0).sum()

    print(f"  Flagged zero:         {zero_count}")
    print(f"  Actual zero:          {zero_actual}")

    results['Zero flag correct'] = zero_count == zero_actual
    _status(results, 'Zero flag correct')

    # ── 6. Coverage ───────────────────────────────────────────
    print(f"\n{sep}")
    print("  6. COST COVERAGE")
    print(sep)

    coverage = df['Cost_Clean'].notna().mean() * 100
    print(f"  Coverage: {coverage:.1f}%")

    results['Coverage > 95%'] = coverage > 95
    _status(results, 'Coverage > 95%')

    # ── Summary ───────────────────────────────────────────────
    print(f"\n{sep}")
    print("  SUMMARY — S05 VALIDATION")
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

    billing = pd.read_csv('data/raw/usage_billing.csv')
    billing = s05_run(billing)
    validate(billing)
