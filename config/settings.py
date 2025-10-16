"""
Configuration settings for AgentMAX CX Platform.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "AgentMAX-CX")

# LLM Configuration
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")  # Changed to gpt-4o-mini (more accessible and faster)
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2000"))

# Agent Configuration
CONTEXT_AGENT_MODEL = os.getenv("CONTEXT_AGENT_MODEL", "gpt-4o-mini")
PATTERN_AGENT_MODEL = os.getenv("PATTERN_AGENT_MODEL", "gpt-4o-mini")
DECISION_AGENT_MODEL = os.getenv("DECISION_AGENT_MODEL", "gpt-4o-mini")
EMPATHY_AGENT_MODEL = os.getenv("EMPATHY_AGENT_MODEL", "gpt-4o-mini")

# Memory Configuration
MEMORY_MAX_HISTORY = int(os.getenv("MEMORY_MAX_HISTORY", "50"))
MEMORY_RELEVANCE_THRESHOLD = float(os.getenv("MEMORY_RELEVANCE_THRESHOLD", "0.7"))

# Workflow Configuration
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "10"))
TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "60"))

# Risk Thresholds
HIGH_VALUE_CUSTOMER_THRESHOLD = 5000.0
CHURN_RISK_THRESHOLD = 0.7
ESCALATION_URGENCY_THRESHOLD = 4  # 1-5 scale

# Priority Mapping
PRIORITY_MAPPING = {
    "VIP": "critical",
    "Loyal": "high",
    "Regular": "medium",
    "Occasional": "low"
}

# Dataset Configuration
DATASET_PATH = DATA_DIR / "AgentMAX_CX_dataset_cleaned.xlsx"
