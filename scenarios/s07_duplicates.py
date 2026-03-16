"""
Scenario 07 — Duplicate Detection & Removal
=============================================
Identifies and flags exact duplicate rows in usage_billing.csv.
~550 duplicates were injected during generation.

Input:  full dataframe
Output: Is_Duplicate (bool), Duplicate_Group_ID (int or NaN)

Note: We FLAG duplicates but don't drop them — the pipeline decides what to do.
"""

import pandas as pd


# Columns used to detect duplicates (original raw columns only)
DEDUP_COLS = [
    'Usage_ID', 'Account_ID', 'Timestamp', 'Service', 'SKU',
    'Usage_Value', 'Unit', 'Cost', 'Currency', 'Region', 'Resource_ID',
]


def run(df, data_dir='data/raw'):
    """
    Execute S07 duplicate detection on the dataframe.

    Args:
        df: DataFrame (must have raw columns present)

    Returns:
        df with new columns: Is_Duplicate, Duplicate_Keep (first occurrence kept)
    """
    # Mark all duplicates (keep=False marks ALL copies)
    df['Is_Duplicate'] = df.duplicated(subset=DEDUP_COLS, keep=False)

    # Mark which to keep (keep='first' marks only subsequent copies)
    df['Duplicate_Keep'] = ~df.duplicated(subset=DEDUP_COLS, keep='first')

    total_dup = df['Is_Duplicate'].sum()
    to_remove = (~df['Duplicate_Keep'] & df['Is_Duplicate']).sum()
    to_keep   = (df['Duplicate_Keep'] & df['Is_Duplicate']).sum()

    print("✅ S07 — Duplicate Detection complete")
    print(f"   Total duplicate rows:     {total_dup}")
    print(f"   First occurrences (keep): {to_keep}")
    print(f"   Extra copies (removable): {to_remove}")
    print(f"   Unique rows:              {(~df['Is_Duplicate']).sum()}")

    return df


if __name__ == '__main__':
    billing = pd.read_csv('data/raw/usage_billing.csv')
    billing = run(billing)
    print("\nDuplicate samples:")
    dups = billing[billing['Is_Duplicate']].sort_values('Usage_ID')
    print(dups[['Usage_ID', 'Account_ID', 'SKU', 'Is_Duplicate', 'Duplicate_Keep']].head(10).to_string(index=False))
