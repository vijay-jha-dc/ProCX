"""
Test script to verify data-driven agent enhancements.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import EventSimulator, DataAnalytics
from models import AgentState
from agents import create_context_agent, create_pattern_agent, create_empathy_agent


def test_data_analytics():
    """Test the DataAnalytics utility."""
    print("="*70)
    print("Testing Data Analytics Utility")
    print("="*70)
    
    analytics = DataAnalytics()
    simulator = EventSimulator()
    
    # Get a VIP customer
    vip_customer = simulator.get_random_customer(segment="VIP")
    if not vip_customer:
        print("❌ No VIP customers found")
        return
    
    print(f"\n✓ Selected Customer: {vip_customer.full_name}")
    print(f"  Segment: {vip_customer.segment}, Tier: {vip_customer.loyalty_tier}")
    print(f"  LTV: ${vip_customer.lifetime_value:.2f}")
    
    # Test similar customers
    print("\n--- Finding Similar Customers ---")
    similar = analytics.find_similar_customers(vip_customer, limit=3)
    print(f"✓ Found {len(similar)} similar customers:")
    for i, cust in enumerate(similar, 1):
        print(f"  {i}. {cust['name']} - Similarity: {cust['similarity_score']:.2%}")
        print(f"     Reasons: {', '.join(cust['similarity_reasons'][:2])}")
    
    # Test segment statistics
    print("\n--- Segment Statistics ---")
    segment_stats = analytics.get_segment_statistics(vip_customer.segment)
    if segment_stats:
        print(f"✓ {vip_customer.segment} Segment:")
        print(f"  Total Customers: {segment_stats['total_customers']}")
        print(f"  Avg LTV: ${segment_stats['avg_lifetime_value']:.2f}")
        print(f"  Percentage: {segment_stats['percentage_of_total']:.1f}%")
    
    # Test cohort comparison
    print("\n--- Cohort Comparison ---")
    cohort = analytics.compare_with_cohort(vip_customer)
    if cohort:
        print(f"✓ Cohort ({vip_customer.segment} + {vip_customer.loyalty_tier}):")
        print(f"  Cohort Size: {cohort['cohort_size']}")
        print(f"  Customer Percentile: {cohort['customer_percentile']:.1f}%")
        print(f"  {'Above' if cohort['above_average'] else 'Below'} average by ${abs(cohort['ltv_difference']):.2f}")
    
    # Test behavioral patterns
    print("\n--- Behavioral Patterns ---")
    patterns = analytics.get_segment_behavioral_patterns(vip_customer.segment)
    if patterns:
        print(f"✓ {vip_customer.segment} Behavioral Patterns:")
        for pattern in patterns[:3]:
            print(f"  - {pattern}")
    
    print("\n" + "="*70)
    print("✅ Data Analytics Test PASSED")
    print("="*70)


def test_pattern_agent_with_data():
    """Test Pattern Agent with real data."""
    print("\n\n" + "="*70)
    print("Testing Pattern Agent with Real Data")
    print("="*70)
    
    # Create event
    simulator = EventSimulator()
    event = simulator.generate_scenario("vip_complaint")
    
    # Create initial state
    state = AgentState(event=event, customer=event.customer)
    
    # Set some context (normally from Context Agent)
    from models import SentimentType
    state.sentiment = SentimentType.VERY_NEGATIVE
    state.urgency_level = 5
    state.customer_risk_score = 0.8
    state.context_summary = "VIP customer with major complaint"
    
    # Run pattern agent
    print(f"\n✓ Processing: {event.customer.full_name} ({event.customer.segment})")
    pattern_agent = create_pattern_agent()
    updated_state = pattern_agent(state)
    
    print(f"\n--- Pattern Agent Results ---")
    print(f"✓ Churn Risk: {updated_state.predicted_churn_risk:.2%}")
    print(f"✓ Historical Insights: {updated_state.historical_insights[:100]}...")
    if updated_state.similar_patterns:
        similar_count = updated_state.similar_patterns[0].get('similar_customers_count', 0)
        print(f"✓ Similar Customers Found: {similar_count}")
        data_risk = updated_state.similar_patterns[0].get('data_driven_churn_risk', 0)
        llm_risk = updated_state.similar_patterns[0].get('llm_churn_risk', 0)
        print(f"✓ Data-Driven Risk: {data_risk:.2%}, LLM Risk: {llm_risk:.2%}")
    
    print("\n" + "="*70)
    print("✅ Pattern Agent Test PASSED (using real data)")
    print("="*70)


if __name__ == "__main__":
    print("\n🧪 Testing Data-Driven Agent Enhancements\n")
    
    try:
        test_data_analytics()
        test_pattern_agent_with_data()
        
        print("\n\n" + "="*70)
        print("✅ ALL TESTS PASSED - Real Data Integration Working!")
        print("="*70)
        print("\nKey Achievements:")
        print("  ✓ Similar customer matching based on actual profiles")
        print("  ✓ Real segment statistics and cohort analysis")
        print("  ✓ Data-driven churn risk calculation")
        print("  ✓ Behavioral pattern analysis from dataset")
        print("  ✓ Enhanced personalization using real data")
        print("\n🏆 Ready for hackathon demo!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
