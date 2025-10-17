"""
Test script for ProactiveMonitor - Demonstrates churn risk detection.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import ProactiveMonitor


def test_proactive_monitor():
    """Test the ProactiveMonitor functionality."""
    print("="*70)
    print("🧠 PROACTIVE MONITOR - Churn Risk Detection Test")
    print("="*70)
    
    # Initialize monitor
    monitor = ProactiveMonitor()
    
    # Test 1: Detect churn risks
    print("\n" + "="*70)
    print("TEST 1: Detecting At-Risk Customers")
    print("="*70)
    
    at_risk = monitor.detect_churn_risks(
        min_churn_risk=0.3,  # Lowered threshold to see more customers
        min_lifetime_value=2000.0,
        segments=["VIP", "Loyal"]  # Focus on valuable customers
    )
    
    if at_risk:
        print(f"\n⚠️  Found {len(at_risk)} at-risk customers!\n")
        
        # Show top 5 most at-risk
        for i, alert in enumerate(at_risk[:5], 1):
            customer = alert['customer']
            print(f"{i}. {customer.full_name} ({customer.customer_id})")
            print(f"   Segment: {customer.segment} | Tier: {customer.loyalty_tier}")
            print(f"   LTV: ${customer.lifetime_value:,.2f}")
            print(f"   Health Score: {alert['health_score']:.2%} | Churn Risk: {alert['churn_risk']:.2%}")
            print(f"   Risk Level: {alert['risk_level'].upper()}")
            print(f"   Reasons: {', '.join(alert['reasons'])}")
            print(f"   Recommended Action: {alert['recommended_action']}")
            if alert['cohort_percentile']:
                print(f"   Cohort Percentile: {alert['cohort_percentile']:.0f}%")
            print()
    else:
        print("\n✅ No at-risk customers found!")
    
    # Test 2: High-value inactivity detection
    print("\n" + "="*70)
    print("TEST 2: Detecting Inactive High-Value Customers")
    print("="*70)
    
    inactive = monitor.detect_high_value_inactivity(
        min_lifetime_value=5000.0,
        inactivity_threshold_days=60
    )
    
    if inactive:
        print(f"\n⚠️  Found {len(inactive)} inactive high-value customers!\n")
        
        for i, alert in enumerate(inactive[:5], 1):
            customer = alert['customer']
            print(f"{i}. {customer.full_name}")
            print(f"   LTV: ${customer.lifetime_value:,.2f}")
            print(f"   Health Score: {alert['health_score']:.2%}")
            print(f"   Est. Inactivity: ~{alert['estimated_inactivity_days']} days")
            print(f"   Action: {alert['recommended_action']}")
            print()
    else:
        print("\n✅ No inactive high-value customers!")
    
    # Test 3: Generate monitoring report
    print("\n" + "="*70)
    print("TEST 3: Overall Customer Health Report")
    print("="*70)
    
    report = monitor.generate_monitoring_report()
    
    print(f"\n📊 Customer Health Overview:")
    print(f"   Total Customers: {report['total_customers']}")
    print(f"   Average Health Score: {report['avg_health_score']:.2%}")
    print(f"   Average Churn Risk: {report['avg_churn_risk']:.2%}")
    print(f"   Customers at Risk (≥60%): {report['customers_at_risk']}")
    print(f"   Critical Risk (≥80%): {report['customers_critical']}")
    
    print(f"\n📈 Health Distribution:")
    dist = report['health_distribution']
    print(f"   Excellent (≥80%): {dist['excellent']} customers")
    print(f"   Good (60-80%): {dist['good']} customers")
    print(f"   Fair (40-60%): {dist['fair']} customers")
    print(f"   Poor (<40%): {dist['poor']} customers")
    
    # Test 4: VIP-only analysis
    print("\n" + "="*70)
    print("TEST 4: VIP Customers At Risk")
    print("="*70)
    
    vip_risks = monitor.detect_churn_risks(
        min_churn_risk=0.2,  # Lower threshold for demo
        min_lifetime_value=1000.0,
        segments=["VIP"]
    )
    
    print(f"\n⚠️  VIP Customers Requiring Attention: {len(vip_risks)}")
    
    if vip_risks:
        print("\n🚨 PRIORITY ALERTS - These VIPs need immediate attention:\n")
        for i, alert in enumerate(vip_risks[:3], 1):
            customer = alert['customer']
            print(f"{i}. {customer.full_name}")
            print(f"   💰 LTV: ${customer.lifetime_value:,.2f}")
            print(f"   ❤️  Health: {alert['health_score']:.2%}")
            print(f"   ⚠️  Churn Risk: {alert['churn_risk']:.2%}")
            print(f"   🎯 Action: {alert['recommended_action']}")
            print()
    
    print("="*70)
    print("✅ Proactive Monitor Test Complete!")
    print("="*70)


if __name__ == "__main__":
    test_proactive_monitor()
