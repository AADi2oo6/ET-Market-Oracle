import math
import logging
import yfinance as yf
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, PendingRollbackError
from app.models.schema import MarketData

logger = logging.getLogger(__name__)

DEFAULT_TICKERS = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ITC.NS"]

def ingest_stock_data(db: Session, tickers: list[str] | None = None) -> None:
    if tickers is None:
        tickers = DEFAULT_TICKERS

    market_data_cache = {}

    # Phase 1: Fetch data from yfinance first
    for ticker_symbol in tickers:
        try:
            logger.info(f"Fetching market data for {ticker_symbol}")
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period="30d")
            
            if hist.empty:
                logger.warning(f"No data found for {ticker_symbol}")
                continue
                
            market_data_cache[ticker_symbol] = hist
        except Exception as e:
            logger.error(f"Error fetching data from yfinance for {ticker_symbol}: {e}")

    # Phase 2: Database operations
    for ticker_symbol, hist in market_data_cache.items():
        try:
            records_upserted = 0
            for index, row in hist.iterrows():
                # index is a pandas Timestamp representing the date
                date_val = index.date()
                
                def clean_float(val):
                    if math.isnan(val):
                        return None
                    return float(val)

                # YFinance returns columns with capitalized names
                open_val = clean_float(row.get("Open", float('nan')))
                high_val = clean_float(row.get("High", float('nan')))
                low_val = clean_float(row.get("Low", float('nan')))
                close_val = clean_float(row.get("Close", float('nan')))
                
                volume_raw = row.get("Volume", 0)
                volume_val = int(volume_raw) if not math.isnan(volume_raw) else None

                existing = db.query(MarketData).filter(
                    MarketData.ticker == ticker_symbol,
                    MarketData.date == date_val
                ).first()

                if existing:
                    existing.open = open_val
                    existing.high = high_val
                    existing.low = low_val
                    existing.close = close_val
                    existing.volume = volume_val
                else:
                    new_record = MarketData(
                        ticker=ticker_symbol,
                        date=date_val,
                        open=open_val,
                        high=high_val,
                        low=low_val,
                        close=close_val,
                        volume=volume_val
                    )
                    db.add(new_record)
                
            try:
                db.commit()
                records_upserted = len(hist)
                logger.info(f"Upserted/Iterated {records_upserted} records for {ticker_symbol}")
            except (OperationalError, PendingRollbackError) as e:
                db.rollback()
                logger.error(f"Database connection error during commit for {ticker_symbol}: {e}")
            
        except (OperationalError, PendingRollbackError) as e:
            db.rollback()
            logger.error(f"Database connection error during row processing for {ticker_symbol}: {e}")
        except Exception as e:
            logger.exception(f"An unexpected error occurred during market data ingestion for {ticker_symbol}: {e}")
            db.rollback()
