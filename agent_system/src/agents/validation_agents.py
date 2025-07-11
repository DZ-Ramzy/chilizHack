"""
Validation Agents - Content, Image, and Preference validation ensemble
"""
from agents import Agent, function_tool
from ..tools.quest_tools import validate_quest_content
from typing import Dict, Any
import json


@function_tool
def validate_content_tool(
    content: str, 
    team_name: str,
    quest_type: str = "individual"
) -> Dict[str, Any]:
    """Validate quest content for appropriateness and quality"""
    
    validation_rules = {
        "min_length": 20,
        "max_length": 500,
        "blocked_words": ["hate", "violence", "toxic", "spam"],
        "required_elements": [team_name.lower()]
    }
    
    # Adjust rules based on quest type
    if quest_type == "clash":
        validation_rules["required_elements"].append("vs")
    elif quest_type == "collective":
        validation_rules["min_length"] = 30
        validation_rules["required_elements"].extend(["community", "together"])
    
    return validate_quest_content(content, validation_rules)


@function_tool
async def validate_image_content_tool(
    image_description: str,
    team_context: str
) -> Dict[str, Any]:
    """Validate image content using AI (simulated o3-mini validation)"""
    
    # Simulated AI image validation
    issues = []
    score = 100
    
    # Check for team relevance
    if team_context.lower() not in image_description.lower():
        issues.append("Image not relevant to team")
        score -= 25
    
    # Check for inappropriate content indicators
    inappropriate_indicators = ["violence", "offensive", "inappropriate", "spam"]
    for indicator in inappropriate_indicators:
        if indicator in image_description.lower():
            issues.append(f"Inappropriate content detected: {indicator}")
            score -= 40
    
    # Check for quality indicators  
    quality_indicators = ["high quality", "clear", "professional", "engaging"]
    quality_found = any(indicator in image_description.lower() for indicator in quality_indicators)
    if not quality_found:
        score -= 10
    
    return {
        "valid": len(issues) == 0 and score >= 70,
        "score": max(0, score),
        "issues": issues,
        "ai_analysis": {
            "content_safety": score >= 60,
            "team_relevance": team_context.lower() in image_description.lower(),
            "quality_score": score
        }
    }


@function_tool
def validate_preference_consistency_tool(
    user_id: int,
    quest_team_id: int,
    user_team_preferences: list
) -> Dict[str, Any]:
    """Validate that quest aligns with user's team preferences"""
    
    user_team_ids = [pref.get("team_id") for pref in user_team_preferences]
    
    is_consistent = quest_team_id in user_team_ids
    
    # Find conflicting teams if any
    conflicts = []
    if not is_consistent:
        conflicts = [
            pref for pref in user_team_preferences 
            if pref.get("team_id") != quest_team_id
        ]
    
    return {
        "consistent": is_consistent,
        "user_supports_team": is_consistent,
        "conflicts": conflicts,
        "recommendation": "approved" if is_consistent else "redirect_to_user_teams"
    }


# Content Validation Agent
content_validator_agent = Agent(
    name="ContentValidator",
    instructions="""
    You are a content validator for the Sports Quest system.
    
    Your role:
    1. Validate quest content for appropriateness and quality
    2. Check for toxic, inappropriate, or spam content
    3. Ensure content meets community standards
    4. Provide improvement suggestions when needed
    
    Validation criteria:
    - No hate speech, violence, or toxic language
    - Appropriate length and structure
    - Relevant to sports and team context
    - Encourages positive fan engagement
    
    Always provide constructive feedback for content improvements.
    """,
    tools=[validate_content_tool],
)

# Image Validation Agent
image_validator_agent = Agent(
    name="ImageValidator", 
    instructions="""
    You are an image content validator for the Sports Quest system.
    
    Your role:
    1. Validate images for appropriateness and quality using AI analysis
    2. Ensure images are relevant to team and sports context
    3. Check for safety and community standard compliance
    4. Provide quality scores and improvement recommendations
    
    Validation focus:
    - Content safety and appropriateness
    - Team relevance and sports context
    - Image quality and engagement potential
    - Community standards compliance
    
    Use AI analysis to provide objective content assessment.
    """,
    tools=[validate_image_content_tool],
)

# Preference Validation Agent
preference_validator_agent = Agent(
    name="PreferenceValidator",
    instructions="""
    You are a preference consistency validator for the Sports Quest system.
    
    Your role:
    1. Ensure quests align with user team preferences
    2. Prevent sending irrelevant quests to users
    3. Identify potential conflicts in team loyalties
    4. Optimize quest targeting for better engagement
    
    Validation logic:
    - Users should only receive quests for teams they support
    - Identify and flag preference conflicts
    - Recommend quest redistribution when needed
    - Ensure personalization accuracy
    
    Focus on maximizing quest relevance and user satisfaction.
    """,
    tools=[validate_preference_consistency_tool],
)