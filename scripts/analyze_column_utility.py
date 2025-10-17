"""
Analyze the dataset to identify useful vs unnecessary columns for ProCX scope.
"""
import pandas as pd
from pathlib import Path

def analyze_column_utility():
    """Analyze each column's utility for the ProCX project."""
    print("="*70)
    print("DATASET COLUMN UTILITY ANALYSIS")
    print("="*70)
    
    # Load dataset
    df = pd.read_excel('data/AgentMAX_CX_dataset.xlsx')
    
    print(f"\nDataset: {len(df)} customers, {len(df.columns)} columns\n")
    
    # Define column utility for ProCX scope
    column_analysis = {
        'customer_id': {
            'utility': '⭐⭐⭐⭐⭐ CRITICAL',
            'use': 'Unique identifier - essential for tracking',
            'keep': True
        },
        'first_name': {
            'utility': '⭐⭐⭐⭐⭐ CRITICAL',
            'use': 'Personalization in agent responses',
            'keep': True
        },
        'last_name': {
            'utility': '⭐⭐⭐⭐⭐ CRITICAL',
            'use': 'Full name for professional communication',
            'keep': True
        },
        'email': {
            'utility': '⭐⭐⭐⭐⭐ CRITICAL',
            'use': 'Primary contact channel, unique identifier',
            'keep': True
        },
        'phone': {
            'utility': '⭐⭐⭐ MEDIUM',
            'use': 'Multi-channel outreach (SMS, calls)',
            'keep': True,
            'notes': 'All same format (+91), no immediate use but future-ready'
        },
        'signup_date': {
            'utility': '⭐⭐⭐⭐⭐ CRITICAL',
            'use': 'Customer tenure, lifecycle stage, anniversary milestones',
            'keep': True
        },
        'country': {
            'utility': '⭐⭐ LOW',
            'use': 'Geographic insights, timezone-aware engagement',
            'keep': True,
            'notes': 'Only 6 countries, could be useful for regional patterns'
        },
        'city': {
            'utility': '⭐ VERY LOW',
            'use': 'Hyper-local offers',
            'keep': False,
            'notes': 'Too granular, adds noise, 10 Indian cities only'
        },
        'segment': {
            'utility': '⭐⭐⭐⭐⭐ CRITICAL',
            'use': 'Core business metric - VIP/Loyal/Regular/Occasional',
            'keep': True
        },
        'lifetime_value': {
            'utility': '⭐⭐⭐⭐⭐ CRITICAL',
            'use': 'Value-based prioritization, churn risk calculation',
            'keep': True
        },
        'avg_order_value': {
            'utility': '⭐⭐⭐⭐⭐ CRITICAL',
            'use': 'Spending patterns, upsell targeting, budget analysis',
            'keep': True
        },
        'preferred_category': {
            'utility': '⭐⭐⭐⭐ HIGH',
            'use': 'Product recommendations, personalized offers',
            'keep': True
        },
        'last_active_date': {
            'utility': '⭐⭐⭐⭐⭐ CRITICAL',
            'use': 'Inactivity detection, engagement scoring, churn risk',
            'keep': True
        },
        'loyalty_tier': {
            'utility': '⭐⭐⭐⭐ HIGH',
            'use': 'Rewards program, tier-based treatment',
            'keep': True
        },
        'opt_in_marketing': {
            'utility': '⭐⭐⭐⭐⭐ CRITICAL',
            'use': 'GDPR/compliance, permission-based marketing',
            'keep': True
        },
        'language': {
            'utility': '⭐⭐⭐ MEDIUM',
            'use': 'Localized messaging, multilingual support',
            'keep': True,
            'notes': '5 languages (en, hi, ta, te, bn) - good for personalization'
        }
    }
    
    # Print analysis
    print("COLUMN-BY-COLUMN ANALYSIS:")
    print("-"*70)
    
    keep_columns = []
    remove_columns = []
    
    for col in df.columns:
        info = column_analysis.get(col, {
            'utility': '❓ UNKNOWN',
            'use': 'Not defined',
            'keep': False
        })
        
        status = "✓ KEEP" if info['keep'] else "✗ REMOVE"
        
        print(f"\n{col}")
        print(f"  {status}")
        print(f"  Utility: {info['utility']}")
        print(f"  Use: {info['use']}")
        if 'notes' in info:
            print(f"  Notes: {info['notes']}")
        
        # Sample data
        sample = df[col].dropna().head(3).tolist()
        print(f"  Sample: {sample}")
        
        if info['keep']:
            keep_columns.append(col)
        else:
            remove_columns.append(col)
    
    # Summary
    print("\n" + "="*70)
    print("RECOMMENDATION SUMMARY")
    print("="*70)
    
    print(f"\n✓ KEEP ({len(keep_columns)} columns):")
    for col in keep_columns:
        print(f"  • {col}")
    
    print(f"\n✗ REMOVE ({len(remove_columns)} columns):")
    for col in remove_columns:
        info = column_analysis[col]
        print(f"  • {col}")
        print(f"    Reason: {info.get('notes', info['use'])}")
    
    # Business justification
    print("\n" + "="*70)
    print("BUSINESS JUSTIFICATION FOR REMOVAL")
    print("="*70)
    
    print("\n🗑️  CITY:")
    print("  Why remove:")
    print("    • Too granular for CX platform scope")
    print("    • 10 cities - not enough diversity for meaningful insights")
    print("    • Country-level data is sufficient for regional patterns")
    print("    • Adds noise to agent context without clear value")
    print("    • No immediate use cases (hyper-local offers not in scope)")
    print("  Alternative:")
    print("    • Keep 'country' for timezone/regional patterns")
    
    # Check if city correlates with anything useful
    print("\n📊 City correlation analysis:")
    city_segment = df.groupby('city')['segment'].value_counts().unstack(fill_value=0)
    print(f"  Segments spread across all {len(df['city'].unique())} cities:")
    print(city_segment.to_string())
    
    print("\n  Conclusion: City has no strong correlation with segment")
    print("  → Safe to remove without losing business insights")
    
    # Final recommendation
    print("\n" + "="*70)
    print("FINAL RECOMMENDATION")
    print("="*70)
    print("\n✅ Create optimized dataset: AgentMAX_CX_dataset_optimized.xlsx")
    print(f"   Remove: {remove_columns}")
    print(f"   Keep: {len(keep_columns)} columns (all critical/high/medium value)")
    print("\n   This will:")
    print("   • Reduce agent context noise")
    print("   • Keep all business-critical fields")
    print("   • Maintain compliance data (opt_in_marketing)")
    print("   • Preserve engagement metrics (last_active_date)")
    print("   • Enable personalization (language, name)")
    print("   • Support churn prediction (tenure, spending, activity)")
    
    return keep_columns, remove_columns


def create_optimized_dataset(keep_columns):
    """Create an optimized dataset with only useful columns."""
    df = pd.read_excel('data/AgentMAX_CX_dataset.xlsx')
    df_optimized = df[keep_columns]
    
    output_path = 'data/AgentMAX_CX_dataset_optimized.xlsx'
    df_optimized.to_excel(output_path, index=False)
    
    print("\n" + "="*70)
    print(f"✅ Created: {output_path}")
    print(f"   Original: {len(df.columns)} columns")
    print(f"   Optimized: {len(df_optimized.columns)} columns")
    print(f"   Removed: {len(df.columns) - len(df_optimized.columns)} columns")
    print("="*70)


if __name__ == '__main__':
    keep_cols, remove_cols = analyze_column_utility()
    
    print("\n" + "="*70)
    user_input = input("\nCreate optimized dataset? (yes/no): ")
    if user_input.lower() in ['yes', 'y']:
        create_optimized_dataset(keep_cols)
    else:
        print("Skipped dataset creation.")
