"""
Quest management API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import List, Optional
from ...models.database import get_db
from ...models.quest import Quest, QuestType, QuestStatus
from ...models.team import Team
from ...models.user import User
import json

router = APIRouter()


class QuestResponse(BaseModel):
    id: int
    title: str
    description: str
    quest_type: str
    status: str
    team_name: str
    target_metric: Optional[str]
    target_value: Optional[int]
    current_progress: int
    metadata: Optional[dict]
    
    class Config:
        from_attributes = True


@router.get("/{user_id}")
async def get_user_quests(
    user_id: int,
    status: Optional[str] = None,
    quest_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Fetch user-specific quests"""
    try:
        stmt = select(Quest).options(selectinload(Quest.team)).where(Quest.user_id == user_id)
        
        if status:
            stmt = stmt.where(Quest.status == QuestStatus(status))
        if quest_type:
            stmt = stmt.where(Quest.quest_type == QuestType(quest_type))
            
        result = await db.execute(stmt)
        quests = result.scalars().all()
        
        quest_data = []
        for quest in quests:
            quest_data.append({
                "id": quest.id,
                "title": quest.title,
                "description": quest.description,
                "quest_type": quest.quest_type.value,
                "status": quest.status.value,
                "team_name": quest.team.name,
                "target_metric": quest.target_metric,
                "target_value": quest.target_value,
                "current_progress": quest.current_progress,
                "metadata": json.loads(quest.metadata) if quest.metadata else {}
            })
            
        return {
            "user_id": user_id,
            "quests": quest_data,
            "total": len(quest_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate")
async def validate_quest_content(
    quest_id: int,
    content: str,
    db: AsyncSession = Depends(get_db)
):
    """Automatic quest content validation"""
    try:
        # Get quest details
        stmt = select(Quest).options(selectinload(Quest.team)).where(Quest.id == quest_id)
        result = await db.execute(stmt)
        quest = result.scalar_one_or_none()
        
        if not quest:
            raise HTTPException(status_code=404, detail="Quest not found")
        
        # Import validation agents
        from ...agents.validation_agents import content_validator_agent
        from agents import Runner
        
        # Run validation through agent
        validation_input = {
            "content": content,
            "team_name": quest.team.name,
            "quest_type": quest.quest_type.value
        }
        
        result = await Runner.run(
            content_validator_agent,
            input=f"Validate this quest content: {json.dumps(validation_input)}"
        )
        
        return {
            "quest_id": quest_id,
            "validation_result": result.to_input_list(),
            "status": "validated"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conditional-create")
async def conditional_create_quest(
    team_name: str,
    event_title: str,
    event_date: str,
    db: AsyncSession = Depends(get_db)
):
    """Create quests based on team existence (core logic from PRD)"""
    try:
        # Import workflow
        from ...core.workflow_engine import sports_quest_workflow
        
        # Create event data
        event_data = {
            "title": event_title,
            "home_team": {"name": team_name},
            "away_team": {"name": "TBD"},
            "event_date": event_date,
            "sport": "football"
        }
        
        # Process through workflow
        result = await sports_quest_workflow.process_sports_event(event_data)
        
        return {
            "team_name": team_name,
            "event_title": event_title,
            "creation_result": result,
            "logic_applied": "conditional_creation_based_on_team_existence"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clash/{team1}vs{team2}")
async def get_clash_quest(
    team1: str,
    team2: str,
    db: AsyncSession = Depends(get_db)
):
    """Fetch clash quest between two teams"""
    try:
        # Find teams
        team1_stmt = select(Team).where(Team.name.ilike(f"%{team1}%"))
        team1_result = await db.execute(team1_stmt)
        team1_obj = team1_result.scalar_one_or_none()
        
        team2_stmt = select(Team).where(Team.name.ilike(f"%{team2}%"))
        team2_result = await db.execute(team2_stmt)
        team2_obj = team2_result.scalar_one_or_none()
        
        if not team1_obj or not team2_obj:
            raise HTTPException(status_code=404, detail="One or both teams not found")
        
        # Find clash quests
        clash_stmt = select(Quest).options(selectinload(Quest.team)).where(
            Quest.quest_type == QuestType.CLASH,
            Quest.team_id.in_([team1_obj.id, team2_obj.id])
        )
        clash_result = await db.execute(clash_stmt)
        clash_quests = clash_result.scalars().all()
        
        clash_data = []
        for quest in clash_quests:
            metadata = json.loads(quest.metadata) if quest.metadata else {}
            clash_data.append({
                "id": quest.id,
                "title": quest.title,
                "description": quest.description,
                "team_name": quest.team.name,
                "team_id": quest.team.id,
                "opponent_team_id": metadata.get("opponent_team_id"),
                "current_progress": quest.current_progress,
                "target_value": quest.target_value,
                "status": quest.status.value
            })
        
        return {
            "clash": f"{team1}vs{team2}",
            "team1": team1_obj.name,
            "team2": team2_obj.name,
            "quests": clash_data,
            "active_clash": len(clash_data) > 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collective/{quest_id}/progress")
async def get_collective_progress(quest_id: int, db: AsyncSession = Depends(get_db)):
    """Real-time collective progress bar"""
    try:
        stmt = select(Quest).options(selectinload(Quest.team)).where(
            Quest.id == quest_id,
            Quest.quest_type == QuestType.COLLECTIVE
        )
        result = await db.execute(stmt)
        quest = result.scalar_one_or_none()
        
        if not quest:
            raise HTTPException(status_code=404, detail="Collective quest not found")
        
        # Calculate progress percentage
        progress_percentage = (
            (quest.current_progress / quest.target_value * 100) 
            if quest.target_value else 0
        )
        
        return {
            "quest_id": quest_id,
            "title": quest.title,
            "current_progress": quest.current_progress,
            "target_value": quest.target_value,
            "progress_percentage": min(progress_percentage, 100),
            "status": quest.status.value,
            "team_name": quest.team.name,
            "real_time_update": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))