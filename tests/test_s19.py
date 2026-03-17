import sys, os
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scenarios.s19_sla import run as s19_run
from validations.v19_sla import validate as v19_validate

def main():
    print("Loading usage_billing.csv...")
    df = pd.read_csv('data/raw/usage_billing.csv')
    df = s19_run(df)
    v19_validate(df)
    
    print("\nSample Data (Messy SLA Fixed):")
    cols = ['Usage_ID', 'SLA_Event', 'SLA_Event_Clean', 'SLA_Messy_Flag']
    messy = df[df['SLA_Messy_Flag']]
    if len(messy) > 0:
        print(messy[cols].head(5).to_string(index=False))

if __name__ == '__main__':
    main()
