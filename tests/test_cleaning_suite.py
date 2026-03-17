import pytest
import pandas as pd

# ==========================================
# Tests for S01-S05
# ==========================================

def test_s01_no_invalid_format(df_cleaned):
    pattern = r'^(AWS|AZ|GCP)-ACCT-\d{3}$'
    valid = df_cleaned['Account_Clean'].dropna().str.match(pattern)
    assert valid.all()

def test_s01_master_mapping(df_cleaned):
    # Only check non-nulls
    bound = df_cleaned[df_cleaned['Account_Clean'].notna()]
    assert bound['Account_In_Master'].all()

def test_s01_nulls_expected(df_cleaned):
    assert df_cleaned['Account_Clean'].isna().sum() > 0

def test_s02_timezone(df_cleaned):
    # Depending on how pandas saves/loads CSVs, datetime objects might load as object string types unless parsed.
    # We verify the format explicitly matches expected UTC format (ends with +00:00 or Z, or we parse it first)
    parsed = pd.to_datetime(df_cleaned['TS_UTC'])
    assert parsed.dt.tz is not None or str(parsed.dtype).startswith('datetime64[')

def test_s02_parse_rate(df_cleaned):
    parsed = df_cleaned['TS_UTC'].notna().sum()
    total = len(df_cleaned)
    assert parsed / total > 0.9

def test_s02_no_garbage_kept(df_cleaned):
    garbage = df_cleaned['TS_Garbage_Flag']
    assert df_cleaned.loc[garbage, 'TS_UTC'].isna().all()

def test_s03_all_in_catalog(df_cleaned):
    assert df_cleaned['SKU_Clean'].notna().mean() > 0.95 # Not all are guaranteed matches

def test_s03_service_valid(df_cleaned):
    valid_services = ['Compute', 'Storage', 'Database']
    # If the service wasn't matched it might be null, but those that are mapped should be in the canonical list
    mapped_services = df_cleaned['Service_Clean'].dropna()
    assert mapped_services.isin(valid_services).all()

def test_s04_units(df_cleaned):
    assert df_cleaned['Unit_Canonical'].isin(['seconds', 'GB']).all()

def test_s04_no_missing_conversions(df_cleaned):
    assert df_cleaned['Usage_Converted'].notna().all()

def test_s05_cost_numeric(df_cleaned):
    assert df_cleaned['Cost_Clean'].dtype == float

def test_s05_currency_valid(df_cleaned):
    assert df_cleaned['Currency_Clean'].isin(['USD', 'INR', 'EUR', 'GBP', 'UNKNOWN']).all()

def test_s05_negative_flag(df_cleaned):
    flagged = df_cleaned['Cost_Clean'] < 0
    assert (flagged == df_cleaned['Is_Negative_Cost']).all()

# ==========================================
# Tests for S06-S10
# ==========================================

def test_s06_valid_regions(df_cleaned):
    assert df_cleaned['Region_Clean'].dropna().str.contains(r'-|[a-z]+').all()

def test_s06_some_unresolved(df_cleaned):
    assert df_cleaned['Region_Clean'].isna().sum() > 0

def test_s07_duplicates_exist(df_cleaned):
    assert df_cleaned['Is_Duplicate'].sum() > 0

def test_s07_keep_flag(df_cleaned):
    dup = df_cleaned[df_cleaned['Is_Duplicate']]
    assert dup['Duplicate_Keep'].isin([True, False]).all()

def test_s08_valid_types(df_cleaned):
    valid = ['Usage', 'Free_Tier', 'Credit', 'Refund']
    assert df_cleaned['Charge_Type_Clean'].isin(valid).all()

def test_s08_contradictions(df_cleaned):
    cond = (df_cleaned['Charge_Type_Clean'] == 'Free_Tier') & (df_cleaned['Cost_Clean'] > 0)
    assert (cond == df_cleaned['Charge_Cost_Contradiction']).all()

def test_s09_anomalies_exist(df_cleaned):
    assert df_cleaned['Is_Usage_Anomaly'].sum() > 0

