import { createContext, useContext, useState, useEffect } from 'react';
import { authApi, portfolioApi, watchlistApi } from '../lib/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [authStatus, setAuthStatus] = useState(null); // 'logged_in' | 'guest' | null
  const [userName, setUserName] = useState('');
  const [token, setToken] = useState(null);
  const [portfolio, setPortfolio] = useState([]);
  const [watchlist, setWatchlist] = useState([]);
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  // Hydrate from localStorage on mount
  useEffect(() => {
    const savedToken = localStorage.getItem('auth_token');
    const savedName = localStorage.getItem('user_name');
    if (savedToken) {
      setToken(savedToken);
      setUserName(savedName || '');
      setAuthStatus('logged_in');
      fetchUserData(savedToken);
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUserData = async (t) => {
    try {
      const [portRes, watchRes] = await Promise.all([
        portfolioApi.getMe(),
        watchlistApi.getMe(),
      ]);
      setPortfolio(portRes.data.holdings || []);
      setWatchlist(watchRes.data.tracked_stocks || []);
    } catch (_) {
      // silently ignore if not authed
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    const res = await authApi.login(email, password);
    const { access_token, name } = res.data;
    localStorage.setItem('auth_token', access_token);
    localStorage.setItem('user_name', name);
    setToken(access_token);
    setUserName(name);
    setAuthStatus('logged_in');
    await fetchUserData(access_token);
  };

  const register = async (name, email, phone, password) => {
    await authApi.register(name, email, phone, password);
    await login(email, password);
  };

  const loginAsGuest = () => {
    setAuthStatus('guest');
    setUserName('Guest');
    setLoading(false);
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_name');
    setToken(null);
    setUserName('');
    setAuthStatus(null);
    setPortfolio([]);
    setWatchlist([]);
    setChatHistory([]);
  };

  const netWorth = portfolio.reduce((sum, h) => sum + (h.current_value || 0), 0);

  return (
    <AuthContext.Provider
      value={{
        authStatus, userName, token, loading,
        portfolio, setPortfolio,
        watchlist, setWatchlist,
        chatHistory, setChatHistory,
        netWorth,
        login, register, loginAsGuest, logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
