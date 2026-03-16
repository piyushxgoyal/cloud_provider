"""
Scenario 03 — SKU & Service Normalization
==========================================
Cleans SKU and Service columns:
  - Normalize SKU names against sku_catalog.csv (case, separators)
  - Fix Service column casing (Compute/Storage/Database)
  - Flag unknown/unmatched SKUs

Input:  dirty SKU (mixed case, underscores, unknowns), dirty Service (case)
Output: SKU_Clean, SKU_Unmatched (bool), SKU_Changed (bool), Service_Clean
"""

import pandas as pd
import re
import os


def load_sku_catalog(data_dir='data/raw'):
    """Load canonical SKUs from sku_catalog.csv (unique SKU_IDs only)."""
    cat = pd.read_csv(os.path.join(data_dir, 'sku_catalog.csv'))
    canonical_skus = cat['SKU_ID'].unique().tolist()

    # Build a lookup: normalized key → canonical SKU
    sku_lookup = {}
    for sku in canonical_skus:
        # Store multiple normalized forms for matching
        key = sku.upper().replace('_', '-').replace('.', '-').strip()
        sku_lookup[key] = sku
        # Also store without separators
        key2 = re.sub(r'[^A-Z0-9]', '', sku.upper())
        sku_lookup[key2] = sku

    return set(canonical_skus), sku_lookup, cat


def clean_sku(val, sku_lookup):
    """
    Normalize a single SKU value to its canonical form.

    Handles:
      - lowercase:   ec2-t3.medium → EC2-t3.medium
      - uppercase:   EC2-T3.MEDIUM → EC2-t3.medium
      - underscores: EC2_t3_medium → EC2-t3.medium
      - unknown:     UNKNOWN-SKU-123 → None

    Returns:
        (canonical_sku, is_unmatched)
    """
    if pd.isna(val) or str(val).strip() == '':
        return (None, True)

    val_str = str(val).strip()

    # Normalize for lookup
    key = val_str.upper().replace('_', '-').replace('.', '-').strip()
    if key in sku_lookup:
        return (sku_lookup[key], False)

    # Try without separators
    key2 = re.sub(r'[^A-Z0-9]', '', val_str.upper())
    if key2 in sku_lookup:
        return (sku_lookup[key2], False)

    return (None, True)


def clean_service(val):
    """
    Normalize Service column to canonical casing.

    Canonical: Compute, Storage, Database
    """
    if pd.isna(val) or str(val).strip() == '':
        return None

    val = str(val).strip().lower()
    mapping = {
        'compute': 'Compute',
        'storage': 'Storage',
        'database': 'Database',
    }
    return mapping.get(val, None)


def run(df, data_dir='data/raw'):
    """
    Execute S03 cleaning on the dataframe.

    Args:
        df: DataFrame with 'SKU' and 'Service' columns
        data_dir: path to raw data directory

    Returns:
        df with new columns: SKU_Clean, SKU_Unmatched, SKU_Changed, Service_Clean
    """
    canonical_skus, sku_lookup, catalog_df = load_sku_catalog(data_dir)

    # Clean SKUs
    sku_results = df['SKU'].apply(lambda x: clean_sku(x, sku_lookup))
    df['SKU_Clean']     = sku_results.apply(lambda x: x[0])
    df['SKU_Unmatched'] = sku_results.apply(lambda x: x[1])
    df['SKU_Changed']   = (df['SKU'] != df['SKU_Clean']) & df['SKU_Clean'].notna()

    # Clean Service
    df['Service_Clean'] = df['Service'].apply(clean_service)

    print("✅ S03 — SKU & Service Normalization complete")
    print(f"   SKUs cleaned:       {df['SKU_Changed'].sum()}")
    print(f"   Unmatched SKUs:     {df['SKU_Unmatched'].sum()}")
    print(f"   Unique clean SKUs:  {df['SKU_Clean'].dropna().nunique()}")
    print(f"   Service nulls:      {df['Service_Clean'].isna().sum()}")

    return df


if __name__ == '__main__':
    import sys
    sys.path.insert(0, '.')
    billing = pd.read_csv('data/raw/usage_billing.csv')
    billing = run(billing)
    print("\nSample:")
    print(billing[['SKU', 'SKU_Clean', 'SKU_Unmatched', 'Service', 'Service_Clean']].sample(10).to_string(index=False))
