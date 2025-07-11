"""
User management API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from loguru import logger
from ...models.database import get_db, async_session
from ...models.user import User
from ...models.user_team import UserTeam
from ...models.team import Team
import json

router = APIRouter()


class UserCreate(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    preferences: Optional[dict] = None


class UserTeamPreference(BaseModel):
    team_id: int
    is_favorite: bool = True
    notification_enabled: bool = True


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    preferences: Optional[dict]
    
    class Config:
        from_attributes = True


@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user with team preferences"""
    try:
        # Check if user already exists
        stmt = select(User).where(
            (User.username == user_data.username) | (User.email == user_data.email)
        )
        existing_user = await db.execute(stmt)
        if existing_user.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Create new user
        user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            preferences=json.dumps(user_data.preferences) if user_data.preferences else None
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            preferences=json.loads(user.preferences) if user.preferences else None
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register/blockchain")
async def register_blockchain_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Register a new user with blockchain address"""
    try:
        async with async_session() as session:
            # Check if user with same address already exists
            existing_user = await session.execute(
                select(User).where(User.address == user_data["address"])
            )
            if existing_user.scalar_one_or_none():
                return {
                    "detail": "User with this address already exists",
                    "already_exists": True
                }
            
            # Create new user
            new_user = User(
                address=user_data["address"],
                preferences=json.dumps({"favorite_teams": user_data.get("favorite_teams", [])})
            )
            session.add(new_user)
            await session.commit()
            
            return {
                "address": user_data["address"],
                "favorite_teams": user_data.get("favorite_teams", []),
                "registered": True
            }
            
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/preferences")
async def get_user_preferences(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get user profile and team preferences"""
    try:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user teams
        team_stmt = select(UserTeam).join(Team).where(UserTeam.user_id == user_id)
        team_result = await db.execute(team_stmt)
        user_teams = team_result.scalars().all()
        
        teams_data = []
        for ut in user_teams:
            team_stmt = select(Team).where(Team.id == ut.team_id)
            team_result = await db.execute(team_stmt)
            team = team_result.scalar_one_or_none()
            if team:
                teams_data.append({
                    "team_id": team.id,
                    "name": team.name,
                    "display_name": team.display_name,
                    "sport": team.sport,
                    "is_favorite": ut.is_favorite,
                    "notification_enabled": ut.notification_enabled
                })
        
        return {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "preferences": json.loads(user.preferences) if user.preferences else {}
            },
            "teams": teams_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}/preferences")
async def update_user_preferences(
    user_id: int, 
    preferences: dict, 
    db: AsyncSession = Depends(get_db)
):
    """Update user preferences"""
    try:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.preferences = json.dumps(preferences)
        await db.commit()
        
        return {
            "message": "Preferences updated successfully",
            "user_id": user_id,
            "preferences": preferences
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{user_id}/triggers")
async def add_team_trigger(
    user_id: int,
    team_preference: UserTeamPreference,
    db: AsyncSession = Depends(get_db)
):
    """Add team trigger/preference for user"""
    try:
        # Verify user exists
        user_stmt = select(User).where(User.id == user_id)
        user_result = await db.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verify team exists
        team_stmt = select(Team).where(Team.id == team_preference.team_id)
        team_result = await db.execute(team_stmt)
        team = team_result.scalar_one_or_none()
        
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        # Check if preference already exists
        existing_stmt = select(UserTeam).where(
            (UserTeam.user_id == user_id) & (UserTeam.team_id == team_preference.team_id)
        )
        existing_result = await db.execute(existing_stmt)
        existing = existing_result.scalar_one_or_none()
        
        if existing:
            # Update existing preference
            existing.is_favorite = team_preference.is_favorite
            existing.notification_enabled = team_preference.notification_enabled
        else:
            # Create new preference
            user_team = UserTeam(
                user_id=user_id,
                team_id=team_preference.team_id,
                is_favorite=team_preference.is_favorite,
                notification_enabled=team_preference.notification_enabled
            )
            db.add(user_team)
        
        await db.commit()
        
        return {
            "message": "Team trigger added successfully",
            "user_id": user_id,
            "team_id": team_preference.team_id,
            "team_name": team.name
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{address}/recommendations")
async def get_team_recommendations(address: str, db: AsyncSession = Depends(get_db)):
    """Get team recommendations for user based on current preferences"""
    try:
        # Get user by address
        user_stmt = select(User).where(User.address == address)
        user_result = await db.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user's current teams
        user_teams_stmt = select(UserTeam).where(UserTeam.user_id == user.id)
        user_teams_result = await db.execute(user_teams_stmt)
        user_teams = user_teams_result.scalars().all()
        user_team_ids = [ut.team_id for ut in user_teams]
        
        # Get teams user doesn't follow yet (simple recommendation)
        available_teams_stmt = select(Team).where(
            ~Team.id.in_(user_team_ids) if user_team_ids else True,
            Team.is_active == True
        ).limit(10)
        available_teams_result = await db.execute(available_teams_stmt)
        available_teams = available_teams_result.scalars().all()
        
        recommendations = [
            {
                "team_id": team.id,
                "name": team.name,
                "display_name": team.display_name,
                "sport": team.sport,
                "league": team.league,
                "logo_url": team.logo_url,
                "recommendation_score": 0.8  # Placeholder algorithm
            }
            for team in available_teams
        ]
        
        return {
            "address": address,
            "recommendations": recommendations,
            "total": len(recommendations)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))