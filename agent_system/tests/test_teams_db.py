#!/usr/bin/env python3
"""
Test pour voir les équipes présentes dans la base de données
"""
import asyncio
import sys
import os

# Add the project root to the path so we can import our modules
sys.path.insert(0, os.path.abspath('..'))

from src.models.database import async_session
from src.models.team import Team
from sqlalchemy import select


async def get_teams_from_db():
    """Récupérer toutes les équipes de la base de données"""
    print("🏟️  Checking teams in database...")
    
    async with async_session() as session:
        try:
            # Get all teams
            stmt = select(Team)
            result = await session.execute(stmt)
            teams = result.scalars().all()
            
            if teams:
                print(f"✅ Found {len(teams)} teams in database:")
                print("-" * 80)
                
                for i, team in enumerate(teams, 1):
                    print(f"{i:2d}. {team.name}")
                    print(f"    Display: {team.display_name}")
                    print(f"    Sport: {team.sport}")
                    print(f"    League: {team.league or 'N/A'}")
                    print(f"    Country: {team.country or 'N/A'}")
                    print(f"    External ID: {team.external_id or 'Not synced'}")
                    print(f"    Active: {team.is_active}")
                    print(f"    Logo: {team.logo_url or 'N/A'}")
                    print()
                
                return teams
            else:
                print("❌ No teams found in database")
                print("💡 You may need to initialize the database with some teams first")
                return []
                
        except Exception as e:
            print(f"❌ Error accessing database: {e}")
            return []


async def get_synced_teams():
    """Récupérer les équipes déjà synchronisées avec SportDevs"""
    print("\n🔄 Checking synced teams...")
    
    async with async_session() as session:
        try:
            # Get teams with external_id (synced with SportDevs)
            stmt = select(Team).where(Team.external_id.isnot(None))
            result = await session.execute(stmt)
            synced_teams = result.scalars().all()
            
            if synced_teams:
                print(f"✅ Found {len(synced_teams)} teams synced with SportDevs:")
                
                for team in synced_teams:
                    print(f"   • {team.name} → SportDevs ID: {team.external_id}")
                
                return synced_teams
            else:
                print("❌ No teams synced with SportDevs yet")
                print("💡 Run the sync endpoint to map teams with SportDevs API")
                return []
                
        except Exception as e:
            print(f"❌ Error checking synced teams: {e}")
            return []


async def suggest_next_steps(teams, synced_teams):
    """Suggérer les prochaines étapes"""
    print("\n📋 NEXT STEPS:")
    
    if not teams:
        print("1. 🏗️  Initialize database with sample teams")
        print("   → Add some popular football teams to get started")
        
    elif not synced_teams:
        print("1. 🔄 Sync teams with SportDevs API")
        print("   → curl -X POST \"http://localhost:8001/api/sync/teams\"")
        
    else:
        print("1. ✅ Teams are ready!")
        print("2. 🔄 Sync events from SportDevs")
        print("   → curl -X POST \"http://localhost:8001/api/sync/events\"")
        print("3. 🎯 Run full sync with quest generation")
        print("   → curl -X POST \"http://localhost:8001/api/sync/full\"")


async def main():
    print("🚀 Checking Teams in Database")
    print("=" * 50)
    
    # Check all teams
    teams = await get_teams_from_db()
    
    # Check synced teams
    synced_teams = await get_synced_teams()
    
    # Suggest next steps
    await suggest_next_steps(teams, synced_teams)
    
    print("\n" + "=" * 50)


if __name__ == "__main__":
    asyncio.run(main())