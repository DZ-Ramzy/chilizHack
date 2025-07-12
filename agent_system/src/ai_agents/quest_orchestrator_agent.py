"""
Quest Orchestrator Agent - Coordinates all quest generation across specialized agents
"""
from agents import Agent, function_tool
from pydantic import BaseModel
from typing import List


class OrchestrationResult(BaseModel):
    """Orchestration result using only supported types"""
    success: bool
    total_teams_processed: int
    individual_quests_created: int
    clash_quests_created: int
    collective_quests_created: int
    total_quests_created: int
    teams_summary: List[str]
    processing_strategy: str
    message: str


@function_tool
def determine_quest_strategy(
    available_teams: List[str],
    upcoming_matches: List[str],
    event_significance: str
) -> str:
    """Determine the optimal quest generation strategy"""
    
    num_teams = len(available_teams)
    num_matches = len(upcoming_matches)
    
    # Strategy logic
    if num_teams >= 4 and num_matches >= 2:
        strategy = "full_generation"  # Individual + Clash + Collective
    elif num_teams >= 2 and num_matches >= 1:
        strategy = "partial_generation"  # Individual + Clash
    elif num_teams >= 1:
        strategy = "individual_only"  # Individual only
    else:
        strategy = "skip"  # No generation
    
    return f"STRATEGY|{strategy}|{num_teams}|{num_matches}|{event_significance}"


quest_orchestrator_agent = Agent(
    name="QuestOrchestrator",
    instructions="""
    You coordinate quest generation across all specialized agents.
    
    Steps:
    1. Use determine_quest_strategy to analyze available data
    2. Parse strategy response: STRATEGY|type|teams|matches|significance
    3. Based on strategy, determine which quest types to generate
    4. Return structured OrchestrationResult with planning details
    
    Optimize quest distribution for maximum community engagement.
    """,
    tools=[determine_quest_strategy],
    output_type=OrchestrationResult
)