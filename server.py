#!/usr/bin/env python3
"""
Brave Search MCP Server

An MCP server that provides comprehensive search capabilities using the Brave Search API.
Includes tools for different search strategies, prompts for efficient searching, 
and robust error handling with retry logic.
"""

# Add this at the very top to catch import errors
print("🔍 Starting server import process...")

try:
    import asyncio
    print("✅ asyncio imported")
    
    import json
    import logging
    import os
    from typing import Any, Dict, List, Optional, Sequence
    from urllib.parse import quote_plus
    print("✅ Standard libraries imported")
    
    import aiohttp
    print("✅ aiohttp imported")
    
    from datetime import datetime, timedelta
    print("✅ datetime imported")

    # Load environment variables from .env file
    from dotenv import load_dotenv
    print("✅ dotenv imported")
    
    load_dotenv()
    print("✅ .env file loaded")

    from mcp.server.fastmcp import FastMCP
    print("✅ FastMCP imported")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)
except Exception as e:
    print(f"❌ Unexpected error during imports: {e}")
    exit(1)

print("🎉 All imports successful!")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("brave-search-mcp")

# Configuration
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
BRAVE_BASE_URL = "https://api.search.brave.com/res/v1"

# Debug: Print API key status (remove this after debugging)
print(f"DEBUG: BRAVE_API_KEY is {'SET' if BRAVE_API_KEY else 'NOT SET'}")
print(f"DEBUG: API key starts with: {BRAVE_API_KEY[:8] + '...' if BRAVE_API_KEY else 'None'}")

if not BRAVE_API_KEY:
    logger.warning("BRAVE_API_KEY environment variable not set")

# Initialize the FastMCP server
mcp = FastMCP("Brave Search API Server")

# Add some logging to show server is initializing
logger.info("🚀 Initializing Brave Search MCP Server...")
logger.info("📡 Server ready to accept connections")

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

@mcp.tool()
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
    
    Args:
        query: Search query string
        count: Number of results to return (1-20)
        offset: Number of results to skip for pagination
        country: Country code for localized results (e.g., "US", "GB", "CA")
        search_lang: Language for search results (e.g., "en", "es", "fr")
        freshness: Time filter ("pd" for past day, "pw" for past week, "pm" for past month, "py" for past year)
    
    Returns:
        List of search results with title, URL, description, and metadata
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
        "count": min(max(count, 1), 20),  # Clamp between 1 and 20
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

@mcp.tool()
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
    
    Args:
        query: Search query string
        count: Number of results to return (1-20)
        offset: Number of results to skip for pagination
        country: Country code for localized results
        search_lang: Language for search results
        freshness: Time filter ("pd" for past day, "pw" for past week, "pm" for past month)
    
    Returns:
        List of news articles with title, URL, description, source, and publication date
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

