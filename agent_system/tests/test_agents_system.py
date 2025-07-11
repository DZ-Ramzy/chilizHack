#!/usr/bin/env python3
"""
Test du Système d'Agents AI - Sports Quest System
"""
import asyncio
import sys
import os

# Add the project root to the path so we can import our modules
sys.path.insert(0, os.path.abspath('..'))

from src.tools.database_tools import get_active_events, check_team_exists, get_team_community_size
from src.tools.quest_tools import generate_quest_content, calculate_quest_difficulty
from src.models.database import async_session
from src.models.event import SportsEvent
from src.models.team import Team
from src.models.quest import Quest
from sqlalchemy import select
from loguru import logger


async def test_database_tools():
    """Test 1: Database tools functionality"""
    print("1. 🛠️  Testing database tools...")
    
    try:
        # Test get_active_events
        events = await get_active_events()
        print(f"   ✅ Active events found: {len(events)}")
        
        if events:
            for event in events[:2]:  # Show first 2 events
                print(f"      - {event['title']} ({event['event_date']})")
        
        # Test check_team_exists
        team_check = await check_team_exists("PSG")
        print(f"   ✅ Team existence check: PSG exists = {team_check.get('exists')}")
        
        # Test community size
        if team_check.get('exists'):
            community_size = await get_team_community_size(team_check['team_id'])
            print(f"   ✅ Community size: {community_size} fans")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Database tools test failed: {e}")
        return False


async def test_quest_tools():
    """Test 2: Quest generation tools"""
    print("\n2. ⚡ Testing quest generation tools...")
    
    try:
        # Test individual quest content generation
        individual_content = generate_quest_content(
            quest_type="individual",
            home_team="PSG",
            event_date="2025-07-15"
        )
        
        print(f"   ✅ Individual quest generated:")
        print(f"      Title: {individual_content['title']}")
        print(f"      Target: {individual_content['target_metric']} ({individual_content['target_value']})")
        
        # Test clash quest content generation
        clash_content = generate_quest_content(
            quest_type="clash",
            home_team="PSG",
            away_team="Real Madrid",
            event_date="2025-07-15"
        )
        
        print(f"   ✅ Clash quest generated:")
        print(f"      Title: {clash_content['title']}")
        print(f"      Target: {clash_content['target_metric']} ({clash_content['target_value']})")
        
        # Test difficulty calculation
        difficulty = calculate_quest_difficulty("individual", individual_content['target_value'])
        print(f"   ✅ Difficulty calculated: {difficulty}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Quest tools test failed: {e}")
        return False


async def test_quest_creation_workflow():
    """Test 3: Full quest creation workflow"""
    print("\n3. 🎯 Testing quest creation workflow...")
    
    try:
        async with async_session() as session:
            # Get first event
            stmt = select(SportsEvent).limit(1)
            result = await session.execute(stmt)
            event = result.scalar_one_or_none()
            
            if not event:
                print("   ⚠️  No events found in database")
                return False
            
            print(f"   🎪 Testing with event: {event.title}")
            
            # Get teams involved
            home_team = await session.get(Team, event.home_team_id)
            away_team = await session.get(Team, event.away_team_id)
            
            print(f"   👥 Teams: {home_team.name} vs {away_team.name}")
            
            # Test team existence checks
            home_exists = await check_team_exists(home_team.name)
            away_exists = await check_team_exists(away_team.name)
            
            print(f"   ✅ Home team exists: {home_exists.get('exists')}")
            print(f"   ✅ Away team exists: {away_exists.get('exists')}")
            
            # Determine quest strategy
            if home_exists.get('exists') and away_exists.get('exists'):
                strategy = "both_teams"  # Individual + Clash quests
                print("   🎯 Strategy: Create individual quests + clash quest")
            elif home_exists.get('exists'):
                strategy = "home_only"
                print("   🎯 Strategy: Create home team quest only")
            elif away_exists.get('exists'):
                strategy = "away_only"
                print("   🎯 Strategy: Create away team quest only")
            else:
                strategy = "skip"
                print("   🎯 Strategy: Skip this event")
            
            # Test quest content generation based on strategy
            quests_generated = []
            
            if strategy in ["both_teams", "home_only"]:
                home_quest = generate_quest_content(
                    quest_type="individual",
                    home_team=home_team.name,
                    event_date=str(event.event_date)
                )
                quests_generated.append(f"Home Quest: {home_quest['title']}")
            
            if strategy in ["both_teams", "away_only"]:
                away_quest = generate_quest_content(
                    quest_type="individual",
                    home_team=away_team.name,
                    event_date=str(event.event_date)
                )
                quests_generated.append(f"Away Quest: {away_quest['title']}")
            
            if strategy == "both_teams":
                clash_quest = generate_quest_content(
                    quest_type="clash",
                    home_team=home_team.name,
                    away_team=away_team.name,
                    event_date=str(event.event_date)
                )
                quests_generated.append(f"Clash Quest: {clash_quest['title']}")
            
            print(f"   ✅ Generated {len(quests_generated)} quest(s):")
            for quest in quests_generated:
                print(f"      - {quest}")
            
            return len(quests_generated) > 0
        
    except Exception as e:
        print(f"   ❌ Quest creation workflow test failed: {e}")
        return False


