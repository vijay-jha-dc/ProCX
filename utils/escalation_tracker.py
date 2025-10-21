"""
Escalation Tracker - Manages human escalation state and prevents duplicate handling.
Tracks which customers have been escalated, their resolution status, and ensures
proper handling across multiple proactive scans.
"""
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict

from config import settings


@dataclass
class EscalationRecord:
    """Represents a customer escalation to human agent."""
    customer_id: str
    escalation_id: str
    escalated_at: datetime
    reason: str
    priority: str  # critical, high, medium
    health_score: int
    assigned_to: Optional[str] = None  # Human agent name/ID
    status: str = "open"  # open, in_progress, resolved, closed
    resolution_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None
    last_updated: datetime = None
    
    # NEW: Track interaction history
    interaction_history: List[Dict[str, Any]] = None  # Stores all actions taken
    
    def __post_init__(self):
        """Set last_updated to current time if not provided."""
        if self.last_updated is None:
            self.last_updated = datetime.now()
        if self.interaction_history is None:
            self.interaction_history = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with ISO format dates."""
        data = asdict(self)
        data['escalated_at'] = self.escalated_at.isoformat()
        data['last_updated'] = self.last_updated.isoformat()
        if self.resolved_at:
            data['resolved_at'] = self.resolved_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EscalationRecord':
        """Create from dictionary with date parsing."""
        data['escalated_at'] = datetime.fromisoformat(data['escalated_at'])
        data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        if data.get('resolved_at'):
            data['resolved_at'] = datetime.fromisoformat(data['resolved_at'])
        return cls(**data)


class EscalationTracker:
    """
    Tracks customer escalations to prevent duplicate handling.
    Maintains state across multiple proactive scans.
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize the Escalation Tracker.
        
        Args:
            storage_path: Path to store escalation records
        """
        self.storage_path = storage_path or (settings.DATA_DIR / "escalations")
        self.storage_path.mkdir(exist_ok=True, parents=True)
        
        self.escalations_file = self.storage_path / "active_escalations.jsonl"
        self.history_file = self.storage_path / "escalation_history.jsonl"
        
        # In-memory cache of active escalations
        self.active_escalations: Dict[str, EscalationRecord] = {}
        self._load_active_escalations()
    
    def _load_active_escalations(self):
        """Load active escalations from disk into memory."""
        if not self.escalations_file.exists():
            return
        
        try:
            with open(self.escalations_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        record = EscalationRecord.from_dict(data)
                        
                        # Only load if still active (not resolved or within time window)
                        if record.status in ["open", "in_progress"]:
                            self.active_escalations[record.customer_id] = record
            
            print(f"[OK] EscalationTracker: Loaded {len(self.active_escalations)} active escalations")
        except Exception as e:
            print(f"[WARN] EscalationTracker: Error loading escalations: {e}")
    
    def _save_active_escalations(self):
        """Save active escalations to disk."""
        try:
            with open(self.escalations_file, 'w', encoding='utf-8') as f:
                for record in self.active_escalations.values():
                    f.write(json.dumps(record.to_dict()) + '\n')
        except Exception as e:
            print(f"[ERROR] EscalationTracker: Error saving escalations: {e}")
    
    def _archive_to_history(self, record: EscalationRecord):
        """Archive a resolved escalation to history."""
        try:
            with open(self.history_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(record.to_dict()) + '\n')
        except Exception as e:
            print(f"[ERROR] EscalationTracker: Error archiving to history: {e}")
    
    def is_customer_escalated(self, customer_id: str) -> bool:
        """
        Check if customer is currently escalated.
        
        Args:
            customer_id: Customer ID to check
            
        Returns:
            True if customer has an active escalation
        """
        return customer_id in self.active_escalations
    
    def get_escalation_status(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """
        Get escalation status for a customer.
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Escalation status dict or None
        """
        record = self.active_escalations.get(customer_id)
        if not record:
            return None
        
        return {
            "is_escalated": True,
            "escalation_id": record.escalation_id,
            "status": record.status,
            "priority": record.priority,
            "escalated_at": record.escalated_at,
            "days_since_escalation": (datetime.now() - record.escalated_at).days,
            "assigned_to": record.assigned_to,
            "reason": record.reason,
            "should_skip": record.status in ["open", "in_progress"]  # Skip if not resolved
        }
    
    def create_escalation(
        self,
        customer_id: str,
        reason: str,
        priority: str,
        health_score: int,
        assigned_to: Optional[str] = None
    ) -> str:
        """
        Create a new escalation record.
        
        Args:
            customer_id: Customer ID
            reason: Reason for escalation
            priority: Priority level (critical, high, medium)
            health_score: Customer health score
            assigned_to: Optional human agent assignment
            
        Returns:
            Escalation ID
        """
        escalation_id = f"ESC_{customer_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        record = EscalationRecord(
            customer_id=customer_id,
            escalation_id=escalation_id,
            escalated_at=datetime.now(),
            reason=reason,
            priority=priority,
            health_score=health_score,
            assigned_to=assigned_to,
            status="open"
        )
        
        self.active_escalations[customer_id] = record
        self._save_active_escalations()
        
        print(f"[ESCALATION] Customer {customer_id} escalated: {reason} (Priority: {priority})")
        
        return escalation_id
    
    def update_escalation_status(
        self,
        customer_id: str,
        status: str,
        resolution_notes: Optional[str] = None,
        assigned_to: Optional[str] = None
    ) -> bool:
        """
        Update escalation status.
        
        Args:
            customer_id: Customer ID
            status: New status (open, in_progress, resolved, closed)
            resolution_notes: Optional resolution notes
            assigned_to: Optional human agent assignment
            
        Returns:
            True if updated successfully
        """
        record = self.active_escalations.get(customer_id)
        if not record:
            print(f"[WARN] No active escalation found for customer {customer_id}")
            return False
        
        old_status = record.status
        record.status = status
        record.last_updated = datetime.now()
        
        # Log this status change as an interaction
        self.log_interaction(
            customer_id=customer_id,
            action_type="status_update",
            details={
                "old_status": old_status,
                "new_status": status,
                "resolution_notes": resolution_notes,
                "assigned_to": assigned_to
            }
        )
        
        if resolution_notes:
            record.resolution_notes = resolution_notes
        
        if assigned_to:
            record.assigned_to = assigned_to
        
        if status in ["resolved", "closed"]:
            record.resolved_at = datetime.now()
            
            # Archive to history
            self._archive_to_history(record)
            
            # Remove from active escalations
            del self.active_escalations[customer_id]
            
            print(f"[RESOLVED] Customer {customer_id} escalation resolved (was {old_status})")
        else:
            print(f"[UPDATE] Customer {customer_id} escalation: {old_status} → {status}")
        
        self._save_active_escalations()
        return True
    
    def log_interaction(
        self,
        customer_id: str,
        action_type: str,
        details: Optional[Dict[str, Any]] = None,
        performed_by: Optional[str] = None
    ) -> bool:
        """
        Log an interaction/action taken on an escalated customer.
        This prevents the next scan from redoing the same action.
        
        Args:
            customer_id: Customer ID
            action_type: Type of action (e.g., 'email_sent', 'call_made', 'discount_offered', 'status_update')
            details: Additional details about the action
            performed_by: Who performed the action (human or system)
            
        Returns:
            True if logged successfully
            
        Example:
            tracker.log_interaction(
                customer_id="C100123",
                action_type="email_sent",
                details={"subject": "Apology for delay", "template": "delay_apology"},
                performed_by="agent_sarah"
            )
        """
        record = self.active_escalations.get(customer_id)
        if not record:
            print(f"[WARN] No active escalation found for customer {customer_id}")
            return False
        
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "details": details or {},
            "performed_by": performed_by or "system"
        }
        
        record.interaction_history.append(interaction)
        record.last_updated = datetime.now()
        
        self._save_active_escalations()
        
        print(f"[LOG] Customer {customer_id}: {action_type} by {performed_by or 'system'}")
        return True
    
    def get_interaction_history(self, customer_id: str) -> List[Dict[str, Any]]:
        """
        Get all interactions for a customer's escalation.
        
        Args:
            customer_id: Customer ID
            
        Returns:
            List of interaction records
        """
        record = self.active_escalations.get(customer_id)
        if not record:
            return []
        
        return record.interaction_history
    
    def get_stale_escalations(self, days_threshold: int = 7) -> List[EscalationRecord]:
        """
        Get escalations that have been open too long.
        
        Args:
            days_threshold: Number of days to consider stale
            
        Returns:
            List of stale escalation records
        """
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        stale = []
        
        for record in self.active_escalations.values():
            if record.escalated_at < cutoff_date and record.status == "open":
                stale.append(record)
        
        return stale
    
    def should_skip_customer(self, customer_id: str) -> Dict[str, Any]:
        """
        Determine if customer should be skipped in proactive scan.
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Dictionary with skip decision and context
        """
        escalation_status = self.get_escalation_status(customer_id)
        
        if not escalation_status:
            return {
                "should_skip": False,
                "reason": None,
                "context": "No active escalation"
            }
        
        days_since = escalation_status["days_since_escalation"]
        status = escalation_status["status"]
        
        # Skip if escalation is still open or in progress
        if status in ["open", "in_progress"]:
            if days_since < 7:  # Within 7 days
                return {
                    "should_skip": True,
                    "reason": f"Active escalation ({status}) - being handled by human",
                    "context": f"Escalated {days_since} days ago: {escalation_status['reason']}",
                    "escalation_id": escalation_status["escalation_id"],
                    "assigned_to": escalation_status.get("assigned_to")
                }
            else:  # Stale escalation (>7 days)
                return {
                    "should_skip": False,
                    "reason": "Stale escalation - may need follow-up",
                    "context": f"Escalation {days_since} days old, consider re-escalating",
                    "escalation_id": escalation_status["escalation_id"],
                    "is_stale": True
                }
        
        return {
            "should_skip": False,
            "reason": None,
            "context": "Previous escalation resolved, can process normally"
        }
    
    def get_customer_escalation_history(self, customer_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get escalation history for a customer.
        
        Args:
            customer_id: Customer ID
            limit: Maximum number of records to return
            
        Returns:
            List of historical escalation records
        """
        history = []
        
        if not self.history_file.exists():
            return history
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        if data.get('customer_id') == customer_id:
                            history.append(data)
        except Exception as e:
            print(f"[ERROR] Error reading escalation history: {e}")
        
        # Sort by escalated_at (most recent first) and limit
        history.sort(key=lambda x: x['escalated_at'], reverse=True)
        return history[:limit]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get escalation statistics.
        
        Returns:
            Statistics dictionary
        """
        active_count = len(self.active_escalations)
        
        # Count by status
        status_counts = {}
        priority_counts = {}
        
        for record in self.active_escalations.values():
            status_counts[record.status] = status_counts.get(record.status, 0) + 1
            priority_counts[record.priority] = priority_counts.get(record.priority, 0) + 1
        
        # Count stale escalations
        stale_count = len(self.get_stale_escalations())
        
        # Count total historical escalations
        total_historical = 0
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                total_historical = sum(1 for line in f if line.strip())
        
        return {
            "active_escalations": active_count,
            "status_breakdown": status_counts,
            "priority_breakdown": priority_counts,
            "stale_escalations": stale_count,
            "total_historical_escalations": total_historical,
            "total_all_time": active_count + total_historical
        }
    
    def clean_old_escalations(self, days_threshold: int = 30):
        """
        Auto-close escalations that are very old.
        
        Args:
            days_threshold: Days after which to auto-close
        """
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        closed_count = 0
        
        customers_to_remove = []
        for customer_id, record in self.active_escalations.items():
            if record.escalated_at < cutoff_date:
                record.status = "closed"
                record.resolution_notes = f"Auto-closed after {days_threshold} days"
                record.resolved_at = datetime.now()
                
                self._archive_to_history(record)
                customers_to_remove.append(customer_id)
                closed_count += 1
        
        # Remove from active
        for customer_id in customers_to_remove:
            del self.active_escalations[customer_id]
        
        if closed_count > 0:
            self._save_active_escalations()
            print(f"[CLEANUP] Auto-closed {closed_count} old escalations")
        
        return closed_count


# Factory function
def create_escalation_tracker() -> EscalationTracker:
    """Create an EscalationTracker instance."""
    return EscalationTracker()
