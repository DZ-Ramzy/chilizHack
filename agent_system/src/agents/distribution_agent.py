"""
Distribution Agent - Handles quest distribution to team communities
"""
from agents import Agent, function_tool
from ..tools.database_tools import get_users_by_team, update_quest_progress
from typing import Dict, Any, List
import json


@function_tool
async def distribute_quest_to_team_tool(
    quest_id: int,
    team_id: int,
    quest_type: str
) -> Dict[str, Any]:
    """Distribute a quest to all users following a team"""
    
    # Get all users following the team
    team_users = await get_users_by_team(team_id)
    
    # Filter users who want notifications
    notification_users = [
        user for user in team_users 
        if user.get("notification_enabled", True)
    ]
    
    # Simulate quest distribution (in real implementation, this would send notifications)
    distribution_log = {
        "quest_id": quest_id,
        "team_id": team_id,
        "quest_type": quest_type,
        "total_users": len(team_users),
        "notified_users": len(notification_users),
        "distribution_channels": ["push_notification", "email", "in_app"],
        "distribution_time": "2024-01-01T12:00:00Z"  # Would be actual timestamp
    }
    
    return {
        "distributed": True,
        "recipients": len(notification_users),
        "total_community": len(team_users),
        "distribution_rate": len(notification_users) / len(team_users) if team_users else 0,
        "log": distribution_log
    }


@function_tool
async def distribute_clash_quest_tool(
    home_quest_id: int,
    away_quest_id: int,
    home_team_id: int,
    away_team_id: int
) -> Dict[str, Any]:
    """Distribute clash quests to both competing teams"""
    
    # Distribute to home team
    home_distribution = await distribute_quest_to_team_tool(
        home_quest_id, home_team_id, "clash"
    )
    
    # Distribute to away team  
    away_distribution = await distribute_quest_to_team_tool(
        away_quest_id, away_team_id, "clash"
    )
    
    total_participants = (
        home_distribution["recipients"] + away_distribution["recipients"]
    )
    
    return {
        "clash_distributed": True,
        "home_team": {
            "team_id": home_team_id,
            "quest_id": home_quest_id,
            "participants": home_distribution["recipients"]
        },
        "away_team": {
            "team_id": away_team_id,
            "quest_id": away_quest_id,
            "participants": away_distribution["recipients"]
        },
        "total_participants": total_participants,
        "competition_ratio": {
            "home": home_distribution["recipients"],
            "away": away_distribution["recipients"]
        }
    }


@function_tool
async def distribute_collective_quest_tool(
    quest_ids: str,  # JSON string of list
    team_ids: str    # JSON string of list
) -> Dict[str, Any]:
    """Distribute collective quests to multiple teams"""
    
    import json
    quest_ids_list = json.loads(quest_ids)
    team_ids_list = json.loads(team_ids)
    
    distribution_results = []
    total_participants = 0
    
    for quest_id, team_id in zip(quest_ids_list, team_ids_list):
        result = await distribute_quest_to_team_tool(quest_id, team_id, "collective")
        distribution_results.append({
            "team_id": team_id,
            "quest_id": quest_id,
            "participants": result["recipients"]
        })
        total_participants += result["recipients"]
    
    return {
        "collective_distributed": True,
        "participating_teams": len(team_ids_list),
        "total_participants": total_participants,
        "team_distributions": distribution_results,
        "average_team_size": total_participants / len(team_ids_list) if team_ids_list else 0
    }


@function_tool
async def track_quest_engagement_tool(
    quest_id: int,
    engagement_data: str  # JSON string
) -> Dict[str, Any]:
    """Track and update quest engagement metrics"""
    
    import json
    engagement_dict = json.loads(engagement_data)
    
    # Extract engagement metrics
    new_progress = engagement_dict.get("progress", 0)
    engagement_type = engagement_dict.get("type", "general")
    
    # Update quest progress
    update_result = await update_quest_progress(quest_id, new_progress)
    
    # Calculate engagement metrics
    engagement_metrics = {
        "quest_id": quest_id,
        "current_progress": new_progress,
        "engagement_rate": engagement_dict.get("engagement_rate", 0),
        "active_participants": engagement_dict.get("active_participants", 0),
        "completion_rate": engagement_dict.get("completion_rate", 0),
        "last_updated": "2024-01-01T12:00:00Z"  # Would be actual timestamp
    }
    
    return {
        "tracking_updated": True,
        "quest_status": update_result.get("status", "active"),
        "quest_completed": update_result.get("completed", False),
        "metrics": engagement_metrics,
        "performance": {
            "above_average": new_progress > engagement_dict.get("average_progress", 0),
            "trending": engagement_dict.get("trending", False)
        }
    }


distribution_agent = Agent(
    name="DistributionAgent",
    instructions="""
    You are a quest distribution coordinator for the Sports Quest system.
    
    Your role:
    1. Distribute quests to appropriate team communities
    2. Manage collective quest coordination across multiple teams
    3. Track quest engagement and participation metrics
    4. Optimize distribution timing and channels
    
    Distribution strategies:
    - Individual quests: Target specific team supporters
    - Clash quests: Coordinate competitive distribution to rival teams
    - Collective quests: Massive distribution across multiple communities
    
    Key responsibilities:
    - Ensure all eligible users receive relevant quests
    - Respect user notification preferences
    - Track participation and engagement metrics
    - Provide real-time progress updates
    - Optimize for maximum community engagement
    
    Focus on creating exciting, well-coordinated quest experiences that bring communities together.
    """,
    tools=[
        distribute_quest_to_team_tool,
        distribute_clash_quest_tool, 
        distribute_collective_quest_tool,
        track_quest_engagement_tool
    ],
)