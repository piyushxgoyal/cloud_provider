import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.chdir(os.path.join(os.path.dirname(__file__), '..'))

from scenarios.s03_sku import run as s03_run
from validations.v03_sku import validate as v03_validate
import pandas as pd

billing = pd.read_csv('data/raw/usage_billing.csv')
billing = s03_run(billing)
print()
v03_validate(billing)
