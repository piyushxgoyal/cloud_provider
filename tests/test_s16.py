import sys, os
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scenarios.s16_utilization import run as s16_run
from validations.v16_utilization import validate as v16_validate

def main():
    print("Loading usage_billing.csv...")
    df = pd.read_csv('data/raw/usage_billing.csv')
    df = s16_run(df)
    v16_validate(df)
    
    print("\nSample Data (Idle):")
    cols = ['Service_Clean', 'CPU_Util', 'CPU_Clean', 'Memory_Util', 'Mem_Clean', 'Is_Idle', 'Is_Overutilized']
    print(df[df['Is_Idle']][cols].head(3).to_string(index=False))

    print("\nSample Data (Overutilized):")
    print(df[df['Is_Overutilized']][cols].head(3).to_string(index=False))

    print("\nSample Data (Storage):")
    storage = df[df['Service_Clean'].str.lower() == 'storage']
    print(storage.head(3)[cols].to_string(index=False))

if __name__ == '__main__':
    main()
