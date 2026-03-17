"""
Transformation 09 — Carbon Footprint Estimates
================================================
Joins the canonical Region with known Grid Carbon Intensity rates to estimate 
the carbon footprint of compute/usage operations.

Output:
  - t09_carbon_footprint.csv
"""

import pandas as pd
import os

# Estimated gCO2eq/kWh for major regions based on grid intensity
CARBON_FACTORS = {
    'us-east-1': 379.6, 'eu-west-1': 316.2, 'ap-south-1': 708.2,
    'us-west-2': 102.8, 'ap-southeast-1': 408.0,
    'eastus': 379.6, 'westeurope': 268.0, 'centralindia': 708.2,
    'canadacentral': 26.0, 'southeastasia': 408.0,
    'us-central1': 394.5, 'europe-west1': 158.0, 'asia-south1': 708.2,
    'us-west1': 54.0, 'asia-southeast1': 408.0
}

def run(df, out_dir='data/transforms'):
    os.makedirs(out_dir, exist_ok=True)
    
    if 'Region_Clean' not in df.columns or 'Usage_Converted' not in df.columns:
        print("⚠️ Missing columns for T09")
        return pd.DataFrame()
        
    carbon_df = df.copy()
    
    # Map the factor
    carbon_df['Carbon_Factor'] = carbon_df['Region_Clean'].map(CARBON_FACTORS).fillna(400.0) # 400 global avg fallback
    
    # We create a pseudo-metric for energy by linking Usage_Converted. 
    # For compute seconds: assume average 100W/server = 0.1kW * (seconds/3600) hours
    # For storage GB: assume 0.002 kWh / GB / month. We handle them differently based on unit.
    
    def estimate_emissions(row):
        usage = row['Usage_Converted']
        factor = row['Carbon_Factor']
        unit = str(row['Unit_Canonical']).lower()
        if pd.isna(usage):
            return 0.0
            
        if 'sec' in unit:
            kwh = 0.1 * (usage / 3600.0)
            return kwh * factor / 1000.0 # kgCO2e
        elif 'gb' in unit:
            # Assuming monthly usage for storage
            kwh = 0.002 * usage 
            return kwh * factor / 1000.0 # kgCO2e
        return 0.0
        
    carbon_df['Estimated_Emissions_kgCO2e'] = carbon_df.apply(estimate_emissions, axis=1)
    
    # Aggregate by Region and Provider
    # Note: extracting provider from Canonical Account mapping, or default by SKU prefix
    summary = carbon_df.groupby(['Region_Clean'], as_index=False).agg(
        Total_Emissions_kg=('Estimated_Emissions_kgCO2e', 'sum'),
        Record_Count=('Usage_ID', 'count')
    ).sort_values('Total_Emissions_kg', ascending=False)
    
    summary.to_csv(os.path.join(out_dir, 't09_carbon_footprint.csv'), index=False)
    
    print("✅ T09 — Carbon Footprint Metrics generated")
    print(f"   Total Estimated Fleet Emissions: {summary['Total_Emissions_kg'].sum():.2f} kg CO2e")
    
    return summary

if __name__ == '__main__':
    df = pd.read_csv('data/cleaned/cleaned_usage_billing.csv')
    run(df)
