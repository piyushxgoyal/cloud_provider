import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.chdir(os.path.join(os.path.dirname(__file__), '..'))

from scenarios.s06_region import run as s06_run
from validations.v06_region import validate as v06_validate
import pandas as pd

billing = pd.read_csv('data/raw/usage_billing.csv')
billing = s06_run(billing)
print()
v06_validate(billing)
