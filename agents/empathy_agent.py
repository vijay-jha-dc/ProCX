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
        Enhanced with NPS awareness.
        
        Args:
            state: Current agent state
            
        Returns:
            Tone guidelines string
        """
        guidelines = []
        
        # Get NPS data for tone adjustment
        nps_data = self.analytics.get_customer_nps(state.customer)
        nps_category = nps_data.get('nps_category') if nps_data else None
        nps_score = nps_data.get('nps_score') if nps_data else None
        
        # NPS-based tone (highest priority)
        if nps_category == "Detractor":
            guidelines.append(f"⚠️ NPS DETRACTOR (score: {nps_score}) - Use service recovery language")
            guidelines.append("Acknowledge their frustration and show commitment to improvement")
            guidelines.append("Offer concrete solutions and follow-up")
        elif nps_category == "Passive":
            guidelines.append(f"NPS Passive (score: {nps_score}) - Re-engage and delight")
            guidelines.append("Show how we can exceed expectations")
        elif nps_category == "Promoter":
            guidelines.append(f"✓ NPS PROMOTER (score: {nps_score}) - Reinforce positive relationship")
            guidelines.append("Express gratitude for their advocacy")
        
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
        Enhanced with language support and NPS awareness.
        
        Args:
            state: Current agent state with all analyses complete
            
        Returns:
            Updated state with personalized response
        """
        if not state.customer or not state.recommended_action:
            state.add_message("empathy_agent", "Error: Missing required data")
            return state
        
        # Get language preference
        customer_language = state.customer.language or "en"
        language_name = {
            "en": "English",
            "hi": "Hindi", 
            "ta": "Tamil",
            "te": "Telugu",
            "bn": "Bengali"
        }.get(customer_language, "English")
        
        # Get real data insights for personalization
        cohort_data = self.analytics.compare_with_cohort(state.customer)
        segment_stats = self.analytics.get_segment_statistics(state.customer.segment)
        nps_data = self.analytics.get_customer_nps(state.customer)
        support_history = self.analytics.get_customer_support_history(state.customer)
        
        # Build enhanced context for LLM
        enhanced_context = []
        
        # Language context
        if customer_language != "en":
            enhanced_context.append(f"🌐 LANGUAGE: Customer prefers {language_name}")
            enhanced_context.append(f"Use culturally appropriate greetings and expressions for {language_name} speakers")
            enhanced_context.append("If response is in English, mention availability of support in their language")
        
        # NPS context
        if nps_data:
            nps_category = nps_data.get('nps_category')
            nps_score = nps_data.get('nps_score')
            enhanced_context.append(f"NPS: {nps_category} (score: {nps_score})")
            
            if nps_category == "Detractor":
                enhanced_context.append("⚠️ Customer has low satisfaction - prioritize service recovery")
                enhanced_context.append("Acknowledge past issues and show commitment to improvement")
            elif nps_category == "Promoter":
                enhanced_context.append("✓ Loyal advocate - reinforce positive relationship")
        
        # Support history context
        if support_history:
            ticket_count = support_history.get('total_tickets', 0)
            avg_csat = support_history.get('avg_csat')
            
            if ticket_count > 0:
                enhanced_context.append(f"Support History: {ticket_count} previous tickets")
                if avg_csat:
                    enhanced_context.append(f"Average CSAT: {avg_csat:.1f}/5.0")
                    if avg_csat < 3.5:
                        enhanced_context.append("⚠️ Low historical satisfaction - extra care needed")
        
        # Cohort performance
        if cohort_data and cohort_data.get('above_average'):
            enhanced_context.append(f"This customer is in the top {100 - cohort_data['customer_percentile']:.0f}% of their cohort")
            enhanced_context.append("Emphasize their valued status")
        
        # LTV context
        if segment_stats:
            avg_ltv = segment_stats.get('avg_lifetime_value', 0)
            if state.customer.lifetime_value > avg_ltv * 1.5:
                enhanced_context.append("Customer has significantly above-average lifetime value")
                enhanced_context.append("Use premium, exclusive language")
        
        personalization_notes = "\n".join(enhanced_context) if enhanced_context else "Standard personalization"
        
        # Get tone guidelines (now includes NPS awareness)
        tone_guidelines = self._determine_tone_guidelines(state)
        
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
        prompt_text += f"\n\nTONE GUIDELINES:\n{tone_guidelines}"
        
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
                f"Tone={state.tone}, Language={language_name}"
            )
            
        except Exception as e:
            state.add_message(
                "empathy_agent",
                f"Error generating response: {str(e)}"
            )
            
            # Generate fallback response (now language-aware)
            state.personalized_response = self._generate_fallback_response(state)
            state.tone = "professional and empathetic"
            state.empathy_score = 0.6
        
        return state
    
    def _generate_fallback_response(self, state: AgentState) -> str:
        """
        Generate a fallback response using real customer data even if LLM fails.
        Enhanced with language awareness and NPS context.
        
        Args:
            state: Current agent state
            
        Returns:
            Data-driven, language-aware fallback response string
        """
        # Get language preference
        customer_language = state.customer.language or "en"
        language_name = {
            "en": "English",
            "hi": "Hindi", 
            "ta": "Tamil",
            "te": "Telugu",
            "bn": "Bengali"
        }.get(customer_language, "English")
        
        # Get NPS and support data
        nps_data = self.analytics.get_customer_nps(state.customer)
        nps_category = nps_data.get('nps_category') if nps_data else None
        support_history = self.analytics.get_customer_support_history(state.customer)
        
        response = f"Dear {state.customer.full_name},\n\n"
        
        # Language note if not English
        if customer_language != "en":
            response += f"(Support also available in {language_name})\n\n"
        
        # NPS-aware opening
        if nps_category == "Detractor":
            response += "We sincerely apologize for not meeting your expectations in the past. "
            response += "Your feedback is invaluable, and we are committed to regaining your trust. "
        elif nps_category == "Promoter":
            response += "Thank you for being such a loyal advocate of our brand! "
        
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
        
        # Support history context
        if support_history:
            avg_csat = support_history.get('avg_csat')
            if avg_csat and avg_csat < 3.5:
                response += "We understand you've had challenges with us before. "
                response += "We're taking extra care to ensure this experience exceeds your expectations. "
        
        # Sentiment-based apology
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
            response += "your case has been marked as high priority, and a specialist will contact you "
            
            # Phone contact if available
            if state.customer.phone:
                response += f"at {state.customer.phone} "
            
            response += "within the next few hours.\n\n"
        
        # Add category-specific note if relevant
        category_insights = self.analytics.get_category_insights(state.customer.preferred_category)
        if category_insights and state.customer.preferred_category:
            response += f"We know how important {state.customer.preferred_category} products are to you. "
        
        response += "Thank you for your patience and understanding.\n\n"
        response += "Best regards,\n"
        response += f"{'VIP' if state.customer.segment == 'VIP' else 'Customer'} Experience Team"
        
        # Language support note
        if customer_language != "en":
            response += f"\n\n({language_name} support: Contact us for assistance in your preferred language)"
        
        return response
    
    def __call__(self, state: AgentState) -> AgentState:
        """Make the agent callable."""
        return self.generate_response(state)


# Factory function for LangGraph
def create_empathy_agent():
    """Create an empathy agent instance."""
    return EmpathyAgent()
