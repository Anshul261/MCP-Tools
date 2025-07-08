"""
Search tools module - Port of MCP search tools to FastAPI-compatible format
"""
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus
import aiohttp
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Configuration
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
BRAVE_BASE_URL = "https://api.search.brave.com/res/v1"

# Search result cache for efficiency
search_cache = {}
cache_ttl = timedelta(hours=1)


class BraveSearchError(Exception):
    """Custom exception for Brave Search API errors"""
    pass


async def make_brave_request(
    endpoint: str,
    params: Dict[str, Any],
    session: aiohttp.ClientSession
) -> Dict[str, Any]:
    """
    Make a request to the Brave Search API with error handling
    """
    if not BRAVE_API_KEY:
        raise BraveSearchError("Brave API key not configured")
    
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": BRAVE_API_KEY
    }
    
    url = f"{BRAVE_BASE_URL}/{endpoint}"
    
    try:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                return await response.json()
            elif response.status == 429:
                raise BraveSearchError("Rate limit exceeded. Please try again later.")
            elif response.status == 401:
                raise BraveSearchError("Invalid API key or authentication failed.")
            elif response.status == 400:
                raise BraveSearchError("Invalid search parameters.")
            else:
                raise BraveSearchError(f"API request failed with status {response.status}")
    except aiohttp.ClientError as e:
        raise BraveSearchError(f"Network error: {str(e)}")


