"""Application-wide constants and configuration values."""

from __future__ import annotations

# Bradley-Terry model parameters
RANDOM_COMPARISON_PROBABILITY = 0.33  # Probability of random vs optimal comparison
RATING_SCALE_MAX = 10.0  # Maximum rating value (0-10 scale)
RATING_SCALE_MIN = 0.0  # Minimum rating value

# Pagination defaults
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 1000

# Item limits
MIN_ITEMS_FOR_RANKING = 2  # Minimum items needed for Bradley-Terry model
MAX_ITEMS_PER_RANKING = 10000  # Maximum items per ranking to prevent abuse

# API timeouts (in seconds)
EXTERNAL_API_CONNECT_TIMEOUT = 3.05
EXTERNAL_API_READ_TIMEOUT = 10.0

# Password requirements
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128

# Comparison limits
MAX_COMPARISON_COUNT_PER_ITEM_PAIR = 100  # Prevent spam comparisons

# Cache TTL (in seconds)
MODEL_CACHE_TTL = 300  # Cache Bradley-Terry model for 5 minutes
RANKING_CACHE_TTL = 60  # Cache ranking data for 1 minute

# Logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

__all__ = [
    "RANDOM_COMPARISON_PROBABILITY",
    "RATING_SCALE_MAX",
    "RATING_SCALE_MIN",
    "DEFAULT_PAGE_SIZE",
    "MAX_PAGE_SIZE",
    "MIN_ITEMS_FOR_RANKING",
    "MAX_ITEMS_PER_RANKING",
    "EXTERNAL_API_CONNECT_TIMEOUT",
    "EXTERNAL_API_READ_TIMEOUT",
    "MIN_PASSWORD_LENGTH",
    "MAX_PASSWORD_LENGTH",
    "MAX_COMPARISON_COUNT_PER_ITEM_PAIR",
    "MODEL_CACHE_TTL",
    "RANKING_CACHE_TTL",
    "LOG_FORMAT",
    "LOG_DATE_FORMAT",
]
