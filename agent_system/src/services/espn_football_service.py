"""
ESPN Football API Service - Integration with ESPN API for real-time sports events
"""
import httpx
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
from ..models.database import async_session
from ..models.team import Team
from ..models.event import SportsEvent
from sqlalchemy import select
import json


class ESPNFootballService:
    """Service to integrate with ESPN Football API for real-time sports data"""
    
    def __init__(self):
        self.base_url = "http://site.api.espn.com/apis/site/v2/sports/soccer"
        # ESPN API league mappings for our teams
        self.league_mappings = {
            "La Liga": "esp.1",
            "Ligue 1": "fra.1", 
            "Premier League": "eng.1",
<<<<<<< HEAD
            "Bundesliga": "ger.1",
            "Champions League": "uefa.champions",
            "Europa League": "uefa.europa",
            "Club World Cup": "fifa.cwc",
            "International Friendlies": "fifa.friendly"
=======
            "Bundesliga": "ger.1"
>>>>>>> e97ca2b (feat: actual code)
        }
        # Team mappings to ESPN IDs
        self.team_mappings = {
            "Real Madrid": {"league": "esp.1", "id": "86"},
            "Barcelona": {"league": "esp.1", "id": "83"},
            "PSG": {"league": "fra.1", "id": "160"},
            "Manchester United": {"league": "eng.1", "id": "360"},
<<<<<<< HEAD
            "Bayern Munich": {"league": "ger.1", "id": "132"},
            "Chelsea": {"league": "eng.1", "id": "363"}
=======
            "Bayern Munich": {"league": "ger.1", "id": "132"}
>>>>>>> e97ca2b (feat: actual code)
        }
        
    async def _make_request(self, endpoint: str) -> Dict[str, Any]:
        """Make HTTP request to ESPN API"""
        async with httpx.AsyncClient() as client:
            try:
                url = f"{self.base_url}/{endpoint}"
                response = await client.get(url, timeout=30.0)
                response.raise_for_status()
                return response.json()
                
            except httpx.RequestError as e:
                logger.error(f"Request error to ESPN: {e}")
                return {}
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return {}
    
    async def search_team(self, team_name: str) -> Optional[Dict[str, Any]]:
        """Search for team by name using ESPN team mappings"""
        team_mapping = self.team_mappings.get(team_name)
        if not team_mapping:
            return None
            
        league = team_mapping["league"]
        team_id = team_mapping["id"]
        
        # Get team data from ESPN
        data = await self._make_request(f"{league}/teams/{team_id}")
        
        if data and "team" in data:
            team_data = data["team"]
            return {
                "id": team_data.get("id"),
                "name": team_data.get("displayName"),
                "abbreviation": team_data.get("abbreviation"),
                "location": team_data.get("location"),
                "color": team_data.get("color"),
                "logos": team_data.get("logos", []),
                "league": league
            }
        return None
    
    async def get_leagues(self) -> List[Dict[str, Any]]:
        """Get all available leagues from ESPN API"""
        try:
            leagues = []
            for league_name, league_code in self.league_mappings.items():
                league_data = await self._make_request(f"{league_code}/scoreboard")
                if league_data:
                    leagues.append({
                        "name": league_name,
                        "code": league_code,
                        "available": True
                    })
            return leagues
        except Exception as e:
            logger.error(f"Error getting leagues: {e}")
            return []
    
    async def get_team_by_id(self, team_id: str, league: str) -> Optional[Dict[str, Any]]:
        """Get team by ESPN ID and league"""
        data = await self._make_request(f"{league}/teams/{team_id}")
        
        if data and "team" in data:
            return data["team"]
        return None
    
    async def get_team_matches(self, team_name: str) -> List[Dict[str, Any]]:
<<<<<<< HEAD
        """Get matches for a team across ALL competitions"""
        team_mapping = self.team_mappings.get(team_name)
        if not team_mapping:
            return []
        
        matches = []
        
        # Search in ALL leagues/competitions for this team
        for league_name, league_code in self.league_mappings.items():
            try:
                # Get scoreboard data for each league
                data = await self._make_request(f"{league_code}/scoreboard")
                
                if data and "events" in data:
                    for event in data["events"]:
                        # Check if our team is involved
                        competitors = event.get("competitions", [{}])[0].get("competitors", [])
                        team_involved = False
                        
                        for competitor in competitors:
                            team = competitor.get("team", {})
                            if team.get("displayName") == team_name or team.get("id") == team_mapping["id"]:
                                team_involved = True
                                break
                        
                        if team_involved:
                            # Add league info to the match
                            match_data = self._parse_espn_event(event)
                            match_data["league"] = league_name
                            match_data["league_code"] = league_code
                            matches.append(match_data)
                            
            except Exception as e:
                logger.warning(f"Error checking {league_name} for {team_name}: {e}")
                continue
