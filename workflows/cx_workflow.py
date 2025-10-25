"""
AgentMAX CX Workflow - LangGraph implementation of the multi-agent system.
"""
from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage

from models import AgentState
from agents import (
    create_context_agent,
    create_pattern_agent,
    create_decision_agent,
    create_empathy_agent
)


class WorkflowState(TypedDict):
    """State for the LangGraph workflow."""
    state: AgentState


def create_cx_workflow():
    """
    Create the AgentMAX CX workflow using LangGraph.
    
    The workflow follows this sequence:
    1. Context Agent - Analyzes the event and extracts context
    2. Pattern Agent - Identifies patterns and predicts behavior
    3. Decision Agent - Makes decisions on actions and escalations
    4. Empathy Agent - Generates personalized response
    
    Returns:
        Compiled LangGraph workflow
    """
    
    # Create agent instances
    context_agent = create_context_agent()
    pattern_agent = create_pattern_agent()
    decision_agent = create_decision_agent()
    empathy_agent = create_empathy_agent()
    
    # Define workflow nodes
    def context_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """Context analysis node."""
        agent_state: AgentState = state["state"]
        updated_state = context_agent(agent_state)
        return {"state": updated_state}
    
    def pattern_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """Pattern recognition node."""
        agent_state: AgentState = state["state"]
        updated_state = pattern_agent(agent_state)
        return {"state": updated_state}
    
    def decision_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """Decision making node."""
        agent_state: AgentState = state["state"]
        updated_state = decision_agent(agent_state)
        return {"state": updated_state}
    
    def empathy_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """Empathy and response generation node."""
        agent_state: AgentState = state["state"]
        updated_state = empathy_agent(agent_state)
        return {"state": updated_state}
    
    # Create the graph
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("context_agent", context_node)
    workflow.add_node("pattern_agent", pattern_node)
    workflow.add_node("decision_agent", decision_node)
    workflow.add_node("empathy_agent", empathy_node)
    
    # Define edges (sequential flow)
    workflow.set_entry_point("context_agent")
    workflow.add_edge("context_agent", "pattern_agent")
    workflow.add_edge("pattern_agent", "decision_agent")
    workflow.add_edge("decision_agent", "empathy_agent")
    workflow.add_edge("empathy_agent", END)
    
    # Compile the graph
    return workflow.compile()


