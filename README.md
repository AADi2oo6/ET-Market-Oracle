<div align="center">

# 🔮 ET Market Oracle

### *The Elite, Context-Aware AI Wealth Manager & Omnichannel Financial Advisor*

[![FastAPI](https://img.shields.io/badge/FastAPI-0.135+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19+-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-FF6B35?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Pinecone](https://img.shields.io/badge/Pinecone-Vector_DB-00C7B7?style=for-the-badge)](https://www.pinecone.io/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Telegram](https://img.shields.io/badge/Telegram_Bot-Integrated-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://core.telegram.org/bots)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

---

![ET Market Oracle Banner](https://placehold.co/1200x400/0a0b0f/6366f1?text=ET+Market+Oracle+%E2%80%94+AI+Wealth+Intelligence+Platform)

</div>

---

## 📌 Overview & Mission

**ET Market Oracle** is a complete, production-grade SaaS platform that bridges the gap between generic AI chatbots and expensive, high-friction wealth management tools.

> *"Your money deserves an AI that knows your portfolio as well as your best analyst—available 24/7, for free."*

Unlike black-box financial apps, ET Market Oracle gives every user a **LangGraph multi-agent system** that speaks to their *specific* holdings—not generic market commentary. It ingests real-time stock data, Economic Times news embeddings, and a user's encrypted mutual fund statement to deliver **hyper-personalized, hallucination-free financial intelligence**.

The platform is fully omnichannel: use the premium React dashboard at your desk, or query your portfolio's health on Telegram from anywhere in the world. **One AI brain. Every surface.**

---

## ✨ Key Features & Innovations

### 🧠 Invisible Context Injection
The React frontend **silently staples** the user's parsed portfolio, holdings, and net worth to every chat prompt. The AI agent acts as a true fiduciary, answering questions like *"Should I buy more INFY?"* with full awareness of how much INFY the user **already holds**.

### 📊 "What-If" Impact Simulator
A custom LangChain tool computes the **exact financial impact** of any hypothetical trade. Ask *"What happens if I buy 50 shares of ZOMATO.NS at ₹230?"* and get real P&L, weight shift, and concentration risk—calculated against your live portfolio in seconds.

### 📈 Autonomous Inline UI Charting
The AI emits strategically placed hidden `[CHART_TICKER:SYMBOL]` tags. The React frontend intercepts these via regex and dynamically renders **interactive 30-day Recharts stock graphs directly inside chat bubbles**—no user action required.

### 🔔 Proactive News Alert Engine (Radar)
A background engine scans the Pinecone vector store (populated with real-time ET News) against the user's specific watchlist stocks. It uses a lightweight `gpt-4o-mini` prompt to classify news as urgent (`WARNING:`) or routine, pushing critical alerts to a **live Notification Bell** with a badge count.

### ⚡ Zero-API Portfolio X-Ray
Users upload a standard **CAMS/KFintech CAS PDF** (Consolidated Account Statement). `casparser` decrypts and parses their entire mutual fund history—**locally, privately, in ~2 seconds**. No broker API account required.

### 📱 Telegram Omnichannel Integration
The exact same LangGraph brain is deployed as a **polling Telegram bot**. Users get portfolio updates, stock analysis, and news briefings right where they already chat—proving the fully decoupled, API-first architecture.

### 🚀 Frictionless Guest Mode
Users can experience the full AI platform **without creating an account**—no friction at the critical "Aha!" moment. Guest mode transparently passes without portfolio context, while authenticated users get the full personalized experience.

---

## ⚔️ The Problem vs. Solution

| # | 🔴 The Problem | 🟢 Our Solution |
|---|---|---|
| 1 | **Expensive & High-Friction Onboarding.** Broker APIs cost thousands; users hate linking bank accounts. | **"Zero-API" Portfolio X-Ray.** Users upload a standard CAMS CAS PDF. `casparser` parses their full history locally in 2 seconds—free and private. |
| 2 | **Generic & Hallucinated AI Advice.** LLMs give the same advice to everyone, often with invented data. | **Context-Aware "Look-Through" AI.** LangGraph silently reads exact holdings and runs deterministic math via live `yfinance` data before answering. |
| 3 | **The Information Disconnect.** How does breaking news affect *my specific* portfolio? | **Hyper-Personalized Proactive Alerts.** A Radar Engine scans Pinecone (real-time ET News) against the user's watchlist and pushes urgent alerts to the UI Notification Bell. |
| 4 | **App Fatigue & Low Engagement.** Users forget to check finance dashboards. | **Lightning-Fast Telegram Integration.** The same LangGraph brain is deployed as a Telegram bot—users get analyses where they already chat. |

---

## 🏗️ Architecture

![Architecture Diagram](https://placehold.co/1200x600/0f172a/6366f1?text=Architecture+Diagram+%E2%80%94+Coming+Soon)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                 │
│   React (Vite) Dashboard ◄──────────────────► Telegram Bot          │
└──────────────────────┬──────────────────────────────────┬───────────┘
                       │ HTTP / REST                       │ python-telegram-bot
┌──────────────────────▼──────────────────────────────────▼───────────┐
│                      FASTAPI BACKEND (Python)                        │
│  /api/auth  /api/portfolio  /api/watchlist  /api/alerts  /api/agent  │
└──────────────────────┬───────────────────────────────────────────────┘
                       │ invoke()
┌──────────────────────▼───────────────────────────────────────────────┐
│                  LANGGRAPH MULTI-AGENT ORCHESTRATOR                   │
│   ┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│   │ search_market   │  │  get_stock_price  │  │  simulate_trade  │   │
│   │ _news (Pinecone)│  │  (yfinance)       │  │  (LangChain Tool)│   │
│   └─────────────────┘  └──────────────────┘  └──────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
                       │
           ┌───────────┴──────────────┐
           ▼                          ▼
   PostgreSQL (Users,          Pinecone (ET News
   Portfolio, Alerts)          Embeddings, RAG)
```

---

## 🛠️ Tech Stack

<div align="center">

### Frontend
[![React](https://img.shields.io/badge/React_19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite_8-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS_3-38BDF8?style=flat-square&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![Recharts](https://img.shields.io/badge/Recharts-FF6B35?style=flat-square)](https://recharts.org)
[![Framer Motion](https://img.shields.io/badge/Framer_Motion-0055FF?style=flat-square&logo=framer&logoColor=white)](https://www.framer.com/motion/)

### Backend
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python_3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![JWT](https://img.shields.io/badge/JWT_Auth-000000?style=flat-square&logo=jsonwebtokens&logoColor=white)](https://jwt.io)
[![bcrypt](https://img.shields.io/badge/bcrypt-Hashing-4A90D9?style=flat-square)](https://pypi.org/project/bcrypt/)
[![Uvicorn](https://img.shields.io/badge/Uvicorn-ASGI-499848?style=flat-square)](https://www.uvicorn.org)

### AI / ML Engine
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-FF6B35?style=flat-square)](https://langchain-ai.github.io/langgraph/)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat-square&logo=langchain&logoColor=white)](https://www.langchain.com)
[![OpenAI](https://img.shields.io/badge/GPT--4o--mini-412991?style=flat-square&logo=openai&logoColor=white)](https://platform.openai.com)
[![FastRouter](https://img.shields.io/badge/FastRouter-API_Gateway-FF6B6B?style=flat-square)](https://fastrouter.ai)

### Data & Databases
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Pinecone](https://img.shields.io/badge/Pinecone-Vector_DB-00C7B7?style=flat-square)](https://pinecone.io)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?style=flat-square)](https://www.sqlalchemy.org/)
[![Redis](https://img.shields.io/badge/Redis-Cache-DC382D?style=flat-square&logo=redis&logoColor=white)](https://redis.io)

### Data Pipelines
[![yfinance](https://img.shields.io/badge/yfinance-Live_Market_Data-6366F1?style=flat-square)](https://pypi.org/project/yfinance/)
[![casparser](https://img.shields.io/badge/casparser-PDF_Parsing-F59E0B?style=flat-square)](https://pypi.org/project/casparser/)
[![Telegram](https://img.shields.io/badge/python--telegram--bot-26A5E4?style=flat-square&logo=telegram&logoColor=white)](https://python-telegram-bot.org)
[![feedparser](https://img.shields.io/badge/feedparser-ET_News_RSS-10B981?style=flat-square)](https://pypi.org/project/feedparser/)

</div>

---

## ⚙️ Local Setup

### Prerequisites

- **Node.js** ≥ 18.x
- **Python** ≥ 3.10
- **PostgreSQL** ≥ 14 (or a cloud instance like Supabase)
- **uv** package manager (`pip install uv`)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/et-market-oracle.git
cd et-market-oracle
```

### 2. Backend Setup

```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows PowerShell

# Install all dependencies
uv pip install -r requirements.txt

# Create and configure the environment file
cp .env.example .env
```

Edit `.env` with your credentials:

```env
DATABASE_URL="postgresql://user:password@localhost:5432/et_market_oracle"
REDIS_URL="rediss://..."
PINECONE_API_KEY="pcsk_..."
PINECONE_INDEX_NAME="et-market-oracle"
FASTROUTER_API_KEY="sk-v1-..."
TELEGRAM_TOKEN="your-telegram-bot-token"
```

```bash
# Initialize the database tables
python -c "from app.core.database import engine, Base; from app.models import schema; Base.metadata.create_all(bind=engine)"

# Start the backend server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

> **API Docs** available at [`http://localhost:8000/docs`](http://localhost:8000/docs)

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

> **App** available at [`http://localhost:5173`](http://localhost:5173)

### 4. Telegram Bot Setup

With the backend running and `.venv` active, from the project root:

```bash
python telegram_bot.py
```

The bot will begin polling and print `✅ Bot is online and listening.`

---

## 🎬 Usage & Demo Flow

### Step 1 — Hook: Instant Frictionless Access
Visit the app. Click **"Continue as Guest"** to immediately experience the full AI Oracle with no sign-up friction. Ask it anything: *"What are the top 3 Indian IT stocks to watch this week?"*

### Step 2 — Sync: Portfolio X-Ray Upload
Register an account, then navigate to **Portfolio → Upload CAS PDF**. Drop in your CAMS or KFintech statement. In ~2 seconds, your entire mutual fund universe is parsed and reflected in your **Net Worth dashboard**.

### Step 3 — Track: Personalized Watchlist
Add any NSE/BSE tickers (e.g., `TCS.NS`, `ZOMATO.NS`) to your watchlist. The dashboard renders **live, interactive 30-day price charts** for all tracked stocks.

### Step 4 — Simulate: The "What-If" Engine
In the AI Chat, ask: *"What would happen to my portfolio if I sold 100 units of my HDFC fund and bought 50 shares of RELIANCE.NS?"*  
The agent silently calls the **Impact Simulator tool** and returns exact P&L, concentration shift, and strategic commentary.

### Step 5 — Alert: The Radar Engine
Click the 🔔 **Bell icon** in the header. Hit **⚡ Scan Now**. The backend queries your watchlist against the latest Economic Times news embeddings in Pinecone, runs an LLM triage, and pushes `WARNING:` or `UPDATE:` level alerts directly to your notification bell—no page refresh needed.

### Step 6 — Telegram: Anywhere Intelligence
Open your Telegram bot chat. Send `/start`, then query: *"Give me a full analysis of INFY.NS for today."* The same LangGraph agent—with full tool access—responds in seconds, right in your chat app.

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

[MIT](LICENSE) © 2025 ET Market Oracle Team

---

<div align="center">

**Built for the ET Hackathon 2025 · Powered by LangGraph, FastAPI, and Real-Time Market Intelligence**

*"Not just an AI. A financial confidant."*

</div>
