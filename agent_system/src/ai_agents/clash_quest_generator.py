"""
Générateur de Clash Quests - Quêtes de rivalité entre équipes
Logique : Search match between teams → Generate opposing quests A vs B
"""
from agents import Agent, WebSearchTool, Runner
from pydantic import BaseModel
from typing import List, Tuple, Optional
from loguru import logger
from ..tools.database_tools import create_quest


class ClashQuest(BaseModel):
    """Une quête de clash entre équipes"""
    title: str
    description: str
    target_value: int
    difficulty: str
    team_side: str  # "A" ou "B"


# Create search agent for match research
match_search_agent = Agent(
    name="MatchSearchAgent",
    instructions="""
    You are a football match research agent. Your job is to search for matches between two specific teams.
    
    When given two team names, search for:
    - Upcoming fixtures between these teams
    - Recent match results between them
    - Head-to-head statistics
    - Current rivalry context
    - Match previews and predictions
    - Player comparisons
    
    Focus on CURRENT and UPCOMING matches (next 30 days preferred).
    Return comprehensive match information that can be used for clash quest generation.
    
    If no direct match is found, search for general rivalry context between the teams.
    """,
    tools=[WebSearchTool()],
    output_type=str
)


async def search_team_match(team_a: str, team_b: str) -> tuple[str, bool]:
    """Search for match information between two teams using ESPN API. Returns (content, match_exists)"""
    try:
        logger.info(f"🔍 Checking ESPN API for match between {team_a} vs {team_b}")
        
        # Import ESPN service
        from ..services.espn_football_service import espn_football_service
        
        # Get matches for both teams from ESPN API
        team_a_matches = await espn_football_service.get_team_matches(team_a)
        team_b_matches = await espn_football_service.get_team_matches(team_b)
        
        # Check if teams face each other in upcoming matches
        match_found = False
        match_details = ""
        
        for match_a in team_a_matches:
            for match_b in team_b_matches:
                # Check if it's the same match (same ID or same opponent)
                if (match_a.get("id") == match_b.get("id") or 
                    (team_b.lower() in str(match_a.get("opponent", "")).lower() and 
                     team_a.lower() in str(match_b.get("opponent", "")).lower())):
                    match_found = True
                    match_details = f"ESPN API Match found: {team_a} vs {team_b} on {match_a.get('date', 'TBD')}"
                    break
            if match_found:
                break
        
        if match_found:
            logger.success(f"✅ ESPN confirmed match between {team_a} vs {team_b}")
            
            # Now search for news about this confirmed match
            logger.info(f"🔍 Searching for news about confirmed match {team_a} vs {team_b}")
            try:
                news_result = await Runner.run(
                    match_search_agent, 
                    input=f"Search for recent news and information about the upcoming football match between {team_a} and {team_b}. Focus on: team form, player updates, match predictions, head-to-head stats, and any match preview content."
                )
                
                if hasattr(news_result, 'final_output') and news_result.final_output:
                    news_content = str(news_result.final_output)
                    combined_content = f"{match_details}\n\nMatch News:\n{news_content}"
                    logger.success(f"✅ Found {len(news_content)} characters of match news")
                    return combined_content, True
                else:
                    logger.warning(f"⚠️ No news found for confirmed match")
                    return match_details, True
                    
            except Exception as news_error:
                logger.error(f"❌ Error fetching match news: {news_error}")
                return match_details, True  # Still return match confirmed
        else:
            logger.info(f"ℹ️ ESPN API: No upcoming match between {team_a} vs {team_b}")
            content = f"ESPN API result: No upcoming matches found between {team_a} and {team_b}. Team A has {len(team_a_matches)} upcoming matches, Team B has {len(team_b_matches)} upcoming matches, but none against each other."
            return content, False
            
    except Exception as e:
        logger.error(f"❌ ESPN API error for {team_a} vs {team_b}: {e}")
        return f"ESPN API error: {str(e)}", False


