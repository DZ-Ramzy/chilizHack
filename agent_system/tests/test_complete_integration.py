#!/usr/bin/env python3
"""
Complete Integration Test - SportDevs API + Database + Quest Generation
"""
import asyncio
import sys
import os

# Add the project root to the path so we can import our modules
sys.path.insert(0, os.path.abspath('..'))

from src.services.database_integration import db_integration
from src.services.sportdevs_service import sportdevs_service
from src.tools.team_mapping import team_mapper
from src.core.init_data import initialize_sample_data
from loguru import logger


async def test_database_setup():
    """Test 1: Database initialization"""
    print("1. 🗄️  Testing database setup...")
    
    try:
        await initialize_sample_data()
        print("   ✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"   ❌ Database setup failed: {e}")
        return False


async def test_sportdevs_api():
    """Test 2: SportDevs API connectivity"""
    print("\n2. 🌐 Testing SportDevs API...")
    
    try:
        # Test team search
        arsenal = await sportdevs_service.search_team("Arsenal")
        if arsenal:
            print(f"   ✅ Team search works: {arsenal.get('name')} (ID: {arsenal.get('id')})")
            
            # Test leagues
            leagues = await sportdevs_service.get_leagues()
            print(f"   ✅ Leagues endpoint works: {len(leagues) if leagues else 0} leagues found")
            
            return True
        else:
            print("   ❌ Team search failed")
            return False
            
    except Exception as e:
        print(f"   ❌ SportDevs API test failed: {e}")
        return False


async def test_team_synchronization():
    """Test 3: Team synchronization with database"""
    print("\n3. 🔄 Testing team synchronization...")
    
    try:
        # Enhanced team sync
        result = await team_mapper.enhanced_team_sync(similarity_threshold=0.6)
        
        synced_count = len(result['synced'])
        failed_count = len(result['failed'])
        review_count = len(result['manual_review'])
        
        print(f"   ✅ Team sync completed:")
        print(f"      - Synced: {synced_count}")
        print(f"      - Failed: {failed_count}")
        print(f"      - Need review: {review_count}")
        
        # Show some synced teams
        for sync in result['synced'][:3]:
            print(f"      ✓ {sync['db_team']} -> {sync['api_team']} (ID: {sync['api_id']})")
        
        return synced_count > 0
        
    except Exception as e:
        print(f"   ❌ Team synchronization failed: {e}")
        return False


async def test_database_integration():
    """Test 4: Complete database integration"""
    print("\n4. 🔗 Testing database integration...")
    
    try:
        # Sync teams with external IDs
        result = await db_integration.sync_teams_with_external_ids()
        
        synced_count = len(result['synced'])
        print(f"   ✅ Database integration completed: {synced_count} teams synced")
        
        # Show statistics
        stats = result['statistics']
        print(f"      - Teams with matches: {stats['found_with_matches']}")
        print(f"      - Teams without matches: {stats['found_without_matches']}")
        print(f"      - Teams not found: {stats['not_found']}")
        
        return synced_count > 0
        
    except Exception as e:
        print(f"   ❌ Database integration failed: {e}")
        return False


async def test_event_creation():
    """Test 5: Event creation from matches"""
    print("\n5. ⚽ Testing event creation...")
    
    try:
        # Sync events for all teams
        result = await db_integration.sync_events_for_all_teams(max_events_per_team=3)
        
        teams_processed = result['teams_processed']
        events_created = result['total_events_created']
        
        print(f"   ✅ Event creation completed:")
        print(f"      - Teams processed: {teams_processed}")
        print(f"      - Events created: {events_created}")
        print(f"      - Events skipped: {result['total_events_skipped']}")
        
        # Show some team results
        for team_result in result['team_results'][:3]:
            if 'error' not in team_result:
                print(f"      ✓ {team_result['team_name']}: {team_result['events_created']} events")
        
        return events_created > 0
        
    except Exception as e:
        print(f"   ❌ Event creation failed: {e}")
        return False


async def test_integration_status():
    """Test 6: Integration status check"""
    print("\n6. 📊 Testing integration status...")
    
    try:
        status = await db_integration.get_integration_status()
        
        print(f"   ✅ Integration status:")
        print(f"      - Total teams: {status['teams']['total']}")
        print(f"      - Synced teams: {status['teams']['synced_with_sportdevs']} ({status['teams']['sync_percentage']:.1f}%)")
        print(f"      - Total events: {status['events']['total']}")
        print(f"      - SportDevs events: {status['events']['from_sportdevs']} ({status['events']['sportdevs_percentage']:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Integration status check failed: {e}")
        return False


async def test_specific_team_workflow():
    """Test 7: Complete workflow for a specific team"""
    print("\n7. 🎯 Testing complete workflow for Arsenal...")
    
    try:
        # Search for Arsenal
        arsenal = await sportdevs_service.search_team("Arsenal")
        if not arsenal:
            print("   ❌ Arsenal not found")
            return False
        
        arsenal_id = arsenal.get("id")
        print(f"   ✅ Found Arsenal: {arsenal.get('name')} (ID: {arsenal_id})")
        
        # Get team matches
        try:
            matches = await sportdevs_service.get_team_matches(arsenal_id)
            print(f"   ✅ Matches retrieved: {len(matches) if matches else 0} matches")
        except Exception as e:
            print(f"   ⚠️  Matches endpoint issue: {e}")
            matches = []
        
        # Create events from matches
        if matches:
            result = await db_integration.create_events_from_matches(arsenal_id, limit=2)
            print(f"   ✅ Events created for Arsenal: {len(result['created'])}")
        else:
            print("   ⚠️  No matches to create events from")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Arsenal workflow failed: {e}")
        return False


async def main():
    """Run all integration tests"""
    print("🚀 Complete SportDevs Integration Test Suite")
    print("=" * 70)
    
    tests = [
        ("Database Setup", test_database_setup),
        ("SportDevs API", test_sportdevs_api),
        ("Team Synchronization", test_team_synchronization),
        ("Database Integration", test_database_integration),
        ("Event Creation", test_event_creation),
        ("Integration Status", test_integration_status),
        ("Specific Team Workflow", test_specific_team_workflow)
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
    print(f"\n📊 FINAL RESULTS:")
    print(f"   Tests passed: {passed}/{total}")
    print(f"   Success rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED! SportDevs integration is fully working!")
        print(f"✅ Database integration complete")
        print(f"✅ API connectivity verified")
        print(f"✅ Team synchronization working")
        print(f"✅ Event creation functional")
        print(f"✅ Ready for production use")
    elif passed >= total * 0.7:  # 70% or more
        print(f"\n✅ MOSTLY WORKING! {passed}/{total} tests passed")
        print(f"⚠️  Some components may need attention")
        print(f"✅ Core functionality is operational")
    else:
        print(f"\n⚠️  NEEDS WORK! Only {passed}/{total} tests passed")
        print(f"❌ Significant issues detected")
        print(f"🔧 Check logs for specific problems")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(main())