import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Radar,
  Settings,
  RefreshCw,
  FileText,
  AlertTriangle,
  BarChart3,
  ExternalLink,
  ChevronRight,
  CheckCircle2,
  Activity
} from 'lucide-react';

const API_BASE = "http://127.0.0.1:8000";

function App() {
  const [config, setConfig] = useState({ products: [], subreddits: [] });
  const [selectedProduct, setSelectedProduct] = useState("profitdoctor");
  const [selectedSubs, setSelectedSubs] = useState(["shopify"]);
  const [selectedReports, setSelectedReports] = useState(["DIRECT_FIT", "INTENSITY"]);
  const [days, setDays] = useState(3);
  const [threads, setThreads] = useState([]);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [syncStatus, setSyncStatus] = useState({ is_running: false, current_step: "Idle", progress: 0 });

  useEffect(() => {
    fetchConfig();
    fetchThreads();
  }, [selectedProduct]);

  // Status Polling
  useEffect(() => {
    let interval;
    if (syncing) {
      interval = setInterval(async () => {
        try {
          const res = await axios.get(`${API_BASE}/sync/status`);
          setSyncStatus(res.data);
          if (!res.data.is_running && res.data.progress === 100) {
            setSyncing(false);
            fetchThreads(); // Refresh list when done
            clearInterval(interval);
          }
        } catch (err) {
          console.error("Polling error", err);
        }
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [syncing]);

  const fetchConfig = async () => {
    try {
      const res = await axios.get(`${API_BASE}/config`);
      setConfig(res.data);
    } catch (err) {
      console.error("Failed to fetch config", err);
    }
  };

  const fetchThreads = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/threads?product=${selectedProduct}`);
      setThreads(res.data);
    } catch (err) {
      console.error("Failed to fetch threads", err);
    }
    setLoading(false);
  };

  const handleSync = async () => {
    setSyncing(true);
    try {
      const subParams = selectedSubs.map(s => `subreddits=${s}`).join('&');
      const repParams = selectedReports.map(r => `reports=${r}`).join('&');
      await axios.post(`${API_BASE}/sync?${subParams}&${repParams}&days=${days}`);
    } catch (err) {
      alert("Sync failed: " + (err.response?.data?.error || err.message));
      setSyncing(false);
    }
  };

  const toggleReport = (type) => {
    setSelectedReports(prev =>
      prev.includes(type) ? prev.filter(t => t !== type) : [...prev, type]
    );
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 flex">
      {/* Sidebar */}
      <aside className="w-80 bg-slate-900 border-r border-slate-800 p-6 flex flex-col gap-8 shadow-xl">
        <div className="flex items-center gap-3 text-indigo-400 mb-4">
          <Radar size={32} />
          <h1 className="text-2xl font-bold tracking-tight text-white">Radar AI</h1>
        </div>

        <div className="space-y-6">
          <section>
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2 block">Active Product</label>
            <select
              value={selectedProduct}
              onChange={(e) => setSelectedProduct(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none transition-all"
            >
              {config.products.map(p => <option key={p} value={p}>{p.toUpperCase()}</option>)}
            </select>
          </section>

          <section>
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2 block">Subreddits</label>
            <div className="grid grid-cols-1 gap-2 max-h-40 overflow-y-auto p-1">
              {config.subreddits.map(sub => (
                <label key={sub} className="flex items-center gap-3 cursor-pointer hover:text-white transition-colors">
                  <input
                    type="checkbox"
                    checked={selectedSubs.includes(sub)}
                    onChange={() => setSelectedSubs(prev => prev.includes(sub) ? prev.filter(s => s !== sub) : [...prev, sub])}
                    className="rounded border-slate-700 bg-slate-800 text-indigo-600 focus:ring-offset-slate-900"
                  />
                  <span className="text-sm">r/{sub}</span>
                </label>
              ))}
            </div>
          </section>

          <section>
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2 block">Report Types</label>
            <div className="space-y-2">
              {["DIRECT_FIT", "OPPORTUNITY", "INTENSITY"].map(type => (
                <button
                  key={type}
                  onClick={() => toggleReport(type)}
                  className={`w-full flex items-center justify-between p-3 rounded-lg border transition-all ${selectedReports.includes(type)
                    ? 'bg-indigo-500/10 border-indigo-500 text-indigo-400'
                    : 'bg-slate-800 border-slate-700 text-slate-400 hover:border-slate-600'
                    }`}
                >
                  <span className="text-sm font-medium">{type.replace('_', ' ')}</span>
                  {selectedReports.includes(type) && <CheckCircle2 size={16} />}
                </button>
              ))}
            </div>
          </section>

          <section>
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2 block">Scraping Range (Days)</label>
            <input
              type="range" min="1" max="14" value={days}
              onChange={(e) => setDays(e.target.value)}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500 mt-1">
              <span>1d</span>
              <span>7d</span>
              <span>14d</span>
            </div>
          </section>

          <div className="space-y-4">
            <button
              onClick={handleSync}
              disabled={syncing}
              className={`w-full font-bold py-4 rounded-xl flex items-center justify-center gap-3 shadow-lg transition-all active:scale-95 ${syncing
                  ? 'bg-slate-700 text-slate-400 cursor-not-allowed border border-slate-600'
                  : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-indigo-600/20'
                }`}
            >
              {syncing ? <RefreshCw className="animate-spin" /> : <Activity />}
              {syncing ? "Syncing..." : "Run Intelligence Sync"}
            </button>

            {syncing && (
              <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700/50 space-y-2 animate-in fade-in slide-in-from-bottom-2 duration-300">
                <div className="flex justify-between text-[10px] font-bold uppercase tracking-wider">
                  <span className="text-indigo-400 flex items-center gap-2">
                    <span className="relative flex h-2 w-2">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
                    </span>
                    {syncStatus.current_step}
                  </span>
                  <span className="text-slate-500">{syncStatus.progress}%</span>
                </div>
                <div className="w-full h-1 bg-slate-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-indigo-600 to-indigo-400 transition-all duration-500 ease-out"
                    style={{ width: `${syncStatus.progress}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="mt-auto border-t border-slate-800 pt-6">
          <div className="flex items-center gap-3 text-slate-500">
            <Settings size={18} />
            <span className="text-sm">Advanced Settings</span>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-10 overflow-y-auto">
        <header className="flex justify-between items-end mb-12">
          <div>
            <h2 className="text-4xl font-extrabold text-white mb-2">Discovery Dashboard</h2>
            <p className="text-slate-400">Total high-relevance matches found: <span className="text-indigo-400 font-bold">{threads.length}</span></p>
          </div>
          <div className="flex gap-4">
            <button onClick={fetchThreads} className="p-3 bg-slate-900 border border-slate-800 rounded-lg text-slate-400 hover:text-white transition-all">
              <RefreshCw size={20} className={loading ? 'animate-spin' : ''} />
            </button>
            <button className="flex items-center gap-2 bg-slate-100 text-slate-900 px-6 py-3 rounded-lg font-bold hover:bg-white transition-all">
              <FileText size={18} />
              Export Results
            </button>
          </div>
        </header>

        {/* Stats Grid */}
        <div className="grid grid-cols-3 gap-6 mb-12">
          <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800 flex items-center justify-between shadow-sm">
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-widest mb-1">Max Intensity</p>
              <h3 className="text-3xl font-bold text-orange-400">9.2</h3>
            </div>
            <BarChart3 size={32} className="text-slate-700" />
          </div>
          <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800 flex items-center justify-between shadow-sm">
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-widest mb-1">Direct Leads</p>
              <h3 className="text-3xl font-bold text-emerald-400">12</h3>
            </div>
            <CheckCircle2 size={32} className="text-slate-700" />
          </div>
          <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800 flex items-center justify-between shadow-sm">
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-widest mb-1">Avg Product Fit</p>
              <h3 className="text-3xl font-bold text-indigo-400">74%</h3>
            </div>
            <Radar size={32} className="text-slate-700" />
          </div>
        </div>

        {/* Threads List */}
        <div className="space-y-4">
          <h3 className="text-xl font-bold text-white flex items-center gap-3 mb-6">
            <AlertTriangle className="text-yellow-500" />
            Top Community Pain Points
          </h3>

          {loading ? (
            <div className="h-64 flex items-center justify-center text-slate-500">Loading intelligence...</div>
          ) : (
            threads.map((thread) => (
              <div key={thread.id} className="bg-slate-900/50 hover:bg-slate-900 border border-slate-800/50 hover:border-slate-700 p-6 rounded-2xl transition-all group flex items-start gap-6">
                <div className="flex flex-col items-center gap-1 min-w-[60px]">
                  <span className="text-xs text-slate-500 uppercase">Score</span>
                  <div className="text-xl font-black text-indigo-400">{thread.relevance_score.toFixed(1)}</div>
                </div>

                <div className="flex-1 space-y-2">
                  <div className="flex items-center gap-3">
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-[10px] font-bold text-indigo-300 uppercase">r/{thread.source}</span>
                    <span className="text-[10px] text-slate-500">●</span>
                    <span className="text-[10px] text-slate-500">{new Date(thread.created_at).toLocaleDateString()}</span>
                  </div>
                  <h4 className="text-lg font-bold text-slate-100 group-hover:text-white leading-tight">{thread.title}</h4>
                  <p className="text-sm text-slate-400 line-clamp-2 leading-relaxed">{thread.body}</p>

                  <div className="flex items-center gap-6 pt-2">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1 bg-slate-800 rounded-full overflow-hidden">
                        <div className="h-full bg-indigo-500" style={{ width: `${thread.semantic_similarity * 100}%` }}></div>
                      </div>
                      <span className="text-[10px] font-semibold text-slate-500 uppercase">Fit: {Math.round(thread.semantic_similarity * 100)}%</span>
                    </div>
                    <div className="flex items-center gap-2 text-slate-500">
                      <BarChart3 size={14} />
                      <span className="text-[10px] font-semibold uppercase">Intensity: {thread.community_score.toFixed(1)}</span>
                    </div>
                  </div>
                </div>

                <a
                  href={thread.url}
                  target="_blank"
                  rel="noreferrer"
                  className="p-3 bg-slate-800 rounded-lg text-slate-400 hover:text-white opacity-0 group-hover:opacity-100 transition-all"
                >
                  <ExternalLink size={20} />
                </a>
              </div>
            ))
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
