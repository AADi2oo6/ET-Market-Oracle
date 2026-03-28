import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

// Animated background lines
function OracleBackground() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      <svg className="absolute inset-0 w-full h-full" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="lineGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#6366f1" stopOpacity="0" />
            <stop offset="50%" stopColor="#6366f1" stopOpacity="0.6" />
            <stop offset="100%" stopColor="#818cf8" stopOpacity="0" />
          </linearGradient>
          <radialGradient id="glowGrad" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#6366f1" stopOpacity="0.15" />
            <stop offset="100%" stopColor="#6366f1" stopOpacity="0" />
          </radialGradient>
        </defs>
        <ellipse cx="30%" cy="60%" rx="500" ry="300" fill="url(#glowGrad)" />
        <polyline
          points="0,400 150,300 250,350 380,200 480,260 580,150 700,220 800,100 900,180 1000,80 1100,140 1200,60"
          fill="none" stroke="url(#lineGrad)" strokeWidth="2" opacity="0.7"
        />
        <polyline
          points="0,500 100,450 220,480 320,380 420,420 550,320 680,370 780,280 900,320 1000,250 1100,290 1200,200"
          fill="none" stroke="#818cf8" strokeWidth="1" opacity="0.3"
        />
        {/* Dot grid */}
        {Array.from({ length: 20 }).map((_, i) =>
          Array.from({ length: 15 }).map((_, j) => (
            <circle
              key={`${i}-${j}`}
              cx={i * 70 + 20}
              cy={j * 60 + 20}
              r="1"
              fill="#6366f1"
              opacity="0.15"
            />
          ))
        )}
      </svg>
    </div>
  );
}

const TABS = ['login', 'register'];

