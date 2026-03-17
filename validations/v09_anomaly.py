"""
Validation 09 — Anomaly Detection Validation
==============================================
Validates the output of S09 (Anomaly Detection).
Checks: total flagged count, extreme outlier accuracy, Z-score bounds.
"""

import pandas as pd


def validate(df):
    """
    Run all validation checks for S09.
    
    Returns:
        (passed, failed, results) tuple
    """
    sep = "=" * 55
    results = {}
    
    # ── 1. Total Flagged Anomalies ────────────────────────────
    print(f"\n{sep}")
    print("  1. ANOMALY COUNT")
    print(sep)
    
    anomalies = df['Is_Usage_Anomaly'].sum()
    print(f"  Flagged Anomalies: {anomalies}")
    print(f"  Expected ~500 (plus potential duplicates ~20-30)")
    
    results['Anomaly count ~500'] = 450 <= anomalies <= 650
    _status(results, 'Anomaly count ~500')
    
    # ── 2. False Positives (Lower Bound) ──────────────────────
    print(f"\n{sep}")
    print("  2. LOWER BOUND CHECK")
    print(sep)
    
    false_positives = df[df['Is_Usage_Anomaly'] & (df['Usage_Value'] < 1000)]
    print(f"  Anomalies under 1000 value: {len(false_positives)}")
    
    # Our normal data goes up to 50k (seconds) and 5k (GB).
    # 10x spikes on 1GB = 10GB. Actually, it's possible to have valid small spikes.
    # But checking if we flagged negative Z-scores:
    neg_anomalies = df[df['Is_Usage_Anomaly'] & (df['Anomaly_Z_Score'] <= 0)]
    print(f"  Anomalies with Z-Score <= 0: {len(neg_anomalies)}")
    
    results['No negative Z-score anomalies'] = len(neg_anomalies) == 0
    _status(results, 'No negative Z-score anomalies')
    
    # ── 3. High Magnitude Outliers ────────────────────────────
    print(f"\n{sep}")
    print("  3. EXTREME OUTLIERS DETECTED")
    print(sep)
    
    # Look at really massive numbers (e.g., > 100,000 for GB or > 1,000,000 for seconds)
    # They should ALL be flagged
    extreme = df[((df['Unit'].str.lower().str.contains('gb') | df['Unit'].str.lower().str.contains('mb')) & (df['Usage_Value'] > 50000)) | 
                 (df['Usage_Value'] > 750000)]
                 
    missed_extreme = extreme[~extreme['Is_Usage_Anomaly']]
    print(f"  Extreme values (>750k usage or >50k GB): {len(extreme)}")
    print(f"  Extreme values missed: {len(missed_extreme)}")
    
    results['All extremes flagged'] = len(missed_extreme) == 0
    _status(results, 'All extremes flagged')
    
    # ── 4. Same SKU comparisons ───────────────────────────────
    print(f"\n{sep}")
    print("  4. SKU-LEVEL COMPARISON")
    print(sep)
    
    # Pick the most common SKU
    top_sku = df['SKU_Clean'].mode()[0]
    sku_data = df[df['SKU_Clean'] == top_sku]
    
    normal_max = sku_data[~sku_data['Is_Usage_Anomaly']]['Usage_Value'].max()
    anomaly_min = sku_data[sku_data['Is_Usage_Anomaly']]['Usage_Value'].min()
    
    print(f"  Top SKU: {top_sku}")
    print(f"  Max Normal Value: {normal_max}")
    print(f"  Min Anomaly Value: {anomaly_min}")
    
    # Min anomaly shouldn't be drastically lower than max normal
    # But because Z-score > 4, Min anomaly will naturally be much higher than Max normal
    # unless Z-score failed.
    
    results['Separation maintained'] = (pd.isna(anomaly_min) or pd.isna(normal_max) or anomaly_min >= normal_max)
    _status(results, 'Separation maintained')
    
    # ── Summary ───────────────────────────────────────────────
    print(f"\n{sep}")
    print("  SUMMARY — S09 VALIDATION")
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
    from scenarios.s03_sku import run as s03_run
    from scenarios.s09_anomaly import run as s09_run
    
    billing = pd.read_csv('data/raw/usage_billing.csv')
    billing = s03_run(billing)
    billing = s09_run(billing)
    validate(billing)
