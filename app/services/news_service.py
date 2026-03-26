import logging
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import feedparser
from sqlalchemy.orm import Session
from app.models.schema import NewsArticle

logger = logging.getLogger(__name__)

def ingest_et_news(db: Session) -> None:
    url = "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"
    try:
        logger.info(f"Fetching news from {url}")
        feed = feedparser.parse(url)
        
        if feed.bozo:
            logger.error(f"Error parsing feed: {feed.bozo_exception}")
            # Depending on feedparser version, some bozo=1 feeds still have valid entries.

        new_count = 0
        for entry in feed.entries:
            link = entry.get("link")
            if not link:
                continue
            
            # Check for duplicate
            existing = db.query(NewsArticle).filter(NewsArticle.link == link).first()
            if existing:
                continue

            title = entry.get("title", "")
            summary = entry.get("summary", "")
            
            published_at = None
            if "published" in entry:
                try:
                    dt = parsedate_to_datetime(entry.published)
                    # Convert to naive UTC if it's aware to match typical DB assumptions
                    if dt.tzinfo:
                        published_at = dt.astimezone(timezone.utc).replace(tzinfo=None)
                    else:
                        published_at = dt
                except Exception as e:
                    logger.warning(f"Could not parse date {entry.published}: {e}")

            article = NewsArticle(
                title=title,
                link=link,
                summary=summary,
                published_at=published_at
            )
            db.add(article)
            new_count += 1
            
        db.commit()
        logger.info(f"Ingested {new_count} new articles.")
    except Exception as e:
        logger.exception(f"An unexpected error occurred during news ingestion: {e}")
        db.rollback()
