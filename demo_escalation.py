"""
VIP ESCALATION DEMO - ProCX Platform
=====================================
Demonstrates AI-driven escalation decision making for high-value customers.
"""

import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import ProCX
from models.customer import CustomerEvent, Customer, EventType


def safe_print(text):
    """Print text safely, handling Unicode characters"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback: encode to ASCII with replacement
        print(text.encode('ascii', errors='replace').decode('ascii'))


def dramatic_pause(seconds=1.5):
    """Add dramatic pause for presentation"""
    time.sleep(seconds)


def print_section_header(title):
    """Print fancy section header"""
    safe_print(f"\n{'='*80}")
    safe_print(f"  {title}")
    safe_print(f"{'='*80}\n")


def cleanup_demo_data():
    """Clean up demo customer data for fresh run"""
    demo_customer_id = "VIP999999"
    
    # Remove memory files
    memory_file = Path(f"data/memory/{demo_customer_id}.jsonl")
    if memory_file.exists():
        memory_file.unlink()
    
    # Remove escalation files
    escalation_dir = Path("data/escalations")
    if escalation_dir.exists():
        for file in escalation_dir.glob(f"{demo_customer_id}_*.jsonl"):
            file.unlink()
        for file in escalation_dir.glob("active_escalations.jsonl"):
            file.unlink()

    dramatic_pause(0.5)


def run_escalation_demo():
    """VIP customer escalation scenario demonstration"""
    
    # Clean up any previous demo data
    cleanup_demo_data()
    
    print_section_header("VIP CUSTOMER CRISIS DETECTED")
    
    safe_print("SCENARIO:")
    safe_print("   High-value VIP customer showing critical churn signals")
    safe_print("   Multiple support tickets, declining engagement, payment issues")
    safe_print("   Will AI escalate to human agent or handle automatically?")
    safe_print("")
    
    dramatic_pause(2)
    
    # Initialize platform (same as main.py)
    platform = ProCX()
    
    # Create VIP crisis scenario
    safe_print("\n Creating VIP customer profile...")
    dramatic_pause()
    
    vip_customer = Customer(
        customer_id="VIP999999",
        first_name="Priya",
        last_name="Kapoor",
        email="priya.kapoor@example.com",
        segment="VIP",
        lifetime_value=25000.0,
        preferred_category="Electronics",
        loyalty_tier="Platinum",
        phone="+91-98765-43210",
        signup_date=(datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
        country="India",
        avg_order_value=166.67,
        last_active_date=(datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d"),
        opt_in_marketing=True,
        language="en"
    )
    
    safe_print(" VIP Customer Created:")
    safe_print(f"   Name: {vip_customer.full_name}")
    safe_print(f"   Segment: {vip_customer.segment} | Tier: {vip_customer.loyalty_tier}")
    safe_print(f"   Lifetime Value: ${vip_customer.lifetime_value:,.2f}")
    safe_print(f"    Red Flags: VIP with 45 days inactivity, high churn risk expected")
    
    dramatic_pause(2)
    
    # Create event (same as main.py)
    safe_print("\n Creating crisis event...")
    event = CustomerEvent(
        event_id="VIP_CRISIS_001",
        customer=vip_customer,
        event_type=EventType.PROACTIVE_RETENTION,
        timestamp=datetime.now(),
        description="VIP customer with critical churn signals - multiple touchpoints required",
        metadata={
            "priority": "critical",
            "trigger": "Multiple critical signals",
            "demo_scenario": "VIP_escalation"
        }
    )
    
    safe_print(f" Event: {event.event_type.value.upper()}")
    safe_print(f"   Priority: CRITICAL")
    
    dramatic_pause(2)
    
    print_section_header(" AI AGENTS ANALYZING SITUATION...")
    
    safe_print("Running through 4-agent workflow:")
    safe_print("   1⃣ Bodha (Context Agent) - Gathering customer history")
    safe_print("   2⃣ Dhyana (Pattern Agent) - Analyzing behavioral patterns")
    safe_print("   3⃣ Niti (Decision Agent) - Making strategic decision")
    safe_print("   4⃣ Karuna (Empathy Agent) - Crafting personalized response")
    
    dramatic_pause(2)
    
    # Process event (SAME WORKFLOW AS MAIN.PY!)
    safe_print("\n Processing...")
    result = platform.process_proactive_event(event, verbose=True)
    
    dramatic_pause(1)
    
    print_section_header(" AI DECISION RESULTS")
    
    if result.predicted_churn_risk:
        safe_print(f"Churn Risk: {result.predicted_churn_risk:.1%}")
    safe_print(f"Priority Level: {result.priority_level.upper() if result.priority_level else 'CRITICAL'}")
    
    dramatic_pause()
    
    # Show what agent DID (not just recommended)
    if result.action_taken:
        print(f"\n Action Taken by AI:")
        print(f"   {result.action_taken}")
    
    if result.discount_applied:
        print(f"\n Incentive Decision:")
        if result.discount_auto_approved:
            print(f"    EXECUTED: {result.discount_applied}% discount applied")
            print(f"   (Auto-approved within 10% threshold)")
        else:
            print(f"    PENDING: {result.discount_applied}% discount queued for approval")
            print(f"   (Exceeds 10% auto-approval limit)")
    
    dramatic_pause(1.5)
    
    # Show escalation decision
    if result.escalation_needed:
        print_section_header(" ESCALATED TO HUMAN AGENT")
        print("AI determined this situation requires human judgment.")
        print(f"\n Context for Human Agent:")
        print(f"   Priority: {result.priority_level.upper()}")
        print(f"   Recommended Action: {result.recommended_action}")
        print(f"   Churn Risk: {result.predicted_churn_risk:.1%}")
        
        if result.discount_applied and not result.discount_auto_approved:
            print(f"\n Pending Approval:")
            print(f"   AI recommends: {result.discount_applied}% discount")
            print(f"   Requires human approval (>10% threshold)")
        
        print(f"\n Draft Message Prepared:")
        safe_print(f"   {result.personalized_response[:150]}...")
        
        print("\n Human agent can review and execute with one click!")
        
    else:
        print_section_header(" AUTOMATED INTERVENTION COMPLETE")
        print("AI successfully handled the situation without escalation.")
        print(f"\n Action Executed: {result.action_taken}")
        print(f"\n Message Sent:")
        if result.personalized_response:
            safe_print(f"   {result.personalized_response[:150]}...")
        else:
            safe_print("   (Message generation in progress)")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    run_escalation_demo()
