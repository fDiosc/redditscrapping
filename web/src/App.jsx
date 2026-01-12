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
  Activity,
  Zap,
  ChevronDown,
  MessageSquare,
  User,
  Plus,
  Trash2,
  Edit,
  Globe,
  PlusCircle,
  X
} from 'lucide-react';

const API_BASE = "http://127.0.0.1:8000";

const CommentsSection = ({ postId }) => {
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchComments = async () => {
      try {
        const res = await axios.get(`${API_BASE}/threads/${postId}/comments`);
        setComments(res.data);
      } catch (err) {
        console.error("Failed to fetch comments", err);
      } finally {
        setLoading(false);
      }
    };
    fetchComments();
  }, [postId]);

  if (loading) return <div className="text-[10px] text-slate-500 italic">Finding community insights...</div>;
  if (!comments.length) return <div className="text-[10px] text-slate-600">No comments ingested for this thread.</div>;

  return (
    <div className="space-y-4">
      {comments.map(c => (
        <div key={c.id} className="bg-slate-800/20 border border-slate-700/50 p-3 rounded-lg flex gap-3">
          <div className="bg-slate-700/50 p-2 rounded-full h-fit">
            <User size={12} className="text-slate-400" />
          </div>
          <div className="flex-1 space-y-1">
            <div className="flex justify-between items-center">
              <span className="text-[10px] font-bold text-slate-400">u/{c.author}</span>
              <span className="text-[10px] text-slate-500 font-mono">Score: {c.score}</span>
            </div>
            <p className="text-[11px] text-slate-300 leading-relaxed font-medium line-clamp-3 hover:line-clamp-none transition-all cursor-default">
              {c.body}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
};

const ProductModal = ({ isOpen, onClose, onSave, product }) => {
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    pain_signals: [],
    intent_signals: [],
    target_subreddits: []
  });

  useEffect(() => {
    if (product) {
      setFormData({
        ...product,
        pain_signals: typeof product.pain_signals === 'string' ? JSON.parse(product.pain_signals) : product.pain_signals,
        intent_signals: typeof product.intent_signals === 'string' ? JSON.parse(product.intent_signals) : product.intent_signals,
        target_subreddits: typeof product.target_subreddits === 'string' ? JSON.parse(product.target_subreddits) : product.target_subreddits,
      });
    } else {
      setFormData({ name: "", description: "", pain_signals: [], intent_signals: [], target_subreddits: [] });
    }
  }, [product, isOpen]);

  if (!isOpen) return null;

  const addTag = (field, value) => {
    if (!value) return;
    setFormData(prev => ({ ...prev, [field]: [...prev[field], value] }));
  };

  const removeTag = (field, index) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field].filter((_, i) => i !== index)
    }));
  };

  return (
    <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto shadow-2xl animate-in zoom-in-95 duration-200">
        <div className="p-6 border-b border-slate-800 flex justify-between items-center sticky top-0 bg-slate-900 z-10">
          <h2 className="text-xl font-bold text-white">{product ? "Edit Product" : "Add New Product"}</h2>
          <button onClick={onClose} className="text-slate-500 hover:text-white transition-colors">
            <X size={24} />
          </button>
        </div>

        <div className="p-6 space-y-6">
          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-500 uppercase">Product Name</label>
            <input
              className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-white outline-none focus:ring-2 focus:ring-indigo-500"
              value={formData.name}
              onChange={e => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g. ProfitDoctor"
            />
          </div>

          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-500 uppercase">Description (Powers semantic matching)</label>
            <textarea
              className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-white outline-none focus:ring-2 focus:ring-indigo-500 h-32"
              value={formData.description}
              onChange={e => setFormData({ ...formData, description: e.target.value })}
              placeholder="Explain what the product does, who it's for, and why it matters..."
            />
          </div>

          {/* Tag Inputs for Signals and Subs */}
          {[
            { label: "Pain Signals (Problems you solve)", field: "pain_signals", placeholder: "e.g. losing money" },
            { label: "Intent Signals (How they search)", field: "intent_signals", placeholder: "e.g. profit tracker" },
            { label: "Target Subreddits", field: "target_subreddits", placeholder: "e.g. shopify" }
          ].map(cfg => (
            <div key={cfg.field} className="space-y-3">
              <label className="text-xs font-bold text-slate-500 uppercase">{cfg.label}</label>
              <div className="flex flex-wrap gap-2 mb-2">
                {formData[cfg.field].map((tag, i) => (
                  <span key={i} className="flex items-center gap-2 bg-slate-800 border border-slate-700 px-3 py-1 rounded-full text-xs text-indigo-400">
                    {tag}
                    <button onClick={() => removeTag(cfg.field, i)} className="text-slate-500 hover:text-red-400">
                      <X size={12} />
                    </button>
                  </span>
                ))}
              </div>
              <div className="flex gap-2">
                <input
                  id={`input-${cfg.field}`}
                  className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder={cfg.placeholder}
                  onKeyDown={e => {
                    if (e.key === 'Enter') {
                      addTag(cfg.field, e.target.value);
                      e.target.value = "";
                    }
                  }}
                />
                <button
                  onClick={() => {
                    const el = document.getElementById(`input-${cfg.field}`);
                    addTag(cfg.field, el.value);
                    el.value = "";
                  }}
                  className="bg-indigo-600 hover:bg-indigo-500 p-2 rounded-lg text-white transition-colors"
                >
                  <Plus size={20} />
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="p-6 border-t border-slate-800 flex justify-end gap-4 bg-slate-900/50">
          <button onClick={onClose} className="px-6 py-2 text-slate-400 hover:text-white font-bold transition-colors">Cancel</button>
          <button
            onClick={() => onSave(formData)}
            className="bg-indigo-600 hover:bg-indigo-500 text-white px-8 py-2 rounded-xl font-bold shadow-lg shadow-indigo-600/20 transition-all active:scale-95"
          >
            Save Product
          </button>
        </div>
      </div>
    </div>
  );
};

const ProductManagement = ({ products, onEdit, onDelete, onCreate }) => {
  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-4xl font-extrabold text-white">Product Settings</h2>
          <p className="text-slate-400">Manage your product knowledge base and matching signals.</p>
        </div>
        <button
          onClick={onCreate}
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-3 rounded-xl font-bold transition-all shadow-lg shadow-indigo-600/20"
        >
          <PlusCircle size={20} />
          Add New Product
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {products.map(p => {
          const pain = typeof p.pain_signals === 'string' ? JSON.parse(p.pain_signals) : p.pain_signals;
          const intent = typeof p.intent_signals === 'string' ? JSON.parse(p.intent_signals) : p.intent_signals;
          const subs = typeof p.target_subreddits === 'string' ? JSON.parse(p.target_subreddits) : p.target_subreddits;

          return (
            <div key={p.id} className="bg-slate-900 border border-slate-800 p-6 rounded-2xl flex flex-col gap-4 group hover:border-indigo-500/50 transition-all">
              <div className="flex justify-between items-start">
                <div className="bg-indigo-500/10 p-3 rounded-xl">
                  <Globe className="text-indigo-400" size={24} />
                </div>
                <div className="flex gap-2">
                  <button onClick={() => onEdit(p)} className="p-2 text-slate-500 hover:text-white hover:bg-slate-800 rounded-lg transition-all">
                    <Edit size={18} />
                  </button>
                  <button onClick={() => onDelete(p.id)} className="p-2 text-slate-500 hover:text-red-400 hover:bg-slate-800 rounded-lg transition-all">
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>

              <div>
                <h3 className="text-xl font-bold text-white uppercase tracking-tight">{p.name || p.id}</h3>
                <p className="text-sm text-slate-400 line-clamp-2 mt-1">{p.description}</p>
              </div>

              <div className="mt-2 space-y-3">
                <div className="flex items-center justify-between text-[10px] uppercase font-bold tracking-wider text-slate-500">
                  <span>Pain Signals</span>
                  <span className="text-indigo-400 font-mono bg-indigo-500/5 px-2 py-0.5 rounded-full">{pain.length}</span>
                </div>
                <div className="flex items-center justify-between text-[10px] uppercase font-bold tracking-wider text-slate-500">
                  <span>Intent Signals</span>
                  <span className="text-cyan-400 font-mono bg-cyan-500/5 px-2 py-0.5 rounded-full">{intent.length}</span>
                </div>
                <div className="flex items-center justify-between text-[10px] uppercase font-bold tracking-wider text-slate-500">
                  <span>Target Subs</span>
                  <span className="text-emerald-400 font-mono bg-emerald-500/5 px-2 py-0.5 rounded-full">{subs.length}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

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
  const [expandedThread, setExpandedThread] = useState(null);
  const [sortBy, setSortBy] = useState("relevance"); // "relevance" or "intensity"
  const [history, setHistory] = useState([]);
  const [view, setView] = useState("dashboard"); // "dashboard" or "products"
  const [products, setProducts] = useState([]);
  const [editingProduct, setEditingProduct] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    fetchConfig();
    fetchThreads();
    fetchHistory();
    fetchProducts();
  }, [selectedProduct]);

  const fetchProducts = async () => {
    try {
      const res = await axios.get(`${API_BASE}/api/products`);
      setProducts(res.data);
    } catch (err) {
      console.error("Failed to fetch products", err);
    }
  };

  // Status Polling
  useEffect(() => {
    let interval;
    if (syncing) {
      interval = setInterval(async () => {
        try {
          const res = await axios.get(`${API_BASE}/sync/status`);
          setSyncStatus(res.data);
          if (!res.data.is_running) {
            setSyncing(false);
            if (res.data.progress === 100) {
              fetchThreads();
              fetchHistory();
            }
            clearInterval(interval);
          }
        } catch (err) {
          console.error("Polling error:", err);
        }
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [syncing]);

  const fetchConfig = async () => {
    try {
      const res = await axios.get(`${API_BASE}/config`);
      setConfig(res.data);
      if (res.data.products?.length > 0 && !res.data.products.includes(selectedProduct)) {
        setSelectedProduct(res.data.products[0]);
      }
    } catch (err) {
      console.error("Failed to fetch config", err);
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await axios.get(`${API_BASE}/sync/history`);
      setHistory(res.data);
    } catch (err) {
      console.error("Failed to fetch history", err);
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

  const handleSaveProduct = async (pData) => {
    try {
      if (editingProduct) {
        await axios.put(`${API_BASE}/api/products/${editingProduct.id}`, pData);
      } else {
        await axios.post(`${API_BASE}/api/products`, pData);
      }
      setIsModalOpen(false);
      setEditingProduct(null);
      fetchProducts();
      fetchConfig();
    } catch (err) {
      console.error("Save failed", err);
      alert("Failed to save product");
    }
  };

  const handleDeleteProduct = async (id) => {
    if (window.confirm("Delete this product and all its analysis?")) {
      try {
        await axios.delete(`${API_BASE}/api/products/${id}`);
        fetchProducts();
        fetchConfig();
        if (selectedProduct === id) setSelectedProduct(products[0]?.id || "");
      } catch (err) {
        console.error("Delete failed", err);
      }
    }
  };

  const openEdit = (p) => {
    setEditingProduct(p);
    setIsModalOpen(true);
  };

  const openCreate = () => {
    setEditingProduct(null);
    setIsModalOpen(true);
  };

  const sortedThreads = [...threads].sort((a, b) => {
    if (sortBy === "intensity") return b.community_score - a.community_score;
    if (sortBy === "fit") return b.semantic_similarity - a.semantic_similarity;
    return b.relevance_score - a.relevance_score;
  });

  const handleSync = async () => {
    console.log("Sync triggered. Product:", selectedProduct, "Subs:", selectedSubs, "Reports:", selectedReports);
    if (selectedSubs.length === 0) {
      alert("Please select at least one subreddit.");
      return;
    }
    setSyncing(true);
    try {
      const subParams = selectedSubs.map(s => `subreddits=${s}`).join('&');
      const repParams = selectedReports.map(r => `reports=${r}`).join('&');
      const url = `${API_BASE}/sync?${subParams}&${repParams}&days=${days}&product=${selectedProduct}`;
      console.log("Calling POST:", url);
      const res = await axios.post(url);
      console.log("Sync API Response:", res.data);
    } catch (err) {
      console.error("Sync Trigger Failed:", err);
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

        <div className="flex flex-col gap-2 mb-2">
          <button
            onClick={() => setView("dashboard")}
            className={`flex items-center gap-3 p-3 rounded-lg transition-all ${view === "dashboard" ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/20" : "text-slate-400 hover:bg-slate-800"}`}
          >
            <Activity size={20} />
            <span className="text-sm font-bold">Discovery Dashboard</span>
          </button>
          <button
            onClick={() => setView("products")}
            className={`flex items-center gap-3 p-3 rounded-lg transition-all ${view === "products" ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/20" : "text-slate-400 hover:bg-slate-800"}`}
          >
            <Settings size={20} />
            <span className="text-sm font-bold">Product Settings</span>
          </button>
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

        <div className="mt-auto space-y-4">
          <section className="border-t border-slate-800 pt-6">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-4 block flex items-center gap-2">
              <RefreshCw size={14} /> Run History
            </label>
            <div className="space-y-3 max-h-60 overflow-y-auto pr-2 custom-scrollbar">
              {history.length === 0 ? (
                <p className="text-[10px] text-slate-600 italic">No past runs recorded.</p>
              ) : (
                history.map(run => (
                  <div key={run.id} className="bg-slate-800/30 border border-slate-800 p-2 rounded-lg hover:border-slate-700 transition-all cursor-pointer group">
                    <div className="flex justify-between items-start mb-1">
                      <span className="text-[10px] font-bold text-indigo-400 truncate uppercase w-2/3">{run.product}</span>
                      <span className="text-[9px] text-slate-500">{new Date(run.timestamp).toLocaleDateString([], { month: 'short', day: 'numeric' })}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-[9px] text-slate-400 truncate w-1/2">r/{run.subreddits}</span>
                      <span className={`text-[8px] px-1.5 py-0.5 rounded-full font-bold uppercase ${run.status === 'Success' ? 'bg-emerald-500/10 text-emerald-500' :
                        run.status.startsWith('Error') ? 'bg-red-500/10 text-red-500' : 'bg-indigo-500/10 text-indigo-400'
                        }`}>
                        {run.status.split(':')[0]}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </section>

          <div className="flex items-center gap-3 text-slate-500 hover:text-slate-300 transition-colors cursor-pointer pt-2">
            <Settings size={18} />
            <span className="text-sm">Advanced Settings</span>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-10 overflow-y-auto">
        <ProductModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onSave={handleSaveProduct}
          product={editingProduct}
        />

        {view === "dashboard" ? (
          <>
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
                  <h3 className="text-3xl font-bold text-orange-400">
                    {threads.length > 0 ? Math.max(...threads.map(t => t.community_score)).toFixed(1) : "0.0"}
                  </h3>
                </div>
                <BarChart3 size={32} className="text-slate-700" />
              </div>
              <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800 flex items-center justify-between shadow-sm">
                <div>
                  <p className="text-xs text-slate-500 uppercase tracking-widest mb-1">High Fit Leads</p>
                  <h3 className="text-3xl font-bold text-emerald-400">
                    {threads.filter(t => t.semantic_similarity > 0.5).length}
                  </h3>
                </div>
                <CheckCircle2 size={32} className="text-slate-700" />
              </div>
              <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800 flex items-center justify-between shadow-sm">
                <div>
                  <p className="text-xs text-slate-500 uppercase tracking-widest mb-1">Avg Product Fit</p>
                  <h3 className="text-3xl font-bold text-indigo-400">
                    {threads.length > 0 ? Math.round((threads.reduce((acc, t) => acc + t.semantic_similarity, 0) / threads.length) * 100) : 0}%
                  </h3>
                </div>
                <Radar size={32} className="text-slate-700" />
              </div>
            </div>

            {/* Threads List */}
            <div className="space-y-4">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-white flex items-center gap-3">
                  <AlertTriangle className="text-yellow-500" />
                  Intelligence Results
                </h3>

                <div className="flex bg-slate-900 p-1 rounded-lg border border-slate-800">
                  <button
                    onClick={() => setSortBy("relevance")}
                    className={`px-4 py-1.5 rounded-md text-xs font-bold transition-all ${sortBy === "relevance" ? "bg-indigo-600 text-white" : "text-slate-500 hover:text-slate-300"}`}
                  >
                    Sort by Score
                  </button>
                  <button
                    onClick={() => setSortBy("fit")}
                    className={`px-4 py-1.5 rounded-md text-xs font-bold transition-all ${sortBy === "fit" ? "bg-indigo-600 text-white" : "text-slate-500 hover:text-slate-300"}`}
                  >
                    Sort by Fit
                  </button>
                  <button
                    onClick={() => setSortBy("intensity")}
                    className={`px-4 py-1.5 rounded-md text-xs font-bold transition-all ${sortBy === "intensity" ? "bg-indigo-600 text-white" : "text-slate-500 hover:text-slate-300"}`}
                  >
                    Sort by Intensity
                  </button>
                </div>
              </div>

              {loading ? (
                <div className="h-64 flex items-center justify-center text-slate-500">Loading intelligence...</div>
              ) : (
                sortedThreads.map((thread) => {
                  const isExpanded = expandedThread === thread.id;
                  const signals = thread.signals_json ? JSON.parse(thread.signals_json) : null;

                  return (
                    <div
                      key={thread.id}
                      className={`bg-slate-900 border transition-all group flex flex-col gap-0 rounded-2xl overflow-hidden ${isExpanded ? 'border-indigo-500 shadow-2xl shadow-indigo-500/10' : 'bg-slate-900/50 border-slate-800/50 hover:border-slate-700'
                        }`}
                    >
                      <div
                        className="p-6 flex items-start gap-6 cursor-pointer"
                        onClick={() => setExpandedThread(isExpanded ? null : thread.id)}
                      >
                        <div className="flex flex-col items-center gap-1 min-w-[60px]">
                          <span className="text-xs text-slate-500 uppercase font-semibold">Score</span>
                          <div className="text-xl font-black text-indigo-400">{thread.relevance_score.toFixed(1)}</div>
                        </div>

                        <div className="flex-1 space-y-2">
                          <div className="flex items-center gap-3">
                            <span className="px-2 py-0.5 rounded bg-slate-800 text-[10px] font-bold text-indigo-300 uppercase">r/{thread.source}</span>
                            <span className="text-[10px] text-slate-500">●</span>
                            <span className="text-[10px] text-slate-500">{new Date(thread.created_at).toLocaleDateString()}</span>
                          </div>
                          <h4 className="text-lg font-bold text-slate-100 group-hover:text-white leading-tight">{thread.title}</h4>
                          {!isExpanded && <p className="text-sm text-slate-400 line-clamp-2 leading-relaxed">{thread.body}</p>}

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
                            <div className={`flex items-center gap-1 text-[10px] font-bold uppercase ml-auto px-3 py-1.5 rounded-lg border transition-all ${isExpanded
                              ? 'bg-slate-800 border-slate-700 text-slate-400'
                              : 'bg-indigo-500/10 border-indigo-500/20 text-indigo-400 hover:bg-indigo-500/20 hover:border-indigo-500/40'
                              }`}>
                              {isExpanded ? "Collapse" : "View Analysis"}
                              <ChevronDown size={14} className={`transition-transform duration-300 ${isExpanded ? 'rotate-180' : ''}`} />
                            </div>
                          </div>
                        </div>
                      </div>

                      {isExpanded && (
                        <div className="px-6 pb-6 pt-0 animate-in fade-in slide-in-from-top-2 duration-300">
                          <div className="border-t border-slate-800 pt-6 space-y-6">
                            {/* Tags Section */}
                            {signals && (
                              <div className="flex flex-wrap gap-2">
                                {signals.intents?.map(intent => (
                                  <span key={intent} className="px-2 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-[10px] font-bold text-indigo-400 uppercase">
                                    {intent}
                                  </span>
                                ))}
                                {signals.product_matches && signals.product_matches[selectedProduct.toLowerCase()] && (
                                  <>
                                    {signals.product_matches[selectedProduct.toLowerCase()].intents?.map(p_intent => (
                                      <span key={p_intent} className="px-2 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-[10px] font-bold text-cyan-400 uppercase">
                                        {p_intent}
                                      </span>
                                    ))}
                                    {signals.product_matches[selectedProduct.toLowerCase()].pain_points?.map(p_point => (
                                      <span key={p_point} className="px-2 py-1 rounded-full bg-orange-500/10 border border-orange-500/20 text-[10px] font-bold text-orange-400 uppercase">
                                        {p_point}
                                      </span>
                                    ))}
                                  </>
                                )}
                              </div>
                            )}

                            {/* Analysis Section */}
                            <div className="grid grid-cols-2 gap-8">
                              <div className="space-y-3">
                                <h5 className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                                  <FileText size={14} /> Full Thread Content
                                </h5>
                                <div className="text-sm text-slate-300 bg-slate-800/50 p-4 rounded-xl border border-slate-800 leading-relaxed max-h-64 overflow-y-auto">
                                  {thread.body}
                                  <div className="mt-4 pt-4 border-t border-slate-800">
                                    <a href={thread.url} target="_blank" rel="noreferrer" className="text-indigo-400 hover:text-indigo-300 font-bold flex items-center gap-1">
                                      Open Original Post <ExternalLink size={14} />
                                    </a>
                                  </div>
                                </div>
                              </div>

                              <div className="space-y-3">
                                <h5 className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                                  <Zap size={14} className="text-yellow-500" /> AI Insight for {selectedProduct.toUpperCase()}
                                </h5>
                                <div className="text-sm text-slate-200 bg-indigo-500/5 p-6 rounded-2xl border border-indigo-500/10 leading-relaxed shadow-inner mb-6 space-y-4">
                                  {(() => {
                                    if (!thread.ai_analysis) return <p className="italic text-slate-500">AI analysis not required for this relevance level.</p>;
                                    try {
                                      const ai = JSON.parse(thread.ai_analysis);
                                      if (ai.error) return <p className="text-red-400">Analysis failed: {ai.details}</p>;

                                      return (
                                        <div className="space-y-4">
                                          <div className="flex justify-between items-start gap-4">
                                            <div className="flex-1">
                                              <p className="font-bold text-indigo-300 text-lg mb-1">{ai.pain_point_summary}</p>
                                              <p className="text-xs text-slate-400 italic">"{ai.pain_quote}"</p>
                                            </div>
                                            <div className="flex flex-col items-end gap-2">
                                              <span className={`px-2 py-1 rounded-md text-[10px] font-black uppercase tracking-tighter ${ai.urgency === 'High' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                                                  ai.urgency === 'Medium' ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30' :
                                                    'bg-slate-700/50 text-slate-400'
                                                }`}>
                                                {ai.urgency} Urgency
                                              </span>
                                              <div className="flex items-center gap-1">
                                                <div className="h-1.5 w-16 bg-slate-800 rounded-full overflow-hidden">
                                                  <div className="h-full bg-indigo-500" style={{ width: `${(ai.product_relevance || 0) * 10}%` }}></div>
                                                </div>
                                                <span className="text-[10px] font-bold text-indigo-400">{ai.product_relevance}/10</span>
                                              </div>
                                            </div>
                                          </div>

                                          <div className="grid grid-cols-1 gap-4 pt-4 border-t border-indigo-500/10">
                                            <div>
                                              <p className="text-[10px] font-bold text-slate-500 uppercase mb-1">Why it matters</p>
                                              <p className="text-[12px] text-slate-300">{ai.relevance_explanation}</p>
                                            </div>
                                            <div className="bg-indigo-500/10 p-3 rounded-xl border border-indigo-500/20">
                                              <p className="text-[10px] font-bold text-indigo-400 uppercase mb-1 flex items-center gap-1">
                                                <MessageSquare size={12} /> Suggested Angle
                                              </p>
                                              <p className="text-[12px] text-indigo-100 italic">{ai.response_angle}</p>
                                            </div>
                                          </div>
                                        </div>
                                      );
                                    } catch (e) {
                                      return <div className="whitespace-pre-line">{thread.ai_analysis}</div>;
                                    }
                                  })()}
                                </div>

                                <h5 className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                                  <MessageSquare size={14} className="text-indigo-400" /> Top Community Responses
                                </h5>
                                <CommentsSection postId={thread.id} />
                              </div>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          </>
        ) : (
          <ProductManagement
            products={products}
            onEdit={openEdit}
            onDelete={handleDeleteProduct}
            onCreate={openCreate}
          />
        )}
      </main>
    </div>
  );
}

export default App;
