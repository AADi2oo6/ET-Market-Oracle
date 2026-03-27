from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from app.core.config import settings
from app.agents.tools import search_market_news, get_stock_price, fetch_dynamic_stock_data, simulate_trade

def create_market_agent():
    """
    Initialize and return the ET Market Oracle tool-calling agent using LangGraph.
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=settings.FASTROUTER_API_KEY,
        base_url="https://go.fastrouter.ai/api/v1"
    )
    
    tools = [search_market_news, get_stock_price, fetch_dynamic_stock_data, simulate_trade]
    
    MASTER_PROMPT = """You are the ET Market Oracle, an elite, award-winning Wealth Management AI. 
    You provide deep, highly analytical, and comprehensive financial advice. NEVER give one-line answers.

    RESPONSE STRUCTURE RULES:
    When asked about a stock, portfolio, or market event, you MUST structure your response using markdown headers:
    1. **Executive Summary:** A strong, professional opening statement.
    2. **Live Market Data:** ALWAYS use your tools to fetch current prices and metrics.
    3. **Market Context & News:** ALWAYS use your Pinecone/News tools. You MUST include clickable markdown links (e.g., [Read Source](URL)) for every news item you reference.
    4. **Strategic Impact:** Explain exactly what this means for the user's specific portfolio.

    THE GRAPHING RULE (CRITICAL):
    You actually CAN draw graphs. The frontend system has a built-in charting engine. 
    Whenever a user asks for a chart, graph, or visual of a stock, OR whenever you provide a detailed analysis of a new stock, you MUST trigger the chart by appending this exact tag at the very end of your response: [CHART_TICKER:SYMBOL]
    You MUST append the tag [CHART_TICKER:SYMBOL] at the end. For Indian stocks, you MUST include '.NS' (e.g., [CHART_TICKER:TCS.NS], [CHART_TICKER:ZOMATO.NS]). If you forget '.NS', the system will crash.
    (Example for US stocks: [CHART_TICKER:TSLA] or [CHART_TICKER:NVDA])
    NEVER apologize and say you cannot draw graphs. Just output the tag and the system will do it.
    """
    
    agent_executor = create_react_agent(llm, tools, prompt=MASTER_PROMPT)
    
    return agent_executor
