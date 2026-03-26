import logging
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.vectorstore import embed_unprocessed_news
from app.agents.orchestrator import create_market_agent

# Configure logging to see tool usage and info
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_tests():
    logger.info("Starting ET Market Oracle Phase 3 Test Script...")
    
    # 1. Open Database Session
    db = SessionLocal()
    
    try:
        # 2. Run Vectorization
        logger.info("Checking for unprocessed news articles to embed...")
        embedded_count = embed_unprocessed_news(db)
        print(f"\n✅ News embedding complete. ({embedded_count} new articles embedded.)")
        
        # 3. Initialize the Agent
        logger.info("Initializing ET Market Oracle Agent...")
        agent = create_market_agent()
        
        # 4. Test Query invoking both tools
        query = "What is the latest news about Reliance, and what is the most recent closing price for RELIANCE.NS?"
        print(f"\n==================================")
        print(f"👤 [USER QUERY]:\n{query}")
        print(f"==================================\n")
        
        # 5. Invoke Agent
        logger.info("Invoking agent. Watch the logs above this to see tool execution...")
        response = agent.invoke({"messages": [("user", query)]})
        
        # 6. Print Final Response
        print("\n==================================")
        print("🤖 [AGENT RESPONSE]:")
        print("==================================")
        
        final_response = "No response output found."
        if "messages" in response and len(response["messages"]) > 0:
            final_response = response["messages"][-1].content
            
        print(final_response)
        print("==================================\n")
        
        with open("agent_output.txt", "w", encoding="utf-8") as f:
            f.write(final_response)
        
    except Exception as e:
        logger.error(f"❌ Error during test script execution: {e}", exc_info=True)
    finally:
        # 7. Close Database Session
        db.close()
        logger.info("Database session closed.")

if __name__ == "__main__":
    run_tests()
