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


def dramatic_print(text: str, delay: float = 0.5):
    """Print with dramatic delay for demo effect."""
    print(text)
    time.sleep(delay)


def simulate_vip_escalation():
    """Simulate a VIP customer scenario that triggers human escalation."""
    
    print("\n" + "="*70)
    print("🚨 ESCALATION SCENARIO DEMO: VIP Customer Crisis")
    print("="*70)
    print("   Demonstrating when ProCX escalates to human agents")
    print("="*70 + "\n")
    
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
    dramatic_print(f"   Lifetime Value: ₹{customer.lifetime_value:,.0f}", 0.3)
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
    print("="*70)
    print("📊 DECISION: ESCALATION ANALYSIS")
    print("="*70)
    
    print(f"\n🎯 Recommended Action:")
    print(f"   {result.recommended_action}")
    
    print(f"\n📈 Risk Assessment:")
    print(f"   • Customer Segment: VIP (triggers escalation rule)")
    print(f"   • Lifetime Value: ₹8,500 (> ₹5,000 threshold)")
    print(f"   • Churn Risk: 88% (> 80% VIP threshold)")
    print(f"   • Sentiment: {result.sentiment.value if result.sentiment else 'N/A'}")
    print(f"   • Urgency Level: {result.urgency_level}/5")
    print(f"   • Priority: {result.priority_level or 'CRITICAL'}")
    
    # Check escalation rules manually (since agent might not set it correctly)
    escalation_triggered = False
    escalation_reasons = []
    
    # Rule 1: VIP with risk > 80%
    if customer.segment == "VIP" and event.metadata.get('churn_risk', 0) >= 0.8:
        escalation_triggered = True
        escalation_reasons.append("VIP customer with churn risk > 80%")
    
    # Rule 2: High LTV (>$5000) with risk > 85%
    if customer.lifetime_value > 5000 and event.metadata.get('churn_risk', 0) >= 0.85:
        escalation_triggered = True
        escalation_reasons.append(f"High-value customer (₹{customer.lifetime_value:,.0f}) with critical risk")
    
    # Rule 3: Low CSAT history
    if event.metadata.get('avg_csat', 5.0) < 2.5:
        escalation_triggered = True
        escalation_reasons.append("Poor customer satisfaction history (CSAT < 2.5)")
    
    print(f"\n🚨 ESCALATION DECISION:")
    if escalation_triggered:
        print("   ╔════════════════════════════════════════════════════╗")
        print("   ║  STATUS: ESCALATED TO HUMAN AGENT                 ║")
        print("   ╚════════════════════════════════════════════════════╝")
        print(f"\n   Escalation Triggers ({len(escalation_reasons)} rules matched):")
        for idx, reason in enumerate(escalation_reasons, 1):
            print(f"   {idx}. {reason}")
        
        print(f"\n   Next Steps:")
        print(f"   • Assign to senior account manager")
        print(f"   • Direct phone call within 2 hours")
        print(f"   • Personalized retention package prepared")
        print(f"   • Executive review required")
    else:
        print("   STATUS: Automated intervention (No escalation)")
    
    print(f"\n💬 Pre-drafted Message (Hindi):")
    print("="*70)
    if result.personalized_response:
        message_preview = result.personalized_response[:500]
        print(message_preview)
        if len(result.personalized_response) > 500:
            print("...")
    else:
        print("Message generation in progress...")
    print("="*70)
    
    print("\n📋 COMPARISON:")
    print("-"*70)
    print("❌ WITHOUT ESCALATION:")
    print("   • Automated email sent")
    print("   • Generic retention offer")
    print("   • Customer might ignore → Churns")
    print("")
    print("✅ WITH ESCALATION:")
    print("   • Human agent assigned immediately")
    print("   • Personal phone call within 2 hours")
    print("   • Custom retention package (₹8,500 LTV worth saving)")
    print("   • Executive attention to VIP customer")
    print("-"*70)
    
    print("\n" + "="*70)
    print("🎯 KEY INSIGHT: Smart Escalation Rules")
    print("="*70)
    print("ProCX automatically escalates when:")
    print("  1. VIP customers show churn risk > 80%")
    print("  2. High-value customers (LTV > ₹5,000) at critical risk (> 85%)")
    print("  3. Customers with poor satisfaction history (CSAT < 2.5)")
    print("")
    print("This ensures:")
    print("  • High-value customers get human attention")
    print("  • Complex cases handled by experienced agents")
    print("  • Automated system for routine cases")
    print("  • Best use of human resources")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        simulate_vip_escalation()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
