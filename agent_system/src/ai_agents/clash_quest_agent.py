"""
Clash Quest Agent - Creates competitive quests between rival team fanbases
"""
from agents import Agent, function_tool
from pydantic import BaseModel
from typing import List
from ..tools.database_tools import create_quest


class ClashQuestResult(BaseModel):
    """Clash quest result using only supported types"""
    success: bool
    home_team_name: str
    away_team_name: str
    home_quest_id: int
    away_quest_id: int
    battle_title: str
    rivalry_level: str
    target_per_team: int
    battle_hashtag: str
    estimated_participants: int
    message: str


@function_tool
async def create_clash_battle_tool(
    home_team_id: int,
    home_team_name: str,
    away_team_id: int,
    away_team_name: str,
    match_date: str
) -> str:
    """Create clash battle between two teams"""
    
    # Determine rivalry level
    legendary_rivalries = [
        ("Real Madrid", "Barcelona"),
        ("Manchester United", "Manchester City"),
        ("PSG", "Marseille")
    ]
    
    rivalry_level = "legendary" if (home_team_name, away_team_name) in legendary_rivalries or (away_team_name, home_team_name) in legendary_rivalries else "high"
    
    # Battle configuration
    target_per_team = 100 if rivalry_level == "legendary" else 50
    battle_hashtag = f"#{home_team_name}vs{away_team_name}Clash"
    battle_title = f"{home_team_name} vs {away_team_name} Fan Battle"
    
    # Create home team quest
    home_quest_id = await create_quest(
        title=f"{battle_title} - {home_team_name} Supporters",
        description=f"Support {home_team_name} in the epic battle against {away_team_name} fans! Target: {target_per_team} social interactions",
        quest_type="clash",
        team_id=home_team_id,
        target_metric="social_interactions",
        target_value=target_per_team
    )
    
    # Create away team quest
    away_quest_id = await create_quest(
        title=f"{battle_title} - {away_team_name} Supporters",
        description=f"Support {away_team_name} in the epic battle against {home_team_name} fans! Target: {target_per_team} social interactions",
        quest_type="clash",
        team_id=away_team_id,
        target_metric="social_interactions",
        target_value=target_per_team
    )
    
    estimated_participants = target_per_team * 4  # Rough estimate
    
    return f"SUCCESS|{home_quest_id}|{away_quest_id}|{battle_title}|{rivalry_level}|{target_per_team}|{battle_hashtag}|{estimated_participants}"


clash_quest_agent = Agent(
    name="ClashQuestAgent",
    instructions="""
    You create competitive clash quests between rival football team fanbases.
    
    Steps:
    1. Use create_clash_battle_tool with team information
    2. Parse response: SUCCESS|home_quest_id|away_quest_id|title|rivalry|target|hashtag|participants
    3. Return structured ClashQuestResult
    
    Create engaging battles that motivate both fanbases to compete fairly.
    """,
    tools=[create_clash_battle_tool],
    output_type=ClashQuestResult
)