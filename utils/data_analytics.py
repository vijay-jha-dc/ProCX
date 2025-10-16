"""
Data Analytics Utility - Real dataset analysis for pattern recognition.
"""
import pandas as pd
from typing import List, Dict, Any, Optional
from pathlib import Path

from models import Customer, AgentState
from config import settings


class DataAnalytics:
    """
    Provides real data analysis capabilities:
    - Find similar customers based on profile
    - Analyze customer segment behaviors
    - Historical pattern matching
    - Churn risk calculation based on actual data
    """
    
    def __init__(self, dataset_path: Optional[Path] = None):
        """Initialize with customer dataset."""
        self.dataset_path = dataset_path or settings.DATASET_PATH
        self.df = None
        self.load_dataset()
    
    def load_dataset(self):
        """Load the customer dataset."""
        try:
            self.df = pd.read_excel(self.dataset_path)
            print(f"✓ DataAnalytics: Loaded {len(self.df)} customers for analysis")
        except Exception as e:
            print(f"✗ DataAnalytics: Error loading dataset: {e}")
            self.df = None
    
    def find_similar_customers(
        self,
        customer: Customer,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find customers similar to the given customer based on:
        - Same segment
        - Similar lifetime value
        - Same preferred category
        - Same loyalty tier
        
        Args:
            customer: Target customer
            limit: Maximum number of similar customers
            
        Returns:
            List of similar customer profiles with similarity scores
        """
        if self.df is None:
            return []
        
        similar = []
        
        for _, row in self.df.iterrows():
            # Skip the same customer
            if row['customer_id'] == customer.customer_id:
                continue
            
            similarity_score = 0.0
            reasons = []
            
            # Same segment (40% weight)
            if row['segment'] == customer.segment:
                similarity_score += 0.4
                reasons.append(f"Same segment ({customer.segment})")
            
            # Similar lifetime value (30% weight)
            ltv_diff = abs(row['lifetime_value'] - customer.lifetime_value)
            ltv_similarity = max(0, 1 - (ltv_diff / customer.lifetime_value))
            if ltv_similarity > 0.7:  # Within 30% of LTV
                similarity_score += 0.3 * ltv_similarity
                reasons.append(f"Similar LTV (${row['lifetime_value']:.2f} vs ${customer.lifetime_value:.2f})")
            
            # Same preferred category (20% weight)
            if row['preferred_category'] == customer.preferred_category:
                similarity_score += 0.2
                reasons.append(f"Same category ({customer.preferred_category})")
            
            # Same loyalty tier (10% weight)
            if row['loyalty_tier'] == customer.loyalty_tier:
                similarity_score += 0.1
                reasons.append(f"Same tier ({customer.loyalty_tier})")
            
            if similarity_score > 0.5:  # Only include reasonably similar customers
                similar.append({
                    'customer_id': row['customer_id'],
                    'name': f"{row['first_name']} {row['last_name']}",
                    'segment': row['segment'],
                    'loyalty_tier': row['loyalty_tier'],
                    'lifetime_value': float(row['lifetime_value']),
                    'preferred_category': row['preferred_category'],
                    'similarity_score': similarity_score,
                    'similarity_reasons': reasons
                })
        
        # Sort by similarity score
        similar.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return similar[:limit]
    
    def get_segment_statistics(self, segment: str) -> Dict[str, Any]:
        """
        Get statistical insights for a customer segment.
        
        Args:
            segment: Customer segment (VIP, Loyal, Regular, Occasional)
            
        Returns:
            Dictionary with segment statistics
        """
        if self.df is None:
            return {}
        
        segment_df = self.df[self.df['segment'] == segment]
        
        if len(segment_df) == 0:
            return {}
        
        return {
            'segment': segment,
            'total_customers': len(segment_df),
            'avg_lifetime_value': float(segment_df['lifetime_value'].mean()),
            'median_lifetime_value': float(segment_df['lifetime_value'].median()),
            'min_lifetime_value': float(segment_df['lifetime_value'].min()),
            'max_lifetime_value': float(segment_df['lifetime_value'].max()),
            'loyalty_tier_distribution': segment_df['loyalty_tier'].value_counts().to_dict(),
            'top_categories': segment_df['preferred_category'].value_counts().head(3).to_dict(),
            'percentage_of_total': (len(segment_df) / len(self.df)) * 100
        }
    
    def calculate_churn_risk(self, customer: Customer, state: AgentState) -> float:
        """
        Calculate churn risk based on real data patterns.
        
        Risk factors:
        - Customer segment and LTV
        - Current sentiment
        - Urgency level
        - Comparison with similar customers
        
        Args:
            customer: Customer object
            state: Current agent state
            
        Returns:
            Churn risk score (0-1)
        """
        risk_score = 0.0
        
        # Base risk by segment (from dataset statistics)
        segment_risks = {
            'VIP': 0.1,        # VIP customers rarely churn but high impact
            'Loyal': 0.2,      # Loyal customers generally stable
            'Regular': 0.4,    # Regular customers moderate risk
            'Occasional': 0.6  # Occasional customers highest risk
        }
        risk_score = segment_risks.get(customer.segment, 0.4)
        
        # Adjust by sentiment
        if state.sentiment:
            sentiment_impact = {
                'very_negative': 0.4,
                'negative': 0.25,
                'neutral': 0.0,
                'positive': -0.15,
                'very_positive': -0.25
            }
            risk_score += sentiment_impact.get(state.sentiment.value, 0.0)
        
        # Adjust by urgency
        if state.urgency_level:
            urgency_impact = (state.urgency_level - 3) * 0.15  # Scale from urgency 1-5
            risk_score += urgency_impact
        
        # Adjust by customer risk score from context
        if state.customer_risk_score:
            risk_score = (risk_score + state.customer_risk_score) / 2
        
        # Compare with segment average LTV
        segment_stats = self.get_segment_statistics(customer.segment)
        if segment_stats:
            avg_ltv = segment_stats.get('avg_lifetime_value', 3000)
            if customer.lifetime_value < avg_ltv * 0.5:
                risk_score += 0.1  # Below-average LTV increases risk
            elif customer.lifetime_value > avg_ltv * 2:
                risk_score -= 0.1  # High LTV reduces risk
        
        # Event type impact
        if state.event:
            event_type = state.event.event_type.value
            if 'cancel' in event_type or 'complaint' in event_type:
                risk_score += 0.2
            elif 'delay' in event_type:
                risk_score += 0.15
            elif 'return' in event_type:
                risk_score += 0.1
        
        # Clamp between 0 and 1
        return max(0.0, min(1.0, risk_score))
    
    def get_segment_behavioral_patterns(self, segment: str) -> List[str]:
        """
        Get behavioral patterns for a customer segment based on data.
        
        Args:
            segment: Customer segment
            
        Returns:
            List of behavioral insights
        """
        if self.df is None:
            return []
        
        stats = self.get_segment_statistics(segment)
        if not stats:
            return []
        
        patterns = []
        
        # LTV insights
        avg_ltv = stats['avg_lifetime_value']
        patterns.append(f"{segment} customers have an average lifetime value of ${avg_ltv:.2f}")
        
        # Loyalty distribution
        if 'loyalty_tier_distribution' in stats:
            top_tier = max(stats['loyalty_tier_distribution'].items(), key=lambda x: x[1])
            patterns.append(f"Most {segment} customers are in {top_tier[0]} tier ({top_tier[1]} customers)")
        
        # Category preferences
        if 'top_categories' in stats:
            top_cat = list(stats['top_categories'].keys())[0]
            patterns.append(f"{segment} customers prefer {top_cat} category")
        
        # Segment-specific insights
        if segment == 'VIP':
            patterns.append("VIP customers expect immediate resolution and premium service")
            patterns.append("VIP customer retention is critical due to high LTV")
        elif segment == 'Loyal':
            patterns.append("Loyal customers value long-term relationship over immediate fixes")
            patterns.append("Loyal customers are more forgiving but need acknowledgment")
        elif segment == 'Regular':
            patterns.append("Regular customers respond well to standard service processes")
            patterns.append("Regular customers can be converted to Loyal with good experiences")
        elif segment == 'Occasional':
            patterns.append("Occasional customers need more guidance and reassurance")
            patterns.append("Occasional customers are more price-sensitive")
        
        return patterns
    
    def get_category_insights(self, category: str) -> Dict[str, Any]:
        """
        Get insights about customers who prefer a specific category.
        
        Args:
            category: Product category
            
        Returns:
            Category insights
        """
        if self.df is None:
            return {}
        
        category_df = self.df[self.df['preferred_category'] == category]
        
        if len(category_df) == 0:
            return {}
        
        return {
            'category': category,
            'total_customers': len(category_df),
            'avg_lifetime_value': float(category_df['lifetime_value'].mean()),
            'segment_distribution': category_df['segment'].value_counts().to_dict(),
            'top_loyalty_tier': category_df['loyalty_tier'].value_counts().idxmax(),
            'percentage_of_total': (len(category_df) / len(self.df)) * 100
        }
    
    def compare_with_cohort(self, customer: Customer) -> Dict[str, Any]:
        """
        Compare customer with their cohort (same segment + tier).
        
        Args:
            customer: Customer to compare
            
        Returns:
            Comparison statistics
        """
        if self.df is None:
            return {}
        
        cohort_df = self.df[
            (self.df['segment'] == customer.segment) &
            (self.df['loyalty_tier'] == customer.loyalty_tier)
        ]
        
        if len(cohort_df) == 0:
            return {}
        
        cohort_avg_ltv = cohort_df['lifetime_value'].mean()
        percentile = (cohort_df['lifetime_value'] < customer.lifetime_value).sum() / len(cohort_df) * 100
        
        return {
            'cohort_size': len(cohort_df),
            'cohort_avg_ltv': float(cohort_avg_ltv),
            'customer_ltv': customer.lifetime_value,
            'customer_percentile': percentile,
            'above_average': customer.lifetime_value > cohort_avg_ltv,
            'ltv_difference': customer.lifetime_value - cohort_avg_ltv
        }
