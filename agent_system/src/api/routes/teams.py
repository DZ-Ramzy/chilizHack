"""
Team management API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
from ...models.database import get_db
from ...models.team import Team

router = APIRouter()


class TeamResponse(BaseModel):
    id: int
    name: str
    display_name: str
    sport: str
    league: Optional[str]
    country: Optional[str]
    logo_url: Optional[str]
    is_active: bool
    
    class Config:
        from_attributes = True


@router.get("/exists/{team_name}")
async def check_team_exists(team_name: str, db: AsyncSession = Depends(get_db)):
    """Check if team exists in system (used by agents)"""
    try:
        stmt = select(Team).where(Team.name.ilike(f"%{team_name}%"))
        result = await db.execute(stmt)
        team = result.scalar_one_or_none()
        
        if team:
            return {
                "exists": True,
                "team": {
                    "id": team.id,
                    "name": team.name,
                    "display_name": team.display_name,
                    "sport": team.sport,
                    "league": team.league
                }
            }
        else:
            return {"exists": False}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[TeamResponse])
async def get_teams(
    sport: Optional[str] = None,
    league: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get list of teams with optional filtering"""
    try:
        stmt = select(Team).where(Team.is_active == True)
        
        if sport:
            stmt = stmt.where(Team.sport.ilike(f"%{sport}%"))
        if league:
            stmt = stmt.where(Team.league.ilike(f"%{league}%"))
            
        stmt = stmt.offset(skip).limit(limit)
        
        result = await db.execute(stmt)
        teams = result.scalars().all()
        
        return [TeamResponse.from_orm(team) for team in teams]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(team_id: int, db: AsyncSession = Depends(get_db)):
    """Get specific team details"""
    try:
        stmt = select(Team).where(Team.id == team_id)
        result = await db.execute(stmt)
        team = result.scalar_one_or_none()
        
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
            
        return TeamResponse.from_orm(team)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{team_id}/community")
async def get_team_community(team_id: int, db: AsyncSession = Depends(get_db)):
    """Get team community info (fan count, etc.)"""
    try:
        # Verify team exists
        team_stmt = select(Team).where(Team.id == team_id)
        team_result = await db.execute(team_stmt)
        team = team_result.scalar_one_or_none()
        
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        # Get community size (would normally import UserTeam here)
        from ...models.user_team import UserTeam
        community_stmt = select(UserTeam).where(UserTeam.team_id == team_id)
        community_result = await db.execute(community_stmt)
        community_members = community_result.scalars().all()
        
        return {
            "team_id": team_id,
            "team_name": team.name,
            "total_fans": len(community_members),
            "active_fans": len([m for m in community_members if m.notification_enabled]),
            "community_growth": "stable"  # Placeholder for analytics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))