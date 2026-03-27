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
    
    system_prompt = (
        "You are the ET Market Oracle, an elite financial advisor. "
        "You MUST use the provided tools to answer user questions. "
        "NEVER hallucinate stock prices or news. "
        "If you use news, you MUST cite the URL."
    )
    
    agent_executor = create_react_agent(llm, tools, prompt=system_prompt)
    
    return agent_executor
