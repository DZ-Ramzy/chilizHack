"""
AI Agents for Sports Quest System - New simple architecture
"""

from .individual_quest_generator import individual_quest_agent
from .clash_quest_generator import clash_quest_agent
from .collective_quest_generator import community_quest_agent

__all__ = [
    "individual_quest_agent",
    "clash_quest_agent",
    "community_quest_agent"
]