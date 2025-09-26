# Stock Agent Demo - AgentOS with Next.js UI

A complete stock analysis system using AGNO AgentOS with a modern Next.js chat interface.

## Architecture

- **Backend**: AgentOS with 3 specialized agents and team memory management
- **Frontend**: Next.js chat interface with real-time communication
- **Agents**: Intelligence Analyst, Bull/Bear Analyst, Trading Manager
- **Team**: Fast Stock Analysis Team with memory and collaboration

## Setup & Running

### 1. Start AgentOS Backend
```bash
# In the Stock-Agent directory
python agent-api.py
```
This starts the AgentOS server on http://localhost:7777/

### 2. Start Next.js UI
```bash
# In the ui directory
cd ui
npm run dev
```
This starts the Next.js UI on http://localhost:3000/

## Usage

### Next.js Chat Interface (Recommended)
1. Open http://localhost:3000/
2. Select "Stock Analysis" from the sidebar
3. Ask about any stock: "Analyze AAPL", "What's the outlook for TSLA?"
4. Get comprehensive analysis from the 3-agent team

### AgentOS Interface
1. Open http://localhost:7777/
2. Use the built-in AgentOS interface
3. View agent configurations and team settings

## Features

- **Team Memory**: Remembers past analyses and learns over time
- **Multi-Agent Collaboration**: 3 agents work together for comprehensive analysis
- **Real-time Chat**: Modern chat interface with loading states
- **Stock Intelligence**: YFinance data, news analysis, and market insights
- **Investment Recommendations**: Bull/bear cases with final trading decisions

## API Endpoints

- `POST /api/chat` - Chat with agents
- `GET /api/agents` - Get agent information
- `GET /docs` - FastAPI documentation

## Files

- `agent-api.py` - Main AgentOS backend with stock agents
- `ui/` - Next.js frontend application
- `advisor-agent.py`, `base-agent.py`, `improved-agent.py` - Other agent variations

## Dependencies

Backend dependencies are managed by UV. The Next.js UI has its own package.json with all required dependencies already installed.