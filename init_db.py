from app.core.database import engine
from app.models.schema import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Creating all tables in the database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Done creating tables.")
