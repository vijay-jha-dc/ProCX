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
    ORDER_PLACED = "order_placed"
    ORDER_DELAYED = "order_delayed"
    ORDER_CANCELLED = "order_cancelled"
    COMPLAINT = "complaint"
    INQUIRY = "inquiry"
    FEEDBACK = "feedback"
    RETURN_REQUEST = "return_request"


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
            "loyalty_tier": self.loyalty_tier
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "customer_id": self.customer.customer_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "description": self.description,
            "metadata": self.metadata
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
