import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import { portfolioApi, watchlistApi } from '../lib/api';
import toast from 'react-hot-toast';

const WATCHLIST_OPTIONS = [
  { label: 'Reliance Industries', ticker: 'RELIANCE.NS' },
  { label: 'TCS', ticker: 'TCS.NS' },
  { label: 'Infosys', ticker: 'INFY.NS' },
  { label: 'HDFC Bank', ticker: 'HDFCBANK.NS' },
  { label: 'ICICI Bank', ticker: 'ICICIBANK.NS' },
  { label: 'Zomato', ticker: 'ZOMATO.NS' },
  { label: 'Adani Ports', ticker: 'ADANIPORTS.NS' },
  { label: 'Wipro', ticker: 'WIPRO.NS' },
];

function fmt(v) {
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(v);
}

export default function Sidebar() {
  const { userName, netWorth, portfolio, setPortfolio, watchlist, setWatchlist, token, authStatus } = useAuth();
  const [uploadOpen, setUploadOpen] = useState(false);
  const [casFile, setCasFile] = useState(null);
  const [casPass, setCasPass] = useState('');
  const [uploading, setUploading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [selectedTickers, setSelectedTickers] = useState(watchlist);
  const [dragOver, setDragOver] = useState(false);
  const fileRef = useRef();

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files[0];
    if (f?.type === 'application/pdf') setCasFile(f);
    else toast.error('Only PDF files accepted');
  };

  const uploadCAS = async () => {
    if (!casFile) return toast.error('Select a PDF first');
    if (!casPass) return toast.error('Enter your PAN card number as password');
    setUploading(true);
    try {
      const res = await portfolioApi.upload(casFile, casPass, token);
      setPortfolio(res.data.holdings || []);
      toast.success(`Loaded ${res.data.holdings?.length || 0} holdings`);
      setUploadOpen(false);
      setCasFile(null);
      setCasPass('');
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const toggleTicker = (ticker) => {
    setSelectedTickers((prev) =>
      prev.includes(ticker) ? prev.filter((t) => t !== ticker) : [...prev, ticker]
    );
  };

  const syncWatchlist = async () => {
    setSyncing(true);
    try {
      await watchlistApi.sync(selectedTickers);
      setWatchlist(selectedTickers);
      toast.success('Watchlist synced!');
    } catch (err) {
      toast.error('Sync failed');
    } finally {
      setSyncing(false);
    }
  };

  return (
    <aside
      className="w-80 h-screen flex flex-col overflow-y-auto py-6 px-4 gap-4"
      style={{
        background: 'rgba(27,28,34,0.95)',
        borderRight: '1px solid rgba(99,102,241,0.08)',
        backdropFilter: 'blur(12px)',
      }}
    >
      {/* Header */}
      <div className="flex items-center gap-2.5 px-2 mb-2">
        <div className="w-8 h-8 rounded-lg bg-indigo-600/30 flex items-center justify-center border border-indigo-500/20">
          <svg viewBox="0 0 24 24" className="w-4 h-4 fill-indigo-400">
            <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z" />
          </svg>
        </div>
        <div>
          <p className="text-xs text-[#908fa0] leading-none">ET Market Oracle</p>
          <p className="text-sm font-medium text-[#e3e2e8]">{authStatus === 'guest' ? 'Guest Mode' : userName}</p>
        </div>
      </div>

      {/* Net Worth Card */}
      <div
        className="rounded-2xl p-4 relative overflow-hidden"
        style={{ background: 'linear-gradient(135deg, rgba(99,102,241,0.15), rgba(129,140,248,0.08))', border: '1px solid rgba(99,102,241,0.2)' }}
      >
        <div className="absolute inset-0 opacity-10" style={{ background: 'radial-gradient(circle at 80% 20%, #6366f1, transparent 60%)' }} />
        <p className="text-xs text-[#908fa0] mb-1 relative z-10">Total Portfolio Value</p>
        <p className="text-3xl font-bold text-[#fbbf24] tracking-tight relative z-10" style={{ letterSpacing: '-0.02em' }}>
          {fmt(netWorth)}
        </p>
        <p className="text-xs text-[#c7c4d7] mt-1.5 relative z-10">{portfolio.length} schemes</p>
      </div>

      {/* CAS Upload */}
      <section className="rounded-2xl p-4" style={{ background: 'rgba(31,31,36,0.8)', border: '1px solid rgba(70,69,84,0.3)' }}>
        <button
          onClick={() => setUploadOpen((o) => !o)}
          className="w-full flex items-center justify-between text-sm font-medium text-[#e3e2e8]"
        >
          <span>📄 Upload CAS Statement</span>
          <motion.span animate={{ rotate: uploadOpen ? 180 : 0 }} className="text-[#908fa0]">▼</motion.span>
        </button>
        <AnimatePresence>
          {uploadOpen && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden"
            >
              <div className="mt-3 text-xs text-[#908fa0] mb-2">
                Download a <span className="text-indigo-400">Detailed CAS</span> from CAMS/KFintech. Password = PAN in ALL CAPS.
              </div>
              <div
                onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleDrop}
                onClick={() => fileRef.current?.click()}
                className="rounded-xl border-2 border-dashed p-4 text-center cursor-pointer transition-colors duration-200"
                style={{ borderColor: dragOver ? '#6366f1' : 'rgba(99,102,241,0.25)', background: dragOver ? 'rgba(99,102,241,0.08)' : 'transparent' }}
              >
                <input ref={fileRef} type="file" accept="application/pdf" className="hidden" onChange={(e) => setCasFile(e.target.files[0])} />
                <p className="text-xs text-[#c7c4d7]">{casFile ? `✓ ${casFile.name}` : 'Drop PDF or click to browse'}</p>
              </div>
              <input
                className="w-full mt-2 px-3 py-2 rounded-xl text-xs text-[#e3e2e8] bg-transparent outline-none"
                style={{ border: '1px solid rgba(70,69,84,0.5)' }}
                placeholder="PDF Password (PAN card)"
                type="password"
                value={casPass}
                onChange={(e) => setCasPass(e.target.value)}
              />
              <motion.button
                onClick={uploadCAS}
                disabled={uploading}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="w-full mt-2 py-2 rounded-xl text-sm font-medium text-white"
                style={{ background: 'linear-gradient(135deg, #6366f1, #818cf8)' }}
              >
                {uploading ? 'Uploading…' : 'Upload & Parse'}
              </motion.button>
            </motion.div>
          )}
        </AnimatePresence>
      </section>

      {/* Holdings */}
      {portfolio.length > 0 && (
        <section className="rounded-2xl p-4" style={{ background: 'rgba(31,31,36,0.8)', border: '1px solid rgba(70,69,84,0.3)' }}>
          <p className="text-xs font-semibold text-[#908fa0] uppercase tracking-widest mb-3">Current Holdings</p>
          <div className="space-y-2">
            {portfolio.slice(0, 5).map((h, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                className="flex items-center justify-between"
              >
                <p className="text-xs text-[#c7c4d7] truncate max-w-[150px]">{h.scheme_name}</p>
                <p className="text-xs font-medium text-[#fbbf24] tabular-nums">{fmt(h.current_value)}</p>
              </motion.div>
            ))}
            {portfolio.length > 5 && (
              <p className="text-xs text-[#908fa0] text-center">+{portfolio.length - 5} more</p>
            )}
          </div>
        </section>
      )}

      {/* Watchlist */}
      <section className="rounded-2xl p-4" style={{ background: 'rgba(31,31,36,0.8)', border: '1px solid rgba(70,69,84,0.3)' }}>
        <p className="text-xs font-semibold text-[#908fa0] uppercase tracking-widest mb-3">Equity Watchlist</p>
        <div className="flex flex-wrap gap-2 mb-3">
          {WATCHLIST_OPTIONS.map(({ label, ticker }) => {
            const selected = selectedTickers.includes(ticker);
            return (
              <motion.button
                key={ticker}
                onClick={() => toggleTicker(ticker)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-2.5 py-1 rounded-lg text-xs font-medium transition-all duration-150"
                style={{
                  background: selected ? 'rgba(99,102,241,0.25)' : 'rgba(52,52,57,0.8)',
                  color: selected ? '#c0c1ff' : '#908fa0',
                  border: `1px solid ${selected ? 'rgba(99,102,241,0.4)' : 'rgba(70,69,84,0.3)'}`,
                }}
              >
                {label}
              </motion.button>
            );
          })}
        </div>
        <motion.button
          onClick={syncWatchlist}
          disabled={syncing || selectedTickers.length === 0}
          whileHover={{ scale: 1.02, boxShadow: '0 0 16px rgba(99,102,241,0.4)' }}
          whileTap={{ scale: 0.98 }}
          className="w-full py-2 rounded-xl text-sm font-semibold text-white disabled:opacity-50"
          style={{ background: 'linear-gradient(135deg, #6366f1, #818cf8)' }}
        >
          {syncing ? 'Syncing…' : '⚡ Sync Live Market Data'}
        </motion.button>
      </section>
    </aside>
  );
}
