"""
Scenario 04 — Unit Normalization & Dimension Validation
========================================================
Cleans Unit column and converts Usage_Value accordingly:
  - sec/seconds/secs/second → seconds (no conversion)
  - mins/minutes/min → seconds (×60)
  - hrs/hours/hr/hour → seconds (×3600)
  - gb/GB/gigabytes/Gb → GB (no conversion)
  - mb/MB/megabytes → GB (÷1024)
  - Flag unit/service dimension mismatches (e.g. Storage billed in seconds)

Input:  dirty Unit strings, Usage_Value, Service_Clean
Output: Unit_Canonical, Usage_Converted, Unit_Dimension_Mismatch (bool)
"""

import pandas as pd
import numpy as np


# ── Normalization maps ────────────────────────────────────────

TIME_UNITS = {
    'sec': ('seconds', 1),
    'secs': ('seconds', 1),
    'second': ('seconds', 1),
    'seconds': ('seconds', 1),
    'min': ('seconds', 60),
    'mins': ('seconds', 60),
    'minutes': ('seconds', 60),
    'hr': ('seconds', 3600),
    'hrs': ('seconds', 3600),
    'hour': ('seconds', 3600),
    'hours': ('seconds', 3600),
}

DATA_UNITS = {
    'gb': ('GB', 1),
    'gigabytes': ('GB', 1),
    'mb': ('GB', 1/1024),
    'megabytes': ('GB', 1/1024),
}

# Expected unit dimension per service
SERVICE_DIMENSION = {
    'Compute': 'time',
    'Database': 'time',
    'Storage': 'data',
}


def normalize_unit(unit_str, usage_val):
    """
    Normalize a unit string and convert the usage value.

    Returns:
        (canonical_unit, converted_value) or (None, None)
    """
    if pd.isna(unit_str) or str(unit_str).strip() == '':
        return (None, usage_val)

    key = str(unit_str).strip().lower()

    if key in TIME_UNITS:
        canonical, factor = TIME_UNITS[key]
        converted = usage_val * factor if pd.notna(usage_val) else np.nan
        return (canonical, round(converted, 2))

    if key in DATA_UNITS:
        canonical, factor = DATA_UNITS[key]
        converted = usage_val * factor if pd.notna(usage_val) else np.nan
        return (canonical, round(converted, 4))

    return (None, usage_val)  # unrecognized


def run(df, data_dir='data/raw'):
    """
    Execute S04 cleaning on the dataframe.

    Args:
        df: DataFrame with 'Unit', 'Usage_Value', 'Service_Clean' columns

    Returns:
        df with new columns: Unit_Canonical, Usage_Converted, Unit_Dimension_Mismatch
    """
    # Normalize units and convert values
    results = df.apply(
        lambda row: normalize_unit(row['Unit'], row['Usage_Value']),
        axis=1
    )
    df['Unit_Canonical']  = results.apply(lambda x: x[0])
    df['Usage_Converted'] = results.apply(lambda x: x[1])

    # Check dimension mismatch: Storage should use data units, Compute/DB should use time
    def check_mismatch(row):
        svc = row.get('Service_Clean')
        unit = row.get('Unit_Canonical')
        if pd.isna(svc) or pd.isna(unit):
            return False
        expected_dim = SERVICE_DIMENSION.get(svc)
        if expected_dim == 'time' and unit != 'seconds':
            return True
        if expected_dim == 'data' and unit != 'GB':
            return True
        return False

    df['Unit_Dimension_Mismatch'] = df.apply(check_mismatch, axis=1)

    print("✅ S04 — Unit Normalization complete")
    print(f"   Rows with canonical unit:    {df['Unit_Canonical'].notna().sum()}")
    print(f"   Unrecognized units:          {df['Unit_Canonical'].isna().sum()}")
    print(f"   Dimension mismatches:        {df['Unit_Dimension_Mismatch'].sum()}")
    print(f"   Unit distribution:")
    print(f"     {df['Unit_Canonical'].value_counts().to_dict()}")

    return df


if __name__ == '__main__':
    import sys
    sys.path.insert(0, '.')
    billing = pd.read_csv('data/raw/usage_billing.csv')

    # Need Service_Clean from S03
    from scenarios.s03_sku import run as s03_run
    billing = s03_run(billing)
    billing = run(billing)

    print("\nSample:")
    print(billing[['Unit', 'Unit_Canonical', 'Usage_Value', 'Usage_Converted', 'Unit_Dimension_Mismatch']].sample(10).to_string(index=False))
