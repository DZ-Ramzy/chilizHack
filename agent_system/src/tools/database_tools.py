"""
Database tools for OpenAI Agents to interact with the sports quest database
"""
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..models.database import async_session
from ..models.user import User
from ..models.team import Team
from ..models.quest import Quest, QuestType, QuestStatus
from ..models.event import SportsEvent
from ..models.user_team import UserTeam
import json


async def check_team_exists(team_name: str) -> Dict[str, Any]:
    """Check if a team exists in the database"""
    async with async_session() as session:
        stmt = select(Team).where(Team.name.ilike(f"%{team_name}%"))
        result = await session.execute(stmt)
        team = result.scalar_one_or_none()
        
        if team:
            return {
                "exists": True,
                "team_id": team.id,
                "name": team.name,
                "display_name": team.display_name,
                "sport": team.sport,
                "league": team.league
            }
        return {"exists": False}


async def get_user_teams(user_id: int) -> List[Dict[str, Any]]:
    """Get all teams followed by a user"""
    async with async_session() as session:
        stmt = select(UserTeam).options(selectinload(UserTeam.team)).where(UserTeam.user_id == user_id)
        result = await session.execute(stmt)
        user_teams = result.scalars().all()
        
        return [
            {
                "team_id": ut.team.id,
                "name": ut.team.name,
                "display_name": ut.team.display_name,
                "sport": ut.team.sport,
                "is_favorite": ut.is_favorite
            }
            for ut in user_teams
        ]


async def get_team_community_size(team_id: int) -> int:
    """Get the number of users following a team"""
    async with async_session() as session:
        stmt = select(UserTeam).where(UserTeam.team_id == team_id)
        result = await session.execute(stmt)
        return len(result.scalars().all())


async def create_quest(
    title: str,
    description: str,
    quest_type: str,
    team_id: int,
    user_id: Optional[int] = None,
    event_id: Optional[int] = None,
    target_metric: Optional[str] = None,
    target_value: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a new quest"""
    async with async_session() as session:
        quest = Quest(
            title=title,
            description=description,
            quest_type=QuestType(quest_type),
            user_id=user_id,
            team_id=team_id,
            event_id=event_id,
            target_metric=target_metric,
            target_value=target_value,
            metadata=json.dumps(metadata) if metadata else None
        )
        
        session.add(quest)
        await session.commit()
        await session.refresh(quest)
        
        return {
            "quest_id": quest.id,
            "title": quest.title,
            "quest_type": quest.quest_type.value,
            "status": quest.status.value,
            "created": True
        }


async def get_active_events() -> List[Dict[str, Any]]:
    """Get all active sports events"""
    async with async_session() as session:
        stmt = select(SportsEvent).options(
            selectinload(SportsEvent.home_team),
            selectinload(SportsEvent.away_team)
        ).where(SportsEvent.is_active == True)
        
        result = await session.execute(stmt)
        events = result.scalars().all()
        
        return [
            {
                "event_id": event.id,
                "title": event.title,
                "home_team": {
                    "id": event.home_team.id,
                    "name": event.home_team.name,
                    "display_name": event.home_team.display_name
                },
                "away_team": {
                    "id": event.away_team.id,
                    "name": event.away_team.name,
                    "display_name": event.away_team.display_name
                },
                "event_date": event.event_date.isoformat(),
                "sport": event.sport,
                "league": event.league
            }
            for event in events
        ]


async def get_users_by_team(team_id: int) -> List[Dict[str, Any]]:
    """Get all users following a specific team"""
    async with async_session() as session:
        stmt = select(UserTeam).options(selectinload(UserTeam.user)).where(UserTeam.team_id == team_id)
        result = await session.execute(stmt)
        user_teams = result.scalars().all()
        
        return [
            {
                "user_id": ut.user.id,
                "username": ut.user.username,
                "email": ut.user.email,
                "is_favorite": ut.is_favorite,
                "notification_enabled": ut.notification_enabled
            }
            for ut in user_teams
        ]


async def update_quest_progress(quest_id: int, progress: int) -> Dict[str, Any]:
    """Update quest progress"""
    async with async_session() as session:
        stmt = select(Quest).where(Quest.id == quest_id)
        result = await session.execute(stmt)
        quest = result.scalar_one_or_none()
        
        if not quest:
            return {"updated": False, "error": "Quest not found"}
        
        quest.current_progress = progress
        
        # Check if quest is completed
        if quest.target_value and progress >= quest.target_value:
            quest.status = QuestStatus.COMPLETED
        
        await session.commit()
        
        return {
            "updated": True,
            "quest_id": quest.id,
            "progress": quest.current_progress,
            "status": quest.status.value,
            "completed": quest.status == QuestStatus.COMPLETED
        }