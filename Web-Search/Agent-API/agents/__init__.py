"""
Agents module initialization
"""
from .enhanced_agent import EnhancedSearchAgent, create_enhanced_agent
from .search_tools import (
    SEARCH_TOOLS,
    web_search,
    news_search,
    smart_search,
    research_search,
)

__all__ = [
    "EnhancedSearchAgent",
    "create_enhanced_agent",
    "SEARCH_TOOLS",
    "web_search",
    "news_search",
    "smart_search",
    "research_search",
]