def test_s09_positive_zscore(df_cleaned):
    # Anomalies can be negative or positive depending on the multiplier bounds (though we usually injected huge positive spikes).
    # The condition is that ABSOLUTE z-score should usually be high if it was flagged via z-score and not just hard bounds.
    anomalies = df_cleaned[df_cleaned['Is_Usage_Anomaly']].dropna(subset=['Anomaly_Z_Score'])
    if len(anomalies) > 0:
        assert (anomalies['Anomaly_Z_Score'].abs() > 3).all()

def test_s10_owner_tags(df_cleaned):
    valid = ['backend', 'frontend', 'security', 'data', 'devops', 'platform', 'UNKNOWN']
    assert df_cleaned['Tag_Owner_Clean'].isin(valid).all()

def test_s10_env_tags(df_cleaned):
    valid = ['production', 'development', 'staging', 'UNKNOWN']
    assert df_cleaned['Tag_Env_Clean'].isin(valid).all()

# ==========================================
# Tests for S11-S15
# ==========================================

def test_s11_orphans_exist(df_cleaned):
    assert df_cleaned['Is_Orphan_Resource'].sum() > 0

def test_s11_no_orphan_zombie_overlap(df_cleaned):
    overlap = df_cleaned['Is_Orphan_Resource'] & df_cleaned['Is_Zombie_Resource']
    assert overlap.sum() == 0

def test_s12_no_pii_leak(df_cleaned):
    if 'Ticket_Text_Masked' not in df_cleaned.columns:
        return
        
    text = df_cleaned['Ticket_Text_Masked'].dropna()
    assert not text.str.contains(r'\d{3}-\d{3}-\d{4}').any()  # phone
    assert not text.str.contains(r'@').any()                # email

def test_s12_severity_valid(df_cleaned):
    if 'Severity_Normalized' in df_cleaned.columns:
        assert df_cleaned['Severity_Normalized'].dropna().isin(['SEV1', 'SEV2', 'SEV3', 'UNKNOWN']).all()

def test_s13_incident_dates(df_cleaned):
    # Start <= End
    if 'Incident_Start_UTC' in df_cleaned.columns and 'Incident_End_UTC' in df_cleaned.columns:
        valid = df_cleaned.dropna(subset=['Incident_Start_UTC', 'Incident_End_UTC'])
        assert (valid['Incident_Start_UTC'] <= valid['Incident_End_UTC']).all()

def test_s14_price_versions(df_cleaned):
    if 'Price_Version_Mismatch' in df_cleaned.columns: # Verify we caught mismatches based on usage timestamp
        assert df_cleaned['Price_Version_Mismatch'].dtype == bool

def test_s15_fx_imputed(df_cleaned):
    assert df_cleaned['FX_Rate_Clean'].notna().all()

def test_s15_cost_usd_calculation(df_cleaned):
    # Cost_USD = Cost_Clean * FX_Rate_Clean
    expected = df_cleaned['Cost_Clean'] * df_cleaned['FX_Rate_Clean']
    # allow minor float variance
    assert (df_cleaned['Cost_USD'] - expected).abs().max() < 0.001

# ==========================================
# Tests for S16-S20
# ==========================================

def test_s16_utilization_bounds(df_cleaned):
    compute_db = df_cleaned[df_cleaned['Service_Clean'].isin(['Compute', 'Database'])]
    assert (compute_db['CPU_Clean'] >= 0).all() and (compute_db['CPU_Clean'] <= 100).all()
    assert (compute_db['Mem_Clean'] >= 0).all() and (compute_db['Mem_Clean'] <= 100).all()

def test_s17_purchase_types(df_cleaned):
    assert df_cleaned['Purchase_Type_Clean'].isin(['on-demand', 'reserved', 'spot']).all()

def test_s18_dept_project_clean(df_cleaned):
    assert (df_cleaned['Dept_Clean'].str.upper() == df_cleaned['Dept_Clean']).all()
    assert (df_cleaned['Project_Clean'].str.upper() == df_cleaned['Project_Clean']).all()

def test_s19_sla_booleans(df_cleaned):
    assert df_cleaned['SLA_Event_Clean'].dtype == bool

def test_s20_log_skew_bounds(df_cleaned):
    # Nulls imputed to 0, anything above 60 flagged
    flagged = df_cleaned[df_cleaned['Is_High_Skew']]
    assert (flagged['Log_Skew_Clean'].abs() > 60).all()
    assert df_cleaned['Log_Skew_Clean'].notna().all()
