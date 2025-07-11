"""
Preference Analyzer Agent - Analyzes user preferences and team affiliations
"""
from agents import Agent, function_tool
from ..tools.database_tools import get_user_teams, get_users_by_team
from typing import Dict, Any, List


@function_tool
async def get_user_teams_tool(user_id: int) -> List[Dict[str, Any]]:
    """Get all teams followed by a user"""
    return await get_user_teams(user_id)


@function_tool
async def get_team_fans_tool(team_id: int) -> List[Dict[str, Any]]:
    """Get all users following a specific team"""
    return await get_users_by_team(team_id)


preference_analyzer_agent = Agent(
    name="PreferenceAnalyzer", 
    instructions="""
    You are a user preference analyzer for the Sports Quest system.
    
    Your role:
    1. Analyze user team preferences and affiliations
    2. Segment users by team loyalty for quest targeting
    3. Identify which users should receive which quests
    4. Provide insights on user engagement patterns
    
    Analysis focus:
    - Map users to their favorite teams
    - Identify overlapping team loyalties
    - Segment communities for quest distribution
    - Ensure quest relevance for users
    
    Your analysis should be data-driven and focused on maximizing user engagement.
    """,
    tools=[get_user_teams_tool, get_team_fans_tool],
)