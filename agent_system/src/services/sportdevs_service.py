"""
SportDevs Football API Service - Integration with SportDevs for real-time sports events
"""
import httpx
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
import os
from ..models.database import async_session
from ..models.team import Team
from ..models.event import SportsEvent
from sqlalchemy import select
import json


class SportDevsService:
    """Service to integrate with SportDevs Football API for real-time sports data"""
    
    def __init__(self):
        self.base_url = "https://football.sportdevs.com"
        self.api_key = os.getenv("SPORTDEVS_API_KEY")
        if not self.api_key:
            raise ValueError("SPORTDEVS_API_KEY environment variable is required")
        
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make HTTP request to SportDevs API"""
        async with httpx.AsyncClient() as client:
            try:
                url = f"{self.base_url}/{endpoint}"
                headers = {"Authorization": f"Bearer {self.api_key}"}
                
                response = await client.get(
                    url,
                    params=params or {},
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                return data if isinstance(data, list) else [data]
                
            except httpx.RequestError as e:
                logger.error(f"Request error to SportDevs: {e}")
                return []
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return []
    
    async def search_team(self, team_name: str) -> Optional[Dict[str, Any]]:
        """Search for team by name"""
        data = await self._make_request("teams", {"name": f"like.*{team_name}*"})
        
        if data:
            return data[0]  # Return first match
        return None
    
    async def get_team_by_id(self, team_id: int) -> Optional[Dict[str, Any]]:
        """Get team by ID"""
        data = await self._make_request("teams", {"id": f"eq.{team_id}"})
        
        if data:
            return data[0]
        return None
    
    async def get_team_matches(self, team_id: int, date: str = None) -> List[Dict[str, Any]]:
        """Get matches for a team - FIXED VERSION"""
        try:
            # Try different approaches for team matches
            params = {}
            
            # First approach: use team filters
            if date:
                params["date"] = f"eq.{date}"
            
            # Try to get all matches and filter by team
            all_matches = await self._make_request("matches", params)
            
            # Filter matches where the team is involved
            team_matches = []
            for match in all_matches:
                home_team = match.get("home_team_id") or match.get("home_team")
                away_team = match.get("away_team_id") or match.get("away_team")
                
                # Check if team_id matches either home or away team
                if (str(home_team) == str(team_id) or 
                    str(away_team) == str(team_id)):
                    team_matches.append(match)
            
            return team_matches
            
        except Exception as e:
            logger.warning(f"Error getting team matches (trying alternative approach): {e}")
            
            # Alternative approach: get limited matches without team filter
            try:
                all_matches = await self._make_request("matches", {"limit": "100"})
                team_matches = []
                
                for match in all_matches:
                    # Try different field names that might contain team info
                    team_fields = ["home_team_id", "away_team_id", "home_team", "away_team", "team_1", "team_2"]
                    
                    for field in team_fields:
                        if str(match.get(field, "")) == str(team_id):
                            team_matches.append(match)
                            break
                
                return team_matches
                
            except Exception as e2:
                logger.error(f"Failed to get team matches with alternative approach: {e2}")
                return []
    
    async def get_matches_by_date(self, date: str, league_id: int = None) -> List[Dict[str, Any]]:
        """Get matches for specific date"""
        params = {"date": f"eq.{date}"}
        if league_id:
            params["league_id"] = f"eq.{league_id}"
        
        return await self._make_request("matches", params)
    
    async def get_leagues(self, country_name: str = None) -> List[Dict[str, Any]]:
        """Get leagues, optionally filtered by country"""
        params = {}
        if country_name:
            params["country_name"] = f"like.*{country_name}*"
        
        return await self._make_request("leagues", params)
    
    async def get_standings(self, league_id: int, season: str = "2025") -> List[Dict[str, Any]]:
        """Get league standings"""
        params = {
            "league_id": f"eq.{league_id}",
            "season": f"eq.{season}"
        }
        
        return await self._make_request("standings", params)
    
    async def team_exists(self, team_name: str) -> Dict[str, Any]:
        """Check if team exists in SportDevs API"""
        team = await self.search_team(team_name)
        
        return {
            "exists": team is not None,
            "team_id": team.get("id") if team else None,
            "team_data": team
        }
    
    async def sync_teams_with_database(self) -> Dict[str, Any]:
        """Sync our database teams with SportDevs team IDs"""
        synced_teams = []
        failed_teams = []
        
        async with async_session() as session:
            # Get all teams from our database
            stmt = select(Team)
            result = await session.execute(stmt)
            db_teams = result.scalars().all()
            
            for team in db_teams:
                try:
                    # Search for team in SportDevs
                    api_team = await self.search_team(team.name)
                    
                    if api_team:
                        # Store SportDevs team ID and data in metadata
                        metadata = {
                            "sportdevs_id": api_team.get("id"),
                            "sportdevs_name": api_team.get("name"),
                            "country_id": api_team.get("country_id"),
                            "hash_image": api_team.get("hash_image"),
                            "founded": api_team.get("founded"),
                            "venue_name": api_team.get("venue_name"),
                            "venue_capacity": api_team.get("venue_capacity"),
                            "city": api_team.get("venue_city")
                        }
                        
                        team.external_id = str(api_team.get("id"))
                        team.metadata = json.dumps(metadata)
                        
                        # Set logo URL from hash_image
                        if api_team.get("hash_image"):
                            team.logo_url = f"https://images.sportdevs.com/{api_team['hash_image']}.png"
                        
                        synced_teams.append({
                            "db_team": team.name,
                            "api_team": api_team.get("name"),
                            "api_id": api_team.get("id"),
                            "country_id": api_team.get("country_id")
                        })
                        
                        logger.info(f"Synced team: {team.name} -> SportDevs ID: {api_team.get('id')}")
                        
                    else:
                        failed_teams.append(team.name)
                        logger.warning(f"Could not find SportDevs team for: {team.name}")
                        
                    # Rate limiting - be respectful to API
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error syncing team {team.name}: {e}")
                    failed_teams.append(team.name)
            
            await session.commit()
        
        return {
            "synced": len(synced_teams),
            "failed": len(failed_teams),
            "synced_teams": synced_teams,
            "failed_teams": failed_teams
        }
    
    async def fetch_upcoming_events_for_db_teams(self) -> List[Dict[str, Any]]:
        """Fetch upcoming events for teams in our database"""
        upcoming_events = []
        
        async with async_session() as session:
            # Get all teams with SportDevs IDs
            stmt = select(Team).where(Team.external_id.isnot(None))
            result = await session.execute(stmt)
            db_teams = result.scalars().all()
            
            for team in db_teams:
                try:
                    if team.external_id:
                        matches = await self.get_team_matches(int(team.external_id))
                        
                        for match in matches:
                            event_data = self._parse_match_data(match, team)
                            if event_data:
                                upcoming_events.append(event_data)
                        
                        # Rate limiting
                        await asyncio.sleep(0.5)
                        
                except Exception as e:
                    logger.error(f"Error fetching matches for team {team.name}: {e}")
        
        return upcoming_events
    
    def _parse_match_data(self, match: Dict[str, Any], db_team: Team) -> Optional[Dict[str, Any]]:
        """Parse SportDevs match data into our format"""
        try:
            # Skip matches without proper start_time or if already finished
            start_time = match.get("start_time")
            status_type = match.get("status_type")
            
            if not start_time or status_type in ["finished", "postponed", "cancelled"]:
                return None
            
            # Parse start_time (ISO format: 2023-11-04T17:45:00+00:00)
            try:
                match_datetime = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            except ValueError:
                logger.warning(f"Could not parse start_time: {start_time}")
                return None
            
            # Only include future matches
            if match_datetime < datetime.now():
                return None
            
            return {
                "sportdevs_match_id": match.get("id"),
                "title": match.get("name", f"{match.get('home_team_name')} vs {match.get('away_team_name')}"),
                "home_team": {
                    "name": match.get("home_team_name"),
                    "sportdevs_id": match.get("home_team_id"),
                    "score": match.get("home_team_score", {}).get("current") if match.get("home_team_score") else None
                },
                "away_team": {
                    "name": match.get("away_team_name"),
                    "sportdevs_id": match.get("away_team_id"),
                    "score": match.get("away_team_score", {}).get("current") if match.get("away_team_score") else None
                },
                "event_date": match_datetime.isoformat(),
                "venue": None,  # SportDevs doesn't seem to include venue info in matches
                "sport": "football",
                "league_id": match.get("league_id"),
                "league_name": match.get("league_name"),
                "tournament_id": match.get("tournament_id"),
                "tournament_name": match.get("tournament_name"),
                "status": status_type or "not_started",
                "season": match.get("season_name"),
                "round": match.get("round", {}).get("name") if match.get("round") else None,
                "db_team_involved": db_team.name
            }
            
        except Exception as e:
            logger.error(f"Error parsing match data: {e}")
            return None
    
    async def create_events_from_api_data(self, events_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create SportsEvent records from SportDevs matches"""
        created_events = []
        skipped_events = []
        
        async with async_session() as session:
            for event_data in events_data:
                try:
                    # Check if both teams exist in our database
                    home_team_name = event_data["home_team"]["name"]
                    away_team_name = event_data["away_team"]["name"]
                    
                    # Find teams in our database by name or external_id
                    home_stmt = select(Team).where(
                        (Team.name.ilike(f"%{home_team_name}%")) |
                        (Team.external_id == str(event_data["home_team"]["sportdevs_id"]))
                    )
                    away_stmt = select(Team).where(
                        (Team.name.ilike(f"%{away_team_name}%")) |
                        (Team.external_id == str(event_data["away_team"]["sportdevs_id"]))
                    )
                    
                    home_result = await session.execute(home_stmt)
                    away_result = await session.execute(away_stmt)
                    
                    home_team = home_result.scalar_one_or_none()
                    away_team = away_result.scalar_one_or_none()
                    
                    if home_team and away_team:
                        # Check if event already exists
                        existing_stmt = select(SportsEvent).where(
                            SportsEvent.external_id == str(event_data["sportdevs_match_id"])
                        )
                        existing_result = await session.execute(existing_stmt)
                        existing_event = existing_result.scalar_one_or_none()
                        
                        if not existing_event:
                            # Create new event
                            event = SportsEvent(
                                title=event_data["title"],
                                description=f"{event_data['league_name']} - Round {event_data.get('round', 'N/A')}",
                                sport=event_data["sport"],
                                league=event_data["league_name"],
                                home_team_id=home_team.id,
                                away_team_id=away_team.id,
                                event_date=datetime.fromisoformat(event_data["event_date"]),
                                venue=event_data["venue"],
                                status=event_data["status"],
                                external_id=str(event_data["sportdevs_match_id"]),
                                event_metadata=json.dumps(event_data)
                            )
                            
                            session.add(event)
                            created_events.append({
                                "title": event_data["title"],
                                "sportdevs_id": event_data["sportdevs_match_id"],
                                "date": event_data["event_date"],
                                "league": event_data["league_name"]
                            })
                            
                        else:
                            skipped_events.append(f"Event already exists: {event_data['title']}")
                    else:
                        missing_teams = []
                        if not home_team:
                            missing_teams.append(home_team_name)
                        if not away_team:
                            missing_teams.append(away_team_name)
                        
                        skipped_events.append(f"Missing teams in DB: {', '.join(missing_teams)} for {event_data['title']}")
                        
                except Exception as e:
                    logger.error(f"Error creating event from API data: {e}")
                    skipped_events.append(f"Error: {event_data.get('title', 'Unknown')} - {str(e)}")
            
            await session.commit()
        
        return {
            "created": len(created_events),
            "skipped": len(skipped_events),
            "created_events": created_events,
            "skipped_events": skipped_events
        }
    
    async def sync_events_and_trigger_quests(self) -> Dict[str, Any]:
        """Main workflow: Sync events and trigger quest generation"""
        logger.info("Starting SportDevs event sync and quest generation...")
        
        # Step 1: Sync teams if needed
        sync_result = await self.sync_teams_with_database()
        logger.info(f"Team sync: {sync_result['synced']} synced, {sync_result['failed']} failed")
        
        # Step 2: Fetch upcoming events
        upcoming_events = await self.fetch_upcoming_events_for_db_teams()
        logger.info(f"Found {len(upcoming_events)} upcoming events")
        
        # Step 3: Create events in database
        create_result = await self.create_events_from_api_data(upcoming_events)
        logger.info(f"Created {create_result['created']} new events, skipped {create_result['skipped']}")
        
        # Step 4: Trigger quest generation for new events
        from ..core.workflow_engine import sports_quest_workflow
        
        quest_results = []
        for event_info in create_result["created_events"]:
            try:
                # Prepare event data for workflow
                workflow_event_data = {
                    "event_id": f"sportdevs_{event_info['sportdevs_id']}",
                    "title": event_info["title"],
                    "home_team": event_info["title"].split(" vs ")[0],
                    "away_team": event_info["title"].split(" vs ")[1],
                    "event_date": event_info["date"],
                    "sport": "football",
                    "league": event_info["league"]
                }
                
                # Trigger quest generation workflow
                quest_result = await sports_quest_workflow.process_sports_event(workflow_event_data)
                quest_results.append(quest_result)
                
                logger.info(f"Quest generation triggered for: {event_info['title']}")
                
            except Exception as e:
                logger.error(f"Failed to trigger quest for event {event_info['title']}: {e}")
        
        return {
            "sync_result": sync_result,
            "events_created": create_result,
            "quests_triggered": len(quest_results),
            "quest_results": quest_results
        }


# Global service instance
sportdevs_service = SportDevsService()