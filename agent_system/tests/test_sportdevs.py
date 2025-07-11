#!/usr/bin/env python3
"""
Test rapide de l'API SportDevs avec la clé fournie
"""
import asyncio
import httpx


async def test_sportdevs_api():
    """Test direct de l'API SportDevs"""
    
    api_key = "XyHObILp6UOD9QOws2ZgyA"
    base_url = "https://football.sportdevs.com"
    
    print(f"🧪 Testing SportDevs API with key: {api_key[:10]}...")
    print(f"Base URL: {base_url}")
    
    async with httpx.AsyncClient() as client:
        headers = {"x-api-key": api_key}
        
        try:
            # Test 1: Search for Arsenal
            print(f"\n1. 🔍 Searching for Arsenal...")
            search_url = f"{base_url}/teams"
            params = {"name": "like.*Arsenal*"}
            
            response = await client.get(search_url, params=params, headers=headers, timeout=10.0)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if data and len(data) > 0:
                    team = data[0]
                    print(f"✅ SUCCESS! Found Arsenal:")
                    print(f"   ID: {team.get('id')}")
                    print(f"   Name: {team.get('name')}")
                    print(f"   Country ID: {team.get('country_id')}")
                    print(f"   Venue: {team.get('venue_name')}")
                    print(f"   Hash Image: {team.get('hash_image')}")
                    
                    # Test 2: Get matches for Arsenal
                    team_id = team.get('id')
                    if team_id:
                        print(f"\n2. ⚽ Getting matches for Arsenal (ID: {team_id})...")
                        matches_url = f"{base_url}/matches"
                        matches_params = {"team_id": f"eq.{team_id}"}
                        
                        matches_response = await client.get(matches_url, params=matches_params, headers=headers, timeout=10.0)
                        
                        if matches_response.status_code == 200:
                            matches_data = matches_response.json()
                            
                            print(f"✅ Found {len(matches_data)} matches for Arsenal:")
                            
                            for i, match in enumerate(matches_data[:3]):  # Show first 3
                                print(f"   {i+1}. {match.get('home_name')} vs {match.get('away_name')} - {match.get('date')} - {match.get('league_name')}")
                            
                            return True
                        else:
                            print(f"❌ Matches API Error: {matches_response.status_code}")
                            print(f"Response: {matches_response.text}")
                            return False
                    
                    return True
                else:
                    print(f"❌ No teams found in response: {data}")
                    return False
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return False


async def test_psg():
    """Test avec PSG également"""
    
    api_key = "XyHObILp6UOD9QOws2ZgyA"
    base_url = "https://football.sportdevs.com"
    
    print(f"\n3. 🔍 Searching for PSG...")
    
    async with httpx.AsyncClient() as client:
        headers = {"x-api-key": api_key}
        
        try:
            search_url = f"{base_url}/teams"
            params = {"name": "like.*Paris*"}
            
            response = await client.get(search_url, params=params, headers=headers, timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                
                if data and len(data) > 0:
                    for team in data:
                        if "Paris" in team.get('name', ''):
                            print(f"✅ Found PSG: {team.get('name')} (ID: {team.get('id')})")
                            return True
                
                print(f"❌ No PSG found in {len(data)} results")
                return False
            else:
                print(f"❌ PSG search error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ PSG search failed: {e}")
            return False


async def test_leagues():
    """Test getting leagues"""
    
    api_key = "XyHObILp6UOD9QOws2ZgyA"
    base_url = "https://football.sportdevs.com"
    
    print(f"\n4. 🏆 Getting leagues...")
    
    async with httpx.AsyncClient() as client:
        headers = {"x-api-key": api_key}
        
        try:
            leagues_url = f"{base_url}/leagues"
            
            response = await client.get(leagues_url, headers=headers, timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Found {len(data)} leagues:")
                
                for i, league in enumerate(data[:5]):  # Show first 5
                    print(f"   {i+1}. {league.get('name')} (ID: {league.get('id')}) - {league.get('country_name')}")
                
                return True
            else:
                print(f"❌ Leagues error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Leagues test failed: {e}")
            return False


async def main():
    print("🚀 Testing SportDevs Football API")
    print("=" * 50)
    
    # Test 1: Basic team search
    arsenal_success = await test_sportdevs_api()
    
    # Test 2: PSG search
    psg_success = await test_psg()
    
    # Test 3: Leagues
    leagues_success = await test_leagues()
    
    if arsenal_success and psg_success and leagues_success:
        print(f"\n🎉 All tests passed! SportDevs API key works perfectly.")
        print(f"✅ The integration should work with your key")
    else:
        print(f"\n⚠️  Some tests failed - check API key or endpoints")
    
    print("\n" + "=" * 50)


if __name__ == "__main__":
    asyncio.run(main())