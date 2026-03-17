"""
Scenario 10 — Tag Normalization
================================
Normalizes resource tags for Owner and Environment.
Handles abbreviations, case variations, and aliases.

Input:  Tag_Owner, Tag_Env
Output: Tag_Owner_Clean, Tag_Env_Clean
"""

import pandas as pd


# ── Canonical Mappings ──────────────────────────────────────

OWNER_MAP = {
    # Backend
    'be': 'backend', 'backend': 'backend', 'back-end': 'backend',
    # Frontend
    'fe': 'frontend', 'frontend': 'frontend', 'front-end': 'frontend',
    # Security
    'sec': 'security', 'security': 'security', 'sec-team': 'security',
    # Data
    'data': 'data', 'data-team': 'data',
    # DevOps
    'devops': 'devops', 'dev-ops': 'devops',
    # Platform
    'platform': 'platform', 'plat': 'platform',
}

ENV_MAP = {
    # Production
    'prod': 'production', 'production': 'production', 'prd': 'production',
    # Development
    'dev': 'development', 'development': 'development', 'develop': 'development',
    # Staging
    'stg': 'staging', 'staging': 'staging', 'stage': 'staging',
}


def clean_tag(val, mapping):
    """Normalize a tag using the provided mapping."""
    if pd.isna(val) or str(val).strip() == '':
        return 'unknown'
    
    clean_val = str(val).strip().lower()
    return mapping.get(clean_val, 'unknown')


def run(df, data_dir='data/raw'):
    """
    Execute S10 tag normalization.
    """
    df['Tag_Owner_Clean'] = df['Tag_Owner'].apply(lambda x: clean_tag(x, OWNER_MAP))
    df['Tag_Env_Clean']   = df['Tag_Env'].apply(lambda x: clean_tag(x, ENV_MAP))
    
    print("✅ S10 — Tag Normalization complete")
    
    owner_changed = (df['Tag_Owner'] != df['Tag_Owner_Clean']).sum()
    env_changed   = (df['Tag_Env'] != df['Tag_Env_Clean']).sum()
    
    print(f"   Owner labels normalized: {owner_changed}")
    print(f"   Env labels normalized:   {env_changed}")
    
    # Show value counts of canonicals to ensure clean distribution
    print(f"   Owner dist: {df['Tag_Owner_Clean'].value_counts().to_dict()}")
    print(f"   Env dist:   {df['Tag_Env_Clean'].value_counts().to_dict()}")

    return df

if __name__ == '__main__':
    billing = pd.read_csv('data/raw/usage_billing.csv')
    billing = run(billing)
    
    print("\nSample Owner normalizations:")
    changed = billing[billing['Tag_Owner'] != billing['Tag_Owner_Clean']]
    print(changed[['Tag_Owner', 'Tag_Owner_Clean']].drop_duplicates().head(10).to_string(index=False))
    
    print("\nSample Env normalizations:")
    changed_env = billing[billing['Tag_Env'] != billing['Tag_Env_Clean']]
    print(changed_env[['Tag_Env', 'Tag_Env_Clean']].drop_duplicates().head(10).to_string(index=False))
