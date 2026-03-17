"""
Transformation 19 — Security Event Correlation
================================================
Investigates compromised resources by correlating High Severity security tickets
with massive cost anomalies (Z-Score > 3).

Output:
  - t19_security_correlation.csv
"""

import pandas as pd
import os

def run(df, out_dir='data/transforms'):
    os.makedirs(out_dir, exist_ok=True)
    
    req = ['Ticket_ID', 'Is_Usage_Anomaly', 'Anomaly_Z_Score', 'Resource_ID', 'Cost_USD']
    if not all(c in df.columns for c in req):
        print("⚠️ Missing columns for T19")
        return pd.DataFrame()
        
    tickets_path = 'data/raw/support_tickets.csv'
    if not os.path.exists(tickets_path):
        print("⚠️ Missing support_tickets.csv for T19")
        return pd.DataFrame()
        
    tickets = pd.read_csv(tickets_path)
    
    # Identify high severity tickets (crypto-mining/compromises often flagged via SEV1)
    sev1_tickets = tickets[tickets['Severity'].str.upper().isin(['SEV1', '1', 'P1', 'HIGH', 'CRITICAL'])].copy()
    sev1_ticket_ids = set(sev1_tickets['Ticket_ID'].dropna())
    
    # Find overlapping resources
    # Where row is an anomaly AND is associated with a SEV1 ticket
    compromised = df[
        (df['Is_Usage_Anomaly'] == True) & 
        (df['Ticket_ID'].isin(sev1_ticket_ids))
    ].copy()
    
    # Aggregate costs of compromised resources
    if compromised.empty:
        print("✅ T19 — No compromised resource correlations found.")
        pd.DataFrame().to_csv(os.path.join(out_dir, 't19_security_correlation.csv'), index=False)
        return pd.DataFrame()
        
    correlations = compromised.groupby(['Resource_ID', 'Ticket_ID'], as_index=False).agg(
        Anomaly_Events_Count=('Usage_ID', 'count'),
        Peak_Z_Score=('Anomaly_Z_Score', 'max'),
        Total_Compromise_Cost=('Cost_USD', 'sum')
    ).sort_values('Total_Compromise_Cost', ascending=False)
    
    correlations.to_csv(os.path.join(out_dir, 't19_security_correlation.csv'), index=False)
    
    print("✅ T19 — Security Event Correlation generated")
    print(f"   Suspected Compromised Resources: {len(correlations)}")
    print(f"   Associated Cost Risk: ${correlations['Total_Compromise_Cost'].sum():.2f}")
    
    return correlations

if __name__ == '__main__':
    df = pd.read_csv('data/cleaned/cleaned_usage_billing.csv')
    run(df)
