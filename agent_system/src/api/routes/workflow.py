"""
Workflow API endpoints - Main agent workflow triggers
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from ...core.workflow_engine import sports_quest_workflow
from loguru import logger

router = APIRouter()


class SportsEventTrigger(BaseModel):
    """Sports event trigger model"""
    event_id: int
    title: str
    home_team: str
    away_team: str
    event_date: str
    sport: str
    league: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ManualQuestRequest(BaseModel):
    """Manual quest creation request"""
    quest_type: str  # individual, clash, collective
    team_id: int
    title: str
    description: str
    target_metric: Optional[str] = "tweets"
    target_value: Optional[int] = 10
    user_id: Optional[int] = None
    event_id: Optional[int] = None


@router.post("/trigger-event")
async def trigger_sports_event(
    event: SportsEventTrigger,
    background_tasks: BackgroundTasks
):
    """
    Trigger the Sports Quest AI workflow for a sports event
    
    This endpoint initiates the complete agent workflow:
    1. Team existence check
    2. User preference analysis  
    3. Quest generation (individual/clash based on team availability)
    4. Parallel validation (content/image/preference)
    5. Quest distribution to communities
    """
    try:
        logger.info(f"Received event trigger: {event.title}")
        
        event_data = {
            "event_id": event.event_id,
            "title": event.title,
            "home_team": {"name": event.home_team},
            "away_team": {"name": event.away_team},
            "event_date": event.event_date,
            "sport": event.sport,
            "league": event.league,
            "metadata": event.metadata or {}
        }
        
        # Process in background to avoid timeout
        background_tasks.add_task(
            sports_quest_workflow.process_sports_event,
            event_data
        )
        
        return {
            "status": "accepted",
            "message": "Sports event processing started",
            "event_id": event.event_id,
            "workflow": "initiated"
        }
        
    except Exception as e:
        logger.error(f"Event trigger failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Workflow initiation failed: {str(e)}")


@router.post("/trigger-event-sync")
async def trigger_sports_event_sync(event: SportsEventTrigger):
    """
    Synchronous version of event trigger (for testing/debugging)
    """
    try:
        event_data = {
            "event_id": event.event_id,
            "title": event.title,
            "home_team": {"name": event.home_team},
            "away_team": {"name": event.away_team},
            "event_date": event.event_date,
            "sport": event.sport,
            "league": event.league,
            "metadata": event.metadata or {}
        }
        
        result = await sports_quest_workflow.process_sports_event(event_data)
        
        return {
            "status": "completed",
            "result": result,
            "event_id": event.event_id
        }
        
    except Exception as e:
        logger.error(f"Sync event processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-manual-quest")
async def create_manual_quest(quest_request: ManualQuestRequest):
    """
    Create a quest manually (bypassing event triggers)
    """
    try:
        quest_data = {
            "type": quest_request.quest_type,
            "team_id": quest_request.team_id,
            "title": quest_request.title,
            "description": quest_request.description,
            "target_metric": quest_request.target_metric,
            "target_value": quest_request.target_value,
            "user_id": quest_request.user_id,
            "event_id": quest_request.event_id
        }
        
        result = await sports_quest_workflow.manual_quest_creation(quest_data)
        
        return {
            "status": "completed",
            "result": result,
            "quest_type": quest_request.quest_type
        }
        
    except Exception as e:
        logger.error(f"Manual quest creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-process-events")
async def batch_process_events(
    events: List[SportsEventTrigger],
    background_tasks: BackgroundTasks
):
    """
    Process multiple sports events in batch
    """
    try:
        logger.info(f"Processing batch of {len(events)} events")
        
        events_data = []
        for event in events:
            event_data = {
                "event_id": event.event_id,
                "title": event.title,
                "home_team": {"name": event.home_team},
                "away_team": {"name": event.away_team},
                "event_date": event.event_date,
                "sport": event.sport,
                "league": event.league,
                "metadata": event.metadata or {}
            }
            events_data.append(event_data)
        
        # Process in background
        background_tasks.add_task(
            sports_quest_workflow.process_multiple_events,
            events_data
        )
        
        return {
            "status": "accepted",
            "message": f"Batch processing of {len(events)} events started",
            "events_count": len(events),
            "workflow": "initiated"
        }
        
    except Exception as e:
        logger.error(f"Batch processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow-status/{event_id}")
async def get_workflow_status(event_id: int):
    """
    Get workflow status for a specific event (placeholder - would need Redis/DB tracking)
    """
    # This would typically query a status tracking system
    return {
        "event_id": event_id,
        "status": "completed",  # placeholder
        "workflow_stages": {
            "team_check": "completed",
            "preference_analysis": "completed", 
            "quest_generation": "completed",
            "validation": "completed",
            "distribution": "completed"
        },
        "message": "Workflow status tracking not yet implemented"
    }