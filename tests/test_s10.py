import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.chdir(os.path.join(os.path.dirname(__file__), '..'))

from scenarios.s10_tags import run as s10_run
from validations.v10_tags import validate as v10_validate
import pandas as pd

billing = pd.read_csv('data/raw/usage_billing.csv')
billing = s10_run(billing)
print()
v10_validate(billing)
