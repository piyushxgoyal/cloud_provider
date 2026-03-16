"""
Scenario 06 — Region Normalization
====================================
Cleans Region column:
  - Normalize to canonical region slugs (us-east-1, eastus, us-central1, etc.)
  - Handle case variations, whitespace, abbreviations
  - Flag unresolvable regions

Input:  dirty Region strings (mixed case, spaces, abbreviations, suffixed)
Output: Region_Clean, Region_Unresolvable (bool)
"""

import pandas as pd
import re


# Canonical regions per cloud
CANONICAL_REGIONS = {
    # AWS
    'us-east-1', 'eu-west-1', 'ap-south-1', 'us-west-2', 'ap-southeast-1',
    # Azure
    'eastus', 'westeurope', 'centralindia', 'canadacentral', 'southeastasia',
    # GCP
    'us-central1', 'europe-west1', 'asia-south1', 'us-west1', 'asia-southeast1',
}

# Fuzzy mapping: known dirty variants → canonical
REGION_ALIASES = {
    # AWS variants
    'us east 1': 'us-east-1', 'useast1': 'us-east-1', 'usea': 'us-east-1',
    'us-east-1': 'us-east-1',
    'eu west 1': 'eu-west-1', 'euwest1': 'eu-west-1',
    'eu-west-1': 'eu-west-1',
    'ap south 1': 'ap-south-1', 'apsouth1': 'ap-south-1',
    'ap-south-1': 'ap-south-1',
    'us west 2': 'us-west-2', 'uswest2': 'us-west-2',
    'us-west-2': 'us-west-2',
    'ap southeast 1': 'ap-southeast-1', 'apsoutheast1': 'ap-southeast-1',
    'ap-southeast-1': 'ap-southeast-1',

    # Azure variants
    'eastus': 'eastus', 'east us': 'eastus', 'eastus2': 'eastus',
    'westeurope': 'westeurope', 'west europe': 'westeurope', 'westeurope2': 'westeurope',
    'centralindia': 'centralindia', 'central india': 'centralindia',
    'canadacentral': 'canadacentral', 'canada central': 'canadacentral',
    'southeastasia': 'southeastasia', 'southeast asia': 'southeastasia',

    # GCP variants
    'us-central1': 'us-central1', 'us central1': 'us-central1', 'uscentral1': 'us-central1',
    'europe-west1': 'europe-west1', 'europe west1': 'europe-west1', 'europewest1': 'europe-west1',
    'asia-south1': 'asia-south1', 'asia south1': 'asia-south1', 'asiasouth1': 'asia-south1',
    'us-west1': 'us-west1', 'us west1': 'us-west1', 'uswest1': 'us-west1',
    'asia-southeast1': 'asia-southeast1', 'asia southeast1': 'asia-southeast1',
}


def clean_region(val):
    """
    Normalize a single region value.

    Returns:
        (canonical_region, is_unresolvable)
    """
    if pd.isna(val) or str(val).strip() == '':
        return (None, True)

    raw = str(val).strip().lower()

    # Remove trailing digits that are typos (e.g. eastus2 → eastus)
    # but keep legitimate ones like us-central1

    # Direct match
    if raw in CANONICAL_REGIONS:
        return (raw, False)

    # Alias lookup
    if raw in REGION_ALIASES:
        return (REGION_ALIASES[raw], False)

    # Try removing extra spaces/dashes
    normalized = re.sub(r'[\s]+', ' ', raw).strip()
    if normalized in REGION_ALIASES:
        return (REGION_ALIASES[normalized], False)

    # Try collapsing all spaces
    collapsed = raw.replace(' ', '')
    if collapsed in REGION_ALIASES:
        return (REGION_ALIASES[collapsed], False)

    # Azure: "East us" → "eastus"
    no_space = raw.replace(' ', '')
    if no_space in CANONICAL_REGIONS:
        return (no_space, False)

    return (None, True)


def run(df, data_dir='data/raw'):
    """
    Execute S06 cleaning on the dataframe.

    Args:
        df: DataFrame with 'Region' column

    Returns:
        df with new columns: Region_Clean, Region_Unresolvable
    """
    results = df['Region'].apply(clean_region)
    df['Region_Clean']        = results.apply(lambda x: x[0])
    df['Region_Unresolvable'] = results.apply(lambda x: x[1])

    print("✅ S06 — Region Normalization complete")
    print(f"   Resolved:       {df['Region_Clean'].notna().sum()}")
    print(f"   Unresolvable:   {df['Region_Unresolvable'].sum()}")
    print(f"   Unique regions: {df['Region_Clean'].dropna().nunique()}")

    return df


if __name__ == '__main__':
    billing = pd.read_csv('data/raw/usage_billing.csv')
    billing = run(billing)
    print("\nRegion distribution:")
    print(billing['Region_Clean'].value_counts().to_string())
