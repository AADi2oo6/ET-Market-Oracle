import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
});

// Attach JWT token to every request if present
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth endpoints
export const authApi = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  register: (name, email, phone, password) =>
    api.post('/auth/register', { name, email, phone, password }),
};

// Portfolio endpoints
export const portfolioApi = {
  getMe: () => api.get('/portfolio/me'),
  upload: (file, password, token) => {
    const form = new FormData();
    form.append('file', file);
    form.append('password', password);
    return api.post('/portfolio/upload', form, {
      headers: {
        'Content-Type': 'multipart/form-data',
        Authorization: `Bearer ${token}`,
      },
    });
  },
};

// Watchlist endpoints
export const watchlistApi = {
  getMe: () => api.get('/watchlist/me'),
  sync: (tickers) => api.post('/watchlist/sync', { tickers }),
};

// Market data endpoint (to be added on backend)
export const marketApi = {
  getHistory: (tickers, period) =>
    api.get('/market/history', { params: { tickers: tickers.join(','), period } }),
};

// Agent chat endpoint
export const agentApi = {
  chat: (message) => api.post('/agent/chat', { message }),
};

export default api;
