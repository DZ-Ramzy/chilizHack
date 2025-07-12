"""
ESPN Football API Routes - REST endpoints for ESPN Football API integration
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from loguru import logger
import json

from ...services.espn_football_service import espn_football_service
from ...models.database import async_session
from ...models.team import Team
from ...models.user import User
from sqlalchemy import select

router = APIRouter(prefix="/api", tags=["espn"])


@router.get("/teams/exists/{team_name}")
async def check_team_exists(team_name: str) -> Dict[str, Any]:
    """Check if team exists in ESPN API - PRD requirement"""
    try:
        result = await espn_football_service.team_exists(team_name)
        return result
    except Exception as e:
        logger.error(f"Error checking team existence: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quests/conditional-create")
async def conditional_create_quest(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create quests based on team existence - PRD core logic"""
    try:
        home_team = event_data.get("home_team")
        away_team = event_data.get("away_team")
        
        if not home_team or not away_team:
            raise HTTPException(status_code=400, detail="home_team and away_team are required")
        
        # Check if teams exist in our system
        home_exists = await espn_football_service.team_exists(home_team)
        away_exists = await espn_football_service.team_exists(away_team)
        
        created_quests = []
        
        if home_exists["exists"] and away_exists["exists"]:
            # Both teams exist → create individual + clash quest
            created_quests = [
                {"type": "individual", "team": home_team, "team_id": home_exists["team_id"]},
                {"type": "individual", "team": away_team, "team_id": away_exists["team_id"]},
                {"type": "clash", "home_team": home_team, "away_team": away_team}
            ]
            logger.info(f"Created 3 quests for {home_team} vs {away_team} (both teams exist)")
            
        elif home_exists["exists"]:
            # Only home team exists → create individual quest
            created_quests = [
                {"type": "individual", "team": home_team, "team_id": home_exists["team_id"]}
            ]
            logger.info(f"Created 1 quest for {home_team} (only home team exists)")
            
        elif away_exists["exists"]:
            # Only away team exists → create individual quest
            created_quests = [
                {"type": "individual", "team": away_team, "team_id": away_exists["team_id"]}
            ]
            logger.info(f"Created 1 quest for {away_team} (only away team exists)")
            
        else:
            # No teams exist → skip event
            logger.info(f"No quests created for {home_team} vs {away_team} (no teams exist in system)")
        
        return {
            "event": f"{home_team} vs {away_team}",
            "home_team_exists": home_exists["exists"],
            "away_team_exists": away_exists["exists"],
            "quests_created": len(created_quests),
            "quests": created_quests
        }
        
    except Exception as e:
        logger.error(f"Error in conditional quest creation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/preferences")
async def get_user_preferences(user_id: str) -> Dict[str, Any]:
    """Get user preferences - PRD requirement"""
    # Placeholder implementation
    return {
        "user_id": user_id,
        "favorite_teams": [],
        "leagues": [],
        "notifications_enabled": True
    }


