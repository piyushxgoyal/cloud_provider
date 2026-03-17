import sys, os
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scenarios.s14_price_version import run as s14_run
from validations.v14_price_version import validate as v14_validate

def main():
    print("Loading usage_billing.csv...")
    df = pd.read_csv('data/raw/usage_billing.csv')
    df = s14_run(df)
    v14_validate(df)
    
    print("\nSample Data (Price Version Fixes):")
    cols = ['Timestamp', 'TS_UTC', 'Price_Version', 'Expected_Price_Version', 'Price_Version_Clean', 'Price_Version_Mismatch']
    mismatched = df[df['Price_Version_Mismatch'] & df['Price_Version'].notna()]
    print(mismatched[cols].head(10).to_string(index=False))

if __name__ == '__main__':
    main()
