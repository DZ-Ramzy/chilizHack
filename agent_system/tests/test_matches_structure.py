#!/usr/bin/env python3
"""
Test pour comprendre la structure des matches dans SportDevs
"""
import asyncio
import httpx
import json


async def test_matches_structure():
    """Comprendre la structure des matches"""
    
    api_key = "XyHObILp6UOD9QOws2ZgyA"
    base_url = "https://football.sportdevs.com"
    
    print(f"🧪 Understanding matches structure in SportDevs API")
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {api_key}"}
        
        try:
            # Test 1: Get raw matches without filters
            print(f"\n1. 🔍 Getting raw matches (no filters)...")
            response = await client.get(f"{base_url}/matches", headers=headers, timeout=10.0)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Found {len(data)} matches")
                
                if data and len(data) > 0:
                    # Show structure of first match
                    first_match = data[0]
                    print(f"\n📋 Structure of first match:")
                    for key, value in first_match.items():
                        print(f"   {key}: {value}")
                    
                    # Look for team-related fields
                    team_fields = [k for k in first_match.keys() if 'team' in k.lower()]
                    home_fields = [k for k in first_match.keys() if 'home' in k.lower()]
                    away_fields = [k for k in first_match.keys() if 'away' in k.lower()]
                    
                    print(f"\n🏠 Team-related fields: {team_fields}")
                    print(f"🏠 Home-related fields: {home_fields}")
                    print(f"🚀 Away-related fields: {away_fields}")
                    
                    return first_match
            else:
                print(f"❌ Matches error: {response.status_code}")
                print(f"Response: {response.text[:300]}")
                return None
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None


async def test_correct_team_filter():
    """Test avec les bons noms de champs"""
    
    api_key = "XyHObILp6UOD9QOws2ZgyA"
    base_url = "https://football.sportdevs.com"
    
    print(f"\n2. 🧪 Testing correct team filters...")
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {api_key}"}
        
        # Essayer différents noms de champs possibles
        possible_filters = [
            {"home_id": "eq.410564"},  # Arsenal ID
            {"away_id": "eq.410564"},
            {"home_team_id": "eq.410564"},
            {"away_team_id": "eq.410564"},
            {"team_home_id": "eq.410564"},
            {"team_away_id": "eq.410564"}
        ]
        
        for i, filter_params in enumerate(possible_filters):
            try:
                filter_name = list(filter_params.keys())[0]
                print(f"\n   Testing filter: {filter_name}")
                
                response = await client.get(f"{base_url}/matches", params=filter_params, headers=headers, timeout=10.0)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Success! Found {len(data)} matches with {filter_name}")
                    
                    if data and len(data) > 0:
                        match = data[0]
                        print(f"   Match: {match.get('home_name', 'N/A')} vs {match.get('away_name', 'N/A')}")
                        return filter_name, data[0]
                        
                elif response.status_code == 400:
                    error_text = response.text
                    print(f"   ❌ Invalid field: {filter_name}")
                else:
                    print(f"   ❌ Other error: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error testing {filter_name}: {e}")
        
        return None, None


async def main():
    print("🚀 Understanding SportDevs Matches API Structure")
    print("=" * 60)
    
    # First understand the structure
    match_example = await test_matches_structure()
    
    # Then test correct filters
    if match_example:
        working_filter, match_data = await test_correct_team_filter()
        
        if working_filter:
            print(f"\n🎉 SUCCESS!")
            print(f"✅ Working filter field: {working_filter}")
            print(f"✅ Can query matches for specific teams")
        else:
            print(f"\n⚠️  Need to understand the correct filter format")
            print(f"💡 Maybe the API uses a different query syntax")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())