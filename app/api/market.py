from fastapi import APIRouter, Query, HTTPException
import yfinance as yf
from datetime import datetime, timedelta

market_router = APIRouter()

@market_router.get("/history")
async def get_market_history(
    tickers: str = Query(..., description="Comma-separated list of tickers"),
    period: str = Query("1mo", description="Time period (1mo, 6mo, 1y, 5y, max)")
):
    try:
        ticker_list = [t.strip() for t in tickers.split(",")]
        dates_set = False
        dates = []
        series = {}
        currencies = {}
        
        for ticker in ticker_list:
            stock = yf.Ticker(ticker)
            data = stock.history(period=period)
            
            # Use fast_info to get currency if possible
            try:
                curr = stock.fast_info.get('currency', 'INR')
            except:
                curr = 'INR'
            currencies[ticker] = curr
            
            if not data.empty:
                if not dates_set:
                    dates = [str(d.date()) for d in data.index]
                    dates_set = True
                
                series[ticker] = [float(v) if not str(v) == 'nan' else None for v in data["Close"].values]
            else:
                series[ticker] = []

        return {
            "dates": dates,
            "series": series,
            "currencies": currencies
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
