"""
Validation 03 — SKU & Service Normalization Validation
=======================================================
Validates the output of S03 (SKU & Service Cleaning).
Checks: canonical format, catalog coverage, unmatched rate, service normalization, distribution.
"""

import pandas as pd
import re
import os


def validate(df, data_dir='data/raw'):
    """
    Run all validation checks for S03.

    Args:
        df: DataFrame after S03 cleaning (has SKU_Clean, SKU_Unmatched, Service_Clean)
        data_dir: path to raw data

    Returns:
        (passed, failed, results) tuple
    """
    sep = "=" * 55
    results = {}

    # Load catalog for reference
    cat = pd.read_csv(os.path.join(data_dir, 'sku_catalog.csv'))
    catalog_skus = set(cat['SKU_ID'].unique())

    # ── 1. Canonical SKU format ───────────────────────────────
    print(f"\n{sep}")
    print("  1. CANONICAL SKU FORMAT")
    print(sep)

    non_null_skus = df['SKU_Clean'].dropna()
    in_catalog = non_null_skus.isin(catalog_skus)

    print(f"  Non-null cleaned SKUs:    {len(non_null_skus)}")
    print(f"  In catalog:               {in_catalog.sum()}")
    print(f"  Not in catalog:           {(~in_catalog).sum()}")

    results['All clean SKUs in catalog'] = in_catalog.all()
    _status(results, 'All clean SKUs in catalog')

    # ── 2. Unmatched rate ─────────────────────────────────────
    print(f"\n{sep}")
    print("  2. UNMATCHED RATE")
    print(sep)

    unmatched = df['SKU_Unmatched'].sum()
    unmatched_pct = unmatched / len(df) * 100

    print(f"  Unmatched rows:    {unmatched}")
    print(f"  Unmatched rate:    {unmatched_pct:.1f}%")
    print(f"  Expected:          ~2-5%")

    if unmatched > 0:
        print(f"\n  Sample unmatched SKUs:")
        print(df[df['SKU_Unmatched']]['SKU'].value_counts().head(5).to_string())

    results['Unmatched rate < 10%'] = unmatched_pct < 10
    _status(results, 'Unmatched rate < 10%')

    # ── 3. SKU change audit ───────────────────────────────────
    print(f"\n{sep}")
    print("  3. SKU CHANGE AUDIT")
    print(sep)

    changed = df['SKU_Changed'].sum()
    change_pct = changed / len(df) * 100

    print(f"  Rows changed:      {changed}  ({change_pct:.1f}%)")

    results['Change rate reasonable'] = 5 <= change_pct <= 40
    _status(results, 'Change rate reasonable')

    # ── 4. Dirty variant spot-check ───────────────────────────
    print(f"\n{sep}")
    print("  4. DIRTY VARIANT SPOT-CHECK")
    print(sep)

    from scenarios.s03_sku import clean_sku, load_sku_catalog
    _, sku_lookup, _ = load_sku_catalog(data_dir)

    test_cases = {
        'ec2-t3.medium':     'EC2-t3.medium',
        'EC2-T3.MEDIUM':     'EC2-t3.medium',
        'EC2_t3_medium':     'EC2-t3.medium',
        's3-standard':       'S3-Standard',
        'S3_STANDARD':       'S3-Standard',
        'VM-STANDARD_D2S':   'VM-Standard_D2s',
        'vm-standard_d2s':   'VM-Standard_D2s',
        'gce-n1-standard-2': 'GCE-n1-standard-2',
    }

    all_passed = True
    for dirty, expected in test_cases.items():
        result, _ = clean_sku(dirty, sku_lookup)
        ok = result == expected
        sym = "✓" if ok else "✗"
        if not ok:
            all_passed = False
        print(f"  {sym}  {dirty!r:25s} → {str(result)!r:22s}  (expected {expected!r})")

    results['Dirty variants normalize'] = all_passed
    _status(results, 'Dirty variants normalize')

    # ── 5. Service normalization ──────────────────────────────
    print(f"\n{sep}")
    print("  5. SERVICE NORMALIZATION")
    print(sep)

    valid_services = {'Compute', 'Storage', 'Database'}
    non_null_svc = df['Service_Clean'].dropna()
    bad_svc = non_null_svc[~non_null_svc.isin(valid_services)]

    print(f"  Non-null services:   {len(non_null_svc)}")
    print(f"  Invalid services:    {len(bad_svc)}")
    print(f"  Service distribution:")
    print(df['Service_Clean'].value_counts().to_string())

    results['All services canonical'] = len(bad_svc) == 0
    _status(results, 'All services canonical')

    # ── 6. SKU distribution ───────────────────────────────────
    print(f"\n{sep}")
    print("  6. SKU DISTRIBUTION")
    print(sep)

    sku_dist = df['SKU_Clean'].value_counts()
    print(f"  Unique clean SKUs: {df['SKU_Clean'].dropna().nunique()}")
    print(f"  Top SKUs:")
    print(sku_dist.head(8).to_string())

    results['Multiple SKUs present'] = df['SKU_Clean'].dropna().nunique() >= 10
    _status(results, 'Multiple SKUs present')

    # ── Summary ───────────────────────────────────────────────
    print(f"\n{sep}")
    print("  SUMMARY — S03 VALIDATION")
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

    billing = pd.read_csv('data/raw/usage_billing.csv')
    billing = s03_run(billing)
    validate(billing)
