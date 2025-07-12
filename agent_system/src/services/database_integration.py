"""
Database Integration Service for ESPN - Complete DB operations
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
import json
from sqlalchemy import select, and_, or_
from ..models.database import async_session
from ..models.team import Team
from ..models.event import SportsEvent
from ..models.user import User
from ..models.quest import Quest
from .espn_football_service import espn_football_service


class DatabaseIntegrationService:
    """Service for complete database integration with ESPN API"""
    
    def __init__(self):
        self.espn = espn_football_service
    
    async def sync_teams_with_external_ids(self) -> Dict[str, Any]:
        """Sync all database teams with ESPN API and update external IDs"""
        results = {
            "synced": [],
            "failed": [],
            "total_processed": 0,
            "statistics": {
                "found_with_matches": 0,
                "found_without_matches": 0,
                "not_found": 0
            }
        }
        
        async with async_session() as session:
            # Get all teams from database
            stmt = select(Team)
            result = await session.execute(stmt)
            db_teams = result.scalars().all()
            
            results["total_processed"] = len(db_teams)
            
            for team in db_teams:
                try:
                    logger.info(f"Processing team: {team.name}")
                    
                    # Search for team in ESPN
                    api_team = await self.espn.search_team(team.name)
                    
                    if api_team:
                        team_id = api_team.get("id")
                        
                        # Try to get matches to verify team is active
                        try:
                            matches = await self.espn.get_team_matches(team_id)
                            matches_count = len(matches) if matches else 0
                            
                            if matches_count > 0:
                                results["statistics"]["found_with_matches"] += 1
                                status = "active_with_matches"
                            else:
                                results["statistics"]["found_without_matches"] += 1
                                status = "found_no_matches"
                                
                        except Exception as e:
                            logger.warning(f"Could not get matches for {team.name}: {e}")
                            matches_count = 0
                            status = "found_matches_error"
                        
                        # Update team with ESPN data
                        metadata = {
                            "espn_id": team_id,
                            "espn_name": api_team.get("name"),
                            "country": api_team.get("country"),
                            "founded": api_team.get("founded"),
                            "logo": api_team.get("logo"),
                            "matches_found": matches_count,
                            "status": status,
                            "last_sync": datetime.now().isoformat()
                        }
                        
                        team.external_id = str(team_id)
                        team.team_metadata = json.dumps(metadata)
                        team.logo_url = api_team.get("logo")
                        team.country = api_team.get("country")
                        team.is_active = True
                        
                        sync_result = {
                            "db_team": team.name,
                            "api_team": api_team.get("name"),
                            "api_id": team_id,
                            "matches_count": matches_count,
                            "status": status
                        }
                        
                        results["synced"].append(sync_result)
                        logger.info(f"✅ Synced: {team.name} -> ID: {team_id} ({matches_count} matches)")
                        
                    else:
                        results["statistics"]["not_found"] += 1
                        results["failed"].append({
                            "team": team.name,
                            "reason": "Not found in ESPN API"
                        })
                        logger.warning(f"❌ Not found: {team.name}")
                
                except Exception as e:
                    logger.error(f"Error processing team {team.name}: {e}")
                    results["failed"].append({
                        "team": team.name,
                        "reason": f"Error: {str(e)}"
                    })
            
            await session.commit()
        
        return results
    
    async def create_events_from_matches(self, team_id: int, limit: int = 10) -> Dict[str, Any]:
        """Create SportsEvent records from ESPN matches for a specific team"""
        results = {
            "created": [],
            "skipped": [],
            "errors": []
        }
        
        try:
            # Get team matches from ESPN
            matches = await self.espn.get_team_matches(team_id)
            
            if not matches:
                return {**results, "message": f"No matches found for team ID {team_id}"}
            
            # Limit matches to process
            matches = matches[:limit]
            
            async with async_session() as session:
                for match in matches:
                    try:
                        # Extract match data
                        event_data = self._parse_match_to_event(match, team_id)
                        
                        if not event_data:
                            results["skipped"].append({
                                "match_id": match.get("id"),
                                "reason": "Could not parse match data"
                            })
                            continue
                        
                        # Check if event already exists
                        existing_event = await session.execute(
                            select(SportsEvent).where(
                                and_(
                                    SportsEvent.external_id == str(match.get("id")),
                                    SportsEvent.source == "espn"
                                )
                            )
                        )
                        
                        if existing_event.scalar_one_or_none():
                            results["skipped"].append({
                                "match_id": match.get("id"),
                                "reason": "Event already exists"
                            })
                            continue
                        
                        # Create new event
                        new_event = SportsEvent(**event_data)
                        session.add(new_event)
                        
                        results["created"].append({
                            "match_id": match.get("id"),
                            "title": event_data["title"],
                            "event_date": event_data["event_date"]
                        })
                        
                    except Exception as e:
                        logger.error(f"Error creating event from match {match.get('id')}: {e}")
                        results["errors"].append({
                            "match_id": match.get("id"),
                            "error": str(e)
                        })
                
                await session.commit()
                
        except Exception as e:
            logger.error(f"Error getting matches for team {team_id}: {e}")
            results["errors"].append({
                "team_id": team_id,
                "error": str(e)
            })
        
        return results
    
    def _parse_match_to_event(self, match: Dict[str, Any], team_id: int) -> Optional[Dict[str, Any]]:
        """Parse ESPN match data into SportsEvent format"""
        try:
            match_id = match.get("id")
            start_time = match.get("start_time")
            
            if not match_id or not start_time:
                return None
            
            # Parse datetime
            try:
                event_date = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            except:
                logger.warning(f"Could not parse date: {start_time}")
                return None
            
            # Extract team names
            home_team = match.get("home_team_name", "Unknown")
            away_team = match.get("away_team_name", "Unknown")
            
            # Create title
            title = f"{home_team} vs {away_team}"
            
            # Extract league info
            league = match.get("tournament_name") or match.get("league_name") or "Unknown League"
            
            return {
                "title": title,
                "description": f"Match between {home_team} and {away_team}",
                "sport": "football",
                "league": league,
                "event_date": event_date,
                "home_team_id": 1,  # Default team ID - needs proper mapping
                "away_team_id": 1,  # Default team ID - needs proper mapping
                "external_id": str(match_id),
                "source": "espn",
                "event_metadata": json.dumps({
                    "home_team": home_team,
                    "away_team": away_team,
                    "home_team_id": match.get("home_team_id"),
                    "away_team_id": match.get("away_team_id"),
                    "tournament_id": match.get("tournament_id"),
                    "status": match.get("status"),
                    "venue": match.get("venue"),
                    "original_match": match
                })
            }
            
        except Exception as e:
            logger.error(f"Error parsing match {match.get('id')}: {e}")
            return None
    
    async def sync_events_for_all_teams(self, max_events_per_team: int = 5) -> Dict[str, Any]:
        """Sync events for all teams that have ESPN external IDs"""
        results = {
            "teams_processed": 0,
            "total_events_created": 0,
            "total_events_skipped": 0,
            "team_results": []
        }
        
        async with async_session() as session:
            # Get teams with external IDs
            stmt = select(Team).where(Team.external_id.isnot(None))
            result = await session.execute(stmt)
            teams_with_ids = result.scalars().all()
            
            results["teams_processed"] = len(teams_with_ids)
            
            for team in teams_with_ids:
                try:
                    if not team.external_id:
                        continue
                    
                    logger.info(f"Syncing events for team: {team.name} (ID: {team.external_id})")
                    
                    # Create events for this team
                    team_result = await self.create_events_from_matches(
                        int(team.external_id), 
                        max_events_per_team
                    )
                    
                    team_summary = {
                        "team_name": team.name,
                        "team_id": team.external_id,
                        "events_created": len(team_result["created"]),
                        "events_skipped": len(team_result["skipped"]),
                        "errors": len(team_result["errors"])
                    }
                    
                    results["team_results"].append(team_summary)
                    results["total_events_created"] += len(team_result["created"])
                    results["total_events_skipped"] += len(team_result["skipped"])
                    
                    logger.info(f"✅ Team {team.name}: {len(team_result['created'])} events created")
                    
                except Exception as e:
                    logger.error(f"Error syncing events for team {team.name}: {e}")
                    results["team_results"].append({
                        "team_name": team.name,
                        "team_id": team.external_id,
                        "error": str(e)
                    })
        
        return results
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get current integration status with ESPN"""
        async with async_session() as session:
            # Count teams
            total_teams = await session.execute(select(Team))
            total_teams_count = len(total_teams.scalars().all())
            
            teams_with_external_id = await session.execute(
                select(Team).where(Team.external_id.isnot(None))
            )
            synced_teams_count = len(teams_with_external_id.scalars().all())
            
            # Count events
            total_events = await session.execute(select(SportsEvent))
            total_events_count = len(total_events.scalars().all())
            
            espn_events = await session.execute(
                select(SportsEvent).where(SportsEvent.source == "espn")
            )
            espn_events_count = len(espn_events.scalars().all())
            
            return {
                "teams": {
                    "total": total_teams_count,
                    "synced_with_espn": synced_teams_count,
                    "sync_percentage": (synced_teams_count / total_teams_count * 100) if total_teams_count > 0 else 0
                },
                "events": {
                    "total": total_events_count,
                    "from_espn": espn_events_count,
                    "espn_percentage": (espn_events_count / total_events_count * 100) if total_events_count > 0 else 0
                },
                "last_updated": datetime.now().isoformat()
            }


# Global service instance
db_integration = DatabaseIntegrationService()