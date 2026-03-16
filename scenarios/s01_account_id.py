"""
Scenario 01 — Account ID Normalization & Master Mapping
========================================================
Cleans Account_ID column:
  - Strip whitespace
  - Uppercase
  - Fix separators (underscores, double dashes → single dash)
  - Remove prefix issues
  - Validate against account_master.csv

Input:  dirty Account_ID (mixed case, whitespace, wrong separators)
Output: Account_Clean, Account_In_Master columns
"""

import pandas as pd
import re
import os


def load_master_accounts(data_dir='data/raw'):
    """Load canonical account IDs from account_master.csv."""
    master_df = pd.read_csv(os.path.join(data_dir, 'account_master.csv'))
    return set(master_df['Account_ID'].tolist()), master_df


def clean_account_id(val, master_accounts):
    """
    Normalize a single Account_ID value to canonical format.

    Canonical format: AWS-ACCT-XXX / AZ-ACCT-XXX / GCP-ACCT-XXX

    Handles:
      - lowercase:    aws-acct-001       → AWS-ACCT-001
      - whitespace:   '  AWS-ACCT-001 '  → AWS-ACCT-001
      - underscores:  AWS_ACCT_001       → AWS-ACCT-001
      - double dash:  AWS--ACCT-001      → AWS-ACCT-001
      - missing prefix (partial): ACCT-001 → try to match in master
    """
    if pd.isna(val) or str(val).strip() == '':
        return None

    val = str(val).strip().upper()              # trim + uppercase
    val = re.sub(r'[_]+', '-', val)             # underscores → dash
    val = re.sub(r'-{2,}', '-', val)            # collapse multiple dashes

    # Check if it matches a known pattern
    # AWS-ACCT-XXX, AZ-ACCT-XXX, GCP-ACCT-XXX
    m = re.match(r'^(AWS|AZ|GCP)-ACCT-(\d{3})$', val)
    if m:
        canonical = f"{m.group(1)}-ACCT-{m.group(2)}"
        return canonical

    # Handle missing cloud prefix: ACCT-XXX → try all prefixes
    m = re.match(r'^ACCT-(\d{3})$', val)
    if m:
        num = m.group(1)
        for prefix in ['AWS', 'AZ', 'GCP']:
            candidate = f"{prefix}-ACCT-{num}"
            if candidate in master_accounts:
                return candidate
        return None  # unresolvable

    return None  # unrecognized format


def run(df, data_dir='data/raw'):
    """
    Execute S01 cleaning on the dataframe.

    Args:
        df: DataFrame with 'Account_ID' column
        data_dir: path to raw data directory

    Returns:
        df with new columns: Account_Clean, Account_In_Master
    """
    master_accounts, master_df = load_master_accounts(data_dir)

    # Clean account IDs
    df['Account_Clean'] = df['Account_ID'].apply(
        lambda x: clean_account_id(x, master_accounts)
    )

    # Flag: is the cleaned account in the master set?
    df['Account_In_Master'] = df['Account_Clean'].apply(
        lambda x: (x in master_accounts) if pd.notna(x) else False
    )

    print("✅ S01 — Account ID Normalization complete")
    print(f"   Rows cleaned:     {(df['Account_ID'] != df['Account_Clean']).sum()}")
    print(f"   Unresolved → null: {df['Account_Clean'].isna().sum()}")
    print(f"   In master:        {df['Account_In_Master'].sum()}")

    return df


if __name__ == '__main__':
    billing = pd.read_csv('data/raw/usage_billing.csv')
    billing = run(billing)
    print(billing[['Account_ID', 'Account_Clean', 'Account_In_Master']].sample(10).to_string(index=False))
