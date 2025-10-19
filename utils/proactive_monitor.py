"""
Proactive Monitor - Detects at-risk customers and triggers preventive actions.
"""
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

from models import Customer
from config import settings
from utils.data_analytics import DataAnalytics


class CustomerHealthScore:
    """Calculate customer health metrics."""
    
    @staticmethod
    def calculate_health_score(customer: Customer, analytics: DataAnalytics) -> float:
        """
        Calculate overall customer health score (0-1) using multi-dimensional analysis.
        
        Higher score = Healthier customer
        Lower score = At risk of churning
        
        Factors (10 dimensions):
        1. Segment strength (15%)
        2. Lifetime value percentile (12%)
        3. Loyalty tier (10%)
        4. Relative value in segment (10%)
        5. Last activity recency (15%) - NEW
        6. Order frequency (12%) - NEW
        7. Spending trends (10%) - NEW  
        8. Support history (8%) - NEW
        9. NPS score (5%) - NEW
        10. Customer tenure (3%) - NEW
        
        Args:
            customer: Customer to analyze
            analytics: DataAnalytics instance for context
            
        Returns:
            Health score from 0 (critical) to 1 (excellent)
        """
        score = 0.0  # Start from zero, build up
        
        # Factor 1: Segment strength (15% weight)
        segment_scores = {"VIP": 0.15, "Loyal": 0.12, "Regular": 0.08, "Occasional": 0.04}
        score += segment_scores.get(customer.segment, 0.05)
        
        # Factor 2: Lifetime value percentile (12% weight)
        cohort_data = analytics.compare_with_cohort(customer)
        if cohort_data:
            percentile = cohort_data.get('customer_percentile', 50)
            score += (percentile / 100) * 0.12
        else:
            score += 0.06  # Neutral if no data
        
        # Factor 3: Loyalty tier (10% weight)
        tier_scores = {"Platinum": 0.10, "Gold": 0.08, "Silver": 0.06, "Bronze": 0.04}
        score += tier_scores.get(customer.loyalty_tier, 0.05)
        
        # Factor 4: Relative value in segment (10% weight)
        segment_stats = analytics.get_segment_statistics(customer.segment)
        if segment_stats:
            avg_ltv = segment_stats.get('avg_lifetime_value', customer.lifetime_value)
            if avg_ltv > 0:
                relative_value = min(customer.lifetime_value / avg_ltv, 2.0)  # Cap at 2x
                score += (relative_value / 2.0) * 0.10  # 0 to 0.10
        else:
            score += 0.05  # Neutral
        
        # Factor 5: Last activity recency (15% weight) - NEW!
        if customer.days_since_active is not None:
            days = customer.days_since_active
            if days < 7:
                score += 0.15  # Very active
            elif days < 30:
                score += 0.12  # Active
            elif days < 60:
                score += 0.08  # Somewhat active
            elif days < 90:
                score += 0.04  # Inactive warning
            else:
                score += 0.0  # Dormant - major red flag
        else:
            score += 0.08  # Neutral if no data
        
        # Factor 6: Order frequency (12% weight) - NEW!
        order_stats = analytics.get_customer_order_stats(customer)
        if order_stats and order_stats.get('total_orders', 0) > 0:
            freq = order_stats.get('order_frequency', 0)  # Orders per month
            if freq >= 3:
                score += 0.12  # Very frequent
            elif freq >= 1:
                score += 0.09  # Regular
            elif freq >= 0.5:
                score += 0.06  # Occasional
            else:
                score += 0.03  # Rare
        else:
            score += 0.06  # Neutral if no orders
        
        # Factor 7: Spending trends (10% weight) - NEW!
        if customer.avg_order_value:
            if customer.avg_order_value > 80:
                score += 0.10  # High spender
            elif customer.avg_order_value > 50:
                score += 0.08  # Above average
            elif customer.avg_order_value > 30:
                score += 0.06  # Average
            else:
                score += 0.04  # Low spender
        else:
            score += 0.05  # Neutral
        
        # Factor 8: Support history (8% weight) - NEW!
        support_stats = analytics.get_customer_support_history(customer)
        if support_stats and support_stats.get('total_tickets', 0) > 0:
            avg_csat = support_stats.get('avg_csat')
            if avg_csat is not None:
                if avg_csat >= 4.5:
                    score += 0.08  # Very satisfied
                elif avg_csat >= 3.5:
                    score += 0.06  # Satisfied
                elif avg_csat >= 2.5:
                    score += 0.04  # Neutral
                else:
                    score += 0.0  # Dissatisfied - red flag
            else:
                score += 0.04  # Neutral if no CSAT
        else:
            score += 0.06  # No tickets = good (no issues)
        
        # Factor 9: NPS score (5% weight) - NEW!
        nps_data = analytics.get_customer_nps(customer)
        if nps_data:
            nps_category = nps_data.get('nps_category')
            if nps_category == 'promoter':
                score += 0.05  # Excellent
            elif nps_category == 'passive':
                score += 0.03  # Neutral
            else:  # detractor
                score += 0.0  # Red flag
        else:
            score += 0.025  # Neutral if no NPS
        
        # Factor 10: Customer tenure (3% weight) - NEW!
        if customer.days_since_signup:
            days = customer.days_since_signup
            if days > 730:  # 2+ years
                score += 0.03  # Long-term customer
            elif days > 365:  # 1+ year
                score += 0.025
            elif days > 180:  # 6+ months
                score += 0.02
            else:  # New customer
                score += 0.015  # Still learning
        else:
            score += 0.015  # Neutral
        
        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, score))
    
    @staticmethod
    def calculate_churn_risk(health_score: float, customer: Customer, analytics: Optional[DataAnalytics] = None) -> float:
        """
        Calculate churn risk based on health score, customer profile, and actual churn patterns.
        
        Args:
            health_score: Customer health score (0-1)
            customer: Customer profile
            analytics: DataAnalytics instance for churn patterns (optional)
            
        Returns:
            Churn risk from 0 (no risk) to 1 (high risk)
        """
        # Base risk is inverse of health
        base_risk = 1.0 - health_score
        
        # Adjust for segment (VIPs less likely to churn without warning)
        if customer.segment == "VIP":
            base_risk *= 0.8  # 20% reduction
        elif customer.segment == "Occasional":
            base_risk *= 1.2  # 20% increase
        
        # Adjust for lifetime value (high value customers need attention)
        if customer.lifetime_value > 10000:
            base_risk *= 1.1  # Slightly higher priority
        
        # NEW: Factor in actual churn data if available
        if analytics:
            churn_data = analytics.get_actual_churn_status(customer)
            if churn_data:
                predicted_score = churn_data.get('predicted_churn_score', 0.0)
                # Blend our calculated risk with the ML predicted score
                base_risk = (base_risk * 0.7) + (predicted_score * 0.3)
        
        return max(0.0, min(1.0, base_risk))


