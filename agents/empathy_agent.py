"""
Empathy Agent - Generates empathetic, personalized customer responses.
"""
import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI

from models import AgentState
from config.prompts import SYSTEM_PROMPTS
from config import settings
from utils.data_analytics import DataAnalytics


class EmpathyAgent:
    """
    Generates empathetic responses:
    - Personalized messaging
    - Appropriate tone
    - Empathy scoring
    - Customer-centric language
    """
    
    def __init__(self, model_name: str = None, temperature: float = 0.7):
        """Initialize the Empathy Agent."""
        self.model_name = model_name or settings.EMPATHY_AGENT_MODEL
        self.temperature = temperature
        
        # Initialize LLM with higher temperature for creativity
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Initialize data analytics for personalization insights
        self.analytics = DataAnalytics()
    
    def _determine_tone_guidelines(self, state: AgentState) -> str:
        """
        Determine the appropriate tone based on customer profile and situation.
        
        Args:
            state: Current agent state
            
        Returns:
            Tone guidelines string
        """
        guidelines = []
        
        # Segment-based tone
        if state.customer.segment in ["VIP", "Loyal"]:
            guidelines.append("Use premium, highly personalized language")
            guidelines.append("Express deep appreciation for their loyalty")
        
        # Sentiment-based tone
        if state.sentiment:
            if state.sentiment.value in ["negative", "very_negative"]:
                guidelines.append("Be extra empathetic and apologetic")
                guidelines.append("Take ownership of the issue")
            elif state.sentiment.value in ["positive", "very_positive"]:
                guidelines.append("Be warm and appreciative")
                guidelines.append("Reinforce positive experience")
        
        # Urgency-based tone
        if state.urgency_level and state.urgency_level >= 4:
            guidelines.append("Be reassuring and action-oriented")
            guidelines.append("Emphasize immediate resolution")
        
        # Priority-based tone
        if state.priority_level == "critical":
            guidelines.append("Show utmost concern and commitment")
        
        return "\n".join(guidelines)
    
    def generate_response(self, state: AgentState) -> AgentState:
        """
        Generate personalized, empathetic response using REAL customer data insights.
        
        Args:
            state: Current agent state with all analyses complete
            
        Returns:
            Updated state with personalized response
        """
        if not state.customer or not state.recommended_action:
            state.add_message("empathy_agent", "Error: Missing required data")
            return state
        
        # Get real data insights for personalization
        cohort_data = self.analytics.compare_with_cohort(state.customer)
        segment_stats = self.analytics.get_segment_statistics(state.customer.segment)
        
        # Build enhanced context for LLM
        enhanced_context = []
        
        if cohort_data and cohort_data.get('above_average'):
            enhanced_context.append(f"This customer is in the top {100 - cohort_data['customer_percentile']:.0f}% of their cohort")
            enhanced_context.append("Emphasize their valued status")
        
        if segment_stats:
            avg_ltv = segment_stats.get('avg_lifetime_value', 0)
            if state.customer.lifetime_value > avg_ltv * 1.5:
                enhanced_context.append("Customer has significantly above-average lifetime value")
                enhanced_context.append("Use premium, exclusive language")
        
        personalization_notes = "\n".join(enhanced_context) if enhanced_context else "Standard personalization"
        
        # Prepare prompt with real data context
        prompt_text = SYSTEM_PROMPTS["empathy_agent"].format(
            customer_name=state.customer.full_name,
            segment=state.customer.segment,
            loyalty_tier=state.customer.loyalty_tier,
            preferred_category=state.customer.preferred_category,
            event_type=state.event.event_type.value if state.event else "inquiry",
            description=state.event.description if state.event else "Customer inquiry",
            sentiment=state.sentiment.value if state.sentiment else "neutral",
            urgency_level=state.urgency_level or 3,
            recommended_action=state.recommended_action,
            priority_level=state.priority_level or "medium",
            escalation_needed=state.escalation_needed
        )
        
        # Add data-driven personalization context
        prompt_text += f"\n\nADDITIONAL PERSONALIZATION CONTEXT (from real customer data):\n{personalization_notes}"
        
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
            state.personalized_response = result.get("personalized_response", "")
            state.tone = result.get("tone", "professional")
            state.empathy_score = float(result.get("empathy_score", 0.7))
            
            state.add_message(
                "empathy_agent",
                f"Response generated: Empathy score={state.empathy_score:.2f}, "
                f"Tone={state.tone}"
            )
            
        except Exception as e:
            state.add_message(
                "empathy_agent",
                f"Error generating response: {str(e)}"
            )
            
            # Generate fallback response
            state.personalized_response = self._generate_fallback_response(state)
            state.tone = "professional and empathetic"
            state.empathy_score = 0.6
        
        return state
    
    def _generate_fallback_response(self, state: AgentState) -> str:
        """
        Generate a fallback response using real customer data even if LLM fails.
        
        Args:
            state: Current agent state
            
        Returns:
            Data-driven fallback response string
        """
        response = f"Dear {state.customer.full_name},\n\n"
        
        # Use real cohort data for personalization
        cohort_data = self.analytics.compare_with_cohort(state.customer)
        
        if cohort_data and cohort_data.get('above_average'):
            response += f"As one of our top {100 - cohort_data['customer_percentile']:.0f}% {state.customer.loyalty_tier} members, "
            response += "your satisfaction is our highest priority. "
        else:
            response += f"Thank you for being a valued {state.customer.loyalty_tier} member. "
        
        response += f"We truly appreciate your continued trust in us"
        
        # Add segment-specific acknowledgment
        if state.customer.lifetime_value > 5000:
            response += f" and your ${state.customer.lifetime_value:.2f} relationship with our brand"
        response += ".\n\n"
        
        if state.sentiment and state.sentiment.value in ["negative", "very_negative"]:
            response += "We sincerely apologize for any inconvenience you've experienced. "
            response += "This does not reflect the standard of service we strive to provide. "
        
        response += f"We are committed to resolving your {state.event.event_type.value if state.event else 'inquiry'} "
        
        # Add urgency-based timeline
        if state.urgency_level >= 4:
            response += "immediately"
        elif state.urgency_level >= 3:
            response += "as quickly as possible"
        else:
            response += "promptly"
        response += ".\n\n"
        
        if state.escalation_needed:
            response += f"Given the nature of your inquiry and your {state.customer.segment} status, "
            response += "your case has been marked as high priority, and a specialist will contact you within the next few hours.\n\n"
        
        # Add category-specific note if relevant
        category_insights = self.analytics.get_category_insights(state.customer.preferred_category)
        if category_insights and state.customer.preferred_category:
            response += f"We know how important {state.customer.preferred_category} products are to you. "
        
        response += "Thank you for your patience and understanding.\n\n"
        response += "Best regards,\n"
        response += f"{'VIP' if state.customer.segment == 'VIP' else 'Customer'} Experience Team"
        
        return response
    
    def __call__(self, state: AgentState) -> AgentState:
        """Make the agent callable."""
        return self.generate_response(state)


# Factory function for LangGraph
def create_empathy_agent():
    """Create an empathy agent instance."""
    return EmpathyAgent()
