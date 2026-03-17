"""
Validation 16 — CPU & Memory Utilization
==========================================
Validates S16:
1. Storage services have NaN utilization.
2. Compute/Database have valid 0-100 utilization (no nulls).
3. Idle and Overutilized flags operate correctly.
"""

import pandas as pd

def validate(df):
    passed = 0
    failed = 0
    
    storage_mask = df['Service_Clean'].str.lower() == 'storage'
    non_storage = ~storage_mask
    
    print("\n=======================================================")
    print("  1. STORAGE IS NULL")
    print("=======================================================")
    storage_cpu = df.loc[storage_mask, 'CPU_Clean'].notna().sum()
    storage_mem = df.loc[storage_mask, 'Mem_Clean'].notna().sum()
    
    print(f"  Storage rows with CPU: {storage_cpu}")
    print(f"  Storage rows with Mem: {storage_mem}")
    
    if storage_cpu == 0 and storage_mem == 0:
        print("  ✓")
        passed += 1
    else:
        print("  X")
        failed += 1
        
    print("\n=======================================================")
    print("  2. NON-STORAGE BOUNDS & COMPLETENESS")
    print("=======================================================")
    null_compute_cpu = df.loc[non_storage, 'CPU_Clean'].isna().sum()
    null_compute_mem = df.loc[non_storage, 'Mem_Clean'].isna().sum()
    
    out_of_bounds_cpu = df.loc[(df['CPU_Clean'] < 0) | (df['CPU_Clean'] > 100), 'CPU_Clean'].count()
    out_of_bounds_mem = df.loc[(df['Mem_Clean'] < 0) | (df['Mem_Clean'] > 100), 'Mem_Clean'].count()
    
    print(f"  Null Compute/Database metrics: CPU={null_compute_cpu}, Mem={null_compute_mem}")
    print(f"  Out of 0-100 bounds: CPU={out_of_bounds_cpu}, Mem={out_of_bounds_mem}")
    
    if null_compute_cpu == 0 and null_compute_mem == 0 and out_of_bounds_cpu == 0 and out_of_bounds_mem == 0:
        print("  ✓")
        passed += 1
    else:
        print("  X")
        failed += 1
        
    print("\n=======================================================")
    print("  3. IDLE / OVERUTILIZED FLAGS")
    print("=======================================================")
    idle = df['Is_Idle'].sum()
    over = df['Is_Overutilized'].sum()
    
    print(f"  IDLE flag count:         {idle}")
    print(f"  OVERUTILIZED flag count: {over}")
    
    # We injected ~8% idle and ~5% overutilized.
    # Base is ~10,000 rows. Compute/DB is ~7000 rows.
    # Idle (<10 and <10) naturally occurs 10% * 10% = 1% + 8% injected = ~9%
    # Over (>80 or >80) naturally occurs 20% + 20% - 4% = 36% + 5% injected = ~41% 
    # So Over should be ~7000 * 0.41 = 2870
    if idle > 200 and idle < 800 and over > 2000 and over < 3500:
        print("  ✓")
        passed += 1
    else:
        print("  X")
        failed += 1
        
    print("\n=======================================================")
    print("  SUMMARY — S16 VALIDATION")
    print("=======================================================")
    print(f"  Passed: {passed}/3")
    print(f"  Failed: {failed}/3\n")
    
    return passed, failed, []
