import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import InlineChart from './InlineChart';
import api from '../lib/api';
import toast from 'react-hot-toast';

// Regex to detect [CHART_TICKER:SYMBOL] in AI output
const CHART_REGEX = /\[CHART_TICKER:([A-Z.]+)\]/g;

// Indian tickers that need .NS suffix
const INDIAN_TICKERS = ['TCS', 'RELIANCE', 'INFY', 'WIPRO', 'ICICIBANK', 'HDFCBANK', 'ZOMATO', 'ADANIPORTS', 'BAJFINANCE', 'AXISBANK'];

function normalizeTicker(t) {
  const upper = t.toUpperCase();
  if (INDIAN_TICKERS.includes(upper) && !upper.includes('.')) return `${upper}.NS`;
  return upper;
}

function parseMessage(text) {
  const charts = [];
  let clean = text;
  let match;
  CHART_REGEX.lastIndex = 0;
  while ((match = CHART_REGEX.exec(text)) !== null) {
    charts.push(normalizeTicker(match[1]));
  }
  clean = text.replace(CHART_REGEX, '').trim();
  return { clean, charts };
}

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

function MessageBubble({ msg }) {
  const isUser = msg.role === 'user';
  const { clean, charts } = parseMessage(msg.content);

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
    >
      {!isUser && (
        <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mr-3 mt-1 shadow-lg ring-1 ring-white/10" style={{ background: 'linear-gradient(135deg, rgba(99,102,241,0.4), rgba(129,140,248,0.2))' }}>
          <svg viewBox="0 0 24 24" className="w-4 h-4 fill-indigo-200">
            <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z" />
          </svg>
        </div>
      )}
      <div className={`max-w-[85%] ${isUser ? 'items-end' : 'items-start'} flex flex-col gap-3`}>
        <div
          className={`px-5 py-3.5 rounded-2xl text-[14.5px] leading-relaxed shadow-xl border ${
            isUser 
              ? 'bg-indigo-600/90 text-white border-indigo-400/30' 
              : 'bg-zinc-900/80 text-zinc-100 border-white/5'
          }`}
          style={{
            backdropFilter: 'blur(16px)',
          }}
        >
          {isUser ? (
            <div className="whitespace-pre-wrap">{clean}</div>
          ) : (
            <ReactMarkdown 
              remarkPlugins={[remarkGfm]}
              components={{
                h1: ({node, ...props}) => <h1 className="text-xl font-bold mb-4 mt-2 text-white border-b border-white/10 pb-2" {...props} />,
                h2: ({node, ...props}) => <h2 className="text-lg font-bold mb-3 mt-4 text-indigo-300" {...props} />,
                h3: ({node, ...props}) => <h3 className="text-md font-bold mb-2 mt-3 text-indigo-400" {...props} />,
                p: ({node, ...props}) => <p className="mb-3 last:mb-0" {...props} />,
                ul: ({node, ...props}) => <ul className="list-disc ml-6 mb-4 space-y-2" {...props} />,
                ol: ({node, ...props}) => <ol className="list-decimal ml-6 mb-4 space-y-2" {...props} />,
                li: ({node, ...props}) => <li className="pl-1" {...props} />,
                code: ({node, inline, ...props}) => 
                  inline ? (
                    <code className="bg-indigo-500/20 text-indigo-300 px-1.5 py-0.5 rounded font-mono text-[13px]" {...props} />
                  ) : (
                    <pre className="bg-black/50 p-4 rounded-xl overflow-x-auto my-4 border border-white/5">
                      <code className="text-zinc-300 font-mono text-[13px]" {...props} />
                    </pre>
                  ),
                a: ({node, ...props}) => <a className="text-indigo-400 hover:text-indigo-300 underline underline-offset-4 decoration-indigo-400/30 transition-colors" target="_blank" rel="noopener noreferrer" {...props} />,
                strong: ({node, ...props}) => <strong className="font-bold text-white" {...props} />,
                blockquote: ({node, ...props}) => <blockquote className="border-l-4 border-indigo-500/50 pl-4 py-1 my-4 italic text-zinc-400 bg-indigo-500/5 rounded-r-lg" {...props} />,
                table: ({node, ...props}) => (
                  <div className="overflow-x-auto my-4 rounded-xl border border-white/10">
                    <table className="min-w-full divide-y divide-white/10" {...props} />
                  </div>
                ),
                thead: ({node, ...props}) => <thead className="bg-white/5" {...props} />,
                th: ({node, ...props}) => <th className="px-4 py-2 text-left text-xs font-semibold text-zinc-300 uppercase tracking-wider" {...props} />,
                td: ({node, ...props}) => <td className="px-4 py-2 text-sm border-t border-white/5 text-zinc-400" {...props} />,
              }}
            >
              {clean}
            </ReactMarkdown>
          )}
        </div>
        {charts.map((ticker) => (
          <div key={ticker} className="w-full">
            <InlineChart ticker={ticker} />
          </div>
        ))}
      </div>
    </motion.div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex items-center gap-2 mb-3">
      <div className="w-7 h-7 rounded-full flex items-center justify-center" style={{ background: 'rgba(99,102,241,0.2)' }}>
        <svg viewBox="0 0 24 24" className="w-3.5 h-3.5 fill-indigo-400">
          <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z" />
        </svg>
      </div>
      <div className="flex gap-1.5 px-4 py-3 rounded-2xl" style={{ background: 'rgba(31,31,36,0.95)', border: '1px solid rgba(70,69,84,0.4)' }}>
        {[0, 0.2, 0.4].map((d, i) => (
          <motion.div
            key={i}
            className="w-1.5 h-1.5 rounded-full bg-indigo-400"
            animate={{ y: [0, -4, 0] }}
            transition={{ duration: 0.6, delay: d, repeat: Infinity }}
          />
        ))}
      </div>
    </div>
  );
}

