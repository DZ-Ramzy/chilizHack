#!/usr/bin/env python3
"""
Test différentes méthodes d'authentification SportDevs
"""
import asyncio
import httpx


async def test_auth_methods():
    """Test différentes méthodes d'auth"""
    
    api_key = "XyHObILp6UOD9QOws2ZgyA"
    base_url = "https://football.sportdevs.com"
    
    print(f"🧪 Testing different auth methods for SportDevs API")
    
    async with httpx.AsyncClient() as client:
        
        # Method 1: x-api-key header
        print(f"\n1. Testing x-api-key header...")
        try:
            headers = {"x-api-key": api_key}
            response = await client.get(f"{base_url}/teams", headers=headers, timeout=10.0)
            print(f"   Status: {response.status_code}")
            if response.status_code != 200:
                print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Method 2: x-apisports-key header (comme dans la doc)
        print(f"\n2. Testing x-apisports-key header...")
        try:
            headers = {"x-apisports-key": api_key}
            response = await client.get(f"{base_url}/teams", headers=headers, timeout=10.0)
            print(f"   Status: {response.status_code}")
            if response.status_code != 200:
                print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Method 3: Authorization Bearer
        print(f"\n3. Testing Authorization Bearer...")
        try:
            headers = {"Authorization": f"Bearer {api_key}"}
            response = await client.get(f"{base_url}/teams", headers=headers, timeout=10.0)
            print(f"   Status: {response.status_code}")
            if response.status_code != 200:
                print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Method 4: API key as query parameter
        print(f"\n4. Testing API key as query parameter...")
        try:
            params = {"api_key": api_key}
            response = await client.get(f"{base_url}/teams", params=params, timeout=10.0)
            print(f"   Status: {response.status_code}")
            if response.status_code != 200:
                print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Method 5: Test without auth to see error message
        print(f"\n5. Testing without auth (to see error message)...")
        try:
            response = await client.get(f"{base_url}/teams", timeout=10.0)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:300]}")
        except Exception as e:
            print(f"   Error: {e}")


async def test_base_endpoint():
    """Test de l'endpoint de base"""
    
    api_key = "XyHObILp6UOD9QOws2ZgyA"
    
    print(f"\n6. Testing base endpoint and common headers...")
    
    async with httpx.AsyncClient() as client:
        
        # Test root endpoint
        try:
            response = await client.get("https://football.sportdevs.com/", timeout=10.0)
            print(f"   Root endpoint status: {response.status_code}")
        except Exception as e:
            print(f"   Root endpoint error: {e}")
        
        # Test avec RapidAPI headers (au cas où c'est via RapidAPI)
        try:
            headers = {
                "X-RapidAPI-Key": api_key,
                "X-RapidAPI-Host": "football.sportdevs.com"
            }
            response = await client.get("https://football.sportdevs.com/teams", headers=headers, timeout=10.0)
            print(f"   RapidAPI headers status: {response.status_code}")
            if response.status_code != 200:
                print(f"   RapidAPI response: {response.text[:200]}")
        except Exception as e:
            print(f"   RapidAPI error: {e}")


async def main():
    await test_auth_methods()
    await test_base_endpoint()
    
    print(f"\n📝 Conclusions:")
    print(f"   - Si toutes les méthodes échouent avec 'Unauthorized', la clé API peut être invalide")
    print(f"   - Ou alors l'endpoint/domaine n'est pas correct")
    print(f"   - Vérifier la documentation officielle SportDevs")


if __name__ == "__main__":
    asyncio.run(main())