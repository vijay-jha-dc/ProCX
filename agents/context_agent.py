"""
Context Agent - Analyzes customer events and extracts contextual information.
"""
import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from models import AgentState, SentimentType
from config.prompts import SYSTEM_PROMPTS
from config import settings
from utils.data_analytics import DataAnalytics


class ContextAgent:
    """
    Analyzes customer events to extract:
    - Sentiment
    - Urgency level
    - Customer risk score
    - Context summary
    """
    
    def __init__(self, model_name: str = None, temperature: float = 0.3):
        """Initialize the Context Agent."""
        self.model_name = model_name or settings.CONTEXT_AGENT_MODEL
        self.temperature = temperature
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Initialize data analytics for context enrichment
        self.analytics = DataAnalytics()
    
    def analyze(self, state: AgentState) -> AgentState:
        """
        Analyze the customer event and extract context.
        
        Args:
            state: Current agent state with event and customer info
            
        Returns:
            Updated state with context analysis
        """
        if not state.event or not state.customer:
            state.add_message("context_agent", "Error: Missing event or customer data")
            return state
        
        # Get real data context for enrichment
        cohort_data = self.analytics.compare_with_cohort(state.customer)
        segment_stats = self.analytics.get_segment_statistics(state.customer.segment)
        
        # Build data-driven context
        data_context = ""
        if cohort_data:
            percentile = cohort_data.get('customer_percentile', 50)
            data_context += f"\n- Customer is at {percentile:.0f} percentile in their cohort"
            if cohort_data.get('above_average'):
                data_context += " (high-value customer)"
        
        if segment_stats:
            data_context += f"\n- {segment_stats['total_customers']} total customers in {state.customer.segment} segment"
            data_context += f"\n- Segment average LTV: ${segment_stats['avg_lifetime_value']:.2f}"
        
        # Prepare prompt with real data enrichment
        prompt_text = SYSTEM_PROMPTS["context_agent"].format(
            customer_name=state.customer.full_name,
            customer_id=state.customer.customer_id,
            segment=state.customer.segment,
            loyalty_tier=state.customer.loyalty_tier,
            lifetime_value=state.customer.lifetime_value,
            preferred_category=state.customer.preferred_category,
            event_type=state.event.event_type.value,
            description=state.event.description,
            timestamp=state.event.timestamp.isoformat()
        )
        
        # Add data-driven context
        if data_context:
            prompt_text += f"\n\nREAL CUSTOMER DATA CONTEXT:{data_context}"
        
        # Get response from LLM
        try:
            response = self.llm.invoke(prompt_text)
            
            # Parse JSON response
            content = response.content
            
            # Extract JSON from markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            
            # Update state
            state.sentiment = SentimentType(result["sentiment"])
            state.urgency_level = int(result["urgency_level"])
            state.customer_risk_score = float(result["customer_risk_score"])
            state.context_summary = result["context_summary"]
            
            state.add_message(
                "context_agent",
                f"Context analyzed: Sentiment={state.sentiment.value}, "
                f"Urgency={state.urgency_level}/5, Risk={state.customer_risk_score:.2f}"
            )
            
        except Exception as e:
            state.add_message(
                "context_agent",
                f"Error during analysis: {str(e)}"
            )
            # Set default values
            state.sentiment = SentimentType.NEUTRAL
            state.urgency_level = 3
            state.customer_risk_score = 0.5
            state.context_summary = "Analysis failed - using defaults"
        
        return state
    
    def __call__(self, state: AgentState) -> AgentState:
        """Make the agent callable."""
        return self.analyze(state)


# Factory function for LangGraph
def create_context_agent():
    """Create a context agent instance."""
    return ContextAgent()
