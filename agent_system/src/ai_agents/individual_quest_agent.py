"""
Individual Quest Agent - Creates personalized quests for team supporters
"""
from agents import Agent, function_tool
from pydantic import BaseModel
from typing import List
from ..tools.database_tools import create_quest


class IndividualQuestResult(BaseModel):
    """Simple result structure using only supported types"""
    success: bool
    team_name: str
    quest_id: int
    title: str
    description: str
    target_value: int
    difficulty: str
    hashtags: List[str]
    message: str


@function_tool
async def create_individual_quest_tool(
    team_id: int,
    team_name: str,
    quest_type: str
) -> str:
    """Create individual quest for a team"""
    
    # Quest configurations by type
    quest_configs = {
        "social": {
            "target": 5,
            "title": f"Support {team_name} on Social Media",
            "description": f"Share 5 posts supporting {team_name} on social media",
            "hashtags": [f"#{team_name}", "#Football", "#Support"]
        },
        "prediction": {
            "target": 3,
            "title": f"Predict {team_name} Match Results",
            "description": f"Make 3 accurate predictions for {team_name} upcoming matches",
            "hashtags": [f"#{team_name}Predictions", "#Football", "#MatchDay"]
        },
        "content": {
            "target": 2,
            "title": f"Create Content for {team_name}",
            "description": f"Create 2 pieces of original content supporting {team_name}",
            "hashtags": [f"#{team_name}Content", "#Football", "#Creativity"]
        }
    }
    
    config = quest_configs.get(quest_type, quest_configs["social"])
    
    # Create quest in database
    quest_id = await create_quest(
        title=config["title"],
        description=config["description"],
        quest_type="individual",
        team_id=team_id,
        target_metric=f"{quest_type}_posts",
        target_value=config["target"]
    )
    
    return f"SUCCESS|{quest_id}|{config['title']}|{config['description']}|{config['target']}|medium|{','.join(config['hashtags'])}"


individual_quest_agent = Agent(
    name="IndividualQuestAgent",
    instructions="""
    You create individual quests for football team supporters.
    
    Steps:
    1. Use create_individual_quest_tool with the provided team information
    2. Parse the tool response format: SUCCESS|quest_id|title|description|target|difficulty|hashtags
    3. Return a properly structured IndividualQuestResult
    
    Always create engaging, achievable quests that motivate team supporters.
    """,
    tools=[create_individual_quest_tool],
    output_type=IndividualQuestResult
)