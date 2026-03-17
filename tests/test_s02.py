import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.chdir(os.path.join(os.path.dirname(__file__), '..'))

from scenarios.s02_timestamp import run as s02_run
from validations.v02_timestamp import validate as v02_validate
import pandas as pd

billing = pd.read_csv('data/raw/usage_billing.csv')
billing = s02_run(billing)
print()
v02_validate(billing)
