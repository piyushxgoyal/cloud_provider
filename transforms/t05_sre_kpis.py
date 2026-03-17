"""
Transformation 05 — SRE KPIs (SLO / SLA)
========================================
Measures SLA attainment based on SLA_Event_Clean.
Grouped by Service and Region to find the least reliable components.

Output:
  - t05_sre_slas.csv
"""

import pandas as pd
import os

def run(df, out_dir='data/transforms'):
    os.makedirs(out_dir, exist_ok=True)
    
    if 'SLA_Event_Clean' not in df.columns:
        print("⚠️ Missing SLA_Event_Clean for T05")
        return df
        
    sre = df.copy()
    sre['Service_Clean'] = sre['Service_Clean'].fillna('UNKNOWN')
    sre['Region_Clean'] = sre['Region_Clean'].fillna('UNKNOWN')
    
    # 1. Component Level Reliability
    agg = sre.groupby(['Service_Clean', 'Region_Clean'], as_index=False).agg(
        Total_Events=('Usage_ID', 'count'),
        SLA_Breaches=('SLA_Event_Clean', 'sum')
    )
    
    # Attainment % = (Total - Breaches) / Total
    agg['SLA_Attainment_Pct'] = ((agg['Total_Events'] - agg['SLA_Breaches']) / agg['Total_Events'] * 100).round(3)
    
    agg = agg.sort_values('SLA_Attainment_Pct', ascending=True)
    
    agg.to_csv(os.path.join(out_dir, 't05_sre_slas.csv'), index=False)
    
    print("✅ T05 — SRE KPIs (SLO/SLA Attainment) generated")
    print(f"   Overall SLA Attainment: {((len(sre) - sre['SLA_Event_Clean'].sum())/len(sre)*100):.2f}%")
    print(f"   Most unreliable: {agg.iloc[0]['Service_Clean']} in {agg.iloc[0]['Region_Clean']} ({agg.iloc[0]['SLA_Attainment_Pct']}%)")
    
    return agg

if __name__ == '__main__':
    df = pd.read_csv('data/cleaned/cleaned_usage_billing.csv')
    run(df)
