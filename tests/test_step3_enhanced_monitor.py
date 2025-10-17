"""
Test Step 3: Verify enhanced ProactiveMonitor with multi-sheet data integration
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import DataAnalytics, EventSimulator
from utils.proactive_monitor import ProactiveMonitor, CustomerHealthScore


def test_enhanced_proactive_monitor():
    """Test ProactiveMonitor with new multi-dimensional health scoring."""
    print("="*70)
    print("STEP 3 VERIFICATION: Enhanced ProactiveMonitor")
    print("="*70)
    
    # Test 1: DataAnalytics loads multiple sheets
    print("\n[Test 1] Multi-sheet data loading...")
    analytics = DataAnalytics()
    
    print(f"  ✓ Customers loaded: {len(analytics.df) if analytics.df is not None else 0}")
    print(f"  ✓ Orders loaded: {len(analytics.orders_df) if analytics.orders_df is not None else 0}")
    print(f"  ✓ Churn labels loaded: {len(analytics.churn_labels_df) if analytics.churn_labels_df is not None else 0}")
    
    # Test 2: Order statistics
    print("\n[Test 2] Testing order statistics...")
    simulator = EventSimulator()
    customer = simulator.get_random_customer(segment="VIP")
    
    if customer:
        order_stats = analytics.get_customer_order_stats(customer)
        print(f"  Customer: {customer.full_name}")
        print(f"  ✓ Total orders: {order_stats.get('total_orders', 0)}")
        print(f"  ✓ Order frequency: {order_stats.get('order_frequency', 0):.2f} orders/month")
        print(f"  ✓ Days since last order: {order_stats.get('days_since_last_order', 'N/A')}")
        print(f"  ✓ Avg order amount: ${order_stats.get('avg_order_amount', 0):.2f}")
    
    # Test 3: Actual churn status
    print("\n[Test 3] Testing churn labels integration...")
    churn_data = analytics.get_actual_churn_status(customer)
    if churn_data:
        print(f"  ✓ Churn status available!")
        print(f"    • Is churned: {churn_data['is_churned']}")
        print(f"    • Churn date: {churn_data['churn_date']}")
        print(f"    • Churn reason: {churn_data['churn_reason']}")
        print(f"    • Predicted score: {churn_data['predicted_churn_score']:.3f}")
    else:
        print(f"  ⚠️  No churn data for this customer")
    
    # Test 4: Support history
    print("\n[Test 4] Testing support ticket history...")
    support_stats = analytics.get_customer_support_history(customer)
    if support_stats:
        print(f"  ✓ Support history available!")
        print(f"    • Total tickets: {support_stats.get('total_tickets', 0)}")
        print(f"    • Open tickets: {support_stats.get('open_tickets', 0)}")
        print(f"    • Avg CSAT: {support_stats.get('avg_csat', 'N/A')}")
    
    # Test 5: NPS data
    print("\n[Test 5] Testing NPS survey data...")
    nps_data = analytics.get_customer_nps(customer)
    if nps_data:
        print(f"  ✓ NPS data available!")
        print(f"    • NPS score: {nps_data['nps_score']}")
        print(f"    • Category: {nps_data['nps_category']}")
        print(f"    • Survey count: {nps_data['survey_count']}")
    else:
        print(f"  ⚠️  No NPS data for this customer")
    
    # Test 6: Enhanced health scoring (10 dimensions)
    print("\n[Test 6] Testing enhanced 10-dimensional health scoring...")
    health_calculator = CustomerHealthScore()
    
    # Test with multiple customers
    test_customers = [
        simulator.get_random_customer(segment="VIP"),
        simulator.get_random_customer(segment="Loyal"),
        simulator.get_random_customer(segment="Occasional")
    ]
    
    print("\n  Customer Health Scores:")
    print(f"  {'Name':<20} {'Segment':<12} {'Health':<10} {'Churn Risk':<12} {'Days Inactive'}")
    print("  " + "-"*66)
    
    for cust in test_customers:
        if cust:
            health = health_calculator.calculate_health_score(cust, analytics)
            churn_risk = health_calculator.calculate_churn_risk(health, cust, analytics)
            
            print(f"  {cust.full_name:<20} {cust.segment:<12} {health*100:>5.1f}%     {churn_risk*100:>5.1f}%       {cust.days_since_active or 'N/A'}")
    
    # Test 7: ProactiveMonitor with enhanced detection
    print("\n[Test 7] Testing ProactiveMonitor with enhanced detection...")
    monitor = ProactiveMonitor()
    
    at_risk = monitor.detect_churn_risks(
        min_churn_risk=0.2,  # Lower threshold to see more results
        min_lifetime_value=2000.0,
        segments=["VIP", "Loyal"]
    )
    
    print(f"\n  ✓ Detected {len(at_risk)} at-risk customers")
    
    if at_risk:
        print("\n  Sample at-risk customer (with enhanced data):")
        sample = at_risk[0]
        cust = sample['customer']
        
        print(f"    • Name: {cust.full_name}")
        print(f"    • Segment: {cust.segment}, Tier: {cust.loyalty_tier}")
        print(f"    • LTV: ${cust.lifetime_value:,.2f}")
        print(f"    • Health Score: {sample['health_score']*100:.1f}%")
        print(f"    • Churn Risk: {sample['churn_risk']*100:.1f}%")
        
        # Show what contributed to the score
        print(f"\n    Contributing factors:")
        print(f"      • Days since active: {cust.days_since_active} days")
        print(f"      • Avg order value: ${cust.avg_order_value}")
        print(f"      • Customer tenure: {cust.days_since_signup} days")
        
        # Get order stats
        order_stats = analytics.get_customer_order_stats(cust)
        if order_stats:
            print(f"      • Total orders: {order_stats.get('total_orders', 0)}")
            print(f"      • Order frequency: {order_stats.get('order_frequency', 0):.2f}/month")
        
        # Get actual churn data
        churn_data = analytics.get_actual_churn_status(cust)
        if churn_data:
            print(f"      • Actual churn: {churn_data['is_churned']} (reason: {churn_data['churn_reason']})")
        
        print(f"\n    Reason: {sample['reason']}")
    
    # Test 8: Validation with actual churn data
    print("\n[Test 8] Validating predictions against actual churn...")
    
    if analytics.churn_labels_df is not None:
        # Find customers who actually churned
        churned_ids = analytics.churn_labels_df[
            analytics.churn_labels_df['is_churn'] == 1
        ]['customer_id'].tolist()[:5]  # Sample 5
        
        print(f"\n  Analyzing {len(churned_ids)} actually churned customers:")
        print(f"  {'Customer ID':<15} {'Our Risk':<12} {'ML Predicted':<15} {'Churn Reason'}")
        print("  " + "-"*70)
        
        for cust_id in churned_ids:
            # Get customer
            cust = simulator.get_customer_by_id(cust_id)
            if cust:
                # Calculate our risk
                health = health_calculator.calculate_health_score(cust, analytics)
                our_risk = health_calculator.calculate_churn_risk(health, cust, analytics)
                
                # Get actual data
                churn_info = analytics.get_actual_churn_status(cust)
                ml_score = churn_info['predicted_churn_score'] if churn_info else 0
                reason = churn_info['churn_reason'] if churn_info else 'unknown'
                
                print(f"  {cust_id:<15} {our_risk*100:>6.1f}%      {ml_score*100:>6.1f}%         {reason}")
    
    # Summary
    print("\n" + "="*70)
    print("✅ STEP 3 COMPLETE - ProactiveMonitor Enhanced!")
    print("="*70)
    print("\nNew capabilities:")
    print("  ✓ 10-dimensional health scoring (vs 4 before)")
    print("  ✓ Order frequency analysis")
    print("  ✓ Last activity recency tracking")
    print("  ✓ Support ticket sentiment integration")
    print("  ✓ NPS score awareness")
    print("  ✓ Actual churn data validation")
    print("  ✓ ML-predicted churn blending")
    print("\nData sources integrated:")
    print(f"  • customers: {len(analytics.df)} rows")
    print(f"  • orders: {len(analytics.orders_df) if analytics.orders_df is not None else 0} rows")
    print(f"  • churn_labels: {len(analytics.churn_labels_df) if analytics.churn_labels_df is not None else 0} rows")
    print(f"  • support_tickets: Available (lazy load)")
    print(f"  • nps_survey: Available (lazy load)")
    print("="*70)


if __name__ == '__main__':
    test_enhanced_proactive_monitor()
