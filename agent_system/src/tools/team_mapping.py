"""
Team Mapping Tools - Enhanced mapping between database teams and ESPN API
"""
from typing import Dict, List, Optional, Tuple
from ..services.espn_football_service import espn_football_service
from ..models.database import async_session
from ..models.team import Team
from sqlalchemy import select
import json
from loguru import logger
import difflib


class TeamMapper:
    """Enhanced team mapping with fuzzy matching and manual overrides"""
    
    def __init__(self):
        # Manual mapping overrides for better accuracy
        self.manual_mappings = {
            "PSG": ["Paris Saint-Germain", "Paris SG", "Paris Saint Germain"],
            "Real Madrid": ["Real Madrid CF", "Real Madrid C.F.", "Real Madrid"],
            "Barcelona": ["FC Barcelona", "Barcelona", "Barça"],
            "Manchester United": ["Manchester United FC", "Manchester Utd", "Man United"],
            "Bayern Munich": ["FC Bayern München", "Bayern München", "FC Bayern Munich", "Bayern Munich"],
            "Liverpool": ["Liverpool FC", "Liverpool F.C."],
            "Chelsea": ["Chelsea FC", "Chelsea F.C."],
            "Arsenal": ["Arsenal FC", "Arsenal F.C.", "Arsenal S.C."],
            "Manchester City": ["Manchester City FC", "Man City", "Manchester City F.C."],
            "Tottenham": ["Tottenham Hotspur FC", "Spurs", "Tottenham Hotspur"],
            "AC Milan": ["AC Milan", "Milano"],
            "Inter Milan": ["Inter Milan", "FC Internazionale Milano", "Inter"],
            "Juventus": ["Juventus FC", "Juventus F.C.", "Juve"],
            "Atletico Madrid": ["Atlético Madrid", "Atletico Madrid", "Atlético de Madrid"],
            "Borussia Dortmund": ["Borussia Dortmund", "BVB", "Dortmund"],
            "Napoli": ["SSC Napoli", "Napoli"],
            "AS Roma": ["AS Roma", "Roma"],
            "Sevilla": ["Sevilla FC", "Sevilla F.C."],
            "Valencia": ["Valencia CF", "Valencia C.F."],
            "Villarreal": ["Villarreal CF", "Villarreal C.F."],
        }
    
    def _calculate_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity score between two team names"""
        # Normalize names for comparison
        norm1 = self._normalize_name(name1)
        norm2 = self._normalize_name(name2)
        
        # Use difflib for similarity calculation
        similarity = difflib.SequenceMatcher(None, norm1, norm2).ratio()
        
        # Bonus for exact substring matches
        if norm1 in norm2 or norm2 in norm1:
            similarity += 0.2
        
        # Bonus for common abbreviations
        if self._check_abbreviation_match(norm1, norm2):
            similarity += 0.15
        
        return min(similarity, 1.0)
    
    def _normalize_name(self, name: str) -> str:
        """Normalize team name for comparison"""
        # Convert to lowercase and remove common suffixes/prefixes
        normalized = name.lower()
        
        # Remove common football club suffixes
        suffixes_to_remove = ["fc", "f.c.", "cf", "c.f.", "football club", "club de football", "s.c."]
        for suffix in suffixes_to_remove:
            if normalized.endswith(f" {suffix}"):
                normalized = normalized[:-len(f" {suffix}")]
            if normalized.startswith(f"{suffix} "):
                normalized = normalized[len(f"{suffix} "):]
        
        # Remove special characters and extra spaces
        normalized = ''.join(c for c in normalized if c.isalnum() or c.isspace())
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def _check_abbreviation_match(self, name1: str, name2: str) -> bool:
        """Check if one name could be an abbreviation of another"""
        words1 = name1.split()
        words2 = name2.split()
        
        # Check if first letters match
        if len(words1) == 1 and len(words2) > 1:
            abbrev = ''.join(word[0] for word in words2 if word)
            return words1[0] == abbrev
        elif len(words2) == 1 and len(words1) > 1:
            abbrev = ''.join(word[0] for word in words1 if word)
            return words2[0] == abbrev
            
        return False
    
    def find_best_match(self, db_team_name: str, api_teams: List[Dict]) -> Tuple[Optional[Dict], float]:
        """Find the best matching team from API results"""
        if not api_teams:
            return None, 0.0
        
        best_match = None
        best_score = 0.0
        
        # Check manual mappings first
        if db_team_name in self.manual_mappings:
            for api_team in api_teams:
                api_name = api_team.get("name", "")
                if api_name in self.manual_mappings[db_team_name]:
                    return api_team, 1.0
        
        # Fuzzy matching
        for api_team in api_teams:
            api_name = api_team.get("name", "")
            score = self._calculate_similarity(db_team_name, api_name)
            
            if score > best_score:
                best_score = score
                best_match = api_team
        
        return best_match, best_score
    
    async def enhanced_team_sync(self, similarity_threshold: float = 0.7) -> Dict:
        """Enhanced team synchronization with ESPN API"""
        results = {
            "synced": [],
            "failed": [],
            "manual_review": [],
            "statistics": {
                "total_teams": 0,
                "high_confidence": 0,
                "medium_confidence": 0,
                "low_confidence": 0,
                "not_found": 0
            }
        }
        
        async with async_session() as session:
            # Get all teams from database
            stmt = select(Team)
            result = await session.execute(stmt)
            db_teams = result.scalars().all()
            
            results["statistics"]["total_teams"] = len(db_teams)
            
            for team in db_teams:
                try:
                    logger.info(f"Processing team: {team.name}")
                    
                    # Search in ESPN API
                    api_team = await espn_football_service.search_team(team.name)
                    
                    if api_team:
                        # Calculate similarity score
                        score = self._calculate_similarity(team.name, api_team.get("name", ""))
                        
                        # Categorize result
                        if score >= 0.9:
                            category = "high_confidence"
                            results["statistics"]["high_confidence"] += 1
                        elif score >= similarity_threshold:
                            category = "medium_confidence"
                            results["statistics"]["medium_confidence"] += 1
                        else:
                            category = "low_confidence"
                            results["statistics"]["low_confidence"] += 1
                        
                        if score >= similarity_threshold:
                            # Update team with ESPN data
                            metadata = {
                                "espn_id": api_team.get("id"),
                                "espn_name": api_team.get("name"),
                                "match_score": score,
                                "category": category,
                                "country": api_team.get("country"),
                                "founded": api_team.get("founded"),
                                "logo": api_team.get("logo")
                            }
                            
                            team.external_id = str(api_team.get("id"))
                            team.team_metadata = json.dumps(metadata)
                            team.logo_url = api_team.get("logo")
                            team.country = api_team.get("country")
                            
                            sync_result = {
                                "db_team": team.name,
                                "api_team": api_team.get("name"),
                                "api_id": api_team.get("id"),
                                "confidence": category,
                                "score": score
                            }
                            
                            results["synced"].append(sync_result)
                            logger.info(f"Synced: {team.name} -> {api_team.get('name')} (score: {score:.2f})")
                            
                        else:
                            # Low confidence - add to manual review
                            results["manual_review"].append({
                                "db_team": team.name,
                                "suggested_match": api_team.get("name"),
                                "score": score,
                                "api_id": api_team.get("id"),
                                "reason": f"Low confidence score: {score:.2f}"
                            })
                            logger.warning(f"Low confidence match for {team.name}: {api_team.get('name')} (score: {score:.2f})")
                    else:
                        results["statistics"]["not_found"] += 1
                        results["failed"].append({
                            "team": team.name,
                            "reason": "No match found in ESPN API"
                        })
                        logger.warning(f"No match found for: {team.name}")
                
                except Exception as e:
                    logger.error(f"Error processing team {team.name}: {e}")
                    results["failed"].append({
                        "team": team.name,
                        "reason": f"Error: {str(e)}"
                    })
            
            await session.commit()
        
        return results
    
    async def manual_team_mapping(self, db_team_name: str, espn_team_id: str) -> Dict:
        """Manually map a team to an ESPN team ID"""
        async with async_session() as session:
            try:
                # Find the database team
                stmt = select(Team).where(Team.name == db_team_name)
                result = await session.execute(stmt)
                team = result.scalar_one_or_none()
                
                if not team:
                    return {"success": False, "error": f"Team '{db_team_name}' not found in database"}
                
                # Check if team exists in ESPN by searching for it
                api_team = await espn_football_service.search_team(db_team_name)
                
                if not api_team or str(api_team.get("id")) != espn_team_id:
                    return {"success": False, "error": f"ESPN team ID {espn_team_id} not found or doesn't match"}
                
                # Update team
                metadata = {
                    "espn_id": api_team.get("id"),
                    "espn_name": api_team.get("name"),
                    "manual_mapping": True,
                    "country": api_team.get("country"),
                    "founded": api_team.get("founded"),
                    "logo": api_team.get("logo")
                }
                
                team.external_id = str(api_team.get("id"))
                team.team_metadata = json.dumps(metadata)
                team.logo_url = api_team.get("logo")
                team.country = api_team.get("country")
                
                await session.commit()
                
                return {
                    "success": True,
                    "mapping": {
                        "db_team": db_team_name,
                        "api_team": api_team.get("name"),
                        "api_id": api_team.get("id")
                    }
                }
                
            except Exception as e:
                logger.error(f"Manual mapping failed: {e}")
                return {"success": False, "error": str(e)}


# Global mapper instance
team_mapper = TeamMapper()