"""
Transformation 10 — Value Forecasting
=======================================
Calculates a 7-day rolling average per Service from the daily cube, and appends a +5% 
growth assumption for naive forecasting.

Output:
  - t10_cost_forecast.csv
"""

import pandas as pd
import os

def run(df, out_dir='data/transforms'):
    os.makedirs(out_dir, exist_ok=True)
    
    req = ['TS_UTC', 'Service_Clean', 'Cost_USD']
    if not all(c in df.columns for c in req):
        print("⚠️ Missing columns for T10")
        return pd.DataFrame()
        
    ts_df = df.dropna(subset=['TS_UTC']).copy()
    ts_df['Date'] = pd.to_datetime(ts_df['TS_UTC'], utc=True).dt.date
    
    daily_service = ts_df.groupby(['Date', 'Service_Clean'], as_index=False).agg(
        Daily_Cost=('Cost_USD', 'sum')
    )
    
    # Ensure dense date range so rolling avg works cleanly
    daily_service['Date'] = pd.to_datetime(daily_service['Date'])
    
    results = []
    for service, group in daily_service.groupby('Service_Clean'):
        group = group.sort_values('Date').set_index('Date')
        
        # 7 Day Rolling Avg
        group['Rolling_7D_Avg'] = group['Daily_Cost'].rolling(window=7, min_periods=1).mean()
        
        # Forecast = Current Rolling Avg * 1.05
        group['Forecast_Next_Month_Daily_Avg'] = group['Rolling_7D_Avg'] * 1.05
        
        group['Service_Clean'] = service
        results.append(group.reset_index())
        
    if not results:
        print("⚠️ No data for T10 forecasting.")
        return pd.DataFrame()
        
    forecast_df = pd.concat(results, ignore_index=True)
    forecast_df.to_csv(os.path.join(out_dir, 't10_cost_forecast.csv'), index=False)
    
    print("✅ T10 — Value Forecasts generated")
    
    return forecast_df

if __name__ == '__main__':
    df = pd.read_csv('data/cleaned/cleaned_usage_billing.csv')
    run(df)
