"""
AgentMAX CX Platform Package
"""
__version__ = "1.0.0"
__author__ = "Team ProCX"
__description__ = "Empathic AI-Driven Customer Experience Platform"

from .agents import (
    ContextAgent,
    PatternAgent,
    DecisionAgent,
    EmpathyAgent
)

from .workflows import (
    create_cx_workflow,
    create_cx_workflow_with_routing,
    run_workflow
)

from .models import (
    Customer,
    CustomerEvent,
    AgentState,
    EventType,
    SentimentType
)

from .utils import (
    EventSimulator,
    MemoryHandler,
    DataAnalytics,
    ProactiveMonitor,
    ProactiveRunner
)

__all__ = [
    # Agents
    "ContextAgent",
    "PatternAgent",
    "DecisionAgent",
    "EmpathyAgent",
    # Workflows
    "create_cx_workflow",
    "create_cx_workflow_with_routing",
    "run_workflow",
    # Models
    "Customer",
    "CustomerEvent",
    "AgentState",
    "EventType",
    "SentimentType",
    # Utils
    "EventSimulator",
    "MemoryHandler",
    "DataAnalytics",
    "ProactiveMonitor",
    "ProactiveRunner"
]
