"""
Générateur de Quêtes Communautaires - Événements footballistiques globaux
Logique : Search global football events → Generate single community quest for all users
"""
from agents import Agent, WebSearchTool, Runner
from pydantic import BaseModel
from typing import List, Optional
from loguru import logger
from ..tools.database_tools import create_quest


class CommunityQuest(BaseModel):
    """Une quête communautaire globale"""
    title: str
    description: str
    target_value: int
    difficulty: str
    event_context: str


# Create search agent for global football events
global_events_search_agent = Agent(
    name="GlobalFootballEventsAgent",
    instructions="""
    You are a global football events research agent. Your job is to search for major upcoming football events and tournaments.
    
    Search for:
    - Major tournament finals (World Cup, Euros, Champions League, etc.)
    - International matches and friendlies
    - Transfer deadline days and windows
    - Awards ceremonies (Ballon d'Or, FIFA Awards, etc.)
    - Season start/end events across major leagues
    - Derby matches and clasicos
    - Major football announcements and milestones
    
    Focus on UPCOMING events (next 30 days) that would interest the global football community.
    Look for events that can unite fans regardless of their team allegiance.
    
    Return comprehensive information about the most significant upcoming football events.
    """,
    tools=[WebSearchTool()],
    output_type=str
)


async def search_global_football_events() -> tuple[str, bool]:
    """Search for major global football events happening soon"""
    try:
        logger.info(f"🌍 Searching for global football events")
        
        # Run the search agent
        result = await Runner.run(
            global_events_search_agent, 
            input=f"Search for major upcoming football events in the next 30 days. Today is July 12, 2025. Focus on tournaments, finals, transfer news, international matches, and other events that would interest the global football community."
        )
        
        if hasattr(result, 'final_output') and result.final_output:
            events_content = str(result.final_output)
            
            # Check if significant events were found
            event_indicators = [
                "final", "tournament", "championship", "world cup", "euros", 
                "champions league", "transfer", "deadline", "international",
                "clasico", "derby", "awards", "ceremony", "season", "launch"
            ]
            
            has_events = any(indicator in events_content.lower() for indicator in event_indicators)
            
            if has_events:
                logger.success(f"✅ Found global football events")
                return events_content, True
            else:
                logger.info(f"ℹ️ No major events found in near future")
                return events_content, False
        else:
            logger.warning(f"⚠️ No search results for global events")
            return "", False
            
    except Exception as e:
        logger.error(f"❌ Global events search error: {e}")
        return "", False


