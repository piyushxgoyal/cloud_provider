"""
Scenario 18 — Department & Project Validation
===============================================
Validates `Department` and `Project` combos.
  - Cleans strings (strips whitespace, forced to UPPERCASE).
  - Validates against the known dictionary of valid combinations.
  - Flags unknown departments, unknown projects, and invalid pairings.
"""

import pandas as pd

# Hardcoded valid business hierarchy
VALID_COMBOS = {
    'ENGINEERING':  ['ALPHA', 'BETA', 'PHOENIX'],
    'FINANCE':      ['DELTA', 'EPSILON', 'NOVA'],
    'MARKETING':    ['GAMMA', 'OMEGA'],
    'DATA_SCIENCE': ['ALPHA', 'PHOENIX', 'NOVA'],
    'SECURITY':     ['BETA', 'DELTA'],
    'DEVOPS':       ['ALPHA', 'BETA', 'PHOENIX', 'GAMMA'],
    'PRODUCT':      ['OMEGA', 'EPSILON'],
    'HR':           ['DELTA', 'GAMMA'],
    'LEGAL':        ['EPSILON', 'NOVA'],
    'OPERATIONS':   ['ALPHA', 'DELTA', 'GAMMA'],
}

ALL_DEPTS = set(VALID_COMBOS.keys())
ALL_PROJECTS = set(p for projs in VALID_COMBOS.values() for p in projs)

def run(df):
    # 1. Clean formatting
    df['Dept_Clean'] = df['Department'].astype(str).str.strip().str.upper()
    df['Project_Clean'] = df['Project'].astype(str).str.strip().str.upper()
    
    # 2. Evaluate status
    df['Is_Unknown_Dept'] = ~df['Dept_Clean'].isin(ALL_DEPTS)
    df['Is_Unknown_Project'] = ~df['Project_Clean'].isin(ALL_PROJECTS)
    
    # Check combo only if both are known
    def is_invalid_combo(row):
        # We only flag invalid combo if the dept and project are themselves known
        if row['Is_Unknown_Dept'] or row['Is_Unknown_Project']:
            return False
            
        dept = row['Dept_Clean']
        proj = row['Project_Clean']
        
        return proj not in VALID_COMBOS.get(dept, [])

    df['Is_Invalid_Combo'] = df.apply(is_invalid_combo, axis=1)
    
    # 3. Printing stats
    print("✅ S18 — Department & Project Validation complete")
    print(f"   Unknown Depts:     {df['Is_Unknown_Dept'].sum()}")
    print(f"   Unknown Projects:  {df['Is_Unknown_Project'].sum()}")
    print(f"   Invalid Combos:    {df['Is_Invalid_Combo'].sum()}")
    
    return df
