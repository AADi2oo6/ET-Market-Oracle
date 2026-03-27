from langchain.tools import tool
from app.core.database import SessionLocal
from app.models.schema import MarketData
from app.core.vectorstore import get_vectorstore
import yfinance as yf

@tool
def search_market_news(query: str) -> str:
    """
    Search for recent market news related to a query.
    Always use this to get the latest context about a company or market before answering.
    """
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search(query, k=3)
    
    if not results:
        return "No recent news found for this query."
        
    formatted_results = []
    for i, doc in enumerate(results, start=1):
        title = doc.metadata.get("title", "Unknown Title")
        source = doc.metadata.get("source", "Unknown Source")
        formatted_results.append(f"[{i}] {title}\nSummary: {doc.page_content}\nURL: {source}")
        
    return "\n\n".join(formatted_results)

@tool
def get_stock_price(ticker: str) -> str:
    """
    Get the most recent close price and volume for a given stock ticker.
    Example tickers: 'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS'
    """
    db = SessionLocal()
    try:
        # Get the most recent market data for this ticker
        market_data = db.query(MarketData)\
            .filter(MarketData.ticker == ticker)\
            .order_by(MarketData.date.desc())\
            .first()
            
        if not market_data:
            return f"No recent market data found for ticker: {ticker}"
            
        return (
            f"Ticker: {market_data.ticker}\n"
            f"Date: {market_data.date}\n"
            f"Close Price: {market_data.close}\n"
            f"Volume: {market_data.volume}"
        )
    except Exception as e:
        return f"Error retrieving stock price: {str(e)}"
    finally:
        db.close()

@tool
def fetch_dynamic_stock_data(ticker: str) -> str:
    """
    Use this tool to fetch live, real-time pricing and basic info for ANY stock ticker (e.g., ZOMATO.NS, TSLA, AAPL) that is NOT currently in the database.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        current_price = info.get("currentPrice", info.get("regularMarketPrice", "N/A"))
        day_high = info.get("dayHigh", "N/A")
        day_low = info.get("dayLow", "N/A")
        name = info.get("shortName", ticker)
        
        return f"Live Data for {name} ({ticker}): Current Price: {current_price}, Day High: {day_high}, Day Low: {day_low}."
    except Exception as e:
        return f"Could not fetch live data for {ticker}. Ensure the ticker symbol is correct."
