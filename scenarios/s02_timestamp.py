"""
Scenario 02 — Timestamp Normalization to UTC
=============================================
Cleans Timestamp column:
  - Parse multiple formats (ISO+tz, ISO+Z, slash, DD-MM-YYYY, etc.)
  - Normalize all to UTC (ISO 8601)
  - Flag garbage dates (1970, 2099) and null them out
  - Handle nulls, 'NULL', 'N/A', garbage strings

Input:  dirty Timestamp string
Output: TS_UTC (datetime), TS_Parse_Failed (bool), TS_Garbage_Flag (bool)
"""

import pandas as pd
import re
import pytz
from dateutil import parser as dateparser
from datetime import timedelta


# Timestamps outside this range are garbage (1970 defaults, 2099 placeholders)
VALID_TS_MIN = pd.Timestamp('2025-01-01', tz='UTC')
VALID_TS_MAX = pd.Timestamp('2027-01-01', tz='UTC')


def clean_timestamp(val):
    """
    Parse a single dirty timestamp string and convert to UTC.

    Handles:
      - ISO with Z:       2026-01-15T10:30:00Z
      - ISO with offset:  2026-01-15T10:30:00+05:30
      - Standard:         2026-01-15 10:30:00
      - Slash:            2026/01/15 10:30
      - DD-MM-YYYY:       15-01-2026 10:30:00
      - Missing hyphen:   2026-0115 10:30
      - Nulls, 'NULL', 'N/A', garbage strings
      - Out-of-range:     1970-01-01, 2099-12-31

    Returns:
        pd.Timestamp (UTC) or pd.NaT
    """
    if pd.isna(val) or str(val).strip().lower() in ('', 'n/a', 'na', 'null', 'none'):
        return pd.NaT

    val = str(val).strip()

    # Skip obvious garbage
    if val.lower() in ('garbage_ts', 'invalid', 'error'):
        return pd.NaT

    # Normalize YYYY/MM/DD → YYYY-MM-DD
    val = re.sub(r'(\d{4})/(\d{2})/(\d{2})', r'\1-\2-\3', val)

    # Fix DD-MM-YYYY → YYYY-MM-DD
    m = re.match(r'^(\d{2})-(\d{2})-(\d{4})(.*)', val)
    if m:
        val = f"{m.group(3)}-{m.group(2)}-{m.group(1)}{m.group(4)}"

    # Fix missing hyphen: 2026-0115 → 2026-01-15
    val = re.sub(r'(\d{4})-(\d{2})(\d{2})\s', r'\1-\2-\3 ', val)

    # Try parsing
    try:
        dt = dateparser.parse(val)
        if dt is None:
            return pd.NaT
    except (ValueError, OverflowError):
        return pd.NaT

    # Normalize to UTC
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    else:
        dt = dt.astimezone(pytz.utc)

    return pd.Timestamp(dt)


def run(df, data_dir='data/raw'):
    """
    Execute S02 cleaning on the dataframe.

    Args:
        df: DataFrame with 'Timestamp' column

    Returns:
        df with new columns: TS_UTC, TS_Parse_Failed, TS_Garbage_Flag
    """
    # Parse timestamps
    df['TS_UTC'] = df['Timestamp'].apply(clean_timestamp)

    # Flag parse failures (had a value but couldn't parse)
    df['TS_Parse_Failed'] = df['TS_UTC'].isna() & df['Timestamp'].notna()

    # Flag garbage dates (parsed but outside valid range)
    df['TS_Garbage_Flag'] = (
        df['TS_UTC'].notna() &
        (
            (df['TS_UTC'] < VALID_TS_MIN) |
            (df['TS_UTC'] > VALID_TS_MAX)
        )
    )

    # Null out garbage timestamps
    garbage_count = df['TS_Garbage_Flag'].sum()
    df.loc[df['TS_Garbage_Flag'], 'TS_UTC'] = pd.NaT

    print("✅ S02 — Timestamp Normalization complete")
    print(f"   Successfully parsed: {df['TS_UTC'].notna().sum()}")
    print(f"   Parse failures:      {df['TS_Parse_Failed'].sum()}")
    print(f"   Garbage flagged:     {garbage_count}")
    print(f"   Final null TS_UTC:   {df['TS_UTC'].isna().sum()}")

    return df


if __name__ == '__main__':
    import sys
    sys.path.insert(0, '.')
    billing = pd.read_csv('data/raw/usage_billing.csv')
    billing = run(billing)
    print("\nSample parsed timestamps:")
    print(billing[['Timestamp', 'TS_UTC', 'TS_Parse_Failed', 'TS_Garbage_Flag']].sample(10).to_string(index=False))
