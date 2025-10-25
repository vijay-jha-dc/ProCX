"""Test discount auto-approval feature"""
from main import ProCX
from models import Customer, CustomerEvent, EventType
from datetime import datetime

# Use REAL customer from dataset who has high churn risk
# C100924 = Tanya Kumar (84.2% churn risk from dashboard)
customer = Customer(
    customer_id='C100924',
    first_name='Tanya',
    last_name='Kumar',
    email='tanya.kumar@example.com',
    segment='Occasional',
    lifetime_value=1016.23,
    preferred_category='Electronics',
    loyalty_tier='Bronze',
    language='en',
    phone='+91-9876543210',
    country='India'
)

# Create proactive retention event
event = CustomerEvent(
    event_id='TEST_EVENT_DISCOUNT',
    customer=customer,
    event_type=EventType.PROACTIVE_RETENTION,
    timestamp=datetime.now(),
    description='Proactive retention - high churn risk customer',
    metadata={'test_discount': True}
)

print("\n" + "="*70)
print("TESTING AUTO-DISCOUNT FEATURE")
print("="*70)
print(f"Customer: {customer.full_name} ({customer.customer_id})")
print(f"Expected Churn Risk: 84.2% (from dashboard)")
print(f"Expected Discount: 10% (churn risk >80%)")
print(f"LTV: ${customer.lifetime_value:,.2f}")
print("\nProcessing through 4-agent workflow...")

procx = ProCX()
result = procx.process_proactive_event(event, verbose=False)

print("\n" + "="*70)
print("RESULTS")
print("="*70)
print(f"[OK] Discount Applied: {result.discount_applied}%")
print(f"[OK] Auto-Approved: {result.discount_auto_approved}")
print(f"[OK] Escalation Needed: {result.escalation_needed}")
print(f"[OK] Priority: {result.priority_level}")
print(f"\n📋 Recommended Action:")
print(f"   {result.recommended_action}")

# Check messages for discount confirmation
discount_msgs = [msg for msg in result.messages if 'AUTO-APPROVED' in msg.get('message', '') or 'discount' in msg.get('message', '').lower()]
if discount_msgs:
    print(f"\n💬 Discount Messages:")
    for msg in discount_msgs:
        print(f"   [{msg['agent']}] {msg['message']}")

if result.personalized_response:
    print(f"\n📧 Generated Message Preview:")
    print("-"*70)
    print(result.personalized_response[:400])
    if len(result.personalized_response) > 400:
        print("...")
    print("-"*70)
else:
    print("\n[WARN] No message generated")

print("\n" + "="*70 + "\n")
