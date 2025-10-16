"""
Pattern Agent - Identifies patterns and predicts customer behavior.
"""
import json
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

from models import AgentState
from config.prompts import SYSTEM_PROMPTS
from config import settings
from utils.data_analytics import DataAnalytics


class PatternAgent:
    """
    Analyzes historical patterns to:
    - Identify similar customer behaviors
    - Predict churn risk
    - Provide historical insights
    - Recommend preventive actions
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
        Get similar customer patterns using REAL dataset similarity matching.
        """
        patterns = []
        
        # Find similar customers from actual dataset
        similar_customers = self.analytics.find_similar_customers(state.customer, limit=5)
        
        if similar_customers:
            patterns.append("SIMILAR CUSTOMERS FROM DATABASE:")
            patterns.append(f"  Found {len(similar_customers)} similar customers based on profile matching")
            
            for i, similar in enumerate(similar_customers[:3], 1):
                patterns.append(f"\n  Similar Customer #{i}:")
                patterns.append(f"    - ID: {similar['customer_id']}, {similar['segment']} segment")
                patterns.append(f"    - LTV: ${similar['lifetime_value']:.2f}, {similar['loyalty_tier']} tier")
                patterns.append(f"    - Similarity: {similar['similarity_score']:.2%}")
                patterns.append(f"    - Match reasons: {', '.join(similar['similarity_reasons'][:2])}")
        
        # Get behavioral patterns for this segment from actual data
        segment_patterns = self.analytics.get_segment_behavioral_patterns(state.customer.segment)
        if segment_patterns:
            patterns.append(f"\nSEGMENT BEHAVIORAL PATTERNS ({state.customer.segment}):")
            for pattern in segment_patterns:
                patterns.append(f"  - {pattern}")
        
        # Event-specific insights
        if state.event:
            event_type = state.event.event_type.value
            patterns.append(f"\nEVENT TYPE INSIGHTS ({event_type}):")
            if "delay" in event_type or "cancel" in event_type:
                patterns.append("  - Delivery issues correlate with 30-40% churn risk increase")
                patterns.append("  - Requires immediate action and compensation")
            elif "complaint" in event_type:
                patterns.append("  - Unresolved complaints have 50%+ churn risk")
                patterns.append("  - Fast resolution critical for retention")
            elif "return" in event_type:
                patterns.append("  - Return requests indicate product/expectation mismatch")
                patterns.append("  - Opportunity to understand customer needs better")
        
        return "\n".join(patterns)
    
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
