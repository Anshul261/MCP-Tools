# Brave Search MCP Server - LLM Developer Guide

## 📋 Project Overview

**Purpose**: A comprehensive MCP (Model Context Protocol) server that provides intelligent search capabilities using the Brave Search API.

**Architecture Pattern**: FastMCP-based server with tools (model-controlled) and prompts (user-controlled)

**Key Value Proposition**: 
- Smart search with retry logic and multiple strategies
- Intelligent prompts that guide effective search workflows
- Caching for API efficiency
- Robust error handling

---

## 🏗️ Code Architecture

### **File Structure**
```
server.py                 # Main server file (all-in-one design)
requirements.txt          # Python dependencies
.env                      # Environment variables (API keys)
example.env              # Template for environment setup
README.md                # User-facing documentation
```

### **Core Components**

#### 1. **Server Initialization** (Lines 1-70)
```python
# Pattern: FastMCP server with environment validation
mcp = FastMCP("Brave Search API Server")
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
```

**Key Design Decision**: All-in-one file approach for simplicity and easy deployment.

#### 2. **API Client Layer** (Lines 71-150)
```python
async def make_brave_request(endpoint, params, session)
def extract_search_results(data)
```

**Pattern**: Async HTTP client with comprehensive error handling
**Responsibilities**: 
- API authentication
- Request/response handling
- Data transformation
- Error mapping to user-friendly messages

#### 3. **Caching System** (Lines 51-60)
```python
search_cache = {}
cache_ttl = timedelta(hours=1)
def is_cache_valid(timestamp)
```

**Pattern**: Simple in-memory cache with TTL
**Key Feature**: Reduces API calls and improves response time

#### 4. **Tools Layer** (Lines 151-400)
Four main tools following the `@mcp.tool()` decorator pattern:

- `web_search()` - Basic search with caching
- `news_search()` - News-specific search  
- `smart_search()` - Multi-strategy intelligent search
- `research_search()` - Comprehensive multi-source research

#### 5. **Prompts Layer** (Lines 401-700)
Three strategic prompts following the `@mcp.prompt()` pattern:

- `debugging_search_prompt()` - Programming issue resolution
- `research_strategy_prompt()` - Academic/business research planning
- `fact_check_prompt()` - Systematic claim verification

---

## 🔧 Extension Patterns

### **Adding New Tools**

**Template Pattern**:
```python
@mcp.tool()
async def new_tool_name(
    param1: str,
    param2: int = 10,
    optional_param: Optional[str] = None
) -> ReturnType:
    """
    Clear description of what this tool does
    
    Args:
        param1: Description of required parameter
        param2: Description with default value
        optional_param: Description of optional parameter
    
    Returns:
        Description of return value structure
    """
    # 1. Input validation
    if not param1:
        return {"error": "param1 is required"}
    
    # 2. Cache check (if applicable)
    cache_key = f"tool_name:{param1}:{param2}"
    if cache_key in search_cache:
        cached_result, timestamp = search_cache[cache_key]
        if is_cache_valid(timestamp):
            return cached_result
    
    # 3. API interaction
    async with aiohttp.ClientSession() as session:
        try:
            # API call logic
            result = await make_brave_request(endpoint, params, session)
            
            # 4. Cache result
            search_cache[cache_key] = (result, datetime.now())
            
            # 5. Return processed result
            return result
            
        except BraveSearchError as e:
            logger.error(f"Tool failed: {str(e)}")
            return {"error": str(e)}
```

### **Adding New Prompts**

**Template Pattern**:
```python
@mcp.prompt()
def new_prompt_name(
    main_param: str,
    context_param: str = "",
    options_param: str = "default"
) -> str:
    """
    Description of what this prompt generates
    
    Args:
        main_param: Primary input for the prompt
        context_param: Additional context
        options_param: Configuration options
    """
    
    # 1. Input analysis
    analysis_result = analyze_input(main_param)
    
    # 2. Strategy generation based on analysis
    if analysis_result == "type_a":
        strategy = generate_strategy_a()
    elif analysis_result == "type_b":
        strategy = generate_strategy_b()
    else:
        strategy = generate_default_strategy()
    
    # 3. Prompt construction
    prompt_content = f"""# Prompt Title: {main_param}

## Analysis
- **Input Type**: {analysis_result}
- **Context**: {context_param or 'Not provided'}
- **Options**: {options_param}

## Recommended Approach
{strategy}

## Tool Recommendations
- Use `tool_name()` for specific_purpose
- Use `other_tool()` for other_purpose

## Expected Outcomes
- Outcome 1
- Outcome 2
"""
    
    return prompt_content
```

