"""
Validation 06 — Region Normalization Validation
=================================================
Validates the output of S06 (Region Normalization).
Checks: canonical format, unresolvable rate, multi-cloud coverage, spot-checks, distribution.
"""

import pandas as pd


CANONICAL_REGIONS = {
    'us-east-1', 'eu-west-1', 'ap-south-1', 'us-west-2', 'ap-southeast-1',
    'eastus', 'westeurope', 'centralindia', 'canadacentral', 'southeastasia',
    'us-central1', 'europe-west1', 'asia-south1', 'us-west1', 'asia-southeast1',
}


def validate(df):
    """
    Run all validation checks for S06.

    Returns:
        (passed, failed, results) tuple
    """
    sep = "=" * 55
    results = {}

    # ── 1. Canonical region check ─────────────────────────────
    print(f"\n{sep}")
    print("  1. CANONICAL REGION CHECK")
    print(sep)

    non_null = df['Region_Clean'].dropna()
    bad = non_null[~non_null.isin(CANONICAL_REGIONS)]

    print(f"  Non-null regions:     {len(non_null)}")
    print(f"  Not in canonical set: {len(bad)}")
    if len(bad) > 0:
        print(f"  Offending: {bad.unique()[:5]}")

    results['All regions canonical'] = len(bad) == 0
    _status(results, 'All regions canonical')

    # ── 2. Unresolvable rate ──────────────────────────────────
    print(f"\n{sep}")
    print("  2. UNRESOLVABLE RATE")
    print(sep)

    unresolvable = df['Region_Unresolvable'].sum()
    pct = unresolvable / len(df) * 100

    print(f"  Unresolvable rows:  {unresolvable}")
    print(f"  Rate:               {pct:.1f}%")

    results['Unresolvable < 5%'] = pct < 5
    _status(results, 'Unresolvable < 5%')

    # ── 3. Spot-checks ────────────────────────────────────────
    print(f"\n{sep}")
    print("  3. DIRTY VARIANT SPOT-CHECK")
    print(sep)

    from scenarios.s06_region import clean_region

    tests = [
        ('us east 1',     'us-east-1'),
        ('US-EAST-1',     'us-east-1'),
        ('EASTUS',        'eastus'),
        ('East us',       'eastus'),
        ('us central1',   'us-central1'),
        ('EUROPE-WEST1',  'europe-west1'),
        ('centralindia',  'centralindia'),
    ]

    all_ok = True
    for dirty, expected in tests:
        result, _ = clean_region(dirty)
        ok = result == expected
        sym = "✓" if ok else "✗"
        if not ok: all_ok = False
        print(f"  {sym}  {dirty!r:20s} → {str(result)!r:20s}  (expected {expected!r})")

    results['All variants normalize'] = all_ok
    _status(results, 'All variants normalize')

    # ── 4. Multi-cloud coverage ───────────────────────────────
    print(f"\n{sep}")
    print("  4. MULTI-CLOUD COVERAGE")
    print(sep)

    aws_regions = {'us-east-1', 'eu-west-1', 'ap-south-1', 'us-west-2', 'ap-southeast-1'}
    az_regions  = {'eastus', 'westeurope', 'centralindia', 'canadacentral', 'southeastasia'}
    gcp_regions = {'us-central1', 'europe-west1', 'asia-south1', 'us-west1', 'asia-southeast1'}

    found = set(non_null.unique())
    aws_found = found & aws_regions
    az_found  = found & az_regions
    gcp_found = found & gcp_regions

    print(f"  AWS regions:   {len(aws_found)}/5  {aws_found}")
    print(f"  Azure regions: {len(az_found)}/5  {az_found}")
    print(f"  GCP regions:   {len(gcp_found)}/5  {gcp_found}")

    results['All 3 clouds present'] = len(aws_found) > 0 and len(az_found) > 0 and len(gcp_found) > 0
    _status(results, 'All 3 clouds present')

    # ── 5. Distribution ───────────────────────────────────────
    print(f"\n{sep}")
    print("  5. REGION DISTRIBUTION")
    print(sep)

    print(df['Region_Clean'].value_counts().to_string())

    results['15 regions present'] = df['Region_Clean'].dropna().nunique() == 15
    _status(results, '15 regions present')

    # ── Summary ───────────────────────────────────────────────
    print(f"\n{sep}")
    print("  SUMMARY — S06 VALIDATION")
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
    from scenarios.s06_region import run as s06_run

    billing = pd.read_csv('data/raw/usage_billing.csv')
    billing = s06_run(billing)
    validate(billing)
