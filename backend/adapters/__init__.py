"""Adapters package."""

from adapters.base import BaseAdapter
from adapters.cursor_adapter import CursorAdapter
from adapters.antigravity_adapter import AntigravityAdapter
from adapters.copilot_adapter import CopilotAdapter
from adapters.gemini_adapter import GeminiAdapter
from adapters.openrouter_adapter import OpenRouterAdapter

__all__ = [
    "BaseAdapter",
    "CursorAdapter",
    "AntigravityAdapter",
    "CopilotAdapter",
    "GeminiAdapter",
    "OpenRouterAdapter",
]
