# 📝 Functional Specification: ET Market Oracle (React Migration)

**To the AI assisting with the React Frontend:**
This document outlines the exact feature parity required to migrate the "ET Market Oracle" from Streamlit to React. The backend is a FastAPI server.

## Verification
- [x] Auth flow (login/register/guest)
- [x] CAS PDF upload → holdings appear
- [x] Watchlist sync
- [x] AI chat with real LangGraph context injection
- [x] Chart rendering (watchlist + inline)

### 1. Global State & Session Management
The application relies heavily on persistent state to prevent losing context during reloads.
* **Authentication State:** Needs to track `auth_status` (`logged_in`, `guest`, or `None`), `user_name`, and a JWT `token`.
* **Cookie Hydration:** The app checks for an `auth_token` cookie on the initial load. If found, it automatically logs the user in and fetches their data.
* **Portfolio State:** An array of objects representing mutual fund holdings (fetched via `GET /api/portfolio/me`).
* **Watchlist State:** An array of strings representing tracked stock tickers (fetched via `GET /api/watchlist/me`).
* **Chat History:** An array of message objects containing `role`, `content`, `type` (text or chart), and `tickers` (if it's a chart message).

### 2. The Authentication Gate (Landing Page)
Before accessing the main app, users must pass the Auth Gate.
* **Login Tab:** Takes Email/Password. Posts to `POST /api/auth/login`. On success, saves the JWT to cookies and global state.
* **Register Tab:** Takes Full Name, Email, Phone (optional), and Password. Posts to `POST /api/auth/register`.
* **Guest Mode:** A button that bypasses login, setting the state to `guest`. Portfolio and watchlist features work in memory but are not saved to the backend.

### 3. Sidebar / Dashboard Panel
This is the user's financial control center.
* **Dynamic Net Worth:** Calculates the sum of `current_value` for all items in the portfolio state.
* **1-Click CAS Upload:**
    * Contains a help popover explaining how to download a CAMS CAS statement.
    * A file uploader (PDF only) and a password input (for the user's PAN card).
    * Submits as `multipart/form-data` to `POST /api/portfolio/upload` with the JWT in the Authorization header.
    * On success, updates the global portfolio state.
* **Current Holdings Display:** Renders a truncated list of the top 5 mutual fund schemes and their current values.
* **Direct Equity Watchlist:**
    * A multi-select dropdown mapping friendly names (e.g., "Reliance Industries") to backend tickers (e.g., "RELIANCE.NS").
    * A "Sync Live Market Data" button that posts the selected tickers to `POST /api/watchlist/sync`.

### 4. Main Chat Interface & Context Injection
This is the core LangGraph AI interaction zone. It requires complex prompt engineering on the client side before sending data to the AI.
* **Context Injection (Invisible Prompting):** When the user types a prompt, the frontend silently appends background data *before* sending it to the agent. It injects:
    1.  A formatted string of all Mutual Fund holdings.
    2.  The exact calculated Net Worth integer (used by the AI's math tools).
    3.  The list of actively tracked Watchlist stocks.
* **Message Rendering:** Maps through the chat history array. Renders user messages on the right and assistant messages on the left.

### 5. Dynamic Charting Engine (Critical React Migration Note)
*Note to React AI: The Streamlit app used Python's `yfinance` directly in the frontend to draw charts. React cannot run `yfinance` in the browser due to CORS and Node dependencies.*
* **Watchlist Comparison Chart (Top of screen):**
    * An expandable accordion section.
    * Contains a radio button for timeframe (`1mo`, `6mo`, `1y`, `5y`, `max`).
    * Contains a multi-select to filter which tracked stocks to plot.
    * **Requirement:** The React app will need to call a new or existing FastAPI endpoint (e.g., `GET /api/market/history?tickers=...&period=...`) to get the time-series data, and plot it using a library like **Recharts** or **Chart.js**.
* **Inline AI Chat Charts:**
    * The LangGraph agent outputs a hidden regex tag when it wants to draw a chart: `[CHART_TICKER:SYMBOL]`.
    * The frontend intercepts the AI's response, removes the tag using Regex so the user doesn't see it, and extracts the symbol.
    * Failsafe logic: If the extracted ticker is in a predefined list of Indian blue chips (e.g., TCS, ZOMATO) and lacks the `.NS` suffix, the frontend auto-appends it.
    * It then renders a 3-month historical line chart directly inside the chat bubble below the text.

***

### How to use this document:

1. Copy the entire markdown block above.
2. Open your new React/Frontend AI chat.
3. Say: *"I am migrating a Python Streamlit app to React (Next.js/Vite with Tailwind). Here is the complete Functional Specification Document. Please read it, and then generate the initial project structure and the `AuthGate` component to get us started."*