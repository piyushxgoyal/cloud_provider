import sys, os
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scenarios.s20_log_skew import run as s20_run
from validations.v20_log_skew import validate as v20_validate

def main():
    print("Loading usage_billing.csv...")
    df = pd.read_csv('data/raw/usage_billing.csv')
    df = s20_run(df)
    v20_validate(df)
    
    print("\nSample Data (High Skew Flagged):")
    cols = ['Usage_ID', 'Log_Skew_Seconds', 'Log_Skew_Clean', 'Is_High_Skew']
    high = df[df['Is_High_Skew']]
    if len(high) > 0:
        print(high[cols].head(5).to_string(index=False))
        
    print("\nSample Data (Nulls Imputed):")
    nulls_orig = df[df['Log_Skew_Seconds'].isna()]
    if len(nulls_orig) > 0:
        print(nulls_orig[cols].head(5).to_string(index=False))

if __name__ == '__main__':
    main()
