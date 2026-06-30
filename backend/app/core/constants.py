"""
Framework-wide constants.
All magic numbers live here — never hardcode values elsewhere.
"""

# Recall testing
DEFAULT_RECALL_INTERVALS = [10, 50, 100, 250, 500, 1000, 2000]
MAX_RECALL_QUESTION_TOKENS = 512

# Scoring thresholds
DEFAULT_SCORE_THRESHOLD = 0.80          # minimum score to call a recall "correct"
EXACT_MATCH_THRESHOLD = 1.0
FUZZY_MATCH_THRESHOLD = 0.85
EMBEDDING_SIMILARITY_THRESHOLD = 0.80

# Conversation generation
INJECT_SLOT_MARKER = "[INJECT_SLOT_{n}]"
MAX_CONVERSATION_TURNS = 5000

# Metrics
FORGETTING_RATE_WINDOW = 50             # turns over which to compute Δ(accuracy)
LONG_TERM_THRESHOLD_TURNS = 500        # "long-term" recall = tested ≥ this many turns after injection

# Token estimation (rough ratio for non-API estimation)
CHARS_PER_TOKEN = 4

# Database
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 200

# API
API_V1_PREFIX = "/api/v1"
