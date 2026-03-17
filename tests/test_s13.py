import sys, os
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scenarios.s13_incidents import run as s13_run
from validations.v13_incidents import validate as v13_validate

def main():
    print("Loading incidents.csv...")
    df = pd.read_csv('data/raw/incidents.csv')
    df = s13_run(df)
    v13_validate(df)

if __name__ == '__main__':
    main()
