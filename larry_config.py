"""
Larry Navigator - Centralized Configuration
All configurable constants in one place
"""

# --- Model Configuration ---
CLAUDE_MODEL = "claude-sonnet-4-20250514"
CLAUDE_MAX_TOKENS = 8192
CLAUDE_TEMPERATURE_DEFAULT = 0.2
CLAUDE_TEMPERATURE_PRECISE = 0.0  # For Cypher generation

# --- RAG Configuration ---
WEB_SEARCH_DEFAULT_RESULTS = 5
WEB_SEARCH_DATE_FILTER_YEARS = 3
NEO4J_DEFAULT_DATABASE = "neo4j"

# --- UI Configuration ---
CLARITY_BASE_SCORE = 20
CLARITY_INCREMENT_PER_MESSAGE = 5
CLARITY_READY_THRESHOLD = 70

# --- Memory Configuration ---
CONVERSATION_MEMORY_WINDOW = 5  # Number of exchanges to remember
