import { Toaster } from 'react-hot-toast';
import { AnimatePresence, motion } from 'framer-motion';
import { AuthProvider, useAuth } from './context/AuthContext';
import AuthGate from './pages/AuthGate';
import Dashboard from './pages/Dashboard';

function AppRouter() {
  const { authStatus, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#0a0b0f]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin" />
          <p className="text-[#908fa0] text-sm italic">Awakening the Oracle…</p>
        </div>
      </div>
    );
  }

  return (
    <AnimatePresence mode="wait">
      {!authStatus ? (
        <motion.div
          key="auth"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
        >
          <AuthGate />
        </motion.div>
      ) : (
        <motion.div
          key="dashboard"
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.35 }}
          style={{ height: '100vh' }}
        >
          <Dashboard />
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: 'rgba(31,31,36,0.95)',
            color: '#e3e2e8',
            border: '1px solid rgba(99,102,241,0.3)',
            backdropFilter: 'blur(12px)',
            fontSize: '13px',
            borderRadius: '12px',
          },
          success: { iconTheme: { primary: '#10b981', secondary: '#0a0b0f' } },
          error: { iconTheme: { primary: '#f43f5e', secondary: '#0a0b0f' } },
        }}
      />
      <AppRouter />
    </AuthProvider>
  );
}
