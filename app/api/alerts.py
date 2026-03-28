from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from typing import List
import logging

from app.core.database import get_db
from app.core.config import settings
from app.core.vectorstore import get_vectorstore
from app.models.schema import UserAlert, User
from app.api.auth import get_current_user

logger = logging.getLogger(__name__)

alerts_router = APIRouter()

# --- Endpoints ---

@alerts_router.get("/me")
def get_my_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns all unread alerts for the current user, newest first."""
    alerts = (
        db.query(UserAlert)
        .filter(UserAlert.user_id == current_user.id, UserAlert.is_read == False)
        .order_by(UserAlert.created_at.desc())
        .all()
    )
    return [
        {
            "id": a.id,
            "ticker": a.ticker,
            "message": a.message,
            "severity": a.severity,
            "created_at": a.created_at.isoformat()
        }
        for a in alerts
    ]

@alerts_router.post("/mark-read/{alert_id}")
def mark_alert_read(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marks a specific alert as read."""
    alert = db.query(UserAlert).filter(
        UserAlert.id == alert_id,
        UserAlert.user_id == current_user.id
    ).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.is_read = True
    db.commit()
    return {"message": "Alert marked as read"}

@alerts_router.post("/scan")
def scan_for_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    The Radar Engine: Scans tracked stocks for recent news and uses an LLM
    to generate proactive alerts if significant events are detected.
    """
    tracked_stocks = current_user.tracked_stocks or []
    if not tracked_stocks:
        return {"message": "No tracked stocks to scan.", "alerts_created": 0}

    vectorstore = get_vectorstore()
    llm = ChatOpenAI(
        api_key=settings.FASTROUTER_API_KEY,
        base_url="https://api.fastrouter.ai/v1",
        model="gpt-4o-mini",
        temperature=0
    )

    alerts_created = 0
    for ticker in tracked_stocks:
        try:
            # Fetch top 2 recent news chunks from Pinecone for this ticker
            docs = vectorstore.similarity_search(ticker, k=2)
            if not docs:
                continue

            news_snippet = "\n---\n".join([doc.page_content for doc in docs])
            prompt = (
                f"Analyze this news about the stock ticker {ticker}. "
                f"If it contains an urgent WARNING, credit rating downgrade, regulatory action, or major market-moving event, "
                f"return a single concise alert sentence starting with 'WARNING:' or 'UPDATE:'. "
                f"If the news is routine or positive noise, return exactly 'NONE'.\n\n"
                f"News:\n{news_snippet}"
            )

            response = llm.invoke([HumanMessage(content=prompt)])
            alert_text = response.content.strip()

            if alert_text and alert_text.upper() != "NONE":
                severity = "high" if alert_text.startswith("WARNING:") else "medium"
                new_alert = UserAlert(
                    user_id=current_user.id,
                    ticker=ticker,
                    message=alert_text,
                    severity=severity,
                )
                db.add(new_alert)
                alerts_created += 1
                logger.info(f"Alert created for user {current_user.id} on {ticker}: {alert_text}")

        except Exception as e:
            logger.error(f"Error scanning {ticker} for user {current_user.id}: {e}")
            continue

    db.commit()
    return {"message": f"Scan complete. {alerts_created} new alert(s) created.", "alerts_created": alerts_created}
