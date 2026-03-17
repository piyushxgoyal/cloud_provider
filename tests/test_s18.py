import sys, os
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scenarios.s18_department import run as s18_run
from validations.v18_department import validate as v18_validate

def main():
    print("Loading usage_billing.csv...")
    df = pd.read_csv('data/raw/usage_billing.csv')
    df = s18_run(df)
    v18_validate(df)
    
    print("\nSample Data (Unknown Department):")
    cols = ['Department', 'Dept_Clean', 'Project', 'Project_Clean', 'Is_Unknown_Dept', 'Is_Invalid_Combo']
    unknown = df[df['Is_Unknown_Dept']]
    if len(unknown) > 0:
        print(unknown[cols].head(3).to_string(index=False))

    print("\nSample Data (Invalid Combos):")
    invalid = df[df['Is_Invalid_Combo']]
    if len(invalid) > 0:
        print(invalid[cols].head(3).to_string(index=False))

if __name__ == '__main__':
    main()
