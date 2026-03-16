"""
Scenario 08 — Charge Type Normalization & Contradiction Flagging
=================================================================
Cleans Charge_Type column:
  - Normalize variants (billable, true, yes → Usage)
  - Normalize free tiers (free, free_tier → Free_Tier)
  - Navigate credits and refunds.
  - Flag anomalies: Cost > 0 but marked as Free_Tier.

Input:  Charge_Type, Cost_Clean (from S05)
Output: Charge_Type_Clean, Charge_Cost_Contradiction (bool)
"""

import pandas as pd


CHARGE_TYPE_MAP = {
    # Usage variants
    'billable': 'Usage', 'true': 'Usage', 'yes': 'Usage', '1': 'Usage',
    # Free variants
    'free': 'Free_Tier', 'free_tier': 'Free_Tier', 'free tier': 'Free_Tier',
    # Credit variants
    'credit': 'Credit',
    # Refund variants
    'refund': 'Refund',
}

def clean_charge_type(val):
    """
    Normalize charge type to 'Usage', 'Free_Tier', 'Credit', 'Refund', or 'Unknown'.
    """
    if pd.isna(val) or str(val).strip() == '':
        return 'Unknown'
    
    clean = str(val).strip().lower()
    
    # Check exact match
    if clean in CHARGE_TYPE_MAP:
        return CHARGE_TYPE_MAP[clean]
    
    return 'Unknown'

def run(df, data_dir='data/raw'):
    """
    Execute S08 on the dataframe.
    Requires Coast_Clean to be present (runs after S05).
    """
    df['Charge_Type_Clean'] = df['Charge_Type'].apply(clean_charge_type)
    
    # Flag contradictions (Free_Tier with Cost > 0)
    # Give a small epsilon for floating point zero
    def check_contradiction(row):
        charge = row.get('Charge_Type_Clean')
        cost = row.get('Cost_Clean')
        if pd.notna(cost) and cost > 0.01 and charge == 'Free_Tier':
            return True
        return False
        
    df['Charge_Cost_Contradiction'] = df.apply(check_contradiction, axis=1)
    
    print("✅ S08 — Charge Type Normalization complete")
    print(f"   Charge Types:      {df['Charge_Type_Clean'].value_counts().to_dict()}")
    print(f"   Unknowns:          {(df['Charge_Type_Clean'] == 'Unknown').sum()}")
    print(f"   Contradictions:    {df['Charge_Cost_Contradiction'].sum()}")
    
    return df

if __name__ == '__main__':
    # Need S05 for Cost_Clean
    import sys
    sys.path.insert(0, '.')
    from scenarios.s05_cost import run as s05_run
    
    billing = pd.read_csv('data/raw/usage_billing.csv')
    billing = s05_run(billing)
    billing = run(billing)
    
    print("\nSample contradictions:")
    contra = billing[billing['Charge_Cost_Contradiction']]
    if len(contra) > 0:
        print(contra[['Charge_Type', 'Charge_Type_Clean', 'Cost', 'Cost_Clean', 'Charge_Cost_Contradiction']].head(10).to_string(index=False))
