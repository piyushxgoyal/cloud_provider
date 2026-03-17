import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.chdir(os.path.join(os.path.dirname(__file__), '..'))

from scenarios.s03_sku import run as s03_run
from scenarios.s09_anomaly import run as s09_run
from validations.v09_anomaly import validate as v09_validate
import pandas as pd

billing = pd.read_csv('data/raw/usage_billing.csv')
billing = s03_run(billing)
billing = s09_run(billing)
print()
v09_validate(billing)
