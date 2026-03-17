import sys, os
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scenarios.s15_fx import run as s15_run
from validations.v15_fx import validate as v15_validate

def main():
    print("Loading usage_billing.csv...")
    df = pd.read_csv('data/raw/usage_billing.csv')
    df = s15_run(df)
    v15_validate(df)
    
    print("\nSample Data (Inverted Fixes):")
    cols = ['Usage_ID', 'Cost', 'Cost_Clean', 'Currency_Clean', 'FX_Rate', 'FX_Rate_Clean', 'Cost_USD']
    inverted = df[df['FX_Wrong_Direction']]
    print(inverted[cols].head(5).to_string(index=False))

    print("\nSample Data (Missing FX Fixed):")
    missing = df[df['FX_Missing']]
    print(missing[cols].head(5).to_string(index=False))

if __name__ == '__main__':
    main()
