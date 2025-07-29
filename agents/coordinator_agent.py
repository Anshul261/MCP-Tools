"""
Coordinator Agent - Team Orchestration and Query Routing
Implements Level 4 AGNO architecture for multi-agent collaboration
"""

import json
from typing import Dict, Any, List, Optional
from enum import Enum

from .base_agent import BaseAgent


class QueryType(Enum):
    """Classification of query types for routing decisions"""
    DOCUMENT_FOCUSED = "document_focused"
    WEB_FOCUSED = "web_focused"
    HYBRID = "hybrid"
    FACT_CHECK = "fact_check"
    CURRENT_EVENTS = "current_events"
    RESEARCH = "research"


class CoordinatorAgent(BaseAgent):
    """
    Coordinator Agent that orchestrates collaboration between specialist agents
    Following AGNO Level 4 principles: narrow scope agents that reason and collaborate
    """
    
    def __init__(self, document_agent=None, web_agent=None, **kwargs):
        """
        Initialize Coordinator Agent
        
        Args:
            document_agent: Document specialist agent
            web_agent: Web research specialist agent
            **kwargs: Additional arguments passed to BaseAgent
        """
        self.document_agent = document_agent
        self.web_agent = web_agent
        
        # Coordinator specific instructions
        instructions = [
            "You are the Coordinator Agent in a Level 4 Multi-Agent System.",
            "Your role is to orchestrate collaboration between specialist agents.",
            "Analyze queries to determine the optimal routing strategy:",
            "- Document Agent: Internal knowledge, policies, historical data",
            "- Web Agent: Current events, external information, fact-checking",
            "- Both: Comprehensive research requiring multiple perspectives",
            "Always synthesize results from specialists into coherent responses.",
            "Identify contradictions between sources and resolve them appropriately.",
            "Maintain quality control and ensure comprehensive coverage.",
            "Route queries efficiently to minimize response time while maximizing accuracy.",
        ]
        
        super().__init__(
            name="Coordinator Agent",
            agent_id="coordinator",
            instructions=instructions,
            storage_table="coordinator_sessions",
            **kwargs
        )
    
    def classify_query(self, query: str) -> Dict[str, Any]:
        """
        Classify query to determine routing strategy
        
        Args:
            query: User query to classify
            
        Returns:
            Classification results with routing recommendations
        """
        query_lower = query.lower()
        
        # Keywords for different query types
        document_keywords = [
            "leave policy", "policy", "internal", "document", "file", "report", "manual",
            "procedure", "guideline", "specification", "contract", "agreement",
            "company", "ethica", "bank", "employee", "hr", "benefits", "salary"
        ]
        
        web_keywords = [
            "model context protocol", "mcp", "latest", "recent", "current", "news", 
            "today", "2024", "2025", "update", "breaking", "trend", "happening", "new",
            "technology", "ai", "software", "general", "what is", "explain"
        ]
        
        fact_check_keywords = [
            "true", "false", "verify", "check", "accurate", "correct",
            "confirm", "validate", "debunk", "myth"
        ]
        
        research_keywords = [
            "research", "study", "analysis", "compare", "evaluate",
            "comprehensive", "detailed", "investigate", "explore"
        ]
        
        # Score different approaches
        scores = {
            "document": sum(1 for kw in document_keywords if kw in query_lower),
            "web": sum(1 for kw in web_keywords if kw in query_lower),
            "fact_check": sum(1 for kw in fact_check_keywords if kw in query_lower),
            "research": sum(1 for kw in research_keywords if kw in query_lower)
        }
        
        # Determine primary classification
        if scores["fact_check"] > 0:
            query_type = QueryType.FACT_CHECK
            routing = "web_first_then_document"
        elif scores["web"] > scores["document"] and scores["web"] > 1:
            query_type = QueryType.WEB_FOCUSED
            routing = "web_primary"
        elif scores["document"] > scores["web"] and scores["document"] > 1:
            query_type = QueryType.DOCUMENT_FOCUSED
            routing = "document_primary"
        elif scores["research"] > 1:
            query_type = QueryType.RESEARCH
            routing = "both_parallel"
        elif "?" in query and any(kw in query_lower for kw in ["current", "recent", "latest"]):
            query_type = QueryType.CURRENT_EVENTS
            routing = "web_primary"
        else:
            query_type = QueryType.HYBRID
            routing = "document_first_then_web"
        
        return {
            "query_type": query_type.value,
            "routing_strategy": routing,
            "confidence_scores": scores,
            "reasoning": self._get_routing_reasoning(query_type, scores)
        }
    
    def _get_routing_reasoning(self, query_type: QueryType, scores: Dict[str, int]) -> str:
        """Generate human-readable reasoning for routing decision"""
        if query_type == QueryType.DOCUMENT_FOCUSED:
            return "Query appears to seek internal/documented information - prioritizing document search"
        elif query_type == QueryType.WEB_FOCUSED:
            return "Query seeks current/external information - prioritizing web search"
        elif query_type == QueryType.FACT_CHECK:
            return "Query requires verification - using web sources then cross-checking with documents"
        elif query_type == QueryType.RESEARCH:
            return "Comprehensive research query - using both agents in parallel"
        elif query_type == QueryType.CURRENT_EVENTS:
            return "Current events query - prioritizing recent web information"
        else:
            return "Hybrid query - checking documents first, then web for additional context"
    
    async def coordinate_response(self, query: str) -> Dict[str, Any]:
        """
        Coordinate response between specialist agents
        
        Args:
            query: User query to process
            
        Returns:
            Coordinated response with metadata
        """
        # Classify the query
        classification = self.classify_query(query)
        routing_strategy = classification["routing_strategy"]
        
        response_data = {
            "query": query,
            "classification": classification,
            "agents_used": [],
            "responses": {},
            "synthesis": "",
            "metadata": {}
        }
        
        try:
            # Execute routing strategy
            if routing_strategy == "document_primary":
                response_data = await self._route_document_primary(query, response_data)
            elif routing_strategy == "web_primary":
                response_data = await self._route_web_primary(query, response_data)
            elif routing_strategy == "both_parallel":
                response_data = await self._route_both_parallel(query, response_data)
            elif routing_strategy == "document_first_then_web":
                response_data = await self._route_document_first_web_second(query, response_data)
            elif routing_strategy == "web_first_then_document":
                response_data = await self._route_web_first_document_second(query, response_data)
            else:
                response_data = await self._route_hybrid(query, response_data)
            
            # Synthesize final response
            response_data["synthesis"] = self._synthesize_responses(response_data)
            
        except Exception as e:
            response_data["error"] = str(e)
            response_data["synthesis"] = f"Error coordinating response: {e}"
        
        return response_data
    
    async def _route_document_primary(self, query: str, response_data: Dict) -> Dict:
        """Route ONLY to document agent - for company-specific queries"""
        if self.document_agent:
            response_data["agents_used"].append("document_agent")
            doc_response = await self.document_agent.aprocess_query(query)
            response_data["responses"]["document"] = doc_response
            # For document-primary, the synthesis IS the document response
            response_data["synthesis"] = doc_response
        
        return response_data
    
    async def _route_web_primary(self, query: str, response_data: Dict) -> Dict:
        """Route ONLY to web agent - for general/current queries"""
        if self.web_agent:
            response_data["agents_used"].append("web_agent")
            web_response = await self.web_agent.aprocess_query(query)
            response_data["responses"]["web"] = web_response
            # For web-primary, the synthesis IS the web response
            response_data["synthesis"] = web_response
        
        return response_data
    
    async def _route_both_parallel(self, query: str, response_data: Dict) -> Dict:
        """Route to both agents in parallel and synthesize - for comprehensive tasks"""
        import asyncio
        
        tasks = []
        
        if self.document_agent:
            response_data["agents_used"].append("document_agent")
            tasks.append(("document", self.document_agent.aprocess_query(query)))
        
        if self.web_agent:
            response_data["agents_used"].append("web_agent")
            tasks.append(("web", self.web_agent.aprocess_query(query)))
        
        # Run both agents in parallel
        if tasks:
            results = await asyncio.gather(*[task[1] for task in tasks], return_exceptions=True)
            for i, (agent_type, result) in enumerate(zip([task[0] for task in tasks], results)):
                if isinstance(result, Exception):
                    response_data["responses"][agent_type] = f"Error: {result}"
                else:
                    response_data["responses"][agent_type] = result
            
            # Synthesize the responses into one unified answer
            doc_response = response_data["responses"].get("document", "")
            web_response = response_data["responses"].get("web", "")
            
            if doc_response and web_response:
                synthesis = f"""## Comprehensive Response

**Internal Knowledge:**
{doc_response}

**External Research:**
{web_response}

**Synthesis:**
Combining internal documentation with current external information to provide a complete answer based on both established procedures and current best practices."""
                response_data["synthesis"] = synthesis
            elif doc_response:
                response_data["synthesis"] = doc_response
            elif web_response:
                response_data["synthesis"] = web_response
        
        return response_data
    
    async def _route_document_first_web_second(self, query: str, response_data: Dict) -> Dict:
        """Route to documents first, then web with context"""
        if self.document_agent:
            response_data["agents_used"].append("document_agent")
            response_data["responses"]["document"] = await self.document_agent.aprocess_query(query)
        
        if self.web_agent:
            response_data["agents_used"].append("web_agent")
            context = {"document_findings": response_data["responses"].get("document", "")}
            response_data["responses"]["web"] = await self.web_agent.aprocess_query(query, context)
        
        return response_data
    
    async def _route_web_first_document_second(self, query: str, response_data: Dict) -> Dict:
        """Route to web first, then documents for verification"""
        if self.web_agent:
            response_data["agents_used"].append("web_agent")
            response_data["responses"]["web"] = await self.web_agent.aprocess_query(query)
        
        if self.document_agent:
            response_data["agents_used"].append("document_agent")
            context = {"web_findings": response_data["responses"].get("web", "")}
            response_data["responses"]["document"] = await self.document_agent.aprocess_query(query, context)
        
        return response_data
    
    async def _route_hybrid(self, query: str, response_data: Dict) -> Dict:
        """Default hybrid routing"""
        return await self._route_document_first_web_second(query, response_data)
    
    def _needs_web_supplement(self, document_response: str) -> bool:
        """Determine if document response needs web supplementation"""
        insufficient_indicators = [
            "not found", "no information", "unable to find", 
            "insufficient", "outdated", "limited information"
        ]
        return any(indicator in document_response.lower() for indicator in insufficient_indicators)
    
    def _synthesize_responses(self, response_data: Dict) -> str:
        """
        Synthesize responses from multiple agents into coherent answer
        
        Args:
            response_data: Response data from agents
            
        Returns:
            Synthesized response string
        """
        responses = response_data.get("responses", {})
        agents_used = response_data.get("agents_used", [])
        classification = response_data.get("classification", {})
        
        if not responses:
            return "No responses available from agents."
        
        synthesis = f"## Query Analysis\n"
        synthesis += f"**Query Type**: {classification.get('query_type', 'unknown')}\n"
        synthesis += f"**Routing Strategy**: {classification.get('routing_strategy', 'unknown')}\n"
        synthesis += f"**Reasoning**: {classification.get('reasoning', 'N/A')}\n\n"
        
        # Combine responses based on what's available
        if "document" in responses and "web" in responses:
            synthesis += "## Comprehensive Analysis\n\n"
            synthesis += "### Internal Knowledge Base\n"
            synthesis += responses["document"] + "\n\n"
            synthesis += "### External/Current Information\n"
            synthesis += responses["web"] + "\n\n"
            synthesis += "### Synthesis\n"
            synthesis += self._generate_conflict_analysis(responses["document"], responses["web"])
        elif "document" in responses:
            synthesis += "## Document-Based Response\n\n"
            synthesis += responses["document"]
            if self._needs_web_supplement(responses["document"]):
                synthesis += "\n\n*Note: This response is based on internal documents. Current external information may provide additional context.*"
        elif "web" in responses:
            synthesis += "## Web-Based Response\n\n"
            synthesis += responses["web"]
        
        synthesis += f"\n\n---\n*Response coordinated using: {', '.join(agents_used)}*"
        
        return synthesis
    
    def _generate_conflict_analysis(self, doc_response: str, web_response: str) -> str:
        """Analyze potential conflicts between document and web responses"""
        # This is a simplified conflict analysis
        # In a full implementation, this would use NLP to detect contradictions
        
        analysis = "Based on both internal documentation and current web information:\n\n"
        analysis += "- **Internal Perspective**: Provides established policies and documented procedures\n"
        analysis += "- **External Perspective**: Offers current market conditions and recent developments\n\n"
        analysis += "Both sources complement each other to provide a comprehensive view. "
        analysis += "Any discrepancies likely reflect the difference between internal policies and external realities."
        
        return analysis
    
    def get_team_status(self) -> Dict[str, Any]:
        """Get status of the multi-agent team"""
        return {
            "coordinator_active": True,
            "document_agent": {
                "available": bool(self.document_agent),
                "capabilities": self.document_agent.get_capabilities() if self.document_agent else None
            },
            "web_agent": {
                "available": bool(self.web_agent),
                "capabilities": self.web_agent.get_capabilities() if self.web_agent else None
            },
            "routing_strategies": [
                "document_primary",
                "web_primary", 
                "both_parallel",
                "document_first_then_web",
                "web_first_then_document",
                "hybrid"
            ]
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Enhanced capabilities for coordinator agent"""
        base_caps = super().get_capabilities()
        team_status = self.get_team_status()
        
        base_caps.update({
            "specialization": "coordination_and_orchestration",
            "team_management": True,
            "query_classification": True,
            "response_synthesis": True,
            "conflict_resolution": True,
            "team_status": team_status,
            "level": "AGNO_Level_4"
        })
        
        return base_caps