"""
Event Scheduler - Periodic sync of sports events and automatic quest generation
"""
import asyncio
from typing import Dict, Any
from datetime import datetime, timedelta
from loguru import logger
import os
from .sportdevs_service import sportdevs_service


class EventScheduler:
    """Scheduler for periodic event synchronization and quest generation"""
    
    def __init__(self):
        self.sync_interval = int(os.getenv("THESPORTSDB_SYNC_INTERVAL", "300"))  # 5 minutes default
        self.is_running = False
        self.scheduler_task = None
        
    async def start_scheduler(self):
        """Start the periodic event synchronization"""
        if self.is_running:
            logger.warning("Event scheduler is already running")
            return
            
        self.is_running = True
        logger.info(f"Starting event scheduler with {self.sync_interval}s interval")
        
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        
    async def stop_scheduler(self):
        """Stop the periodic event synchronization"""
        if not self.is_running:
            logger.warning("Event scheduler is not running")
            return
            
        self.is_running = False
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
                
        logger.info("Event scheduler stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.is_running:
            try:
                await self._periodic_sync()
                await asyncio.sleep(self.sync_interval)
                
            except asyncio.CancelledError:
                logger.info("Scheduler loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                # Continue running even if one sync fails
                await asyncio.sleep(self.sync_interval)
    
    async def _periodic_sync(self):
        """Perform periodic synchronization"""
        logger.info("Starting periodic event sync...")
        
        try:
            # Full sync: teams + events + quest generation
            # Use SportDevs service instead
            from .database_integration import db_integration
            result = await db_integration.sync_teams_with_external_ids()
            
            logger.info(f"Periodic sync completed - Result: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"Periodic sync failed: {e}")
            raise
    
    async def manual_sync(self) -> Dict[str, Any]:
        """Manually trigger a synchronization"""
        logger.info("Manual sync triggered")
        return await self._periodic_sync()
    
    async def sync_specific_team_events(self, team_name: str) -> Dict[str, Any]:
        """Sync events for a specific team"""
        logger.info(f"Syncing events for team: {team_name}")
        
        try:
            # Search team in SportDevs
            team_data = await sportdevs_service.search_team(team_name)
            if not team_data:
                return {"error": f"Team '{team_name}' not found in SportDevs API"}
            
            # Get team matches
            matches = await sportdevs_service.get_team_matches(team_data.get("id", team_data.get("name", team_name)))
            
            # Create events from matches
            from .database_integration import db_integration
            create_result = await db_integration.create_events_from_matches(matches, team_data)
            
            # Trigger quest generation for new events
            from ..core.workflow_engine import sports_quest_workflow
            
            quest_results = []
            for event_info in create_result["created_events"]:
                try:
                    workflow_event_data = {
                        "event_id": f"thesportsdb_{event_info['thesportsdb_id']}",
                        "title": event_info["title"],
                        "home_team": event_info["title"].split(" vs ")[0],
                        "away_team": event_info["title"].split(" vs ")[1],
                        "event_date": event_info["date"],
                        "sport": "football",
                        "league": event_info["league"]
                    }
                    
                    quest_result = await sports_quest_workflow.process_sports_event(workflow_event_data)
                    quest_results.append(quest_result)
                    
                except Exception as e:
                    logger.error(f"Failed to trigger quest for event {event_info['title']}: {e}")
            
            return {
                "team": team_name,
                "thesportsdb_id": team_id,
                "events_found": len(parsed_events),
                "events_created": create_result["created"],
                "quests_triggered": len(quest_results),
                "created_events": create_result["created_events"]
            }
            
        except Exception as e:
            logger.error(f"Error syncing team events for {team_name}: {e}")
            return {"error": str(e)}
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get current scheduler status"""
        return {
            "is_running": self.is_running,
            "sync_interval_seconds": self.sync_interval,
            "next_sync_in": self.sync_interval if self.is_running else None,
            "last_sync": "Not implemented - would track in Redis/DB"
        }


# Global scheduler instance
event_scheduler = EventScheduler()


# Startup function to be called when the application starts
async def start_event_scheduler():
    """Start the event scheduler when the application starts"""
    if os.getenv("ENABLE_EVENT_SCHEDULER", "true").lower() == "true":
        await event_scheduler.start_scheduler()
        logger.info("Event scheduler started automatically")
    else:
        logger.info("Event scheduler disabled via environment variable")


# Shutdown function to be called when the application stops
async def stop_event_scheduler():
    """Stop the event scheduler when the application stops"""
    await event_scheduler.stop_scheduler()