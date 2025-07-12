"""
Quest management API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
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


@router.get("/")
async def get_all_quests(
    status: Optional[str] = None,
    quest_type: Optional[str] = None,
    team_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all quests with optional filtering"""
    try:
        stmt = select(Quest).options(selectinload(Quest.team))
        
        if status:
            stmt = stmt.where(Quest.status == QuestStatus(status))
        if quest_type:
            stmt = stmt.where(Quest.quest_type == QuestType(quest_type))
        if team_id:
            stmt = stmt.where(Quest.team_id == team_id)
            
        stmt = stmt.offset(skip).limit(limit).order_by(Quest.created_at.desc())
        
        result = await db.execute(stmt)
        quests = result.scalars().all()
        
        quest_data = []
        total_xp_available = 0
        
        for quest in quests:
            # Extract rewards and XP from metadata
            metadata = json.loads(quest.quest_metadata) if quest.quest_metadata else {}
            rewards = metadata.get("rewards", {})
            
            xp_reward = rewards.get("points", quest.target_value * 10)  # Default XP calculation
            points_reward = rewards.get("points", quest.target_value * 5)
            badges = rewards.get("badges", [])
            difficulty = metadata.get("difficulty", "medium")
            
            total_xp_available += xp_reward
            
            quest_data.append({
                "id": quest.id,
                "title": quest.title,
                "description": quest.description,
                "quest_type": quest.quest_type.value,
                "status": quest.status.value,
                "team_name": quest.team.name,
                "team_id": quest.team.id,
                "user_id": quest.user_id,
                "target_metric": quest.target_metric,
                "target_value": quest.target_value,
                "current_progress": quest.current_progress,
                "xp_reward": xp_reward,
                "points_reward": points_reward,
                "badges": badges,
                "difficulty": difficulty,
                "created_at": quest.created_at.isoformat(),
                "metadata": metadata
            })
            
        return {
            "quests": quest_data,
            "total": len(quest_data),
            "total_xp_available": total_xp_available,
            "filters": {
                "status": status,
                "quest_type": quest_type,
                "team_id": team_id
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        total_xp_available = 0
        
        for quest in quests:
            # Extract rewards and XP from metadata
            metadata = json.loads(quest.quest_metadata) if quest.quest_metadata else {}
            rewards = metadata.get("rewards", {})
            
            xp_reward = rewards.get("points", quest.target_value * 10)  # Default XP calculation
            points_reward = rewards.get("points", quest.target_value * 5)
            badges = rewards.get("badges", [])
            difficulty = metadata.get("difficulty", "medium")
            
            total_xp_available += xp_reward
            
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
                "xp_reward": xp_reward,
                "points_reward": points_reward,
                "badges": badges,
                "difficulty": difficulty,
                "metadata": metadata
            })
            
        return {
            "user_id": user_id,
            "quests": quest_data,
            "total": len(quest_data),
            "total_xp_available": total_xp_available
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




class QuestGenerationRequest(BaseModel):
    home_team: str
    away_team: str
    event_title: str
    event_date: str
    sport: str = "football"
    league: Optional[str] = None
    event_id: Optional[int] = None


@router.get("/test/individual")
async def test_individual_agent(db: AsyncSession = Depends(get_db)):
    """Test individual quest agent"""
    try:
        from ...ai_agents.individual_quest_agent import individual_quest_agent
        from agents import Runner
        
        prompt = "Create a social quest for team_id: 1, team_name: PSG, quest_type: social"
        
        run_result = await Runner.run(individual_quest_agent, input=prompt)
        
        if hasattr(run_result, 'final_output') and run_result.final_output:
            result_data = run_result.final_output.model_dump()
        else:
            result_data = {"message": "No final output available", "raw_result": str(run_result)}
            
        return {"success": True, "result": result_data}
        
    except Exception as e:
        import traceback
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


@router.get("/test/clash")
async def test_clash_agent(db: AsyncSession = Depends(get_db)):
    """Test clash quest agent"""
    try:
        from ...ai_agents.clash_quest_agent import clash_quest_agent
        from agents import Runner
        
        prompt = "Create clash battle: home_team_id: 1, home_team_name: PSG, away_team_id: 2, away_team_name: Real Madrid, match_date: 2025-07-20T20:00:00Z"
        
        run_result = await Runner.run(clash_quest_agent, input=prompt)
        
        if hasattr(run_result, 'final_output') and run_result.final_output:
            result_data = run_result.final_output.model_dump()
        else:
            result_data = {"message": "No final output available", "raw_result": str(run_result)}
            
        return {"success": True, "result": result_data}
        
    except Exception as e:
        import traceback
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


@router.get("/test/collective")
async def test_collective_agent(db: AsyncSession = Depends(get_db)):
    """Test collective quest agent"""
    try:
        from ...ai_agents.collective_quest_agent import collective_quest_agent
        from agents import Runner
        
        prompt = "Create community quest: participating_team_ids: [1,2,3], participating_team_names: [PSG,Real Madrid,Barcelona], event_title: Champions League Final, event_significance: final"
        
        run_result = await Runner.run(collective_quest_agent, input=prompt)
        
        if hasattr(run_result, 'final_output') and run_result.final_output:
            result_data = run_result.final_output.model_dump()
        else:
            result_data = {"message": "No final output available", "raw_result": str(run_result)}
            
        return {"success": True, "result": result_data}
        
    except Exception as e:
        import traceback
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


@router.get("/test/orchestrator")
async def test_orchestrator_agent(db: AsyncSession = Depends(get_db)):
    """Test quest orchestrator agent"""
    try:
        from ...ai_agents.quest_orchestrator_agent import quest_orchestrator_agent
        from agents import Runner
        
        prompt = "Plan quest generation: available_teams: [PSG,Real Madrid,Barcelona,Manchester United,Bayern Munich], upcoming_matches: [PSG vs Real Madrid, Barcelona vs Bayern Munich], event_significance: important"
        
        run_result = await Runner.run(quest_orchestrator_agent, input=prompt)
        
        if hasattr(run_result, 'final_output') and run_result.final_output:
            result_data = run_result.final_output.model_dump()
        else:
            result_data = {"message": "No final output available", "raw_result": str(run_result)}
            
        return {"success": True, "result": result_data}
        
    except Exception as e:
        import traceback
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


@router.get("/generate/all")
async def generate_all_quests(db: AsyncSession = Depends(get_db)):
    """Generate multiple quests for all active teams with Individual, Clash, and Collective types"""
    try:
        from ...tools.database_tools import get_all_active_teams
        
        # Get all active teams first
        all_teams = await get_all_active_teams()
        
        if not all_teams:
            return {
                "success": False,
                "message": "No active teams found",
                "total_quests_created": 0
            }
        
        return {
            "success": True,
            "total_teams_found": len(all_teams),
            "teams": all_teams,
            "message": "Found teams, agents disabled for testing"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate")
async def generate_quest(
    request: QuestGenerationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate quests based on event data using quest generator agent"""
    try:
        # Import quest generator agent and runner
        from ...ai_agents.quest_generator import quest_generator_agent
        from ...tools.database_tools import check_team_exists
        from agents import Runner
        
        # Check team existence BEFORE running the agent
        home_team_result = await check_team_exists(request.home_team)
        away_team_result = await check_team_exists(request.away_team)
        
        home_exists = home_team_result["exists"]
        away_exists = away_team_result["exists"]
        
        # Determine strategy based on team existence
        if not home_exists and not away_exists:
            return {
                "event_title": request.event_title,
                "teams": f"{request.home_team} vs {request.away_team}",
                "result": {
                    "success": False,
                    "strategy": "Check if home and away teams exist for quest generation.",
                    "event_title": request.event_title,
                    "teams_found": {
                        "home": False,
                        "away": False
                    },
                    "individual_quests": [],
                    "clash_quests": [],
                    "collective_quests": [],
                    "total_quests_created": 0,
                    "message": "Neither home nor away team has been found. Unable to create any quests."
                },
                "status": "quest_generation_completed"
            }
        
        # Prepare event data for the agent with only existing teams
        strategy = "both_teams" if home_exists and away_exists else ("home_only" if home_exists else "away_only")
        
        event_prompt = f"""
        Generate quests for this sports event with strategy: {strategy}
        - Event: {request.event_title}
        - Home Team: {request.home_team} (exists: {home_exists}, id: {home_team_result.get('team_id', 'N/A')})
        - Away Team: {request.away_team} (exists: {away_exists}, id: {away_team_result.get('team_id', 'N/A')})
        - Date: {request.event_date}
        - Sport: {request.sport}
        - League: {request.league or 'N/A'}
        - Event ID: {request.event_id}
        
        Create quests only for existing teams. Use the provided team IDs.
        Return a structured QuestGenerationResult with strategy: {strategy}.
        """
        
        # Run quest generator agent
        run_result = await Runner.run(
            quest_generator_agent,
            input=event_prompt
        )
        
        # Extract the final result from RunResult
        if hasattr(run_result, 'final_output'):
            agent_output = run_result.final_output
        else:
            agent_output = run_result
        
        # Convert result to dict if it's a Pydantic model
        if hasattr(agent_output, 'model_dump'):
            result_data = agent_output.model_dump()
        elif hasattr(agent_output, 'dict'):
            result_data = agent_output.dict()
        else:
            result_data = {"message": str(agent_output)}
        
        return {
            "event_title": request.event_title,
            "teams": f"{request.home_team} vs {request.away_team}",
            "result": result_data,
            "status": "quest_generation_completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