def extract_search_results(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract and format search results from Brave API response
    """
    results = []
    
    # Web results
    if "web" in data and "results" in data["web"]:
        for result in data["web"]["results"]:
            results.append({
                "type": "web",
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "description": result.get("description", ""),
                "snippet": result.get("snippet", ""),
                "age": result.get("age", ""),
                "language": result.get("language", "")
            })
    
    # News results
    if "news" in data and "results" in data["news"]:
        for result in data["news"]["results"]:
            results.append({
                "type": "news",
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "description": result.get("description", ""),
                "age": result.get("age", ""),
                "source": result.get("meta_url", {}).get("hostname", "")
            })
    
    # FAQ results
    if "faq" in data and "results" in data["faq"]:
        for result in data["faq"]["results"]:
            results.append({
                "type": "faq",
                "question": result.get("question", ""),
                "answer": result.get("answer", ""),
                "title": result.get("title", ""),
                "url": result.get("url", "")
            })
    
    return results


def is_cache_valid(timestamp: datetime) -> bool:
    """Check if cached result is still valid"""
    return datetime.now() - timestamp < cache_ttl


async def web_search(
    query: str,
    count: int = 10,
    offset: int = 0,
    country: str = "US",
    search_lang: str = "en",
    freshness: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Perform a web search using Brave Search API
    """
    # Check cache first
    cache_key = f"web:{query}:{count}:{offset}:{country}:{search_lang}:{freshness}"
    if cache_key in search_cache:
        cached_result, timestamp = search_cache[cache_key]
        if is_cache_valid(timestamp):
            logger.info(f"Returning cached result for query: {query}")
            return cached_result
    
    params = {
        "q": query,
        "count": min(max(count, 1), 20),
        "offset": offset,
        "country": country,
        "search_lang": search_lang,
        "result_filter": "web"
    }
    
    if freshness:
        params["freshness"] = freshness
    
    async with aiohttp.ClientSession() as session:
        try:
            data = await make_brave_request("web/search", params, session)
            results = extract_search_results(data)
            
            # Cache the results
            search_cache[cache_key] = (results, datetime.now())
            
            logger.info(f"Found {len(results)} results for query: {query}")
            return results
            
        except BraveSearchError as e:
            logger.error(f"Search failed for query '{query}': {str(e)}")
            return [{"error": str(e), "query": query}]


async def news_search(
    query: str,
    count: int = 10,
    offset: int = 0,
    country: str = "US",
    search_lang: str = "en",
    freshness: str = "pw"
) -> List[Dict[str, Any]]:
    """
    Search for recent news articles using Brave Search API
    """
    # Check cache first
    cache_key = f"news:{query}:{count}:{offset}:{country}:{search_lang}:{freshness}"
    if cache_key in search_cache:
        cached_result, timestamp = search_cache[cache_key]
        if is_cache_valid(timestamp):
            logger.info(f"Returning cached news result for query: {query}")
            return cached_result
    
    params = {
        "q": query,
        "count": min(max(count, 1), 20),
        "offset": offset,
        "country": country,
        "search_lang": search_lang,
        "result_filter": "news",
        "freshness": freshness
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            data = await make_brave_request("web/search", params, session)
            results = extract_search_results(data)
            
            # Filter for news results only
            news_results = [r for r in results if r.get("type") == "news"]
            
            # Cache the results
            search_cache[cache_key] = (news_results, datetime.now())
            
            logger.info(f"Found {len(news_results)} news results for query: {query}")
            return news_results
            
        except BraveSearchError as e:
            logger.error(f"News search failed for query '{query}': {str(e)}")
            return [{"error": str(e), "query": query}]


async def smart_search(
    query: str,
    max_attempts: int = 3,
    result_threshold: int = 5
) -> Dict[str, Any]:
    """
    Intelligent search that tries multiple strategies to find valid results
    """
    search_strategies = [
        {"query": query, "params": {}},
        {"query": f'"{query}"', "params": {}},
        {"query": query, "params": {"freshness": "py"}},
        {"query": query.replace(" ", " AND "), "params": {}},
    ]
    
    search_history = []
    best_results = []
    
    async with aiohttp.ClientSession() as session:
        for attempt, strategy in enumerate(search_strategies[:max_attempts], 1):
            try:
                params = {
                    "q": strategy["query"],
                    "count": 20,
                    "result_filter": "web",
                    **strategy["params"]
                }
                
                logger.info(f"Attempt {attempt}: Searching for '{strategy['query']}'")
                data = await make_brave_request("web/search", params, session)
                results = extract_search_results(data)
                
                search_history.append({
                    "attempt": attempt,
                    "query": strategy["query"],
                    "params": strategy["params"],
                    "result_count": len(results),
                    "success": len(results) >= result_threshold
                })
                
                if len(results) >= result_threshold:
                    best_results = results
                    logger.info(f"Successful search on attempt {attempt} with {len(results)} results")
                    break
                elif len(results) > len(best_results):
                    best_results = results
                    
            except BraveSearchError as e:
                search_history.append({
                    "attempt": attempt,
                    "query": strategy["query"],
                    "params": strategy["params"],
                    "error": str(e),
                    "success": False
                })
                logger.warning(f"Attempt {attempt} failed: {str(e)}")
    
    return {
        "results": best_results,
        "search_metadata": {
            "original_query": query,
            "total_attempts": len(search_history),
            "successful_attempts": sum(1 for h in search_history if h.get("success", False)),
            "final_result_count": len(best_results),
            "search_history": search_history
        }
    }


async def research_search(
    topic: str,
    depth: str = "medium",
    include_academic: bool = True,
    include_news: bool = True,
    time_range: str = "all"
) -> Dict[str, Any]:
    """
    Comprehensive research search combining multiple result types and sources
    """
    depth_configs = {
        "light": {"web_count": 10, "news_count": 5},
        "medium": {"web_count": 15, "news_count": 10},
        "deep": {"web_count": 20, "news_count": 15}
    }
    
    config = depth_configs.get(depth, depth_configs["medium"])
    
    # Determine freshness filter
    freshness_map = {
        "recent": "pm",
        "year": "py",
        "all": None
    }
    freshness = freshness_map.get(time_range)
    
    research_results = {
        "topic": topic,
        "search_strategy": {
            "depth": depth,
            "include_academic": include_academic,
            "include_news": include_news,
            "time_range": time_range
        },
        "results": {}
    }
    
    async with aiohttp.ClientSession() as session:
        # Primary web search
        try:
            web_params = {
                "q": topic,
                "count": config["web_count"],
                "result_filter": "web"
            }
            if freshness:
                web_params["freshness"] = freshness
            
            web_data = await make_brave_request("web/search", web_params, session)
            research_results["results"]["web"] = extract_search_results(web_data)
            
        except BraveSearchError as e:
            research_results["results"]["web"] = [{"error": str(e)}]
        
        # Academic search
        if include_academic:
            try:
                academic_query = f"{topic} site:edu OR site:org OR filetype:pdf OR academic OR research OR study"
                academic_params = {
                    "q": academic_query,
                    "count": 10,
                    "result_filter": "web"
                }
                
                academic_data = await make_brave_request("web/search", academic_params, session)
                research_results["results"]["academic"] = extract_search_results(academic_data)
                
            except BraveSearchError as e:
                research_results["results"]["academic"] = [{"error": str(e)}]
        
        # News search
        if include_news:
            try:
                news_params = {
                    "q": topic,
                    "count": config["news_count"],
                    "result_filter": "news",
                    "freshness": "pm"
                }
                
                news_data = await make_brave_request("web/search", news_params, session)
                research_results["results"]["news"] = extract_search_results(news_data)
                
            except BraveSearchError as e:
                research_results["results"]["news"] = [{"error": str(e)}]
    
    # Calculate summary statistics
    total_results = sum(
        len([r for r in section if "error" not in r]) 
        for section in research_results["results"].values()
    )
    
    research_results["summary"] = {
        "total_results": total_results,
        "sources": list(research_results["results"].keys()),
        "search_completed": datetime.now().isoformat()
    }
    
    return research_results


# Export all tools as a dictionary for easy access
SEARCH_TOOLS = {
    "web_search": web_search,
    "news_search": news_search,
    "smart_search": smart_search,
    "research_search": research_search,
}