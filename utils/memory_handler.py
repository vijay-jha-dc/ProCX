"""
Memory Handler - Manages conversation history and state persistence.
"""
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

from models import AgentState, CustomerEvent, Customer
from config import settings


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle Customer objects and other types."""
    
    def default(self, obj):
        if isinstance(obj, Customer):
            return obj.to_dict()
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return super().default(obj)


class MemoryHandler:
    """
    Handles memory management for the agent system:
    - Stores conversation history
    - Retrieves relevant past interactions
    - Manages state persistence
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize the Memory Handler.
        
        Args:
            storage_path: Path to store memory files
        """
        self.storage_path = storage_path or settings.DATA_DIR / "memory"
        self.storage_path.mkdir(exist_ok=True)
        
        self.max_history = settings.MEMORY_MAX_HISTORY
        self.relevance_threshold = settings.MEMORY_RELEVANCE_THRESHOLD
        
        # In-memory cache
        self.session_history: List[Dict[str, Any]] = []
    
    def save_interaction(self, state: AgentState) -> str:
        """
        Save an interaction to memory.
        
        Args:
            state: Agent state to save
            
        Returns:
            Interaction ID
        """
        interaction_id = f"interaction_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        interaction = {
            "interaction_id": interaction_id,
            "timestamp": datetime.now().isoformat(),
            "customer_id": state.customer.customer_id if state.customer else None,
            "event_type": state.event.event_type.value if state.event else None,
            "state": state.to_dict()
        }
        
        # Add to session history
        self.session_history.append(interaction)
        
        # Persist to disk
        if state.customer:
            customer_file = self.storage_path / f"{state.customer.customer_id}.jsonl"
            with open(customer_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(interaction, cls=CustomJSONEncoder) + "\n")
        
        return interaction_id
    
    def get_customer_history(
        self,
        customer_id: str,
        max_items: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve customer's interaction history.
        
        Args:
            customer_id: Customer ID
            max_items: Maximum number of items to retrieve
            
        Returns:
            List of past interactions
        """
        customer_file = self.storage_path / f"{customer_id}.jsonl"
        
        if not customer_file.exists():
            return []
        
        history = []
        with open(customer_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    history.append(json.loads(line))
        
        # Sort by timestamp (most recent first)
        history.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Limit results
        if max_items:
            history = history[:max_items]
        else:
            history = history[:self.max_history]
        
        return history
    
    def get_recent_interactions(
        self,
        customer_id: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get recent interactions within specified days.
        
        Args:
            customer_id: Customer ID
            days: Number of days to look back
            
        Returns:
            List of recent interactions
        """
        all_history = self.get_customer_history(customer_id)
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent = [
            interaction for interaction in all_history
            if datetime.fromisoformat(interaction["timestamp"]) > cutoff_date
        ]
        
        return recent
    
    def find_similar_interactions(
        self,
        event_type: str,
        customer_segment: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar interactions across all customers.
        
        Args:
            event_type: Type of event to match
            customer_segment: Optional customer segment filter
            limit: Maximum number of results
            
        Returns:
            List of similar interactions
        """
        similar = []
        
        # Search through all customer files
        for customer_file in self.storage_path.glob("*.jsonl"):
            with open(customer_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        interaction = json.loads(line)
                        
                        # Check event type match
                        if interaction.get("event_type") == event_type:
                            # Check segment if specified
                            if customer_segment:
                                customer_data = interaction.get("state", {}).get("customer", {})
                                if customer_data.get("segment") != customer_segment:
                                    continue
                            
                            similar.append(interaction)
                            
                            if len(similar) >= limit:
                                break
            
            if len(similar) >= limit:
                break
        
        return similar[:limit]
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get summary of current session.
        
        Returns:
            Session summary statistics
        """
        if not self.session_history:
            return {"total_interactions": 0}
        
        summary = {
            "total_interactions": len(self.session_history),
            "start_time": self.session_history[0]["timestamp"],
            "end_time": self.session_history[-1]["timestamp"],
            "unique_customers": len(set(
                i.get("customer_id") for i in self.session_history
                if i.get("customer_id")
            )),
            "event_types": {}
        }
        
        # Count event types
        for interaction in self.session_history:
            event_type = interaction.get("event_type", "unknown")
            summary["event_types"][event_type] = \
                summary["event_types"].get(event_type, 0) + 1
        
        return summary
    
    def clear_session(self):
        """Clear current session history."""
        self.session_history = []
    
    def export_customer_data(
        self,
        customer_id: str,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Export all data for a specific customer.
        
        Args:
            customer_id: Customer ID
            output_path: Optional output path
            
        Returns:
            Path to exported file
        """
        history = self.get_customer_history(customer_id, max_items=None)
        
        if not output_path:
            output_path = self.storage_path / f"export_{customer_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({
                "customer_id": customer_id,
                "export_date": datetime.now().isoformat(),
                "total_interactions": len(history),
                "interactions": history
            }, f, indent=2)
        
        return output_path
