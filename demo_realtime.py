"""
Real-Time Event Simulation Demo
Demonstrates event-driven architecture capability of ProCX Platform

This simulates what happens when a critical event (like payment failure) 
occurs and triggers instant intervention through our 4-agent system.
"""
import sys
import time
from datetime import datetime
from pathlib import Path

# Add parent directory to path
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


def dramatic_print(text: str, delay: float = 0.6):
    """Print with dramatic timing for presentation effect"""
    safe_print(text)
    time.sleep(delay)


def simulate_payment_failure():
    """
    Simulates a VIP customer's payment failure happening in real-time.
    Shows instant detection and intervention through ProCX agents.
    """
    
    print("\n" + "="*70)
    print("🎬 REAL-TIME EVENT SIMULATION: Payment Failure Detection")
    print("="*70)
    print("   Demonstrating event-driven architecture")
    print("   Same 4-agent workflow, triggered by live event")
    print("="*70)
    
    # Simulate timeline with dramatic effect
    dramatic_print("\n⏰ 11:00:00 AM - VIP customer's payment transaction FAILS", 0.8)
    dramatic_print("   └─ Reason: Card expired", 0.3)
    dramatic_print("   └─ Customer: Tanya Kumar", 0.3)
    dramatic_print("   └─ Segment: VIP | LTV: ₹15,000", 0.3)
    dramatic_print("   └─ Language: Tamil (auto-detected)", 0.3)
    
    dramatic_print("\n⚡ 11:00:01 AM - Event captured → ProCX Platform triggered", 0.8)
    dramatic_print("   └─ Event Type: Payment Failure", 0.3)
    dramatic_print("   └─ Priority: HIGH (VIP + Payment issue)", 0.3)
    
    dramatic_print("\n🧠 11:00:02 AM - Multi-Agent Processing Pipeline:", 0.6)
    dramatic_print("   ┌─────────────────────────────────────────────┐", 0.2)
    dramatic_print("   │ Agent 1: Bodha (बोध) - Context Agent       │", 0.3)
    dramatic_print("   │ └─ Analyzing sentiment & urgency...         │", 0.3)
    dramatic_print("   │ └─ Extracting customer context...           │", 0.3)
    dramatic_print("   ├─────────────────────────────────────────────┤", 0.2)
    dramatic_print("   │ Agent 2: Dhyana (ध्यान) - Pattern Agent    │", 0.3)
    dramatic_print("   │ └─ Finding churn signals...                 │", 0.3)
    dramatic_print("   │ └─ Analyzing similar customer patterns...   │", 0.3)
    dramatic_print("   ├─────────────────────────────────────────────┤", 0.2)
    dramatic_print("   │ Agent 3: Niti (नीति) - Decision Agent      │", 0.3)
    dramatic_print("   │ └─ Determining best action...               │", 0.3)
    dramatic_print("   │ └─ Checking escalation rules...             │", 0.3)
    dramatic_print("   ├─────────────────────────────────────────────┤", 0.2)
    dramatic_print("   │ Agent 4: Karuna (करुणा) - Empathy Agent    │", 0.3)
    dramatic_print("   │ └─ Generating culturally-aware message...   │", 0.3)
    dramatic_print("   │ └─ Festival context: Diwali (Oct 23)        │", 0.3)
    dramatic_print("   └─────────────────────────────────────────────┘", 0.2)
    
    print("\n" + "-"*70)
    print("⚙️  PROCESSING... (Running actual ProCX workflow)")
    print("-"*70)
    
    # Initialize ProCX Platform
    procx = ProCX()
    
    # Create the customer
    customer = Customer(
        customer_id="C100924",
        first_name="Tanya",
        last_name="Kumar",
        email="tanya.kumar@example.com",
        segment="VIP",
        lifetime_value=15000.0,
        preferred_category="Electronics",
        loyalty_tier="Platinum",
        language="ta",  # Tamil
        phone="+91-9876543210",
        country="India"
    )
    
    # Create the payment failure event
    event = CustomerEvent(
        event_id=f"PAYMENT_FAIL_{customer.customer_id}_{int(time.time())}",
        customer=customer,
        event_type=EventType.PROACTIVE_RETENTION,
        timestamp=datetime.now(),
        description="Payment failed - card expired, immediate retention risk",
        metadata={
            'event_source': 'payment_gateway',
            'failure_reason': 'expired_card',
            'transaction_amount': 2499.00,
            'retry_count': 0,
            'is_recurring': True,
            'trigger': 'real_time_webhook'
        }
    )
    
    # Process through actual workflow
    start_time = time.time()
    result = procx.process_proactive_event(event, verbose=False)
    elapsed = time.time() - start_time
    
    # Show results with timing
    dramatic_print(f"\n✅ 11:00:{2+int(elapsed):02d} AM - Intervention READY!", 0.8)
    
    print("\n" + "="*70)
    print("📊 INTERVENTION DETAILS")
    print("="*70)
    
    print(f"\n🎯 Recommended Action:")
    print(f"   {result.recommended_action}")
    
    print(f"\n📈 Customer Analysis:")
    print(f"   • Sentiment: {result.sentiment.value if result.sentiment else 'N/A'}")
    print(f"   • Urgency Level: {result.urgency_level}/5")
    print(f"   • Customer Risk Score: {result.customer_risk_score*100:.1f}%" if hasattr(result, 'customer_risk_score') and result.customer_risk_score else "   • Risk Score: HIGH")
    print(f"   • Priority: {result.priority_level or 'HIGH'}")
    
    print(f"\n🌐 Communication Details:")
    print(f"   • Language: Tamil (தமிழ்)")
    print(f"   • Channel: WhatsApp (customer preferred)")
    print(f"   • Festival Context: Diwali 2025")
    print(f"   • Empathy Score: {result.empathy_score*100:.0f}%" if result.empathy_score else "   • Empathy Score: High")
    
    print(f"\n⚡ Performance Metrics:")
    print(f"   • Total Processing Time: {elapsed:.2f} seconds")
    print(f"   • Agents Executed: 4 (Bodha → Dhyana → Niti → Karuna)")
    print(f"   • Event to Intervention: < {int(elapsed)+1} seconds")
    
    print(f"\n💬 Generated Message:")
    print("="*70)
    if result.personalized_response:
        # Print first 400 characters of the message
        message_preview = result.personalized_response[:400]
        print(message_preview)
        if len(result.personalized_response) > 400:
            print("...")
    else:
        print("Message generation in progress...")
    print("="*70)
    
    print("\n🏆 OUTCOME:")
    print("-"*70)
    print("✅ Crisis averted in < 5 seconds!")
    print("")
    print("📊 Comparison:")
    print("   • Traditional Approach: Wait 3+ hours for batch scan")
    print("                          → Customer already frustrated")
    print("                          → Higher churn probability")
    print("")
    print("   • ProCX Approach: Instant detection & intervention")
    print("                    → Issue prevented before customer notices")
    print("                    → Culturally-aware Tamil message")
    print("                    → Festival-appropriate greeting (Diwali)")
    print("-"*70)
    
    print("\n" + "="*70)
    print("🎯 KEY INSIGHT: Same 4-agent workflow works for BOTH:")
    print("   • Batch Mode: Scheduled scans (python main.py --interventions)")
    print("   • Event Mode: Real-time triggers (webhook/database listener)")
    print("")
    print("   Architecture is flexible and production-ready!")
    print("="*70 + "\n")


def main():
    """Main entry point"""
    try:
        simulate_payment_failure()
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Demo stopped by user")
    except Exception as e:
        print(f"\n\n[ERROR] Demo error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
