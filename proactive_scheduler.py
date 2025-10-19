"""
Proactive Scheduler - Continuously monitors customers and triggers interventions.

This is what makes ProCX truly PROACTIVE vs just a demo script.
Runs in background, scanning customers at regular intervals.
"""
import time
import schedule
from datetime import datetime
from typing import Optional
from pathlib import Path

from models import AgentState
from utils import ProactiveMonitor
from workflows import create_proactive_workflow, run_workflow
from config import settings


class ProactiveScheduler:
    """
    Automated scheduler that runs proactive monitoring at regular intervals.
    
    This is the key component that makes the system proactive:
    - Runs continuously in background
    - Scans customers without human intervention
    - Triggers agent pipeline when risks detected
    - Logs all interventions
    """
    
    def __init__(
        self,
        scan_interval_minutes: int = 5,
        min_churn_risk: float = 0.6,
        max_interventions_per_run: int = 10
    ):
        """
        Initialize the scheduler.
        
        Args:
            scan_interval_minutes: How often to scan (default: 5 minutes)
            min_churn_risk: Minimum risk threshold to trigger intervention
            max_interventions_per_run: Limit interventions per scan to avoid spam
        """
        self.scan_interval = scan_interval_minutes
        self.min_churn_risk = min_churn_risk
        self.max_interventions = max_interventions_per_run
        
        # Initialize components
        self.monitor = ProactiveMonitor()
        self.workflow = create_proactive_workflow()
        
        # Tracking
        self.total_scans = 0
        self.total_interventions = 0
        self.last_scan_time = None
        
        print(f"🔄 ProactiveScheduler initialized")
        print(f"   Scan interval: Every {scan_interval_minutes} minutes")
        print(f"   Churn risk threshold: {min_churn_risk:.0%}")
        print(f"   Max interventions per run: {max_interventions_per_run}")
    
    def scan_and_intervene(self):
        """
        Main scanning logic - called on schedule.
        
        This is the core proactive loop:
        1. Scan all customers
        2. Identify at-risk customers
        3. Prioritize by risk level
        4. Generate interventions
        5. Log results
        """
        self.total_scans += 1
        scan_start = time.time()
        
        print(f"\n{'='*70}")
        print(f"🔍 PROACTIVE SCAN #{self.total_scans}")
        print(f"{'='*70}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Scanning customers for churn risk >= {self.min_churn_risk:.0%}...")
        
        # Step 1: Detect at-risk customers
        alerts = self.monitor.detect_churn_risks(
            min_churn_risk=self.min_churn_risk,
            min_lifetime_value=1000.0
        )
        
        if not alerts:
            print("✓ No at-risk customers detected")
            print(f"Scan completed in {time.time() - scan_start:.2f}s\n")
            self.last_scan_time = datetime.now()
            return
        
        print(f"⚠️  Found {len(alerts)} at-risk customers")
        
        # Step 2: Limit interventions to avoid overwhelming customers
        alerts_to_process = alerts[:self.max_interventions]
        
        if len(alerts) > self.max_interventions:
            print(f"   Processing top {self.max_interventions} priority cases")
            print(f"   {len(alerts) - self.max_interventions} others queued for next scan")
        
        # Step 3: Process each intervention
        interventions_created = 0
        
        for i, alert in enumerate(alerts_to_process, 1):
            customer = alert['customer']
            
            print(f"\n[{i}/{len(alerts_to_process)}] Processing: {customer.full_name}")
            print(f"     Churn Risk: {alert['churn_risk']:.1%} | LTV: ${customer.lifetime_value:,.2f}")
            
            try:
                # Create proactive event
                from models import CustomerEvent, EventType
                
                event = CustomerEvent(
                    event_id=f"PROACTIVE_SCAN{self.total_scans}_{customer.customer_id}",
                    customer=customer,
                    event_type=EventType.PROACTIVE_RETENTION,
                    timestamp=datetime.now(),
                    description=f"Proactive churn prevention: {alert['risk_level']} risk detected",
                    metadata={
                        'scan_number': self.total_scans,
                        'health_score': alert['health_score'],
                        'churn_risk': alert['churn_risk'],
                        'risk_level': alert['risk_level']
                    }
                )
                
                # Run through agent pipeline
                initial_state = AgentState(
                    event=event,
                    customer=customer
                )
                
                final_state = run_workflow(self.workflow, initial_state)
                
                # Log intervention (in production, would save to DB and trigger delivery)
                self._log_intervention(final_state, alert)
                
                interventions_created += 1
                print(f"     ✓ Intervention generated")
                
            except Exception as e:
                print(f"     ❌ Error: {str(e)}")
        
        # Summary
        self.total_interventions += interventions_created
        scan_duration = time.time() - scan_start
        
        print(f"\n{'='*70}")
        print(f"📊 SCAN SUMMARY")
        print(f"{'='*70}")
        print(f"Duration: {scan_duration:.2f}s")
        print(f"At-risk detected: {len(alerts)}")
        print(f"Interventions created: {interventions_created}")
        print(f"Total interventions (all-time): {self.total_interventions}")
        print(f"{'='*70}\n")
        
        self.last_scan_time = datetime.now()
    
    def _log_intervention(self, state: AgentState, alert: dict):
        """
        Log intervention details.
        In production, would:
        1. Save to database
        2. Trigger delivery via SendGrid/Twilio
        3. Update customer record
        4. Create audit trail
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "customer_id": state.customer.customer_id,
            "customer_name": state.customer.full_name,
            "churn_risk": alert['churn_risk'],
            "health_score": alert['health_score'],
            "intervention_type": state.recommended_action,
            "channel": getattr(state, 'channel', 'email'),
            "escalation_needed": state.escalation_needed,
            "message_preview": state.personalized_response[:100] if state.personalized_response else None
        }
        
        # In production: Save to interventions table
        # db.interventions.insert(log_entry)
        
        # For demo: Could append to JSONL file
        # with open('logs/proactive_interventions.jsonl', 'a') as f:
        #     json.dump(log_entry, f)
        #     f.write('\n')
    
    def run_continuous(self):
        """
        Run continuously - this is what makes it PROACTIVE.
        
        In production, this would run as:
        - Docker container with restart policy
        - Systemd service on Linux
        - Windows Service
        - Kubernetes CronJob
        """
        print("\n🚀 Starting Proactive Scheduler (Continuous Mode)")
        print(f"   Will scan every {self.scan_interval} minutes")
        print("   Press Ctrl+C to stop\n")
        
        # Schedule the job
        schedule.every(self.scan_interval).minutes.do(self.scan_and_intervene)
        
        # Run first scan immediately
        print("Running initial scan...")
        self.scan_and_intervene()
        
        # Keep running
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n⏹️  Scheduler stopped by user")
            self._print_final_stats()
    
    def run_once(self):
        """
        Run a single scan (useful for testing/demo).
        """
        print("\n🔄 Running one-time proactive scan...\n")
        self.scan_and_intervene()
        self._print_final_stats()
    
    def _print_final_stats(self):
        """Print final statistics."""
        print(f"\n{'='*70}")
        print(f"📊 FINAL STATISTICS")
        print(f"{'='*70}")
        print(f"Total scans performed: {self.total_scans}")
        print(f"Total interventions generated: {self.total_interventions}")
        if self.total_scans > 0:
            print(f"Average interventions per scan: {self.total_interventions / self.total_scans:.1f}")
        if self.last_scan_time:
            print(f"Last scan: {self.last_scan_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")


def main():
    """CLI entry point for scheduler."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ProCX Proactive Scheduler")
    parser.add_argument(
        "--mode",
        choices=["continuous", "once"],
        default="once",
        help="Run mode: continuous (background) or once (single scan)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Scan interval in minutes (for continuous mode)"
    )
    parser.add_argument(
        "--risk-threshold",
        type=float,
        default=0.6,
        help="Minimum churn risk threshold (0-1)"
    )
    parser.add_argument(
        "--max-interventions",
        type=int,
        default=10,
        help="Maximum interventions per scan"
    )
    
    args = parser.parse_args()
    
    # Create scheduler
    scheduler = ProactiveScheduler(
        scan_interval_minutes=args.interval,
        min_churn_risk=args.risk_threshold,
        max_interventions_per_run=args.max_interventions
    )
    
    # Run based on mode
    if args.mode == "continuous":
        scheduler.run_continuous()
    else:
        scheduler.run_once()


if __name__ == "__main__":
    main()
