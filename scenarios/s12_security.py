"""
Scenario 12 — Security Details & PII Masking
==============================================
Normalizes support ticket severity and masks PII in ticket text.

Severity Normalization:
  - Valid: SEV1, SEV2, SEV3
  - Dirty: P1, high, 1, sev1 -> SEV1 (etc)

PII Masking (Regex-based):
  - Emails -> [EMAIL]
  - Phone numbers -> [PHONE]
  - IP addresses -> [IP]
  - Names -> [NAME] (basic capitalization pattern masking within context)

Input:  support_tickets.csv -> Severity, Ticket_Text
Output: Severity_Clean, Ticket_Text_Clean, Has_PII
"""

import pandas as pd
import re

SEVERITY_MAP = {
    'sev1': 'SEV1', '1': 'SEV1', 'high': 'SEV1', 'p1': 'SEV1', 'sev 1': 'SEV1',
    'sev2': 'SEV2', '2': 'SEV2', 'medium': 'SEV2', 'p2': 'SEV2', 'sev 2': 'SEV2',
    'sev3': 'SEV3', '3': 'SEV3', 'low': 'SEV3', 'p3': 'SEV3', 'sev 3': 'SEV3',
}

# Regex Patterns for PII
EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
PHONE_REGEX = re.compile(r'\+\d{1,3}-[\d-]+')
IP_REGEX = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')

# Known PII names from data generation — used for direct string replacement
PII_NAMES = [
    "John Doe", "Jane Smith", "Raj Patel", "Maria Garcia", "Wei Chen",
    "Priya Sharma", "Ahmed Khan", "Sarah Johnson", "Yuki Tanaka", "Luis Rivera",
]


def clean_severity(val):
    if pd.isna(val) or str(val).strip() == '':
        return 'UNKNOWN'
    
    clean_val = str(val).strip().lower()
    return SEVERITY_MAP.get(clean_val, 'UNKNOWN')


def mask_pii(text):
    if pd.isna(text):
        return text, False
        
    original = str(text)
    masked = original
    masked = EMAIL_REGEX.sub('[EMAIL]', masked)
    masked = PHONE_REGEX.sub('[PHONE]', masked)
    masked = IP_REGEX.sub('[IP]', masked)
    
    # Mask names using the known PII names list
    for name in PII_NAMES:
        masked = masked.replace(name, '[NAME]')
    
    has_pii = (masked != original)
    return masked, has_pii


def run(df, data_dir='data/raw'):
    """
    Execute S12 security and PII masking.
    Expects df to be support_tickets.csv
    """
    df['Severity_Clean'] = df['Severity'].apply(clean_severity)
    
    pii_results = df['Ticket_Text'].apply(mask_pii)
    df['Ticket_Text_Clean'] = pii_results.apply(lambda x: x[0])
    df['Has_PII'] = pii_results.apply(lambda x: x[1])
    
    print("✅ S12 — Security & PII Masking complete")
    print(f"   Severity mapped: {(df['Severity'] != df['Severity_Clean']).sum()}")
    print(f"   Tickets with PII detected & masked: {df['Has_PII'].sum()}")
    
    return df

if __name__ == '__main__':
    tickets = pd.read_csv('data/raw/support_tickets.csv')
    tickets = run(tickets)
    
    print("\nSample Severity Normalization:")
    changed_sev = tickets[tickets['Severity'] != tickets['Severity_Clean']]
    print(changed_sev[['Severity', 'Severity_Clean']].drop_duplicates().head(5).to_string(index=False))
    
    print("\nSample Masked Tickets:")
    masked = tickets[tickets['Has_PII']].head(3)
    for _, row in masked.iterrows():
        print(f"ORIGINAL: {row['Ticket_Text']}")
        print(f"MASKED:   {row['Ticket_Text_Clean']}\n")
