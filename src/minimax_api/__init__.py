"""Python client for the Minimax (Saop) accounting REST API."""

from minimax_api._generated import models
from minimax_api.auth import Credentials, InMemoryTokenStore, Token, TokenStore
from minimax_api.budget import Budget, BudgetStore, InMemoryBudgetStore
from minimax_api.client import MinimaxClient
from minimax_api.envelope import MinimaxModel, SearchResult
from minimax_api.errors import (
    ConcurrencyError,
    MinimaxAuthError,
    MinimaxError,
    NotFoundError,
    RateBudgetExceeded,
    TransportError,
    ValidationError,
)
from minimax_api.region import RS, Region

__all__ = [
    "RS",
    "Budget",
    "BudgetStore",
    "ConcurrencyError",
    "Credentials",
    "InMemoryBudgetStore",
    "InMemoryTokenStore",
    "MinimaxAuthError",
    "MinimaxClient",
    "MinimaxError",
    "MinimaxModel",
    "NotFoundError",
    "RateBudgetExceeded",
    "Region",
    "SearchResult",
    "Token",
    "TokenStore",
    "TransportError",
    "ValidationError",
    "models",
]
