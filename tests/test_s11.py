import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.chdir(os.path.join(os.path.dirname(__file__), '..'))

from scenarios.s01_account_id import run as s01_run
from scenarios.s11_resource import run as s11_run
from validations.v11_resource import validate as v11_validate
import pandas as pd

billing = pd.read_csv('data/raw/usage_billing.csv')
billing = s01_run(billing)
billing = s11_run(billing)
print()
v11_validate(billing)
