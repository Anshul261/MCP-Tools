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

# PHASE 1: INTELLIGENCE GATHERING AGENTS

market_analyst = Agent(
    model=get_model(),
    tools=[YFinanceTools(), DuckDuckGoTools()],
    description=dedent("""
        You are a market analyst specializing in technical analysis and market trends.
        Focus on price action, volume analysis, market sentiment, and technical indicators.
    """),
    instructions=dedent("""
        1. Analyze current stock price trends and technical indicators
        2. Evaluate volume patterns and market liquidity
        3. Assess support and resistance levels
        4. Review market sentiment indicators
        5. Compare performance against market indices
        6. Identify technical patterns and signals
        7. Provide short-term price momentum analysis
    """),
    expected_output="Technical analysis with price trends, volume analysis, and market positioning data",
    markdown=True,
)

social_analyst = Agent(
    model=get_model(),
    tools=[DuckDuckGoTools(), Newspaper4kTools()],
    description=dedent("""
        You are a social sentiment analyst tracking retail investor behavior, 
        social media trends, and public perception of stocks.
    """),
    instructions=dedent("""
        1. Monitor social media sentiment around the stock
        2. Track retail investor discussions and trends
        3. Analyze Reddit, Twitter, and financial forums
        4. Identify viral trends affecting the stock
        5. Assess meme stock potential and retail flow
        6. Monitor influencer and analyst social media activity
        7. Gauge public perception and brand sentiment
    """),
    expected_output="Social sentiment analysis with retail investor behavior and public perception insights",
    markdown=True,
)

news_analyst = Agent(
    model=get_model(),
    tools=[Newspaper4kTools(), DuckDuckGoTools(), YFinanceTools()],
    description=dedent("""
        You are a news analyst focused on breaking news, press releases, 
        and media coverage that could impact stock performance.
    """),
    instructions=dedent("""
        1. Monitor recent company news and press releases
        2. Track industry-specific news and trends
        3. Identify regulatory changes and their impact
        4. Analyze earnings announcements and guidance
        5. Review management interviews and statements
        6. Assess competitive developments
        7. Monitor macroeconomic news affecting the sector
    """),
    expected_output="News analysis with key developments, regulatory impacts, and media coverage summary",
    markdown=True,
)

fundamentals_analyst = Agent(
    model=get_model(),
    tools=[YFinanceTools(), DuckDuckGoTools()],
    description=dedent("""
        You are a fundamentals analyst specializing in financial statement analysis,
        valuation metrics, and long-term company health assessment.
    """),
    instructions=dedent("""
        1. Analyze key financial ratios and metrics
        2. Review revenue growth and profitability trends
        3. Assess balance sheet strength and debt levels
        4. Evaluate cash flow and dividend sustainability
        5. Compare valuation multiples to industry peers
        6. Analyze management effectiveness and strategy
        7. Review analyst recommendations and price targets
    """),
    expected_output="Fundamental analysis with financial health, valuation metrics, and long-term outlook",
    markdown=True,
)

# PHASE 2: STRATEGY & DEBATE AGENTS

bull_researcher = Agent(
    model=get_model(),
    tools=[ReasoningTools()],
    description=dedent("""
        You are a bull researcher who builds the strongest possible case for why
        the stock should be bought. You analyze all positive factors and growth potential.
    """),
    instructions=dedent("""
        1. Identify all positive catalysts and growth drivers
        2. Highlight competitive advantages and market opportunities
        3. Emphasize strong financial metrics and trends
        4. Point out undervaluation opportunities
        5. Present best-case scenarios for future performance
        6. Counter potential negative arguments with positive perspectives
        7. Build a compelling investment thesis for buying
        8. Use data from Phase 1 analysts to support bullish arguments
    """),
    expected_output="Strong bullish investment case with supporting evidence and growth projections",
    markdown=True,
)

bear_researcher = Agent(
    model=get_model(),
    tools=[ReasoningTools()],
    description=dedent("""
        You are a bear researcher who identifies all potential risks and reasons
        why the stock could decline. You focus on downside scenarios and red flags.
    """),
    instructions=dedent("""
        1. Identify all risk factors and potential headwinds
        2. Highlight competitive threats and market challenges
        3. Point out concerning financial metrics or trends
        4. Assess overvaluation risks and bubble indicators
        5. Present worst-case scenarios for future performance
        6. Counter bullish arguments with skeptical analysis
        7. Build a compelling case for avoiding or shorting the stock
        8. Use data from Phase 1 analysts to support bearish arguments
    """),
    expected_output="Comprehensive bearish analysis with risk assessment and downside scenarios",
    markdown=True,
)

