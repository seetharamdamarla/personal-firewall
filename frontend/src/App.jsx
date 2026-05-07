import React, { useState, useEffect } from 'react';
import { Shield, ShieldAlert, ShieldCheck, Activity, Terminal, Trash2, Crosshair, Globe as GlobeIcon, Zap } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { motion, AnimatePresence } from 'framer-motion';
import { getBlockedIps, blockIp, unblockIp } from './api';
import { Globe } from './components/Globe';
import { Meteors } from './components/Meteors';
import { NumberTicker } from './components/NumberTicker';

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
    const interval = setInterval(fetchData, 5000);
    
    const ws = new WebSocket('ws://172.16.206.50:8000/ws/alerts');
    ws.onmessage = (event) => {
      const alert = JSON.parse(event.data);
      setAlerts(prev => [alert, ...prev].slice(0, 5));
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

  const avgThreatScore = blockedIps.length 
    ? Math.round(blockedIps.reduce((acc, curr) => acc + curr.threat_score, 0) / blockedIps.length)
    : 0;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 p-8 font-sans selection:bg-slate-200 overflow-x-hidden relative">
      <div className="max-w-7xl mx-auto relative z-10">
        
        {/* Header */}
        <header className="flex justify-between items-center mb-12">
          <motion.h1 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl font-bold flex items-center gap-4 text-slate-900 tracking-tight"
          >
            <Shield className="w-10 h-10 text-slate-900" />
            Enterprise SOC
          </motion.h1>
          <motion.div 
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex items-center gap-3 px-4 py-2 bg-emerald-50 border border-emerald-200 text-emerald-700 rounded-full font-medium shadow-sm"
          >
            <span className="w-2.5 h-2.5 bg-emerald-500 rounded-full animate-pulse" />
            System Protected
          </motion.div>
        </header>

        {/* Bento Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          
          {/* Active Blocks Metric */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="col-span-1 p-6 rounded-2xl bg-white border border-slate-200 shadow-sm relative group overflow-hidden"
          >
            <div className="flex items-center gap-5 relative z-10">
              <div className="p-4 rounded-xl bg-red-50 text-red-600 border border-red-100">
                <ShieldAlert className="w-8 h-8" />
              </div>
              <div>
                <p className="text-slate-500 font-medium text-sm mb-1">Total Active Blocks</p>
                <div className="text-4xl font-bold text-slate-900 flex items-center">
                  <NumberTicker value={blockedIps.length} />
                </div>
              </div>
            </div>
          </motion.div>

          {/* Average Threat Score Metric */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="col-span-1 p-6 rounded-2xl bg-white border border-slate-200 shadow-sm relative group overflow-hidden"
          >
            <div className="flex items-center gap-5 relative z-10">
              <div className="p-4 rounded-xl bg-blue-50 text-blue-600 border border-blue-100">
                <Activity className="w-8 h-8" />
              </div>
              <div>
                <p className="text-slate-500 font-medium text-sm mb-1">Global Threat Score</p>
                <div className="text-4xl font-bold text-slate-900 flex items-center">
                  <NumberTicker value={avgThreatScore} />
                  <span className="text-2xl ml-1 text-slate-400">%</span>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Interactive Globe Card */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="col-span-1 lg:row-span-2 p-6 rounded-2xl bg-white border border-slate-200 shadow-sm relative overflow-hidden flex flex-col items-center justify-center min-h-[400px]"
          >
            <div className="absolute top-6 left-6 flex items-center gap-2 text-slate-900 font-bold z-10">
              <GlobeIcon className="w-5 h-5 text-slate-400" /> Attack Origin Map
            </div>
            <Globe className="absolute top-10" blockedIps={blockedIps} />
          </motion.div>

          {/* Manual Intervention Form */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="col-span-1 lg:col-span-2 p-6 rounded-2xl bg-slate-900 border border-slate-800 relative overflow-hidden shadow-xl"
          >
            <Meteors number={15} />
            <div className="relative z-10">
              <h2 className="text-xl font-bold mb-6 flex items-center gap-3 text-white">
                <Crosshair className="w-6 h-6 text-slate-400" />
                Manual Mitigation
              </h2>
              <form onSubmit={handleBlock} className="flex gap-4 items-end">
                <div className="flex-1">
                  <label className="block text-sm font-medium text-slate-300 mb-2">Target IP Address</label>
                  <input 
                    type="text" 
                    required
                    value={targetIp}
                    onChange={e => setTargetIp(e.target.value)}
                    className="w-full bg-slate-950/50 border border-slate-700 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-400 transition-all"
                    placeholder="e.g. 185.176.222.106"
                  />
                </div>
                <div className="flex-1">
                  <label className="block text-sm font-medium text-slate-300 mb-2">Reason</label>
                  <input 
                    type="text" 
                    value={reason}
                    onChange={e => setReason(e.target.value)}
                    className="w-full bg-slate-950/50 border border-slate-700 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-400 transition-all"
                    placeholder="Suspicious packet payload"
                  />
                </div>
                <button 
                  type="submit" 
                  disabled={isBlocking}
                  className="bg-white hover:bg-slate-200 text-slate-900 font-bold py-3 px-6 rounded-xl transition-all flex items-center gap-2 disabled:opacity-50 min-w-[160px] justify-center shadow-lg"
                >
                  {isBlocking ? (
                    <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }}>
                      <Zap className="w-5 h-5" />
                    </motion.div>
                  ) : (
                    <><Zap className="w-5 h-5" /> Enforce Rule</>
                  )}
                </button>
              </form>
            </div>
          </motion.div>
        </div>

        {/* Animated Table */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="rounded-2xl bg-white border border-slate-200 shadow-sm overflow-hidden"
        >
          <div className="p-6 border-b border-slate-100 flex items-center gap-3 bg-slate-50/50">
            <Terminal className="w-6 h-6 text-slate-400" />
            <h2 className="text-lg font-bold text-slate-900">Kernel-Level nftables Drops</h2>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-white text-slate-500 text-sm border-b border-slate-100">
                  <th className="px-6 py-4 font-semibold">Target IP</th>
                  <th className="px-6 py-4 font-semibold">Threat Intel</th>
                  <th className="px-6 py-4 font-semibold">Geolocation</th>
                  <th className="px-6 py-4 font-semibold">Trigger Source</th>
                  <th className="px-6 py-4 font-semibold">Time Elapsed</th>
                  <th className="px-6 py-4 font-semibold text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                <AnimatePresence>
                  {blockedIps.map((block) => (
                    <motion.tr 
                      key={block.ip}
                      initial={{ opacity: 0, height: 0, backgroundColor: "#f8fafc" }}
                      animate={{ opacity: 1, height: "auto", backgroundColor: "#ffffff" }}
                      exit={{ opacity: 0, x: -50 }}
                      transition={{ duration: 0.3 }}
                      className="group hover:bg-slate-50 transition-colors"
                    >
                      <td className="px-6 py-4 font-mono font-medium text-slate-900">{block.ip}</td>
                      <td className="px-6 py-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-bold border ${
                          block.threat_score > 50 ? 'bg-red-50 text-red-600 border-red-200' :
                          block.threat_score > 10 ? 'bg-amber-50 text-amber-600 border-amber-200' :
                          'bg-emerald-50 text-emerald-600 border-emerald-200'
                        }`}>
                          {block.threat_score}% Score
                        </span>
                      </td>
                      <td className="px-6 py-4 text-slate-600 flex items-center gap-2">
                        <GlobeIcon className="w-4 h-4 text-slate-400" /> {block.country}
                      </td>
                      <td className="px-6 py-4">
                        <span className="px-2 py-1 bg-slate-100 text-slate-600 rounded text-xs font-medium border border-slate-200">
                          {block.reason}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-slate-500 text-sm">
                        {block.created_at ? formatDistanceToNow(new Date(block.created_at + 'Z'), { addSuffix: true }) : 'Just now'}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button 
                          onClick={() => handleUnblock(block.ip)}
                          className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors inline-flex items-center gap-2 text-sm font-medium"
                        >
                          <Trash2 className="w-4 h-4" /> Unblock
                        </button>
                      </td>
                    </motion.tr>
                  ))}
                  {blockedIps.length === 0 && (
                    <tr>
                      <td colSpan="6" className="px-6 py-12 text-center text-slate-500 bg-slate-50/50">
                        System is secure. No active drops in the kernel.
                      </td>
                    </tr>
                  )}
                </AnimatePresence>
              </tbody>
            </table>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

export default App;
