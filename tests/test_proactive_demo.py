"""
Demo: Proactive Customer Intervention System
Run this to see proactive churn prevention in action!
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.proactive_runner import create_proactive_runner


def demo_proactive_intervention():
    """Demo the proactive intervention system."""
    print("="*70)
    print("🚀 PROACTIVE CUSTOMER INTERVENTION DEMO")
    print("="*70)
    print("\nThis demo will:")
    print("  1. Scan all VIP and Loyal customers")
    print("  2. Detect customers at risk of churning")
    print("  3. Generate proactive retention interventions")
    print("  4. Create personalized outreach messages")
    print("\n" + "="*70 + "\n")
    
    # Create runner with lower threshold to see more results
    runner = create_proactive_runner(
        min_churn_risk=0.25,  # Lower threshold for demo
        min_lifetime_value=2000.0,
        focus_segments=["VIP", "Loyal"]
    )
    
    # Run single scan (process top 3 customers)
    results = runner.run_once(max_interventions=3)
    
    print("\n" + "="*70)
    print("🎉 DEMO COMPLETE!")
    print("="*70)
    print(f"\nKey Takeaways:")
    print(f"  ✅ Proactive system detected {results['customers_scanned']} at-risk customers")
    print(f"  ✅ Generated {results['successful']} intervention plans automatically")
    print(f"  ✅ Each customer received a personalized retention strategy")
    print(f"  ✅ System runs BEFORE customers complain or leave")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    demo_proactive_intervention()