async def generate_community_quest(events_content: str) -> Optional[CommunityQuest]:
    """Generate a single community quest based on global football events"""
    try:
        from agents import Agent, Runner
        
        logger.info(f"🌟 Generating community quest from global events")
        logger.info(f"📰 Events content length: {len(events_content)} characters")
        
        # Create community quest agent
        community_agent = Agent(
            name="CommunityQuestGenerator",
            instructions=f"""
            You are generating a SINGLE community quest for all football fans based on major upcoming events.
            
            GLOBAL FOOTBALL EVENTS CONTEXT:
            {events_content}
            
            Based on this context, create ONE engaging community quest that:
            1. Focuses on the COMPETITION/TOURNAMENT itself, not specific teams
            2. Can be completed by fans of ANY team worldwide
            3. Celebrates the event as a global football moment
            4. Encourages community participation across all nationalities
            
            Available community actions:
            - Tweet predictions about major events (if social media)
            - Tweet reactions to football news (if social media)
            - Tweet in global football discussions (if social media)
            - Watch tournament highlights and matches
            - Read about tournament history and records
            - Learn about participating teams and players
            - Follow tournament news and updates
            - Celebrate the global football community
            - Support your favorite teams in the tournament
            - Discover football culture from different countries
            
            IMPORTANT: If the action involves social media posting/sharing, use ONLY Twitter.
            
            Quest creation rules:
            1. Write in immersive Community Manager style
            2. Reference the most exciting upcoming event from the context
            3. Make it inclusive for fans of all teams and nationalities
            4. Keep it simple: maximum 1-2 actions only
            5. Use storytelling language that unites the global football community
            6. Make fans feel part of football history in the making
            
            Return exactly 1 quest in this JSON format:
            {{
                "title": "🌍 Global Football Moment",
                "description": "Immersive description that captures the magic of global football and the specific event. Paint the picture of why this moment matters to every football fan worldwide. Then clearly state: Complete this quest by [1-2 simple actions]. Together we celebrate the beautiful game!",
                "target_value": 2,
                "difficulty": "easy",
                "event_context": "Brief summary of the main event this quest is about"
            }}
            
            Generate the community quest now based on the events context provided.
            """
        )
        
        # Run the agent
        result = await Runner.run(community_agent, input=f"Generate one community quest for global football events")
        
        if hasattr(result, 'final_output') and result.final_output:
            # Parse the JSON response
            import json
            try:
                response_text = str(result.final_output)
                logger.info(f"🔍 Community agent response: {response_text[:200]}...")
                
                # Find and parse JSON
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    quest_data = json.loads(json_str)
                    
                    community_quest = CommunityQuest(
                        title=quest_data.get('title', f'🌍 Global Football Quest'),
                        description=quest_data.get('description', f'Join the global football community!'),
                        target_value=quest_data.get('target_value', 5),
                        difficulty=quest_data.get('difficulty', 'medium'),
                        event_context=quest_data.get('event_context', 'Global football events')
                    )
                    
                    logger.success(f"✅ Generated community quest: {community_quest.title}")
                    return community_quest
                else:
                    logger.warning(f"⚠️ No JSON found in community agent response")
                    return None
                    
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON parsing error in community generation: {e}")
                return None
        else:
            logger.warning(f"⚠️ Community agent returned no output")
            return None
        
    except Exception as e:
        logger.error(f"❌ Error generating community quest: {e}")
        # Fallback community quest
        logger.info(f"🔄 Falling back to simple community generation")
        
        community_quest = CommunityQuest(
            title=f"🌍 United by Football",
            description=f"Across continents, through different languages and cultures, one thing unites us all—the beautiful game. From the grassroots pitches to the grandest stadiums, football weaves stories that transcend borders. As part of this global family, your voice adds to the chorus of millions who live and breathe football. Complete this quest by tweeting one message about what football means to you, regardless of which team you support. The beautiful game belongs to all of us!",
            target_value=1,
            difficulty="easy",
            event_context="Global football community celebration"
        )
        
        return community_quest


async def save_community_quest(quest: CommunityQuest) -> str:
    """Save community quest to database (using global team_id=0 for community quests)"""
    try:
        logger.info(f"💾 Saving community quest: {quest.title}")
        
        quest_id = await create_quest(
            title=quest.title,
            description=quest.description,
            quest_type="collective",
            team_id=0,  # Use team_id=0 for global community quests
            target_metric="community_actions",
            target_value=quest.target_value
        )
        
        logger.success(f"✅ Saved community quest with ID: {quest_id}")
        return f"SUCCESS|Saved community quest: {quest_id}"
        
    except Exception as e:
        logger.error(f"❌ Error saving community quest: {e}")
        return f"ERROR|{str(e)}"


# Create the community quest agent
community_quest_agent = Agent(
    name="CommunityQuestGenerator",
    instructions="""
    You generate community quests for global football events.
    
    Your workflow:
    1. Search for major global football events happening soon
    2. Generate one community quest that appeals to all football fans
    3. Save the quest to the database for all users
    
    Focus on:
    - Major tournaments and events
    - Global football community building
    - Cross-team fan engagement
    - Shared football culture and passion
    - International football unity
    
    Make community quests exciting, inclusive, and relevant to current global football context.
    """,
    tools=[search_global_football_events, generate_community_quest, save_community_quest],
    output_type=str
)