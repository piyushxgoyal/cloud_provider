"""
Transformation 11 — Tag Completeness Scorecards
=================================================
Calculates the percentage of rows having valid tags (Owner and Env).
Used by cloud governance teams to track resource tagging compliance.

Output:
  - t11_tag_completeness.csv
"""

import pandas as pd
import os

def run(df, out_dir='data/transforms'):
    os.makedirs(out_dir, exist_ok=True)
    
    req = ['Account_ID', 'Tag_Owner_Clean', 'Tag_Env_Clean']
    if not all(c in df.columns for c in req):
        print("⚠️ Missing columns for T11")
        return pd.DataFrame()
        
    tag_df = df.copy()
    
    # Valid tags are anything except 'UNKNOWN' or NaNs
    tag_df['Has_Owner'] = (tag_df['Tag_Owner_Clean'] != 'UNKNOWN') & tag_df['Tag_Owner_Clean'].notna()
    tag_df['Has_Env'] = (tag_df['Tag_Env_Clean'] != 'UNKNOWN') & tag_df['Tag_Env_Clean'].notna()
    
    # Scorecard by Account
    scorecard = tag_df.groupby('Account_ID', as_index=False).agg(
        Total_Resources=('Usage_ID', 'count'),
        Valid_Owner_Tags=('Has_Owner', 'sum'),
        Valid_Env_Tags=('Has_Env', 'sum')
    )
    
    scorecard['Owner_Compliance_Pct'] = (scorecard['Valid_Owner_Tags'] / scorecard['Total_Resources'] * 100).round(1)
    scorecard['Env_Compliance_Pct'] = (scorecard['Valid_Env_Tags'] / scorecard['Total_Resources'] * 100).round(1)
    
    # Overall Score (Average of the two)
    scorecard['Overall_Compliance_Pct'] = ((scorecard['Owner_Compliance_Pct'] + scorecard['Env_Compliance_Pct']) / 2).round(1)
    
    scorecard = scorecard.sort_values('Overall_Compliance_Pct', ascending=True) # Worst first
    
    scorecard.to_csv(os.path.join(out_dir, 't11_tag_completeness.csv'), index=False)
    
    print("✅ T11 — Tag Completeness Scorecards generated")
    try:
        avg_score = scorecard['Overall_Compliance_Pct'].mean()
        print(f"   Fleet Tagging Compliance: {avg_score:.1f}%")
    except:
        pass
        
    return scorecard

if __name__ == '__main__':
    df = pd.read_csv('data/cleaned/cleaned_usage_billing.csv')
    run(df)
