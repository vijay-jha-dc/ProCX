"""
Event Simulator - Generates realistic customer events for testing.
"""
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd

from models import Customer, CustomerEvent, EventType
from config import settings


class EventSimulator:
    """
    Simulates customer events for testing and development:
    - Generates realistic customer scenarios
    - Creates various event types
    - Simulates different customer segments
    """
    
    def __init__(self, dataset_path: Optional[str] = None):
        """
        Initialize the Event Simulator.
        
        Args:
            dataset_path: Path to customer dataset
        """
        self.dataset_path = dataset_path or settings.DATASET_PATH
        self.customers_df = None
        self.load_customers()
    
    def load_customers(self):
        """Load customer data from dataset."""
        try:
            self.customers_df = pd.read_excel(self.dataset_path)
            print(f"[OK] Loaded {len(self.customers_df)} customers")
        except Exception as e:
            print(f"[ERROR] Error loading customers: {e}")
            self.customers_df = None
    
    def get_random_customer(self, segment: Optional[str] = None) -> Optional[Customer]:
        """
        Get a random customer from the dataset.
        
        Args:
            segment: Optional segment filter (VIP, Loyal, Regular, Occasional)
            
        Returns:
            Customer object or None
        """
        if self.customers_df is None:
            return None
        
        df = self.customers_df
        if segment:
            df = df[df["segment"] == segment]
        
        if len(df) == 0:
            return None
        
        row = df.sample(n=1).iloc[0]
        
        return Customer(
            customer_id=row["customer_id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row["email"],
            segment=row["segment"],
            lifetime_value=float(row["lifetime_value"]),
            preferred_category=row["preferred_category"],
            loyalty_tier=row["loyalty_tier"],
            # New fields from original dataset
            phone=str(row["phone"]) if pd.notna(row.get("phone")) else None,
            signup_date=str(row["signup_date"]) if pd.notna(row.get("signup_date")) else None,
            country=str(row["country"]) if pd.notna(row.get("country")) else None,
            avg_order_value=float(row["avg_order_value"]) if pd.notna(row.get("avg_order_value")) else None,
            last_active_date=str(row["last_active_date"]) if pd.notna(row.get("last_active_date")) else None,
            opt_in_marketing=bool(row["opt_in_marketing"]) if pd.notna(row.get("opt_in_marketing")) else None,
            language=str(row["language"]) if pd.notna(row.get("language")) else None
        )
    
    def get_customer_by_id(self, customer_id: str) -> Optional[Customer]:
        """
        Get specific customer by ID.
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Customer object or None
        """
        if self.customers_df is None:
            return None
        
        row = self.customers_df[self.customers_df["customer_id"] == customer_id]
        
        if len(row) == 0:
            return None
        
        row = row.iloc[0]
        
        return Customer(
            customer_id=row["customer_id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row["email"],
            segment=row["segment"],
            lifetime_value=float(row["lifetime_value"]),
            preferred_category=row["preferred_category"],
            loyalty_tier=row["loyalty_tier"],
            # New fields from original dataset
            phone=str(row["phone"]) if pd.notna(row.get("phone")) else None,
            signup_date=str(row["signup_date"]) if pd.notna(row.get("signup_date")) else None,
            country=str(row["country"]) if pd.notna(row.get("country")) else None,
            avg_order_value=float(row["avg_order_value"]) if pd.notna(row.get("avg_order_value")) else None,
            last_active_date=str(row["last_active_date"]) if pd.notna(row.get("last_active_date")) else None,
            opt_in_marketing=bool(row["opt_in_marketing"]) if pd.notna(row.get("opt_in_marketing")) else None,
            language=str(row["language"]) if pd.notna(row.get("language")) else None
        )
    
    def generate_event(
        self,
        customer: Optional[Customer] = None,
        event_type: Optional[EventType] = None
    ) -> CustomerEvent:
        """
        Generate a realistic customer event.
        
        Args:
            customer: Customer object (random if not provided)
            event_type: Specific event type (random if not provided)
            
        Returns:
            CustomerEvent object
        """
        # Get customer
        if customer is None:
            customer = self.get_random_customer()
        
        if customer is None:
            raise ValueError("No customers available")
        
        # Get event type
        if event_type is None:
            event_type = random.choice(list(EventType))
        
        # Generate event description based on type
        description = self._generate_event_description(customer, event_type)
        
        # Generate event ID
        event_id = f"EVT_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}"
        
        # Create event
        event = CustomerEvent(
            event_id=event_id,
            customer=customer,
            event_type=event_type,
            timestamp=datetime.now(),
            description=description,
            metadata=self._generate_metadata(customer, event_type)
        )
        
        return event
    
    def _generate_event_description(
        self,
        customer: Customer,
        event_type: EventType
    ) -> str:
        """Generate realistic event description."""
        
        descriptions = {
            EventType.ORDER_PLACED: [
                f"Placed an order for {customer.preferred_category} items worth ${{amount:.2f}}",
                f"New order in {customer.preferred_category} category - Order #{{order_id}}",
                f"Customer purchased {customer.preferred_category} products totaling ${{amount:.2f}}"
            ],
            EventType.ORDER_DELAYED: [
                f"Order #{{order_id}} for {customer.preferred_category} is delayed by {{days}} days",
                f"Shipment delayed - {customer.preferred_category} order expected {{days}} days late",
                f"Customer inquiring about delayed {customer.preferred_category} order #{{order_id}}"
            ],
            EventType.ORDER_CANCELLED: [
                f"Order #{{order_id}} cancelled - {customer.preferred_category} items",
                f"Customer cancelled {customer.preferred_category} order worth ${{amount:.2f}}",
                f"Cancellation request for order #{{order_id}}"
            ],
            EventType.COMPLAINT: [
                f"Complaint about {customer.preferred_category} product quality",
                f"Customer unhappy with recent {customer.preferred_category} purchase",
                f"Filed complaint regarding order #{{order_id}} - {customer.preferred_category}"
            ],
            EventType.INQUIRY: [
                f"Inquiry about {customer.preferred_category} product availability",
                f"Question regarding {customer.preferred_category} order status",
                f"General inquiry about {customer.loyalty_tier} tier benefits"
            ],
            EventType.FEEDBACK: [
                f"Positive feedback on {customer.preferred_category} purchase",
                f"Customer shared experience with recent {customer.preferred_category} order",
                f"Feedback submitted for order #{{order_id}}"
            ],
            EventType.RETURN_REQUEST: [
                f"Return request for {customer.preferred_category} order #{{order_id}}",
                f"Customer wants to return {customer.preferred_category} items",
                f"Return initiated for order worth ${{amount:.2f}}"
            ]
        }
        
        # Select random template
        template = random.choice(descriptions[event_type])
        
        # Fill in placeholders
        description = template.format(
            order_id=f"ORD{random.randint(100000, 999999)}",
            amount=random.uniform(50, 500),
            days=random.randint(2, 10)
        )
        
        return description
    
    def _generate_metadata(
        self,
        customer: Customer,
        event_type: EventType
    ) -> Dict[str, Any]:
        """Generate event metadata."""
        metadata = {
            "channel": random.choice(["email", "chat", "phone", "web"]),
            "priority": random.choice(["low", "medium", "high"]),
            "tags": [customer.preferred_category, event_type.value]
        }
        
        # Add type-specific metadata
        if event_type in [EventType.ORDER_PLACED, EventType.ORDER_DELAYED, 
                          EventType.ORDER_CANCELLED]:
            metadata["order_id"] = f"ORD{random.randint(100000, 999999)}"
            metadata["order_amount"] = round(random.uniform(50, 500), 2)
        
        return metadata
    
    def generate_scenario(self, scenario_name: str) -> CustomerEvent:
        """
        Generate predefined scenario for testing.
        
        Args:
            scenario_name: Name of the scenario
            
        Returns:
            CustomerEvent object
        """
        scenarios = {
            "vip_complaint": {
                "segment": "VIP",
                "event_type": EventType.COMPLAINT,
                "custom_description": "Extremely unhappy with delayed premium order. This is the third time!"
            },
            "loyal_order_delay": {
                "segment": "Loyal",
                "event_type": EventType.ORDER_DELAYED,
                "custom_description": "Order delayed by 5 days. Need it urgently for a gift."
            },
            "new_customer_inquiry": {
                "segment": "Occasional",
                "event_type": EventType.INQUIRY,
                "custom_description": "First time buyer asking about shipping times and return policy."
            },
            "high_value_at_risk": {
                "segment": "VIP",
                "event_type": EventType.ORDER_CANCELLED,
                "custom_description": "Cancelled order due to poor experience. Considering switching to competitor."
            },
            "positive_feedback": {
                "segment": "Loyal",
                "event_type": EventType.FEEDBACK,
                "custom_description": "Absolutely loved the recent purchase! Best customer service ever."
            }
        }
        
        if scenario_name not in scenarios:
            raise ValueError(f"Unknown scenario: {scenario_name}")
        
        scenario = scenarios[scenario_name]
        customer = self.get_random_customer(segment=scenario["segment"])
        
        if customer is None:
            raise ValueError(f"No customers found for segment: {scenario['segment']}")
        
        event_id = f"SCENARIO_{scenario_name.upper()}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return CustomerEvent(
            event_id=event_id,
            customer=customer,
            event_type=scenario["event_type"],
            timestamp=datetime.now(),
            description=scenario["custom_description"],
            metadata={"scenario": scenario_name}
        )
    
    def get_available_scenarios(self) -> List[str]:
        """Get list of available predefined scenarios."""
        return [
            "vip_complaint",
            "loyal_order_delay",
            "new_customer_inquiry",
            "high_value_at_risk",
            "positive_feedback"
        ]
    
    def get_dataset_stats(self) -> Dict[str, Any]:
        """Get statistics about the loaded dataset."""
        if self.customers_df is None:
            return {"error": "No dataset loaded"}
        
        return {
            "total_customers": len(self.customers_df),
            "segments": self.customers_df["segment"].value_counts().to_dict(),
            "loyalty_tiers": self.customers_df["loyalty_tier"].value_counts().to_dict(),
            "categories": self.customers_df["preferred_category"].value_counts().to_dict(),
            "lifetime_value_stats": {
                "mean": float(self.customers_df["lifetime_value"].mean()),
                "median": float(self.customers_df["lifetime_value"].median()),
                "min": float(self.customers_df["lifetime_value"].min()),
                "max": float(self.customers_df["lifetime_value"].max())
            }
        }
