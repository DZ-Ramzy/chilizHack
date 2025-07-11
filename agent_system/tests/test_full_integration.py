#!/usr/bin/env python3
"""
Test complet de l'intégration SportDevs avec le service mis à jour
"""
import asyncio
import sys
import os

# Add the project root to the path so we can import our modules
sys.path.insert(0, os.path.abspath('..'))

from src.services.sportdevs_service import sportdevs_service


async def test_team_search():
    """Test recherche d'équipes"""
    print("1. 🔍 Testing team search...")
    
    teams_to_test = ["Arsenal", "PSG", "Real Madrid", "Barcelona"]
    
    found_teams = []
    
    for team_name in teams_to_test:
        try:
            team = await sportdevs_service.search_team(team_name)
            if team:
                found_teams.append(team)
                print(f"   ✅ {team_name}: {team.get('name')} (ID: {team.get('id')})")
            else:
                print(f"   ❌ {team_name}: Not found")
        except Exception as e:
            print(f"   ❌ {team_name}: Error - {e}")
    
    return found_teams


async def test_team_matches():
    """Test récupération de matchs pour une équipe"""
    print(f"\n2. ⚽ Testing team matches...")
    
    # Use Arsenal as test team (we found it works)
    try:
        arsenal = await sportdevs_service.search_team("Arsenal")
        if arsenal:
            arsenal_id = arsenal.get("id")
            print(f"   Testing matches for Arsenal (ID: {arsenal_id})")
            
            matches = await sportdevs_service.get_team_matches(arsenal_id)
            print(f"   ✅ Found {len(matches)} matches for Arsenal")
            
            for i, match in enumerate(matches[:3]):  # Show first 3
                print(f"      {i+1}. {match.get('name')} - {match.get('start_time')} - {match.get('tournament_name')}")
            
            return matches
        else:
            print(f"   ❌ Arsenal not found for matches test")
            return []
    except Exception as e:
        print(f"   ❌ Error getting matches: {e}")
        return []


async def test_team_exists():
    """Test vérification d'existence d'équipes"""
    print(f"\n3. ✅ Testing team existence checks...")
    
    teams_to_check = ["Arsenal", "PSG", "Unknown Team", "Barcelona"]
    
    for team_name in teams_to_check:
        try:
            result = await sportdevs_service.team_exists(team_name)
            exists = result.get("exists")
            team_id = result.get("team_id")
            
            if exists:
                print(f"   ✅ {team_name}: EXISTS (ID: {team_id})")
            else:
                print(f"   ❌ {team_name}: NOT FOUND")
        except Exception as e:
            print(f"   ❌ {team_name}: Error - {e}")


async def test_leagues():
    """Test récupération des ligues"""
    print(f"\n4. 🏆 Testing leagues...")
    
    try:
        leagues = await sportdevs_service.get_leagues()
        print(f"   ✅ Found {len(leagues)} leagues")
        
        # Show some interesting leagues
        for i, league in enumerate(leagues[:5]):
            print(f"      {i+1}. {league.get('name')} (ID: {league.get('id')})")
        
        return leagues
    except Exception as e:
        print(f"   ❌ Error getting leagues: {e}")
        return []


async def main():
    print("🚀 Testing SportDevs Integration - Full Service Test")
    print("=" * 70)
    
    try:
        # Test 1: Team search
        found_teams = await test_team_search()
        
        # Test 2: Team matches
        matches = await test_team_matches()
        
        # Test 3: Team existence
        await test_team_exists()
        
        # Test 4: Leagues
        leagues = await test_leagues()
        
        # Summary
        print(f"\n📊 SUMMARY:")
        print(f"   Teams found: {len(found_teams)}")
        print(f"   Matches found: {len(matches)}")
        print(f"   Leagues found: {len(leagues)}")
        
        if found_teams and matches:
            print(f"\n🎉 SUCCESS! SportDevs integration is working properly!")
            print(f"✅ API authentication works")
            print(f"✅ Team search works")
            print(f"✅ Match retrieval works")
            print(f"✅ Ready to run the full system")
        else:
            print(f"\n⚠️  Some components need attention")
        
    except Exception as e:
        print(f"\n❌ Critical error in test: {e}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(main())