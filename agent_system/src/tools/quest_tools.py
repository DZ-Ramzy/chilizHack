"""
Quest generation and validation tools for OpenAI Agents
"""
from typing import Dict, Any, List, Optional
import json
import random
from datetime import datetime, timedelta


def generate_quest_content(
    quest_type: str,
    home_team: str,
    away_team: Optional[str] = None,
    event_date: Optional[str] = None,
    user_preferences: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Generate quest content based on type, teams, and user preferences"""
    
    # Get user language preference (default to French)
    language = user_preferences.get("language", "fr") if user_preferences else "fr"
    engagement_level = user_preferences.get("engagement_level", "medium") if user_preferences else "medium"
    
    # Language-specific templates
    templates = {
        "fr": {
            "individual": [
                f"🔥 Montrez votre soutien à {home_team} ! Partagez 5 tweets avec #Allez{home_team.replace(' ', '')} avant le match !",
                f"⚽ Mission {home_team} : Créez du contenu pour encourager l'équipe avant le grand match !",
                f"🏆 Objectif {home_team} : Partagez une story Instagram avec votre prédiction du score !"
            ],
            "clash": [
                f"⚔️ CLASH : {home_team} vs {away_team} ! Qui aura le plus de soutien sur les réseaux ? 100 tweets pour votre équipe !",
                f"🥊 Bataille épique : Fans de {home_team} contre fans de {away_team} ! Qui dominera Twitter ?",
                f"🔥 Défi ultime : {home_team} vs {away_team} - Première équipe à atteindre 1000 posts gagne !"
            ],
            "collective": [
                f"🌍 OBJECTIF COMMUNAUTAIRE : 10,000 tweets #Football avant {event_date} ! Tous ensemble !",
                f"🚀 Mission collective : Faire trending {home_team}vs{away_team} dans le monde entier !",
                f"💪 Défi global : 50,000 interactions sur tous les réseaux avant le coup d'envoi !"
            ]
        },
        "en": {
            "individual": [
                f"🔥 Show your support for {home_team}! Share 5 tweets with #Go{home_team.replace(' ', '')} before the match!",
                f"⚽ {home_team} Mission: Create content to encourage the team before the big match!",
                f"🏆 {home_team} Goal: Share an Instagram story with your score prediction!"
            ],
            "clash": [
                f"⚔️ CLASH: {home_team} vs {away_team}! Who will have the most support on social media? 100 tweets for your team!",
                f"🥊 Epic Battle: {home_team} fans vs {away_team} fans! Who will dominate Twitter?",
                f"🔥 Ultimate Challenge: {home_team} vs {away_team} - First team to reach 1000 posts wins!"
            ],
            "collective": [
                f"🌍 COMMUNITY GOAL: 10,000 #Football tweets before {event_date}! All together!",
                f"🚀 Collective Mission: Make {home_team}vs{away_team} trending worldwide!",
                f"💪 Global Challenge: 50,000 interactions on all platforms before kickoff!"
            ]
        },
        "es": {
            "individual": [
                f"🔥 ¡Muestra tu apoyo a {home_team}! ¡Comparte 5 tweets con #Vamos{home_team.replace(' ', '')} antes del partido!",
                f"⚽ Misión {home_team}: ¡Crea contenido para animar al equipo antes del gran partido!",
                f"🏆 Objetivo {home_team}: ¡Comparte una historia de Instagram con tu predicción del marcador!"
            ],
            "clash": [
                f"⚔️ CLASH: ¡{home_team} vs {away_team}! ¿Quién tendrá más apoyo en las redes? ¡100 tweets para tu equipo!",
                f"🥊 Batalla épica: ¡Fans de {home_team} contra fans de {away_team}! ¿Quién dominará Twitter?",
                f"🔥 Desafío definitivo: {home_team} vs {away_team} - ¡El primer equipo en llegar a 1000 posts gana!"
            ],
            "collective": [
                f"🌍 OBJETIVO COMUNITARIO: ¡10,000 tweets #Football antes del {event_date}! ¡Todos juntos!",
                f"🚀 Misión colectiva: ¡Hacer trending {home_team}vs{away_team} en todo el mundo!",
                f"💪 Desafío global: ¡50,000 interacciones en todas las plataformas antes del inicio!"
            ]
        }
    }
    
    # Get templates for the user's language (fallback to French)
    lang_templates = templates.get(language, templates["fr"])
    
    if quest_type not in lang_templates:
        quest_type = "individual"
    
    content = random.choice(lang_templates[quest_type])
    
    # Generate target metrics based on quest type and engagement level
    base_metrics = {
        "individual": {"metric": "tweets", "value": random.randint(3, 10)},
        "clash": {"metric": "tweets", "value": random.randint(50, 200)},
        "collective": {"metric": "interactions", "value": random.randint(1000, 50000)}
    }
    
    # Adjust target values based on engagement level
    engagement_multipliers = {
        "low": 0.7,
        "medium": 1.0,
        "high": 1.5
    }
    
    multiplier = engagement_multipliers.get(engagement_level, 1.0)
    target_value = int(base_metrics[quest_type]["value"] * multiplier)
    
    target_metrics = {
        "metric": base_metrics[quest_type]["metric"],
        "value": target_value
    }
    
    return {
        "title": content.split("!")[0] + "!",
        "description": content,
        "target_metric": target_metrics["metric"],
        "target_value": target_metrics["value"],
        "hashtags": generate_hashtags(home_team, away_team, language),
        "content_suggestions": generate_content_suggestions(quest_type, home_team, away_team, language),
        "language": language,
        "engagement_level": engagement_level
    }


def generate_hashtags(home_team: str, away_team: Optional[str] = None, language: str = "fr") -> List[str]:
    """Generate relevant hashtags for the quest"""
    
    # Language-specific prefixes
    team_prefixes = {
        "fr": f"Allez{home_team.replace(' ', '')}",
        "en": f"Go{home_team.replace(' ', '')}",
        "es": f"Vamos{home_team.replace(' ', '')}"
    }
    
    hashtags = [
        f"#{home_team.replace(' ', '')}",
        f"#{team_prefixes.get(language, team_prefixes['fr'])}",
        "#SportsQuest",
        "#Football"
    ]
    
    if away_team:
        hashtags.extend([
            f"#{away_team.replace(' ', '')}",
            f"#{home_team.replace(' ', '')}vs{away_team.replace(' ', '')}"
        ])
    
    return hashtags


def generate_content_suggestions(
    quest_type: str, 
    home_team: str, 
    away_team: Optional[str] = None,
    language: str = "fr"
) -> List[str]:
    """Generate content suggestions for users"""
    
    # Language-specific suggestions
    suggestions_by_lang = {
        "fr": [
            f"Partagez votre prédiction du score pour {home_team}",
            f"Postez une photo de votre maillot {home_team}",
            f"Racontez votre meilleur souvenir de {home_team}",
            "Créez un meme de soutien à votre équipe",
            "Partagez les stats de votre joueur préféré"
        ],
        "en": [
            f"Share your score prediction for {home_team}",
            f"Post a photo of your {home_team} jersey",
            f"Tell your best {home_team} memory",
            "Create a meme supporting your team",
            "Share your favorite player's stats"
        ],
        "es": [
            f"Comparte tu predicción del marcador para {home_team}",
            f"Publica una foto de tu camiseta de {home_team}",
            f"Cuenta tu mejor recuerdo de {home_team}",
            "Crea un meme apoyando a tu equipo",
            "Comparte las estadísticas de tu jugador favorito"
        ]
    }
    
    suggestions = suggestions_by_lang.get(language, suggestions_by_lang["fr"])
    
    if quest_type == "clash" and away_team:
        clash_suggestions = {
            "fr": [
                f"Comparez les équipes {home_team} vs {away_team}",
                f"Défendez pourquoi {home_team} va gagner",
                "Créez du contenu pour intimider l'équipe adverse"
            ],
            "en": [
                f"Compare the teams {home_team} vs {away_team}",
                f"Defend why {home_team} will win",
                "Create content to intimidate the opposing team"
            ],
            "es": [
                f"Compara los equipos {home_team} vs {away_team}",
                f"Defiende por qué {home_team} va a ganar",
                "Crea contenido para intimidar al equipo rival"
            ]
        }
        suggestions.extend(clash_suggestions.get(language, clash_suggestions["fr"]))
    
    return suggestions


def validate_quest_content(content: str, validation_rules: Dict[str, Any]) -> Dict[str, Any]:
    """Validate quest content against rules"""
    issues = []
    score = 100
    
    # Check length
    if len(content) < validation_rules.get("min_length", 10):
        issues.append("Content too short")
        score -= 20
    
    if len(content) > validation_rules.get("max_length", 500):
        issues.append("Content too long")
        score -= 15
    
    # Check for inappropriate content (basic checks)
    inappropriate_words = validation_rules.get("blocked_words", [])
    for word in inappropriate_words:
        if word.lower() in content.lower():
            issues.append(f"Inappropriate content detected: {word}")
            score -= 30
    
    # Check for required elements
    required_elements = validation_rules.get("required_elements", [])
    for element in required_elements:
        if element.lower() not in content.lower():
            issues.append(f"Missing required element: {element}")
            score -= 10
    
    return {
        "valid": len(issues) == 0,
        "score": max(0, score),
        "issues": issues,
        "suggestions": generate_improvement_suggestions(issues) if issues else []
    }


def generate_improvement_suggestions(issues: List[str]) -> List[str]:
    """Generate suggestions to improve content"""
    suggestions = []
    
    for issue in issues:
        if "too short" in issue:
            suggestions.append("Add more details about your team support")
        elif "too long" in issue:
            suggestions.append("Make your message more concise")
        elif "inappropriate" in issue:
            suggestions.append("Use positive language to support your team")
        elif "missing" in issue:
            suggestions.append("Include team name or relevant hashtags")
    
    return suggestions


def calculate_quest_difficulty(
    quest_type: str,
    target_value: int,
    time_limit_hours: int = 24
) -> str:
    """Calculate quest difficulty level"""
    
    difficulty_thresholds = {
        "individual": {"easy": 5, "medium": 15, "hard": 30},
        "clash": {"easy": 50, "medium": 150, "hard": 300},
        "collective": {"easy": 1000, "medium": 10000, "hard": 50000}
    }
    
    thresholds = difficulty_thresholds.get(quest_type, difficulty_thresholds["individual"])
    
    # Adjust for time limit
    time_factor = 24 / time_limit_hours if time_limit_hours > 0 else 1
    adjusted_target = target_value * time_factor
    
    if adjusted_target <= thresholds["easy"]:
        return "easy"
    elif adjusted_target <= thresholds["medium"]:
        return "medium"
    else:
        return "hard"