class ProactiveMonitor:
    """
    Monitors customer health and identifies at-risk customers for proactive intervention.
    """
    
    def __init__(self, dataset_path: Optional[Path] = None):
        """
        Initialize the Proactive Monitor.
        
        Args:
            dataset_path: Path to customer dataset
        """
        self.dataset_path = dataset_path or settings.DATASET_PATH
        self.analytics = DataAnalytics(dataset_path=self.dataset_path)
        self.health_calculator = CustomerHealthScore()
        
        print("✓ ProactiveMonitor initialized")
    
    def detect_churn_risks(
        self,
        min_churn_risk: float = 0.6,
        min_lifetime_value: float = 1000.0,
        segments: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect customers at risk of churning.
        
        Args:
            min_churn_risk: Minimum churn risk threshold (0-1)
            min_lifetime_value: Minimum LTV to consider
            segments: Optional list of segments to focus on (e.g., ["VIP", "Loyal"])
            
        Returns:
            List of at-risk customer alerts with details
        """
        if self.analytics.df is None:
            print("❌ No dataset available")
            return []
        
        at_risk_customers = []
        
        # Filter customers - DIVERSE SELECTION across all segments
        df = self.analytics.df.copy()
        
        # If no segments specified, ensure diversity across ALL segments
        if not segments:
            # Get mix from all segments with different tiers
            segment_samples = []
            for seg in ['VIP', 'Loyal', 'Regular', 'Occasional']:
                seg_df = df[df['segment'] == seg]
                if len(seg_df) > 0:
                    # Sample up to 30 from each segment for diversity
                    sample_size = min(30, len(seg_df))
                    segment_samples.append(seg_df.sample(n=sample_size, random_state=42))
            
            if segment_samples:
                df = pd.concat(segment_samples).reset_index(drop=True)
        else:
            df = df[df['segment'].isin(segments)]
        
        df = df[df['lifetime_value'] >= min_lifetime_value]
        
        print(f"\n🔍 Scanning {len(df)} customers for churn risk...")
        
        for _, row in df.iterrows():
            # Create Customer object
            customer = Customer(
                customer_id=row['customer_id'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                email=row['email'],
                segment=row['segment'],
                lifetime_value=float(row['lifetime_value']),
                preferred_category=row['preferred_category'],
                loyalty_tier=row['loyalty_tier'],
                # New fields from original dataset
                phone=str(row['phone']) if pd.notna(row.get('phone')) else None,
                signup_date=str(row['signup_date']) if pd.notna(row.get('signup_date')) else None,
                country=str(row['country']) if pd.notna(row.get('country')) else None,
                avg_order_value=float(row['avg_order_value']) if pd.notna(row.get('avg_order_value')) else None,
                last_active_date=str(row['last_active_date']) if pd.notna(row.get('last_active_date')) else None,
                opt_in_marketing=bool(row['opt_in_marketing']) if pd.notna(row.get('opt_in_marketing')) else None,
                language=str(row['language']) if pd.notna(row.get('language')) else None
            )
            
            # Calculate health and churn risk
            health_score = self.health_calculator.calculate_health_score(
                customer, self.analytics
            )
            churn_risk = self.health_calculator.calculate_churn_risk(
                health_score, customer, self.analytics  # Pass analytics for churn data
            )
            
            # Check if at risk
            if churn_risk >= min_churn_risk:
                # Get similar customers for context
                similar = self.analytics.find_similar_customers(customer, limit=3)
                
                # Get cohort comparison
                cohort_data = self.analytics.compare_with_cohort(customer)
                
                # Determine risk reasons
                reasons = []
                if health_score < 0.4:
                    reasons.append("Low health score")
                if customer.segment in ["VIP", "Loyal"]:
                    reasons.append("High-value segment at risk")
                if cohort_data and cohort_data.get('customer_percentile', 50) < 30:
                    reasons.append("Below-average in cohort")
                if not reasons:
                    reasons.append("General churn risk indicators")
                
                # Determine recommended action
                if customer.segment == "VIP":
                    action = "immediate_personal_outreach"
                elif customer.lifetime_value > 5000:
                    action = "retention_offer_premium"
                elif customer.segment == "Loyal":
                    action = "retention_offer_standard"
                else:
                    action = "engagement_campaign"
                
                alert = {
                    'customer': customer,
                    'health_score': health_score,
                    'churn_risk': churn_risk,
                    'risk_level': self._categorize_risk(churn_risk),
                    'reasons': reasons,
                    'recommended_action': action,
                    'similar_customers_count': len(similar),
                    'cohort_percentile': cohort_data.get('customer_percentile') if cohort_data else None,
                    'detected_at': datetime.now().isoformat()
                }
                
                at_risk_customers.append(alert)
        
        # Sort by churn risk (highest first)
        at_risk_customers.sort(key=lambda x: x['churn_risk'], reverse=True)
        
        print(f"⚠️  Found {len(at_risk_customers)} at-risk customers")
        
        return at_risk_customers
    
    def detect_high_value_inactivity(
        self,
        min_lifetime_value: float = 5000.0,
        inactivity_threshold_days: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Detect high-value customers who appear inactive.
        
        Note: Since we don't have actual purchase dates, we use health scores
        as a proxy for activity/engagement.
        
        Args:
            min_lifetime_value: Minimum LTV to consider
            inactivity_threshold_days: Days of inactivity (simulated)
            
        Returns:
            List of inactive high-value customer alerts
        """
        if self.analytics.df is None:
            return []
        
        inactive_customers = []
        
        # Filter high-value customers
        df = self.analytics.df[self.analytics.df['lifetime_value'] >= min_lifetime_value]
        
        print(f"\n🔍 Scanning {len(df)} high-value customers for inactivity...")
        
        for _, row in df.iterrows():
            customer = Customer(
                customer_id=row['customer_id'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                email=row['email'],
                segment=row['segment'],
                lifetime_value=float(row['lifetime_value']),
                preferred_category=row['preferred_category'],
                loyalty_tier=row['loyalty_tier'],
                # New fields from original dataset
                phone=str(row['phone']) if pd.notna(row.get('phone')) else None,
                signup_date=str(row['signup_date']) if pd.notna(row.get('signup_date')) else None,
                country=str(row['country']) if pd.notna(row.get('country')) else None,
                avg_order_value=float(row['avg_order_value']) if pd.notna(row.get('avg_order_value')) else None,
                last_active_date=str(row['last_active_date']) if pd.notna(row.get('last_active_date')) else None,
                opt_in_marketing=bool(row['opt_in_marketing']) if pd.notna(row.get('opt_in_marketing')) else None,
                language=str(row['language']) if pd.notna(row.get('language')) else None
            )
            
            # Calculate health score (lower = more "inactive")
            health_score = self.health_calculator.calculate_health_score(
                customer, self.analytics
            )
            
            # Consider "inactive" if health score is below threshold
            # In real system, this would check actual last_purchase_date
            if health_score < 0.6:  # Simulated inactivity
                alert = {
                    'customer': customer,
                    'health_score': health_score,
                    'estimated_inactivity_days': int((1 - health_score) * inactivity_threshold_days),
                    'risk_level': 'high' if health_score < 0.4 else 'medium',
                    'recommended_action': 'reengagement_campaign',
                    'detected_at': datetime.now().isoformat()
                }
                inactive_customers.append(alert)
        
        print(f"⚠️  Found {len(inactive_customers)} inactive high-value customers")
        
        return inactive_customers
    
    def get_proactive_opportunities(
        self,
        opportunity_type: str = "retention"
    ) -> List[Dict[str, Any]]:
        """
        Identify proactive engagement opportunities.
        
        Args:
            opportunity_type: Type of opportunity (retention, upsell, milestone)
            
        Returns:
            List of proactive opportunities
        """
        if opportunity_type == "retention":
            return self.detect_churn_risks(min_churn_risk=0.6)
        elif opportunity_type == "high_value":
            return self.detect_high_value_inactivity()
        else:
            return []
    
    def generate_monitoring_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive monitoring report.
        
        Returns:
            Report with overall customer health metrics
        """
        if self.analytics.df is None:
            return {"error": "No dataset available"}
        
        print("\n📊 Generating monitoring report...")
        
        # Calculate health scores for all customers
        health_scores = []
        churn_risks = []
        
        for _, row in self.analytics.df.iterrows():
            customer = Customer(
                customer_id=row['customer_id'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                email=row['email'],
                segment=row['segment'],
                lifetime_value=float(row['lifetime_value']),
                preferred_category=row['preferred_category'],
                loyalty_tier=row['loyalty_tier'],
                # New fields from original dataset
                phone=str(row['phone']) if pd.notna(row.get('phone')) else None,
                signup_date=str(row['signup_date']) if pd.notna(row.get('signup_date')) else None,
                country=str(row['country']) if pd.notna(row.get('country')) else None,
                avg_order_value=float(row['avg_order_value']) if pd.notna(row.get('avg_order_value')) else None,
                last_active_date=str(row['last_active_date']) if pd.notna(row.get('last_active_date')) else None,
                opt_in_marketing=bool(row['opt_in_marketing']) if pd.notna(row.get('opt_in_marketing')) else None,
                language=str(row['language']) if pd.notna(row.get('language')) else None
            )
            
            health = self.health_calculator.calculate_health_score(customer, self.analytics)
            churn = self.health_calculator.calculate_churn_risk(health, customer, self.analytics)
            
            health_scores.append(health)
            churn_risks.append(churn)
        
        report = {
            'total_customers': len(self.analytics.df),
            'avg_health_score': sum(health_scores) / len(health_scores),
            'avg_churn_risk': sum(churn_risks) / len(churn_risks),
            'customers_at_risk': len([r for r in churn_risks if r >= 0.6]),
            'customers_critical': len([r for r in churn_risks if r >= 0.8]),
            'health_distribution': {
                'excellent': len([h for h in health_scores if h >= 0.8]),
                'good': len([h for h in health_scores if 0.6 <= h < 0.8]),
                'fair': len([h for h in health_scores if 0.4 <= h < 0.6]),
                'poor': len([h for h in health_scores if h < 0.4])
            },
            'generated_at': datetime.now().isoformat()
        }
        
        print("✓ Report generated")
        
        return report
    
    @staticmethod
    def _categorize_risk(churn_risk: float) -> str:
        """Categorize churn risk level."""
        if churn_risk >= 0.8:
            return "critical"
        elif churn_risk >= 0.7:
            return "high"
        elif churn_risk >= 0.6:
            return "medium"
        else:
            return "low"


def create_proactive_monitor(dataset_path: Optional[Path] = None) -> ProactiveMonitor:
    """
    Factory function to create a ProactiveMonitor instance.
    
    Args:
        dataset_path: Optional path to customer dataset
        
    Returns:
        ProactiveMonitor instance
    """
    return ProactiveMonitor(dataset_path=dataset_path)
