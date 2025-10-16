"""
Decision Agent - Makes decisions on actions and escalations.
"""
import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI

from models import AgentState
from config.prompts import SYSTEM_PROMPTS
from config import settings


class DecisionAgent:
    """
    Makes strategic decisions:
    - Recommended actions
    - Escalation needs
    - Priority levels
    - Action steps
    """
    
    def __init__(self, model_name: str = None, temperature: float = 0.3):
        """Initialize the Decision Agent."""
        self.model_name = model_name or settings.DECISION_AGENT_MODEL
        self.temperature = temperature
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            openai_api_key=settings.OPENAI_API_KEY
        )
    
    def _should_escalate(self, state: AgentState) -> bool:
        """
        Determine if escalation is needed based on rules.
        
        Args:
            state: Current agent state
            
        Returns:
            True if escalation is needed
        """
        # VIP customer with negative sentiment
        if state.customer.is_vip and state.sentiment and \
           state.sentiment.value in ["negative", "very_negative"]:
            return True
        
        # High urgency
        if state.urgency_level and state.urgency_level >= settings.ESCALATION_URGENCY_THRESHOLD:
            return True
        
        # High churn risk
        if state.predicted_churn_risk and \
           state.predicted_churn_risk >= settings.CHURN_RISK_THRESHOLD:
            return True
        
        # High-value customer at risk
        if state.customer.is_high_value and \
           state.customer_risk_score and state.customer_risk_score >= 0.7:
            return True
        
        return False
    
    def _determine_priority(self, state: AgentState) -> str:
        """
        Determine priority level.
        
        Args:
            state: Current agent state
            
        Returns:
            Priority level: low, medium, high, or critical
        """
        # Check for critical conditions
        if state.customer.segment == "VIP":
            return "critical"
        
        if state.urgency_level and state.urgency_level >= 4:
            return "critical"
        
        if state.predicted_churn_risk and state.predicted_churn_risk >= 0.8:
            return "critical"
        
        # High priority
        if state.customer.segment == "Loyal" or state.customer.is_high_value:
            if state.urgency_level and state.urgency_level >= 3:
                return "high"
        
        if state.sentiment and state.sentiment.value == "very_negative":
            return "high"
        
        # Medium priority
        if state.urgency_level and state.urgency_level >= 2:
            return "medium"
        
        # Default to low
        return "low"
    
    def make_decision(self, state: AgentState) -> AgentState:
        """
        Make decision on actions and escalations.
        
        Args:
            state: Current agent state with context and pattern analysis
            
        Returns:
            Updated state with decision
        """
        if not state.customer or not state.context_summary:
            state.add_message("decision_agent", "Error: Missing required data")
            return state
        
        # Determine escalation and priority
        escalation_needed = self._should_escalate(state)
        priority_level = self._determine_priority(state)
        
        # Prepare prompt
        prompt_text = SYSTEM_PROMPTS["decision_agent"].format(
            customer_name=state.customer.full_name,
            segment=state.customer.segment,
            loyalty_tier=state.customer.loyalty_tier,
            lifetime_value=state.customer.lifetime_value,
            is_vip=state.customer.is_vip,
            event_type=state.event.event_type.value if state.event else "unknown",
            sentiment=state.sentiment.value if state.sentiment else "unknown",
            urgency_level=state.urgency_level or 3,
            customer_risk_score=state.customer_risk_score or 0.5,
            churn_risk=state.predicted_churn_risk or 0.5,
            context_summary=state.context_summary,
            historical_insights=state.historical_insights or "No insights available"
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
            
            # Update state
            state.recommended_action = result.get("recommended_action", "")
            state.escalation_needed = escalation_needed  # Use rule-based decision
            state.priority_level = priority_level  # Use rule-based decision
            
            state.add_message(
                "decision_agent",
                f"Decision made: Priority={state.priority_level}, "
                f"Escalation={'Yes' if state.escalation_needed else 'No'}"
            )
            
            # Add reasoning to messages
            if "reasoning" in result:
                state.add_message("decision_agent", f"Reasoning: {result['reasoning']}")
            
        except Exception as e:
            state.add_message(
                "decision_agent",
                f"Error during decision making: {str(e)}"
            )
            # Set default values
            state.recommended_action = "Review customer issue and provide appropriate response"
            state.escalation_needed = escalation_needed
            state.priority_level = priority_level
        
        return state
    
    def __call__(self, state: AgentState) -> AgentState:
        """Make the agent callable."""
        return self.make_decision(state)


# Factory function for LangGraph
def create_decision_agent():
    """Create a decision agent instance."""
    return DecisionAgent()
