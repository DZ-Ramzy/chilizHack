"""
Workflow Engine - Orchestrates the Sports Quest AI workflow (Simplified Version)
"""
from typing import Dict, Any, List
from loguru import logger
import json
from ..tools.database_tools import get_active_events, check_team_exists
from ..tools.quest_tools import generate_quest_content


class SportsQuestWorkflow:
    """Main workflow coordinator for Sports Quest AI system"""
    
    def __init__(self):
        pass
        
    async def process_sports_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a sports event through the complete workflow
        
        Args:
            event_data: Sports event information
            
        Returns:
            Workflow result with quest creation status
        """
        
        try:
            logger.info(f"Starting workflow for event: {event_data.get('title', 'Unknown')}")
            
            home_team = event_data.get("home_team", "")
            away_team = event_data.get("away_team", "")
            
            # Step 1: Check team existence
            home_exists = await check_team_exists(home_team) if home_team else {"exists": False}
            away_exists = await check_team_exists(away_team) if away_team else {"exists": False}
            
            logger.info(f"Team check: {home_team}={home_exists.get('exists')}, {away_team}={away_exists.get('exists')}")
            
            # Step 2: Determine quest strategy
            quests_created = []
            
            if home_exists.get('exists') and away_exists.get('exists'):
                # Both teams exist - create individual + clash quests
                strategy = "both_teams"
                
                # Individual quest for home team
                home_quest = generate_quest_content(
                    quest_type="individual",
                    home_team=home_team,
                    event_date=str(event_data.get("event_date", ""))
                )
                quests_created.append({"type": "individual", "team": home_team, "quest": home_quest})
                
                # Individual quest for away team
                away_quest = generate_quest_content(
                    quest_type="individual", 
                    home_team=away_team,
                    event_date=str(event_data.get("event_date", ""))
                )
                quests_created.append({"type": "individual", "team": away_team, "quest": away_quest})
                
                # Clash quest
                clash_quest = generate_quest_content(
                    quest_type="clash",
                    home_team=home_team,
                    away_team=away_team,
                    event_date=str(event_data.get("event_date", ""))
                )
                quests_created.append({"type": "clash", "teams": f"{home_team} vs {away_team}", "quest": clash_quest})
                
            elif home_exists.get('exists'):
                # Only home team exists
                strategy = "home_only"
                home_quest = generate_quest_content(
                    quest_type="individual",
                    home_team=home_team,
                    event_date=str(event_data.get("event_date", ""))
                )
                quests_created.append({"type": "individual", "team": home_team, "quest": home_quest})
                
            elif away_exists.get('exists'):
                # Only away team exists
                strategy = "away_only"
                away_quest = generate_quest_content(
                    quest_type="individual",
                    home_team=away_team,
                    event_date=str(event_data.get("event_date", ""))
                )
                quests_created.append({"type": "individual", "team": away_team, "quest": away_quest})
                
            else:
                # No teams exist - skip
                strategy = "skip"
                logger.warning(f"No teams found for event {event_data.get('title')} - skipping")
            
            logger.info(f"Workflow completed successfully - Strategy: {strategy}, Quests: {len(quests_created)}")
            
            return {
                "success": True,
                "event_id": event_data.get("event_id"),
                "strategy": strategy,
                "teams_found": {
                    "home": home_exists.get('exists', False),
                    "away": away_exists.get('exists', False)
                },
                "quests_created": quests_created,
                "total_quests": len(quests_created),
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Workflow failed for event {event_data.get('title', 'Unknown')}: {e}")
            return {
                "success": False,
                "event_id": event_data.get("event_id"),
                "error": str(e),
                "status": "failed"
            }
    
    async def create_manual_quest(
        self, 
        quest_type: str, 
        team_name: str, 
        user_preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a manual quest for a specific team
        
        Args:
            quest_type: Type of quest (individual, collective)
            team_name: Target team name
            user_preferences: User preferences for personalization
            
        Returns:
            Quest creation result
        """
        
        try:
            logger.info(f"Creating manual quest: {quest_type} for {team_name}")
            
            # Check if team exists
            team_check = await check_team_exists(team_name)
            
            if not team_check.get('exists'):
                return {
                    "success": False,
                    "error": f"Team '{team_name}' not found in system",
                    "status": "team_not_found"
                }
            
            # Generate quest content
            quest_content = generate_quest_content(
                quest_type=quest_type,
                home_team=team_name,
                user_preferences=user_preferences
            )
            
            logger.info(f"Manual quest created successfully for {team_name}")
            
            return {
                "success": True,
                "quest_type": quest_type,
                "team_name": team_name,
                "team_id": team_check.get('team_id'),
                "quest": quest_content,
                "status": "created"
            }
            
        except Exception as e:
            logger.error(f"Manual quest creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "status": "failed"
            }


# Global workflow instance
sports_quest_workflow = SportsQuestWorkflow()