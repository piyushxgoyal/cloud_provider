import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.chdir(os.path.join(os.path.dirname(__file__), '..'))

from scenarios.s12_security import run as s12_run
from validations.v12_security import validate as v12_validate
import pandas as pd

tickets = pd.read_csv('data/raw/support_tickets.csv')
tickets = s12_run(tickets)
print()
v12_validate(tickets)
