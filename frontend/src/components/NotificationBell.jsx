import { useState, useEffect, useRef } from 'react';

const API_BASE = '/api';

const getAuthHeaders = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem('auth_token')}`,
});

function SeverityDot({ severity }) {
  const colors = {
    high: '#ef4444',
    medium: '#f59e0b',
    low: '#10b981',
  };
  return (
    <span
      style={{
        display: 'inline-block',
        width: 8,
        height: 8,
        borderRadius: '50%',
        background: colors[severity] || colors.medium,
        marginRight: 6,
        flexShrink: 0,
        marginTop: 5,
      }}
    />
  );
}

function BellIcon({ hasAlerts }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="22"
      height="22"
      viewBox="0 0 24 24"
      fill={hasAlerts ? 'currentColor' : 'none'}
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      style={{ display: 'block' }}
    >
      <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
      <path d="M13.73 21a2 2 0 0 1-3.46 0" />
    </svg>
  );
}

export default function NotificationBell() {
  const [alerts, setAlerts] = useState([]);
  const [open, setOpen] = useState(false);
  const [scanning, setScanning] = useState(false);
  const dropdownRef = useRef(null);

  const fetchAlerts = async () => {
    try {
      const res = await fetch(`${API_BASE}/alerts/me`, { headers: getAuthHeaders() });
      if (!res.ok) return;
      const data = await res.json();
      setAlerts(data);
    } catch (e) {
      console.error('Failed to fetch alerts', e);
    }
  };

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 60_000);
    return () => clearInterval(interval);
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handler = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const markRead = async (id) => {
    try {
      await fetch(`${API_BASE}/alerts/mark-read/${id}`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });
      setAlerts((prev) => prev.filter((a) => a.id !== id));
    } catch (e) {
      console.error('Failed to mark alert as read', e);
    }
  };

  const scanNow = async () => {
    setScanning(true);
    try {
      await fetch(`${API_BASE}/alerts/scan`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });
      await fetchAlerts();
    } catch (e) {
      console.error('Scan failed', e);
    } finally {
      setScanning(false);
    }
  };

  return (
    <div ref={dropdownRef} style={{ position: 'relative', display: 'inline-block' }}>
      {/* Bell Button */}
      <button
        id="notification-bell-btn"
        onClick={() => setOpen((o) => !o)}
        title="Notifications"
        style={{
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          color: alerts.length > 0 ? '#f59e0b' : '#94a3b8',
          padding: '6px',
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          position: 'relative',
          transition: 'color 0.2s',
        }}
      >
        <BellIcon hasAlerts={alerts.length > 0} />
        {alerts.length > 0 && (
          <span
            style={{
              position: 'absolute',
              top: 2,
              right: 2,
              background: '#ef4444',
              color: '#fff',
              borderRadius: '50%',
              width: 16,
              height: 16,
              fontSize: 10,
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              lineHeight: 1,
              border: '2px solid #0f172a',
            }}
          >
            {alerts.length > 9 ? '9+' : alerts.length}
          </span>
        )}
      </button>

      {/* Dropdown */}
      {open && (
        <div
          id="notification-dropdown"
          style={{
            position: 'absolute',
            right: 0,
            top: 'calc(100% + 8px)',
            width: 340,
            background: '#1e293b',
            border: '1px solid #334155',
            borderRadius: 12,
            boxShadow: '0 20px 40px rgba(0,0,0,0.5)',
            zIndex: 9999,
            overflow: 'hidden',
          }}
        >
          {/* Header */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '12px 16px',
              borderBottom: '1px solid #334155',
            }}
          >
            <span style={{ color: '#f1f5f9', fontWeight: 600, fontSize: 14 }}>
              🔔 Alerts {alerts.length > 0 && `(${alerts.length})`}
            </span>
            <button
              onClick={scanNow}
              disabled={scanning}
              id="scan-alerts-btn"
              style={{
                background: '#3b82f6',
                border: 'none',
                borderRadius: 6,
                color: '#fff',
                fontSize: 11,
                fontWeight: 600,
                cursor: scanning ? 'not-allowed' : 'pointer',
                padding: '4px 10px',
                opacity: scanning ? 0.6 : 1,
                transition: 'opacity 0.2s',
              }}
            >
              {scanning ? 'Scanning…' : '⚡ Scan Now'}
            </button>
          </div>

          {/* Alert List */}
          <div style={{ maxHeight: 360, overflowY: 'auto' }}>
            {alerts.length === 0 ? (
              <div
                style={{
                  padding: '24px 16px',
                  textAlign: 'center',
                  color: '#64748b',
                  fontSize: 13,
                }}
              >
                ✅ No new alerts. Click "Scan Now" to check your watchlist.
              </div>
            ) : (
              alerts.map((alert) => (
                <div
                  key={alert.id}
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: 8,
                    padding: '12px 16px',
                    borderBottom: '1px solid #1e293b',
                    background: '#0f172a',
                    transition: 'background 0.2s',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = '#1a2633')}
                  onMouseLeave={(e) => (e.currentTarget.style.background = '#0f172a')}
                >
                  <SeverityDot severity={alert.severity} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    {alert.ticker && (
                      <span
                        style={{
                          background: '#1d4ed8',
                          color: '#bfdbfe',
                          fontSize: 10,
                          fontWeight: 700,
                          padding: '1px 6px',
                          borderRadius: 4,
                          marginBottom: 4,
                          display: 'inline-block',
                          letterSpacing: '0.05em',
                        }}
                      >
                        {alert.ticker}
                      </span>
                    )}
                    <p
                      style={{
                        color: '#e2e8f0',
                        fontSize: 12,
                        lineHeight: 1.5,
                        margin: '4px 0 0',
                        wordBreak: 'break-word',
                      }}
                    >
                      {alert.message}
                    </p>
                    <span style={{ color: '#475569', fontSize: 10, marginTop: 4, display: 'block' }}>
                      {new Date(alert.created_at).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
                  </div>
                  <button
                    onClick={() => markRead(alert.id)}
                    title="Mark as read"
                    style={{
                      background: 'none',
                      border: '1px solid #334155',
                      borderRadius: 6,
                      color: '#64748b',
                      cursor: 'pointer',
                      padding: '3px 7px',
                      fontSize: 11,
                      flexShrink: 0,
                      transition: 'all 0.2s',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = '#10b981';
                      e.currentTarget.style.color = '#10b981';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = '#334155';
                      e.currentTarget.style.color = '#64748b';
                    }}
                  >
                    ✓
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
