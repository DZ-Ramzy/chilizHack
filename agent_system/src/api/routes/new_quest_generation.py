"""
New Simple Quest Generation API
Logique simple : Fetch content → Generate quests → Save to DB
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ...models.database import get_db
from ...tools.database_tools import get_all_active_teams
from loguru import logger

router = APIRouter()


@router.get("/individual")
async def generate_individual_quests(db: AsyncSession = Depends(get_db)):
    """Generate individual quests using simple approach"""
    try:
        from ...ai_agents.individual_quest_generator import (
            fetch_team_news, generate_individual_quests, save_individual_quests
        )
        
        # Get all teams
        all_teams = await get_all_active_teams()
        if not all_teams:
            return {"success": False, "message": "No teams found"}
        
        logger.info(f"🚀 Starting INDIVIDUAL quest generation for {len(all_teams)} teams...")
        
        results = []
        total_quests_created = 0
        
        for team in all_teams:
            try:
                logger.info(f"📝 Processing {team['name']}...")
                
                # Step 1: Fetch news
                news_content = await fetch_team_news(team['name'])
                
                # Step 2: Generate quests
                quests = await generate_individual_quests(team['name'], news_content)
                
                # Step 3: Save to database
                if quests:
                    save_result = await save_individual_quests(team['id'], team['name'], quests)
                    
                    results.append({
                        "team": team['name'],
                        "quests_generated": len(quests),
                        "save_result": save_result,
                        "status": "success"
                    })
                    total_quests_created += len(quests)
                    
                    logger.success(f"✅ {team['name']}: {len(quests)} quests created")
                else:
                    results.append({
                        "team": team['name'],
                        "quests_generated": 0,
                        "save_result": "No quests generated",
                        "status": "skipped"
                    })
                    logger.warning(f"⚠️ {team['name']}: No quests generated")
                
            except Exception as e:
                logger.error(f"❌ Error processing {team['name']}: {e}")
                results.append({
                    "team": team['name'],
                    "quests_generated": 0,
                    "save_result": f"Error: {str(e)}",
                    "status": "error"
                })
        
        logger.success(f"🎉 INDIVIDUAL quest generation complete: {total_quests_created} total quests")
        
        return {
            "success": True,
            "approach": "simple_individual_generation",
            "total_teams": len(all_teams),
            "total_quests_created": total_quests_created,
            "results": results,
            "message": f"Generated {total_quests_created} individual quests for {len(all_teams)} teams"
        }
        
    except Exception as e:
        logger.error(f"❌ Individual quest generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-individual/{team_name}")
async def test_individual_for_team(team_name: str, db: AsyncSession = Depends(get_db)):
    """Test individual quest generation for a specific team"""
    try:
        from ...ai_agents.individual_quest_generator import (
            fetch_team_news, generate_individual_quests
        )
        
        logger.info(f"🧪 Testing individual quest generation for {team_name}")
        
        # Fetch news
        news_content = await fetch_team_news(team_name)
        
        # Generate quests (without saving)
        quests = await generate_individual_quests(team_name, news_content)
        
        return {
            "success": True,
            "team": team_name,
            "news_content_length": len(news_content),
            "news_preview": news_content[:200] + "..." if len(news_content) > 200 else news_content,
            "quests_generated": len(quests),
            "quests": [quest.model_dump() for quest in quests],
            "message": f"Generated {len(quests)} quests for {team_name}"
        }
        
    except Exception as e:
        logger.error(f"❌ Test error for {team_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clash")
async def generate_clash_quests(db: AsyncSession = Depends(get_db)):
    """Generate clash quests between team pairs"""
    try:
        from ...ai_agents.clash_quest_generator import (
            search_team_match, generate_clash_quests as generate_clash_quests_func, save_clash_quests
        )
        
        # Get all teams
        all_teams = await get_all_active_teams()
        if not all_teams or len(all_teams) < 2:
            return {"success": False, "message": "Need at least 2 teams for clash quests"}
        
        logger.info(f"⚔️ Starting CLASH quest generation for {len(all_teams)} teams...")
        
        results = []
        total_clash_quests_created = 0
        
        # Create ALL possible team pairs for clash quests
        from itertools import combinations
        team_pairs = list(combinations(all_teams, 2))
        
        for team_a, team_b in team_pairs:
            try:
                logger.info(f"⚔️ Processing clash: {team_a['name']} vs {team_b['name']}")
                
                # Step 1: Search for match info and check if match exists
                match_content, match_exists = await search_team_match(team_a['name'], team_b['name'])
                
                if not match_exists:
                    results.append({
                        "clash": f"{team_a['name']} vs {team_b['name']}",
                        "team_a_quests": 0,
                        "team_b_quests": 0,
                        "total_quests": 0,
                        "save_result": "No real match found between teams",
                        "status": "no_match"
                    })
                    logger.info(f"🚫 {team_a['name']} vs {team_b['name']}: No real match exists, skipping clash quest")
                    continue
                
                # Step 2: Generate clash quests only if match exists
                team_a_quests, team_b_quests = await generate_clash_quests_func(
                    team_a['name'], team_b['name'], match_content
                )
                
                # Step 3: Save to database
                if team_a_quests or team_b_quests:
                    save_result = await save_clash_quests(
                        team_a['id'], team_b['id'], 
                        team_a['name'], team_b['name'],
                        team_a_quests, team_b_quests
                    )
                    
                    total_quests = len(team_a_quests) + len(team_b_quests)
                    total_clash_quests_created += total_quests
                    
                    results.append({
                        "clash": f"{team_a['name']} vs {team_b['name']}",
                        "team_a_quests": len(team_a_quests),
                        "team_b_quests": len(team_b_quests),
                        "total_quests": total_quests,
                        "save_result": save_result,
                        "status": "success"
                    })
                    
                    logger.success(f"✅ {team_a['name']} vs {team_b['name']}: {total_quests} clash quests created")
                else:
                    results.append({
                        "clash": f"{team_a['name']} vs {team_b['name']}",
                        "team_a_quests": 0,
                        "team_b_quests": 0,
                        "total_quests": 0,
                        "save_result": "No clash quests generated",
                        "status": "skipped"
                    })
                    logger.warning(f"⚠️ {team_a['name']} vs {team_b['name']}: No clash quests generated")
            
            except Exception as e:
                logger.error(f"❌ Error processing clash {team_a['name']} vs {team_b['name']}: {e}")
                results.append({
                    "clash": f"{team_a['name']} vs {team_b['name']}",
                    "team_a_quests": 0,
                    "team_b_quests": 0,
                    "total_quests": 0,
                    "save_result": f"Error: {str(e)}",
                    "status": "error"
                })
        
        logger.success(f"🎉 CLASH quest generation complete: {total_clash_quests_created} total clash quests")
        
        return {
            "success": True,
            "approach": "clash_quest_generation",
            "total_teams": len(all_teams),
            "total_clash_pairs": len(results),
            "total_clash_quests_created": total_clash_quests_created,
            "results": results,
            "message": f"Generated {total_clash_quests_created} clash quests for {len(results)} team pairs"
        }
        
    except Exception as e:
        logger.error(f"❌ Clash quest generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-clash/{team_a}/{team_b}")
async def test_clash_for_teams(team_a: str, team_b: str, db: AsyncSession = Depends(get_db)):
    """Test clash quest generation for specific teams"""
    try:
        from ...ai_agents.clash_quest_generator import (
            search_team_match, generate_clash_quests as generate_clash_quests_func
        )
        
        logger.info(f"🧪 Testing clash quest generation for {team_a} vs {team_b}")
        
        # Search for match info and check if match exists
        match_content, match_exists = await search_team_match(team_a, team_b)
        
        if not match_exists:
            return {
                "success": False,
                "team_a": team_a,
                "team_b": team_b,
                "match_content_length": len(match_content),
                "match_preview": match_content[:200] + "..." if len(match_content) > 200 else match_content,
                "team_a_quests": 0,
                "team_b_quests": 0,
                "total_quests": 0,
                "quests": {"team_a": [], "team_b": []},
                "message": f"No real match found between {team_a} and {team_b}, no clash quest generated"
            }
        
        # Generate clash quests only if match exists
        team_a_quests, team_b_quests = await generate_clash_quests_func(team_a, team_b, match_content)
        
        return {
            "success": True,
            "team_a": team_a,
            "team_b": team_b,
            "match_content_length": len(match_content),
            "match_preview": match_content[:200] + "..." if len(match_content) > 200 else match_content,
            "team_a_quests": len(team_a_quests),
            "team_b_quests": len(team_b_quests),
            "total_quests": len(team_a_quests) + len(team_b_quests),
            "quests": {
                "team_a": [quest.model_dump() for quest in team_a_quests],
                "team_b": [quest.model_dump() for quest in team_b_quests]
            },
            "message": f"Generated {len(team_a_quests)} quests for {team_a} and {len(team_b_quests)} quests for {team_b}"
        }
        
    except Exception as e:
        logger.error(f"❌ Test clash error for {team_a} vs {team_b}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collective")
async def generate_collective_quest(db: AsyncSession = Depends(get_db)):
    """Generate one community quest based on global football events"""
    try:
        from ...ai_agents.collective_quest_generator import (
            search_global_football_events, generate_community_quest, save_community_quest
        )
        
        logger.info(f"🌍 Starting COLLECTIVE quest generation...")
        
        # Step 1: Search for global football events
        events_content, events_found = await search_global_football_events()
        
        if not events_found:
            return {
                "success": False,
                "message": "No major global football events found for community quest",
                "events_content_length": len(events_content),
                "events_preview": events_content[:200] + "..." if len(events_content) > 200 else events_content
            }
        
        # Step 2: Generate community quest
        community_quest = await generate_community_quest(events_content)
        
        if not community_quest:
            return {
                "success": False,
                "message": "Failed to generate community quest",
                "events_content_length": len(events_content)
            }
        
        # Step 3: Save to database
        save_result = await save_community_quest(community_quest)
        
        logger.success(f"🎉 COLLECTIVE quest generation complete")
        
        return {
            "success": True,
            "approach": "collective_quest_generation",
            "events_content_length": len(events_content),
            "events_preview": events_content[:200] + "..." if len(events_content) > 200 else events_content,
            "quest": {
                "title": community_quest.title,
                "description": community_quest.description,
                "target_value": community_quest.target_value,
                "difficulty": community_quest.difficulty,
                "event_context": community_quest.event_context
            },
            "save_result": save_result,
            "message": f"Generated 1 community quest: {community_quest.title}"
        }
        
    except Exception as e:
        logger.error(f"❌ Collective quest generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-collective")
async def test_collective_generation(db: AsyncSession = Depends(get_db)):
    """Test community quest generation without saving"""
    try:
        from ...ai_agents.collective_quest_generator import (
            search_global_football_events, generate_community_quest
        )
        
        logger.info(f"🧪 Testing collective quest generation")
        
        # Search for global events
        events_content, events_found = await search_global_football_events()
        
        # Generate quest (without saving)
        community_quest = None
        if events_found:
            community_quest = await generate_community_quest(events_content)
        
        return {
            "success": True,
            "events_found": events_found,
            "events_content_length": len(events_content),
            "events_preview": events_content[:300] + "..." if len(events_content) > 300 else events_content,
            "quest_generated": community_quest is not None,
            "quest": community_quest.model_dump() if community_quest else None,
            "message": f"Test complete - Events found: {events_found}, Quest generated: {community_quest is not None}"
        }
        
    except Exception as e:
        logger.error(f"❌ Test collective error: {e}")
        raise HTTPException(status_code=500, detail=str(e))