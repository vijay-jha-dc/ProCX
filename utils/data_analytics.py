"""
Data Analytics Utility - Real dataset analysis for pattern recognition.
"""
import pandas as pd
import warnings
from typing import List, Dict, Any, Optional
from pathlib import Path

from models import Customer, AgentState
from config import settings

# Suppress pandas warnings for cleaner output
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)


class DataAnalytics:
    """
    Provides real data analysis capabilities:
    - Find similar customers based on profile
    - Analyze customer segment behaviors
    - Historical pattern matching
    - Churn risk calculation based on actual data
    - Multi-sheet data integration (orders, churn_labels, support_tickets, etc.)
    
    Implements singleton pattern to avoid reloading data multiple times.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls, dataset_path: Optional[Path] = None):
        """Singleton pattern - only create one instance."""
        if cls._instance is None:
            cls._instance = super(DataAnalytics, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, dataset_path: Optional[Path] = None):
        """Initialize with customer dataset and load critical sheets (only once)."""
        # Only initialize once
        if DataAnalytics._initialized:
            return
            
        self.dataset_path = dataset_path or settings.DATASET_PATH
        self.df = None  # customers sheet
        self.orders_df = None
        self.churn_labels_df = None
        self.support_tickets_df = None
        self.nps_survey_df = None
        self.payments_df = None  # NEW: for payment analysis
        
        self.load_dataset()
        DataAnalytics._initialized = True
    
    def load_dataset(self):
        """Load the customer dataset and critical sheets."""
        try:
            # Determine if this is a multi-sheet file or single-sheet optimized file
            xl = pd.ExcelFile(self.dataset_path)
            
            if 'customers' in xl.sheet_names:
                # Multi-sheet file (original dataset)
                self.df = pd.read_excel(self.dataset_path, sheet_name='customers')
                print(f"[OK] DataAnalytics: Loaded {len(self.df)} customers for analysis")
                
                # Load critical sheets for enhanced analysis
                self._load_orders()
                self._load_churn_labels()
            else:
                # Single-sheet file (optimized dataset)
                self.df = pd.read_excel(self.dataset_path)
                print(f"[OK] DataAnalytics: Loaded {len(self.df)} customers for analysis")
                print(f"  Note: Using optimized dataset (single sheet). Multi-sheet features unavailable.")
            
        except Exception as e:
            print(f"X DataAnalytics: Error loading dataset: {e}")
            self.df = None
    
    def _load_orders(self):
        """Load orders sheet for purchase behavior analysis."""
        try:
            self.orders_df = pd.read_excel(self.dataset_path, sheet_name='orders')
            print(f"[OK] DataAnalytics: Loaded {len(self.orders_df)} orders")
        except Exception as e:
            print(f"  [WARN]  Orders sheet not available: {e}")
            self.orders_df = None
    
    def _load_churn_labels(self):
        """Load churn labels for ground truth validation."""
        try:
            self.churn_labels_df = pd.read_excel(self.dataset_path, sheet_name='churn_labels')
            print(f"[OK] DataAnalytics: Loaded {len(self.churn_labels_df)} churn labels")
        except Exception as e:
            print(f"  [WARN]  Churn labels sheet not available: {e}")
            self.churn_labels_df = None
    
    def _load_support_tickets(self):
        """Lazy load support tickets when needed."""
        if self.support_tickets_df is None:
            try:
                self.support_tickets_df = pd.read_excel(self.dataset_path, sheet_name='support_tickets')
                print(f"[OK] DataAnalytics: Loaded {len(self.support_tickets_df)} support tickets")
            except Exception as e:
                print(f"  [WARN]  Support tickets sheet not available: {e}")
                self.support_tickets_df = None
        return self.support_tickets_df
    
    def _load_nps_survey(self):
        """Lazy load NPS survey when needed."""
        if self.nps_survey_df is None:
            try:
                self.nps_survey_df = pd.read_excel(self.dataset_path, sheet_name='nps_survey')
                print(f"[OK] DataAnalytics: Loaded {len(self.nps_survey_df)} NPS surveys")
            except Exception as e:
                print(f"  [WARN]  NPS survey sheet not available: {e}")
                self.nps_survey_df = None
        return self.nps_survey_df
    
    def _load_payments(self):
        """Lazy load payments sheet when needed."""
        if self.payments_df is None:
            try:
                self.payments_df = pd.read_excel(self.dataset_path, sheet_name='payments')
                print(f"[OK] DataAnalytics: Loaded {len(self.payments_df)} payments")
            except Exception as e:
                print(f"  [WARN]  Payments sheet not available: {e}")
                self.payments_df = None
        return self.payments_df
    
    def find_similar_issues(
        self,
        event_description: str,
        event_type: str,
        customer_segment: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        🎯 INTELLIGENT ISSUE-BASED PATTERN MATCHING
        
        Find similar historical issues from support_tickets sheet and analyze:
        - What solutions worked (high CSAT)
        - What solutions failed (low CSAT)
        - Segment-specific patterns
        - Resolution effectiveness
        
        This is NOT just customer matching - it's ISSUE matching!
        
        Args:
            event_description: Current issue description
            event_type: Type of event (complaint, inquiry, etc.)
            customer_segment: Customer's segment (VIP, Loyal, etc.)
            limit: Max number of similar issues to return
            
        Returns:
            List of similar historical issues with outcomes
        """
        tickets = self._load_support_tickets()
        if tickets is None or len(tickets) == 0:
            return []
        
        # Extract keywords from current issue (simple but effective)
        keywords = self._extract_issue_keywords(event_description, event_type)
        
        if not keywords:
            return []
        
        similar_issues = []
        
        for _, ticket in tickets.iterrows():
            # Skip tickets without necessary data
            if pd.isna(ticket.get('issue_description')):
                continue
            
            issue_desc = str(ticket['issue_description']).lower()
            ticket_category = str(ticket.get('category', '')).lower()
            
            # Calculate similarity score
            similarity_score = 0.0
            matched_keywords = []
            
            # Keyword matching
            for keyword in keywords:
                if keyword in issue_desc or keyword in ticket_category:
                    similarity_score += 0.2
                    matched_keywords.append(keyword)
            
            # Segment boost (same segment issues are more relevant)
            ticket_segment = ticket.get('segment', '')
            if ticket_segment == customer_segment:
                similarity_score += 0.3
                matched_keywords.append(f"same_segment({customer_segment})")
            
            # Event type matching
            if event_type.lower() in ticket_category:
                similarity_score += 0.2
                matched_keywords.append(f"category_match({event_type})")
            
            # Only include if reasonably similar
            if similarity_score >= 0.4:
                # Analyze resolution quality
                csat = ticket.get('csat_score', 0)
                status = ticket.get('status', 'unknown')
                resolution_time = ticket.get('resolution_time_hours', 0)
                
                # Classify resolution effectiveness
                if csat >= 4.5:
                    effectiveness = "excellent"
                elif csat >= 4.0:
                    effectiveness = "good"
                elif csat >= 3.0:
                    effectiveness = "mediocre"
                else:
                    effectiveness = "poor"
                
                similar_issues.append({
                    'ticket_id': ticket.get('ticket_id', 'unknown'),
                    'customer_id': ticket.get('customer_id', 'unknown'),
                    'segment': ticket_segment,
                    'issue_description': ticket['issue_description'],
                    'category': ticket.get('category', 'unknown'),
                    'resolution': ticket.get('resolution', 'unknown'),
                    'csat_score': float(csat) if not pd.isna(csat) else 0.0,
                    'status': status,
                    'resolution_time_hours': float(resolution_time) if not pd.isna(resolution_time) else 0.0,
                    'similarity_score': similarity_score,
                    'matched_keywords': matched_keywords,
                    'effectiveness': effectiveness
                })
        
        # Sort by similarity score (highest first)
        similar_issues.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return similar_issues[:limit]
    
    def _extract_issue_keywords(self, description: str, event_type: str) -> List[str]:
        """
        Extract meaningful keywords from issue description.
        
        Smart extraction based on common CX issues.
        """
        description = description.lower()
        keywords = []
        
        # Common issue patterns
        issue_patterns = {
            'delivery': ['delay', 'shipping', 'delivery', 'late', 'arrived', 'package', 'tracking'],
            'product': ['wrong', 'defective', 'broken', 'damaged', 'quality', 'missing', 'incorrect'],
            'refund': ['refund', 'return', 'money back', 'charge', 'billing'],
            'account': ['login', 'password', 'access', 'account', 'forgot'],
            'cancellation': ['cancel', 'subscription', 'terminate', 'stop'],
            'inquiry': ['question', 'how to', 'information', 'help', 'wondering']
        }
        
        # Extract event type keywords
        if event_type:
            keywords.append(event_type.lower())
        
        # Extract pattern-based keywords
        for category, pattern_words in issue_patterns.items():
            for word in pattern_words:
                if word in description:
                    keywords.append(word)
                    # Also add the category
                    if category not in keywords:
                        keywords.append(category)
        
        # Extract individual important words (nouns, verbs)
        words = description.split()
        important_words = [w for w in words if len(w) > 4]  # Words longer than 4 chars
        keywords.extend(important_words[:5])  # Max 5 additional words
        
        return list(set(keywords))  # Remove duplicates
    
    def get_resolution_effectiveness_analysis(
        self,
        similar_issues: List[Dict[str, Any]],
        customer_segment: str
    ) -> Dict[str, Any]:
        """
        🎯 ANALYZE WHAT SOLUTIONS ACTUALLY WORK
        
        Learn from historical data which resolutions lead to:
        - High CSAT (satisfied customers)
        - Low CSAT (dissatisfied customers)
        
        Segment-specific recommendations.
        
        Args:
            similar_issues: List of similar historical issues
            customer_segment: Current customer's segment
            
        Returns:
            Analysis of resolution effectiveness
        """
        if not similar_issues:
            return {
                'total_similar_issues': 0,
                'recommendation': 'No historical data - use best practices'
            }
        
        # Separate by effectiveness
        excellent_resolutions = [i for i in similar_issues if i['effectiveness'] == 'excellent']
        good_resolutions = [i for i in similar_issues if i['effectiveness'] == 'good']
        poor_resolutions = [i for i in similar_issues if i['effectiveness'] == 'poor']
        
        # Focus on segment-specific patterns
        segment_issues = [i for i in similar_issues if i['segment'] == customer_segment]
        
        # Find best practices (what worked)
        best_practices = []
        if excellent_resolutions:
            # Group by resolution type
            resolution_groups = {}
            for issue in excellent_resolutions:
                res_key = str(issue['resolution'])[:50]  # First 50 chars as key
                if res_key not in resolution_groups:
                    resolution_groups[res_key] = []
                resolution_groups[res_key].append(issue)
            
            # Find most common successful resolutions
            for res, issues in sorted(resolution_groups.items(), key=lambda x: len(x[1]), reverse=True):
                avg_csat = sum(i['csat_score'] for i in issues) / len(issues)
                avg_time = sum(i['resolution_time_hours'] for i in issues) / len(issues)
                
                best_practices.append({
                    'resolution_type': res,
                    'success_count': len(issues),
                    'avg_csat': avg_csat,
                    'avg_resolution_time': avg_time,
                    'segments': list(set(i['segment'] for i in issues))
                })
        
        # Find what to avoid (what failed)
        avoid_patterns = []
        if poor_resolutions:
            for issue in poor_resolutions[:3]:  # Top 3 failures
                avoid_patterns.append({
                    'resolution': str(issue['resolution'])[:50],
                    'csat': issue['csat_score'],
                    'segment': issue['segment']
                })
        
        # Generate recommendation
        recommendation = self._generate_smart_recommendation(
            best_practices,
            avoid_patterns,
            customer_segment,
            segment_issues
        )
        
        return {
            'total_similar_issues': len(similar_issues),
            'segment_specific_issues': len(segment_issues),
            'excellent_resolutions': len(excellent_resolutions),
            'good_resolutions': len(good_resolutions),
            'poor_resolutions': len(poor_resolutions),
            'best_practices': best_practices[:3],  # Top 3
            'avoid_patterns': avoid_patterns,
            'recommendation': recommendation,
            'avg_csat_historical': sum(i['csat_score'] for i in similar_issues) / len(similar_issues),
            'avg_resolution_time': sum(i['resolution_time_hours'] for i in similar_issues) / len(similar_issues)
        }
    
    def _generate_smart_recommendation(
        self,
        best_practices: List[Dict],
        avoid_patterns: List[Dict],
        customer_segment: str,
        segment_issues: List[Dict]
    ) -> str:
        """Generate actionable recommendation based on historical data."""
        recommendations = []
        
        if best_practices:
            top_practice = best_practices[0]
            recommendations.append(
                f"✅ PROVEN SOLUTION: '{top_practice['resolution_type']}' "
                f"worked in {top_practice['success_count']} cases "
                f"({top_practice['avg_csat']:.1f}/5 CSAT)"
            )
            
            if customer_segment in top_practice['segments']:
                recommendations.append(
                    f"   → This solution specifically worked for {customer_segment} customers!"
                )
        
        if avoid_patterns:
            recommendations.append(
                f"❌ AVOID: {len(avoid_patterns)} resolution(s) led to low satisfaction"
            )
            worst = avoid_patterns[0]
            recommendations.append(
                f"   → '{worst['resolution']}' resulted in {worst['csat']:.1f}/5 CSAT"
            )
        
        if segment_issues:
            recommendations.append(
                f"📊 {len(segment_issues)} similar cases found for {customer_segment} segment"
            )
        
        if not recommendations:
            recommendations.append("No specific historical patterns - use general best practices")
        
        return " | ".join(recommendations)
    
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
        
        stats = {
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
        
        # Add new field statistics if available
        if 'avg_order_value' in segment_df.columns:
            stats['avg_order_value'] = float(segment_df['avg_order_value'].mean())
            stats['median_order_value'] = float(segment_df['avg_order_value'].median())
        
        if 'country' in segment_df.columns:
            stats['country_distribution'] = segment_df['country'].value_counts().to_dict()
        
        if 'language' in segment_df.columns:
            stats['language_distribution'] = segment_df['language'].value_counts().to_dict()
        
        if 'opt_in_marketing' in segment_df.columns:
            stats['opt_in_rate'] = float(segment_df['opt_in_marketing'].sum() / len(segment_df) * 100)
        
        return stats
    
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

    
    def get_customer_order_stats(self, customer: Customer) -> Dict[str, Any]:
        """
        Get order statistics for a customer.
        
        Args:
            customer: Customer object
            
        Returns:
            Dictionary with order metrics (frequency, recency, total orders, etc.)
        """
        if self.orders_df is None:
            return {}
        
        customer_orders = self.orders_df[self.orders_df['customer_id'] == customer.customer_id]
        
        if len(customer_orders) == 0:
            return {
                'total_orders': 0,
                'order_frequency': 0,
                'days_since_last_order': None,
                'avg_order_amount': 0
            }
        
        # Convert order_date to datetime if needed
        if 'order_date' in customer_orders.columns:
            customer_orders['order_date'] = pd.to_datetime(customer_orders['order_date'])
            last_order_date = customer_orders['order_date'].max()
            days_since_last = (pd.Timestamp.now() - last_order_date).days
        else:
            days_since_last = None
        
        stats = {
            'total_orders': len(customer_orders),
            'order_frequency': len(customer_orders) / max(1, customer.days_since_signup or 365) * 30,  # Orders per month
            'days_since_last_order': days_since_last,
            'avg_order_amount': float(customer_orders['total_amount'].mean()) if 'total_amount' in customer_orders.columns else customer.avg_order_value
        }
        
        # Order status distribution
        if 'order_status' in customer_orders.columns:
            stats['status_distribution'] = customer_orders['order_status'].value_counts().to_dict()
        
        return stats
    
    def get_actual_churn_status(self, customer: Customer) -> Optional[Dict[str, Any]]:
        """
        Get actual churn status and reason from churn_labels sheet.
        
        Args:
            customer: Customer object
            
        Returns:
            Dictionary with churn status, date, reason, and predicted score
        """
        if self.churn_labels_df is None:
            return None
        
        churn_data = self.churn_labels_df[
            self.churn_labels_df['customer_id'] == customer.customer_id
        ]
        
        if len(churn_data) == 0:
            return None
        
        row = churn_data.iloc[0]
        
        return {
            'is_churned': bool(row['is_churn']) if pd.notna(row['is_churn']) else False,
            'churn_date': str(row['churn_date']) if pd.notna(row.get('churn_date')) else None,
            'churn_reason': str(row['churn_reason']) if pd.notna(row.get('churn_reason')) else None,
            'predicted_churn_score': float(row['predicted_churn_score']) if pd.notna(row['predicted_churn_score']) else 0.0
        }
    
    def get_customer_support_history(self, customer: Customer) -> Dict[str, Any]:
        """
        Get support ticket history for a customer.
        
        Args:
            customer: Customer object
            
        Returns:
            Dictionary with ticket count, avg sentiment, resolution time, etc.
        """
        tickets_df = self._load_support_tickets()
        
        if tickets_df is None:
            return {}
        
        customer_tickets = tickets_df[tickets_df['customer_id'] == customer.customer_id]
        
        if len(customer_tickets) == 0:
            return {
                'total_tickets': 0,
                'open_tickets': 0,
                'avg_csat': None
            }
        
        stats = {
            'total_tickets': len(customer_tickets),
            'open_tickets': len(customer_tickets[customer_tickets['status'] == 'open']) if 'status' in customer_tickets.columns else 0
        }
        
        # CSAT scores
        if 'csat_score' in customer_tickets.columns:
            csat_scores = customer_tickets['csat_score'].dropna()
            if len(csat_scores) > 0:
                stats['avg_csat'] = float(csat_scores.mean())
                stats['min_csat'] = float(csat_scores.min())
        
        # Priority distribution
        if 'priority' in customer_tickets.columns:
            stats['priority_distribution'] = customer_tickets['priority'].value_counts().to_dict()
        
        return stats
    
    def get_customer_nps(self, customer: Customer) -> Optional[Dict[str, Any]]:
        """
        Get NPS survey data for a customer.
        
        Args:
            customer: Customer object
            
        Returns:
            Dictionary with latest NPS score and feedback
        """
        nps_df = self._load_nps_survey()
        
        if nps_df is None:
            return None
        
        customer_nps = nps_df[nps_df['customer_id'] == customer.customer_id]
        
        if len(customer_nps) == 0:
            return None
        
        # Get latest NPS
        if 'date' in customer_nps.columns:
            customer_nps['date'] = pd.to_datetime(customer_nps['date'])
            latest = customer_nps.sort_values('date', ascending=False).iloc[0]
        else:
            latest = customer_nps.iloc[-1]
        
        nps_score = int(latest['nps_score']) if pd.notna(latest['nps_score']) else None
        
        return {
            'nps_score': nps_score,
            'nps_category': 'promoter' if nps_score and nps_score >= 9 else ('passive' if nps_score and nps_score >= 7 else 'detractor'),
            'feedback_text': str(latest['feedback_text']) if pd.notna(latest.get('feedback_text')) else None,
            'survey_count': len(customer_nps)
        }

    def get_customer_payment_reliability(self, customer: Customer) -> Dict[str, Any]:
        """
        Get payment failure rate and reliability from payments sheet.
        
        Payment failures are a STRONG churn indicator - customers with
        payment issues are likely having financial problems or dissatisfaction.
        
        Args:
            customer: Customer object
            
        Returns:
            Dictionary with payment stats and risk score
        """
        payments_df = self._load_payments()
        
        if payments_df is None or self.orders_df is None:
            return {
                'total_payments': 0,
                'payment_risk': 0.0
            }
        
        # STEP 1: Get customer's orders
        customer_orders = self.orders_df[
            self.orders_df['customer_id'] == customer.customer_id
        ]
        
        if len(customer_orders) == 0:
            return {
                'total_payments': 0,
                'failed_payments': 0,
                'payment_risk': 0.0
            }
        
        # STEP 2: Get payments for those orders (JOIN operation)
        order_ids = customer_orders['order_id'].tolist()
        customer_payments = payments_df[
            payments_df['order_id'].isin(order_ids)
        ]
        
        if len(customer_payments) == 0:
            return {
                'total_payments': 0,
                'failed_payments': 0,
                'payment_risk': 0.0
            }
        
        # STEP 3: Calculate failure rate
        failed = len(customer_payments[customer_payments['status'] == 'failed'])
        total = len(customer_payments)
        failure_rate = failed / total if total > 0 else 0.0
        
        # Payment risk: scale failure rate (>20% failure = very high risk)
        payment_risk = min(1.0, failure_rate * 3)  # 33% failure = 1.0 risk
        
        return {
            'total_payments': total,
            'failed_payments': failed,
            'successful_payments': total - failed,
            'failure_rate': failure_rate,
            'payment_risk': payment_risk,
            'preferred_method': customer_payments['payment_method'].mode()[0] if len(customer_payments) > 0 else None
        }
