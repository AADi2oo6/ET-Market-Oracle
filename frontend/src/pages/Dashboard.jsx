import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import Sidebar from '../components/Sidebar';
import WatchlistChart from '../components/WatchlistChart';
import ChatWindow from '../components/ChatWindow';

export default function Dashboard() {
  const { userName, logout, authStatus } = useAuth();

  return (
    <div className="flex h-screen bg-[#0a0b0f] overflow-hidden font-inter">
      {/* Sidebar */}
      <Sidebar />

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Topbar */}
        <header
          className="flex items-center justify-between px-6 py-3 flex-shrink-0"
          style={{ borderBottom: '1px solid rgba(70,69,84,0.25)', background: 'rgba(10,11,15,0.9)', backdropFilter: 'blur(8px)' }}
        >
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs text-[#c7c4d7]">Live Market Data</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm text-[#908fa0]">
              {authStatus === 'guest' ? '👤 Guest' : `👋 ${userName}`}
            </span>
            <motion.button
              onClick={logout}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="text-xs px-3 py-1.5 rounded-lg text-[#908fa0] hover:text-[#e3e2e8] transition-colors"
              style={{ border: '1px solid rgba(70,69,84,0.4)' }}
            >
              Logout
            </motion.button>
          </div>
        </header>

        {/* Scrollable main area */}
        <div className="flex-1 overflow-y-auto flex flex-col">
          {/* Watchlist chart */}
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="px-5 pt-4 pb-2 flex-shrink-0"
          >
            <WatchlistChart />
          </motion.div>

          {/* Chat area */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.4 }}
            className="flex-1 mx-5 mb-4 rounded-2xl overflow-hidden flex flex-col"
            style={{
              background: 'rgba(18,19,23,0.9)',
              border: '1px solid rgba(70,69,84,0.25)',
              minHeight: 0,
            }}
          >
            <div className="px-5 py-3 flex-shrink-0" style={{ borderBottom: '1px solid rgba(70,69,84,0.2)' }}>
              <div className="flex items-center gap-2">
                <div className="w-5 h-5 rounded-md bg-indigo-600/30 flex items-center justify-center">
                  <svg viewBox="0 0 24 24" className="w-3 h-3 fill-indigo-400">
                    <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z" />
                  </svg>
                </div>
                <span className="text-sm font-medium text-[#e3e2e8]">Oracle AI Chat</span>
                <span className="text-xs italic text-[#ffe2ab] ml-1">Insights for the Sovereign Investor</span>
              </div>
            </div>
            <div className="flex-1 min-h-0">
              <ChatWindow />
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
