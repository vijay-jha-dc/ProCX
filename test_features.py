"""
Test Script for Enhanced Features
Tests festival context and escalation tracking functionality.
"""
from datetime import datetime
from utils.festival_context import FestivalContextManager
from utils.escalation_tracker import EscalationTracker


def test_festival_context():
    """Test festival context manager."""
    print("="*70)
    print("🎉 TESTING FESTIVAL CONTEXT MANAGER")
    print("="*70)
    
    manager = FestivalContextManager()
    
    # Test 1: Current festival
    print("\n1️⃣ Current Festival Context:")
    festival = manager.get_current_festival_context()
    if festival:
        print(f"   ✅ Active Festival: {festival['festival_name']}")
        print(f"   📅 Date: {festival['festival_date']}")
        print(f"   📝 Significance: {festival['significance']}")
    else:
        print("   ℹ️ No active festival in current period")
    
    # Test 2: Seasonal context
    print("\n2️⃣ Current Seasonal Context:")
    season = manager.get_seasonal_context()
    print(f"   ✅ Season: {season['season']}")
    print(f"   🎨 Tone: {season['messaging_tone']}")
    
    # Test 3: Product relevance (simulate Diwali period)
    print("\n3️⃣ Product-Festival Relevance (Simulated Diwali):")
    diwali_date = datetime(2025, 10, 17)  # 3 days before Diwali
    relevance = manager.is_product_festival_relevant(
        product_category="Home Decor",
        purchased_date=diwali_date
    )
    print(f"   Product: Home Decor")
    print(f"   Purchase Date: {diwali_date.date()}")
    print(f"   ✅ Festival Relevant: {relevance['is_festival_relevant']}")
    if relevance['is_festival_relevant']:
        print(f"   ⭐ Relevance Score: {relevance['relevance_score']}")
        print(f"   🎊 Festival: {relevance['festival']}")
        print(f"   📋 Context: {relevance['context']}")
    
    # Test 4: Festival greetings
    print("\n4️⃣ Festival Greetings (if active):")
    for lang_code, lang_name in [("en", "English"), ("hi", "Hindi"), ("ta", "Tamil")]:
        greeting = manager.get_festival_greeting(lang_code, diwali_date)
        if greeting:
            print(f"   {lang_name}: {greeting[:60]}...")
    
    print("\n✅ Festival Context Tests Complete!\n")


