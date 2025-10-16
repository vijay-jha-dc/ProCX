"""Analyze the original dataset to identify valuable missing columns."""
import pandas as pd
import sys

def analyze_datasets():
    """Compare original and cleaned datasets."""
    print('='*70)
    print('DATASET ANALYSIS: What We\'re Missing')
    print('='*70)
    
    # Load both
    df_original = pd.read_excel('data/AgentMAX_CX_dataset.xlsx')
    df_cleaned = pd.read_excel('data/AgentMAX_CX_dataset_cleaned.xlsx')
    
    print(f'\nOriginal: {len(df_original)} rows, {len(df_original.columns)} columns')
    print(f'Cleaned:  {len(df_cleaned)} rows, {len(df_cleaned.columns)} columns')
    
    # Missing columns
    missing_cols = set(df_original.columns) - set(df_cleaned.columns)
    
    print(f'\n\n{"MISSING COLUMNS":-^70}')
    print(f'\nRemoved: {sorted(missing_cols)}')
    
    print(f'\n\n{"DETAILED ANALYSIS":-^70}')
    
    for col in sorted(missing_cols):
        print(f'\n📊 {col.upper()}')
        print('-'*70)
        print(f'  Data Type: {df_original[col].dtype}')
        print(f'  Non-null:  {df_original[col].notna().sum():,}/{len(df_original):,} ({df_original[col].notna().sum()/len(df_original)*100:.1f}%)')
        print(f'  Unique:    {df_original[col].nunique():,}')
        
        # Sample values
        if df_original[col].dtype in ['object', 'string']:
            samples = df_original[col].dropna().head(5).tolist()
            print(f'  Samples:   {samples}')
            # Value counts for categorical
            if df_original[col].nunique() < 50:
                print(f'\n  Value Distribution:')
                vc = df_original[col].value_counts().head(10)
                for val, count in vc.items():
                    print(f'    • {val}: {count} ({count/len(df_original)*100:.1f}%)')
        else:
            samples = df_original[col].dropna().head(5).tolist()
            print(f'  Samples:   {samples}')
            # Stats for numeric
            if df_original[col].dtype in ['int64', 'float64']:
                print(f'  Min:       {df_original[col].min()}')
                print(f'  Max:       {df_original[col].max()}')
                print(f'  Mean:      {df_original[col].mean():.2f}')
                print(f'  Median:    {df_original[col].median():.2f}')
    
    # Business Value Assessment
    print(f'\n\n{"BUSINESS VALUE ASSESSMENT":-^70}')
    
    value_assessment = {
        'phone': {
            'value': '⭐⭐⭐ HIGH',
            'reason': 'Contact channel for proactive outreach (SMS, WhatsApp)',
            'use_cases': ['Proactive retention calls', 'SMS alerts', 'Multi-channel engagement']
        },
        'signup_date': {
            'value': '⭐⭐⭐⭐⭐ CRITICAL',
            'reason': 'Customer tenure analysis, lifecycle stage detection',
            'use_cases': ['New customer onboarding', 'Anniversary milestones', 'Churn risk (tenure correlation)', 'Customer lifetime calculations']
        },
        'country': {
            'value': '⭐⭐⭐ HIGH',
            'reason': 'Geographic insights, timezone-aware engagement',
            'use_cases': ['Regional preferences', 'Timezone-based contact timing', 'Geographic trends', 'Local holiday awareness']
        },
        'city': {
            'value': '⭐⭐ MEDIUM',
            'reason': 'Granular location data (less critical than country)',
            'use_cases': ['Hyper-local offers', 'Regional support teams']
        },
        'avg_order_value': {
            'value': '⭐⭐⭐⭐⭐ CRITICAL',
            'reason': 'Purchase behavior metric, upsell opportunity detection',
            'use_cases': ['Upsell targeting', 'Value tier segmentation', 'Spending pattern analysis', 'Budget-aware recommendations']
        },
        'last_active_date': {
            'value': '⭐⭐⭐⭐⭐ CRITICAL',
            'reason': 'Inactivity detection, engagement recency',
            'use_cases': ['Dormancy alerts', 'Re-engagement campaigns', 'Churn risk scoring', 'Activity-based health score']
        },
        'opt_in_marketing': {
            'value': '⭐⭐⭐⭐ VERY HIGH',
            'reason': 'Compliance, channel preference',
            'use_cases': ['GDPR/CAN-SPAM compliance', 'Appropriate contact channels', 'Permission-based marketing']
        },
        'language': {
            'value': '⭐⭐⭐ HIGH',
            'reason': 'Personalization, accessibility',
            'use_cases': ['Localized messaging', 'Agent language matching', 'Multilingual support']
        }
    }
    
    for col in sorted(missing_cols):
        if col in value_assessment:
            info = value_assessment[col]
            print(f'\n💡 {col.upper()}')
            print(f'   Value:     {info["value"]}')
            print(f'   Why:       {info["reason"]}')
            print(f'   Use Cases:')
            for use_case in info['use_cases']:
                print(f'     • {use_case}')
    
    # Recommendations
    print(f'\n\n{"RECOMMENDATIONS":-^70}')
    print('\n🎯 HIGH PRIORITY - Add These ASAP:')
    print('   1. last_active_date   → Critical for churn detection')
    print('   2. signup_date        → Customer lifecycle/tenure')
    print('   3. avg_order_value    → Upsell targeting & segmentation')
    print('   4. opt_in_marketing   → Compliance & channel selection')
    
    print('\n⚡ MEDIUM PRIORITY - Add Soon:')
    print('   5. phone              → Multi-channel outreach')
    print('   6. country            → Geographic personalization')
    print('   7. language           → Localized messaging')
    
    print('\n📝 OPTIONAL:')
    print('   8. city               → Hyper-local features')
    
    print('\n'+'='*70)

if __name__ == '__main__':
    analyze_datasets()
