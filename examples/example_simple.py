"""
Simple example demonstrating AgentMAX CX Platform usage.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import AgentState, EventType
from utils import EventSimulator
from workflows import create_cx_workflow, run_workflow


def simple_example():
    """Run a simple example of the platform."""
    
    print("="*70)
    print("🎯 AgentMAX CX - Simple Example")
    print("="*70)
    print()
    
    # 1. Initialize simulator
    print("📊 Loading customer data...")
    simulator = EventSimulator()
    stats = simulator.get_dataset_stats()
    print(f"   ✓ Loaded {stats['total_customers']} customers")
    print()
    
    # 2. Generate a test event
    print("🎲 Generating test event...")
    event = simulator.generate_scenario("vip_complaint")
    print(f"   ✓ Event: {event.event_type.value}")
    print(f"   ✓ Customer: {event.customer.full_name} ({event.customer.segment})")
    print(f"   ✓ Description: {event.description}")
    print()
    
    # 3. Create workflow
    print("⚙️  Creating LangGraph workflow...")
    workflow = create_cx_workflow()
    print("   ✓ Workflow ready")
    print()
    
    # 4. Create initial state
    print("🔄 Processing through agents...")
    initial_state = AgentState(
        event=event,
        customer=event.customer
    )
    
    # 5. Run workflow
    final_state = run_workflow(workflow, initial_state)
    print("   ✓ Processing complete")
    print()
    
    # 6. Display results
    print("="*70)
    print("📊 RESULTS")
    print("="*70)
    print()
    
    print(f"🔍 Sentiment: {final_state.sentiment.value if final_state.sentiment else 'N/A'}")
    print(f"⚡ Urgency: {final_state.urgency_level}/5")
    print(f"🎯 Priority: {final_state.priority_level}")
    print(f"🚨 Escalation: {'YES' if final_state.escalation_needed else 'NO'}")
    print(f"📈 Churn Risk: {final_state.predicted_churn_risk:.1%}")
    print()
    
    print("💬 Personalized Response:")
    print("-"*70)
    print(final_state.personalized_response)
    print("-"*70)
    print()
    
    print("✅ Example completed successfully!")


if __name__ == "__main__":
    simple_example()
