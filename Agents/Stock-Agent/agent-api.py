from textwrap import dedent
from agno.models.azure import AzureOpenAI
from agno.agent import Agent
from rich.console import Console
from rich.panel import Panel
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools
from agno.tools.yfinance import YFinanceTools
import os
from dotenv import load_dotenv
from agno.team import Team
from agno.tools.reasoning import ReasoningTools
from agno.os import AgentOS
from agno.models.ollama import Ollama

load_dotenv()
console = Console()
from agno.db.sqlite import SqliteDb
# db_url = "postgresql+psycopg://ai:ai@localhost:5533/ai"
# db = PostgresDb(db_url=db_url)

db = SqliteDb(db_file="tmp/data.db")

def get_model():
    return AzureOpenAI(
        id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    )

def get_model_gpt5():
    return AzureOpenAI(
        id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME_5"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY_5"),
        api_version="2025-03-01-preview",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_5"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    )


def get_model_ollama():
    return Ollama(id="gpt-oss:20b")


# Combined Intelligence Analyst
intelligence_analyst = Agent(
    model=get_model(),
    tools=[YFinanceTools(), DuckDuckGoTools(), Newspaper4kTools()],
    description=dedent("""
        I gather current market data, news, and financial metrics for stocks
    """),
    instructions=dedent("""
        "Get current stock data, recent news, and key financial metrics",
        "Focus on facts and data, not opinions",
        "Check memory for previous analysis of this stock",
        "Highlight what's changed since last analysis"
    """),
    expected_output="Integrated intelligence report covering technical, fundamental, news, and sentiment factors",
    markdown=True,
)

# Bull vs Bear Debate Agent
bull_bear_analyst = Agent(
    model=get_model(),
    tools=[ReasoningTools()],
    description=dedent("""
        You are a debate analyst who presents both bullish and bearish cases,
        then synthesizes them into a balanced investment thesis.
    """),
    instructions=dedent("""
        Based on the intelligence analysis, present:

        1. BULL CASE (2-3 strongest arguments):
        - Key growth drivers and catalysts
        - Competitive advantages
        - Undervaluation or momentum factors

        2. BEAR CASE (2-3 strongest concerns):
        - Primary risk factors
        - Overvaluation concerns
        - Competitive or regulatory threats

        3. SYNTHESIS:
        - Which case is stronger and why
        - Key factors that will determine outcome
        - Probability-weighted scenarios

        Be decisive but balanced. Focus on the most compelling arguments.
    """),
    expected_output="Bull/bear debate with synthesized investment thesis and key decision factors",
    markdown=True,
)

# Trading & Risk Manager
trading_manager = Agent(
    model=get_model(),
    tools=[YFinanceTools(), ReasoningTools()],
    description=dedent("""
        You are a trading and risk manager who makes final investment decisions
        and provides specific execution guidance.
    """),
    instructions=dedent("""
        "Analyze the market data provided by other team members",
        "Consider both bullish and bearish perspectives",
        "Reference past predictions and their outcomes from memory",
        "Consider user risk tolerance and preferences from memory",
        "Provide clear, actionable investment advice",
        "Be decisive but explain your reasoning"
    """),
    expected_output="Final investment decision with position sizing, entry/exit strategy, and monitoring plan",
    markdown=True,
)

fast_stock_team = Team(
    name="Fast Stock Analysis Team",
    db=db,
    model=get_model(),
    members=[intelligence_analyst, bull_bear_analyst, trading_manager],
    tools=[ReasoningTools()],
    instructions=[
        """
        SIMPLE MISSION: Answer the user's stock question accurately and quickly.

        APPROACH:
        - If user asks about a stock, get current data and provide analysis
        - Remember what we've analyzed before to avoid redundant work
        - Learn from past recommendations to improve accuracy
        - Give direct, actionable answers to what the user actually asks
        - Work together efficiently - don't overcomplicate simple questions

        MEMORY USAGE:
        - Check if we've analyzed this stock recently
        - Reference past prediction accuracy
        - Remember user preferences and risk tolerance
        - Build knowledge of successful patterns over time

        OUTPUT:
        Direct answer to user's question with relevant analysis and clear recommendation when appropriate.
"""
    ],
    enable_user_memories=True,
    enable_session_summaries=True,
    enable_agentic_memory=True,
    markdown=True,
    cache_session=True,
    tool_call_limit=10,
    share_member_interactions=True,
    stream_intermediate_steps=True,
    add_datetime_to_context=True,
    add_name_to_context=True,
    add_member_tools_to_context=True,
    add_history_to_context=True,
    num_history_runs=3,
    stream=True,
)

agent_os = AgentOS(
    description="Stock Analysis AgentOS",
    agents=[intelligence_analyst, bull_bear_analyst, trading_manager],
    teams=[fast_stock_team],
)
app = agent_os.get_app()

# Add CORS middleware for Next.js UI
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
    ],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    """Run our AgentOS with Stock Analysis.

    AgentOS UI: http://localhost:7777/
    Next.js UI: http://localhost:3000/ (run separately)
    API Docs: http://localhost:7777/docs
    """
    console.print(Panel.fit("Stock Analysis AgentOS", style="bold green"))
    console.print("AgentOS UI: http://localhost:7777/")
    console.print("Chat API: http://localhost:7777/api/chat")
    console.print("API Docs: http://localhost:7777/docs")
    console.print("Next.js UI: http://localhost:3000/ (run separately)")

    agent_os.serve(app="agent-api:app", host="0.0.0.0", port=7777, reload=True)
