import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.chdir(os.path.join(os.path.dirname(__file__), '..'))

from scenarios.s05_cost import run as s05_run
from scenarios.s08_charge_type import run as s08_run
from validations.v08_charge_type import validate as v08_validate
import pandas as pd

billing = pd.read_csv('data/raw/usage_billing.csv')
billing = s05_run(billing)
billing = s08_run(billing)
print()
v08_validate(billing)
