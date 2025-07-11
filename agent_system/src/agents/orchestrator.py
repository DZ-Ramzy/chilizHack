"""
Orchestrator Agent - Main coordinator for the Sports Quest system
Implements the workflow from the PRD using OpenAI Agents handoffs
"""
from agents import Agent, handoff, function_tool
from ..tools.database_tools import get_active_events, check_team_exists, get_team_community_size
from .preference_analyzer import preference_analyzer_agent
from .quest_generator import quest_generator_agent
from .validation_agents import content_validator_agent, image_validator_agent, preference_validator_agent
from .distribution_agent import distribution_agent
from typing import Dict, Any, List
import json


@function_tool
async def get_sports_events_tool() -> List[Dict[str, Any]]:
    """Get all active sports events"""
    return await get_active_events()


@function_tool
async def check_teams_existence_tool(home_team_name: str, away_team_name: str) -> Dict[str, Any]:
    """Check existence of both teams and determine quest strategy"""
    
    home_team_exists = await check_team_exists(home_team_name)
    away_team_exists = await check_team_exists(away_team_name)
    
    strategy = {
        "home_team": home_team_exists,
        "away_team": away_team_exists,
        "quest_strategy": "none"
    }
    
    # Determine quest creation strategy based on team existence
    if home_team_exists.get("exists") and away_team_exists.get("exists"):
        strategy["quest_strategy"] = "both_teams"  # Individual + Clash quests
    elif home_team_exists.get("exists"):
        strategy["quest_strategy"] = "home_only"   # Only home team quest
    elif away_team_exists.get("exists"):
        strategy["quest_strategy"] = "away_only"   # Only away team quest
    else:
        strategy["quest_strategy"] = "skip"       # Skip event
    
    return strategy


@function_tool
def analyze_event_workflow_tool(event_data: str) -> Dict[str, str]:
    """Analyze event and determine workflow path"""
    
    import json
    event_dict = json.loads(event_data)
    
    home_team = event_dict.get("home_team", {})
    away_team = event_dict.get("away_team", {})
    
    workflow_decision = {
        "event_id": str(event_dict.get("event_id")),
        "home_team_id": str(home_team.get("id")),
        "away_team_id": str(away_team.get("id")),
        "home_team_name": home_team.get("name", ""),
        "away_team_name": away_team.get("name", ""),
        "next_action": "check_teams",
        "workflow_type": "standard"
    }
    
    return workflow_decision


orchestrator_agent = Agent(
    name="SportsQuestOrchestrator",
    instructions="""
    You are the main orchestrator for the Sports Quest AI system.
    
    Your primary role is to coordinate the entire quest generation workflow:
    
    WORKFLOW PROCESS:
    1. Receive sports event triggers
    2. Use integrated team existence checking to verify teams
    3. Based on team existence, determine quest strategy:
       - Both teams exist → Individual + Clash quests
       - One team exists → Individual quest only  
       - No teams exist → Skip event
    4. Hand off to PreferenceAnalyzer to segment users
    5. Hand off to QuestGenerator to create appropriate quests
    6. Hand off to validation agents (Content, Image, Preference) for parallel validation
    7. If validation passes → Hand off to DistributionAgent
    8. If validation fails → Return to QuestGenerator for improvements
    
    HANDOFF STRATEGY:
    - Start with integrated team verification using check_teams_existence_tool
    - Use preference_analyzer_agent for user segmentation
    - Route to quest_generator_agent based on team availability
    - Coordinate parallel validation through validation agents
    - Complete workflow with distribution_agent
    
    DECISION LOGIC:
    - Event: "PSG vs Real Madrid"
    - If both PSG and Real Madrid exist → Create individual PSG quest + individual Real quest + clash quest
    - If only PSG exists → Create only PSG individual quest
    - If neither exists → Skip event
    
    You maintain context throughout the workflow and ensure all steps complete successfully.
    Provide clear status updates and error handling at each step.
    """,
    tools=[get_sports_events_tool, analyze_event_workflow_tool, check_teams_existence_tool],
    handoffs=[
        handoff(preference_analyzer_agent), 
        handoff(quest_generator_agent),
        handoff(content_validator_agent),
        handoff(image_validator_agent),
        handoff(preference_validator_agent),
        handoff(distribution_agent)
    ],
)