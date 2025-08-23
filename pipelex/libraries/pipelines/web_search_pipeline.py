import asyncio
from typing import Dict, Any
from pipelex.tools.websearch.web_search import search_web


async def perform_web_search(query: Dict[str, Any]) -> str:
    """
    Perform web search using the web_search module.
    
    Args:
        query: WebSearchQuery object containing search parameters
        
    Returns:
        str: Raw search results from web search
    """
    try:
        # Extract parameters from the query object
        query_text = query.get("query_text", "")
        search_type = query.get("search_type", "search")
        num_results = query.get("num_results", 3)
        api_key = query.get("api_key")
        
        if not query_text:
            return "Error: No query text provided"
        
        # Perform the web search
        result = await search_web(
            query=query_text,
            search_type=search_type,
            num_results=num_results,
            api_key=api_key
        )
        
        return result
        
    except Exception as e:
        return f"Error performing web search: {str(e)}"

