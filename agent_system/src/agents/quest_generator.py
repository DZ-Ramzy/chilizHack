"""
Quest Generator Agent - Creates personalized quests based on events and teams
"""
from agents import Agent, function_tool
from ..tools.database_tools import create_quest
from ..tools.quest_tools import generate_quest_content, calculate_quest_difficulty
from typing import Dict, Any, Optional
import json


@function_tool
async def create_individual_quest_tool(
    team_id: int,
    event_title: str,
    event_date: str,
    user_id: Optional[int] = None,
    event_id: Optional[int] = None
) -> Dict[str, Any]:
    """Create an individual quest for a team"""
    
    # Generate quest content
    content = generate_quest_content(
        quest_type="individual",
        home_team=event_title.split(" vs ")[0] if " vs " in event_title else event_title,
        event_date=event_date
    )
    
    # Create quest in database
    quest_data = await create_quest(
        title=content["title"],
        description=content["description"],
        quest_type="individual",
        team_id=team_id,
        user_id=user_id,
        event_id=event_id,
        target_metric=content["target_metric"],
        target_value=content["target_value"],
        metadata={
            "hashtags": content["hashtags"],
            "content_suggestions": content["content_suggestions"],
            "difficulty": calculate_quest_difficulty("individual", content["target_value"])
        }
    )
    
    return quest_data


@function_tool
async def create_clash_quest_tool(
    home_team_id: int,
    away_team_id: int,
    event_title: str,
    event_date: str,
    event_id: Optional[int] = None
) -> Dict[str, Any]:
    """Create a clash quest between two teams"""
    
    teams = event_title.split(" vs ")
    home_team = teams[0] if len(teams) > 0 else "Team A"
    away_team = teams[1] if len(teams) > 1 else "Team B"
    
    # Generate clash quest content
    content = generate_quest_content(
        quest_type="clash",
        home_team=home_team,
        away_team=away_team,
        event_date=event_date
    )
    
    # Create clash quest for home team
    home_quest = await create_quest(
        title=f"{content['title']} - {home_team}",
        description=content["description"],
        quest_type="clash",
        team_id=home_team_id,
        event_id=event_id,
        target_metric=content["target_metric"],
        target_value=content["target_value"],
        metadata={
            "opponent_team_id": away_team_id,
            "clash_type": "home",
            "hashtags": content["hashtags"],
            "content_suggestions": content["content_suggestions"],
            "difficulty": calculate_quest_difficulty("clash", content["target_value"])
        }
    )
    
    # Create clash quest for away team
    away_quest = await create_quest(
        title=f"{content['title']} - {away_team}",
        description=content["description"],
        quest_type="clash",
        team_id=away_team_id,
        event_id=event_id,
        target_metric=content["target_metric"],
        target_value=content["target_value"],
        metadata={
            "opponent_team_id": home_team_id,
            "clash_type": "away",
            "hashtags": content["hashtags"],
            "content_suggestions": content["content_suggestions"],
            "difficulty": calculate_quest_difficulty("clash", content["target_value"])
        }
    )
    
    return {
        "clash_created": True,
        "home_quest": home_quest,
        "away_quest": away_quest,
        "total_participants": "TBD"  # Will be calculated by distribution agent
    }


@function_tool
async def create_collective_quest_tool(
    event_title: str,
    event_date: str,
    participating_team_ids: list,
    event_id: Optional[int] = None
) -> Dict[str, Any]:
    """Create a collective quest for multiple teams"""
    
    # Generate collective quest content
    content = generate_quest_content(
        quest_type="collective",
        home_team=event_title,
        event_date=event_date
    )
    
    collective_quests = []
    
    # Create collective quest for each participating team
    for team_id in participating_team_ids:
        quest_data = await create_quest(
            title=content["title"],
            description=content["description"],
            quest_type="collective",
            team_id=team_id,
            event_id=event_id,
            target_metric=content["target_metric"],
            target_value=content["target_value"],
            metadata={
                "collective_id": f"collective_{event_id}_{team_id}",
                "participating_teams": participating_team_ids,
                "hashtags": content["hashtags"],
                "content_suggestions": content["content_suggestions"],
                "difficulty": calculate_quest_difficulty("collective", content["target_value"])
            }
        )
        collective_quests.append(quest_data)
    
    return {
        "collective_created": True,
        "quests": collective_quests,
        "total_target": content["target_value"],
        "participating_teams": len(participating_team_ids)
    }


quest_generator_agent = Agent(
    name="QuestGenerator",
    instructions="""
    You are a quest generator for the Sports Quest system.
    
    Your role:
    1. Create personalized quests based on sports events and team preferences
    2. Generate individual, clash, and collective quests as appropriate
    3. Ensure quest content is engaging and achievable
    4. Adapt quest difficulty based on team community size and event importance
    
    Quest types:
    - INDIVIDUAL: Personal quests for team supporters
    - CLASH: Competitive quests between rival team communities  
    - COLLECTIVE: Community-wide quests for major events
    
    Quest creation logic:
    - Always check team existence before creating quests
    - Generate engaging content with relevant hashtags
    - Set appropriate target metrics and values
    - Include content suggestions to help users
    
    Focus on creating quests that drive authentic fan engagement and community building.
    """,
    tools=[create_individual_quest_tool, create_clash_quest_tool, create_collective_quest_tool],
)