---

## 🎯 Key Design Patterns

### **1. Error Handling Pattern**
```python
try:
    result = await api_operation()
    return success_response(result)
except SpecificAPIError as e:
    logger.error(f"Specific error context: {str(e)}")
    return {"error": "User-friendly error message"}
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
    return {"error": "General error message"}
```

### **2. Caching Pattern**
```python
# Check cache
cache_key = f"operation:{param1}:{param2}"
if cache_key in search_cache:
    cached_result, timestamp = search_cache[cache_key]
    if is_cache_valid(timestamp):
        return cached_result

# Perform operation
result = await expensive_operation()

# Cache result
search_cache[cache_key] = (result, datetime.now())
return result
```

### **3. Multi-Strategy Pattern** (see `smart_search`)
```python
strategies = [
    {"query": query, "params": {}},
    {"query": f'"{query}"', "params": {}},  # Exact phrase
    {"query": query, "params": {"freshness": "py"}},  # Time filter
]

for attempt, strategy in enumerate(strategies):
    result = await try_strategy(strategy)
    if result_is_good_enough(result):
        return result
    
return best_result_so_far
```

---

## 🔍 Understanding the API Integration

### **Brave Search API Endpoints**
- **Base URL**: `https://api.search.brave.com/res/v1`
- **Main Endpoint**: `/web/search`
- **Authentication**: `X-Subscription-Token` header

### **API Response Structure**
```python
{
    "web": {
        "results": [
            {
                "title": "Page title",
                "url": "https://example.com",
                "description": "Page description",
                "snippet": "Content snippet",
                "age": "2024-01-01T00:00:00Z",
                "language": "en"
            }
        ]
    },
    "news": {
        "results": [...]
    },
    "faq": {
        "results": [...]
    }
}
```

### **Parameter Mapping**
- `q`: Search query
- `count`: Results per page (1-20)
- `offset`: Pagination offset  
- `country`: Localization (US, GB, CA, etc.)
- `search_lang`: Language filter (en, es, fr, etc.)
- `freshness`: Time filter (pd, pw, pm, py)
- `result_filter`: Content type (web, news, videos)

---

## 🧪 Testing and Development

### **Testing Individual Functions**
```python
# Test API client
async def test_api():
    async with aiohttp.ClientSession() as session:
        result = await make_brave_request("web/search", {"q": "test"}, session)
        print(result)

# Test tools
result = await web_search("test query", count=5)
print(result)

# Test prompts
prompt = debugging_search_prompt("TypeError: 'NoneType' object is not subscriptable", "Python", "FastAPI")
print(prompt)
```

### **Adding Debug Information**
```python
# Add debug logging to any function
logger.info(f"Function called with params: {locals()}")
logger.debug(f"Intermediate result: {intermediate_value}")
```

### **Environment Setup for Development**
```bash
# 1. Install dependencies
pip install mcp aiohttp python-dotenv

# 2. Set up environment
echo "BRAVE_API_KEY=your_key_here" > .env

# 3. Test the server
python server.py

# 4. Test with Inspector
mcp dev server.py
```

---

## 📚 Dependencies and Requirements

### **Core Dependencies**
```python
# FastMCP framework
from mcp.server.fastmcp import FastMCP

# Async HTTP client
import aiohttp

# Environment management
from dotenv import load_dotenv

# Standard library
import asyncio, json, logging, os
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus
from datetime import datetime, timedelta
```

