"""
Initialize database with sample data for testing Sports Quest AI
"""
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.database import async_session, init_db
from ..models.team import Team
from ..models.user import User
from ..models.event import SportsEvent
from ..models.user_team import UserTeam
from datetime import datetime, timedelta
import json


async def create_sample_teams():
    """Create sample teams for testing"""
    teams_data = [
        {
            "name": "PSG",
            "display_name": "Paris Saint-Germain",
            "sport": "football",
            "league": "Ligue 1",
            "country": "France"
        },
        {
            "name": "Real Madrid",
            "display_name": "Real Madrid CF", 
            "sport": "football",
            "league": "La Liga",
            "country": "Spain"
        },
        {
            "name": "Barcelona",
            "display_name": "FC Barcelona",
            "sport": "football", 
            "league": "La Liga",
            "country": "Spain"
        },
        {
            "name": "Manchester United",
            "display_name": "Manchester United FC",
            "sport": "football",
            "league": "Premier League",
            "country": "England"
        },
        {
            "name": "Bayern Munich",
            "display_name": "FC Bayern München",
            "sport": "football",
            "league": "Bundesliga", 
            "country": "Germany"
        }
    ]
    
    async with async_session() as session:
        for team_data in teams_data:
            team = Team(**team_data)
            session.add(team)
        
        await session.commit()
        print(f"Created {len(teams_data)} sample teams")


async def create_sample_users():
    """Create sample users for testing"""
    users_data = [
        {
            "username": "psg_fan_1",
            "email": "psg1@example.com",
            "full_name": "Jean Dupont",
            "preferences": json.dumps({"language": "fr", "notifications": True})
        },
        {
            "username": "real_madrid_fan",
            "email": "real1@example.com", 
            "full_name": "Carlos Garcia",
            "preferences": json.dumps({"language": "es", "notifications": True})
        },
        {
            "username": "multi_team_fan",
            "email": "multi@example.com",
            "full_name": "Alex Johnson", 
            "preferences": json.dumps({"language": "en", "notifications": True})
        }
    ]
    
    async with async_session() as session:
        for user_data in users_data:
            user = User(**user_data)
            session.add(user)
        
        await session.commit()
        print(f"Created {len(users_data)} sample users")


async def create_sample_events():
    """Create sample sports events"""
    async with async_session() as session:
        # Get teams for events
        from sqlalchemy import select
        
        teams_stmt = select(Team)
        teams_result = await session.execute(teams_stmt)
        teams = {team.name: team.id for team in teams_result.scalars().all()}
        
        if "PSG" in teams and "Real Madrid" in teams:
            # Create PSG vs Real Madrid event
            event = SportsEvent(
                title="PSG vs Real Madrid",
                description="Champions League Semi-Final",
                sport="football",
                league="Champions League",
                home_team_id=teams["PSG"],
                away_team_id=teams["Real Madrid"],
                event_date=datetime.now() + timedelta(days=3),
                venue="Parc des Princes",
                status="scheduled"
            )
            session.add(event)
        
        if "Barcelona" in teams and "Bayern Munich" in teams:
            # Create Barcelona vs Bayern event
            event2 = SportsEvent(
                title="Barcelona vs Bayern Munich",
                description="Champions League Semi-Final",
                sport="football",
                league="Champions League", 
                home_team_id=teams["Barcelona"],
                away_team_id=teams["Bayern Munich"],
                event_date=datetime.now() + timedelta(days=4),
                venue="Camp Nou",
                status="scheduled"
            )
            session.add(event2)
        
        await session.commit()
        print("Created sample sports events")


async def create_user_team_preferences():
    """Create user-team relationships"""
    async with async_session() as session:
        from sqlalchemy import select
        
        # Get users and teams
        users_stmt = select(User)
        users_result = await session.execute(users_stmt)
        users = {user.username: user.id for user in users_result.scalars().all()}
        
        teams_stmt = select(Team)
        teams_result = await session.execute(teams_stmt)
        teams = {team.name: team.id for team in teams_result.scalars().all()}
        
        # Create preferences
        preferences = [
            {"user": "psg_fan_1", "team": "PSG", "is_favorite": True},
            {"user": "real_madrid_fan", "team": "Real Madrid", "is_favorite": True},
            {"user": "multi_team_fan", "team": "PSG", "is_favorite": True},
            {"user": "multi_team_fan", "team": "Barcelona", "is_favorite": False},
        ]
        
        for pref in preferences:
            if pref["user"] in users and pref["team"] in teams:
                user_team = UserTeam(
                    user_id=users[pref["user"]],
                    team_id=teams[pref["team"]],
                    is_favorite=pref["is_favorite"],
                    notification_enabled=True
                )
                session.add(user_team)
        
        await session.commit()
        print("Created user-team preferences")


async def initialize_sample_data():
    """Initialize all sample data"""
    print("Initializing Sports Quest AI database with sample data...")
    
    # Initialize database tables
    await init_db()
    print("Database tables initialized")
    
    # Create sample data
    await create_sample_teams()
    await create_sample_users() 
    await create_sample_events()
    await create_user_team_preferences()
    
    print("✅ Sample data initialization completed!")
    print("\nSample scenario available:")
    print("- Event: PSG vs Real Madrid")
    print("- Teams: PSG, Real Madrid, Barcelona, Bayern Munich, Manchester United")
    print("- Users: psg_fan_1, real_madrid_fan, multi_team_fan")
    print("- Workflow can be tested with /api/workflow/trigger-event endpoint")


if __name__ == "__main__":
    import asyncio
    asyncio.run(initialize_sample_data())