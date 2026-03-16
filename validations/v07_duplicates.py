"""
Validation 07 — Duplicate Detection Validation
================================================
Validates the output of S07 (Duplicate Detection).
Checks: duplicate count, flag consistency, unique Usage_IDs, dedup result size.
"""

import pandas as pd


def validate(df):
    """
    Run all validation checks for S07.

    Returns:
        (passed, failed, results) tuple
    """
    sep = "=" * 55
    results = {}

    # ── 1. Duplicate count ────────────────────────────────────
    print(f"\n{sep}")
    print("  1. DUPLICATE COUNT")
    print(sep)

    total_dup = df['Is_Duplicate'].sum()
    extra     = (~df['Duplicate_Keep'] & df['Is_Duplicate']).sum()

    print(f"  Total rows:           {len(df)}")
    print(f"  Duplicate rows:       {total_dup}")
    print(f"  Extra copies:         {extra}")
    print(f"  Expected ~550 extras")

    results['Extra copies ~550'] = 400 <= extra <= 700
    _status(results, 'Extra copies ~550')

    # ── 2. Flag consistency ───────────────────────────────────
    print(f"\n{sep}")
    print("  2. FLAG CONSISTENCY")
    print(sep)

    # Non-duplicate rows should all have Duplicate_Keep=True
    non_dup_bad = df[~df['Is_Duplicate'] & ~df['Duplicate_Keep']]
    print(f"  Non-dup with Keep=False: {len(non_dup_bad)}")

    results['Non-dup all Keep=True'] = len(non_dup_bad) == 0
    _status(results, 'Non-dup all Keep=True')

    # ── 3. Dedup result size ──────────────────────────────────
    print(f"\n{sep}")
    print("  3. DEDUP RESULT SIZE")
    print(sep)

    kept = df[df['Duplicate_Keep']]
    print(f"  Rows after dedup:   {len(kept)}")
    print(f"  Expected ~10,000")

    results['Dedup ~10000 rows'] = 9800 <= len(kept) <= 10200
    _status(results, 'Dedup ~10000 rows')

    # ── 4. Usage_ID duplicates ────────────────────────────────
    print(f"\n{sep}")
    print("  4. USAGE_ID DUPLICATES")
    print(sep)

    uid_dups = df['Usage_ID'].duplicated(keep=False).sum()
    print(f"  Rows with duplicate Usage_ID: {uid_dups}")

    results['Usage_ID dups match'] = uid_dups == total_dup
    _status(results, 'Usage_ID dups match')

    # ── 5. Sample duplicates ──────────────────────────────────
    print(f"\n{sep}")
    print("  5. SAMPLE DUPLICATES")
    print(sep)

    dup_rows = df[df['Is_Duplicate']].sort_values('Usage_ID')
    if len(dup_rows) > 0:
        sample_id = dup_rows['Usage_ID'].iloc[0]
        group = df[df['Usage_ID'] == sample_id]
        print(f"  Sample Usage_ID: {sample_id}")
        print(f"  Copies found: {len(group)}")
        print(group[['Usage_ID', 'Account_ID', 'SKU', 'Is_Duplicate', 'Duplicate_Keep']].to_string(index=False))

    results['Sample has 2+ copies'] = len(group) >= 2 if len(dup_rows) > 0 else False
    _status(results, 'Sample has 2+ copies')

    # ── Summary ───────────────────────────────────────────────
    print(f"\n{sep}")
    print("  SUMMARY — S07 VALIDATION")
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
    from scenarios.s07_duplicates import run as s07_run

    billing = pd.read_csv('data/raw/usage_billing.csv')
    billing = s07_run(billing)
    validate(billing)
