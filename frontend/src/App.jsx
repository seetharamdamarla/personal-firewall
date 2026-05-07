import React, { useState, useEffect } from 'react';
import { Shield, ShieldAlert, ShieldCheck, Activity, Terminal, Trash2, Crosshair, Globe } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { getBlockedIps, blockIp, unblockIp } from './api';
import './index.css';

function App() {
  const [blockedIps, setBlockedIps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [targetIp, setTargetIp] = useState('');
  const [reason, setReason] = useState('');
  const [isBlocking, setIsBlocking] = useState(false);
  const [alerts, setAlerts] = useState([]);

  const fetchData = async () => {
    try {
      const data = await getBlockedIps();
      setBlockedIps(data);
    } catch (error) {
      console.error("Failed to fetch data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Auto-refresh data every 5s
    
    // Connect to FastAPI WebSocket
    const ws = new WebSocket('ws://172.16.206.50:8000/ws/alerts');
    ws.onmessage = (event) => {
      const alert = JSON.parse(event.data);
      setAlerts(prev => [alert, ...prev].slice(0, 5)); // Keep latest 5 alerts
    };

    return () => {
      clearInterval(interval);
      ws.close();
    };
  }, []);

  const handleBlock = async (e) => {
    e.preventDefault();
    if (!targetIp) return;
    
    setIsBlocking(true);
    try {
      await blockIp(targetIp, reason || "Manual SOC Action");
      setTargetIp('');
      setReason('');
      await fetchData();
    } catch (error) {
      alert("Failed to block IP: " + error.message);
    } finally {
      setIsBlocking(false);
    }
  };

  const handleUnblock = async (ip) => {
    try {
      await unblockIp(ip);
      await fetchData();
    } catch (error) {
      alert("Failed to unblock IP: " + error.message);
    }
  };

  const getThreatColor = (score) => {
    if (score > 50) return 'threat-high';
    if (score > 10) return 'threat-medium';
    return 'threat-low';
  };

  const avgThreatScore = blockedIps.length 
    ? Math.round(blockedIps.reduce((acc, curr) => acc + curr.threat_score, 0) / blockedIps.length)
    : 0;

  return (
    <div>
      <header className="dashboard-header">
        <h1 className="title">
          <Shield size={36} color="var(--accent-color)" />
          Personal Firewall SOC
        </h1>
        <div className="status-badge">
          <div className="status-dot"></div>
          System Protected
        </div>
      </header>

      <div className="metrics-grid">
        <div className="glass-panel metric-card">
          <div className="metric-icon danger">
            <ShieldAlert size={28} />
          </div>
          <div className="metric-info">
            <h3>Active Blocks</h3>
            <p>{blockedIps.length}</p>
          </div>
        </div>

        <div className="glass-panel metric-card">
          <div className="metric-icon blue">
            <Activity size={28} />
          </div>
          <div className="metric-info">
            <h3>Avg Threat Score</h3>
            <p>{avgThreatScore}%</p>
          </div>
        </div>

        <div className="glass-panel metric-card">
          <div className="metric-icon green">
            <ShieldCheck size={28} />
          </div>
          <div className="metric-info">
            <h3>Live WebSocket</h3>
            <p>Connected</p>
          </div>
        </div>
      </div>

      <div className="main-grid">
        <div className="glass-panel">
          <h2 className="section-title">
            <Terminal size={20} />
            Active Firewall Rules (nftables)
          </h2>
          
          <div className="table-container">
            {loading ? (
              <p style={{ color: 'var(--text-secondary)' }}>Loading firewall state...</p>
            ) : blockedIps.length === 0 ? (
              <p style={{ color: 'var(--text-secondary)' }}>No active blocks. System is quiet.</p>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>IP Address</th>
                    <th>Threat Intel</th>
                    <th>Origin</th>
                    <th>Trigger Reason</th>
                    <th>Time</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {blockedIps.map((block) => (
                    <tr key={block.ip}>
                      <td style={{ fontFamily: 'monospace', fontSize: '1rem' }}>{block.ip}</td>
                      <td className={getThreatColor(block.threat_score)}>
                        {block.threat_score}% Score
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <Globe size={14} color="var(--text-secondary)" />
                          {block.country}
                        </div>
                      </td>
                      <td><span className="badge">{block.reason}</span></td>
                      <td style={{ color: 'var(--text-secondary)' }}>
                        {formatDistanceToNow(new Date(block.created_at + 'Z'), { addSuffix: true })}
                      </td>
                      <td>
                        <button 
                          className="btn-danger btn-sm"
                          onClick={() => handleUnblock(block.ip)}
                        >
                          <Trash2 size={14} /> Unblock
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        <div className="side-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div className="glass-panel">
            <h2 className="section-title">
              <Crosshair size={20} />
              Manual Intervention
            </h2>
            <form onSubmit={handleBlock}>
              <div className="input-group">
                <label>Target IP Address</label>
                <input 
                  type="text" 
                  placeholder="e.g. 192.168.1.50" 
                  value={targetIp}
                  onChange={(e) => setTargetIp(e.target.value)}
                  required
                />
              </div>
              <div className="input-group">
                <label>Reason</label>
                <input 
                  type="text" 
                  placeholder="Suspicious activity" 
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                />
              </div>
              <button type="submit" className="btn-primary" disabled={isBlocking}>
                <ShieldAlert size={18} />
                {isBlocking ? 'Applying Block...' : 'Block & Analyze IP'}
              </button>
            </form>
          </div>

          {alerts.length > 0 && (
            <div className="glass-panel" style={{ border: '1px solid var(--danger-color)' }}>
              <h2 className="section-title" style={{ color: 'var(--danger-color)' }}>
                <Activity size={20} />
                Live Alerts
              </h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {alerts.map((alert, i) => (
                  <div key={i} style={{ padding: '1rem', background: 'rgba(248, 81, 73, 0.1)', borderRadius: '8px', fontSize: '0.875rem' }}>
                    <strong>{alert.type.toUpperCase()}:</strong> New event received via WebSocket.
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