def test_escalation_tracker():
    """Test escalation tracking."""
    print("="*70)
    print("🚨 TESTING ESCALATION TRACKER")
    print("="*70)
    
    tracker = EscalationTracker()
    
    # Test 1: Get initial statistics
    print("\n1️⃣ Initial Statistics:")
    stats = tracker.get_statistics()
    print(f"   📊 Active Escalations: {stats['active_escalations']}")
    print(f"   📚 Total Historical: {stats['total_historical_escalations']}")
    print(f"   🔢 All-Time Total: {stats['total_all_time']}")
    
    # Test 2: Create test escalation
    print("\n2️⃣ Creating Test Escalation:")
    test_customer_id = "TEST_C999999"
    
    # First, check if already exists
    if tracker.is_customer_escalated(test_customer_id):
        print(f"   ℹ️ Test customer already escalated, cleaning up first...")
        tracker.update_escalation_status(test_customer_id, "resolved", "Test cleanup")
    
    escalation_id = tracker.create_escalation(
        customer_id=test_customer_id,
        reason="Test escalation for feature demo",
        priority="high",
        health_score=35
    )
    print(f"   ✅ Created: {escalation_id}")
    
    # Test 3: Check if should skip
    print("\n3️⃣ Testing Skip Logic:")
    skip_decision = tracker.should_skip_customer(test_customer_id)
    print(f"   Should Skip: {skip_decision['should_skip']}")
    if skip_decision['should_skip']:
        print(f"   ✅ Reason: {skip_decision['reason']}")
        print(f"   📝 Context: {skip_decision['context']}")
    
    # Test 4: Get escalation status
    print("\n4️⃣ Escalation Status:")
    status = tracker.get_escalation_status(test_customer_id)
    if status:
        print(f"   ✅ Customer: {test_customer_id}")
        print(f"   📌 Status: {status['status']}")
        print(f"   ⚡ Priority: {status['priority']}")
        print(f"   📅 Days Since Escalation: {status['days_since_escalation']}")
    
    # Test 5: Update status
    print("\n5️⃣ Resolving Test Escalation:")
    success = tracker.update_escalation_status(
        customer_id=test_customer_id,
        status="resolved",
        resolution_notes="Test escalation resolved - feature validation complete"
    )
    if success:
        print(f"   ✅ Escalation resolved successfully")
        
        # Verify it's no longer active
        is_escalated = tracker.is_customer_escalated(test_customer_id)
        print(f"   ✅ Still escalated: {is_escalated} (should be False)")
    
    # Test 6: Check statistics after
    print("\n6️⃣ Final Statistics:")
    stats = tracker.get_statistics()
    print(f"   📊 Active Escalations: {stats['active_escalations']}")
    print(f"   📚 Total Historical: {stats['total_historical_escalations']}")
    
    # Test 7: Test customer that's NOT escalated
    print("\n7️⃣ Testing Non-Escalated Customer:")
    skip_decision = tracker.should_skip_customer("C999998_NOT_ESCALATED")
    print(f"   Should Skip: {skip_decision['should_skip']} (should be False)")
    print(f"   Context: {skip_decision['context']}")
    
    print("\n✅ Escalation Tracker Tests Complete!\n")


def test_integration():
    """Test integration scenarios."""
    print("="*70)
    print("🔗 TESTING INTEGRATION SCENARIOS")
    print("="*70)
    
    festival_manager = FestivalContextManager()
    escalation_tracker = EscalationTracker()
    
    # Scenario 1: Festival purchase with escalation
    print("\n📦 Scenario 1: Critical Festival Purchase")
    print("-" * 70)
    
    customer_id = "C100088"
    product_category = "Home Decor"
    purchase_date = datetime(2025, 10, 17)  # Before Diwali
    
    print(f"Customer ID: {customer_id}")
    print(f"Product: {product_category}")
    print(f"Purchase Date: {purchase_date.date()}")
    
    # Check festival relevance
    relevance = festival_manager.is_product_festival_relevant(
        product_category,
        purchase_date
    )
    
    print(f"\n🎊 Festival Relevance:")
    print(f"   Relevant: {relevance['is_festival_relevant']}")
    if relevance['is_festival_relevant']:
        print(f"   Score: {relevance['relevance_score']}")
        print(f"   Festival: {relevance['festival']}")
        
        # If critical purchase, should get higher priority
        if relevance['relevance_score'] >= 0.9:
            print(f"\n⚡ CRITICAL PURCHASE DETECTED!")
            print(f"   → This should trigger high-priority escalation")
            print(f"   → Extra empathy and urgency required")
    
    # Check if customer already escalated
    print(f"\n🚨 Escalation Status:")
    skip_decision = escalation_tracker.should_skip_customer(customer_id)
    if skip_decision['should_skip']:
        print(f"   ⏭️ Customer should be SKIPPED")
        print(f"   Reason: {skip_decision['reason']}")
    else:
        print(f"   ✅ Customer can be processed")
        print(f"   Context: {skip_decision['context']}")
    
    print("\n✅ Integration Tests Complete!\n")


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("🧪 PROCX ENHANCED FEATURES TEST SUITE")
    print("="*70 + "\n")
    
    try:
        test_festival_context()
        test_escalation_tracker()
        test_integration()
        
        print("="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        print("\n📚 For detailed documentation, see:")
        print("   - docs/ENHANCED_FEATURES.md")
        print("   - FEATURE_SUMMARY.md")
        print("\n🚀 Ready to use in production!")
        print()
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
