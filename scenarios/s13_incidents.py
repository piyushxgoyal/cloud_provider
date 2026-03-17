"""
Scenario 13 — Incident Normalization
====================================
Normalizes data within `incidents.csv`.
"""
import pandas as pd
from scenarios.s02_timestamp import clean_timestamp, VALID_TS_MIN, VALID_TS_MAX
import re

def clean_sla(val):
    if pd.isna(val):
        return pd.NA
    s = str(val).strip().lower()
    if s in ('true', '1', 'yes'):
        return True
    if s in ('false', '0', 'no'):
        return False
    return pd.NA

def run(df):
    df['Incident_Start_UTC'] = df['Incident_Start'].apply(clean_timestamp)
    df.loc[(df['Incident_Start_UTC'] < VALID_TS_MIN) | (df['Incident_Start_UTC'] > VALID_TS_MAX), 'Incident_Start_UTC'] = pd.NaT
    
    df['Incident_End_UTC'] = df['Incident_End'].apply(clean_timestamp)
    df.loc[(df['Incident_End_UTC'] < VALID_TS_MIN) | (df['Incident_End_UTC'] > VALID_TS_MAX), 'Incident_End_UTC'] = pd.NaT
    
    # Swap if start is after end
    mask = df['Incident_End_UTC'] < df['Incident_Start_UTC']
    df.loc[mask, ['Incident_Start_UTC', 'Incident_End_UTC']] = df.loc[mask, ['Incident_End_UTC', 'Incident_Start_UTC']].values
    
    df['SLA_Breach_Clean'] = df['SLA_Breach'].apply(clean_sla)
    
    print("✅ S13 — Incident Normalization complete")
    print(f"   Original rows:            {len(df)}")
    print(f"   Valid Start TS:           {df['Incident_Start_UTC'].notna().sum()}")
    print(f"   Valid End TS:             {df['Incident_End_UTC'].notna().sum()}")
    print(f"   Cleaned SLABreach True:   {(df['SLA_Breach_Clean'] == True).sum()}")
    print(f"   Cleaned SLABreach False:  {(df['SLA_Breach_Clean'] == False).sum()}")
    
    return df
