"""
Customer data models and schemas for AgentMAX CX Platform.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class Segment(Enum):
    """Customer segment classification."""
    VIP = "VIP"
    LOYAL = "Loyal"
    REGULAR = "Regular"
    OCCASIONAL = "Occasional"


class LoyaltyTier(Enum):
    """Customer loyalty tier."""
    PLATINUM = "Platinum"
    GOLD = "Gold"
    SILVER = "Silver"
    BRONZE = "Bronze"


class SentimentType(Enum):
    """Sentiment classification."""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class EventType(Enum):
    """Customer event types."""
    # Reactive Events (Customer-initiated)
    ORDER_PLACED = "order_placed"
    ORDER_DELAYED = "order_delayed"
    ORDER_CANCELLED = "order_cancelled"
    COMPLAINT = "complaint"
    INQUIRY = "inquiry"
    FEEDBACK = "feedback"
    RETURN_REQUEST = "return_request"
    
    # Proactive Events (System-initiated)
    PROACTIVE_RETENTION = "proactive_retention"  # Churn prevention outreach
    PROACTIVE_UPSELL = "proactive_upsell"  # Personalized upgrade offer
    PROACTIVE_CHECK_IN = "proactive_check_in"  # Wellness check for high-value customers
    PROACTIVE_MILESTONE = "proactive_milestone"  # Celebrate customer milestones
    PROACTIVE_FEEDBACK_REQUEST = "proactive_feedback_request"  # Request feedback proactively


@dataclass
class Customer:
    """Customer profile information."""
    customer_id: str
    first_name: str
    last_name: str
    email: str
    segment: str
    lifetime_value: float
    preferred_category: str
    loyalty_tier: str
    
    # New fields from original dataset
    phone: Optional[str] = None
    signup_date: Optional[str] = None  # ISO format: YYYY-MM-DD
    country: Optional[str] = None
    avg_order_value: Optional[float] = None
    last_active_date: Optional[str] = None  # ISO format: YYYY-MM-DD
    opt_in_marketing: Optional[bool] = None
    language: Optional[str] = None  # Language code: en, hi, ta, te, bn
    
    @property
    def full_name(self) -> str:
        """Get customer's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_vip(self) -> bool:
        """Check if customer is VIP."""
        return self.segment == "VIP"
    
    @property
    def is_high_value(self) -> bool:
        """Check if customer has high lifetime value."""
        return self.lifetime_value > 5000
    
    @property
    def days_since_signup(self) -> Optional[int]:
        """Calculate days since customer signup."""
        if not self.signup_date:
            return None
        try:
            signup = datetime.fromisoformat(self.signup_date)
            return (datetime.now() - signup).days
        except (ValueError, TypeError):
            return None
    
    @property
    def days_since_active(self) -> Optional[int]:
        """Calculate days since last activity."""
        if not self.last_active_date:
            return None
        try:
            last_active = datetime.fromisoformat(self.last_active_date)
            return (datetime.now() - last_active).days
        except (ValueError, TypeError):
            return None
    
    @property
    def is_inactive(self) -> bool:
        """Check if customer is inactive (>90 days since last activity)."""
        days = self.days_since_active
        return days is not None and days > 90
    
    @property
    def is_high_spender(self) -> bool:
        """Check if customer has high average order value."""
        return self.avg_order_value is not None and self.avg_order_value > 70
    
    @property
    def can_contact_marketing(self) -> bool:
        """Check if customer opted in for marketing communications."""
        return self.opt_in_marketing is True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "customer_id": self.customer_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "segment": self.segment,
            "lifetime_value": self.lifetime_value,
            "preferred_category": self.preferred_category,
            "loyalty_tier": self.loyalty_tier,
            "phone": self.phone,
            "signup_date": self.signup_date,
            "country": self.country,
            "avg_order_value": self.avg_order_value,
            "last_active_date": self.last_active_date,
            "opt_in_marketing": self.opt_in_marketing,
            "language": self.language
        }


@dataclass
class CustomerEvent:
    """Customer interaction event."""
    event_id: str
    customer: Customer
    event_type: EventType
    timestamp: datetime
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_proactive(self) -> bool:
        """Check if this is a proactive (system-initiated) event."""
        proactive_types = [
            EventType.PROACTIVE_RETENTION,
            EventType.PROACTIVE_UPSELL,
            EventType.PROACTIVE_CHECK_IN,
            EventType.PROACTIVE_MILESTONE,
            EventType.PROACTIVE_FEEDBACK_REQUEST
        ]
        return self.event_type in proactive_types
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "customer_id": self.customer.customer_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "description": self.description,
            "metadata": self.metadata,
            "is_proactive": self.is_proactive
        }


@dataclass
class AgentState:
    """State object passed between agents in the workflow."""
    # Input
    event: Optional[CustomerEvent] = None
    customer: Optional[Customer] = None
    
    # Context Analysis
    context_summary: Optional[str] = None
    sentiment: Optional[SentimentType] = None
    urgency_level: Optional[int] = None  # 1-5 scale
    customer_risk_score: Optional[float] = None  # 0-1 scale
    
    # Pattern Recognition
    similar_patterns: List[Dict[str, Any]] = field(default_factory=list)
    historical_insights: Optional[str] = None
    predicted_churn_risk: Optional[float] = None
    
    # Decision Making
    recommended_action: Optional[str] = None
    escalation_needed: bool = False
    priority_level: Optional[str] = None  # low, medium, high, critical
    
    # Empathy & Response
    empathy_score: Optional[float] = None
    personalized_response: Optional[str] = None
    tone: Optional[str] = None
    
    # Agent Communication
    messages: List[Dict[str, str]] = field(default_factory=list)
    next_agent: Optional[str] = None
    
    # Metadata
    processing_time: float = 0.0
    confidence_score: float = 0.0
    
    def add_message(self, agent: str, message: str):
        """Add a message from an agent."""
        self.messages.append({
            "agent": agent,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event": self.event.to_dict() if self.event else None,
            "customer": self.customer.to_dict() if self.customer else None,
            "context_summary": self.context_summary,
            "sentiment": self.sentiment.value if self.sentiment else None,
            "urgency_level": self.urgency_level,
            "customer_risk_score": self.customer_risk_score,
            "similar_patterns": self.similar_patterns,
            "historical_insights": self.historical_insights,
            "predicted_churn_risk": self.predicted_churn_risk,
            "recommended_action": self.recommended_action,
            "escalation_needed": self.escalation_needed,
            "priority_level": self.priority_level,
            "empathy_score": self.empathy_score,
            "personalized_response": self.personalized_response,
            "tone": self.tone,
            "messages": self.messages,
            "processing_time": self.processing_time,
            "confidence_score": self.confidence_score
        }
