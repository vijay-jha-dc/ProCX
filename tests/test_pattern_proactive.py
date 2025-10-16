"""
Test enhanced Pattern Agent with proactive prediction capabilities.
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents import create_pattern_agent
from models import Customer, CustomerEvent, AgentState, EventType, SentimentType
from utils import EventSimulator


def test_proactive_pattern_agent():
    """Test the enhanced Pattern Agent with proactive features."""
    print("="*70)
    print("🧠 ENHANCED PATTERN AGENT - Proactive Prediction Test")
    print("="*70)
    
    # Initialize
    pattern_agent = create_pattern_agent()
    simulator = EventSimulator()
    
    # Test 1: Get a VIP customer
    print("\n" + "="*70)
    print("TEST 1: Proactive Predictions for VIP Customer")
    print("="*70)
    
    vip_customer = simulator.get_random_customer(segment="VIP")
    if not vip_customer:
        print("❌ No VIP customers found")
        return
    
    print(f"\n✓ Selected: {vip_customer.full_name}")
    print(f"  Segment: {vip_customer.segment}")
    print(f"  LTV: ${vip_customer.lifetime_value:,.2f}")
    print(f"  Tier: {vip_customer.loyalty_tier}")
    
    # Create a proactive retention event
    proactive_event = CustomerEvent(
        event_id="PROACTIVE_001",
        customer=vip_customer,
        event_type=EventType.PROACTIVE_RETENTION,
        timestamp=datetime.now(),
        description="Proactive churn prevention outreach",
        metadata={"reason": "health_score_declining"}
    )
    
    # Create state with context (simulated)
    state = AgentState(
        event=proactive_event,
        customer=vip_customer,
        context_summary="Customer showing signs of disengagement",
        sentiment=SentimentType.NEUTRAL,
        urgency_level=3,
        customer_risk_score=0.45
    )
    
    # Test future behavior prediction
    print("\n📊 Generating Proactive Predictions...")
    predictions = pattern_agent.predict_future_behavior(state)
    
    print(f"\n🔮 BEHAVIOR PREDICTIONS:")
    print(f"   Current Health Score: {predictions['health_score']:.2%}")
    print(f"   Current Churn Risk: {predictions['churn_risk']:.2%}")
    
    print(f"\n📅 FUTURE TIMEFRAMES:")
    for timeframe in ['predictions_30_days', 'predictions_60_days', 'predictions_90_days']:
        pred = predictions[timeframe]
        print(f"   {pred['days']} days:")
        print(f"     Churn Probability: {pred['churn_probability']:.2%}")
        print(f"     Engagement Probability: {pred['engagement_probability']:.2%}")
        print(f"     Urgency: {pred['intervention_urgency'].upper()}")
    
    window = predictions['optimal_intervention_window']
    print(f"\n⏰ OPTIMAL INTERVENTION WINDOW:")
    print(f"   Timeframe: {window['start_days']}-{window['end_days']} days")
    print(f"   Urgency Level: {window['urgency'].upper()}")
    print(f"   Recommendation: {window['message']}")
    
    print(f"\n🎯 RECOMMENDED PROACTIVE ACTIONS:")
    for i, action in enumerate(predictions['recommended_proactive_actions'], 1):
        print(f"   {i}. [{action['priority'].upper()}] {action['action']}")
        print(f"      → {action['description']}")
        print(f"      Expected Impact: {action['expected_impact']}")
    
    # Test 2: Generate comprehensive proactive insights
    print("\n" + "="*70)
    print("TEST 2: Comprehensive Proactive Insights")
    print("="*70)
    
    insights = pattern_agent.generate_proactive_insights(state)
    print(f"\n{insights}")
    
    # Test 3: Compare Reactive vs Proactive Analysis
    print("\n" + "="*70)
    print("TEST 3: Reactive vs Proactive Event Analysis")
    print("="*70)
    
    # Reactive event (complaint)
    reactive_event = CustomerEvent(
        event_id="REACTIVE_001",
        customer=vip_customer,
        event_type=EventType.COMPLAINT,
        timestamp=datetime.now(),
        description="Order was delayed by 3 days",
        metadata={}
    )
    
    reactive_state = AgentState(
        event=reactive_event,
        customer=vip_customer,
        context_summary="Customer complaint about delivery delay",
        sentiment=SentimentType.NEGATIVE,
        urgency_level=4,
        customer_risk_score=0.65
    )
    
    print("\n📍 REACTIVE EVENT (Complaint):")
    print("   Event: Customer complains about delay")
    print("   Analysis: Responding to existing problem")
    
    # Proactive event (retention)
    print("\n📍 PROACTIVE EVENT (Retention):")
    print("   Event: System detected churn risk")
    print("   Analysis: Preventing future problem")
    
    proactive_insights_detailed = pattern_agent.generate_proactive_insights(state)
    print(f"\n{proactive_insights_detailed}")
    
    # Test 4: Different customer segments
    print("\n" + "="*70)
    print("TEST 4: Proactive Predictions by Segment")
    print("="*70)
    
    segments = ["VIP", "Loyal", "Regular"]
    for segment in segments:
        customer = simulator.get_random_customer(segment=segment)
        if not customer:
            continue
        
        test_state = AgentState(
            event=proactive_event,
            customer=customer,
            context_summary=f"Proactive analysis for {segment} customer",
            sentiment=SentimentType.NEUTRAL,
            urgency_level=2,
            customer_risk_score=0.3
        )
        
        pred = pattern_agent.predict_future_behavior(test_state)
        
        print(f"\n{segment} Customer: {customer.full_name}")
        print(f"   LTV: ${customer.lifetime_value:,.2f}")
        print(f"   Health: {pred['health_score']:.2%}")
        print(f"   Churn Risk: {pred['churn_risk']:.2%}")
        print(f"   Intervention: {pred['optimal_intervention_window']['urgency']}")
        print(f"   Top Action: {pred['recommended_proactive_actions'][0]['action'] if pred['recommended_proactive_actions'] else 'None'}")
    
    print("\n" + "="*70)
    print("✅ Enhanced Pattern Agent Test Complete!")
    print("="*70)


if __name__ == "__main__":
    test_proactive_pattern_agent()
