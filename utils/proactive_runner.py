"""
Proactive Runner - Monitors customers and triggers proactive interventions.
"""
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from models import Customer, CustomerEvent, AgentState, EventType
from utils import ProactiveMonitor, MemoryHandler


class ProactiveRunner:
    """
    Runs proactive customer monitoring and triggers interventions.
    
    Can run as:
    - One-time scan
    - Scheduled job (cron)
    - Continuous monitoring loop
    """
    
    def __init__(
        self,
        min_churn_risk: float = 0.6,
        min_lifetime_value: float = 2000.0,
        focus_segments: Optional[List[str]] = None
    ):
        """
        Initialize the Proactive Runner.
        
        Args:
            min_churn_risk: Minimum churn risk to trigger intervention
            min_lifetime_value: Minimum LTV to consider
            focus_segments: Segments to focus on (default: VIP, Loyal)
        """
        self.min_churn_risk = min_churn_risk
        self.min_lifetime_value = min_lifetime_value
        self.focus_segments = focus_segments or ["VIP", "Loyal"]
        
        # Initialize components
        self.monitor = ProactiveMonitor()
        self.memory = MemoryHandler()
        
        # Lazy load workflow to avoid circular import
        from workflows import create_proactive_workflow
        self.workflow = create_proactive_workflow()
        
        print("✓ ProactiveRunner initialized")
        print(f"  Monitoring segments: {', '.join(self.focus_segments)}")
        print(f"  Churn risk threshold: {self.min_churn_risk:.0%}")
        print(f"  Min LTV: ${self.min_lifetime_value:,.0f}")
    
    def scan_customers(self) -> List[Dict[str, Any]]:
        """
        Scan all customers for proactive intervention opportunities.
        
        Returns:
            List of customers requiring intervention
        """
        print(f"\n{'='*70}")
        print(f"🔍 PROACTIVE SCAN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")
        
        # Detect at-risk customers
        at_risk = self.monitor.detect_churn_risks(
            min_churn_risk=self.min_churn_risk,
            min_lifetime_value=self.min_lifetime_value,
            segments=self.focus_segments
        )
        
        return at_risk
    
    def create_proactive_event(
        self,
        customer: Customer,
        alert: Dict[str, Any]
    ) -> CustomerEvent:
        """
        Create a proactive event for a customer.
        
        Args:
            customer: Customer to engage
            alert: Alert details from monitor
            
        Returns:
            Proactive CustomerEvent
        """
        event_id = f"PROACTIVE_{customer.customer_id}_{int(time.time())}"
        
        # Determine event type based on risk level
        if alert['churn_risk'] >= 0.8:
            event_type = EventType.PROACTIVE_RETENTION
            description = f"Critical churn risk detected: {alert['churn_risk']:.1%}"
        elif alert['churn_risk'] >= 0.6:
            event_type = EventType.PROACTIVE_RETENTION
            description = f"Churn risk detected: {alert['churn_risk']:.1%}"
        else:
            event_type = EventType.PROACTIVE_CHECK_IN
            description = "Proactive customer wellness check"
        
        return CustomerEvent(
            event_id=event_id,
            customer=customer,
            event_type=event_type,
            timestamp=datetime.now(),
            description=description,
            metadata={
                'health_score': alert['health_score'],
                'churn_risk': alert['churn_risk'],
                'risk_level': alert['risk_level'],
                'reasons': alert['reasons'],
                'recommended_action': alert['recommended_action']
            }
        )
    
    def process_proactive_intervention(
        self,
        alert: Dict[str, Any],
        verbose: bool = True
    ) -> AgentState:
        """
        Process a proactive intervention for an at-risk customer.
        
        Args:
            alert: Alert from monitor
            verbose: Print detailed output
            
        Returns:
            Final AgentState with intervention plan
        """
        customer = alert['customer']
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"🎯 PROACTIVE INTERVENTION: {customer.full_name}")
            print(f"{'='*70}")
            print(f"Customer: {customer.customer_id} | {customer.segment} | {customer.loyalty_tier}")
            print(f"LTV: ${customer.lifetime_value:,.2f}")
            print(f"Health: {alert['health_score']:.2%} | Churn Risk: {alert['churn_risk']:.2%}")
            print(f"Risk Level: {alert['risk_level'].upper()}")
            print(f"Reasons: {', '.join(alert['reasons'][:2])}")
            print(f"{'='*70}\n")
        
        # Create proactive event
        event = self.create_proactive_event(customer, alert)
        
        # Create initial state
        initial_state = AgentState(
            event=event,
            customer=customer,
            context_summary=f"Proactive intervention for {alert['risk_level']} churn risk",
            customer_risk_score=alert['churn_risk']
        )
        
        # Run workflow
        if verbose:
            print("⚙️  Running proactive workflow...\n")
        
        # Import run_workflow here to avoid circular dependency
        from workflows import run_workflow
        
        start_time = time.time()
        final_state = run_workflow(self.workflow, initial_state)
        final_state.processing_time = time.time() - start_time
        
        # Save to memory
        self.memory.save_interaction(final_state)
        
        # Display results
        if verbose:
            self._display_intervention_results(final_state, alert)
        
        return final_state
    
    def _display_intervention_results(self, state: AgentState, alert: Dict[str, Any]):
        """Display intervention results."""
        print(f"\n{'='*70}")
        print(f"📊 INTERVENTION PLAN")
        print(f"{'='*70}\n")
        
        print(f"🔮 Predictions:")
        print(f"   Churn Risk: {state.predicted_churn_risk:.2%}")
        print(f"   Priority: {state.priority_level.upper()}")
        print(f"   Escalation: {'YES' if state.escalation_needed else 'NO'}")
        
        print(f"\n🎯 Recommended Action:")
        print(f"   {state.recommended_action or alert['recommended_action']}")
        
        print(f"\n💬 Proactive Message:")
        print(f"{'-'*70}")
        print(state.personalized_response or "No message generated")
        print(f"{'-'*70}")
        
        print(f"\n⏱️  Processing Time: {state.processing_time:.2f}s")
        print(f"{'='*70}\n")
    
    def run_once(self, max_interventions: Optional[int] = None) -> Dict[str, Any]:
        """
        Run a single proactive scan and process interventions.
        
        Args:
            max_interventions: Maximum number of interventions to process
            
        Returns:
            Summary of interventions
        """
        # Scan for at-risk customers
        at_risk = self.scan_customers()
        
        if not at_risk:
            print("\n✅ No customers require proactive intervention at this time")
            return {
                "scan_time": datetime.now().isoformat(),
                "customers_scanned": 0,
                "interventions_triggered": 0,
                "results": []
            }
        
        # Process interventions
        print(f"\n⚠️  {len(at_risk)} customers require proactive intervention")
        
        if max_interventions:
            at_risk = at_risk[:max_interventions]
            print(f"   Processing top {max_interventions} priority customers\n")
        
        results = []
        for i, alert in enumerate(at_risk, 1):
            print(f"\n[{i}/{len(at_risk)}] Processing intervention...")
            
            try:
                final_state = self.process_proactive_intervention(alert, verbose=True)
                results.append({
                    "customer_id": alert['customer'].customer_id,
                    "success": True,
                    "churn_risk": alert['churn_risk'],
                    "action_taken": final_state.recommended_action
                })
            except Exception as e:
                print(f"❌ Error processing intervention: {e}")
                results.append({
                    "customer_id": alert['customer'].customer_id,
                    "success": False,
                    "error": str(e)
                })
        
        # Summary
        successful = sum(1 for r in results if r.get('success'))
        print(f"\n{'='*70}")
        print(f"✅ PROACTIVE SCAN COMPLETE")
        print(f"{'='*70}")
        print(f"   Interventions Processed: {len(results)}")
        print(f"   Successful: {successful}")
        print(f"   Failed: {len(results) - successful}")
        print(f"{'='*70}\n")
        
        return {
            "scan_time": datetime.now().isoformat(),
            "customers_scanned": len(at_risk),
            "interventions_triggered": len(results),
            "successful": successful,
            "failed": len(results) - successful,
            "results": results
        }
    
    def run_continuous(
        self,
        interval_seconds: int = 3600,
        max_iterations: Optional[int] = None
    ):
        """
        Run continuous monitoring with periodic scans.
        
        Args:
            interval_seconds: Time between scans (default: 1 hour)
            max_iterations: Maximum number of iterations (None = infinite)
        """
        print(f"\n{'='*70}")
        print(f"🔄 STARTING CONTINUOUS PROACTIVE MONITORING")
        print(f"{'='*70}")
        print(f"Scan Interval: {interval_seconds}s ({interval_seconds/60:.0f} minutes)")
        print(f"Max Iterations: {max_iterations or 'Infinite'}")
        print(f"{'='*70}\n")
        
        iteration = 0
        try:
            while True:
                iteration += 1
                print(f"\n{'='*70}")
                print(f"Iteration {iteration}")
                print(f"{'='*70}")
                
                # Run scan
                self.run_once(max_interventions=5)  # Limit to 5 per scan
                
                # Check if we should stop
                if max_iterations and iteration >= max_iterations:
                    print(f"\n✅ Reached max iterations ({max_iterations})")
                    break
                
                # Wait for next scan
                print(f"\n⏸️  Waiting {interval_seconds}s until next scan...")
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Continuous monitoring stopped by user")
            print(f"   Total iterations: {iteration}")


def create_proactive_runner(
    min_churn_risk: float = 0.6,
    min_lifetime_value: float = 2000.0,
    focus_segments: Optional[List[str]] = None
) -> ProactiveRunner:
    """
    Factory function to create a ProactiveRunner instance.
    
    Args:
        min_churn_risk: Minimum churn risk threshold
        min_lifetime_value: Minimum LTV to consider
        focus_segments: Segments to focus on
        
    Returns:
        ProactiveRunner instance
    """
    return ProactiveRunner(
        min_churn_risk=min_churn_risk,
        min_lifetime_value=min_lifetime_value,
        focus_segments=focus_segments
    )
