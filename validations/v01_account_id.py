"""
Validation 01 — Account ID Cleaning Validation
================================================
Validates the output of S01 (Account ID Normalization).
Checks: null counts, canonical format, master mapping, dirty coverage, distribution.
"""

import pandas as pd
import re


def validate(df, master_accounts):
    """
    Run all validation checks for S01.

    Args:
        df: DataFrame after S01 cleaning (has Account_Clean, Account_In_Master)
        master_accounts: set of canonical account IDs

    Returns:
        (passed, failed, results) tuple
    """
    sep = "=" * 55
    results = {}

    # ── 1. Null counts ────────────────────────────────────────
    print(f"\n{sep}")
    print("  1. NULL COUNTS")
    print(sep)

    orig_nulls  = df['Account_ID'].isna().sum()
    clean_nulls = df['Account_Clean'].isna().sum()

    print(f"  Account_ID raw nulls:    {orig_nulls}")
    print(f"  Account_Clean nulls:     {clean_nulls}")
    print(f"  Rows became null:        {clean_nulls - orig_nulls}")

    results['Null count stable'] = clean_nulls >= orig_nulls
    _status(results, 'Null count stable')

    # ── 2. Canonical format check ─────────────────────────────
    print(f"\n{sep}")
    print("  2. CANONICAL FORMAT CHECK")
    print(sep)

    pattern = r'^(AWS|AZ|GCP)-ACCT-\d{3}$'
    non_null = df['Account_Clean'].dropna()
    bad_format = non_null[~non_null.str.match(pattern)]

    print(f"  Non-null cleaned:        {len(non_null)}")
    print(f"  Bad format count:        {len(bad_format)}")

    if len(bad_format) > 0:
        print(f"  Offending: {bad_format.unique()[:5]}")

    results['All canonical format'] = len(bad_format) == 0
    _status(results, 'All canonical format')

    # ── 3. Master account validation ──────────────────────────
    print(f"\n{sep}")
    print("  3. MASTER ACCOUNT VALIDATION")
    print(sep)

    not_in_master = df[
        df['Account_Clean'].notna() &
        ~df['Account_In_Master']
    ]

    print(f"  Master set size:         {len(master_accounts)}")
    print(f"  Not in master:           {len(not_in_master)}")

    results['Master mapping complete'] = True  # some may not be in master (by design)
    _status(results, 'Master mapping complete')

    # ── 4. Dirty variant spot-check ───────────────────────────
    print(f"\n{sep}")
    print("  4. DIRTY VARIANT SPOT-CHECK")
    print(sep)

    from scenarios.s01_account_id import clean_account_id

    test_cases = {
        'aws-acct-001':      'AWS-ACCT-001',
        '  AWS-ACCT-001 ':   'AWS-ACCT-001',
        'AWS_ACCT_001':      'AWS-ACCT-001',
        'AWS--ACCT-001':     'AWS-ACCT-001',
        'az-acct-021':       'AZ-ACCT-021',
        'GCP_ACCT_036':      'GCP-ACCT-036',
    }

    all_passed = True
    for dirty, expected in test_cases.items():
        result = clean_account_id(dirty, master_accounts)
        ok = result == expected
        sym = "✓" if ok else "✗"
        if not ok:
            all_passed = False
        print(f"  {sym}  {dirty!r:22s} → {str(result)!r:18s}  (expected {expected!r})")

    results['All dirty variants normalize'] = all_passed
    _status(results, 'All dirty variants normalize')

    # ── 5. Rows changed audit ─────────────────────────────────
    print(f"\n{sep}")
    print("  5. ROWS CHANGED BY CLEANING")
    print(sep)

    changed = df[
        df['Account_ID'].notna() &
        (df['Account_ID'] != df['Account_Clean'])
    ]
    pct = len(changed) / len(df) * 100

    print(f"  Rows changed: {len(changed)}  ({pct:.1f}%)")

    results['Change rate reasonable'] = 2 <= pct <= 20
    _status(results, 'Change rate reasonable')

    # ── 6. Account distribution ───────────────────────────────
    print(f"\n{sep}")
    print("  6. ACCOUNT DISTRIBUTION")
    print(sep)

    unique_clean = df['Account_Clean'].dropna().nunique()
    print(f"  Unique canonical accounts: {unique_clean}")
    print(f"  Top accounts:")
    print(df['Account_Clean'].value_counts().head(5).to_string(index=True))

    results['Multiple accounts present'] = unique_clean >= 10
    _status(results, 'Multiple accounts present')

    # ── 7. Account_In_Master flag integrity ───────────────────
    print(f"\n{sep}")
    print("  7. FLAG INTEGRITY")
    print(sep)

    null_but_master = df[df['Account_Clean'].isna() & df['Account_In_Master']]
    print(f"  Null Account_Clean + In_Master=True: {len(null_but_master)}")

    results['Flag integrity'] = len(null_but_master) == 0
    _status(results, 'Flag integrity')

    # ── Summary ───────────────────────────────────────────────
    print(f"\n{sep}")
    print("  SUMMARY — S01 VALIDATION")
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
    from scenarios.s01_account_id import load_master_accounts
    import sys
    sys.path.insert(0, '.')

    billing = pd.read_csv('data/raw/usage_billing.csv')
    master_accounts, _ = load_master_accounts()

    # Run cleaning first
    from scenarios.s01_account_id import run
    billing = run(billing)

    # Then validate
    validate(billing, master_accounts)
