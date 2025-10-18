"""
Pattern Agent - Identifies patterns and predicts customer behavior.
Enhanced with PROACTIVE prediction capabilities.
"""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from models import AgentState, EventType
from config.prompts import SYSTEM_PROMPTS
from config import settings
from utils.data_analytics import DataAnalytics
from utils.proactive_monitor import ProactiveMonitor, CustomerHealthScore


class PatternAgent:
    """
    Analyzes historical patterns to:
    - Identify similar customer behaviors
    - Predict churn risk
    - Provide historical insights
    - Recommend preventive actions
    - [NEW] PROACTIVE: Predict future behavior and optimal intervention timing
    """
    
    def __init__(self, model_name: str = None, temperature: float = 0.5):
        """Initialize the Pattern Agent."""
        self.model_name = model_name or settings.PATTERN_AGENT_MODEL
        self.temperature = temperature
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Initialize data analytics for real pattern matching
        self.analytics = DataAnalytics()
        
        # Initialize proactive monitor for health scoring
        self.health_calculator = CustomerHealthScore()
    
    def _get_historical_context(self, state: AgentState) -> str:
        """
        Get historical context for the customer using REAL dataset analysis.
        """
        context_parts = []
        
        # Get segment statistics from actual data
        segment_stats = self.analytics.get_segment_statistics(state.customer.segment)
        if segment_stats:
            context_parts.append(f"SEGMENT ANALYSIS ({state.customer.segment}):")
            context_parts.append(f"  - Total {state.customer.segment} customers in database: {segment_stats['total_customers']}")
            context_parts.append(f"  - Average LTV for segment: ${segment_stats['avg_lifetime_value']:.2f}")
            context_parts.append(f"  - This customer's LTV: ${state.customer.lifetime_value:.2f}")
            context_parts.append(f"  - Segment represents {segment_stats['percentage_of_total']:.1f}% of customer base")
        
        # Compare with cohort (same segment + tier)
        cohort_comparison = self.analytics.compare_with_cohort(state.customer)
        if cohort_comparison:
            context_parts.append(f"\nCOHORT COMPARISON ({state.customer.segment} + {state.customer.loyalty_tier}):")
            context_parts.append(f"  - Cohort size: {cohort_comparison['cohort_size']} customers")
            context_parts.append(f"  - Customer is at {cohort_comparison['customer_percentile']:.1f} percentile in cohort")
            if cohort_comparison['above_average']:
                context_parts.append(f"  - ⚠️ Above average by ${cohort_comparison['ltv_difference']:.2f} (valuable customer)")
            else:
                context_parts.append(f"  - Below average by ${abs(cohort_comparison['ltv_difference']):.2f}")
        
        # Category insights
        category_insights = self.analytics.get_category_insights(state.customer.preferred_category)
        if category_insights:
            context_parts.append(f"\nCATEGORY INSIGHTS ({state.customer.preferred_category}):")
            context_parts.append(f"  - {category_insights['total_customers']} customers prefer this category")
            context_parts.append(f"  - Average LTV in category: ${category_insights['avg_lifetime_value']:.2f}")
        
        # Current state
        context_parts.append(f"\nCURRENT SITUATION:")
        context_parts.append(f"  - Urgency: {state.urgency_level}/5")
        context_parts.append(f"  - Sentiment: {state.sentiment.value if state.sentiment else 'unknown'}")
        context_parts.append(f"  - Risk score: {state.customer_risk_score:.2f}")
        
        return "\n".join(context_parts)
    
    def _get_similar_patterns(self, state: AgentState) -> str:
        """
        🎯 DUAL-LAYER PATTERN MATCHING (ENHANCED!)
        
        Layer 1: Similar CUSTOMERS (profile-based)
        Layer 2: Similar ISSUES (problem-based) ← NEW!
        
        This gives us BOTH "who else is like this customer" AND 
        "how did we solve this type of problem before"
        """
        patterns = []
        
        # ========== LAYER 1: SIMILAR CUSTOMERS ==========
        similar_customers = self.analytics.find_similar_customers(state.customer, limit=5)
        
        if similar_customers:
            patterns.append("=" * 70)
            patterns.append("🔍 LAYER 1: SIMILAR CUSTOMER PROFILES")
            patterns.append("=" * 70)
            patterns.append(f"Found {len(similar_customers)} customers with similar profiles:\n")
            
            for i, similar in enumerate(similar_customers[:3], 1):
                patterns.append(f"  Customer #{i}:")
                patterns.append(f"    - ID: {similar['customer_id']}, {similar['segment']} segment")
                patterns.append(f"    - LTV: ${similar['lifetime_value']:.2f}, {similar['loyalty_tier']} tier")
                patterns.append(f"    - Similarity: {similar['similarity_score']:.2%}")
                patterns.append(f"    - Match reasons: {', '.join(similar['similarity_reasons'][:2])}\n")
        
        # ========== LAYER 2: SIMILAR ISSUES (NEW!) ==========
        if state.event:
            event_desc = state.event.description if hasattr(state.event, 'description') else ""
            event_type = state.event.event_type.value if hasattr(state.event, 'event_type') else "inquiry"
            
            # Find similar historical issues from support_tickets
            similar_issues = self.analytics.find_similar_issues(
                event_description=event_desc,
                event_type=event_type,
                customer_segment=state.customer.segment,
                limit=10
            )
            
            if similar_issues:
                patterns.append("\n" + "=" * 70)
                patterns.append("🎯 LAYER 2: SIMILAR HISTORICAL ISSUES (INTELLIGENT MATCHING!)")
                patterns.append("=" * 70)
                patterns.append(f"Found {len(similar_issues)} similar past issues in support tickets:\n")
                
                # Show top 3 most similar issues
                for i, issue in enumerate(similar_issues[:3], 1):
                    patterns.append(f"  Issue #{i} (Similarity: {issue['similarity_score']:.1%}):")
                    patterns.append(f"    - Ticket: {issue['ticket_id']}, {issue['segment']} customer")
                    patterns.append(f"    - Problem: {issue['issue_description'][:80]}...")
                    patterns.append(f"    - Resolution: {str(issue['resolution'])[:60]}...")
                    patterns.append(f"    - Outcome: {issue['csat_score']:.1f}/5 CSAT ({issue['effectiveness']})")
                    patterns.append(f"    - Keywords matched: {', '.join(issue['matched_keywords'][:3])}\n")
                
                # ========== RESOLUTION EFFECTIVENESS ANALYSIS ==========
                effectiveness = self.analytics.get_resolution_effectiveness_analysis(
                    similar_issues,
                    state.customer.segment
                )
                
                patterns.append("\n" + "=" * 70)
                patterns.append("📊 RESOLUTION EFFECTIVENESS ANALYSIS")
                patterns.append("=" * 70)
                patterns.append(f"Historical Success Rate:")
                patterns.append(f"  ✅ Excellent resolutions: {effectiveness['excellent_resolutions']}")
                patterns.append(f"  👍 Good resolutions: {effectiveness['good_resolutions']}")
                patterns.append(f"  👎 Poor resolutions: {effectiveness['poor_resolutions']}")
                patterns.append(f"  📈 Average CSAT: {effectiveness['avg_csat_historical']:.1f}/5")
                patterns.append(f"  ⏱️  Average resolution time: {effectiveness['avg_resolution_time']:.1f} hours")
                
                patterns.append(f"\n🎯 SMART RECOMMENDATION:")
                patterns.append(f"  {effectiveness['recommendation']}")
                
                # Show best practices
                if effectiveness['best_practices']:
                    patterns.append(f"\n✨ PROVEN SOLUTIONS (What worked before):")
                    for bp in effectiveness['best_practices']:
                        patterns.append(
                            f"  → {bp['resolution_type']} "
                            f"({bp['success_count']} successes, {bp['avg_csat']:.1f}/5 CSAT)"
                        )
                
                # Show what to avoid
                if effectiveness['avoid_patterns']:
                    patterns.append(f"\n⚠️  AVOID THESE (What failed before):")
                    for ap in effectiveness['avoid_patterns']:
                        patterns.append(
                            f"  ✗ {ap['resolution']} "
                            f"(resulted in {ap['csat']:.1f}/5 CSAT for {ap['segment']})"
                        )
            else:
                patterns.append("\n" + "=" * 70)
                patterns.append("🎯 LAYER 2: SIMILAR HISTORICAL ISSUES")
                patterns.append("=" * 70)
                patterns.append("  No directly matching historical issues found.")
                patterns.append("  Using general best practices for this event type.\n")
        
        # ========== SEGMENT BEHAVIORAL PATTERNS ==========
        segment_patterns = self.analytics.get_segment_behavioral_patterns(state.customer.segment)
        if segment_patterns:
            patterns.append("\n" + "=" * 70)
            patterns.append(f"📈 SEGMENT BEHAVIORAL PATTERNS ({state.customer.segment})")
            patterns.append("=" * 70)
            for pattern in segment_patterns:
                patterns.append(f"  - {pattern}")
        
        # ========== EVENT TYPE INSIGHTS ==========
        if state.event:
            event_type = state.event.event_type.value
            patterns.append(f"\n" + "=" * 70)
            patterns.append(f"💡 GENERAL EVENT TYPE INSIGHTS ({event_type})")
            patterns.append("=" * 70)
            if "delay" in event_type.lower() or "delivery" in event_type.lower():
                patterns.append("  - Delivery issues correlate with 30-40% churn risk increase")
                patterns.append("  - Requires immediate action and compensation")
                patterns.append("  - VIPs expect expedited resolution")
            elif "complaint" in event_type.lower():
                patterns.append("  - Unresolved complaints have 50%+ churn risk")
                patterns.append("  - Fast resolution critical for retention")
                patterns.append("  - First complaint is opportunity to build trust")
            elif "return" in event_type.lower() or "refund" in event_type.lower():
                patterns.append("  - Return requests indicate product/expectation mismatch")
                patterns.append("  - Opportunity to understand customer needs better")
                patterns.append("  - Easy refund process builds long-term loyalty")
            elif "inquiry" in event_type.lower():
                patterns.append("  - Questions indicate engagement - positive signal")
                patterns.append("  - Helpful responses drive future purchases")
                patterns.append("  - Upsell opportunity if handled well")
        
        return "\n".join(patterns)
    
    def predict_future_behavior(self, state: AgentState) -> Dict[str, Any]:
        """
        PROACTIVE: Predict customer behavior in the next 30/60/90 days.
        Enhanced with real order history, churn patterns, and behavioral data.
        
        Args:
            state: Current agent state
            
        Returns:
            Dictionary with future behavior predictions
        """
        if not state.customer:
            return {}
        
        # Calculate current health score
        health_score = self.health_calculator.calculate_health_score(
            state.customer, self.analytics
        )
        
        # Calculate churn risk (now includes ML predictions)
        churn_risk = self.health_calculator.calculate_churn_risk(
            health_score, state.customer, self.analytics
        )
        
        # Get enriched customer data
        order_stats = self.analytics.get_customer_order_stats(state.customer)
        churn_data = self.analytics.get_actual_churn_status(state.customer)
        support_stats = self.analytics.get_customer_support_history(state.customer)
        nps_data = self.analytics.get_customer_nps(state.customer)
        
        # Predict likelihood of various outcomes
        predictions = {
            "health_score": health_score,
            "churn_risk": churn_risk,
            "predictions_30_days": self._predict_timeframe(
                health_score, churn_risk, 30, state.customer, order_stats
            ),
            "predictions_60_days": self._predict_timeframe(
                health_score, churn_risk, 60, state.customer, order_stats
            ),
            "predictions_90_days": self._predict_timeframe(
                health_score, churn_risk, 90, state.customer, order_stats
            ),
            "optimal_intervention_window": self._calculate_intervention_window(
                churn_risk, state.customer, order_stats
            ),
            "recommended_proactive_actions": self._get_proactive_recommendations(
                state.customer, health_score, churn_risk, order_stats, support_stats, nps_data
            ),
            # NEW: Add behavioral insights
            "behavioral_insights": {
                "order_frequency": order_stats.get('order_frequency', 0) if order_stats else 0,
                "days_since_last_order": order_stats.get('days_since_last_order') if order_stats else None,
                "days_inactive": state.customer.days_since_active,
                "tenure_days": state.customer.days_since_signup,
                "is_dormant": state.customer.is_inactive,
                "avg_csat": support_stats.get('avg_csat') if support_stats else None,
                "nps_category": nps_data.get('nps_category') if nps_data else None,
                "actual_churn_status": churn_data.get('is_churned') if churn_data else None,
                "churn_reason": churn_data.get('churn_reason') if churn_data else None
            }
        }
        
        return predictions
    
    def _predict_timeframe(self, health_score: float, churn_risk: float, 
                          days: int, customer, order_stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict outcomes for a specific timeframe with order pattern analysis.
        
        Args:
            health_score: Current health score
            churn_risk: Current churn risk
            days: Number of days ahead
            customer: Customer object
            order_stats: Order statistics from multi-sheet data
        """
        # Base time factor: risk increases over time
        time_multiplier = 1 + (days / 90) * 0.3  # 30% increase over 90 days
        
        # Order frequency factor: declining orders increase risk
        order_frequency = order_stats.get('order_frequency', 0) if order_stats else 0
        expected_orders = order_frequency * (days / 30)  # Orders expected in this timeframe
        
        # Engagement factor: inactive customers higher risk
        engagement_factor = 1.0
        if customer.is_inactive:
            engagement_factor = 1.4
        elif customer.days_since_active > 30:
            engagement_factor = 1.2
        
        # Tenure factor: new customers more volatile, loyal customers more stable
        tenure_factor = 1.0
        if customer.days_since_signup < 90:
            tenure_factor = 1.3  # New customers higher risk
        elif customer.days_since_signup > 730:  # 2+ years
            tenure_factor = 0.8  # Loyal customers lower risk
        
        # Adjusted churn risk
        adjusted_risk = min(
            churn_risk * time_multiplier * engagement_factor * tenure_factor, 
            1.0
        )
        
        return {
            "days": days,
            "churn_probability": adjusted_risk,
            "expected_orders": round(expected_orders, 1),
            "engagement_probability": 1 - adjusted_risk,
            "intervention_urgency": "high" if adjusted_risk > 0.7 else "medium" if adjusted_risk > 0.5 else "low"
        }
    
    def _calculate_intervention_window(self, churn_risk: float, customer, 
                                      order_stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate optimal time window for proactive intervention.
        Enhanced with order patterns and engagement data.
        """
        # Get days since last order if available
        days_since_order = order_stats.get('days_since_last_order') if order_stats else None
        
        # Adjust urgency based on churn risk and engagement
        if churn_risk >= 0.7:
            urgency_msg = "Act within 7 days to prevent churn"
            if customer.is_inactive and days_since_order and days_since_order > 60:
                urgency_msg = f"CRITICAL: Customer inactive for {customer.days_since_active} days, last order {days_since_order} days ago"
            
            return {
                "start_days": 0,
                "end_days": 7,
                "urgency": "immediate",
                "message": urgency_msg
            }
        elif churn_risk >= 0.5:
            urgency_msg = "Reach out within 2-3 weeks"
            if days_since_order and days_since_order > 30:
                urgency_msg = f"Customer hasn't ordered in {days_since_order} days - re-engagement needed"
            
            return {
                "start_days": 7,
                "end_days": 21,
                "urgency": "soon",
                "message": urgency_msg
            }
        else:
            return {
                "start_days": 21,
                "end_days": 60,
                "urgency": "normal",
                "message": "Monitor and engage within 2 months"
            }
    
    def _get_proactive_recommendations(
        self, 
        customer, 
        health_score: float, 
        churn_risk: float,
        order_stats: Dict[str, Any],
        support_stats: Dict[str, Any],
        nps_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate proactive action recommendations based on comprehensive data.
        Now data-driven using actual order patterns, support history, and NPS.
        """
        recommendations = []
        
        # Get behavioral data
        order_frequency = order_stats.get('order_frequency', 0) if order_stats else 0
        days_since_order = order_stats.get('days_since_last_order') if order_stats else None
        avg_csat = support_stats.get('avg_csat') if support_stats else None
        nps_category = nps_data.get('nps_category') if nps_data else None
        
        # HIGH CHURN RISK - Retention focus
        if churn_risk >= 0.6:
            # VIP/High-value customers get premium treatment
            if customer.segment == "VIP" or customer.is_high_spender:
                recommendations.append({
                    "action": "vip_personal_outreach",
                    "priority": "critical",
                    "description": f"Personal call from account manager - Customer hasn't ordered in {days_since_order} days" if days_since_order else "Personal call from account manager",
                    "expected_impact": "high",
                    "channel": "phone" if customer.phone else "email"
                })
            
            # Detractors need special attention
            if nps_category == "Detractor":
                recommendations.append({
                    "action": "service_recovery",
                    "priority": "critical",
                    "description": f"Service recovery - NPS Detractor with {avg_csat:.1f} avg CSAT" if avg_csat else "Service recovery - NPS Detractor",
                    "expected_impact": "high"
                })
            
            # Targeted retention offer based on order history
            discount_pct = 20 if customer.segment == "VIP" else 15
            recommendations.append({
                "action": "retention_offer",
                "priority": "high",
                "description": f"Send {discount_pct}% discount on {customer.preferred_category} - Win back after {days_since_order} days" if days_since_order and days_since_order > 30 else f"Send {discount_pct}% discount on {customer.preferred_category}",
                "expected_impact": "medium-high"
            })
        
        # MEDIUM RISK - Re-engagement focus
        elif churn_risk >= 0.4:
            # Declining order frequency
            if order_frequency < 0.5:  # Less than 1 order every 2 months
                recommendations.append({
                    "action": "reactivation_campaign",
                    "priority": "high",
                    "description": f"Low order frequency ({order_frequency:.2f} orders/month) - Send 'We Miss You' campaign",
                    "expected_impact": "medium"
                })
            
            # General engagement
            recommendations.append({
                "action": "engagement_campaign",
                "priority": "medium",
                "description": f"Send curated {customer.preferred_category} recommendations",
                "expected_impact": "medium"
            })
        
        # LOW RISK but high value - Nurture and upsell
        elif customer.is_high_spender:
            # NPS Promoters can be brand advocates
            if nps_category == "Promoter":
                recommendations.append({
                    "action": "advocacy_program",
                    "priority": "medium",
                    "description": "Invite to referral program - High NPS Promoter",
                    "expected_impact": "medium"
                })
            
            recommendations.append({
                "action": "loyalty_appreciation",
                "priority": "low",
                "description": f"Thank you message with exclusive preview - {customer.days_since_signup} days loyalty",
                "expected_impact": "low-medium"
            })
        
        # Always recommend personalized communication
        recommendations.append({
            "action": "personalized_content",
            "priority": "ongoing",
            "description": f"Regular updates about {customer.preferred_category} products",
            "expected_impact": "low"
        })
        
        return recommendations
    
    def generate_proactive_insights(self, state: AgentState) -> str:
        """
        Generate comprehensive proactive insights for the customer.
        
        Args:
            state: Current agent state
            
        Returns:
            Formatted string with proactive insights
        """
        predictions = self.predict_future_behavior(state)
        
        if not predictions:
            return "Unable to generate proactive insights"
        
        insights = []
        insights.append(f"🔮 PROACTIVE BEHAVIOR PREDICTIONS:")
        insights.append(f"   Current Health: {predictions['health_score']:.2%}")
        insights.append(f"   Churn Risk: {predictions['churn_risk']:.2%}")
        
        insights.append(f"\n📅 FUTURE PREDICTIONS:")
        for timeframe in ['predictions_30_days', 'predictions_60_days', 'predictions_90_days']:
            pred = predictions[timeframe]
            insights.append(
                f"   {pred['days']} days: {pred['churn_probability']:.1%} churn risk "
                f"({pred['intervention_urgency']} urgency)"
            )
        
        window = predictions['optimal_intervention_window']
        insights.append(f"\n⏰ OPTIMAL INTERVENTION:")
        insights.append(f"   Window: {window['start_days']}-{window['end_days']} days")
        insights.append(f"   Urgency: {window['urgency'].upper()}")
        insights.append(f"   → {window['message']}")
        
        insights.append(f"\n🎯 RECOMMENDED PROACTIVE ACTIONS:")
        for i, rec in enumerate(predictions['recommended_proactive_actions'][:3], 1):
            insights.append(
                f"   {i}. [{rec['priority'].upper()}] {rec['action']}: {rec['description']}"
            )
        
        return "\n".join(insights)
    
    def analyze_patterns(self, state: AgentState) -> AgentState:
        """
        Analyze patterns and predict customer behavior.
        
        Args:
            state: Current agent state with context analysis
            
        Returns:
            Updated state with pattern analysis
        """
        if not state.customer or not state.context_summary:
            state.add_message("pattern_agent", "Error: Missing context data")
            return state
        
        # Get historical data
        historical_context = self._get_historical_context(state)
        similar_patterns = self._get_similar_patterns(state)
        
        # Prepare prompt
        prompt_text = SYSTEM_PROMPTS["pattern_agent"].format(
            customer_name=state.customer.full_name,
            segment=state.customer.segment,
            loyalty_tier=state.customer.loyalty_tier,
            lifetime_value=state.customer.lifetime_value,
            event_type=state.event.event_type.value if state.event else "unknown",
            sentiment=state.sentiment.value if state.sentiment else "unknown",
            urgency_level=state.urgency_level or 3,
            risk_score=state.customer_risk_score or 0.5,
            historical_context=historical_context,
            similar_patterns=similar_patterns
        )
        
        # Get response from LLM
        try:
            response = self.llm.invoke(prompt_text)
            content = response.content
            
            # Extract JSON from markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            
            # Calculate churn risk using REAL data analytics
            data_driven_churn_risk = self.analytics.calculate_churn_risk(state.customer, state)
            llm_churn_risk = float(result.get("predicted_churn_risk", 0.5))
            
            # Combine LLM prediction with data-driven analysis (60% data, 40% LLM)
            state.predicted_churn_risk = (data_driven_churn_risk * 0.6) + (llm_churn_risk * 0.4)
            
            state.historical_insights = result.get("historical_insights", "")
            
            # Store similar patterns with actual customer data
            similar_customers = self.analytics.find_similar_customers(state.customer, limit=3)
            state.similar_patterns = [{
                "pattern_summary": result.get("pattern_summary", ""),
                "preventive_recommendations": result.get("preventive_recommendations", []),
                "similar_customers_count": len(similar_customers),
                "data_driven_churn_risk": data_driven_churn_risk,
                "llm_churn_risk": llm_churn_risk
            }]
            
            state.add_message(
                "pattern_agent",
                f"Pattern analysis complete: Churn risk={state.predicted_churn_risk:.2f} "
                f"(Data: {data_driven_churn_risk:.2f}, LLM: {llm_churn_risk:.2f}), "
                f"Found {len(similar_customers)} similar customers"
            )
            
            # ADD PROACTIVE PREDICTIONS for proactive events
            if state.event and hasattr(state.event, 'is_proactive') and state.event.is_proactive:
                proactive_insights = self.generate_proactive_insights(state)
                state.add_message("pattern_agent", f"Proactive predictions generated:\n{proactive_insights}")
                
                # Store proactive predictions in similar_patterns for later use
                predictions = self.predict_future_behavior(state)
                if state.similar_patterns:
                    state.similar_patterns[0]['proactive_predictions'] = predictions
            
        except Exception as e:
            state.add_message(
                "pattern_agent",
                f"Error during pattern analysis: {str(e)}"
            )
            # Use data-driven fallback even if LLM fails
            state.predicted_churn_risk = self.analytics.calculate_churn_risk(state.customer, state)
            state.historical_insights = "LLM analysis failed - using data-driven churn calculation"
            
            similar_customers = self.analytics.find_similar_customers(state.customer, limit=3)
            state.similar_patterns = [{
                "pattern_summary": "Fallback analysis",
                "similar_customers_count": len(similar_customers)
            }]
        
        return state
    
    def __call__(self, state: AgentState) -> AgentState:
        """Make the agent callable."""
        return self.analyze_patterns(state)


# Factory function for LangGraph
def create_pattern_agent():
    """Create a pattern agent instance."""
    return PatternAgent()