async def generate_clash_quests(team_a: str, team_b: str, match_content: str) -> Tuple[List[ClashQuest], List[ClashQuest]]:
    """Generate opposing clash quests for both teams"""
    try:
        from agents import Agent, Runner
        
        logger.info(f"⚔️ Generating clash quests for {team_a} vs {team_b}")
        logger.info(f"📰 Match content length: {len(match_content)} characters")
        
        # Create clash quest agent
        clash_agent = Agent(
            name="ClashQuestGenerator",
            instructions=f"""
            You are generating clash quests for a football rivalry between {team_a} and {team_b}.
            
            MATCH/RIVALRY CONTEXT:
            {match_content}
            
            Based on this context, generate 2 opposing quests - one for {team_a} fans and one for {team_b} fans.
            These should be competitive challenges where fans of each team can show their support.
            
            Available actions for clash quests:
            - Tweet predictions/support for your team (if social media)
            - Tweet photos wearing team colors/gear (if social media)
            - Tweet match predictions and scores (if social media)
            - Tweet friendly banter with rival fans (if social media)
            - Watch team highlights and classic matches
            - Learn about historical victories over rivals
            - Support your team during the match
            - Celebrate team achievements
            - Read about team vs rival statistics
            - Follow team news and updates
            
            IMPORTANT: If the action involves social media posting/sharing, use ONLY Twitter.
            
            Quest creation rules:
            1. Write immersive, Community Manager style descriptions
            2. Reference specific match details and create emotional connection
            3. Each quest should be the opposite perspective (Team A vs Team B)
            4. Keep it simple: maximum 1-2 actions per quest
            5. Use storytelling language that builds anticipation and rivalry
            6. Make fans feel part of something bigger
            
            Return exactly 2 quests in this JSON format:
            [
              {{
                "title": "⚔️ {team_a} Quest Title",
                "description": "Immersive story about the rivalry and match context. Paint the picture of why this matters. Then clearly state: Complete this quest by [1-2 simple actions]. Together we rise!",
                "target_value": 2,
                "difficulty": "easy",
                "team_side": "A"
              }},
              {{
                "title": "🛡️ {team_b} Quest Title", 
                "description": "Immersive story about the rivalry from the opposite perspective. Build the emotional stakes. Then clearly state: Complete this quest by [1-2 simple actions]. Victory awaits!",
                "target_value": 2,
                "difficulty": "easy",
                "team_side": "B"
              }}
            ]
            
            Generate the clash quests now based on the match context provided.
            """
        )
        
        # Run the agent
        result = await Runner.run(clash_agent, input=f"Generate clash quests for {team_a} vs {team_b}")
        
        if hasattr(result, 'final_output') and result.final_output:
            # Parse the JSON response
            import json
            try:
                response_text = str(result.final_output)
                logger.info(f"🔍 Clash agent response: {response_text[:200]}...")
                
                # Find and parse JSON
                import re
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    quest_data = json.loads(json_str)
                    
                    # Separate quests by team
                    team_a_quests = []
                    team_b_quests = []
                    
                    for quest in quest_data:
                        clash_quest = ClashQuest(
                            title=quest.get('title', f'⚔️ {team_a} vs {team_b} Clash'),
                            description=quest.get('description', f'Support your team!'),
                            target_value=quest.get('target_value', 4),
                            difficulty=quest.get('difficulty', 'medium'),
                            team_side=quest.get('team_side', 'A')
                        )
                        
                        if clash_quest.team_side == "A":
                            team_a_quests.append(clash_quest)
                        else:
                            team_b_quests.append(clash_quest)
                    
                    logger.success(f"✅ Generated {len(team_a_quests)} quests for {team_a}, {len(team_b_quests)} quests for {team_b}")
                    return team_a_quests, team_b_quests
                else:
                    logger.warning(f"⚠️ No JSON found in clash agent response")
                    return [], []
                    
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON parsing error in clash generation: {e}")
                return [], []
        else:
            logger.warning(f"⚠️ Clash agent returned no output")
            return [], []
        
    except Exception as e:
        logger.error(f"❌ Error generating clash quests: {e}")
        # Fallback clash quests
        logger.info(f"🔄 Falling back to simple clash generation")
        
        team_a_quest = ClashQuest(
            title=f"⚔️ {team_a} Legacy Defender",
            description=f"The rivalry between {team_a} and {team_b} runs deeper than just 90 minutes on the pitch. It's about history, passion, and unwavering loyalty. As a {team_a} supporter, you carry the torch of generations of fans who've lived and breathed this beautiful rivalry. Complete this quest by tweeting one powerful message about why {team_a} means everything to you. Your voice echoes through the stadium!",
            target_value=1,
            difficulty="easy",
            team_side="A"
        )
        
        team_b_quest = ClashQuest(
            title=f"🛡️ {team_b} Pride Warrior",
            description=f"When {team_b} faces {team_a}, it's more than a match—it's a testament to everything we stand for. The colors, the chants, the unbreakable bond between supporters. You are part of a legacy that transcends football itself. Complete this quest by tweeting one heartfelt message about what makes {team_b} your eternal choice. Together we are unstoppable!",
            target_value=1,
            difficulty="easy",
            team_side="B"
        )
        
        return [team_a_quest], [team_b_quest]


async def save_clash_quests(team_a_id: int, team_b_id: int, team_a_name: str, team_b_name: str, 
                          team_a_quests: List[ClashQuest], team_b_quests: List[ClashQuest]) -> str:
    """Save clash quests to database"""
    try:
        logger.info(f"💾 Saving clash quests for {team_a_name} vs {team_b_name}")
        
        saved_quest_ids = []
        
        # Save Team A quests
        for quest in team_a_quests:
            quest_id = await create_quest(
                title=quest.title,
                description=quest.description,
                quest_type="clash",
                team_id=team_a_id,
                target_metric="rivalry_actions",
                target_value=quest.target_value
            )
            saved_quest_ids.append(f"A:{quest_id}")
        
        # Save Team B quests
        for quest in team_b_quests:
            quest_id = await create_quest(
                title=quest.title,
                description=quest.description,
                quest_type="clash",
                team_id=team_b_id,
                target_metric="rivalry_actions",
                target_value=quest.target_value
            )
            saved_quest_ids.append(f"B:{quest_id}")
        
        logger.success(f"✅ Saved {len(saved_quest_ids)} clash quests: {saved_quest_ids}")
        return f"SUCCESS|Saved {len(saved_quest_ids)} clash quests: {saved_quest_ids}"
        
    except Exception as e:
        logger.error(f"❌ Error saving clash quests: {e}")
        return f"ERROR|{str(e)}"


# Create the clash quest agent
clash_quest_agent = Agent(
    name="ClashQuestGenerator",
    instructions="""
    You generate clash quests for football team rivalries.
    
    Your workflow:
    1. Search for match information between two teams
    2. Generate opposing quests - one for each team's fans
    3. Save both quests to the database
    
    Focus on:
    - Competitive but friendly rivalry
    - Team pride and support
    - Social media engagement
    - Match predictions and banter
    - Fan community building
    
    Make clash quests exciting, balanced, and engaging for both fan bases.
    """,
    tools=[search_team_match, generate_clash_quests, save_clash_quests],
    output_type=str
)