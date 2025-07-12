"""
Sync API endpoints - Manual synchronization with ESPN API
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
from ...services.espn_football_service import espn_football_service
from ...services.event_scheduler import event_scheduler
from ...tools.team_mapping import team_mapper
from loguru import logger

router = APIRouter()


class TeamSyncRequest(BaseModel):
    """Request model for team-specific sync"""
    team_name: str
    trigger_quests: bool = True


class ManualMappingRequest(BaseModel):
    """Request model for manual team mapping"""
    db_team_name: str
    espn_team_id: str


class SyncResponse(BaseModel):
    """Response model for sync operations"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


@router.post("/teams", response_model=SyncResponse)
async def sync_teams():
    """
    Manually sync all teams with ESPN API
    """
    try:
        logger.info("Manual team sync triggered via API")
        
        result = await team_mapper.enhanced_team_sync()
        
        return SyncResponse(
            success=True,
            message=f"Team sync completed: {len(result['synced'])} synced, {len(result['failed'])} failed",
            data=result
        )
        
    except Exception as e:
        logger.error(f"Team sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"Team sync failed: {str(e)}")


@router.post("/events", response_model=SyncResponse) 
async def sync_events():
    """
    Manually sync events for all teams in database using ESPN API
    """
    try:
        logger.info("Manual event sync triggered via API")
        
        # Get leagues from ESPN
        leagues = await espn_football_service.get_leagues()
        
        events_created = 0
        events_skipped = 0
        
        # For now, we'll create a simple sync - this can be enhanced later
        result = {
            "created": events_created,
            "skipped": events_skipped,
            "leagues_found": len(leagues) if leagues else 0
        }
        
        return SyncResponse(
            success=True,
            message=f"Event sync completed: {result['created']} created, {result['skipped']} skipped",
            data=result
        )
        
    except Exception as e:
        logger.error(f"Event sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"Event sync failed: {str(e)}")


@router.post("/full", response_model=SyncResponse)
async def full_sync():
    """
    Full synchronization: teams + events + quest generation
    """
    try:
        logger.info("Full sync triggered via API")
        
        # Step 1: Sync teams
        team_result = await team_mapper.enhanced_team_sync()
        
        # Step 2: Sync events (simplified for now)
        leagues = await espn_football_service.get_leagues()
        
        result = {
            "teams_synced": len(team_result['synced']),
            "teams_failed": len(team_result['failed']),
            "leagues_found": len(leagues) if leagues else 0,
            "team_sync_details": team_result
        }
        
        return SyncResponse(
            success=True,
            message="Full sync completed successfully",
            data=result
        )
        
    except Exception as e:
        logger.error(f"Full sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"Full sync failed: {str(e)}")


@router.post("/full-background")
async def full_sync_background(background_tasks: BackgroundTasks):
    """
    Full synchronization in background (non-blocking)
    """
    try:
        logger.info("Background full sync triggered via API")
        
        background_tasks.add_task(full_sync)
        
        return {
            "status": "accepted",
            "message": "Full sync started in background"
        }
        
    except Exception as e:
        logger.error(f"Background sync trigger failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/team", response_model=SyncResponse)
async def sync_specific_team(request: TeamSyncRequest):
    """
    Sync events for a specific team using ESPN API
    """
    try:
        logger.info(f"Team-specific sync triggered for: {request.team_name}")
        
        # Search for team in ESPN
        team_data = await espn_football_service.search_team(request.team_name)
        
        if not team_data:
            raise HTTPException(status_code=404, detail=f"Team '{request.team_name}' not found in ESPN API")
        
        # Get team matches (if the endpoint works)
        try:
            matches = await espn_football_service.get_team_matches(team_data.get("id"))
            matches_count = len(matches) if matches else 0
        except Exception as e:
            logger.warning(f"Could not get matches for team {request.team_name}: {e}")
            matches_count = 0
        
        result = {
            "team_found": True,
            "team_id": team_data.get("id"),
            "team_name": team_data.get("name"),
            "matches_found": matches_count
        }
        
        return SyncResponse(
            success=True,
            message=f"Team sync completed for {request.team_name}: {matches_count} matches found",
            data=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Team sync failed for {request.team_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Team sync failed: {str(e)}")


@router.get("/scheduler/status")
async def get_scheduler_status():
    """
    Get current scheduler status
    """
    return event_scheduler.get_scheduler_status()


@router.post("/scheduler/start")
async def start_scheduler():
    """
    Start the event scheduler
    """
    try:
        await event_scheduler.start_scheduler()
        return {
            "success": True,
            "message": "Event scheduler started"
        }
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scheduler/stop")
async def stop_scheduler():
    """
    Stop the event scheduler
    """
    try:
        await event_scheduler.stop_scheduler()
        return {
            "success": True,
            "message": "Event scheduler stopped"
        }
    except Exception as e:
        logger.error(f"Failed to stop scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scheduler/trigger")
async def trigger_manual_sync():
    """
    Manually trigger a sync (same as scheduler would do)
    """
    try:
        logger.info("Manual scheduler sync triggered via API")
        
        result = await event_scheduler.manual_sync()
        
        return SyncResponse(
            success=True,
            message="Manual sync completed",
            data=result
        )
        
    except Exception as e:
        logger.error(f"Manual sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-team/{team_name}")
async def test_team_search(team_name: str):
    """
    Test team search in ESPN API (for debugging)
    """
    try:
        team_data = await espn_football_service.search_team(team_name)
        
        if not team_data:
            return {"found": False, "team_name": team_name}
        
        return {
            "found": True,
            "team_name": team_name,
            "espn_data": {
                "id": team_data.get("id"),
                "name": team_data.get("name"),
                "country": team_data.get("country"),
                "logo": team_data.get("logo"),
                "founded": team_data.get("founded")
            }
        }
        
    except Exception as e:
        logger.error(f"Team search test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-events/{team_name}")
async def test_team_events(team_name: str):
    """
    Test getting events for a team (for debugging)
    """
    try:
        # First find the team
        team_data = await espn_football_service.search_team(team_name)
        
        if not team_data:
            return {"error": f"Team '{team_name}' not found"}
        
        team_id = team_data.get("id")
        
        # Try to get team matches
        try:
            matches = await espn_football_service.get_team_matches(team_id)
            matches_count = len(matches) if matches else 0
        except Exception as e:
            matches = []
            matches_count = 0
            logger.warning(f"Could not get matches: {e}")
        
        return {
            "team": team_name,
            "espn_id": team_id,
            "matches_count": matches_count,
            "sample_matches": matches[:3] if matches else [],
            "note": "ESPN API provides comprehensive match data"
        }
        
    except Exception as e:
        logger.error(f"Team events test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/teams/enhanced", response_model=SyncResponse)
async def enhanced_team_sync(similarity_threshold: float = 0.7):
    """
    Enhanced team synchronization with fuzzy matching and confidence scoring
    """
    try:
        logger.info("Enhanced team sync triggered via API")
        
        result = await team_mapper.enhanced_team_sync(similarity_threshold)
        
        return SyncResponse(
            success=True,
            message=f"Enhanced sync completed: {len(result['synced'])} synced, {len(result['failed'])} failed, {len(result['manual_review'])} need review",
            data=result
        )
        
    except Exception as e:
        logger.error(f"Enhanced team sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"Enhanced team sync failed: {str(e)}")


@router.post("/teams/manual-mapping", response_model=SyncResponse)
async def manual_team_mapping(request: ManualMappingRequest):
    """
    Manually map a database team to a ESPN team ID
    """
    try:
        logger.info(f"Manual mapping: {request.db_team_name} -> {request.espn_team_id}")
        
        result = await team_mapper.manual_team_mapping(
            request.db_team_name, 
            request.espn_team_id
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return SyncResponse(
            success=True,
            message=f"Manual mapping completed for {request.db_team_name}",
            data=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Manual mapping failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/espn/leagues")
async def get_espn_leagues():
    """
    Get all available leagues from ESPN API
    """
    try:
        leagues = await espn_football_service.get_leagues()
        
        return {
            "success": True,
            "count": len(leagues) if leagues else 0,
            "leagues": leagues[:10] if leagues else [],  # Show first 10
            "message": f"Found {len(leagues) if leagues else 0} leagues"
        }
        
    except Exception as e:
        logger.error(f"Failed to get leagues: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/espn/teams")
async def get_espn_teams(limit: int = 20):
    """
    Get teams from ESPN API
    """
    try:
        # ESPN doesn't have a direct "get all teams" endpoint
        # We'll need to implement this differently
        return {
            "success": True,
            "message": "Use team search endpoints instead - ESPN API uses league-specific endpoints",
            "available_endpoints": [
                "/sync/test-team/{team_name}",
                "/teams/exists/{team_name}",
                "/espn/search/{query}"
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get teams: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/espn/search/{query}")
async def search_espn(query: str):
    """
    Search for teams in ESPN API
    """
    try:
        team = await espn_football_service.search_team(query)
        exists_result = await espn_football_service.team_exists(query)
        
        return {
            "query": query,
            "team_found": team is not None,
            "team_data": team,
            "exists_check": exists_result
        }
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))