@router.put("/users/{user_id}/preferences")
async def update_user_preferences(user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
    """Update user preferences - PRD requirement"""
    # Placeholder implementation
    return {
        "user_id": user_id,
        "updated": True,
        "preferences": preferences
    }


@router.get("/quests/{user_id}")
async def get_user_quests(user_id: str) -> Dict[str, Any]:
    """Get user-specific quests - PRD requirement"""
    # Placeholder implementation
    return {
        "user_id": user_id,
        "quests": [
            {
                "id": "quest_1",
                "title": "Tweet about your team's upcoming match",
                "type": "social",
                "team": "PSG",
                "deadline": "2025-07-12T15:00:00Z",
                "status": "active"
            }
        ]
    }


@router.post("/quests/validate")
async def validate_quest(quest_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate quest relevance - PRD requirement"""
    # Placeholder implementation
    relevance_score = 0.8  # Mock score
    
    return {
        "quest_id": quest_data.get("id"),
        "relevance_score": relevance_score,
        "valid": relevance_score > 0.5,
        "validation_details": {
            "content_relevant": True,
            "timing_appropriate": True,
            "team_match": True
        }
    }


@router.get("/missions/generate/{team_id}")
async def generate_team_missions(team_id: str) -> Dict[str, Any]:
    """Generate missions for team events - PRD requirement"""
    try:
        # Find team by ID in our mappings
        team_name = None
        league = None
        for name, mapping in espn_football_service.team_mappings.items():
            if mapping["id"] == team_id:
                team_name = name
                league = mapping["league"]
                break
        
        if not team_name:
            raise HTTPException(status_code=404, detail=f"Team {team_id} not found in mappings")
        
        # Get team info from ESPN
        team_data = await espn_football_service.get_team_by_id(team_id, league)
        
        if not team_data:
            raise HTTPException(status_code=404, detail=f"Team {team_id} not found in ESPN")
        
        # Get upcoming matches for this team
        matches = await espn_football_service.get_team_matches(team_name)
        
        missions = []
        for match in matches[:3]:  # Limit to next 3 matches
            missions.append({
                "id": f"mission_{match['id']}",
                "title": f"Support {team_name} in upcoming match",
                "type": "pre_match",
                "match_id": match.get("id", "unknown"),
                "match_date": match.get("date", "TBD"),
                "opponent": "TBD",
                "tasks": [
                    "Share team lineup predictions",
                    "Post pre-match excitement",
                    "Engage with other fans"
                ]
            })
        
        return {
            "team_id": team_id,
            "team_name": team_name,
            "missions_generated": len(missions),
            "missions": missions
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid team_id format")
    except Exception as e:
        logger.error(f"Error generating missions for team {team_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sync/test-team/{team_name}")
async def test_team_search(team_name: str) -> Dict[str, Any]:
    """Test team search in ESPN API"""
    try:
        team = await espn_football_service.search_team(team_name)
        
        if team:
            return {
                "found": True,
                "team_name": team_name,
                "api_team": {
                    "id": team.get("id"),
                    "name": team.get("name"),
                    "country_id": team.get("country_id"),
                    "venue_name": team.get("venue_name"),
                    "hash_image": team.get("hash_image")
                }
            }
        else:
            return {
                "found": False,
                "team_name": team_name,
                "message": f"Team '{team_name}' not found in ESPN API"
            }
            
    except Exception as e:
        logger.error(f"Error testing team search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sync/test-matches/{team_name}")
async def test_team_matches(team_name: str) -> Dict[str, Any]:
    """Test getting matches for a team"""
    try:
        # First find the team
        team = await espn_football_service.search_team(team_name)
        
        if not team:
            return {
                "found": False,
                "team_name": team_name,
                "message": f"Team '{team_name}' not found"
            }
        
        # Get upcoming matches
        matches = await espn_football_service.get_team_matches(team_name)
        
        return {
            "found": True,
            "team_name": team_name,
            "team_id": team["id"],
            "upcoming_matches": len(matches),
            "matches": matches[:5]  # Show first 5 matches
        }
        
    except Exception as e:
        logger.error(f"Error testing team matches: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync/teams")
async def sync_teams_with_espn() -> Dict[str, Any]:
    """Sync database teams with ESPN API"""
    try:
        result = await espn_football_service.sync_teams_with_database()
        return result
    except Exception as e:
        logger.error(f"Error syncing teams: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync/events")
async def sync_events_from_espn() -> Dict[str, Any]:
    """Sync events from ESPN API"""
    try:
        upcoming_events = await espn_football_service.fetch_upcoming_events_for_db_teams()
        create_result = await espn_football_service.create_events_from_api_data(upcoming_events)
        
        return {
            "events_fetched": len(upcoming_events),
            "events_created": create_result["created"],
            "events_skipped": create_result["skipped"],
            "created_events": create_result["created_events"],
            "skipped_events": create_result["skipped_events"]
        }
        
    except Exception as e:
        logger.error(f"Error syncing events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync/full")
async def full_sync_and_quest_generation() -> Dict[str, Any]:
    """Full sync with quest generation - main workflow"""
    try:
        result = await espn_football_service.sync_events_and_trigger_quests()
        return result
    except Exception as e:
        logger.error(f"Error in full sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/teams/add-chelsea")
async def add_chelsea_team() -> Dict[str, Any]:
    """Add Chelsea to the database"""
    try:
        from ...models.team import Team
        from ...models.database import async_session
        from sqlalchemy import select
        
        async with async_session() as session:
            # Check if Chelsea already exists
            existing_team = await session.execute(
                select(Team).where(Team.name == "Chelsea")
            )
            existing = existing_team.scalar_one_or_none()
            if existing:
                return {
                    "success": False,
                    "message": "Chelsea already exists in database",
                    "team_id": existing.id
                }
            
            # Create Chelsea team
            chelsea = Team(
                name="Chelsea",
                display_name="Chelsea FC",
                sport="football",
                league="Premier League",
                country="England",
                external_id="363",  # ESPN API ID
                is_active=True
            )
            
            session.add(chelsea)
            await session.commit()
            await session.refresh(chelsea)
            
            return {
                "success": True,
                "message": "Chelsea added successfully",
                "team": {
                    "id": chelsea.id,
                    "name": chelsea.name,
                    "display_name": chelsea.display_name,
                    "sport": chelsea.sport,
                    "league": chelsea.league,
                    "external_id": chelsea.external_id
                }
            }
        
    except Exception as e:
        logger.error(f"Error adding Chelsea: {e}")
        raise HTTPException(status_code=500, detail=str(e))