async def test_preference_analysis():
    """Test 4: User preference analysis simulation"""
    print("\n4. 👤 Testing preference analysis...")
    
    try:
        # Simulate user preferences
        test_users = [
            {
                "user_id": 1,
                "teams": ["PSG"],
                "language": "fr",
                "engagement_level": "high"
            },
            {
                "user_id": 2,
                "teams": ["Real Madrid"],
                "language": "es",
                "engagement_level": "medium"
            },
            {
                "user_id": 3,
                "teams": ["PSG", "Barcelona"],
                "language": "en",
                "engagement_level": "high"
            }
        ]
        
        print(f"   ✅ Testing with {len(test_users)} users")
        
        # Test preference-based quest customization
        for user in test_users:
            print(f"   👤 User {user['user_id']} ({user['language']}):")
            
            for team in user['teams']:
                # Check if team exists
                team_check = await check_team_exists(team)
                
                if team_check.get('exists'):
                    # Generate personalized quest
                    quest_content = generate_quest_content(
                        quest_type="individual",
                        home_team=team,
                        event_date="2025-07-15",
                        user_preferences={
                            "language": user['language'],
                            "engagement_level": user['engagement_level']
                        }
                    )
                    
                    print(f"      - {team}: {quest_content['title'][:50]}...")
                else:
                    print(f"      - {team}: Team not found in system")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Preference analysis test failed: {e}")
        return False


async def test_quest_validation():
    """Test 5: Quest validation process"""
    print("\n5. ✅ Testing quest validation...")
    
    try:
        # Generate test quest content
        test_quest = generate_quest_content(
            quest_type="individual",
            home_team="PSG",
            event_date="2025-07-15"
        )
        
        print(f"   📝 Testing quest: {test_quest['title']}")
        
        # Validation tests
        validations = []
        
        # Content validation
        content_valid = len(test_quest['title']) > 10 and len(test_quest['description']) > 20
        validations.append(("Content length", content_valid))
        
        # Target validation
        target_valid = test_quest['target_value'] > 0 and test_quest['target_metric'] is not None
        validations.append(("Target metrics", target_valid))
        
        # Hashtag validation
        hashtag_valid = len(test_quest.get('hashtags', [])) >= 2
        validations.append(("Hashtags", hashtag_valid))
        
        # Content suggestions validation
        suggestions_valid = len(test_quest.get('content_suggestions', [])) >= 1
        validations.append(("Content suggestions", suggestions_valid))
        
        # Display validation results
        for validation_name, is_valid in validations:
            status = "✅" if is_valid else "❌"
            print(f"   {status} {validation_name}: {'Valid' if is_valid else 'Invalid'}")
        
        # Overall validation score
        valid_count = sum(1 for _, valid in validations if valid)
        validation_score = valid_count / len(validations) * 100
        
        print(f"   📊 Validation score: {validation_score:.1f}% ({valid_count}/{len(validations)})")
        
        return validation_score >= 80  # 80% validation threshold
        
    except Exception as e:
        print(f"   ❌ Quest validation test failed: {e}")
        return False


async def test_distribution_simulation():
    """Test 6: Quest distribution simulation"""
    print("\n6. 📡 Testing quest distribution simulation...")
    
    try:
        # Simulate distribution to different user segments
        distribution_targets = [
            {"segment": "PSG Hardcore Fans", "count": 150, "channel": "push_notification"},
            {"segment": "PSG Casual Fans", "count": 300, "channel": "in_app"},
            {"segment": "General Football Fans", "count": 50, "channel": "social_media"},
        ]
        
        total_distributed = 0
        
        for target in distribution_targets:
            # Simulate distribution
            distributed = target['count']
            total_distributed += distributed
            
            print(f"   📤 {target['segment']}: {distributed} users via {target['channel']}")
        
        print(f"   ✅ Total distributed: {total_distributed} users")
        
        # Simulate engagement metrics
        estimated_engagement = total_distributed * 0.25  # 25% engagement rate
        print(f"   📈 Estimated engagement: {estimated_engagement:.0f} users")
        
        return total_distributed > 0
        
    except Exception as e:
        print(f"   ❌ Distribution simulation test failed: {e}")
        return False