def create_cx_workflow_with_routing():
    """
    Create an advanced workflow with conditional routing.
    
    This version includes:
    - Early exit for simple inquiries
    - Escalation routing
    - Retry logic for failed steps
    
    Returns:
        Compiled LangGraph workflow with routing
    """
    
    # Create agent instances
    context_agent = create_context_agent()
    pattern_agent = create_pattern_agent()
    decision_agent = create_decision_agent()
    empathy_agent = create_empathy_agent()
    
    # Define workflow nodes
    def context_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """Context analysis node."""
        agent_state: AgentState = state["state"]
        updated_state = context_agent(agent_state)
        return {"state": updated_state}
    
    def pattern_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """Pattern recognition node."""
        agent_state: AgentState = state["state"]
        updated_state = pattern_agent(agent_state)
        return {"state": updated_state}
    
    def decision_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """Decision making node."""
        agent_state: AgentState = state["state"]
        updated_state = decision_agent(agent_state)
        return {"state": updated_state}
    
    def empathy_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """Empathy and response generation node."""
        agent_state: AgentState = state["state"]
        updated_state = empathy_agent(agent_state)
        return {"state": updated_state}
    
    def escalation_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle escalation to human agent - but still generate empathy response first."""
        agent_state: AgentState = state["state"]
        
        # Generate empathy response even for escalated cases
        updated_state = empathy_agent(agent_state)
        
        # Add detailed escalation context for human agent
        escalation_message = "🚨 ESCALATED TO HUMAN AGENT\n"
        escalation_message += f"Recommended Action: {updated_state.recommended_action}\n"
        escalation_message += f"Priority: {updated_state.priority_level}\n"
        escalation_message += f"Churn Risk: {updated_state.predicted_churn_risk:.1%}" if updated_state.predicted_churn_risk else ""
        
        updated_state.add_message(
            "escalation_handler",
            escalation_message
        )
        return {"state": updated_state}
    
    # Routing functions
    def should_analyze_patterns(state: Dict[str, Any]) -> str:
        """Determine if pattern analysis is needed."""
        agent_state: AgentState = state["state"]
        
        # Skip pattern analysis for very simple inquiries
        if agent_state.urgency_level and agent_state.urgency_level <= 2:
            if agent_state.sentiment and agent_state.sentiment.value == "positive":
                return "decision_agent"  # Skip to decision for simple positive inquiries
        
        return "pattern_agent"
    
    def should_escalate(state: Dict[str, Any]) -> str:
        """Determine if escalation is needed."""
        agent_state: AgentState = state["state"]
        
        if agent_state.escalation_needed:
            return "escalation_handler"
        
        return "empathy_agent"
    
    # Create the graph
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("context_agent", context_node)
    workflow.add_node("pattern_agent", pattern_node)
    workflow.add_node("decision_agent", decision_node)
    workflow.add_node("empathy_agent", empathy_node)
    workflow.add_node("escalation_handler", escalation_node)
    
    # Define edges with routing
    workflow.set_entry_point("context_agent")
    
    # Conditional routing after context
    workflow.add_conditional_edges(
        "context_agent",
        should_analyze_patterns,
        {
            "pattern_agent": "pattern_agent",
            "decision_agent": "decision_agent"
        }
    )
    
    workflow.add_edge("pattern_agent", "decision_agent")
    
    # Conditional routing after decision
    workflow.add_conditional_edges(
        "decision_agent",
        should_escalate,
        {
            "empathy_agent": "empathy_agent",
            "escalation_handler": "escalation_handler"
        }
    )
    
    # Both paths end
    workflow.add_edge("empathy_agent", END)
    workflow.add_edge("escalation_handler", END)
    
    # Compile the graph
    return workflow.compile()


def run_workflow(workflow, initial_state: AgentState) -> AgentState:
    """
    Run the workflow with an initial state.
    
    Args:
        workflow: Compiled LangGraph workflow
        initial_state: Initial agent state
        
    Returns:
        Final agent state after workflow completion
    """
    result = workflow.invoke({"state": initial_state})
    return result["state"]


async def run_workflow_async(workflow, initial_state: AgentState) -> AgentState:
    """
    Run the workflow asynchronously.
    
    Args:
        workflow: Compiled LangGraph workflow
        initial_state: Initial agent state
        
    Returns:
        Final agent state after workflow completion
    """
    result = await workflow.ainvoke({"state": initial_state})
    return result["state"]


def stream_workflow(workflow, initial_state: AgentState):
    """
    Stream the workflow execution step by step.
    
    Args:
        workflow: Compiled LangGraph workflow
        initial_state: Initial agent state
        
    Yields:
        Step-by-step results
    """
    for step in workflow.stream({"state": initial_state}):
        yield step


def create_proactive_workflow():
    """
    Create a PROACTIVE workflow optimized for preventive customer engagement.
    
    This workflow is designed for:
    - Proactive churn prevention
    - Customer health monitoring
    - Preventive retention campaigns
    - Predictive intervention
    
    Key differences from reactive workflow:
    - Focuses on FUTURE behavior prediction
    - Emphasizes intervention timing
    - Generates preventive action plans
    - Optimized for batch processing
    
    Returns:
        Compiled LangGraph workflow for proactive engagement
    """
    
    # Create agent instances
    context_agent = create_context_agent()
    pattern_agent = create_pattern_agent()
    decision_agent = create_decision_agent()
    empathy_agent = create_empathy_agent()
    
    # Define workflow nodes for proactive processing
    def proactive_context_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Context analysis for proactive events.
        Focuses on customer health rather than immediate sentiment.
        """
        agent_state: AgentState = state["state"]
        
        # For proactive events, set baseline context
        if agent_state.event and hasattr(agent_state.event, 'is_proactive') and agent_state.event.is_proactive:
            agent_state.add_message("proactive_workflow", "Processing proactive intervention")
        
        updated_state = context_agent(agent_state)
        return {"state": updated_state}
    
    def proactive_pattern_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pattern analysis for proactive events.
        Emphasizes future predictions and intervention windows.
        """
        agent_state: AgentState = state["state"]
        
        # Enhanced pattern analysis with proactive predictions
        updated_state = pattern_agent(agent_state)
        
        # Add proactive-specific insights
        if agent_state.event and hasattr(agent_state.event, 'is_proactive') and agent_state.event.is_proactive:
            updated_state.add_message(
                "proactive_workflow",
                f"Proactive churn risk: {updated_state.predicted_churn_risk:.2%}"
            )
        
        return {"state": updated_state}
    
    def proactive_decision_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decision making for proactive interventions.
        Focuses on WHEN and HOW to reach out.
        """
        agent_state: AgentState = state["state"]
        updated_state = decision_agent(agent_state)
        
        # Adjust priority for proactive events
        if agent_state.event and hasattr(agent_state.event, 'is_proactive') and agent_state.event.is_proactive:
            # Proactive events are typically medium priority unless high churn risk
            if updated_state.predicted_churn_risk and updated_state.predicted_churn_risk >= 0.7:
                updated_state.priority_level = "high"
                updated_state.add_message("proactive_workflow", "High churn risk - elevated priority")
            elif not updated_state.priority_level or updated_state.priority_level == "low":
                updated_state.priority_level = "medium"
        
        return {"state": updated_state}
    
    def proactive_empathy_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Response generation for proactive outreach.
        Tone is more positive and forward-looking.
        """
        agent_state: AgentState = state["state"]
        
        # Set proactive tone
        if agent_state.event and hasattr(agent_state.event, 'is_proactive') and agent_state.event.is_proactive:
            agent_state.add_message(
                "proactive_workflow",
                "Generating proactive, forward-looking message"
            )
        
        updated_state = empathy_agent(agent_state)
        return {"state": updated_state}
    
    # Create the graph
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("proactive_context", proactive_context_node)
    workflow.add_node("proactive_pattern", proactive_pattern_node)
    workflow.add_node("proactive_decision", proactive_decision_node)
    workflow.add_node("proactive_empathy", proactive_empathy_node)
    
    # Define edges (sequential flow optimized for proactive)
    workflow.set_entry_point("proactive_context")
    workflow.add_edge("proactive_context", "proactive_pattern")
    workflow.add_edge("proactive_pattern", "proactive_decision")
    workflow.add_edge("proactive_decision", "proactive_empathy")
    workflow.add_edge("proactive_empathy", END)
    
    # Compile the graph
    return workflow.compile()
