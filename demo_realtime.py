"""
Real-Time Event Demo - ProCX Platform
======================================
Demonstrates instant event-driven intervention for payment failures.
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
    """Simulates real-time payment failure intervention"""
    
    print("\n" + "="*70)
    print(" REAL-TIME EVENT: Payment Failure Detection")
    print("="*70)
    
    # Simulate timeline with dramatic effect
    dramatic_print("\n 11:00:00 AM - VIP customer payment FAILS", 0.8)
    dramatic_print("    Customer: Tanya Kumar | VIP | LTV: $15,000", 0.3)
    dramatic_print("    Reason: Card expired", 0.3)
    
    dramatic_print("\n 11:00:01 AM - Event captured, AI agents triggered", 0.8)
    
    dramatic_print("\n 11:00:02 AM - Multi-Agent Processing:", 0.6)
    dramatic_print("    Agent 1: Context Analysis", 0.3)
    dramatic_print("    Agent 2: Pattern Recognition", 0.3)
    dramatic_print("    Agent 3: Decision Making", 0.3)
    dramatic_print("    Agent 4: Message Generation (Tamil)", 0.3)
    
    print("\n" + "-"*70)
    print("  PROCESSING...")
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
        signup_date="2023-01-15",
        country="India",
        avg_order_value=1500.0,
        last_active_date="2025-10-25",
        opt_in_marketing=True
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
    dramatic_print(f"\n 11:00:{2+int(elapsed):02d} AM - Intervention READY!", 0.8)
    
    print("\n" + "="*70)
    print(" INTERVENTION DETAILS")
    print("="*70)
    
    if result.recommended_action:
        print(f"\n Action:")
        print(f"   {result.recommended_action}")
    
    print(f"\n Analysis:")
    print(f"   • Urgency: {result.urgency_level}/5" if result.urgency_level else "   • Urgency: HIGH")
    print(f"   • Priority: {result.priority_level or 'CRITICAL'}")
    
    print(f"\n Communication:")
    print(f"   • Language: Tamil")
    print(f"   • Channel: WhatsApp")
    print(f"   • Processing Time: {elapsed:.2f} seconds")
    
    if result.personalized_response:
        print(f"\n Generated Message Preview:")
        print("-"*70)
        print(result.personalized_response[:300] + "...")
        print("-"*70)
    
    print("\n" + "="*70)
    print(f" Event-to-Intervention: {int(elapsed)+1} seconds")
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
