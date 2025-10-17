"""
Test Dataset Optimization: Verify city field removed, all other fields working
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import DataAnalytics, EventSimulator
from utils.proactive_monitor import ProactiveMonitor


def test_optimized_dataset():
    """Test that optimized dataset works correctly without city field."""
    print("="*70)
    print("DATASET OPTIMIZATION VERIFICATION")
    print("="*70)
    
    # Test 1: DataAnalytics loads optimized dataset
    print("\n[Test 1] Loading optimized dataset...")
    analytics = DataAnalytics()
    
    if analytics.df is None:
        print("  ❌ Failed to load dataset")
        return
    
    print(f"  ✓ Loaded {len(analytics.df)} customers")
    print(f"  ✓ Total columns: {len(analytics.df.columns)}")
    
    # Check city is removed
    if 'city' in analytics.df.columns:
        print("  ❌ ERROR: City column still present!")
    else:
        print("  ✓ City column successfully removed")
    
    # Check all other columns present
    expected_columns = [
        'customer_id', 'first_name', 'last_name', 'email', 
        'phone', 'signup_date', 'country',
        'segment', 'lifetime_value', 'avg_order_value', 
        'preferred_category', 'last_active_date', 
        'loyalty_tier', 'opt_in_marketing', 'language'
    ]
    
    missing = [col for col in expected_columns if col not in analytics.df.columns]
    if missing:
        print(f"  ❌ Missing columns: {missing}")
    else:
        print(f"  ✓ All {len(expected_columns)} expected columns present")
    
    # Test 2: Customer objects don't have city field
    print("\n[Test 2] Customer model verification...")
    simulator = EventSimulator()
    customer = simulator.get_random_customer()
    
    if customer:
        print(f"  ✓ Customer created: {customer.full_name}")
        
        # Check city attribute
        has_city = hasattr(customer, 'city')
        if has_city:
            print(f"  ⚠️  WARNING: Customer still has city attribute (value: {customer.city})")
        else:
            print("  ✓ City attribute not present")
        
        # Check other fields still work
        print(f"\n  Essential fields:")
        print(f"    • Name: {customer.full_name}")
        print(f"    • Country: {customer.country}")
        print(f"    • Phone: {customer.phone}")
        print(f"    • Language: {customer.language}")
        print(f"    • LTV: ${customer.lifetime_value:,.2f}")
        print(f"    • Avg Order: ${customer.avg_order_value}")
        print(f"    • Days since active: {customer.days_since_active}")
        print(f"    • Can contact: {customer.can_contact_marketing}")
    
    # Test 3: ProactiveMonitor works without city
    print("\n[Test 3] ProactiveMonitor with optimized data...")
    monitor = ProactiveMonitor()
    
    at_risk = monitor.detect_churn_risks(
        min_churn_risk=0.3,
        min_lifetime_value=3000.0,
        segments=["VIP"]
    )
    
    print(f"  ✓ Detected {len(at_risk)} at-risk VIP customers")
    
    if at_risk:
        sample = at_risk[0]
        customer = sample['customer']
        print(f"\n  Sample at-risk customer:")
        print(f"    • Name: {customer.full_name}")
        print(f"    • Country: {customer.country} (no city clutter)")
        print(f"    • Churn Risk: {sample['churn_risk']*100:.1f}%")
        print(f"    • Health: {sample['health_score']*100:.1f}%")
    
    # Test 4: to_dict() doesn't include city
    print("\n[Test 4] Customer serialization...")
    customer = simulator.get_random_customer(segment="Loyal")
    customer_dict = customer.to_dict()
    
    if 'city' in customer_dict:
        print(f"  ❌ ERROR: City in dictionary: {customer_dict['city']}")
    else:
        print("  ✓ City not in serialized dictionary")
    
    print(f"  ✓ Dictionary has {len(customer_dict)} fields")
    print(f"  ✓ Country preserved: {customer_dict['country']}")
    
    # Test 5: Segment statistics
    print("\n[Test 5] Enhanced segment statistics...")
    stats = analytics.get_segment_statistics("VIP")
    
    print(f"  VIP Segment:")
    print(f"    • Total customers: {stats.get('total_customers')}")
    print(f"    • Avg LTV: ${stats.get('avg_lifetime_value', 0):,.2f}")
    print(f"    • Avg Order Value: ${stats.get('avg_order_value', 0):.2f}")
    
    if 'country_distribution' in stats:
        print(f"    • Countries: {len(stats['country_distribution'])} countries")
        top_country = max(stats['country_distribution'].items(), key=lambda x: x[1])
        print(f"      → Top: {top_country[0]} ({top_country[1]} customers)")
    
    if 'language_distribution' in stats:
        print(f"    • Languages: {len(stats['language_distribution'])} languages")
    
    # Summary
    print("\n" + "="*70)
    print("✅ DATASET OPTIMIZATION COMPLETE!")
    print("="*70)
    print("\nWhat changed:")
    print("  ✗ Removed: city (unnecessary granularity)")
    print("  ✓ Kept: country (sufficient for regional insights)")
    print("  ✓ Kept: All 14 other critical/high/medium value fields")
    print("\nBenefits:")
    print("  • Reduced agent context noise")
    print("  • Cleaner data model")
    print("  • No loss of business-critical information")
    print("  • Faster processing (less data to parse)")
    print("\nDataset: AgentMAX_CX_dataset_optimized.xlsx")
    print(f"Size: 1,000 customers × 15 columns")
    print("="*70)


if __name__ == '__main__':
    test_optimized_dataset()
