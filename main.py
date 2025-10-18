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
from utils import EventSimulator, MemoryHandler, ProactiveMonitor
from workflows import create_cx_workflow, create_cx_workflow_with_routing, run_workflow
from config import settings


class AgentMAXCX:
    """Main application class for ProCX Platform."""
    
    def __init__(self, use_routing: bool = True):
        """
        Initialize the ProCX Platform.
        
        Args:
            use_routing: Use advanced workflow with routing (default: True)
        """
        print("🚀 Initializing ProCX Platform...")
        
        # Initialize components
        self.event_simulator = EventSimulator()
        self.memory_handler = MemoryHandler()
        self.proactive_monitor = ProactiveMonitor()
        
        # Create workflow
        if use_routing:
            print("   Creating advanced workflow with conditional routing...")
            self.workflow = create_cx_workflow_with_routing()
        else:
            print("   Creating standard workflow...")
            self.workflow = create_cx_workflow()
        
        print("✓ ProCX Platform ready!\n")
    
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
        """Display processing results with DATA INSIGHTS from multiple sheets."""
        print(f"\n{'='*70}")
        print(f"📊 ANALYSIS RESULTS (Powered by Multi-Sheet Dataset)")
        print(f"{'='*70}\n")
        
        # Context Analysis
        print("🔍 Context Analysis:")
        print(f"   Sentiment: {state.sentiment.value if state.sentiment else 'N/A'}")
        print(f"   Urgency Level: {state.urgency_level}/5")
        print(f"   Customer Risk Score: {state.customer_risk_score:.2%}")
        print(f"   Summary: {state.context_summary}\n")
        
        # NEW: Show data-driven insights from multiple sheets
        from utils import DataAnalytics
        analytics = DataAnalytics()
        
        # Cohort comparison (from customers sheet)
        cohort = analytics.compare_with_cohort(state.customer)
        if cohort:
            print("💎 DATA INSIGHTS (Real Customer Database):")
            print(f"   Customer Percentile: {cohort['customer_percentile']:.0f}th percentile in {state.customer.segment} cohort")
            print(f"   Cohort Size: {cohort['cohort_size']} similar customers")
            print(f"   Value vs Average: {'+'if cohort['above_average'] else '-'}${abs(cohort['ltv_difference']):.2f}")
        
        # Churn prediction (from churn_labels sheet)
        churn_data = analytics.get_actual_churn_status(state.customer)
        if churn_data and churn_data.get('predicted_churn_score'):
            print(f"   ML Churn Prediction: {churn_data['predicted_churn_score']:.1%} (from churn_labels sheet)")
        
        # Support history (from support_tickets sheet)
        support = analytics.get_customer_support_history(state.customer)
        if support and support.get('total_tickets', 0) > 0:
            print(f"   Support History: {support['total_tickets']} tickets, {support.get('avg_csat', 0):.1f}/5 avg CSAT")
        
        # Payment reliability (from payments sheet) - NEW!
        payment = analytics.get_customer_payment_reliability(state.customer)
        if payment and payment.get('total_payments', 0) > 0:
            failed = payment['failed_payments']
            total = payment['total_payments']
            print(f"   Payment Reliability: {total - failed}/{total} successful ({(1-payment['failure_rate']):.1%})")
            if payment['failure_rate'] > 0.2:
                print(f"   ⚠️  HIGH payment failure rate - churn risk indicator!")
        
        print()  # Spacing
        
        # Pattern Analysis
        print("📈 Pattern Analysis (Historical Data):")
        print(f"   Churn Risk: {state.predicted_churn_risk:.2%} (60% data + 40% AI)")
        print(f"   Insights: {state.historical_insights}")
        
        # Show similar customers AND similar issues
        if state.similar_patterns:
            pattern = state.similar_patterns[0]
            if pattern.get('similar_customers_count', 0) > 0:
                print(f"   Similar Customers: Found {pattern['similar_customers_count']} with matching profiles")
            
            # NEW: Show issue-based pattern matching results
            if pattern.get('pattern_summary'):
                print(f"   Issue Patterns: {pattern['pattern_summary'][:100]}...")
        
        print()  # Spacing
        
        # Decision
        print("⚖️  Decision:")
        print(f"   Priority: {state.priority_level.upper()}")
        print(f"   Escalation Needed: {'YES ⚠️' if state.escalation_needed else 'NO'}")
        print(f"   Recommended Action: {state.recommended_action}\n")
        
        # Response
        print("💬 Personalized Response:")
        print(f"   Tone: {state.tone or 'professional and empathetic'}")
        if state.empathy_score is not None:
            print(f"   Empathy Score: {state.empathy_score:.2%}")
        print(f"\n{'-'*70}")
        print(state.personalized_response or "No response generated")
        print(f"{'-'*70}\n")
        
        # Processing Info
        print(f"⏱️  Processing Time: {state.processing_time:.2f}s")
        print(f"💾  Memory: Interaction saved to data/memory/{state.customer.customer_id}.jsonl")
        print(f"{'='*70}\n")
    
    def display_health_dashboard(self):
        """Display real-time customer health dashboard."""
        report = self.proactive_monitor.generate_monitoring_report()
        
        print("\n" + "="*70)
        print("📊 CUSTOMER HEALTH DASHBOARD - REAL-TIME MONITORING")
        print("="*70)
        print(f"\n🏢 Total Customers: {report['total_customers']:,}")
        print(f"💚 Average Health Score: {report['avg_health_score']:.1%}")
        print(f"⚠️  Average Churn Risk: {report['avg_churn_risk']:.1%}")
        print(f"\n🚨 AT-RISK CUSTOMERS:")
        print(f"   High Risk (≥60%): {report['customers_at_risk']} customers")
        print(f"   Critical (≥80%): {report['customers_critical']} customers")
        
        print(f"\n📈 HEALTH DISTRIBUTION:")
        dist = report['health_distribution']
        total = report['total_customers']
        
        # ASCII bar charts
        print(f"   🟢 Excellent (≥80%): {dist['excellent']:3d} {'█' * (dist['excellent'] * 50 // total)}")
        print(f"   🟡 Good (60-80%):    {dist['good']:3d} {'█' * (dist['good'] * 50 // total)}")
        print(f"   🟠 Fair (40-60%):    {dist['fair']:3d} {'█' * (dist['fair'] * 50 // total)}")
        print(f"   🔴 Poor (<40%):      {dist['poor']:3d} {'█' * (dist['poor'] * 50 // total)}")
        print("="*70 + "\n")
    
    def _create_proactive_event(self, customer, alert):
        """Helper to create proactive event from health alert."""
        from models import CustomerEvent
        from datetime import datetime
        import time
        
        event_id = f"PROACTIVE_{customer.customer_id}_{int(time.time())}"
        
        return CustomerEvent(
            event_id=event_id,
            customer=customer,
            event_type=EventType.INQUIRY,  # Using existing type
            timestamp=datetime.now(),
            description=f"Proactive retention: Churn risk {alert['churn_risk']:.1%}",
            metadata={
                'is_proactive': True,
                'health_score': alert['health_score'],
                'churn_risk': alert['churn_risk'],
                'risk_level': alert['risk_level'],
                'reasons': alert['reasons']
            }
        )
    
    def run_proactive_demo(self, max_interventions: int = 5):
        """
        🔮 PROACTIVE MODE: Detect at-risk customers and intervene BEFORE they churn!
        
        This is what makes ProCX special - we don't wait for problems,
        we PREDICT and PREVENT them!
        """
        print("\n" + "="*70)
        print("🔮 PROACTIVE CUSTOMER RETENTION SYSTEM - ProCX")
        print("="*70)
        print("\n💡 How it works:")
        print("   1. Continuously monitor ALL customers (not just complaints)")
        print("   2. Analyze 10 health factors (orders, support, NPS, engagement)")
        print("   3. Predict churn risk using REAL data (not guesses)")
        print("   4. Auto-generate personalized retention interventions")
        print("   5. Reach out BEFORE customers complain or leave")
        print("\n" + "="*70 + "\n")
        
        input("Press Enter to scan customer base...")
        
        # Show dashboard first
        self.display_health_dashboard()
        
        input("Press Enter to detect at-risk customers...")
        
        # Detect at-risk customers
        print("\n🔍 Scanning 1,000 customers for churn risk...")
        at_risk = self.proactive_monitor.detect_churn_risks(
            min_churn_risk=0.6,
            min_lifetime_value=2000.0,
            segments=["VIP", "Loyal"]
        )
        
        if not at_risk:
            print("✅ Great news! No high-risk customers detected.")
            return
        
        print(f"\n⚠️  Found {len(at_risk)} at-risk customers requiring intervention!")
        print(f"   Processing top {min(max_interventions, len(at_risk))} priority cases...\n")
        
        # Process top N interventions
        for i, alert in enumerate(at_risk[:max_interventions], 1):
            customer = alert['customer']
            
            print(f"\n{'='*70}")
            print(f"🎯 PROACTIVE INTERVENTION #{i}/{min(max_interventions, len(at_risk))}")
            print(f"{'='*70}")
            print(f"👤 Customer: {customer.full_name}")
            print(f"   ID: {customer.customer_id}")
            print(f"   Segment: {customer.segment} | Tier: {customer.loyalty_tier}")
            print(f"   Lifetime Value: ${customer.lifetime_value:,.2f}")
            print(f"\n📊 Health Analysis:")
            print(f"   Health Score: {alert['health_score']:.1%} {'🟢' if alert['health_score'] >= 0.7 else '🟡' if alert['health_score'] >= 0.5 else '🔴'}")
            print(f"   Churn Risk: {alert['churn_risk']:.1%} {'🔴' if alert['churn_risk'] >= 0.7 else '🟠'}")
            print(f"   Risk Level: {alert['risk_level'].upper()}")
            print(f"   Risk Factors: {', '.join(alert['reasons'][:3])}")
            print(f"\n🎯 Recommended Action: {alert['recommended_action']}")
            print(f"{'='*70}\n")
            
            if i < max_interventions and i < len(at_risk):
                input(f"Press Enter to generate retention message for {customer.first_name}...")
            
            # Create proactive event
            event = self._create_proactive_event(customer, alert)
            
            # Process through workflow
            result = self.process_event(event, verbose=False)
            
            # Display intervention
            print(f"💬 PERSONALIZED RETENTION MESSAGE:")
            print(f"{'-'*70}")
            print(result.personalized_response or "No response generated")
            print(f"{'-'*70}")
            print(f"\n✅ Intervention plan created and ready to deploy!")
            print(f"   Priority: {result.priority_level.upper()}")
            print(f"   Escalation: {'YES - Assign to manager' if result.escalation_needed else 'NO - Automated outreach'}")
            print(f"   Processing Time: {result.processing_time:.2f}s")
            
            if i < max_interventions and i < len(at_risk):
                input("\nPress Enter for next customer...")
        
        # Final summary
        print(f"\n{'='*70}")
        print(f"✅ PROACTIVE SCAN COMPLETE")
        print(f"{'='*70}")
        print(f"\n📈 Results:")
        print(f"   Total Customers Scanned: 1,000")
        print(f"   At-Risk Detected: {len(at_risk)}")
        print(f"   Interventions Generated: {min(max_interventions, len(at_risk))}")
        print(f"   Prevented Churn: Estimated {min(max_interventions, len(at_risk)) * 0.7:.0f} customers saved")
        print(f"   Revenue Protected: ${sum(a['customer'].lifetime_value for a in at_risk[:max_interventions]):,.2f}")
        print(f"\n💡 Key Insight: Proactive beats reactive every time!")
        print(f"{'='*70}\n")
    
    def run_interactive_mode(self):
        """Run the platform in interactive mode."""
        print("\n" + "="*70)
        print("🎮 ProCX - Interactive Mode")
        print("="*70)
        
        # Show quick stats on start
        stats = self.event_simulator.get_dataset_stats()
        print(f"\n📊 Dataset Loaded: {stats['total_customers']} customers")
        print(f"   Segments: VIP ({stats['segments'].get('VIP', 0)}), "
              f"Loyal ({stats['segments'].get('Loyal', 0)}), "
              f"Regular ({stats['segments'].get('Regular', 0)})")
        print(f"   Total LTV: ${stats['lifetime_value_stats']['mean'] * stats['total_customers']:,.0f}")
        
        while True:
            print("\nOptions:")
            print("1. Process random event")
            print("2. Process specific scenario")
            print("3. Process VIP customer event")
            print("4. View customer health dashboard")
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
                self.display_health_dashboard()
            
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
    
    def run_demo(self, num_events: int = 5):
        """
        Run a demo with multiple events.
        
        Args:
            num_events: Number of events to process
        """
        print("\n" + "="*70)
        print(f"🎬 ProCX - REACTIVE Demo Mode")
        print("="*70)
        print("\n💡 Showing reactive customer service (responding to complaints)")
        print("   For PROACTIVE mode, run: python main.py --mode proactive\n")
        
        scenarios = self.event_simulator.get_available_scenarios()
        
        for i, scenario_name in enumerate(scenarios[:num_events], 1):
            print(f"\n{'='*70}")
            print(f"🎯 Scenario {i}/{min(num_events, len(scenarios))}: {scenario_name.replace('_', ' ').title()}")
            print(f"{'='*70}")
            
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
        description="ProCX - Proactive Customer Experience Platform"
    )
    parser.add_argument(
        "--mode",
        choices=["interactive", "demo", "proactive", "test"],
        default="interactive",
        help="Run mode (default: interactive)"
    )
    parser.add_argument(
        "--demo-count",
        type=int,
        default=5,
        help="Number of events in demo mode (default: 5)"
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
    elif args.mode == "proactive":
        platform.run_proactive_demo(max_interventions=5)
    elif args.mode == "test":
        # Quick test
        print("🧪 Running quick test...")
        event = platform.event_simulator.generate_event()
        platform.process_event(event)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
