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
from agno.db.postgres import PostgresDb

load_dotenv()
console = Console()

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
db = PostgresDb(db_url=db_url)

def get_model():
    return AzureOpenAI(
        id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    )

# Combined Intelligence Analyst (replaces 4 separate analysts)
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

# Bull vs Bear Debate Agent (replaces 3 separate debate agents)
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

# Trading & Risk Manager (replaces 3 separate execution agents)
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

# STREAMLINED STOCK ANALYSIS TEAM (with memory preserved)
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
    # Memory features restored - critical for institutional knowledge
    enable_user_memories=True,
    enable_session_summaries=True,
    enable_agentic_memory=True,
    markdown=True,
    cache_session= True,
    tool_call_limit=10,
    share_member_interactions=True,
    stream_intermediate_steps=True,
    add_datetime_to_context=True,  # Critical for financial analysis
    add_name_to_context=True,  # Helps with team coordination
    add_member_tools_to_context=True,  # Default but verify

    add_history_to_context=True,
    num_history_runs=3,
    stream=True
)

def main():
    console.print(Panel.fit("Fast Stock Analysis Team Ready (With Memory)", style="bold green"))
    console.print("Welcome! I'm your AI Stock Analysis Team with institutional memory.")
    console.print("I learn from past analyses and track prediction accuracy over time.")
    console.print("Provide a stock ticker for rapid analysis.")
    console.print("Example: 'Analyze NVDA' or 'Quick analysis of TSLA'")
    console.print("Type 'quit' to exit.\n")

    while True:
        try:
            question = input("You: ").strip()
            
            if question.lower() in ['quit', 'exit', 'bye']:
                console.print("[green]Analysis session ended![/green]")
                break
                
            if not question:
                continue
                
            console.print("[blue]Fast analysis in progress (checking memory for previous insights)...[/blue]")
            
            # Start timing
            import time
            start_time = time.time()
            
            # Use print_response for streaming with memory integration
            fast_stock_team.print_response(question)
            
            # Calculate and display timing
            end_time = time.time()
            duration = end_time - start_time
            
            console.print(f"\n[green]Analysis completed in {duration:.1f} seconds[/green]")
            console.print("[dim]Memory updated with new insights for future reference[/dim]")
            
        except KeyboardInterrupt:
            console.print("\n[green]Analysis session ended![/green]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            console.print("Please try a different question.")

if __name__ == "__main__":
    main()