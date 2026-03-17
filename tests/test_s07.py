import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.chdir(os.path.join(os.path.dirname(__file__), '..'))

from scenarios.s07_duplicates import run as s07_run
from validations.v07_duplicates import validate as v07_validate
import pandas as pd

billing = pd.read_csv('data/raw/usage_billing.csv')
billing = s07_run(billing)
print()
v07_validate(billing)
