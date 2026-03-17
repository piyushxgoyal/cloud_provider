"""
Transformation 15 — Support Ticket Clustering
===============================================
Maps Ticket_Text_Masked descriptions into simple analytical buckets
using keyword associations (e.g. outage, billing, performance, access).

Output:
  - t15_ticket_clustering.csv
"""

import pandas as pd
import os

def run(df, out_dir='data/transforms'):
    os.makedirs(out_dir, exist_ok=True)
    
    tickets_path = 'data/raw/support_tickets.csv'
    if not os.path.exists(tickets_path):
        print("⚠️ Missing support_tickets.csv for T15")
        return pd.DataFrame()
        
    tickets = pd.read_csv(tickets_path)
    
    if 'Ticket_Text' not in tickets.columns:
        print("⚠️ Missing Ticket_Text")
        return tickets
        
    def cluster_ticket(text):
        if pd.isna(text):
            return "Unclassified"
        t = str(text).lower()
        if any(w in t for w in ['down', 'outage', 'unreachable', 'offline', 'unavailable']):
            return "Outage / Availability"
        elif any(w in t for w in ['slow', 'latency', 'timeout', 'performance', 'lag']):
            return "Performance Degradation"
        elif any(w in t for w in ['bill', 'invoice', 'charge', 'cost', 'expensive']):
            return "Billing & Cost"
        elif any(w in t for w in ['login', 'access', 'permission', 'iam', 'role', 'denied']):
            return "IAM & Access"
        else:
            return "General Query"
            
    tickets['Ticket_Category'] = tickets['Ticket_Text'].apply(cluster_ticket)
    
    # Group and count
    clusters = tickets.groupby('Ticket_Category', as_index=False).agg(
        Ticket_Count=('Ticket_ID', 'count')
    ).sort_values('Ticket_Count', ascending=False)
    
    clusters.to_csv(os.path.join(out_dir, 't15_ticket_clustering.csv'), index=False)
    print("✅ T15 — Support Ticket Clustering generated")
    
    return clusters

if __name__ == '__main__':
    run(None)
