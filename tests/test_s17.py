import sys, os
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scenarios.s17_purchase_type import run as s17_run
from validations.v17_purchase_type import validate as v17_validate

def main():
    print("Loading usage_billing.csv...")
    df = pd.read_csv('data/raw/usage_billing.csv')
    df = s17_run(df)
    v17_validate(df)
    
    print("\nSample Data (Mismatches Fixed):")
    cols = ['Usage_ID', 'Purchase_Type', 'Purchase_Type_Clean', 'Purchase_Type_Mismatch']
    mismatches = df[df['Purchase_Type_Mismatch']]
    print(mismatches[cols].head(10).to_string(index=False))

if __name__ == '__main__':
    main()
