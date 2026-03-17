import pytest
import pandas as pd
import os

@pytest.fixture(scope="session")
def df_cleaned():
    """
    Loads the fully cleaned dataset produced at the end of S01-S20.
    In a real CI pipeline, this fixture might run the orchestrator `pipeline.py`
    and yield the resulting dataframe. Here, since Phase 3 is done, we just
    load the saved artifact to test its integrity.
    """
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'cleaned', 'cleaned_usage_billing.csv')
    return pd.read_csv(file_path)
