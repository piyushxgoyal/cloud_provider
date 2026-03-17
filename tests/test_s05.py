import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.chdir(os.path.join(os.path.dirname(__file__), '..'))

from scenarios.s05_cost import run as s05_run
from validations.v05_cost import validate as v05_validate
import pandas as pd

billing = pd.read_csv('data/raw/usage_billing.csv')
billing = s05_run(billing)
print()
v05_validate(billing)