=======
        """Get matches for a team"""
        team_mapping = self.team_mappings.get(team_name)
        if not team_mapping:
            return []
            
        league = team_mapping["league"]
        
        # Get scoreboard data for the league
        data = await self._make_request(f"{league}/scoreboard")
        
        matches = []
        if data and "events" in data:
            for event in data["events"]:
                # Check if our team is involved
                competitors = event.get("competitions", [{}])[0].get("competitors", [])
                team_involved = False
                
                for competitor in competitors:
                    team = competitor.get("team", {})
                    if team.get("displayName") == team_name or team.get("id") == team_mapping["id"]:
                        team_involved = True
                        break
                
                if team_involved:
                    matches.append(self._parse_espn_event(event))
>>>>>>> e97ca2b (feat: actual code)
        
        return matches
    
    async def get_matches_by_league(self, league: str) -> List[Dict[str, Any]]:
        """Get all matches for a specific league"""
        data = await self._make_request(f"{league}/scoreboard")
        
        matches = []
        if data and "events" in data:
            for event in data["events"]:
                matches.append(self._parse_espn_event(event))
        
        return matches
    
    async def team_exists(self, team_name: str) -> Dict[str, Any]:
        """Check if team exists in our ESPN mappings"""
        team_data = await self.search_team(team_name)
        
        return {
            "exists": team_data is not None,
            "team_id": team_data.get("id") if team_data else None,
            "team_data": team_data
        }
    
    async def sync_teams_with_database(self) -> Dict[str, Any]:
        """Sync our database teams with ESPN team data"""
        synced_teams = []
        failed_teams = []
        
        async with async_session() as session:
            stmt = select(Team)
            result = await session.execute(stmt)
            db_teams = result.scalars().all()
            
            for team in db_teams:
                try:
                    espn_team = await self.search_team(team.name)
                    
                    if espn_team:
                        metadata = {
                            "espn_id": espn_team.get("id"),
                            "espn_name": espn_team.get("name"),
                            "abbreviation": espn_team.get("abbreviation"),
                            "location": espn_team.get("location"),
                            "color": espn_team.get("color"),
                            "league": espn_team.get("league")
                        }
                        
                        team.external_id = str(espn_team.get("id"))
                        team.metadata = json.dumps(metadata)
                        
                        # Set logo URL from ESPN logos
                        logos = espn_team.get("logos", [])
                        if logos:
                            team.logo_url = logos[0].get("href")
                        
                        synced_teams.append({
                            "db_team": team.name,
                            "espn_team": espn_team.get("name"),
                            "espn_id": espn_team.get("id"),
                            "league": espn_team.get("league")
                        })
                        
                        logger.info(f"Synced team: {team.name} -> ESPN ID: {espn_team.get('id')}")
                        
                    else:
                        failed_teams.append(team.name)
                        logger.warning(f"Could not find ESPN team for: {team.name}")
                        
                    await asyncio.sleep(0.1)  # Rate limiting
                    
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
            stmt = select(Team)
            result = await session.execute(stmt)
            db_teams = result.scalars().all()
            
            for team in db_teams:
                try:
                    matches = await self.get_team_matches(team.name)
                    
                    for match in matches:
                        event_data = self._parse_match_data(match, team)
                        if event_data:
                            upcoming_events.append(event_data)
                    
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Error fetching matches for team {team.name}: {e}")
        
        return upcoming_events
    
    def _parse_espn_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Parse ESPN event data"""
        competition = event.get("competitions", [{}])[0]
        competitors = competition.get("competitors", [])
        
        home_team = None
        away_team = None
        
        for competitor in competitors:
            if competitor.get("homeAway") == "home":
                home_team = competitor.get("team", {})
            else:
                away_team = competitor.get("team", {})
        
        return {
            "id": event.get("id"),
            "name": event.get("name"),
            "date": event.get("date"),
            "status": event.get("status", {}).get("type", {}).get("name"),
            "home_team": {
                "id": home_team.get("id") if home_team else None,
                "name": home_team.get("displayName") if home_team else None,
                "abbreviation": home_team.get("abbreviation") if home_team else None,
                "score": competitor.get("score") if competitor.get("homeAway") == "home" else None
            } if home_team else None,
            "away_team": {
                "id": away_team.get("id") if away_team else None,
                "name": away_team.get("displayName") if away_team else None,
                "abbreviation": away_team.get("abbreviation") if away_team else None,
                "score": competitor.get("score") if competitor.get("homeAway") == "away" else None
            } if away_team else None,
            "venue": competition.get("venue", {}).get("fullName"),
            "league": event.get("season", {}).get("slug")
        }
    
    def _parse_match_data(self, match: Dict[str, Any], db_team: Team) -> Optional[Dict[str, Any]]:
        """Parse ESPN match data into our format"""
        try:
            # Parse event date
            event_date_str = match.get("date")
            if not event_date_str:
                return None
                
            try:
                match_datetime = datetime.fromisoformat(event_date_str.replace("Z", "+00:00"))
            except ValueError:
                logger.warning(f"Could not parse date: {event_date_str}")
                return None
            
            # Only include future matches
            if match_datetime < datetime.now():
                return None
            
            home_team = match.get("home_team", {})
            away_team = match.get("away_team", {})
            
            return {
                "espn_event_id": match.get("id"),
                "title": match.get("name", f"{home_team.get('name')} vs {away_team.get('name')}"),
                "home_team": home_team,
                "away_team": away_team,
                "event_date": match_datetime.isoformat(),
                "venue": match.get("venue"),
                "sport": "football",
                "league": match.get("league"),
                "status": match.get("status", "not_started"),
                "db_team_involved": db_team.name
            }
            
        except Exception as e:
            logger.error(f"Error parsing ESPN match data: {e}")
            return None
    
    async def create_events_from_api_data(self, events_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create SportsEvent records from ESPN matches"""
        created_events = []
        skipped_events = []
        
        async with async_session() as session:
            for event_data in events_data:
                try:
                    home_team_name = event_data["home_team"]["name"]
                    away_team_name = event_data["away_team"]["name"]
                    
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
                            SportsEvent.external_id == str(event_data["espn_event_id"])
                        )
                        existing_result = await session.execute(existing_stmt)
                        existing_event = existing_result.scalar_one_or_none()
                        
                        if not existing_event:
                            event = SportsEvent(
                                title=event_data["title"],
                                description=f"{event_data['league']} Match",
                                sport=event_data["sport"],
                                league=event_data["league"],
                                home_team_id=home_team.id,
                                away_team_id=away_team.id,
                                event_date=datetime.fromisoformat(event_data["event_date"]),
                                venue=event_data["venue"],
                                status=event_data["status"],
                                external_id=str(event_data["espn_event_id"]),
                                event_metadata=json.dumps(event_data)
                            )
                            
                            session.add(event)
                            created_events.append({
                                "title": event_data["title"],
                                "espn_id": event_data["espn_event_id"],
                                "date": event_data["event_date"],
                                "league": event_data["league"]
                            })
                            
                        else:
                            skipped_events.append(f"Event already exists: {event_data['title']}")
                    else:
                        missing_teams = []
                        if not home_team:
                            missing_teams.append(home_team_name)
                        if not away_team:
                            missing_teams.append(away_team_name)
                        
                        skipped_events.append(f"Missing teams in DB: {', '.join(missing_teams)}")
                        
                except Exception as e:
                    logger.error(f"Error creating event from ESPN data: {e}")
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
        logger.info("Starting ESPN event sync and quest generation...")
        
        # Step 1: Sync teams
        sync_result = await self.sync_teams_with_database()
        logger.info(f"Team sync: {sync_result['synced']} synced, {sync_result['failed']} failed")
        
        # Step 2: Fetch upcoming events
        upcoming_events = await self.fetch_upcoming_events_for_db_teams()
        logger.info(f"Found {len(upcoming_events)} upcoming events")
        
        # Step 3: Create events in database
        create_result = await self.create_events_from_api_data(upcoming_events)
        logger.info(f"Created {create_result['created']} new events, skipped {create_result['skipped']}")
        
        return {
            "sync_result": sync_result,
            "events_created": create_result,
            "message": "ESPN sync completed. Use /api/quests/generate for quest creation"
        }


# Global service instance
espn_football_service = ESPNFootballService()