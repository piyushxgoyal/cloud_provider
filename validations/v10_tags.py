"""
Validation 10 — Tag Normalization Validation
==============================================
Validates the output of S10 (Tag Normalization).
Checks: canonical mapping completeness, zero unknown rate (if expected), and spot-mapping check.
"""

import pandas as pd


def validate(df):
    """
    Run all validation checks for S10.
    
    Returns:
        (passed, failed, results) tuple
    """
    sep = "=" * 55
    results = {}
    
    # ── 1. Canonical Tag Owner ────────────────────────────────
    print(f"\n{sep}")
    print("  1. CANONICAL TAG OWNER")
    print(sep)
    
    valid_owners = {'backend', 'frontend', 'security', 'data', 'devops', 'platform'}
    bad_owners = df[~df['Tag_Owner_Clean'].isin(valid_owners)]
    
    print(f"  Invalid owners found: {len(bad_owners)}")
    print(f"  Unique valid owners: {df['Tag_Owner_Clean'].nunique()}")
    
    results['All Owner tags canonical'] = len(bad_owners) == 0
    _status(results, 'All Owner tags canonical')
    
    # ── 2. Canonical Tag Env ──────────────────────────────────
    print(f"\n{sep}")
    print("  2. CANONICAL TAG ENV")
    print(sep)
    
    valid_envs = {'production', 'development', 'staging'}
    bad_envs = df[~df['Tag_Env_Clean'].isin(valid_envs)]
    
    print(f"  Invalid envs found: {len(bad_envs)}")
    print(f"  Unique valid envs: {df['Tag_Env_Clean'].nunique()}")
    
    results['All Env tags canonical'] = len(bad_envs) == 0
    _status(results, 'All Env tags canonical')
    
    # ── 3. Spot-check Owner Mappings ─────────────────────────
    print(f"\n{sep}")
    print("  3. SPOT-CHECK OWNER MAPPINGS")
    print(sep)
    
    from scenarios.s10_tags import clean_tag, OWNER_MAP
    
    owner_tests = [
        ('BE', 'backend'),
        ('Backend', 'backend'),
        ('sec-team', 'security'),
        ('PLATFORM', 'platform'),
        ('dev-ops', 'devops'),
        ('Data', 'data')
    ]
    
    owner_ok = True
    for dirty, expected in owner_tests:
        res = clean_tag(dirty, OWNER_MAP)
        if res != expected:
            print(f"  ✗ '{dirty}' mapped to '{res}', expected '{expected}'")
            owner_ok = False
            
    print(f"  Spot-check tested {len(owner_tests)} variants.")
    results['Spot-check Owners passed'] = owner_ok
    _status(results, 'Spot-check Owners passed')
    
    # ── 4. Spot-check Env Mappings ───────────────────────────
    print(f"\n{sep}")
    print("  4. SPOT-CHECK ENV MAPPINGS")
    print(sep)
    
    from scenarios.s10_tags import ENV_MAP
    
    env_tests = [
        ('prod', 'production'),
        ('PROD', 'production'),
        ('prd', 'production'),
        ('develop', 'development'),
        ('stg', 'staging'),
        ('Staging', 'staging')
    ]
    
    env_ok = True
    for dirty, expected in env_tests:
        res = clean_tag(dirty, ENV_MAP)
        if res != expected:
            print(f"  ✗ '{dirty}' mapped to '{res}', expected '{expected}'")
            env_ok = False
            
    print(f"  Spot-check tested {len(env_tests)} variants.")
    results['Spot-check Envs passed'] = env_ok
    _status(results, 'Spot-check Envs passed')
    
    # ── Summary ───────────────────────────────────────────────
    print(f"\n{sep}")
    print("  SUMMARY — S10 VALIDATION")
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
    from scenarios.s10_tags import run as s10_run
    
    billing = pd.read_csv('data/raw/usage_billing.csv')
    billing = s10_run(billing)
    validate(billing)
