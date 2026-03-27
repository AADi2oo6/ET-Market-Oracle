from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import yfinance as yf
from datetime import datetime

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.schema import User, MarketData

watchlist_router = APIRouter()

class WatchlistUpdate(BaseModel):
    tickers: list[str]

@watchlist_router.post("/sync")
async def sync_watchlist(payload: WatchlistUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        # Update user's tracked stocks
        current_user.tracked_stocks = payload.tickers
        db.commit()

        # Fetch yfinance data for each and upsert to MarketData
        for ticker in payload.tickers:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")
            if not hist.empty:
                last_quote = hist.iloc[-1]
                md = db.query(MarketData).filter_by(ticker=ticker, date=last_quote.name.date()).first()
                if not md:
                    md = MarketData(
                        ticker=ticker,
                        date=last_quote.name.date(),
                        open=float(last_quote["Open"]),
                        high=float(last_quote["High"]),
                        low=float(last_quote["Low"]),
                        close=float(last_quote["Close"]),
                        volume=int(last_quote["Volume"])
                    )
                    db.add(md)
                else:
                    md.open = float(last_quote["Open"])
                    md.high = float(last_quote["High"])
                    md.low = float(last_quote["Low"])
                    md.close = float(last_quote["Close"])
                    md.volume = int(last_quote["Volume"])
                db.commit()
                
        return {"status": "success", "message": "Watchlist synced and market data fetched."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@watchlist_router.get("/me")
async def get_watchlist(current_user: User = Depends(get_current_user)):
    return {"tracked_stocks": current_user.tracked_stocks or []}
