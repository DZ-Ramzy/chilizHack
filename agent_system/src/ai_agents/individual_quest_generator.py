"""
Générateur de Quêtes Individuelles - Approche Simple
Logique : Agent search news → Generate list of quests based on content
"""
from agents import Agent, WebSearchTool, Runner
from pydantic import BaseModel
from typing import List
from loguru import logger
from ..tools.database_tools import create_quest


class IndividualQuest(BaseModel):
    """Une quête individuelle"""
    title: str
    description: str
    target_value: int
    difficulty: str


# Create search agent with WebSearchTool
search_agent = Agent(
    name="NewsSearchAgent",
    instructions="""
    You are a sports news research agent. Your job is to search for current, relevant football news.
    
    When given a team name, search for:
    - Recent match results and upcoming fixtures
    - Player transfers, injuries, and updates
    - Team news and training updates
    - Goals, records, and achievements
    - Current season performance
    
    Focus on RECENT and SPECIFIC news (last 7 days preferred).
    Return comprehensive news content that can be used for quest generation.
    
    Search thoroughly and return detailed, current information.
    """,
    tools=[WebSearchTool()],
    output_type=str
)


async def agent_search(team_name: str) -> str:
    """Use search agent to fetch news for a team"""
    try:
        logger.info(f"🔍 Agent searching news for {team_name}")
        
        # Run the search agent
        result = await Runner.run(
            search_agent, 
            input=f"Search for current football news about {team_name}. Focus on recent matches, transfers, player updates, and team news from the last week."
        )
        
        if hasattr(result, 'final_output') and result.final_output:
            news_content = str(result.final_output)
            logger.success(f"✅ Agent found {len(news_content)} characters of news for {team_name}")
            return news_content
        else:
            logger.warning(f"⚠️ Agent returned no news for {team_name}")
            return f"Recent {team_name} updates: Team preparing for upcoming fixtures, player training updates, and fan engagement activities."
            
    except Exception as e:
        logger.error(f"❌ Agent search error for {team_name}: {e}")
        return f"Recent {team_name} updates: Team preparing for upcoming fixtures, player training updates, and fan engagement activities."


async def fetch_team_news(team_name: str) -> str:
    """Fetch real news for a specific team using agent search"""
    try:
        # Use agent_search instead of direct WebSearchTool call
        news_content = await agent_search(team_name)
        return news_content
        
    except Exception as e:
        logger.error(f"❌ Error fetching news for {team_name}: {e}")
        return f"Recent {team_name} updates: Team preparing for upcoming fixtures, player training updates, and fan engagement activities."


