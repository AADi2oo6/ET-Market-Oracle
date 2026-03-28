import os
import re
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from app.agents.orchestrator import create_market_agent

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Use the provided token (Recommend moving to .env later)
TELEGRAM_TOKEN = "8632186079:AAEGk6VpUktUIY59K-ncnS_mVvQQrpLSYr8"

# Initialize the agent once for the bot
agent = create_market_agent()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    welcome_message = (
        "🤖 **Welcome to the ET Market Oracle!**\n\n"
        "I am your elite, AI-powered Wealth Manager. I am connected to real-time market data, "
        "The Economic Times news via Pinecone, and our financial simulator.\n\n"
        "Ask me about any stock, market news, or simulate a trade!"
    )
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process user messages and route them through LangGraph."""
    user_text = update.message.text
    
    # Show 'typing...' action to the user while the AI thinks
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    try:
        # Run the synchronous agent invocation in a thread to avoid blocking the async bot
        response = await asyncio.to_thread(
            agent.invoke,
            {"messages": [("user", user_text)]}
        )
        
        raw_bot_reply = response["messages"][-1].content
        
        # Telegram cannot render Streamlit charts, so we must cleanly strip out our hidden tags
        clean_reply = re.sub(r'\[CHART_TICKER:.*?\]', '', raw_bot_reply).strip()
        
        # Send the response back to the user
        await update.message.reply_text(clean_reply)
        
    except Exception as e:
        logger.error(f"Telegram Bot Error: {e}")
        error_msg = f"⚠️ Oracle encountered an error while analyzing the markets: {str(e)}"
        await update.message.reply_text(error_msg)

def main():
    """Start the bot."""
    logger.info("🚀 Starting ET Market Oracle Telegram Bot...")
    
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start_command))

    # Message handler for all text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C
    logger.info("✅ Bot is online and listening. Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