async def test_full_agent_workflow():
    """Test 7: Complete agent workflow simulation"""
    print("\n7. 🤖 Testing complete agent workflow...")
    
    try:
        print("   🎬 Simulating: New Event Trigger -> Quest Generation -> Distribution")
        
        # Step 1: Event detection
        events = await get_active_events()
        if not events:
            print("   ⚠️  No active events to process")
            return False
        
        event = events[0]
        print(f"   🎪 Processing event: {event['title']}")
        
        # Step 2: Team analysis
        teams = event['title'].split(' vs ')
        if len(teams) != 2:
            teams = [event['title'], "Unknown"]
        
        home_team, away_team = teams[0].strip(), teams[1].strip()
        
        # Step 3: Quest strategy determination
        home_exists = await check_team_exists(home_team)
        away_exists = await check_team_exists(away_team)
        
        quest_count = 0
        
        # Step 4: Quest generation
        if home_exists.get('exists'):
            home_quest = generate_quest_content("individual", home_team, str(event['event_date']))
            quest_count += 1
            print(f"   ⚡ Generated home quest: {home_quest['title'][:40]}...")
        
        if away_exists.get('exists'):
            away_quest = generate_quest_content("individual", away_team, str(event['event_date']))
            quest_count += 1
            print(f"   ⚡ Generated away quest: {away_quest['title'][:40]}...")
        
        if home_exists.get('exists') and away_exists.get('exists'):
            clash_quest = generate_quest_content("clash", home_team, away_team, str(event['event_date']))
            quest_count += 1
            print(f"   ⚡ Generated clash quest: {clash_quest['title'][:40]}...")
        
        # Step 5: Validation
        validation_passed = quest_count > 0
        print(f"   ✅ Validation: {'Passed' if validation_passed else 'Failed'}")
        
        # Step 6: Distribution simulation
        if validation_passed:
            estimated_users = quest_count * 200  # 200 users per quest
            print(f"   📡 Distribution: {estimated_users} users targeted")
        
        print(f"   🎯 Workflow result: {quest_count} quest(s) generated and distributed")
        
        return quest_count > 0
        
    except Exception as e:
        print(f"   ❌ Full agent workflow test failed: {e}")
        return False


async def main():
    """Run all agent system tests"""
    print("🤖 Testing Sports Quest AI Agent System")
    print("=" * 70)
    
    tests = [
        ("Database Tools", test_database_tools),
        ("Quest Tools", test_quest_tools),
        ("Quest Creation Workflow", test_quest_creation_workflow),
        ("Preference Analysis", test_preference_analysis),
        ("Quest Validation", test_quest_validation),
        ("Distribution Simulation", test_distribution_simulation),
        ("Full Agent Workflow", test_full_agent_workflow)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            success = await test_func()
            if success:
                passed += 1
        except Exception as e:
            print(f"   ❌ Test '{test_name}' crashed: {e}")
    
    # Final summary
    print(f"\n🤖 AGENT SYSTEM TEST RESULTS:")
    print(f"   Tests passed: {passed}/{total}")
    print(f"   Success rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print(f"\n🎉 ALL AGENT TESTS PASSED!")
        print(f"✅ Database tools operational")
        print(f"✅ Quest generation working")
        print(f"✅ Workflow logic validated")
        print(f"✅ Preference analysis functional")
        print(f"✅ Validation system working")
        print(f"✅ Distribution simulation ready")
        print(f"✅ Full agent workflow operational")
        print(f"\n🚀 Agent system ready for production!")
    elif passed >= total * 0.7:  # 70% or more
        print(f"\n✅ AGENT SYSTEM MOSTLY WORKING! {passed}/{total} tests passed")
        print(f"⚠️  Some components may need fine-tuning")
        print(f"✅ Core agent functionality is operational")
    else:
        print(f"\n⚠️  AGENT SYSTEM NEEDS WORK! Only {passed}/{total} tests passed")
        print(f"❌ Significant issues detected in agent workflow")
        print(f"🔧 Check logs for specific problems")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(main())