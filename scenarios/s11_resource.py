"""
Scenario 11 — Resource ID Standardization
==========================================
Validates Resource_ID against the resource_inventory.csv.
Flags:
  - Orphan resources (not in inventory)
  - Zombie/Terminated resources (in inventory but not active)
  - Cloud Mismatch (resource belongs to a different cloud than the account)

Input:  Resource_ID, Account_Clean (from S01, or fallback to Account_ID)
Output: Is_Orphan_Resource, Is_Zombie_Resource, Resource_Cloud_Mismatch
"""

import pandas as pd
import os

def load_inventory(data_dir='data/raw'):
    inv_path = os.path.join(data_dir, 'resource_inventory.csv')
    return pd.read_csv(inv_path)

def load_accounts(data_dir='data/raw'):
    acct_path = os.path.join(data_dir, 'account_master.csv')
    return pd.read_csv(acct_path)

def run(df, data_dir='data/raw'):
    """
    Execute S11 resource validation.
    """
    inv_df = load_inventory(data_dir)
    acct_df = load_accounts(data_dir)
    
    # 1. Map Account to Cloud Provider
    acct_to_cloud = acct_df.set_index('Account_ID')['Cloud_Provider'].to_dict()
    
    # We use Account_Clean if available, else Account_ID
    acct_col = 'Account_Clean' if 'Account_Clean' in df.columns else 'Account_ID'
    df['_temp_billing_cloud'] = df[acct_col].map(acct_to_cloud)
    
    # 2. Extract Inventory Info
    # For fast lookup
    inv_status = inv_df.set_index('Resource_ID')['Status'].to_dict()
    inv_cloud = inv_df.set_index('Resource_ID')['Cloud_Provider'].to_dict()
    
    # 3. Apply Checks
    df['Is_Orphan_Resource'] = ~df['Resource_ID'].isin(inv_status.keys())
    
    def check_zombie(res_id):
        status = inv_status.get(res_id, 'unknown')
        return status in ['zombie', 'terminated']
        
    df['Is_Zombie_Resource'] = df['Resource_ID'].apply(check_zombie)
    
    def check_mismatch(row):
        res_id = row['Resource_ID']
        expected_cloud = row['_temp_billing_cloud']
        actual_cloud = inv_cloud.get(res_id)
        if pd.isna(actual_cloud):
            # It's an orphan, but we can also check prefix as a secondary check, 
            # though usually prefix mismatch means we just flag it if actual != expected.
            # We'll just flag if actual_cloud and expected don't match (and it IS in inventory).
            # OR we can guess from prefix: aws- -> AWS, az- -> Azure, gcp- -> GCP
            prefix = str(res_id).split('-')[0].lower()
            if prefix == 'aws' and expected_cloud != 'AWS': return True
            if prefix == 'az' and expected_cloud != 'Azure': return True
            if prefix == 'gcp' and expected_cloud != 'GCP': return True
            return False
        return actual_cloud != expected_cloud

    df['Resource_Cloud_Mismatch'] = df.apply(check_mismatch, axis=1)
    
    # Clean up temp col
    df.drop(columns=['_temp_billing_cloud'], inplace=True, errors='ignore')
    
    print("✅ S11 — Resource ID Standardization complete")
    print(f"   Orphan Resources:  {df['Is_Orphan_Resource'].sum()}")
    print(f"   Zombie/Terminated: {df['Is_Zombie_Resource'].sum()}")
    print(f"   Cloud Mismatches:  {df['Resource_Cloud_Mismatch'].sum()}")
    
    return df

if __name__ == '__main__':
    # Need S01 for Account_Clean mapping
    import sys
    sys.path.insert(0, '.')
    from scenarios.s01_account_id import run as s01_run
    
    billing = pd.read_csv('data/raw/usage_billing.csv')
    billing = s01_run(billing)
    billing = run(billing)
    
    print("\nSample Orphans:")
    orphans = billing[billing['Is_Orphan_Resource']]
    if len(orphans) > 0:
        print(orphans[['Usage_ID', 'Account_Clean', 'Resource_ID', 'Is_Orphan_Resource']].head(5).to_string(index=False))
        
    print("\nSample Zombies:")
    zombies = billing[billing['Is_Zombie_Resource']]
    if len(zombies) > 0:
        print(zombies[['Usage_ID', 'Account_Clean', 'Resource_ID', 'Is_Zombie_Resource']].head(5).to_string(index=False))
