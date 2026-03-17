"""
Validation 12 — Security Details & PII Masking
================================================
Validates S12 (Security & PII Masking).
Checks canonical severity output and verifies PII leakage handling.
"""

import pandas as pd
import re

def validate(df):
    """
    Run all validation checks for S12.
    """
    sep = "=" * 55
    results = {}
    
    # ── 1. Canonical Severity ─────────────────────────────────
    print(f"\n{sep}")
    print("  1. CANONICAL SEVERITY")
    print(sep)
    
    valid_sev = {'SEV1', 'SEV2', 'SEV3'}
    bad_sev = df[~df['Severity_Clean'].isin(valid_sev)]
    
    print(f"  Invalid severity values: {len(bad_sev)}")
    print(f"  Distribution: {df['Severity_Clean'].value_counts().to_dict()}")
    
    results['All Severity tags canonical'] = len(bad_sev) == 0
    _status(results, 'All Severity tags canonical')
    
    # ── 2. Spot-check Severity Mappings ──────────────────────
    print(f"\n{sep}")
    print("  2. SPOT-CHECK SEVERITY MAPPING")
    print(sep)
    
    from scenarios.s12_security import clean_severity
    
    tests = [
        ('sev1', 'SEV1'),
        ('SEV1', 'SEV1'),
        ('high', 'SEV1'),
        ('1', 'SEV1'),
        ('P2', 'SEV2'),
        ('medium', 'SEV2'),
        ('low', 'SEV3')
    ]
    
    spot_ok = True
    for dirty, expected in tests:
        res = clean_severity(dirty)
        if res != expected:
            print(f"  ✗ '{dirty}' mapped to '{res}', expected '{expected}'")
            spot_ok = False
            
    print(f"  Tested {len(tests)} variants.")
    results['Severity spot-checks pass'] = spot_ok
    _status(results, 'Severity spot-checks pass')
    
    # ── 3. PII Leakage Check ──────────────────────────────────
    print(f"\n{sep}")
    print("  3. PII LEAKAGE IN CLEAN TEXT")
    print(sep)
    
    email_regex = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
    ip_regex = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
    phone_regex = re.compile(r'\+\d{1,3}-[\d-]+')
    
    leaked_emails = df[df['Ticket_Text_Clean'].str.contains(email_regex, na=False)]
    leaked_ips = df[df['Ticket_Text_Clean'].str.contains(ip_regex, na=False)]
    leaked_phones = df[df['Ticket_Text_Clean'].str.contains(phone_regex, na=False)]
    
    print(f"  Leaked Emails: {len(leaked_emails)}")
    print(f"  Leaked IPs:    {len(leaked_ips)}")
    print(f"  Leaked Phones: {len(leaked_phones)}")
    
    results['No leaked Emails/IPs/Phones'] = (len(leaked_emails) == 0) and (len(leaked_ips) == 0) and (len(leaked_phones) == 0)
    _status(results, 'No leaked Emails/IPs/Phones')
    
    # ── 4. Has_PII Flag Consistency ───────────────────────────
    print(f"\n{sep}")
    print("  4. PII FLAG CONSISTENCY")
    print(sep)
    
    # Ensure that if the text changed, Has_PII is true
    df['Text_Changed'] = df['Ticket_Text'] != df['Ticket_Text_Clean']
    inconsistent = df[df['Has_PII'] != df['Text_Changed']]
    
    print(f"  Rows with inconsistent change flag: {len(inconsistent)}")
    
    results['Has_PII flag accurate'] = len(inconsistent) == 0
    _status(results, 'Has_PII flag accurate')

    # ── Summary ───────────────────────────────────────────────
    print(f"\n{sep}")
    print("  SUMMARY — S12 VALIDATION")
    print(sep)
    
    passed = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if not v)
    
    for check, ok in results.items():
        sym = "✅ PASS" if ok else "❌ FAIL"
        print(f"  {sym}  {check}")
    
    print(f"\n  Passed: {passed}/{len(results)}")
    print(f"  Failed: {failed}/{len(results)}")
    
    return passed, failed, results

def _status(results, key):
    sym = "✓" if results[key] else "✗ FAIL"
    print(f"  {sym}")

if __name__ == '__main__':
    import sys
    sys.path.insert(0, '.')
    from scenarios.s12_security import run as s12_run
    
    tickets = pd.read_csv('data/raw/support_tickets.csv')
    tickets = s12_run(tickets)
    validate(tickets)
