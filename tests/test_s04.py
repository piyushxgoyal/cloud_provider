import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.chdir(os.path.join(os.path.dirname(__file__), '..'))

from scenarios.s04_unit import run as s04_run
from validations.v04_unit import validate as v04_validate
import pandas as pd

billing = pd.read_csv('data/raw/usage_billing.csv')
billing = s04_run(billing)
print()
v04_validate(billing)