### **Understanding Dependency Roles**
- **FastMCP**: Handles MCP protocol, tool/prompt registration, client communication
- **aiohttp**: Async HTTP client for Brave API calls
- **dotenv**: Environment variable management for API keys
- **typing**: Type hints for better code clarity and IDE support

---

## 🚀 Deployment Considerations

### **Environment Variables**
```bash
# Required
BRAVE_API_KEY=your_brave_search_api_key

# Optional configurations
SEARCH_DEFAULT_COUNT=10
CACHE_TTL_HOURS=1
LOG_LEVEL=INFO
```

### **Performance Optimization**
1. **Caching**: Implemented for 1-hour TTL
2. **Async Operations**: All API calls are async
3. **Error Handling**: Graceful degradation
4. **Rate Limiting**: Can be added as shown above

### **Security Considerations**
1. **API Key Protection**: Never log or expose API keys
2. **Input Validation**: Validate all user inputs
3. **Error Messages**: Don't expose internal details
4. **Rate Limiting**: Prevent API abuse

---

## 🎭 Prompt Engineering Guidelines

### **Effective Prompt Structure**
1. **Clear Title**: Descriptive heading
2. **Analysis Section**: Break down the user's input
3. **Strategy Section**: Step-by-step approach
4. **Tool Recommendations**: Specific MCP tools to use
5. **Expected Outcomes**: What success looks like

### **Prompt Content Patterns**
```python
f"""# {Title}: {user_input}

## Analysis
- **Input Type**: {analyzed_type}
- **Context**: {context_info}
- **Requirements**: {requirements}

## Recommended Approach

### Phase 1: {phase_name}
{phase_instructions}

### Phase 2: {phase_name}
{phase_instructions}

## Tool Usage
1. `tool_name(param="{example}")` for {purpose}
2. `other_tool(param="{example}")` for {other_purpose}

## Success Criteria
- {criterion_1}
- {criterion_2}
"""
```

---

## 🔧 Troubleshooting Guide for LLMs

### **Common Issues and Solutions**

1. **Import Errors**
   - Check FastMCP installation: `pip install mcp`
   - Verify Python version >= 3.8

2. **API Key Issues**
   - Ensure `.env` file exists and is loaded
   - Check `BRAVE_API_KEY` is set correctly

3. **Connection Issues**
   - WSL users: Use WSL IP address instead of localhost
   - Check firewall settings
   - Verify port 6274 is available

4. **Cache Issues**
   - Clear cache: `search_cache.clear()`
   - Adjust TTL: `cache_ttl = timedelta(hours=X)`

### **Debug Mode Activation**
```python
# Add to server.py for debugging
logging.basicConfig(level=logging.DEBUG)
logger.setLevel(logging.DEBUG)

# Add debug prints
print(f"DEBUG: Function {function_name} called with {params}")
```

---

## 🎯 Best Practices for LLM Modifications

1. **Follow Existing Patterns**: Use the established patterns for tools, prompts, and error handling

2. **Maintain Type Hints**: Always include proper type annotations

3. **Add Logging**: Include appropriate logging for new functionality

4. **Error Handling**: Implement comprehensive error handling

5. **Documentation**: Update docstrings and comments

6. **Testing**: Test new features with MCP Inspector

7. **Caching**: Consider caching for expensive operations

8. **User Experience**: Ensure error messages are user-friendly

---

## 📝 Quick Reference

### **Adding a Simple Tool**
```python
@mcp.tool()
async def tool_name(param: str) -> Dict[str, Any]:
    """Tool description"""
    # Implementation
    return {"result": "value"}
```

### **Adding a Simple Prompt**
```python
@mcp.prompt()
def prompt_name(input_param: str) -> str:
    """Prompt description"""
    return f"Prompt content with {input_param}"
```

### **API Call Pattern**
```python
async with aiohttp.ClientSession() as session:
    try:
        data = await make_brave_request(endpoint, params, session)
        return process_results(data)
    except BraveSearchError as e:
        return {"error": str(e)}
```

---

This README provides comprehensive guidance for LLMs to understand, modify, and extend the Brave Search MCP server effectively. The patterns and examples should enable confident code modifications while maintaining the existing architecture and quality standards.