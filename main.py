"""
ProCX Platform - Proactive Customer Experience System

100% proactive multi-agent AI system for customer churn prevention.
Built for AgentMAX Hackathon 2025.
"""
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from models import AgentState, EventType, Customer, CustomerEvent
from utils import MemoryHandler, ProactiveMonitor
from workflows import create_cx_workflow, run_workflow
from config import settings


def safe_print(text: str):
    """
    Print text safely, handling Unicode encoding errors.
    Falls back to ASCII-only output if terminal doesn't support Unicode.
    """
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback: replace non-ASCII characters
        ascii_text = text.encode('ascii', 'ignore').decode('ascii')
        print(ascii_text)


class ProCX:
    """ProCX Platform - 100% Proactive-only customer experience system."""
    
    def __init__(self):
        """Initialize the ProCX Platform."""
        print(">> Initializing ProCX Platform (Proactive Mode)...")
        
        # Initialize components
        self.memory_handler = MemoryHandler()
        self.proactive_monitor = ProactiveMonitor()
        
        # Create workflow
        print("   Creating proactive workflow with multi-agent system...")
        self.workflow = create_cx_workflow()
        
        print("[OK] ProCX Platform ready!\n")
    
    def process_proactive_event(self, event: CustomerEvent, verbose: bool = True) -> AgentState:
        """
        Process a proactive event through the agent workflow.
        
        Args:
            event: Customer event to process
            verbose: Print detailed output
            
        Returns:
            Final agent state after workflow
        """
        # 🔥 NEW: Check if customer was already contacted today
        recent_history = self.memory_handler.get_recent_interactions(
            event.customer.customer_id,
            days=1  # Last 24 hours
        )
        
        if recent_history:
            last_interaction = recent_history[0]
            timestamp = datetime.fromisoformat(last_interaction['timestamp'])
            hours_ago = (datetime.now() - timestamp).total_seconds() / 3600
            
            if hours_ago < 24:
                if verbose:
                    print(f"\n{'='*70}")
                    print(f"[SKIP] Customer already contacted {hours_ago:.1f} hours ago")
                    print(f"[SKIP] {event.customer.full_name} ({event.customer.customer_id})")
                    print(f"{'='*70}\n")
                
                # Return the previous state instead of re-processing
                return AgentState(
                    customer=event.customer,
                    event=event,
                    messages=[{
                        "agent": "duplicate_prevention",
                        "message": f"Skipped: Already contacted {hours_ago:.1f} hours ago",
                        "timestamp": datetime.now().isoformat()
                    }]
                )
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"[TARGET] PROACTIVE INTERVENTION")
            print(f"{'='*70}")
            print(f"[CUSTOMER] {event.customer.full_name} ({event.customer.customer_id})")
            print(f"   Segment: {event.customer.segment} | Tier: {event.customer.loyalty_tier}")
            print(f"   Lifetime Value: ${event.customer.lifetime_value:,.2f}")
        
        # Create initial state
        initial_state = AgentState(
            customer=event.customer,
            event=event,
            messages=[]
        )
        
        # Run through workflow
        start_time = time.time()
        try:
            final_state = run_workflow(self.workflow, initial_state)
            elapsed = time.time() - start_time
            
            if verbose:
                print(f"\n[TIME] Processing time: {elapsed:.2f} seconds")
                print(f"{'='*70}\n")
            
            # Store in memory
            self.memory_handler.save_interaction(final_state)
            
            return final_state
            
        except Exception as e:
            print(f"\n[ERROR] Error processing event: {str(e)}")
            if verbose:
                import traceback
                traceback.print_exc()
            return initial_state
    
    def run_proactive_scan(
        self,
        min_churn_risk: float = 0.6,
        max_interventions: int = 5,
        verbose: bool = True
    ) -> list:
        """
        Run proactive scan to identify and intervene with at-risk customers.
        
        Args:
            min_churn_risk: Minimum churn risk threshold (0-1)
            max_interventions: Maximum number of interventions to process
            verbose: Print detailed output
            include_escalation_demo: Add synthetic escalation case for demo
            
        Returns:
            List of intervention results
        """
        if verbose:
            print(f"\n{'='*70}")
            print(f"[SCAN] PROACTIVE CUSTOMER SCAN")
            print(f"{'='*70}")
            print(f"Scanning for at-risk customers...")
            print(f"Risk threshold: {min_churn_risk:.0%}")
        
        # Detect at-risk customers
        at_risk_customers = self.proactive_monitor.detect_churn_risks(
            min_churn_risk=min_churn_risk
        )
        
        if verbose:
            print(f"[WARNING] Found {len(at_risk_customers)} at-risk customers requiring intervention!")
        
        if not at_risk_customers:
            if verbose:
                print("[OK] No high-risk customers detected at this time.")
            return []
        
        # Process top N interventions
        interventions_to_process = at_risk_customers[:max_interventions]
        
        results = []
        
        for idx, alert in enumerate(interventions_to_process, 1):
            customer = alert['customer']
            
            if verbose:
                print(f"\n{'='*70}")
                print(f"[TARGET] PROACTIVE INTERVENTION #{idx}/{len(interventions_to_process)}")
                print(f"{'='*70}")
                print(f"[CUSTOMER] {customer.full_name} ({customer.customer_id})")
                print(f"   Segment: {customer.segment} | Tier: {customer.loyalty_tier}")
                print(f"   Lifetime Value: ${customer.lifetime_value:,.2f}")
                print(f"\n[ANALYSIS] Health Analysis:")
                health_status = "[CRITICAL]" if alert['health_score'] < 0.4 else "[WARNING]" if alert['health_score'] < 0.6 else "[OK]"
                risk_status = "[CRITICAL]" if alert['churn_risk'] > 0.7 else "[WARNING]" if alert['churn_risk'] > 0.5 else "[OK]"
                print(f"   Health Score: {alert['health_score']*100:.1f}% {health_status}")
                print(f"   Churn Risk: {alert['churn_risk']*100:.1f}% {risk_status}")
                print(f"   Risk Level: {alert['risk_level'].upper()}")
            
            # Create proactive event
            event_type = EventType.PROACTIVE_RETENTION if alert['churn_risk'] >= 0.7 else EventType.PROACTIVE_CHECK_IN
            
            event = CustomerEvent(
                event_id=f"PROACTIVE_{customer.customer_id}_{int(time.time())}",
                customer=customer,
                event_type=event_type,
                timestamp=datetime.now(),
                description=f"Proactive intervention - churn risk: {alert['churn_risk']:.1%}",
                metadata=alert
            )
            
            # Process through workflow
            result = self.process_proactive_event(event, verbose=False)
            results.append({
                'customer': customer,
                'alert': alert,
                'result': result
            })
            
            if verbose and result.personalized_response:
                print(f"\n[ACTION] Recommended Action: {result.recommended_action}")
                print(f"[MESSAGE] Personalized Message:")
                # Use safe_print for response that may contain Unicode
                response_preview = f"   {result.personalized_response[:200]}..."
                safe_print(response_preview)
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"[OK] Completed {len(results)} proactive interventions")
            print(f"{'='*70}\n")
        
        return results
    
    def display_health_dashboard(self):
        """Display customer health dashboard."""
        print(f"\n{'='*70}")
        print(f"[DASHBOARD] CUSTOMER HEALTH DASHBOARD")
        print(f"{'='*70}")
        
        # Get all at-risk customers
        all_at_risk = self.proactive_monitor.detect_churn_risks(min_churn_risk=0.3)
        
        # Categorize by risk level
        critical = [c for c in all_at_risk if c['churn_risk'] >= 0.8]
        high = [c for c in all_at_risk if 0.6 <= c['churn_risk'] < 0.8]
        medium = [c for c in all_at_risk if 0.4 <= c['churn_risk'] < 0.6]
        low = [c for c in all_at_risk if c['churn_risk'] < 0.4]
        
        print(f"\n[CRITICAL] Critical Risk: {len(critical)} customers (>=80% churn risk)")
        print(f"[HIGH] High Risk: {len(high)} customers (60-79% churn risk)")
        print(f"[MEDIUM] Medium Risk: {len(medium)} customers (40-59% churn risk)")
        print(f"[LOW] Low Risk: {len(low)} customers (<40% churn risk)")
        
        # Show top 10 at-risk
        print(f"\n[LIST] Top 10 At-Risk Customers:")
        print(f"{'='*70}")
        
        for idx, alert in enumerate(all_at_risk[:10], 1):
            customer = alert['customer']
            risk_label = "[CRITICAL]" if alert['churn_risk'] >= 0.8 else "[HIGH]" if alert['churn_risk'] >= 0.6 else "[MEDIUM]"
            
            print(f"\n{idx}. {risk_label} {customer.full_name} ({customer.customer_id})")
            print(f"   Segment: {customer.segment} | LTV: ${customer.lifetime_value:,.2f}")
            print(f"   Health: {alert['health_score']*100:.1f}% | Churn Risk: {alert['churn_risk']*100:.1f}%")
        
        print(f"\n{'='*70}\n")


def main():
    """Main entry point for ProCX Platform."""
    import argparse
    
    parser = argparse.ArgumentParser(description='ProCX - Proactive Customer Experience Platform')
    parser.add_argument('--interventions', action='store_true', 
                       help='Run proactive interventions scan')
    parser.add_argument('--dashboard', action='store_true',
                       help='Display customer health dashboard')
    parser.add_argument('--max-interventions', type=int, default=5,
                       help='Maximum number of interventions to process (default: 5)')
    parser.add_argument('--risk-threshold', type=float, default=0.6,
                       help='Minimum churn risk threshold 0-1 (default: 0.6)')
    
    args = parser.parse_args()
    
    # Initialize platform
    procx = ProCX()
    
    if args.dashboard:
        procx.display_health_dashboard()
    elif args.interventions:
        procx.run_proactive_scan(
            min_churn_risk=args.risk_threshold,
            max_interventions=args.max_interventions,
            verbose=True
        )
    else:
        # Default: show both
        procx.display_health_dashboard()
        print("\n" + "="*70)
        print("[TIP] Run with --interventions to execute proactive interventions")
        print("="*70 + "\n")


if __name__ == "__main__":
    main()
