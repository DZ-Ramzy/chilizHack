"""
Web Search Tools - Utilise l'outil WebSearch disponible pour la recherche d'actualités
"""
from loguru import logger

async def search_web_content(query: str) -> str:
    """Search web content using the available WebSearch tool"""
    try:
        logger.info(f"🔍 Searching web for: {query}")
        
        # Direct import and use of WebSearch tool function
        # This will be replaced by actual WebSearch function call
        from anthropic_tools import WebSearch
        
        # Use WebSearch with a prompt to extract football news
        search_result = WebSearch(
            query=query,
            prompt=f"Extract football news, match results, transfer information, and player updates from the search results for the query: {query}"
        )
        
        logger.success(f"✅ Web search completed for: {query}")
        return search_result
        
    except ImportError:
        # Fallback if WebSearch tool is not available
        logger.warning(f"⚠️ WebSearch tool not available, using fallback for: {query}")
        return f"No search results available for: {query}"
        
    except Exception as e:
        logger.error(f"❌ Error in web search for '{query}': {e}")
        return f"Search error for: {query}"