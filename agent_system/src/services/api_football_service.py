"""
API-Football Service - Integration with API-Football for real-time sports events
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


class APIFootballService:
    """Service to integrate with API-Football for real-time sports data"""
    
    def __init__(self):
        self.base_url = "https://api-football-v1.p.rapidapi.com/v3"
        self.api_key = os.getenv("API_FOOTBALL_KEY", "your_api_key_here")
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }
        
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make HTTP request to API-Football"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/{endpoint}",
                    headers=self.headers,
                    params=params or {},
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("errors"):
                    logger.error(f"API-Football error: {data['errors']}")
                    return {"response": []}
                    
                return data
                
            except httpx.RequestError as e:
                logger.error(f"Request error to API-Football: {e}")
                return {"response": []}
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return {"response": []}
    
    async def get_live_fixtures(self, league_ids: List[int] = None) -> List[Dict[str, Any]]:
        """Get live fixtures from API-Football"""
        params = {"live": "all"}
        if league_ids:
            params["league"] = ",".join(map(str, league_ids))
            
        data = await self._make_request("fixtures", params)
        return data.get("response", [])
    
    async def get_fixtures_by_date(self, date: str, league_ids: List[int] = None) -> List[Dict[str, Any]]:
        """Get fixtures for a specific date (YYYY-MM-DD)"""
        params = {"date": date}
        if league_ids:
            params["league"] = ",".join(map(str, league_ids))
            
        data = await self._make_request("fixtures", params)
        return data.get("response", [])
    
    async def get_next_fixtures(self, team_id: int, count: int = 10) -> List[Dict[str, Any]]:
        """Get next fixtures for a specific team"""
        params = {
            "team": team_id,
            "next": count
        }
        
        data = await self._make_request("fixtures", params)
        return data.get("response", [])
    
    async def get_team_info(self, team_name: str) -> Optional[Dict[str, Any]]:
        """Search for team by name"""
        params = {"search": team_name}
        
        data = await self._make_request("teams", params)
        teams = data.get("response", [])
        
        if teams:
            return teams[0]  # Return first match
        return None
    
    async def get_major_leagues(self) -> List[Dict[str, Any]]:
        """Get major football leagues"""
        # Major league IDs from API-Football
        major_leagues = [
            39,   # Premier League
            140,  # La Liga
            78,   # Bundesliga
            61,   # Ligue 1
            135,  # Serie A
            2,    # Champions League
            3,    # Europa League
        ]
        
        all_leagues = []
        for league_id in major_leagues:
            params = {"id": league_id}
            data = await self._make_request("leagues", params)
            leagues = data.get("response", [])
            all_leagues.extend(leagues)
            
        return all_leagues
    
    async def sync_teams_with_database(self) -> Dict[str, Any]:
        """Sync our database teams with API-Football team IDs"""
        synced_teams = []
        failed_teams = []
        
        async with async_session() as session:
            # Get all teams from our database
            stmt = select(Team)
            result = await session.execute(stmt)
            db_teams = result.scalars().all()
            
            for team in db_teams:
                try:
                    # Search for team in API-Football
                    api_team = await self.get_team_info(team.name)
                    
                    if api_team:
                        # Store API-Football team ID in metadata
                        team_data = api_team.get("team", {})
                        metadata = {
                            "api_football_id": team_data.get("id"),
                            "api_football_name": team_data.get("name"),
                            "founded": team_data.get("founded"),
                            "logo": team_data.get("logo"),
                            "venue": api_team.get("venue", {})
                        }
                        
                        team.external_id = str(team_data.get("id"))
                        team.metadata = json.dumps(metadata)
                        team.logo_url = team_data.get("logo")
                        
                        synced_teams.append({
                            "db_team": team.name,
                            "api_team": team_data.get("name"),
                            "api_id": team_data.get("id")
                        })
                        
                        logger.info(f"Synced team: {team.name} -> API ID: {team_data.get('id')}")
                        
                    else:
                        failed_teams.append(team.name)
                        logger.warning(f"Could not find API team for: {team.name}")
                        
                    # Rate limiting - API-Football free tier
                    await asyncio.sleep(1)
                    
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
    
    async def fetch_upcoming_fixtures_for_db_teams(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Fetch upcoming fixtures for teams in our database"""
        upcoming_fixtures = []
        
        async with async_session() as session:
            # Get all teams with API-Football IDs
            stmt = select(Team).where(Team.external_id.isnot(None))
            result = await session.execute(stmt)
            db_teams = result.scalars().all()
            
            for team in db_teams:
                try:
                    if team.external_id:
                        api_team_id = int(team.external_id)
                        fixtures = await self.get_next_fixtures(api_team_id, 5)
                        
                        for fixture in fixtures:
                            fixture_data = self._parse_fixture_data(fixture, team)
                            if fixture_data:
                                upcoming_fixtures.append(fixture_data)
                        
                        # Rate limiting
                        await asyncio.sleep(1)
                        
                except Exception as e:
                    logger.error(f"Error fetching fixtures for team {team.name}: {e}")
        
        return upcoming_fixtures
    
    def _parse_fixture_data(self, fixture: Dict[str, Any], db_team: Team) -> Optional[Dict[str, Any]]:
        """Parse API-Football fixture data into our format"""
        try:
            fixture_info = fixture.get("fixture", {})
            teams_info = fixture.get("teams", {})
            league_info = fixture.get("league", {})
            
            home_team = teams_info.get("home", {})
            away_team = teams_info.get("away", {})
            
            return {
                "api_fixture_id": fixture_info.get("id"),
                "title": f"{home_team.get('name')} vs {away_team.get('name')}",
                "home_team": {
                    "name": home_team.get("name"),
                    "api_id": home_team.get("id"),
                    "logo": home_team.get("logo")
                },
                "away_team": {
                    "name": away_team.get("name"),
                    "api_id": away_team.get("id"),
                    "logo": away_team.get("logo")
                },
                "event_date": fixture_info.get("date"),
                "venue": fixture_info.get("venue", {}).get("name"),
                "sport": "football",
                "league": league_info.get("name"),
                "status": fixture_info.get("status", {}).get("long", "scheduled"),
                "db_team_involved": db_team.name
            }
            
        except Exception as e:
            logger.error(f"Error parsing fixture data: {e}")
            return None
    
    async def create_events_from_fixtures(self, fixtures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create SportsEvent records from API-Football fixtures"""
        created_events = []
        skipped_events = []
        
        async with async_session() as session:
            for fixture in fixtures:
                try:
                    # Check if both teams exist in our database
                    home_team_name = fixture["home_team"]["name"]
                    away_team_name = fixture["away_team"]["name"]
                    
                    # Find teams in our database
                    home_stmt = select(Team).where(Team.name.ilike(f"%{home_team_name}%"))
                    away_stmt = select(Team).where(Team.name.ilike(f"%{away_team_name}%"))
                    
                    home_result = await session.execute(home_stmt)
                    away_result = await session.execute(away_stmt)
                    
                    home_team = home_result.scalar_one_or_none()
                    away_team = away_result.scalar_one_or_none()
                    
                    if home_team and away_team:
                        # Check if event already exists
                        existing_stmt = select(SportsEvent).where(
                            SportsEvent.external_id == str(fixture["api_fixture_id"])
                        )
                        existing_result = await session.execute(existing_stmt)
                        existing_event = existing_result.scalar_one_or_none()
                        
                        if not existing_event:
                            # Create new event
                            event = SportsEvent(
                                title=fixture["title"],
                                description=f"{fixture['league']} match",
                                sport=fixture["sport"],
                                league=fixture["league"],
                                home_team_id=home_team.id,
                                away_team_id=away_team.id,
                                event_date=datetime.fromisoformat(fixture["event_date"].replace("Z", "+00:00")),
                                venue=fixture["venue"],
                                status=fixture["status"],
                                external_id=str(fixture["api_fixture_id"]),
                                event_metadata=json.dumps(fixture)
                            )
                            
                            session.add(event)
                            created_events.append({
                                "title": fixture["title"],
                                "api_id": fixture["api_fixture_id"],
                                "date": fixture["event_date"]
                            })
                            
                        else:
                            skipped_events.append(f"Event already exists: {fixture['title']}")
                    else:
                        missing_teams = []
                        if not home_team:
                            missing_teams.append(home_team_name)
                        if not away_team:
                            missing_teams.append(away_team_name)
                        
                        skipped_events.append(f"Missing teams: {', '.join(missing_teams)} for {fixture['title']}")
                        
                except Exception as e:
                    logger.error(f"Error creating event from fixture: {e}")
                    skipped_events.append(f"Error: {fixture.get('title', 'Unknown')} - {str(e)}")
            
            await session.commit()
        
        return {
            "created": len(created_events),
            "skipped": len(skipped_events),
            "created_events": created_events,
            "skipped_events": skipped_events
        }


# Global service instance
api_football_service = APIFootballService()