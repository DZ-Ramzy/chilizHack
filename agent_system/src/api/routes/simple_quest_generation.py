"""
Ultra-Simple Quest Generation - Direct database writes
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ...models.database import get_db
from ...tools.database_tools import create_quest, get_all_active_teams
from loguru import logger

router = APIRouter()


@router.get("/ultra-simple")
async def ultra_simple_quest_generation(db: AsyncSession = Depends(get_db)):
    """Ultra-simple direct quest creation"""
    try:
        logger.info("🚀 Starting ULTRA-SIMPLE quest generation...")
        
        # Get teams
        all_teams = await get_all_active_teams()
        if not all_teams:
            return {"success": False, "message": "No teams found"}
        
        created_quests = []
        
        # Create 2 individual quests per team
        for team in all_teams:
            try:
                # Quest 1
                quest_id_1 = await create_quest(
                    title=f"📱 {team['name']} Fan Challenge",
                    description=f"Connect with fellow {team['name']} supporters! Share team content and engage with the community.",
                    quest_type="individual",
                    team_id=team['id'],
                    target_metric="fan_engagement",
                    target_value=3
                )
                created_quests.append(f"Individual {team['name']} Quest 1: ID {quest_id_1}")
                
                # Quest 2  
                quest_id_2 = await create_quest(
                    title=f"📰 {team['name']} News Sharer",
                    description=f"Share the latest {team['name']} updates and news with fellow fans across social platforms.",
                    quest_type="individual", 
                    team_id=team['id'],
                    target_metric="content_sharing",
                    target_value=5
                )
                created_quests.append(f"Individual {team['name']} Quest 2: ID {quest_id_2}")
                
                logger.success(f"✅ Created 2 individual quests for {team['name']}")
                
            except Exception as e:
                logger.error(f"❌ Error creating quests for {team['name']}: {e}")
        
        # Create 1 collective quest
        try:
            collective_id = await create_quest(
                title="🌟 Global Football Unity",
                description="Unite football fans worldwide! Celebrate the beautiful game together regardless of team allegiance.",
                quest_type="collective",
                team_id=1,  # Assign to first team
                target_metric="unity_actions", 
                target_value=20
            )
            created_quests.append(f"Collective Quest: ID {collective_id}")
            logger.success(f"✅ Created collective quest")
            
        except Exception as e:
            logger.error(f"❌ Error creating collective quest: {e}")
        
        logger.success(f"🎉 ULTRA-SIMPLE generation complete: {len(created_quests)} quests created")
        
        return {
            "success": True,
            "approach": "ultra_simple_direct",
            "total_teams": len(all_teams),
            "total_quests_created": len(created_quests),
            "created_quests": created_quests,
            "message": f"Successfully created {len(created_quests)} quests directly"
        }
        
    except Exception as e:
        logger.error(f"❌ Ultra-simple generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-create") 
async def test_create_single_quest(db: AsyncSession = Depends(get_db)):
    """Test creating a single quest"""
    try:
        quest_id = await create_quest(
            title="🧪 Test Quest",
            description="This is a test quest to verify creation works.",
            quest_type="individual",
            team_id=1,
            target_metric="test_metric",
            target_value=1
        )
        
        return {
            "success": True,
            "quest_id": quest_id,
            "message": f"Test quest created with ID: {quest_id}"
        }
        
    except Exception as e:
        logger.error(f"❌ Test quest creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))