async def generate_individual_quests(team_name: str, news_content: str) -> List[IndividualQuest]:
    """Generate smart individual quests using agent with news analysis"""
    try:
        from agents import Agent, Runner
        
        logger.info(f"🧠 Using smart agent to generate quests for {team_name}")
        logger.info(f"📰 News content length: {len(news_content)} characters")
        
        # Create smart quest agent with system prompt containing the news
        smart_agent = Agent(
            name="SmartQuestGenerator",
            instructions=f"""
            You are generating individual football fan quests for {team_name} based on REAL current news.
            
            CURRENT NEWS TO ANALYZE:
            {news_content}
            
            Based on this news content, analyze for specific events (goals, transfers, matches, injuries, records, etc.) and generate 2-3 engaging quests that reference these REAL events.
            
            Available actions for quests:
            - Tweet about specific events/players (if social media)
            - Retweet official content with comments (if social media)
            - Follow official team accounts on Twitter (if social media)
            - Watch match highlights or team videos
            - Read articles about the team/players
            - Celebrate team victories in your own way
            - Support the team during matches
            - Learn about team history or players
            - Engage with team content online
            
            IMPORTANT: If the action involves social media posting/sharing, use ONLY Twitter.
            
            Quest creation rules:
            1. Write immersive descriptions like a Community Manager would
            2. Reference specific players, scores, opponents, dates from the news
            3. Keep it simple: maximum 1-2 concrete actions only
            4. Use engaging, storytelling language that connects fans emotionally
            5. Make it feel like exclusive insider content
            
            Return exactly 2-3 quests in this JSON format:
            [
              {{
                "title": "🎯 Engaging Quest Title",
                "description": "Immersive, well-written description that tells a story and mentions specific news context. Then clearly state: Complete this quest by [1-2 simple actions]. Join the conversation and show your passion!",
                "target_value": 2,
                "difficulty": "easy"
              }}
            ]
            
            Generate the quests now based on the news content provided above.
            """
        )
        
        # Run the agent with minimal input since news is in system instructions
        result = await Runner.run(smart_agent, input=f"Generate individual quests for {team_name}")
        
        if hasattr(result, 'final_output') and result.final_output:
            # Parse the JSON response from the agent
            import json
            try:
                # Get the response text
                response_text = str(result.final_output)
                logger.info(f"🔍 Agent response for {team_name}: {response_text[:200]}...")
                
                # Try to find and parse JSON
                import re
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    quest_data = json.loads(json_str)
                    
                    # Convert to IndividualQuest objects
                    quests = []
                    for quest in quest_data:
                        quests.append(IndividualQuest(
                            title=quest.get('title', f'📱 {team_name} Fan Quest'),
                            description=quest.get('description', f'Support {team_name}!'),
                            target_value=quest.get('target_value', 3),
                            difficulty=quest.get('difficulty', 'easy')
                        ))
                    
                    logger.success(f"✅ Smart agent generated {len(quests)} quests for {team_name}")
                    return quests
                else:
                    logger.warning(f"⚠️ No JSON found in agent response for {team_name}")
                    return []
                    
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON parsing error for {team_name}: {e}")
                return []
        else:
            logger.warning(f"⚠️ Smart agent returned no output for {team_name}")
            return []
        
    except Exception as e:
        logger.error(f"❌ Error with smart agent for {team_name}: {e}")
        # Fallback to simple quest generation
        logger.info(f"🔄 Falling back to simple quest generation for {team_name}")
        
        quest = IndividualQuest(
            title=f"🏆 {team_name} Inside Story",
            description=f"Step into the heart of {team_name}'s journey this season. Every match tells a story, every player has a moment to shine. As a true supporter, you're part of this incredible narrative. Complete this quest by tweeting one message about what makes {team_name} special to you. Your voice matters in our community!",
            target_value=1,
            difficulty="easy"
        )
        return [quest]


async def save_individual_quests(team_id: int, team_name: str, quests: List[IndividualQuest]) -> str:
    """Save individual quests to database"""
    try:
        logger.info(f"💾 Saving {len(quests)} individual quests for {team_name}")
        
        saved_quest_ids = []
        
        for quest in quests:
            quest_id = await create_quest(
                title=quest.title,
                description=quest.description,
                quest_type="individual",
                team_id=team_id,
                target_metric="engagement_actions",
                target_value=quest.target_value
            )
            saved_quest_ids.append(quest_id)
        
        logger.success(f"✅ Saved {len(saved_quest_ids)} quests for {team_name}: {saved_quest_ids}")
        return f"SUCCESS|Saved {len(saved_quest_ids)} quests: {saved_quest_ids}"
        
    except Exception as e:
        logger.error(f"❌ Error saving quests for {team_name}: {e}")
        return f"ERROR|{str(e)}"


# Create the individual quest agent
individual_quest_agent = Agent(
    name="IndividualQuestGenerator",
    instructions="""
    You generate individual quests for football teams.
    
    Your workflow:
    1. Fetch fresh news content for the team
    2. Generate 2-3 relevant individual quests based on the news
    3. Save the quests to the database
    
    Focus on:
    - Fan community engagement
    - Social media activities  
    - Team support and spirit
    - News sharing and discussion
    
    Make quests engaging, achievable, and relevant to current team context.
    """,
    tools=[fetch_team_news, generate_individual_quests, save_individual_quests],
    output_type=str
)