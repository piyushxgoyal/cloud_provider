"""
Validation 11 — Resource ID Validation
========================================
Validates the output of S11 (Resource ID Standardization).
Checks: flag generation counts and logical consistency.
"""

import pandas as pd


def validate(df):
    """
    Run all validation checks for S11.
    
    Returns:
        (passed, failed, results) tuple
    """
    sep = "=" * 55
    results = {}
    
    # ── 1. Orphan Detection Rate ──────────────────────────────
    print(f"\n{sep}")
    print("  1. ORPHAN DETECTION")
    print(sep)
    
    orphans = df['Is_Orphan_Resource'].sum()
    print(f"  Orphan rows flagged: {orphans}")
    print(f"  Expected ~300-600")
    
    results['Detected orphans bounds'] = 250 <= orphans <= 650
    _status(results, 'Detected orphans bounds')
    
    # ── 2. Zombie Detection Rate ──────────────────────────────
    print(f"\n{sep}")
    print("  2. ZOMBIE DETECTION")
    print(sep)
    
    zombies = df['Is_Zombie_Resource'].sum()
    print(f"  Zombie/Terminated rows flagged: {zombies}")
    print(f"  Expected ~100-300 (1% zombie/terminated generation)")
    
    results['Detected zombies ~100-300'] = 50 <= zombies <= 400
    _status(results, 'Detected zombies ~100-300')
    
    # ── 3. Cloud Mismatch Rate ────────────────────────────────
    print(f"\n{sep}")
    print("  3. CLOUD MISMATCH DETECTION")
    print(sep)
    
    mismatches = df['Resource_Cloud_Mismatch'].sum()
    print(f"  Cloud Mismatch rows flagged: {mismatches}")
    print(f"  Expected ~300-600")
    
    results['Detected mismatches bounds'] = 250 <= mismatches <= 650
    _status(results, 'Detected mismatches bounds')
    
    # ── 4. Logical Consistency ────────────────────────────────
    print(f"\n{sep}")
    print("  4. LOGICAL CONSISTENCY")
    print(sep)
    
    # A zombie row cannot be an orphan (zombies exist in inventory)
    orphan_zombies = df[df['Is_Orphan_Resource'] & df['Is_Zombie_Resource']]
    print(f"  Rows flagged as both Orphan and Zombie: {len(orphan_zombies)}")
    
    results['Mutually exclusive orphan/zombie'] = len(orphan_zombies) == 0
    _status(results, 'Mutually exclusive orphan/zombie')
    
    # ── Summary ───────────────────────────────────────────────
    print(f"\n{sep}")
    print("  SUMMARY — S11 VALIDATION")
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
    from scenarios.s01_account_id import run as s01_run
    from scenarios.s11_resource import run as s11_run
    
    billing = pd.read_csv('data/raw/usage_billing.csv')
    billing = s01_run(billing)
    billing = s11_run(billing)
    validate(billing)
