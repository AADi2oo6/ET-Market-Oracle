import logging
from app.core.database import engine, Base, SessionLocal
from app.services.news_service import ingest_et_news
from app.services.market_service import ingest_stock_data

# Set up simple logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def run_seed():
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    logger.info("Schema initialized.")
    
    db = SessionLocal()
    try:
        logger.info("Starting ingestion of ET News...")
        ingest_et_news(db)
        logger.info("Finished ET News ingestion.")
        
        logger.info("Starting ingestion of Stock Data...")
        ingest_stock_data(db)
        logger.info("Finished Stock Data ingestion.")
        
    except Exception as e:
        logger.error(f"Error during seeding: {e}")
    finally:
        db.close()
        logger.info("Database session closed.")

if __name__ == "__main__":
    run_seed()
