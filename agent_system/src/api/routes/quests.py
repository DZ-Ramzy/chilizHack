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
from loguru import logger

router = APIRouter()

# Include ultra-simple generation
from .simple_quest_generation import router as simple_router


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
                "team_name": quest.team.name if quest.team else "Unknown Team",
                "team_id": quest.team.id if quest.team else quest.team_id,
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
                "team_name": quest.team.name if quest.team else "Unknown Team",
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


@router.get("/test/research")
async def test_research_orchestrator(db: AsyncSession = Depends(get_db)):
    """Test football research orchestrator with sub-agents"""
    try:
        from ...ai_agents.research_sub_agents import football_research_orchestrator
        from agents import Runner
        
        prompt = "Research current football news, player updates, and match schedules for quest inspiration"
        
        run_result = await Runner.run(football_research_orchestrator, input=prompt)
        
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


@router.delete("/purge")
async def purge_all_quests(db: AsyncSession = Depends(get_db)):
    """Purge all existing quests from database"""
    try:
        from sqlalchemy import delete
        
        # Delete all quests
        stmt = delete(Quest)
        result = await db.execute(stmt)
        await db.commit()
        
        return {
            "success": True,
            "message": f"Purged {result.rowcount} quests from database",
            "deleted_count": result.rowcount
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/generate/simple")
async def generate_simple_quests(db: AsyncSession = Depends(get_db)):
    """Generate quests using simple direct approach"""
    try:
        from ...tools.database_tools import get_all_active_teams
        from ...ai_agents.simple_quest_system import (
            fetch_team_news, create_individual_quests,
            fetch_match_news, create_clash_quest, 
            create_collective_quest
        )
        
        # Get all active teams
        all_teams = await get_all_active_teams()
        if not all_teams:
            return {"success": False, "message": "No active teams found"}
        
        logger.info(f"🚀 Starting SIMPLE quest generation for {len(all_teams)} teams...")
        
        created_quests = {
            "individual": [],
            "clash": [], 
            "collective": []
        }
        
        # 1. INDIVIDUAL QUESTS - Direct approach
        logger.info(f"📝 Creating individual quests...")
        for team in all_teams:
            try:
                # Fetch news directly
                news_content = await fetch_team_news(team['name'])
                
                # Create quests directly 
                result = await create_individual_quests(team['id'], team['name'], news_content)
                
                created_quests["individual"].append({
                    "team": team['name'],
                    "result": result
                })
                logger.success(f"✅ Individual quests for {team['name']}: {result}")
                
            except Exception as e:
                logger.error(f"❌ Error for {team['name']}: {e}")
        
        # 2. CLASH QUESTS - Check team pairs
        logger.info(f"⚔️ Checking clash quests...")
        clash_count = 0
        for i, team1 in enumerate(all_teams):
            for team2 in all_teams[i+1:]:
                try:
                    # Fetch match-specific news
                    match_content = await fetch_match_news(team1['name'], team2['name'])
                    
                    # Create clash quest if match exists
                    result = await create_clash_quest(
                        team1['id'], team1['name'], 
                        team2['id'], team2['name'], 
                        match_content
                    )
                    
                    if result.startswith("SUCCESS"):
                        created_quests["clash"].append({
                            "teams": f"{team1['name']} vs {team2['name']}",
                            "result": result
                        })
                        clash_count += 1
                        logger.success(f"✅ Clash quest: {team1['name']} vs {team2['name']}")
                    
                except Exception as e:
                    logger.error(f"❌ Clash error {team1['name']} vs {team2['name']}: {e}")
        
        # 3. COLLECTIVE QUEST - Simple and generic
        logger.info(f"🌟 Creating collective quest...")
        try:
            team_names = [team['name'] for team in all_teams]
            result = await create_collective_quest(team_names)
            
            created_quests["collective"].append({
                "teams": "All teams",
                "result": result
            })
            logger.success(f"✅ Collective quest: {result}")
            
        except Exception as e:
            logger.error(f"❌ Collective quest error: {e}")
        
        # Summary
        total_created = len(created_quests["individual"]) + len(created_quests["clash"]) + len(created_quests["collective"])
        
        logger.success(f"🎉 SIMPLE QUEST GENERATION COMPLETED!")
        logger.info(f"   📊 Total: {total_created}")
        logger.info(f"   📝 Individual: {len(created_quests['individual'])}")
        logger.info(f"   ⚔️ Clash: {len(created_quests['clash'])}")
        logger.info(f"   🌟 Collective: {len(created_quests['collective'])}")
        
        return {
            "success": True,
            "architecture": "simple_direct_approach",
            "total_teams": len(all_teams),
            "teams": all_teams,
            "total_quests_created": total_created,
            "created_quests": created_quests,
            "message": f"Successfully generated {total_created} quests using simple direct approach"
        }
        
    except Exception as e:
        logger.error(f"❌ Error in simple quest generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/generate/all")
async def generate_all_quests(db: AsyncSession = Depends(get_db)):
    """Generate all types of quests using new simple architecture"""
    try:
        import asyncio
        from ...tools.database_tools import get_all_active_teams
        
        logger.info(f"🚀 Starting comprehensive quest generation...")
        
        # Import new quest generation endpoints
        from . import new_quest_generation
        
        results = {}
        total_quests_created = 0
        
        # Generate Individual Quests
        logger.info(f"📝 Step 1: Generating Individual Quests...")
        try:
            individual_result = await new_quest_generation.generate_individual_quests(db)
            results["individual"] = individual_result
            if individual_result.get("success"):
                total_quests_created += individual_result.get("total_quests_created", 0)
        except Exception as e:
            logger.error(f"❌ Individual quest generation failed: {e}")
            results["individual"] = {"success": False, "error": str(e)}
        
        # Generate Clash Quests  
        logger.info(f"⚔️ Step 2: Generating Clash Quests...")
        try:
            clash_result = await new_quest_generation.generate_clash_quests(db)
            results["clash"] = clash_result
            if clash_result.get("success"):
                total_quests_created += clash_result.get("total_clash_quests_created", 0)
        except Exception as e:
            logger.error(f"❌ Clash quest generation failed: {e}")
            results["clash"] = {"success": False, "error": str(e)}
        
        # Generate Collective Quest
        logger.info(f"🌍 Step 3: Generating Collective Quest...")
        try:
            collective_result = await new_quest_generation.generate_collective_quest(db)
            results["collective"] = collective_result
            if collective_result.get("success"):
                total_quests_created += 1  # Collective generates 1 quest
        except Exception as e:
            logger.error(f"❌ Collective quest generation failed: {e}")
            results["collective"] = {"success": False, "error": str(e)}
        
        logger.success(f"🎉 Complete quest generation finished: {total_quests_created} total quests created")
        
        return {
            "individual": [],
            "clash": [],
            "collective": []
        }
        
        # Individual Quests (multiple per team based on real events)
        logger.info(f"📝 Generating individual quests for {len(all_teams)} teams...")
        for i, team in enumerate(all_teams, 1):
            try:
                logger.info(f"📝 Individual quests for {team['name']} ({i}/{len(all_teams)})...")
                
                # Filter context for individual quest
                filtered_context = context_triage_agent.filter_for_individual_quest(team_contexts[team['id']])
                
                # Count available events for this team
                team_context = team_contexts[team['id']]
                event_count = len(team_context.news) + len(team_context.player_news) + len(team_context.transfer_updates)
                
                # Force at least 1 quest per team regardless of event count
                quest_attempts = 1  # Create exactly 1 quest per team
                
                team_quests_created = 0
                for quest_num in range(quest_attempts):
                    try:
                        # Use direct function call to ensure database saving
                        from ...ai_agents.simplified_quest_generators import create_individual_quest_with_context
                        
                        result = await create_individual_quest_with_context(
                            team_id=team['id'],
                            team_name=team['name'],
                            filtered_context=filtered_context
                        )
                        
                        if result.startswith("SUCCESS"):
                            parts = result.split("|")
                            quest_data = {
                                "success": True,
                                "quest_id": int(parts[1]),
                                "team_name": team['name'],
                                "title": parts[2],
                                "description": parts[3],
                                "target_value": int(parts[4]),
                                "difficulty": parts[5],
                                "message": f"Individual quest created successfully for {team['name']}"
                            }
                            created_quests["individual"].append({
                                "team": team['name'],
                                "quest_number": quest_num + 1,
                                "event_count": event_count,
                                "result": quest_data
                            })
                            team_quests_created += 1
                            logger.success(f"✅ Individual quest #{quest_num + 1} saved to database for {team['name']} (ID: {parts[1]})")
                        else:
                            logger.warning(f"⚠️ Quest creation skipped for {team['name']}: {result}")
                            
                    except Exception as quest_e:
                        logger.error(f"❌ Error creating individual quest #{quest_num + 1} for {team['name']}: {quest_e}")
                
                logger.info(f"📊 {team['name']}: {team_quests_created} individual quests created from {event_count} events")
                    
            except Exception as e:
                logger.error(f"❌ Error processing individual quests for {team['name']}: {e}")
        
        # Clash Quests (only for teams with upcoming/live matches)
        total_pairs = len(all_teams) * (len(all_teams) - 1) // 2
        logger.info(f"⚔️ Checking for clash quests among {total_pairs} team pairs...")
        
        pair_count = 0
        clash_pairs_found = 0
        
        for i, team1 in enumerate(all_teams):
            for team2 in all_teams[i+1:]:
                pair_count += 1
                try:
                    logger.info(f"⚔️ Checking clash potential: {team1['name']} vs {team2['name']} ({pair_count}/{total_pairs})...")
                    
                    # Filter context for clash quest
                    filtered_context = context_triage_agent.filter_for_clash_quest(
                        team_contexts[team1['id']], 
                        team_contexts[team2['id']]
                    )
                    
                    # Pre-check if there's a real match before generating quest
                    from ...ai_agents.simplified_quest_generators import _parse_clash_context
                    clash_elements = _parse_clash_context(team1['name'], team2['name'], filtered_context)
                    
                    # Only create clash quest if real match detected
                    if clash_elements.get('has_real_match', False):
                        clash_pairs_found += 1
                        logger.info(f"🎯 Real match detected! Creating clash quest for {team1['name']} vs {team2['name']}...")
                        
                        # Use direct function call to ensure database saving
                        from ...ai_agents.simplified_quest_generators import create_clash_quest_with_context
                        
                        result = await create_clash_quest_with_context(
                            home_team_id=team1['id'],
                            home_team_name=team1['name'],
                            away_team_id=team2['id'],
                            away_team_name=team2['name'],
                            filtered_context=filtered_context
                        )
                        
                        if result.startswith("SUCCESS"):
                            parts = result.split("|")
                            quest_data = {
                                "success": True,
                                "home_team_name": team1['name'],
                                "away_team_name": team2['name'],
                                "home_quest_id": int(parts[1]),
                                "away_quest_id": int(parts[2]),
                                "battle_title": parts[3],
                                "target_per_team": int(parts[4]),
                                "message": f"Clash quest created successfully for {team1['name']} vs {team2['name']}"
                            }
                            created_quests["clash"].append({
                                "teams": f"{team1['name']} vs {team2['name']}",
                                "match_info": clash_elements.get('match_info', 'Match detected'),
                                "result": quest_data
                            })
                            logger.success(f"✅ Clash quest saved to database for {team1['name']} vs {team2['name']} (IDs: {parts[1]}, {parts[2]})")
                        else:
                            logger.warning(f"⚠️ Clash quest creation failed for {team1['name']} vs {team2['name']}: {result}")
                    else:
                        logger.info(f"📋 No upcoming/live match found for {team1['name']} vs {team2['name']} - skipping clash quest")
                        
                except Exception as e:
                    logger.error(f"❌ Error processing clash quest for {team1['name']} vs {team2['name']}: {e}")
        
        logger.info(f"🎯 Clash quest summary: {clash_pairs_found} real matches found out of {total_pairs} possible pairs")
        
        # Collective Quest (single quest with global filtered context)
        logger.info(f"🌟 Generating collective quest for all teams...")
        try:
            # Filter context for collective quest
            filtered_context = context_triage_agent.filter_for_collective_quest(team_contexts)
            
            team_names = [team['name'] for team in all_teams]
            
            # Generate collective quest with simplified agent
            result = await Runner.run(
                simplified_collective_agent,
                input=f"Create collective quest for teams {', '.join(team_names)} using this context:\n{filtered_context}"
            )
            
            if hasattr(result, 'final_output') and result.final_output:
                quest_data = result.final_output.model_dump() if hasattr(result.final_output, 'model_dump') else {"message": str(result.final_output)}
                created_quests["collective"].append({
                    "teams": "All teams",
                    "result": quest_data
                })
                logger.success(f"✅ Collective quest created for all teams")
            else:
                logger.warning(f"⚠️ No output for collective quest")
                
        except Exception as e:
            logger.error(f"❌ Error creating collective quest: {e}")
        
        # Final Summary
        total_created = len(created_quests["individual"]) + len(created_quests["clash"]) + len(created_quests["collective"])
        
        logger.success(f"🎉 OPTIMIZED QUEST GENERATION COMPLETED!")
        logger.info(f"   📊 Total quests created: {total_created}")
        logger.info(f"   📝 Individual: {len(created_quests['individual'])}")
        logger.info(f"   ⚔️ Clash: {len(created_quests['clash'])}")
        logger.info(f"   🌟 Collective: {len(created_quests['collective'])}")
        
        # Context data summary (without quality scoring)
        context_summary = {}
        for team_id, context in team_contexts.items():
            team_name = next(team['name'] for team in all_teams if team['id'] == team_id)
            context_summary[team_name] = {
                "data_points": {
                    "news": len(context.news),
                    "results": len(context.recent_results),
                    "transfers": len(context.transfer_updates),
                    "fixtures": len(context.upcoming_matches),
                    "player_news": len(context.player_news),
                    "community": len(context.community_trends)
                }
            }
        
        return {
            "success": True,
            "architecture": "optimized_centralized_research",
            "total_teams_found": len(all_teams),
            "teams": all_teams,
            "total_quests_created": total_created,
            "created_quests": created_quests,
            "context_summary": context_summary,
            "performance_optimization": {
                "research_phase": f"1 search per team ({len(all_teams)} total)",
                "generation_phase": f"{total_created} quests generated without additional searches",
                "estimated_time_saved": f"{total_pairs * 2} search operations eliminated"
            },
            "message": f"Successfully generated {total_created} quests using optimized centralized research architecture"
        }
        
    except Exception as e:
        logger.error(f"❌ Error in optimized quest generation: {e}")
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


