import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.chdir(os.path.join(os.path.dirname(__file__), '..'))

from scenarios.s01_account_id import run as s01_run, load_master_accounts
from validations.v01_account_id import validate as v01_validate
import pandas as pd

billing = pd.read_csv('data/raw/usage_billing.csv')
billing = s01_run(billing)
print()
master_accounts, _ = load_master_accounts()
v01_validate(billing, master_accounts)