research_manager = Agent(
    model=get_model(),
    tools=[ReasoningTools()],
    description=dedent("""
        You are the research manager who synthesizes all analysis from Phase 1 and Phase 2
        to create a balanced, comprehensive investment thesis.
    """),
    instructions=dedent("""
        1. Synthesize findings from all Phase 1 intelligence gathering
        2. Balance bull and bear arguments from Phase 2 debate
        3. Identify the most critical factors affecting the stock
        4. Assess probability-weighted scenarios
        5. Determine key catalysts and risk factors to monitor
        6. Create integrated investment thesis
        7. Prepare balanced analysis for final decision making
        8. Highlight areas of agreement and disagreement between analysts
    """),
    expected_output="Synthesized investment thesis balancing all perspectives with key decision factors",
    markdown=True,
)

# PHASE 3: EXECUTION & FINAL DECISION AGENTS

trader_agent = Agent(
    model=get_model(),
    tools=[YFinanceTools(), ReasoningTools()],
    description=dedent("""
        You are a trader focused on execution timing, position sizing, and tactical decisions.
        You translate investment thesis into actionable trading strategies.
    """),
    instructions=dedent("""
        1. Assess optimal entry and exit timing
        2. Recommend position sizing based on conviction and risk
        3. Identify key price levels for execution
        4. Suggest order types and execution strategies
        5. Plan for various market scenarios
        6. Set stop-loss and take-profit levels
        7. Consider market liquidity and trading costs
        8. Provide tactical implementation guidance
    """),
    expected_output="Trading strategy with entry/exit points, position sizing, and execution plan",
    markdown=True,
)

risk_debate_agent = Agent(
    model=get_model(),
    tools=[ReasoningTools()],
    description=dedent("""
        You are a risk debate specialist who evaluates investment proposals from
        three perspectives: Risky (aggressive), Safe (conservative), and Neutral (balanced).
        You facilitate the final risk assessment debate.
    """),
    instructions=dedent("""
        RISKY PERSPECTIVE:
        - Advocate for larger position sizes and leveraged exposure
        - Focus on maximum return potential
        - Emphasize growth opportunities and catalysts
        - Accept higher volatility for higher returns
        
        SAFE PERSPECTIVE:
        - Advocate for smaller positions and risk management
        - Focus on capital preservation
        - Emphasize downside protection and diversification
        - Prefer lower volatility and steady returns
        
        NEUTRAL PERSPECTIVE:
        - Balance risk and reward considerations
        - Recommend moderate position sizing
        - Consider both upside and downside scenarios equally
        - Focus on risk-adjusted returns
        
        Facilitate debate between these three approaches and synthesize into final risk assessment.
    """),
    expected_output="Risk debate analysis from three perspectives with final risk-adjusted recommendation",
    markdown=True,
)

portfolio_manager = Agent(
    model=get_model(),
    tools=[ReasoningTools()],
    description=dedent("""
        You are the portfolio manager with final decision authority. You make the ultimate
        BUY/SELL/HOLD decision based on all team analysis and risk assessment.
    """),
    instructions=dedent("""
        1. Review all analysis from intelligence gathering phase
        2. Consider bull/bear debate and synthesized research
        3. Evaluate trader execution strategy and timing
        4. Assess risk debate conclusions and position sizing
        5. Make final BUY/SELL/HOLD decision with clear rationale
        6. Set position size and risk parameters
        7. Define success metrics and exit criteria
        8. Provide clear, actionable investment decision
    """),
    expected_output="Final investment decision (BUY/SELL/HOLD) with rationale, position size, and monitoring plan",
    markdown=True,
)

# POST-DECISION AGENTS

