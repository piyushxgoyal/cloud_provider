"""
Transformation 01 — Daily and Monthly Cost & Usage Cubes
==========================================================
Aggregates Cost_USD and Usage_Converted by:
  - Date (Daily and YYYY-MM)
  - Service
  - SKU
  - Region

Output:
  - t01_daily_cube.csv
  - t01_monthly_cube.csv
"""

import pandas as pd
import os

def run(df, out_dir='data/transforms'):
    os.makedirs(out_dir, exist_ok=True)
    
    # Needs valid TS_UTC, Service, SKU, Region, Cost_USD, Usage_Converted
    req_cols = ['TS_UTC', 'Service_Clean', 'SKU_Clean', 'Region_Clean', 'Cost_USD', 'Usage_Converted']
    missing = [c for c in req_cols if c not in df.columns]
    if missing:
        print(f"⚠️ Missing columns for T01: {missing}")
        return df

    # Drop fully null dates just for the cube
    cube_df = df.dropna(subset=['TS_UTC']).copy()
    
    # 1. Add Date and Month dimensions
    # TS_UTC is parsed as datetime
    cube_df['TS_UTC'] = pd.to_datetime(cube_df['TS_UTC'], utc=True)
    cube_df['Date'] = cube_df['TS_UTC'].dt.date
    cube_df['Month'] = cube_df['TS_UTC'].dt.to_period('M').astype(str)
    
    # Normalize grouping columns (fill NAs with 'UNKNOWN')
    grp_cols = ['Service_Clean', 'SKU_Clean', 'Region_Clean']
    for c in grp_cols:
        cube_df[c] = cube_df[c].fillna('UNKNOWN')

    # 2. Daily Cube
    daily = cube_df.groupby(['Date'] + grp_cols, as_index=False).agg(
        Total_Cost_USD=('Cost_USD', 'sum'),
        Total_Usage=('Usage_Converted', 'sum'),
        Log_Count=('Usage_ID', 'count')
    )
    
    # 3. Monthly Cube
    monthly = cube_df.groupby(['Month'] + grp_cols, as_index=False).agg(
        Total_Cost_USD=('Cost_USD', 'sum'),
        Total_Usage=('Usage_Converted', 'sum'),
        Log_Count=('Usage_ID', 'count')
    )
    
    # Save
    daily.to_csv(os.path.join(out_dir, 't01_daily_cube.csv'), index=False)
    monthly.to_csv(os.path.join(out_dir, 't01_monthly_cube.csv'), index=False)
    
    print("✅ T01 — Cost & Usage Cubes generated")
    print(f"   Daily Cube Rows:   {len(daily)}")
    print(f"   Monthly Cube Rows: {len(monthly)}")
    
    return daily, monthly

if __name__ == '__main__':
    df = pd.read_csv('data/cleaned/cleaned_usage_billing.csv')
    daily, monthly = run(df)
    if daily is not None:
        print("\nSample Daily Cube:")
        print(daily.head(3).to_string(index=False))
