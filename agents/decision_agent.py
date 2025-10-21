"""
Decision Agent - Makes decisions on actions and escalations.
Enhanced with compliance checks, multi-channel recommendations, and escalation tracking.
"""
import json
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI

from models import AgentState
from config.prompts import SYSTEM_PROMPTS
from config import settings
from utils.data_analytics import DataAnalytics
from utils.escalation_tracker import EscalationTracker


class DecisionAgent:
    """Makes strategic proactive decisions.

    Responsibilities:
    - Recommend next best proactive action (retention offer, wellness check, premium outreach)
    - Determine if human escalation is warranted (high churn risk VIP, severe dissatisfaction, very high LTV risk)
    - Assign qualitative priority level (low/medium/high/critical/handled)
    - Produce channel mix respecting marketing opt-in & regional preferences
    - Enforce compliance (no promotional outreach for opt-out customers)
    - Prevent duplicate automated handling when human escalation is active
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
        
        # Initialize data analytics for support history and churn insights
        self.analytics = DataAnalytics()
        
        # Initialize escalation tracker to prevent duplicate handling
        self.escalation_tracker = EscalationTracker()
    
    def _check_marketing_compliance(self, customer) -> Dict[str, Any]:
        """
        Check marketing compliance based on opt-in status.
        
        Args:
            customer: Customer object
            
        Returns:
            Dictionary with compliance information
        """
        can_contact = customer.opt_in_marketing if customer.opt_in_marketing is not None else True
        
        compliance_info = {
            "can_send_marketing": can_contact,
            "can_send_promotional": can_contact,
            "can_send_transactional": True,  # Always allowed
            "can_send_service": True,  # Always allowed for service-related
            "restrictions": []
        }
        
        if not can_contact:
            compliance_info["restrictions"].append("⚠️ Customer opted out of marketing communications")
            compliance_info["restrictions"].append("Only send transactional and service-related messages")
            compliance_info["restrictions"].append("Do NOT send promotional offers, newsletters, or marketing campaigns")
        
        return compliance_info
    
    def _recommend_channels(self, state: AgentState) -> List[Dict[str, Any]]:
        """
        Recommend appropriate communication channels based on customer profile and compliance.
        
        Args:
            state: Current agent state
            
        Returns:
            List of recommended channels with priorities
        """
        customer = state.customer
        channels = []
        
        # Get compliance info
        compliance = self._check_marketing_compliance(customer)
        
        # Get support history for context
        support_history = self.analytics.get_customer_support_history(customer)
        avg_csat = support_history.get('avg_csat') if support_history else None
        
        # Email (always available)
        email_channel = {
            "channel": "email",
            "address": customer.email,
            "priority": "primary",
            "compliance": "always_allowed",
            "notes": "Primary communication channel"
        }
        channels.append(email_channel)
        
        # Phone/SMS (if available and appropriate)
        if customer.phone:
            # High-priority cases warrant phone contact
            if state.priority_level in ["critical", "high"]:
                phone_channel = {
                    "channel": "phone",
                    "number": customer.phone,
                    "priority": "high",
                    "compliance": "service_allowed",
                    "notes": f"{state.priority_level.upper()} priority - Personal call recommended"
                }
                
                # Add urgency context
                if state.urgency_level and state.urgency_level >= 4:
                    phone_channel["notes"] += " | URGENT - Contact within 24 hours"
                
                # Add support history context
                if avg_csat and avg_csat < 3.5:
                    phone_channel["notes"] += f" | Low CSAT history ({avg_csat:.1f}) - Extra care needed"
                
                channels.append(phone_channel)
            
            # SMS for quick updates (compliance-aware)
            if compliance["can_send_marketing"] or state.priority_level in ["critical", "high"]:
                sms_channel = {
                    "channel": "sms",
                    "number": customer.phone,
                    "priority": "medium",
                    "compliance": "allowed" if compliance["can_send_marketing"] else "service_only",
                    "notes": "Quick updates and notifications"
                }
                
                if not compliance["can_send_marketing"]:
                    sms_channel["notes"] += " | ⚠️ Service-related only (no marketing)"
                
                channels.append(sms_channel)
        
        # In-app notifications (if customer is active)
        if customer.days_since_active is not None and customer.days_since_active < 7:
            app_channel = {
                "channel": "in_app",
                "priority": "medium",
                "compliance": "always_allowed",
                "notes": "Active user - In-app notifications effective"
            }
            channels.append(app_channel)
        
        # WhatsApp (for Indian market with phone)
        if customer.country == "India" and customer.phone and compliance["can_send_marketing"]:
            whatsapp_channel = {
                "channel": "whatsapp",
                "number": customer.phone,
                "priority": "medium",
                "compliance": "requires_opt_in",
                "notes": "Popular in India - Consider for high-value customers"
            }
            channels.append(whatsapp_channel)
        
        return channels
    
    def _should_escalate(self, state: AgentState) -> bool:
        """Determine if escalation is needed based on proactive-first rules.

        Logic (proactive-only):
        - VIP with very high churn risk (>80%)
        - Very low CSAT history (<2.5) indicating repeated dissatisfaction
        - High-value (LTV > $5000) with critical churn risk (>85%)
        All other proactive situations are handled without human escalation.
        """
        # Get support history
        support_history = self.analytics.get_customer_support_history(state.customer)
        
        # Proactive-only escalation rules
        # VIP with very high churn risk
        if state.customer.is_vip and state.predicted_churn_risk and state.predicted_churn_risk >= 0.8:
            return True

        # Repeated poor CSAT history
        if support_history:
            avg_csat = support_history.get('avg_csat')
            if avg_csat and avg_csat < 2.5:
                return True

        # High-value critical churn risk
        if state.customer.lifetime_value > 5000 and state.predicted_churn_risk and state.predicted_churn_risk >= 0.85:
            return True

        return False
    
    def _determine_priority(self, state: AgentState) -> str:
        """
        Determine priority level.
        Enhanced with NPS and support history.
        
        Args:
            state: Current agent state
            
        Returns:
            Priority level: low, medium, high, or critical
        """
        # Get NPS data
        nps_data = self.analytics.get_customer_nps(state.customer)
        nps_category = nps_data.get('nps_category') if nps_data else None
        
        # Get support history
        support_history = self.analytics.get_customer_support_history(state.customer)
        avg_csat = support_history.get('avg_csat') if support_history else None
        
        # Check for critical conditions
        if state.customer.segment == "VIP":
            return "critical"
        
        if state.urgency_level and state.urgency_level >= 4:
            return "critical"
        
        if state.predicted_churn_risk and state.predicted_churn_risk >= 0.8:
            return "critical"
        
        # NPS Detractors with complaints need critical attention
        if nps_category == "Detractor" and state.sentiment and \
           state.sentiment.value in ["negative", "very_negative"]:
            return "critical"
        
        # Low CSAT history escalates priority
        if avg_csat and avg_csat < 3.0:
            return "critical"
        
        # High priority
        if state.customer.segment == "Loyal" or state.customer.is_high_value:
            if state.urgency_level and state.urgency_level >= 3:
                return "high"
        
        if state.sentiment and state.sentiment.value == "very_negative":
            return "high"
        
        # NPS Passives with issues get high priority
        if nps_category == "Passive" and state.urgency_level and state.urgency_level >= 3:
            return "high"
        
        # Medium priority
        if state.urgency_level and state.urgency_level >= 2:
            return "medium"
        
        # Default to low
        return "low"
    
    def make_decision(self, state: AgentState) -> AgentState:
        """
        Make decision on actions and escalations.
        Enhanced with compliance checks, multi-channel recommendations, and escalation tracking.
        
        Args:
            state: Current agent state with context and pattern analysis
            
        Returns:
            Updated state with decision, compliance info, and channel recommendations
        """
        if not state.customer or not state.context_summary:
            state.add_message("decision_agent", "Error: Missing required data")
            return state
        
        # 🚨 NEW: Check if customer is already escalated to human
        skip_decision = self.escalation_tracker.should_skip_customer(state.customer.customer_id)
        
        if skip_decision['should_skip']:
            # Customer is currently being handled by human - skip automated intervention
            state.add_message(
                "decision_agent",
                f"⏭️ SKIPPING: {skip_decision['reason']}"
            )
            state.add_message(
                "decision_agent",
                f"Context: {skip_decision['context']}"
            )
            
            # Mark this explicitly in state
            state.escalation_needed = False  # Don't re-escalate
            state.priority_level = "handled"  # Special status
            state.recommended_action = f"Customer already escalated ({skip_decision.get('escalation_id')}). Human agent handling."
            
            if skip_decision.get('assigned_to'):
                state.add_message(
                    "decision_agent",
                    f"Assigned to: {skip_decision['assigned_to']}"
                )
            
            return state
        
        # If stale escalation, add context
        if skip_decision.get('is_stale'):
            state.add_message(
                "decision_agent",
                f"⚠️ Note: {skip_decision['context']}"
            )
        
        # Check marketing compliance
        compliance_info = self._check_marketing_compliance(state.customer)
        
        # Get recommended channels
        recommended_channels = self._recommend_channels(state)
        
        # Determine escalation and priority
        escalation_needed = self._should_escalate(state)
        priority_level = self._determine_priority(state)
        
        # Get support history and churn data for context
        support_history = self.analytics.get_customer_support_history(state.customer)
        churn_data = self.analytics.get_actual_churn_status(state.customer)
        
        # Build enhanced context for LLM
        enhanced_context = f"\n\nCOMPLIANCE & CHANNEL INFO:\n"
        enhanced_context += f"Marketing Opt-in: {'YES' if compliance_info['can_send_marketing'] else 'NO (⚠️ NO PROMOTIONAL CONTENT)'}\n"
        enhanced_context += f"Recommended Channels: {', '.join([ch['channel'] for ch in recommended_channels])}\n"
        
        if support_history:
            enhanced_context += f"\nSupport History: {support_history.get('total_tickets', 0)} tickets, "
            if support_history.get('avg_csat'):
                enhanced_context += f"Avg CSAT: {support_history['avg_csat']:.1f}/5.0\n"
        
        if churn_data and churn_data.get('is_churned'):
            enhanced_context += f"\n⚠️ CHURN ALERT: Customer has churned - Reason: {churn_data.get('churn_reason')}\n"
        
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
        
        # Add enhanced context
        prompt_text += enhanced_context
        
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
            
            # 🚨 NEW: Create escalation record if escalation is needed
            if state.escalation_needed:
                escalation_reason = result.get("reasoning", "Automated escalation based on customer risk")
                escalation_id = self.escalation_tracker.create_escalation(
                    customer_id=state.customer.customer_id,
                    reason=escalation_reason,
                    priority=state.priority_level,
                    health_score=state.customer_risk_score or 0,
                    assigned_to=None  # Will be assigned by human agent team
                )
                
                state.add_message(
                    "decision_agent",
                    f"🚨 Escalation created: {escalation_id}"
                )
            
            # Store compliance and channel info in metadata
            if not hasattr(state, 'metadata'):
                state.metadata = {}
            state.metadata['compliance'] = compliance_info
            state.metadata['recommended_channels'] = recommended_channels
            
            # Build decision message
            decision_msg = f"Decision made: Priority={state.priority_level}, "
            decision_msg += f"Escalation={'Yes' if state.escalation_needed else 'No'}, "
            decision_msg += f"Marketing={'Allowed' if compliance_info['can_send_marketing'] else 'RESTRICTED'}"
            
            state.add_message("decision_agent", decision_msg)
            
            # Add channel recommendations
            primary_channels = [ch for ch in recommended_channels if ch['priority'] in ['primary', 'high']]
            if primary_channels:
                channels_msg = "Recommended channels: " + ", ".join([
                    f"{ch['channel']} ({ch['priority']})" for ch in primary_channels
                ])
                state.add_message("decision_agent", channels_msg)
            
            # Add compliance restrictions if any
            if compliance_info['restrictions']:
                state.add_message("decision_agent", f"⚠️ Restrictions: {'; '.join(compliance_info['restrictions'][:2])}")
            
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
            
            # Store compliance and channel info even on error
            if not hasattr(state, 'metadata'):
                state.metadata = {}
            state.metadata['compliance'] = compliance_info
            state.metadata['recommended_channels'] = recommended_channels
        
        return state
    
    def __call__(self, state: AgentState) -> AgentState:
        """Make the agent callable."""
        return self.make_decision(state)


# Factory function for LangGraph
def create_decision_agent():
    """Create a decision agent instance."""
    return DecisionAgent()