@mcp.tool()
async def smart_search(
    query: str,
    max_attempts: int = 3,
    result_threshold: int = 5
) -> Dict[str, Any]:
    """
    Intelligent search that tries multiple strategies to find valid results
    
    Args:
        query: Search query string
        max_attempts: Maximum number of search attempts with different strategies
        result_threshold: Minimum number of results considered "successful"
    
    Returns:
        Dictionary containing the best search results and metadata about the search process
    """
    search_strategies = [
        {"query": query, "params": {}},
        {"query": f'"{query}"', "params": {}},  # Exact phrase search
        {"query": query, "params": {"freshness": "py"}},  # Past year results
        {"query": query.replace(" ", " AND "), "params": {}},  # AND search
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

@mcp.tool()
async def research_search(
    topic: str,
    depth: str = "medium",
    include_academic: bool = True,
    include_news: bool = True,
    time_range: str = "all"
) -> Dict[str, Any]:
    """
    Comprehensive research search combining multiple result types and sources
    
    Args:
        topic: Research topic or question
        depth: Search depth ("light", "medium", "deep")
        include_academic: Whether to include academic and scholarly sources
        include_news: Whether to include recent news articles
        time_range: Time range for results ("recent", "year", "all")
    
    Returns:
        Comprehensive research results organized by source type
    """
    depth_configs = {
        "light": {"web_count": 10, "news_count": 5},
        "medium": {"web_count": 15, "news_count": 10},
        "deep": {"web_count": 20, "news_count": 15}
    }
    
    config = depth_configs.get(depth, depth_configs["medium"])
    
    # Determine freshness filter
    freshness_map = {
        "recent": "pm",  # Past month
        "year": "py",    # Past year
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
        
        # Academic search (using specific academic terms)
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
                    "freshness": "pm"  # Past month for news
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

# PROMPTS - Intelligent search templates

@mcp.prompt()
def debugging_search_prompt(
    error_message: str,
    programming_language: str = "",
    framework: str = "",
    context: str = ""
) -> str:
    """
    Generate an effective search strategy for debugging programming issues
    
    Args:
        error_message: The error message or issue description
        programming_language: Programming language being used
        framework: Framework or library being used
        context: Additional context about the problem
    """
    
    # Create targeted search queries for debugging
    search_queries = []
    
    # Base error search
    base_query = f'"{error_message}"'
    if programming_language:
        base_query += f" {programming_language}"
    if framework:
        base_query += f" {framework}"
    search_queries.append(base_query)
    
    # Alternative searches
    if programming_language:
        search_queries.append(f"{programming_language} {error_message} solution")
        search_queries.append(f"{programming_language} {error_message} fix")
    
    if framework:
        search_queries.append(f"{framework} {error_message}")
    
    # Stack Overflow specific search
    stackoverflow_query = f"site:stackoverflow.com {error_message}"
    if programming_language:
        stackoverflow_query += f" {programming_language}"
    search_queries.append(stackoverflow_query)
    
    prompt_content = f"""# Debugging Search Strategy

## Problem Analysis
- **Error Message**: {error_message}
- **Programming Language**: {programming_language or 'Not specified'}
- **Framework**: {framework or 'Not specified'}
- **Context**: {context or 'Not provided'}

## Recommended Search Queries

Here are optimized search queries to help you find solutions:

"""
    
    for i, query in enumerate(search_queries, 1):
        prompt_content += f"{i}. `{query}`\n"
    
    prompt_content += """
## Search Tips

1. **Start with the exact error message** in quotes for precise matches
2. **Add your programming language** to filter relevant results
3. **Include framework/library names** if applicable
4. **Check Stack Overflow first** for community solutions
5. **Look for official documentation** and GitHub issues
6. **Try variations** of the error message if no results found

## Suggested Tools

Use these MCP tools for your search:
- `web_search()` for general searches
- `smart_search()` for persistent searching with multiple strategies
- `research_search()` for comprehensive investigation

## Next Steps

1. Try the first search query
2. If no results, move to the next query
3. Look for recent solutions (past year)
4. Check official documentation
5. Consider similar error patterns
"""
    
    return prompt_content

@mcp.prompt()
def research_strategy_prompt(
    research_question: str,
    domain: str = "",
    depth_level: str = "medium",
    time_sensitivity: str = "balanced"
) -> str:
    """
    Generate a comprehensive research strategy for any topic or question
    
    Args:
        research_question: The main research question or topic
        domain: Subject domain (e.g., "technology", "medicine", "business")
        depth_level: Research depth ("overview", "medium", "comprehensive")
        time_sensitivity: Time focus ("current", "historical", "balanced")
    """
    
    # Analyze the research question
    question_type = "general"
    if "?" in research_question:
        if research_question.lower().startswith(("what", "how", "why", "when", "where", "who")):
            question_type = "factual"
        elif "compare" in research_question.lower() or "vs" in research_question.lower():
            question_type = "comparative"
        elif "trend" in research_question.lower() or "future" in research_question.lower():
            question_type = "trend_analysis"
    
    # Generate search strategy based on parameters
    search_strategies = {
        "overview": {
            "web_searches": 2,
            "news_searches": 1,
            "academic_focus": False
        },
        "medium": {
            "web_searches": 3,
            "news_searches": 2,
            "academic_focus": True
        },
        "comprehensive": {
            "web_searches": 5,
            "news_searches": 3,
            "academic_focus": True
        }
    }
    
    strategy = search_strategies.get(depth_level, search_strategies["medium"])
    
    prompt_content = f"""# Research Strategy: {research_question}

## Research Analysis
- **Question Type**: {question_type.replace('_', ' ').title()}
- **Domain**: {domain or 'General'}
- **Depth Level**: {depth_level.title()}
- **Time Focus**: {time_sensitivity.title()}

## Recommended Search Approach

### Phase 1: Foundation Research
"""
    
    if question_type == "factual":
        prompt_content += """
1. **Direct Search**: Search for the exact question or key terms
2. **Authoritative Sources**: Look for official sources, encyclopedias, verified data
3. **Cross-Reference**: Verify information across multiple reliable sources
"""
    elif question_type == "comparative":
        prompt_content += """
1. **Individual Research**: Research each item/concept separately first
2. **Comparison Search**: Search for direct comparisons and versus articles
3. **Expert Analysis**: Look for professional analysis and reviews
"""
    elif question_type == "trend_analysis":
        prompt_content += """
1. **Current State**: Research the present situation
2. **Historical Context**: Understand past trends and patterns
3. **Future Projections**: Look for expert predictions and analysis
"""
    else:
        prompt_content += """
1. **Broad Overview**: Start with general searches to understand the topic
2. **Specific Aspects**: Dive deeper into particular aspects
3. **Multiple Perspectives**: Gather different viewpoints and approaches
"""
    
    prompt_content += f"""
### Phase 2: Deep Investigation

**Recommended Tools and Queries:**

1. **Primary Search**:
   ```
   research_search(
       topic="{research_question}",
       depth="{depth_level}",
       include_academic={str(strategy['academic_focus']).lower()},
       include_news={str(time_sensitivity in ['current', 'balanced']).lower()},
       time_range="{'recent' if time_sensitivity == 'current' else 'all'}"
   )
   ```

2. **Targeted Searches** (try {strategy['web_searches']} variations):
   - "{research_question}"
   - {research_question.replace('?', '')} analysis
   - {research_question.replace('?', '')} expert opinion
"""
    
    if domain:
        prompt_content += f"   - {research_question.replace('?', '')} {domain}\n"
    
    if time_sensitivity == "current":
        prompt_content += f"""
3. **Recent Developments**:
   ```
   news_search(
       query="{research_question}",
       freshness="pw",
       count=10
   )
   ```
"""
    
    prompt_content += """
### Phase 3: Verification and Synthesis

1. **Source Quality Check**:
   - Verify credibility of sources
   - Look for peer-reviewed content
   - Check publication dates
   - Cross-reference facts

2. **Gap Analysis**:
   - Identify missing information
   - Note conflicting viewpoints
   - Find areas needing more research

3. **Synthesis Preparation**:
   - Organize findings by theme
   - Note source reliability
   - Prepare balanced summary

## Quality Indicators

**Good Sources Look For**:
- Recent publication dates (if current info needed)
- Author credentials and expertise
- Peer review or editorial oversight
- Citation of other reliable sources
- Balanced presentation of information

**Red Flags to Avoid**:
- Outdated information (unless historical research)
- Unclear authorship
- Extreme bias without balance
- Lack of supporting evidence
- Poor source citations

## Recommended MCP Tools Sequence

1. `research_search()` for comprehensive initial research
2. `smart_search()` for persistent searching if results are sparse
3. `news_search()` for current developments and recent information
4. `web_search()` for specific follow-up queries

## Success Metrics

- **Coverage**: Multiple perspectives and sources represented
- **Reliability**: High-quality, credible sources prioritized
- **Relevance**: Information directly addresses the research question
- **Recency**: Up-to-date information when time-sensitive
- **Depth**: Sufficient detail for the intended depth level
"""
    
    return prompt_content

@mcp.prompt()
def fact_check_prompt(
    claim: str,
    urgency: str = "normal",
    source_preference: str = "balanced"
) -> str:
    """
    Generate a systematic fact-checking strategy for verifying claims
    
    Args:
        claim: The statement or claim to fact-check
        urgency: Urgency level ("low", "normal", "high")
        source_preference: Source preference ("official", "academic", "news", "balanced")
    """
    
    prompt_content = f"""# Fact-Check Strategy: {claim}

## Claim Analysis
- **Statement**: {claim}
- **Urgency Level**: {urgency.title()}
- **Source Preference**: {source_preference.title()}

## Verification Strategy

### Step 1: Direct Verification
Search for the exact claim and direct refutations:

```
web_search(
    query='"{claim}"',
    count=15,
    freshness="pm"
)
```

### Step 2: Authority Sources
"""
    
    if source_preference in ["official", "balanced"]:
        prompt_content += f"""
**Official Sources Search**:
```
web_search(
    query="{claim} site:gov OR site:edu OR official",
    count=10
)
```
"""
    
    if source_preference in ["academic", "balanced"]:
        prompt_content += f"""
**Academic Sources Search**:
```
web_search(
    query="{claim} scholarly research study academic",
    count=10
)
```
"""
    
    if source_preference in ["news", "balanced"]:
        prompt_content += f"""
**News and Media Analysis**:
```
news_search(
    query="{claim}",
    freshness="pw",
    count=10
)
```
"""
    
    prompt_content += f"""
### Step 3: Counterargument Research
```
web_search(
    query="{claim} false debunked myth",
    count=10
)
```

### Step 4: Fact-Checking Sites
```
web_search(
    query="{claim} site:snopes.com OR site:factcheck.org OR site:politifact.com",
    count=10
)
```

## Evaluation Framework

### Source Credibility Checklist
- [ ] **Author/Organization**: Clearly identified and reputable
- [ ] **Publication Date**: Recent enough to be relevant
- [ ] **Citations**: Includes references and sources
- [ ] **Methodology**: Clear research or reporting methods
- [ ] **Bias Check**: Consider potential conflicts of interest

### Evidence Quality
- [ ] **Primary Sources**: Original research, documents, or data
- [ ] **Secondary Sources**: Analysis or reporting of primary sources
- [ ] **Expert Opinion**: Qualified specialists in relevant field
- [ ] **Consensus**: Agreement among multiple reliable sources

### Red Flags
- [ ] **No author or unclear authorship**
- [ ] **Extreme bias or emotional language**
- [ ] **Lack of supporting evidence**
- [ ] **Outdated information**
- [ ] **Known unreliable source**

## Verification Levels

### High Confidence
- Multiple authoritative sources confirm
- Primary evidence available
- Expert consensus exists
- No credible contradictions

### Medium Confidence
- Some reliable sources confirm
- Limited primary evidence
- Some expert support
- Minor contradictions exist

### Low Confidence
- Few or questionable sources
- Lack of primary evidence
- No clear expert consensus
- Significant contradictions

### Insufficient Evidence
- Very few sources
- No reliable verification
- Conflicting information
- More research needed

## Recommended MCP Tool Sequence

1. **Initial Search**: `web_search()` with exact claim in quotes
2. **Authority Check**: `web_search()` with official/academic modifiers
3. **Counter-research**: `web_search()` looking for refutations
4. **Comprehensive Review**: `research_search()` for thorough analysis
5. **Recent Updates**: `news_search()` for latest developments

## Documentation Template

**Claim**: {claim}

**Verification Status**: [High/Medium/Low Confidence | Insufficient Evidence]

**Key Findings**:
- Supporting Evidence: [List sources that confirm]
- Contradicting Evidence: [List sources that refute]
- Expert Opinion: [Relevant expert statements]

**Source Summary**:
- Total sources reviewed: [Number]
- Authoritative sources: [Number]
- Quality assessment: [Brief evaluation]

**Conclusion**: [Summary of verification results]

**Last Updated**: [Date of fact-check]
"""
    
    return prompt_content

if __name__ == "__main__":
    mcp.run()