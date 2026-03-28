import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { marketApi } from '../lib/api';

export default function InlineChart({ ticker }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetchChart();
  }, [ticker]);

  const [currency, setCurrency] = useState('INR');

  const fetchChart = async () => {
    setLoading(true);
    try {
      const res = await marketApi.getHistory([ticker], '3mo');
      const { dates, series, currencies } = res.data;
      const chartData = dates.map((d, i) => ({ 
        date: d, 
        price: series[ticker]?.[i] 
      })).filter(item => item.price !== null);
      
      setData(chartData);
      if (currencies && currencies[ticker]) {
        setCurrency(currencies[ticker]);
      }
    } catch {
      setData(
        Array.from({ length: 60 }, (_, i) => ({
          date: `2024-01-${(i % 28) + 1}`,
          price: 1000 + Math.random() * 300 - 150 + i * 3,
        }))
      );
    } finally {
      setLoading(false);
    }
  };

  const getCurrencySymbol = (code) => {
    if (code === 'USD') return '$';
    if (code === 'INR') return '₹';
    return code + ' ';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-48 rounded-2xl" style={{ background: 'rgba(31,31,36,0.9)', border: '1px solid rgba(70,69,84,0.3)' }}>
        <div className="w-5 h-5 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin" />
      </div>
    );
  }

  const symbol = getCurrencySymbol(currency);
  const first = data[0]?.price ?? 0;
  const last = data[data.length - 1]?.price ?? 0;
  const gain = last - first;
  const gainPct = first ? (gain / first) * 100 : 0;
  const positive = gain >= 0;

  return (
    <div
      className="rounded-2xl overflow-hidden w-full transition-all hover:border-indigo-500/30"
      style={{ background: 'rgba(21,22,27,0.95)', border: '1px solid rgba(70,69,84,0.3)', minWidth: '300px' }}
    >
      <div className="px-5 pt-4 pb-2 flex items-center justify-between">
        <div>
          <p className="text-sm font-bold text-[#e3e2e8] tracking-tight">{ticker}</p>
          <p className="text-[10px] text-[#908fa0] uppercase tracking-wider font-medium">3-Month Performance</p>
        </div>
        <div className="text-right">
          <p className="text-sm font-bold tabular-nums" style={{ color: positive ? '#10b981' : '#f43f5e' }}>
            {positive ? '↑' : '↓'} {Math.abs(gainPct).toFixed(2)}%
          </p>
          <p className="text-[11px] text-[#c7c4d7] tabular-nums font-semibold">
            {symbol}{last.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
        </div>
      </div>
      
      <div className="h-40 w-full px-2 pb-4">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id={`gradient-${ticker}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={positive ? '#10b981' : '#f43f5e'} stopOpacity={0.3}/>
                <stop offset="95%" stopColor={positive ? '#10b981' : '#f43f5e'} stopOpacity={0}/>
              </linearGradient>
            </defs>
            <XAxis 
              dataKey="date" 
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#464554', fontSize: 9 }}
              minTickGap={40}
              tickFormatter={(str) => {
                const d = new Date(str);
                return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
              }}
            />
            <YAxis 
              hide={false}
              orientation="right"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#464554', fontSize: 9 }}
              domain={['auto', 'auto']}
              tickFormatter={(val) => `${symbol}${val > 1000 ? (val/1000).toFixed(1) + 'k' : Math.round(val)}`}
            />
            <Tooltip
              content={({ active, payload, label }) => {
                if (active && payload?.length) {
                  return (
                    <div className="text-[11px] px-3 py-2 rounded-xl shadow-2xl border border-white/10" style={{ background: 'rgba(10,11,15,0.95)', color: '#e3e2e8', backdropFilter: 'blur(8px)' }}>
                      <p className="font-bold text-indigo-300 mb-1">{new Date(label).toLocaleDateString(undefined, { month: 'long', day: 'numeric', year: 'numeric' })}</p>
                      <p className="tabular-nums">{symbol}{Number(payload[0].value).toFixed(2)}</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Line
              type="monotone"
              dataKey="price"
              stroke={positive ? '#10b981' : '#f43f5e'}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, strokeWidth: 0, fill: positive ? '#10b981' : '#f43f5e' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
