"""
Demo: Escalation Scenario - VIP Customer with Critical Churn Risk
Shows when ProCX escalates to human intervention
"""
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from main import ProCX
from models import Customer, CustomerEvent, EventType


def safe_print(text: str):
    """Print text safely, handling Unicode encoding errors."""
    try:
        print(text)
    except UnicodeEncodeError:
        ascii_text = text.encode('ascii', 'ignore').decode('ascii')
        print(ascii_text)


def dramatic_print(text: str, delay: float = 0.5):
    """Print with dramatic delay for demo effect."""
    safe_print(text)
    time.sleep(delay)


def simulate_vip_escalation():
    """Simulate a VIP customer scenario that triggers human escalation."""
    
    safe_print("\n" + "="*70)
    safe_print("🚨 ESCALATION SCENARIO DEMO: VIP Customer Crisis")
    safe_print("="*70)
    safe_print("   Demonstrating when ProCX escalates to human agents")
    safe_print("="*70 + "\n")
    
    dramatic_print("📋 SCENARIO: VIP customer shows multiple risk signals", 0.8)
    dramatic_print("   • Multiple support tickets with low satisfaction", 0.5)
    dramatic_print("   • Declining engagement over 60 days", 0.5)
    dramatic_print("   • High lifetime value at risk (₹8,500)", 0.5)
    dramatic_print("   • Platinum tier member", 0.5)
    
    dramatic_print("\n⚙️  Initializing ProCX Platform...", 0.8)
    
    # Initialize ProCX
    procx = ProCX()
    
    # Create VIP customer with escalation triggers
    customer = Customer(
        customer_id="C100567",
        first_name="Rajesh",
        last_name="Malhotra",
        email="rajesh.malhotra@example.com",
        segment="VIP",
        lifetime_value=8500.0,  # High value (> $5000)
        preferred_category="Electronics",
        loyalty_tier="Platinum",
        language="hi",  # Hindi
        phone="+91-9988776655",
        country="India"
    )
    
    dramatic_print(f"\n👤 TARGET CUSTOMER:", 0.6)
    dramatic_print(f"   Name: {customer.full_name}", 0.3)
    dramatic_print(f"   Customer ID: {customer.customer_id}", 0.3)
    dramatic_print(f"   Segment: {customer.segment} (VIP Status)", 0.3)
    dramatic_print(f"   Lifetime Value: ${customer.lifetime_value:,.0f}", 0.3)
    dramatic_print(f"   Loyalty Tier: {customer.loyalty_tier}", 0.3)
    dramatic_print(f"   Language: Hindi", 0.3)
    
    # Create event with HIGH churn risk metadata
    event = CustomerEvent(
        event_id=f"ESCALATION_DEMO_{customer.customer_id}_{int(time.time())}",
        customer=customer,
        event_type=EventType.PROACTIVE_RETENTION,
        timestamp=datetime.now(),
        description="VIP customer with critical churn risk - multiple negative signals",
        metadata={
            'churn_risk': 0.88,  # 88% churn risk
            'predicted_churn_risk': 0.88,
            'health_score': 0.12,
            'risk_level': 'critical',
            'trigger_reason': 'vip_critical_risk',
            'support_tickets': 5,
            'avg_csat': 2.1,  # Low satisfaction
            'days_since_activity': 45,
            'declining_engagement': True
        }
    )
    
    dramatic_print("\n🔍 RISK ANALYSIS:", 0.6)
    dramatic_print("   • Churn Risk: 88% (CRITICAL)", 0.4)
    dramatic_print("   • Health Score: 12% (VERY LOW)", 0.4)
    dramatic_print("   • Recent Support Tickets: 5 (Avg CSAT: 2.1/5.0)", 0.4)
    dramatic_print("   • Days Since Last Activity: 45 days", 0.4)
    
    dramatic_print("\n🧠 Processing through 4-agent workflow...", 0.8)
    
    # Process through agents
    start_time = time.time()
    result = procx.process_proactive_event(event, verbose=False)
    elapsed = time.time() - start_time
    
    dramatic_print(f"✅ Analysis complete in {elapsed:.1f} seconds\n", 0.8)
    
    # Display results
    safe_print("="*70)
    safe_print("📊 DECISION: ESCALATION ANALYSIS")
    safe_print("="*70)
    
    safe_print(f"\n🎯 Recommended Action:")
    safe_print(f"   {result.recommended_action}")
    
    safe_print(f"\n📈 Risk Assessment:")
    safe_print(f"   • Customer Segment: VIP (triggers escalation rule)")
    safe_print(f"   • Lifetime Value: ₹{customer.lifetime_value:,.0f} (> ₹5,000 threshold)")
    safe_print(f"   • Churn Risk: {event.metadata.get('churn_risk', 0)*100:.0f}% (> 80% VIP threshold)")
    safe_print(f"   • Sentiment: {result.sentiment.value if result.sentiment else 'N/A'}")
    safe_print(f"   • Urgency Level: {result.urgency_level}/5")
    safe_print(f"   • Priority: {result.priority_level or 'CRITICAL'}")
    
    # 🔥 TRUST THE AGENT - Check if agent made escalation decision
    safe_print(f"\n🚨 ESCALATION DECISION:")
    
    if result.escalation_needed:
        print("   ╔════════════════════════════════════════════════════╗")
        print("   ║  STATUS: ESCALATED TO HUMAN AGENT                 ║")
        print("   ╚════════════════════════════════════════════════════╝")
        
        print(f"\n   🎯 Recommended Action for Human Agent:")
        print(f"   {result.recommended_action}")
        
        print(f"\n   📋 Escalation Context:")
        print(f"   • Priority Level: {result.priority_level.upper()}")
        print(f"   • Churn Risk: {result.predicted_churn_risk*100:.0f}%" if result.predicted_churn_risk else "   • Churn Risk: HIGH")
        print(f"   • Customer Value: ₹{customer.lifetime_value:,.0f}")
        print(f"   • Urgency: {result.urgency_level}/5 - {'CRITICAL' if result.urgency_level >= 4 else 'HIGH'}")
        
        print(f"\n   🔔 Next Steps for Human Agent:")
        print(f"   1. Review customer history and support tickets")
        print(f"   2. Direct phone call within 2 hours (Language: Hindi)")
        print(f"   3. Consider: {result.recommended_action[:100]}...")
        print(f"   4. Prepare personalized retention offer")
        print(f"   5. Executive review if needed")
        
        # Show escalation message from workflow
        escalation_msgs = [msg for msg in result.messages if msg.get('agent') == 'escalation_handler']
        if escalation_msgs:
            print(f"\n   ℹ️  System Note: {escalation_msgs[-1].get('message', '')[:200]}")
    else:
        print("   ╔════════════════════════════════════════════════════╗")
        print("   ║  STATUS: AUTOMATED INTERVENTION                    ║")
        print("   ╚════════════════════════════════════════════════════╝")
        print(f"\n   Agent decided: No escalation needed")
        print(f"   Handling via automated workflow")
    
    safe_print(f"\n💬 Pre-drafted Message (Hindi):")
    safe_print("="*70)
    if result.personalized_response:
        message_preview = result.personalized_response[:500]
        print(message_preview)
        if len(result.personalized_response) > 500:
            print("...")
    else:
        print("Message generation in progress...")
    safe_print("="*70)
    
    safe_print("\n📋 COMPARISON:")
    safe_print("-"*70)
    safe_print("❌ WITHOUT ESCALATION:")
    safe_print("   • Automated email sent")
    safe_print("   • Generic retention offer")
    safe_print("   • Customer might ignore → Churns")
    safe_print("")
    safe_print("✅ WITH ESCALATION:")
    safe_print("   • Human agent assigned immediately")
    safe_print("   • Personal phone call within 2 hours")
    safe_print("   • Custom retention package (₹8,500 LTV worth saving)")
    safe_print("   • Executive attention to VIP customer")
    safe_print("-"*70)
    
    safe_print("\n" + "="*70)
    safe_print("🎯 KEY INSIGHT: Smart Escalation Rules")
    safe_print("="*70)
    safe_print("ProCX automatically escalates when:")
    safe_print("  1. VIP customers show churn risk > 80%")
    safe_print("  2. High-value customers (LTV > ₹5,000) at critical risk (> 85%)")
    safe_print("  3. Customers with poor satisfaction history (CSAT < 2.5)")
    safe_print("")
    safe_print("This ensures:")
    safe_print("  • High-value customers get human attention")
    safe_print("  • Complex cases handled by experienced agents")
    safe_print("  • Automated system for routine cases")
    safe_print("  • Best use of human resources")
    safe_print("="*70 + "\n")


if __name__ == "__main__":
    try:
        simulate_vip_escalation()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
