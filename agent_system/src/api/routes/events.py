"""
Sports events API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from ...models.database import get_db
from ...models.event import SportsEvent
from ...models.team import Team

router = APIRouter()


class EventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    sport: str
    league: Optional[str]
    home_team: dict
    away_team: dict
    event_date: datetime
    venue: Optional[str]
    status: str
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[EventResponse])
async def get_events(
    sport: Optional[str] = None,
    league: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get list of sports events"""
    try:
        stmt = select(SportsEvent).options(
            selectinload(SportsEvent.home_team),
            selectinload(SportsEvent.away_team)
        ).where(SportsEvent.is_active == True)
        
        if sport:
            stmt = stmt.where(SportsEvent.sport.ilike(f"%{sport}%"))
        if league:
            stmt = stmt.where(SportsEvent.league.ilike(f"%{league}%"))
        if status:
            stmt = stmt.where(SportsEvent.status == status)
            
        stmt = stmt.offset(skip).limit(limit).order_by(SportsEvent.event_date)
        
        result = await db.execute(stmt)
        events = result.scalars().all()
        
        events_data = []
        for event in events:
            events_data.append({
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "sport": event.sport,
                "league": event.league,
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
                "event_date": event.event_date,
                "venue": event.venue,
                "status": event.status
            })
            
        return events_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{event_id}")
async def get_event(event_id: int, db: AsyncSession = Depends(get_db)):
    """Get specific event details"""
    try:
        stmt = select(SportsEvent).options(
            selectinload(SportsEvent.home_team),
            selectinload(SportsEvent.away_team),
            selectinload(SportsEvent.quests)
        ).where(SportsEvent.id == event_id)
        
        result = await db.execute(stmt)
        event = result.scalar_one_or_none()
        
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "sport": event.sport,
            "league": event.league,
            "home_team": {
                "id": event.home_team.id,
                "name": event.home_team.name,
                "display_name": event.home_team.display_name,
                "logo_url": event.home_team.logo_url
            },
            "away_team": {
                "id": event.away_team.id,
                "name": event.away_team.name,
                "display_name": event.away_team.display_name,
                "logo_url": event.away_team.logo_url
            },
            "event_date": event.event_date,
            "venue": event.venue,
            "status": event.status,
            "quests_generated": len(event.quests) if event.quests else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))