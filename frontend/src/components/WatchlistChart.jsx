import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend
} from 'recharts';
import { marketApi } from '../lib/api';
import { useAuth } from '../context/AuthContext';

const PERIODS = ['1mo', '6mo', '1y', '5y', 'max'];
const LINE_COLORS = ['#6366f1', '#f59e0b', '#10b981', '#f43f5e', '#8b5cf6', '#06b6d4'];

const CustomTooltip = ({ active, payload, label, currencies }) => {
  if (!active || !payload?.length) return null;
  const getSymbol = (code) => code === 'USD' ? '$' : (code === 'INR' ? '₹' : code + ' ');
  
  return (
    <div
      className="rounded-xl p-3 text-xs shadow-2xl border border-white/10"
      style={{ background: 'rgba(10,11,15,0.95)', backdropFilter: 'blur(12px)' }}
    >
      <p className="text-[#908fa0] mb-2 font-medium">{new Date(label).toLocaleDateString(undefined, { month: 'long', day: 'numeric', year: 'numeric' })}</p>
      {payload.map((p, i) => (
        <div key={i} className="flex items-center justify-between gap-4 mb-1">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full" style={{ background: p.color }} />
            <span className="text-[#c7c4d7] font-medium">{p.name}</span>
          </div>
          <span className="text-[#e3e2e8] font-bold tabular-nums">
            {getSymbol(currencies?.[p.name] || 'INR')}{Number(p.value).toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </span>
        </div>
      ))}
    </div>
  );
};

export default function WatchlistChart() {
  const { watchlist } = useAuth();
  const [period, setPeriod] = useState('1mo');
  const [data, setData] = useState([]);
  const [tickers, setTickers] = useState([]);
  const [currencies, setCurrencies] = useState({});
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(true);
  const [selected, setSelected] = useState([]);

  useEffect(() => {
    if (watchlist?.length) setSelected(watchlist);
  }, [watchlist]);

  useEffect(() => {
    if (!selected.length) return;
    fetchData();
  }, [selected, period]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await marketApi.getHistory(selected, period);
      const { dates, series, currencies: fetchedCurrencies } = res.data;
      setTickers(Object.keys(series));
      if (fetchedCurrencies) setCurrencies(fetchedCurrencies);
      
      const chartData = dates.map((d, i) => {
        const pt = { date: d };
        Object.keys(series).forEach((t) => { pt[t] = series[t][i]; });
        return pt;
      }).filter(pt => Object.values(pt).some(v => v !== null && typeof v === 'number'));

      setData(chartData);
    } catch {
      // Fallback
      setTickers(selected);
      setData([]);
    } finally {
      setLoading(false);
    }
  };

  const mainCurrencySymbol = tickers.length > 0 ? (currencies[tickers[0]] === 'USD' ? '$' : '₹') : '₹';

  return (
    <div
      className="rounded-2xl overflow-hidden transition-all duration-300"
      style={{ background: 'rgba(27,28,34,0.9)', border: '1px solid rgba(99,102,241,0.1)' }}
    >
      {/* Header */}
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-5 py-4 hover:bg-white/[0.02] transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-400">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"></polyline><polyline points="16 7 22 7 22 13"></polyline></svg>
          </div>
          <span className="text-sm font-bold text-[#e3e2e8] tracking-tight">Market Trends</span>
          {selected.length > 0 && (
            <span className="text-[10px] px-2 py-0.5 rounded-full font-bold text-indigo-300 border border-indigo-500/20 bg-indigo-500/10">
              {selected.length} ASSETS
            </span>
          )}
        </div>
        <div className="flex items-center gap-4">
          {/* Period selector */}
          {open && (
            <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
              {PERIODS.map((p) => (
                <button
                  key={p}
                  onClick={() => setPeriod(p)}
                  className="px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all duration-150"
                  style={{
                    background: period === p ? 'rgba(99,102,241,0.25)' : 'transparent',
                    color: period === p ? '#c0c1ff' : '#6b7280',
                    border: '1px solid',
                    borderColor: period === p ? 'rgba(99,102,241,0.3)' : 'transparent'
                  }}
                >
                  {p}
                </button>
              ))}
            </div>
          )}
          <motion.div animate={{ rotate: open ? 180 : 0 }} className="text-[#908fa0]">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="m6 9 6 6 6-6"></path></svg>
          </motion.div>
        </div>
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            {selected.length === 0 ? (
              <div className="px-5 pb-8 pt-2 text-center">
                <p className="text-sm text-[#908fa0]">Your watchlist is empty.</p>
                <p className="text-[10px] text-[#4b4e63] mt-1">Add stocks in the sidebar to visualize trends.</p>
              </div>
            ) : loading ? (
              <div className="h-60 flex items-center justify-center">
                <div className="w-6 h-6 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin" />
              </div>
            ) : (
              <div className="px-3 pb-6 relative">
                {/* Oracle glow behind chart */}
                <div className="absolute inset-0 pointer-events-none" style={{ background: 'radial-gradient(circle at 50% 50%, rgba(99,102,241,0.04), transparent 80%)' }} />
                <ResponsiveContainer width="100%" height={260}>
                  <LineChart data={data} margin={{ top: 20, right: 30, left: 10, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(70,69,84,0.15)" vertical={false} />
                    <XAxis 
                      dataKey="date" 
                      tick={{ fill: '#4b4e63', fontSize: 10, fontWeight: 500 }} 
                      axisLine={false} 
                      tickLine={false} 
                      minTickGap={60}
                      tickFormatter={(d) => new Date(d).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                    />
                    <YAxis 
                      tick={{ fill: '#4b4e63', fontSize: 10, fontWeight: 500 }} 
                      axisLine={false} 
                      tickLine={false} 
                      width={45} 
                      tickFormatter={(v) => `${mainCurrencySymbol}${v >= 1000 ? (v/1000).toFixed(1) + 'k' : v}`} 
                    />
                    <Tooltip content={<CustomTooltip currencies={currencies} />} />
                    <Legend 
                      verticalAlign="top" 
                      height={36} 
                      iconType="circle"
                      iconSize={8}
                      formatter={(val) => <span className="text-[10px] font-bold uppercase tracking-wider text-[#908fa0] px-2">{val}</span>}
                    />
                    {tickers.map((t, i) => (
                      <Line
                        key={t}
                        type="monotone"
                        dataKey={t}
                        stroke={LINE_COLORS[i % LINE_COLORS.length]}
                        strokeWidth={2.5}
                        dot={false}
                        activeDot={{ r: 5, strokeWidth: 0, fill: LINE_COLORS[i % LINE_COLORS.length] }}
                        animationDuration={1500}
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