reflector_agent = Agent(
    model=get_model(),
    tools=[ReasoningTools()],
    description=dedent("""
        You are a reflector agent who analyzes the decision-making process and
        learns from outcomes to improve future analysis.
    """),
    instructions=dedent("""
        1. Review the quality of analysis from each phase
        2. Identify where predictions were accurate or inaccurate
        3. Assess decision-making process effectiveness
        4. Learn from market outcomes vs predictions
        5. Update mental models and analytical approaches
        6. Identify biases or blind spots in analysis
        7. Recommend process improvements
        8. Document lessons learned for future decisions
    """),
    expected_output="Process reflection with lessons learned and recommendations for improvement",
    markdown=True,
)

# MAIN STOCK ANALYSIS TEAM

stock_analysis_team = Team(
    name="Stock Analysis Team",
    db=db,
    model=get_model(),
    members=[
        # Phase 1: Intelligence Gathering
        market_analyst, social_analyst, news_analyst, fundamentals_analyst,
        # Phase 2: Strategy & Debate  
        bull_researcher, bear_researcher, research_manager,
        # Phase 3: Execution & Decision
        trader_agent, risk_debate_agent, portfolio_manager,
        # Post-Decision
        reflector_agent
    ],
    tools=[ReasoningTools()],
    instructions=[
        """
STOCK ANALYSIS TEAM WORKFLOW

MISSION: Conduct comprehensive stock analysis following a structured multi-phase approach
to generate high-quality investment decisions with proper risk management.

WORKFLOW PHASES:

PHASE 1: INTELLIGENCE GATHERING
- Market Analyst: Technical analysis and price action
- Social Analyst: Sentiment and retail investor behavior  
- News Analyst: Breaking news and company developments
- Fundamentals Analyst: Financial health and valuation

PHASE 2: STRATEGY & DEBATE
- Bull Researcher: Build strongest case for buying
- Bear Researcher: Identify all risks and downside scenarios
- Research Manager: Synthesize all findings into balanced thesis

PHASE 3: EXECUTION & FINAL DECISION
- Trader Agent: Develop execution strategy and timing
- Risk Debate Agent: Evaluate from Risky/Safe/Neutral perspectives
- Portfolio Manager: Make final BUY/SELL/HOLD decision

POST-DECISION: LEARNING & REFLECTION
- Reflector Agent: Analyze process and learn from outcomes

COORDINATION PRINCIPLES:

1. SEQUENTIAL FLOW
   - Phase 1 agents gather intelligence first
   - Phase 2 agents debate and synthesize findings
   - Phase 3 agents make final decision and execution plans
   - Post-decision reflection and learning

2. INFORMATION CASCADE
   - Each phase builds on previous phase outputs
   - Later phases reference and build upon earlier analysis
   - Final decision incorporates all previous work

3. BALANCED PERSPECTIVE
   - Ensure both bullish and bearish views are represented
   - Consider multiple timeframes and scenarios
   - Balance quantitative analysis with qualitative insights

4. RISK-CONSCIOUS DECISIONS
   - Always consider downside scenarios
   - Size positions appropriately for risk level
   - Plan exit strategies and stop-losses

5. CONTINUOUS LEARNING
   - Document reasoning and predictions
   - Track accuracy over time
   - Improve process based on outcomes

DELIVERABLE: Clear BUY/SELL/HOLD recommendation with:
- Investment thesis and supporting analysis
- Risk assessment and position sizing
- Entry/exit strategy and price targets
- Key catalysts and risks to monitor
"""
    ],
    enable_user_memories=True,
    enable_session_summaries=True,
    markdown=True,
    enable_agentic_memory=True,
    stream=True
)

def main():
    console.print(Panel.fit("Stock Analysis Team Ready", style="bold green"))
    console.print("Welcome! I'm your AI Stock Analysis Team.")
    console.print("Provide a stock ticker and any specific analysis requirements.")
    console.print("Example: 'Analyze NVDA for a 6-month investment horizon'")
    console.print("Type 'quit' to exit.\n")

    while True:
        try:
            question = input("You: ").strip()
            
            if question.lower() in ['quit', 'exit', 'bye']:
                console.print("[green]Analysis session ended![/green]")
                break
                
            if not question:
                continue
                
            console.print("[blue]Stock Analysis Team processing your request...[/blue]")
            stock_analysis_team.print_response(question)
            
        except KeyboardInterrupt:
            console.print("\n[green]Analysis session ended![/green]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            console.print("Please try a different question.")

if __name__ == "__main__":
    main()