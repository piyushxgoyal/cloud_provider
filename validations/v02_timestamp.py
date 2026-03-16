"""
Validation 02 — Timestamp Normalization Validation
===================================================
Validates the output of S02 (Timestamp to UTC).
Checks: parse rate, UTC enforcement, valid range, garbage flags, format coverage.
"""

import pandas as pd
import re


def validate(df):
    """
    Run all validation checks for S02.

    Args:
        df: DataFrame after S02 cleaning (has TS_UTC, TS_Parse_Failed, TS_Garbage_Flag)

    Returns:
        (passed, failed, results) tuple
    """
    sep = "=" * 55
    results = {}

    VALID_TS_MIN = pd.Timestamp('2025-01-01', tz='UTC')
    VALID_TS_MAX = pd.Timestamp('2027-01-01', tz='UTC')

    # ── 1. Parse success rate ─────────────────────────────────
    print(f"\n{sep}")
    print("  1. PARSE SUCCESS RATE")
    print(sep)

    total        = len(df)
    parsed_ok    = df['TS_UTC'].notna().sum()
    parse_failed = df['TS_Parse_Failed'].sum()
    garbage      = df['TS_Garbage_Flag'].sum()
    final_null   = df['TS_UTC'].isna().sum()

    print(f"  Total rows:           {total}")
    print(f"  Successfully parsed:  {parsed_ok}")
    print(f"  Parse failures:       {parse_failed}")
    print(f"  Garbage dates:        {garbage}")
    print(f"  Final null TS_UTC:    {final_null}")

    parse_rate = parsed_ok / total * 100
    print(f"  Parse rate:           {parse_rate:.1f}%")

    results['Parse rate > 90%'] = parse_rate > 90
    _status(results, 'Parse rate > 90%')

    # ── 2. UTC timezone enforcement ───────────────────────────
    print(f"\n{sep}")
    print("  2. UTC TIMEZONE ENFORCEMENT")
    print(sep)

    col_tz = str(df['TS_UTC'].dt.tz)
    print(f"  Column timezone: {col_tz}")
    print(f"  Column dtype:    {df['TS_UTC'].dtype}")

    results['Timezone is UTC'] = col_tz == 'UTC'
    _status(results, 'Timezone is UTC')

    # ── 3. Valid date range check ─────────────────────────────
    print(f"\n{sep}")
    print("  3. VALID DATE RANGE CHECK")
    print(sep)

    non_null_ts = df['TS_UTC'].dropna()
    if len(non_null_ts) > 0:
        ts_min = non_null_ts.min()
        ts_max = non_null_ts.max()
        print(f"  TS_UTC min: {ts_min}")
        print(f"  TS_UTC max: {ts_max}")

        out_of_range = df[
            df['TS_UTC'].notna() &
            ((df['TS_UTC'] < VALID_TS_MIN) | (df['TS_UTC'] > VALID_TS_MAX))
        ]
        print(f"  Out of range after cleaning: {len(out_of_range)}")

        results['No out-of-range timestamps'] = len(out_of_range) == 0
    else:
        results['No out-of-range timestamps'] = True

    _status(results, 'No out-of-range timestamps')

    # ── 4. Garbage flag check ─────────────────────────────────
    print(f"\n{sep}")
    print("  4. GARBAGE FLAG CHECK")
    print(sep)

    garbage_rows = df[df['TS_Garbage_Flag']]
    print(f"  Garbage rows total: {len(garbage_rows)}")

    if len(garbage_rows) > 0:
        # All garbage rows should have NaT in TS_UTC now
        garbage_not_nulled = garbage_rows[garbage_rows['TS_UTC'].notna()]
        print(f"  Garbage rows NOT nulled: {len(garbage_not_nulled)}")
        results['All garbage nulled'] = len(garbage_not_nulled) == 0

        print(f"\n  Sample garbage rows (raw Timestamp):")
        print(garbage_rows['Timestamp'].head(5).to_string(index=False))
    else:
        results['All garbage nulled'] = True

    _status(results, 'All garbage nulled')

    # ── 5. Input format coverage ──────────────────────────────
    print(f"\n{sep}")
    print("  5. INPUT FORMAT COVERAGE")
    print(sep)

    raw = df['Timestamp'].dropna().astype(str)

    iso_z     = raw.str.contains(r'\d{4}-\d{2}-\d{2}T.*Z$', na=False, regex=True).sum()
    iso_tz    = raw.str.contains(r'[+-]\d{2}:\d{2}$', na=False, regex=True).sum()
    slash     = raw.str.contains(r'\d{4}/\d{2}/\d{2}', na=False, regex=True).sum()
    dd_mm     = raw.str.match(r'^\d{2}-\d{2}-\d{4}', na=False).sum()
    standard  = raw.str.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}', na=False).sum()

    formats = {
        'ISO with Z':       iso_z,
        'ISO with offset':  iso_tz,
        'Slash (YYYY/MM)':  slash,
        'DD-MM-YYYY':       dd_mm,
        'Standard':         standard,
    }

    for fmt, count in formats.items():
        sym = "✓" if count > 0 else "✗ none found"
        print(f"  {sym}  {fmt:20s}: {count} rows")

    detected = sum(1 for c in formats.values() if c > 0)
    results['Multiple formats detected'] = detected >= 3
    _status(results, 'Multiple formats detected')

    # ── 6. Null preservation check ────────────────────────────
    print(f"\n{sep}")
    print("  6. NULL PRESERVATION")
    print(sep)

    orig_nulls  = df['Timestamp'].isna().sum()
    final_nulls = df['TS_UTC'].isna().sum()

    print(f"  Original Timestamp nulls:  {orig_nulls}")
    print(f"  Final TS_UTC nulls:        {final_nulls}")
    print(f"  Increase:                  {final_nulls - orig_nulls}")

    results['Null count increased'] = final_nulls >= orig_nulls
    _status(results, 'Null count increased')

    # ── 7. Date distribution (months) ─────────────────────────
    print(f"\n{sep}")
    print("  7. DATE DISTRIBUTION")
    print(sep)

    if len(non_null_ts) > 0:
        month_dist = non_null_ts.dt.month.value_counts().sort_index()
        print("  Month distribution:")
        for month, count in month_dist.items():
            month_name = {1: 'Jan', 2: 'Feb', 3: 'Mar'}.get(month, f'M{month}')
            print(f"    {month_name} 2026: {count}")

        results['Data spans Jan-Mar'] = len(month_dist) >= 2
    else:
        results['Data spans Jan-Mar'] = False

    _status(results, 'Data spans Jan-Mar')

    # ── Summary ───────────────────────────────────────────────
    print(f"\n{sep}")
    print("  SUMMARY — S02 VALIDATION")
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
    from scenarios.s02_timestamp import run as s02_run

    billing = pd.read_csv('data/raw/usage_billing.csv')
    billing = s02_run(billing)
    validate(billing)