export default function AuthGate() {
  const [tab, setTab] = useState('login');
  const [form, setForm] = useState({ email: '', password: '', name: '', phone: '' });
  const [busy, setBusy] = useState(false);
  const { login, register, loginAsGuest } = useAuth();

  const handle = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      if (tab === 'login') {
        await login(form.email, form.password);
        toast.success('Welcome back!');
      } else {
        await register(form.name, form.email, form.phone || null, form.password);
        toast.success('Account created!');
      }
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Something went wrong');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="relative min-h-screen flex bg-[#0a0b0f] overflow-hidden font-inter">
      {/* Hero side */}
      <div className="hidden lg:flex flex-col justify-center items-start w-[55%] relative px-16 py-12">
        <OracleBackground />
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-xl bg-indigo-600/30 flex items-center justify-center border border-indigo-500/20">
              <svg viewBox="0 0 24 24" className="w-6 h-6 fill-indigo-400">
                <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z" />
              </svg>
            </div>
            <span className="text-xl font-semibold text-[#e3e2e8] tracking-tight">ET Market Oracle</span>
          </div>
          <h1 className="text-6xl font-bold text-[#e3e2e8] leading-tight tracking-tight mb-4">
            Clarity amidst<br />
            <span className="text-indigo-400">market noise.</span>
          </h1>
          <p className="text-lg italic text-[#ffe2ab] font-medium opacity-90">
            Insights for the Sovereign Investor
          </p>
          <div className="mt-12 flex gap-6">
            {['Portfolio AI', 'Real-time Charts', 'CAS Upload'].map((feat) => (
              <div key={feat} className="flex items-center gap-2 text-[#c7c4d7] text-sm">
                <div className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
                {feat}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Auth card side */}
      <div className="flex-1 flex items-center justify-center px-6 py-12">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
          className="w-full max-w-md"
          style={{
            background: 'rgba(31,31,36,0.85)',
            backdropFilter: 'blur(20px)',
            WebkitBackdropFilter: 'blur(20px)',
            border: '1px solid rgba(192,193,255,0.1)',
            borderRadius: '1.25rem',
            padding: '2.5rem',
            boxShadow: '0 32px 64px rgba(99,102,241,0.08)',
          }}
        >
          {/* Logo small */}
          <div className="flex items-center gap-2 mb-6">
            <div className="w-7 h-7 rounded-lg bg-indigo-600/30 flex items-center justify-center border border-indigo-500/20">
              <svg viewBox="0 0 24 24" className="w-4 h-4 fill-indigo-400">
                <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z" />
              </svg>
            </div>
            <span className="text-sm font-semibold text-[#e3e2e8]">ET Market Oracle</span>
          </div>

          {/* Tab switcher */}
          <div className="flex rounded-xl p-1 mb-6" style={{ background: 'rgba(13,14,18,0.6)' }}>
            {TABS.map((t) => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all duration-200 capitalize ${
                  tab === t
                    ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/30'
                    : 'text-[#c7c4d7] hover:text-[#e3e2e8]'
                }`}
              >
                {t === 'login' ? 'Login' : 'Register'}
              </button>
            ))}
          </div>

          <form onSubmit={submit} className="space-y-4">
            <AnimatePresence mode="wait">
              <motion.div
                key={tab}
                initial={{ opacity: 0, x: tab === 'register' ? 20 : -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="space-y-4"
              >
                {tab === 'register' && (
                  <>
                    <OracleInput label="Full Name" name="name" type="text" value={form.name} onChange={handle} required />
                    <OracleInput label="Phone (optional)" name="phone" type="tel" value={form.phone} onChange={handle} />
                  </>
                )}
                <OracleInput label="Email" name="email" type="email" value={form.email} onChange={handle} required />
                <OracleInput label="Password" name="password" type="password" value={form.password} onChange={handle} required />
              </motion.div>
            </AnimatePresence>

            <motion.button
              type="submit"
              disabled={busy}
              whileHover={{ scale: 1.02, boxShadow: '0 0 24px rgba(99,102,241,0.5)' }}
              whileTap={{ scale: 0.98 }}
              className="w-full py-3 rounded-xl font-semibold text-white transition-all duration-200 mt-2"
              style={{ background: 'linear-gradient(135deg, #6366f1, #818cf8)', cursor: busy ? 'not-allowed' : 'pointer' }}
            >
              {busy ? <SpinnerIcon /> : tab === 'login' ? 'Login' : 'Create Account'}
            </motion.button>
          </form>

          <div className="my-5 flex items-center gap-3">
            <div className="flex-1 h-px" style={{ background: 'linear-gradient(to right, transparent, rgba(99,102,241,0.3), transparent)' }} />
            <span className="text-xs text-[#908fa0]">or</span>
            <div className="flex-1 h-px" style={{ background: 'linear-gradient(to left, transparent, rgba(99,102,241,0.3), transparent)' }} />
          </div>

          <motion.button
            onClick={loginAsGuest}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="w-full py-3 rounded-xl font-medium text-[#c7c4d7] hover:text-[#e3e2e8] transition-all duration-200 text-sm"
            style={{ border: '1px solid rgba(99,102,241,0.2)', background: 'transparent' }}
          >
            Continue as Guest
          </motion.button>

          <p className="text-center text-xs text-[#464554] mt-4 italic">
            Insights for the Sovereign Investor
          </p>
        </motion.div>
      </div>
    </div>
  );
}

function OracleInput({ label, name, type, value, onChange, required }) {
  const [focused, setFocused] = useState(false);
  return (
    <div className="relative">
      <input
        id={name}
        name={name}
        type={type}
        value={value}
        onChange={onChange}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        required={required}
        placeholder={label}
        className="w-full bg-transparent text-[#e3e2e8] text-sm rounded-xl px-4 py-3 outline-none transition-all duration-200 placeholder-[#464554]"
        style={{
          border: `1px solid ${focused ? 'rgba(99,102,241,0.7)' : 'rgba(70,69,84,0.5)'}`,
          boxShadow: focused ? '0 0 12px rgba(99,102,241,0.2)' : 'none',
        }}
      />
    </div>
  );
}

function SpinnerIcon() {
  return (
    <svg className="animate-spin mx-auto w-5 h-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
    </svg>
  );
}
