"""
Collective Quest Agent - Creates community-wide quests that unite all fans
"""
from agents import Agent, function_tool
from pydantic import BaseModel
from typing import List
from ..tools.database_tools import create_quest


class CollectiveQuestResult(BaseModel):
    """Collective quest result using only supported types"""
    success: bool
    quest_title: str
    participating_teams: List[str]
    community_target: int
    individual_target_per_team: int
    unity_hashtag: str
    quest_ids: List[int]
    estimated_participants: int
    event_significance: str
    message: str


@function_tool
async def create_community_quest_tool(
    participating_team_ids: List[int],
    participating_team_names: List[str],
    event_title: str,
    event_significance: str
) -> str:
    """Create community-wide quest for all participating teams"""
    
    # Quest configuration based on significance
    significance_configs = {
        "regular": {
            "community_target": 1000,
            "title": "Weekly Football Community Challenge",
            "description": "Unite the football community in celebration"
        },
        "important": {
            "community_target": 5000,
            "title": "Big Match Community Rally",
            "description": "Show the power of football community spirit"
        },
        "final": {
            "community_target": 10000,
            "title": "Championship Final Community Celebration",
            "description": "Historic moment - unite all football fans"
        }
    }
    
    config = significance_configs.get(event_significance, significance_configs["regular"])
    individual_target = config["community_target"] // len(participating_team_names) if participating_team_names else 100
    
    unity_hashtag = "#FootballUnity2025"
    quest_ids = []
    
    # Create quest for each participating team
    for i, team_id in enumerate(participating_team_ids):
        team_name = participating_team_names[i] if i < len(participating_team_names) else f"Team{team_id}"
        
        quest_id = await create_quest(
            title=f"{config['title']} - {team_name}",
            description=f"{config['description']} | {team_name} contribution target: {individual_target}",
            quest_type="collective",
            team_id=team_id,
            target_metric="community_actions",
            target_value=individual_target
        )
        quest_ids.append(quest_id)
    
    estimated_participants = len(participating_team_names) * 200  # Rough estimate
    
    # Format response
    quest_ids_str = ",".join(map(str, quest_ids))
    teams_str = ",".join(participating_team_names)
    
    return f"SUCCESS|{config['title']}|{teams_str}|{config['community_target']}|{individual_target}|{unity_hashtag}|{quest_ids_str}|{estimated_participants}|{event_significance}"


collective_quest_agent = Agent(
    name="CollectiveQuestAgent",
    instructions="""
    You create community-wide collective quests that unite all football fans.
    
    Steps:
    1. Use create_community_quest_tool with team and event information
    2. Parse response: SUCCESS|title|teams|community_target|individual_target|hashtag|quest_ids|participants|significance
    3. Return structured CollectiveQuestResult
    
    Create unifying quests that bring the entire football community together.
    """,
    tools=[create_community_quest_tool],
    output_type=CollectiveQuestResult
)