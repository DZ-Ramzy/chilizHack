#!/usr/bin/env python3
"""
Test avec la méthode d'auth qui marche (Authorization Bearer)
"""
import asyncio
import httpx


async def test_working_auth():
    """Test avec Authorization Bearer qui a fonctionné"""
    
    api_key = "XyHObILp6UOD9QOws2ZgyA"
    base_url = "https://football.sportdevs.com"
    
    print(f"🧪 Testing SportDevs API with Authorization Bearer")
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {api_key}"}
        
        try:
            # Test 1: Get teams (general)
            print(f"\n1. 🔍 Getting teams...")
            response = await client.get(f"{base_url}/teams", headers=headers, timeout=10.0)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS! Found {len(data)} teams")
                
                # Show first few teams
                for i, team in enumerate(data[:3]):
                    print(f"   {i+1}. {team.get('name')} (ID: {team.get('id')}) - {team.get('venue_name')}")
                
                # Test 2: Search for Arsenal specifically
                print(f"\n2. 🔍 Searching for Arsenal...")
                arsenal_params = {"name": "like.*Arsenal*"}
                arsenal_response = await client.get(f"{base_url}/teams", params=arsenal_params, headers=headers, timeout=10.0)
                
                if arsenal_response.status_code == 200:
                    arsenal_data = arsenal_response.json()
                    
                    if arsenal_data and len(arsenal_data) > 0:
                        arsenal = arsenal_data[0]
                        print(f"✅ Found Arsenal: {arsenal.get('name')} (ID: {arsenal.get('id')})")
                        
                        # Test 3: Get matches for Arsenal
                        arsenal_id = arsenal.get('id')
                        if arsenal_id:
                            print(f"\n3. ⚽ Getting matches for Arsenal (ID: {arsenal_id})...")
                            matches_params = {"team_id": f"eq.{arsenal_id}"}
                            matches_response = await client.get(f"{base_url}/matches", params=matches_params, headers=headers, timeout=10.0)
                            
                            if matches_response.status_code == 200:
                                matches_data = matches_response.json()
                                print(f"✅ Found {len(matches_data)} matches for Arsenal:")
                                
                                for i, match in enumerate(matches_data[:3]):
                                    print(f"   {i+1}. {match.get('home_name')} vs {match.get('away_name')} - {match.get('date')}")
                                
                                return True
                            else:
                                print(f"❌ Matches error: {matches_response.status_code}")
                                print(f"Response: {matches_response.text[:200]}")
                    else:
                        print(f"❌ Arsenal not found")
                else:
                    print(f"❌ Arsenal search error: {arsenal_response.status_code}")
                    
            else:
                print(f"❌ Teams API Error: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return False


async def test_leagues():
    """Test leagues endpoint"""
    
    api_key = "XyHObILp6UOD9QOws2ZgyA"
    base_url = "https://football.sportdevs.com"
    
    print(f"\n4. 🏆 Testing leagues endpoint...")
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {api_key}"}
        
        try:
            response = await client.get(f"{base_url}/leagues", headers=headers, timeout=10.0)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Found {len(data)} leagues:")
                
                for i, league in enumerate(data[:5]):
                    print(f"   {i+1}. {league.get('name')} (ID: {league.get('id')})")
                
                return True
            else:
                print(f"❌ Leagues error: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ Leagues test failed: {e}")
            return False


async def main():
    print("🚀 Testing SportDevs Football API with working auth")
    print("=" * 60)
    
    teams_success = await test_working_auth()
    leagues_success = await test_leagues()
    
    if teams_success and leagues_success:
        print(f"\n🎉 ALL TESTS PASSED! SportDevs API integration is working!")
        print(f"✅ Authorization Bearer method works perfectly")
        print(f"✅ Teams and matches endpoints are accessible")
        print(f"✅ Ready to integrate with the main system")
    else:
        print(f"\n⚠️  Some tests failed")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())