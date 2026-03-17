"""
Validation 18 — Department & Project Validation
=================================================
Validates S18:
1. Dept_Clean and Project_Clean exist and are uppercase.
2. The flags accurately reflect the known dictionary.
"""

from scenarios.s18_department import VALID_COMBOS, ALL_DEPTS, ALL_PROJECTS

def validate(df):
    passed = 0
    failed = 0
    
    print("\n=======================================================")
    print("  1. CLEAN FORMATTING")
    print("=======================================================")
    # Check if all clean columns are strictly uppercase
    non_upper_dept = df[df['Dept_Clean'].str.upper() != df['Dept_Clean']]
    non_upper_proj = df[df['Project_Clean'].str.upper() != df['Project_Clean']]
    
    print(f"  Rows with non-uppercase Dept_Clean:    {len(non_upper_dept)}")
    print(f"  Rows with non-uppercase Project_Clean: {len(non_upper_proj)}")
    
    if len(non_upper_dept) == 0 and len(non_upper_proj) == 0:
        print("  ✓")
        passed += 1
    else:
        print("  X")
        failed += 1
        
    print("\n=======================================================")
    print("  2. DETECTION FLAGS ACCURACY")
    print("=======================================================")
    # Using the same sets to double check the flag logic natively
    calculated_unknown_dept = ~df['Dept_Clean'].isin(ALL_DEPTS)
    dept_errors = (df['Is_Unknown_Dept'] != calculated_unknown_dept).sum()
    
    calculated_unknown_proj = ~df['Project_Clean'].isin(ALL_PROJECTS)
    proj_errors = (df['Is_Unknown_Project'] != calculated_unknown_proj).sum()
    
    print(f"  Unknown Dept detection errors:    {dept_errors}")
    print(f"  Unknown Project detection errors: {proj_errors}")
    
    if dept_errors == 0 and proj_errors == 0:
        print("  ✓")
        passed += 1
    else:
        print("  X")
        failed += 1
        
    print("\n=======================================================")
    print("  SUMMARY — S18 VALIDATION")
    print("=======================================================")
    print(f"  Passed: {passed}/2")
    print(f"  Failed: {failed}/2\n")
    
    return passed, failed, []