export default function ChatWindow() {
  const { chatHistory, setChatHistory, portfolio, watchlist, netWorth } = useAuth();
  const [input, setInput] = useState('');
  const [thinking, setThinking] = useState(false);
  const bottomRef = useRef();
  const textareaRef = useRef();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, thinking]);

  const buildContextPrefix = (userMsg) => {
    const holdingsSummary = portfolio.length
      ? `\n\nPortfolio Context (${portfolio.length} holdings, Net Worth ₹${Math.round(netWorth)}):\n` +
        portfolio.map((h) => `- ${h.scheme_name}: ₹${h.current_value} (${h.units} units)`).join('\n')
      : '';
    const watchlistSummary = watchlist.length
      ? `\n\nActive Watchlist Stocks: ${watchlist.join(', ')}`
      : '';
    return `${userMsg}${holdingsSummary}${watchlistSummary}`;
  };

  const send = async () => {
    const text = input.trim();
    if (!text || thinking) return;
    const userMsg = { role: 'user', content: text };
    
    // Optimistically add just the user's base text to the chat UI
    setChatHistory((h) => [...h, userMsg]);
    setInput('');
    setThinking(true);

    try {
      // Build the enriched prompt with context
      const enrichedPrompt = buildContextPrefix(text);
      
      // Build the message history array for the LangGraph agent
      // We map over existing history and append the current enriched prompt
      const payloadMessages = [...chatHistory, { role: 'user', content: enrichedPrompt }].map(m => ({
        role: m.role,
        content: m.content
      }));

      const res = await api.post('/agent/chat', { messages: payloadMessages });
      
      const responseContent = res.data.response || res.data.message || 'Done.';
      const aiMsg = { role: 'assistant', content: responseContent };
      setChatHistory((h) => [...h, aiMsg]);
    } catch (err) {
      const errMsg = { role: 'assistant', content: '⚠️ Could not reach the Oracle. Please check your connection.' };
      setChatHistory((h) => [...h, errMsg]);
    } finally {
      setThinking(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-1">
        {chatHistory.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full gap-4 opacity-50">
            <div className="w-12 h-12 rounded-2xl bg-indigo-600/20 flex items-center justify-center">
              <svg viewBox="0 0 24 24" className="w-6 h-6 fill-indigo-400">
                <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z" />
              </svg>
            </div>
            <p className="text-[#c7c4d7] text-sm text-center">
              Ask the Oracle anything about your portfolio,<br />market trends, or investment strategy.
            </p>
          </div>
        )}
        <AnimatePresence>
          {chatHistory.map((msg, i) => (
            <MessageBubble key={i} msg={msg} />
          ))}
        </AnimatePresence>
        {thinking && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <div
        className="px-4 py-3"
        style={{ borderTop: '1px solid rgba(70,69,84,0.3)' }}
      >
        <div
          className="flex items-end gap-2 rounded-2xl px-4 py-2"
          style={{ background: 'rgba(31,31,36,0.9)', border: '1px solid rgba(99,102,241,0.2)' }}
        >
          <textarea
            ref={textareaRef}
            className="flex-1 bg-transparent text-sm text-[#e3e2e8] resize-none outline-none placeholder-[#464554] leading-relaxed"
            placeholder="Ask the Oracle… (Shift+Enter for new line)"
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
            style={{ maxHeight: '120px', overflowY: 'auto' }}
            onInput={(e) => {
              e.target.style.height = 'auto';
              e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
            }}
          />
          <motion.button
            onClick={send}
            disabled={!input.trim() || thinking}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            className="w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 disabled:opacity-30 transition-all"
            style={{ background: 'linear-gradient(135deg, #6366f1, #818cf8)' }}
          >
            <svg viewBox="0 0 24 24" className="w-4 h-4 fill-white" style={{ transform: 'rotate(90deg) translateX(-1px)' }}>
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
            </svg>
          </motion.button>
        </div>
        <p className="text-center text-[10px] text-[#464554] mt-1.5 italic">Context-aware · Your portfolio data is appended automatically</p>
      </div>
    </div>
  );
}
