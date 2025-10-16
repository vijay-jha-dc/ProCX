"""
AgentMAX CX Platform - Main Application
An empathic AI-driven customer experience system powered by LangGraph.
"""
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from models import AgentState, EventType
from utils import EventSimulator, MemoryHandler
from workflows import create_cx_workflow, create_cx_workflow_with_routing, run_workflow
from config import settings


class AgentMAXCX:
    """Main application class for AgentMAX CX Platform."""
    
    def __init__(self, use_routing: bool = True):
        """
        Initialize the AgentMAX CX Platform.
        
        Args:
            use_routing: Use advanced workflow with routing (default: True)
        """
        print("🚀 Initializing AgentMAX CX Platform...")
        
        # Initialize components
        self.event_simulator = EventSimulator()
        self.memory_handler = MemoryHandler()
        
        # Create workflow
        if use_routing:
            print("   Creating advanced workflow with conditional routing...")
            self.workflow = create_cx_workflow_with_routing()
        else:
            print("   Creating standard workflow...")
            self.workflow = create_cx_workflow()
        
        print("✓ AgentMAX CX Platform ready!\n")
    
    def process_event(self, event, verbose: bool = True) -> AgentState:
        """
        Process a customer event through the agent workflow.
        
        Args:
            event: CustomerEvent to process
            verbose: Print detailed progress
            
        Returns:
            Final AgentState with results
        """
        if verbose:
            print(f"\n{'='*70}")
            print(f"🎯 Processing Event: {event.event_id}")
            print(f"{'='*70}")
            print(f"Customer: {event.customer.full_name} ({event.customer.customer_id})")
            print(f"Segment: {event.customer.segment} | Tier: {event.customer.loyalty_tier}")
            print(f"Lifetime Value: ${event.customer.lifetime_value:,.2f}")
            print(f"Event Type: {event.event_type.value}")
            print(f"Description: {event.description}")
            print(f"{'='*70}\n")
        
        # Create initial state
        initial_state = AgentState(
            event=event,
            customer=event.customer
        )
        
        # Run workflow
        start_time = time.time()
        
        if verbose:
            print("⚙️  Running agent workflow...\n")
        
        final_state = run_workflow(self.workflow, initial_state)
        
        # Calculate processing time
        final_state.processing_time = time.time() - start_time
        
        # Save to memory
        self.memory_handler.save_interaction(final_state)
        
        # Display results
        if verbose:
            self._display_results(final_state)
        
        return final_state
    
    def _display_results(self, state: AgentState):
        """Display processing results."""
        print(f"\n{'='*70}")
        print(f"📊 ANALYSIS RESULTS")
        print(f"{'='*70}\n")
        
        # Context Analysis
        print("🔍 Context Analysis:")
        print(f"   Sentiment: {state.sentiment.value if state.sentiment else 'N/A'}")
        print(f"   Urgency Level: {state.urgency_level}/5")
        print(f"   Customer Risk Score: {state.customer_risk_score:.2%}")
        print(f"   Summary: {state.context_summary}\n")
        
        # Pattern Analysis
        print("📈 Pattern Analysis:")
        print(f"   Churn Risk: {state.predicted_churn_risk:.2%}")
        print(f"   Insights: {state.historical_insights}\n")
        
        # Decision
        print("⚖️  Decision:")
        print(f"   Priority: {state.priority_level.upper()}")
        print(f"   Escalation Needed: {'YES ⚠️' if state.escalation_needed else 'NO'}")
        print(f"   Recommended Action: {state.recommended_action}\n")
        
        # Response
        print("💬 Personalized Response:")
        print(f"   Tone: {state.tone or 'professional and empathetic'}")
        print(f"   Empathy Score: {state.empathy_score:.2%}")
        print(f"\n{'-'*70}")
        print(state.personalized_response or "No response generated")
        print(f"{'-'*70}\n")
        
        # Processing Info
        print(f"⏱️  Processing Time: {state.processing_time:.2f}s")
        print(f"{'='*70}\n")
    
    def run_interactive_mode(self):
        """Run the platform in interactive mode."""
        print("\n" + "="*70)
        print("🎮 AgentMAX CX - Interactive Mode")
        print("="*70)
        
        while True:
            print("\nOptions:")
            print("1. Process random event")
            print("2. Process specific scenario")
            print("3. Process VIP customer event")
            print("4. View dataset statistics")
            print("5. View session summary")
            print("6. Exit")
            
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == "1":
                event = self.event_simulator.generate_event()
                self.process_event(event)
            
            elif choice == "2":
                scenarios = self.event_simulator.get_available_scenarios()
                print("\nAvailable scenarios:")
                for i, scenario in enumerate(scenarios, 1):
                    print(f"{i}. {scenario}")
                
                scenario_choice = input("\nSelect scenario (1-5): ").strip()
                try:
                    scenario_idx = int(scenario_choice) - 1
                    if 0 <= scenario_idx < len(scenarios):
                        event = self.event_simulator.generate_scenario(scenarios[scenario_idx])
                        self.process_event(event)
                    else:
                        print("❌ Invalid selection")
                except ValueError:
                    print("❌ Invalid input")
            
            elif choice == "3":
                event = self.event_simulator.generate_event(
                    customer=self.event_simulator.get_random_customer(segment="VIP")
                )
                self.process_event(event)
            
            elif choice == "4":
                stats = self.event_simulator.get_dataset_stats()
                print("\n" + "="*70)
                print("📊 Dataset Statistics")
                print("="*70)
                print(json.dumps(stats, indent=2))
            
            elif choice == "5":
                summary = self.memory_handler.get_session_summary()
                print("\n" + "="*70)
                print("📋 Session Summary")
                print("="*70)
                print(json.dumps(summary, indent=2))
            
            elif choice == "6":
                print("\n👋 Thank you for using AgentMAX CX!")
                break
            
            else:
                print("❌ Invalid option. Please try again.")
    
    def run_demo(self, num_events: int = 3):
        """
        Run a demo with multiple events.
        
        Args:
            num_events: Number of events to process
        """
        print("\n" + "="*70)
        print(f"🎬 AgentMAX CX - Demo Mode ({num_events} events)")
        print("="*70 + "\n")
        
        scenarios = self.event_simulator.get_available_scenarios()[:1]
        
        for i, scenario_name in enumerate(scenarios[:num_events], 1):
            print(f"\n🎯 Demo {i}/{num_events}: {scenario_name}")
            print("-"*70)
            
            try:
                event = self.event_simulator.generate_scenario(scenario_name)
                self.process_event(event, verbose=True)
                
                if i < num_events:
                    input("\nPress Enter to continue to next demo...")
            
            except Exception as e:
                print(f"❌ Error processing event: {e}")
        
        # Show summary
        print("\n" + "="*70)
        print("📊 Demo Summary")
        print("="*70)
        summary = self.memory_handler.get_session_summary()
        print(json.dumps(summary, indent=2))
        print()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AgentMAX CX - Empathic AI Customer Experience Platform"
    )
    parser.add_argument(
        "--mode",
        choices=["interactive", "demo", "test"],
        default="interactive",
        help="Run mode (default: interactive)"
    )
    parser.add_argument(
        "--demo-count",
        type=int,
        default=3,
        help="Number of events in demo mode (default: 3)"
    )
    parser.add_argument(
        "--no-routing",
        action="store_true",
        help="Use simple workflow without routing"
    )
    
    args = parser.parse_args()
    
    # Check for API key
    if not settings.OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("   Please add it to your .env file")
        return 1
    
    # Initialize platform
    platform = AgentMAXCX(use_routing=not args.no_routing)
    
    # Run based on mode
    if args.mode == "interactive":
        platform.run_interactive_mode()
    elif args.mode == "demo":
        platform.run_demo(num_events=args.demo_count)
    elif args.mode == "test":
        # Quick test
        print("🧪 Running quick test...")
        event = platform.event_simulator.generate_event()
        platform.process_event(event)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
