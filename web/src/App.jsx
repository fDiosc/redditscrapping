import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { SignedIn, SignedOut, UserButton, useAuth, useClerk } from "@clerk/clerk-react";
import {
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
  X,
  Search,
  TrendingUp,
  Filter,
  BarChart2,
  Shield,
  Calendar,
  ArrowUp,
  HelpCircle,
  CheckCircle,
  ChevronUp,
  LogOut,
  Layout,
  Clock,
  Sparkles,
  Check,
  Copy,
  Loader2,
  AlertCircle,
  ThumbsUp,
  ThumbsDown,
  Radar
} from 'lucide-react';
import LandingPage from './pages/LandingPage';
import SonarLogo from './components/SonarLogo';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

const STYLE_LABELS = {
  empathetic: '💜 Empathetic',
  helpful_expert: '🎓 Helpful Expert',
  casual: '😊 Casual',
  technical: '🔧 Technical',
  brief: '⚡ Brief',
  product_referral: '🚀 Product Referral'
};


const Tooltip = ({ text, children }) => {
  const [show, setShow] = useState(false);
  return (
    <div className="relative inline-block group" onMouseEnter={() => setShow(true)} onMouseLeave={() => setShow(false)}>
      {children}
      {show && (
        <div className="absolute z-[100] bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 p-2 bg-slate-800 text-slate-200 text-[10px] font-medium rounded-lg border border-slate-700 shadow-2xl animate-in fade-in zoom-in duration-200">
          <div className="relative z-10">{text}</div>
          <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-slate-800"></div>
        </div>
      )}
    </div>
  );
};

// Interactive Onboarding - Guides users through first product creation
const InteractiveOnboarding = ({ onComplete, onOpenProductModal, hasProducts, onStartSync }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);

  const steps = [
    {
      id: 'welcome',
      title: "Welcome to SonarPro! 🚀",
      subtitle: "Let's find your first leads in under 5 minutes",
      content: "SonarPro uses AI to scan Reddit and find people who need exactly what you're selling. No cold emails, no ads, just genuine conversations.",
      action: null,
      actionLabel: "Let's Go",
      icon: <Radar className="text-purple-400" size={32} />,
    },
    {
      id: 'product',
      title: "Set Up Your Product",
      subtitle: "Tell us what you're selling",
      content: hasProducts
        ? "Great! You already have a product configured. You can add more later in Product Settings."
        : "Click below to add your first product. Pro tip: paste your website URL and we'll fill in the details automatically!",
      action: hasProducts ? null : () => onOpenProductModal(),
      actionLabel: hasProducts ? "Continue" : "Add Your Product",
      icon: <PlusCircle className="text-indigo-400" size={32} />,
      skipIf: hasProducts,
    },
    {
      id: 'subreddits',
      title: "Choose Your Hunting Grounds",
      subtitle: "Where does your audience hang out?",
      content: "Select the subreddits where your ideal customers discuss their problems. We'll suggest some based on your product category.",
      action: null,
      actionLabel: "Continue",
      icon: <Globe className="text-cyan-400" size={32} />,
    },
    {
      id: 'sync',
      title: "Run Your First Scan",
      subtitle: "Let's find some leads!",
      content: "Click 'Run Intelligence Sync' in the sidebar to start scanning Reddit. This takes 2-3 minutes depending on how many subreddits you selected.",
      action: () => onStartSync(),
      actionLabel: "Start Scanning",
      icon: <Activity className="text-emerald-400" size={32} />,
    },
    {
      id: 'complete',
      title: "You're All Set! 🎉",
      subtitle: "Time to make some sales",
      content: "Once the scan completes, you'll see leads ranked by relevance. Click on any lead to see AI insights and generate a personalized response.",
      action: null,
      actionLabel: "Start Closing Deals",
      icon: <CheckCircle className="text-green-400" size={32} />,
    }
  ];

  const step = steps[currentStep];
  const totalSteps = steps.length;

  const handleNext = () => {
    // For product step without products, just open modal and don't advance
    if (step.id === 'product' && !hasProducts) {
      onOpenProductModal();
      return;
    }

    // Execute any other step action
    if (step.action) {
      step.action();
    }

    if (currentStep === totalSteps - 1) {
      onComplete();
    } else {
      setIsAnimating(true);
      setTimeout(() => {
        setCurrentStep(prev => prev + 1);
        setIsAnimating(false);
      }, 200);
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setIsAnimating(true);
      setTimeout(() => {
        setCurrentStep(prev => prev - 1);
        setIsAnimating(false);
      }, 200);
    }
  };

  return (
    <div className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-slate-950/90 backdrop-blur-md animate-in fade-in duration-300">
      <div className={`w-full max-w-lg bg-gradient-to-b from-slate-900 to-slate-950 border border-purple-500/20 rounded-3xl shadow-2xl overflow-hidden ring-1 ring-white/5 transition-all duration-200 ${isAnimating ? 'opacity-0 scale-95' : 'opacity-100 scale-100'}`}>
        {/* Progress bar */}
        <div className="h-1 bg-slate-800 flex">
          {steps.map((_, i) => (
            <div
              key={i}
              className={`flex-1 transition-all duration-500 ${i <= currentStep ? 'bg-gradient-to-r from-purple-500 to-indigo-500' : ''}`}
            />
          ))}
        </div>

        <div className="p-8">
          {/* Header */}
          <div className="flex justify-between items-start mb-6">
            <div className="p-3 bg-slate-800/50 rounded-2xl border border-slate-700/50">
              {step.icon}
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                Step {currentStep + 1} of {totalSteps}
              </span>
              <button
                onClick={onComplete}
                className="text-slate-600 hover:text-slate-400 transition-colors p-1"
                title="Skip onboarding"
              >
                <X size={18} />
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="mb-8">
            <h2 className="text-2xl font-black text-white mb-1">{step.title}</h2>
            <p className="text-sm font-medium text-purple-400 mb-4">{step.subtitle}</p>
            <p className="text-slate-400 leading-relaxed">{step.content}</p>
          </div>

          {/* Tips for specific steps */}
          {step.id === 'subreddits' && (
            <div className="bg-indigo-500/10 border border-indigo-500/20 rounded-xl p-4 mb-6">
              <p className="text-xs font-bold text-indigo-400 uppercase mb-2">💡 Pro Tips</p>
              <ul className="text-xs text-slate-400 space-y-1">
                <li>• Start with 3-5 active subreddits</li>
                <li>• Look for subreddits where people ask for recommendations</li>
                <li>• Niche subreddits often have higher quality leads</li>
              </ul>
            </div>
          )}

          {step.id === 'sync' && (
            <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-4 mb-6">
              <p className="text-xs font-bold text-emerald-400 uppercase mb-2">⏱️ What happens next</p>
              <ul className="text-xs text-slate-400 space-y-1">
                <li>• We'll scan the last 3 days of posts</li>
                <li>• AI analyzes each thread for buying signals</li>
                <li>• You'll see leads ranked by relevance</li>
              </ul>
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-between items-center pt-4 border-t border-slate-800">
            <button
              onClick={currentStep === 0 ? onComplete : handleBack}
              className="text-xs font-bold text-slate-500 hover:text-white uppercase tracking-widest transition-colors px-4 py-2"
            >
              {currentStep === 0 ? "Skip Tutorial" : "← Back"}
            </button>
            <button
              onClick={handleNext}
              className="px-8 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-sm font-black uppercase tracking-wide rounded-xl transition-all shadow-lg shadow-purple-900/30 active:scale-95 flex items-center gap-2"
            >
              {step.actionLabel}
              {currentStep < totalSteps - 1 && <ChevronRight size={16} />}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Legacy wrapper for backwards compatibility
const OnboardingWizard = ({ steps, onComplete }) => {
  return (
    <InteractiveOnboarding
      onComplete={onComplete}
      onOpenProductModal={() => { }}
      hasProducts={true}
      onStartSync={() => { }}
    />
  );
};

const CommentsSection = ({ postId }) => {
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchComments = async () => {
      try {
        const res = await axios.get(`${API_BASE}/api/threads/${postId}/comments`);
        setComments(res.data);
      } catch (err) {

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
    target_subreddits: [],
    website_url: "",
    default_response_style: "empathetic"
  });
  const [extracting, setExtracting] = useState(false);
  const [extractError, setExtractError] = useState(null);
  const [suggestedSubs, setSuggestedSubs] = useState([]);
  const { getToken } = useAuth();

  const getAuthHeaders = async () => {
    const token = await getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  useEffect(() => {
    if (product) {
      setFormData({
        ...product,
        pain_signals: typeof product.pain_signals === 'string' ? JSON.parse(product.pain_signals) : product.pain_signals,
        intent_signals: typeof product.intent_signals === 'string' ? JSON.parse(product.intent_signals) : product.intent_signals,
        target_subreddits: typeof product.target_subreddits === 'string' ? JSON.parse(product.target_subreddits) : product.target_subreddits,
      });
    } else {
      setFormData({ name: "", description: "", pain_signals: [], intent_signals: [], target_subreddits: [], website_url: "", default_response_style: "empathetic" });
    }
    setExtractError(null);
    setSuggestedSubs([]);
  }, [product, isOpen]);

  const handleExtractUrl = async () => {
    if (!formData.website_url) return;

    setExtracting(true);
    setExtractError(null);

    try {
      const headers = await getAuthHeaders();
      const res = await axios.post(`${API_BASE}/api/extract/url`, {
        url: formData.website_url
      }, { headers });

      const data = res.data;

      // Auto-fill form with extracted data
      setFormData(prev => ({
        ...prev,
        name: data.name || prev.name,
        description: data.description || prev.description,
        pain_signals: data.pain_signals?.length ? data.pain_signals : prev.pain_signals,
        intent_signals: data.intent_signals?.length ? data.intent_signals : prev.intent_signals,
      }));

      // Fetch subreddit suggestions based on category
      if (data.category) {
        try {
          const subRes = await axios.post(`${API_BASE}/api/subreddits/suggest`, {
            category: data.category,
            pain_signals: data.pain_signals,
            intent_signals: data.intent_signals
          }, { headers });
          setSuggestedSubs(subRes.data.suggestions || []);
        } catch (e) {
          // Silently fail subreddit suggestions
        }
      }

    } catch (err) {
      setExtractError(err.response?.data?.detail || "Failed to extract. Please fill in manually.");
    } finally {
      setExtracting(false);
    }
  };

  if (!isOpen) return null;

  const addTag = (field, value) => {
    if (!value || !value.trim()) return;

    let newTags = [];

    if (field === 'pain_signals') {
      // Split on periods, filter empty, trim whitespace
      newTags = value
        .split(/[.•\n]/)
        .map(s => s.trim())
        .filter(s => s.length > 3); // Ignore very short fragments
    } else if (field === 'target_subreddits') {
      // Parse subreddits: extract names from "r/shopify", "/r/marketing", etc.
      // Use regex to find all subreddit patterns and extract just the name
      const subredditPattern = /(?:\/r\/|r\/)([a-zA-Z0-9_]+)/gi;
      let match;
      const extracted = [];
      while ((match = subredditPattern.exec(value)) !== null) {
        extracted.push(match[1].toLowerCase());
      }

      // If no r/ patterns found, treat as comma/space separated plain names
      if (extracted.length === 0) {
        extracted.push(...value
          .split(/[,\s]+/)
          .map(s => s.trim().toLowerCase())
          .filter(s => s.length > 0 && /^[a-z0-9_]+$/.test(s))
        );
      }
      newTags = extracted;
    } else if (field === 'intent_signals') {
      // Split on commas, periods, or newlines
      newTags = value
        .split(/[,.\n]/)
        .map(s => s.trim())
        .filter(s => s.length > 2);
    } else {
      // Default: single tag
      newTags = [value.trim()];
    }

    // Add all new tags (avoid duplicates)
    if (newTags.length > 0) {
      setFormData(prev => ({
        ...prev,
        [field]: [...prev[field], ...newTags.filter(t => !prev[field].includes(t))]
      }));
    }
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
            <label className="text-xs font-bold text-slate-500 uppercase flex items-center gap-2">
              Website URL
              <span className="text-purple-400 font-normal">(Auto-fill with AI)</span>
            </label>
            <div className="flex gap-2">
              <input
                className="flex-1 bg-slate-800 border border-slate-700 rounded-lg p-3 text-white outline-none focus:ring-2 focus:ring-indigo-500"
                value={formData.website_url || ""}
                onChange={e => setFormData({ ...formData, website_url: e.target.value })}
                placeholder="https://yourproduct.com"
              />
              <button
                onClick={handleExtractUrl}
                disabled={extracting || !formData.website_url}
                className={`px-4 py-2 rounded-lg font-bold text-sm flex items-center gap-2 transition-all ${extracting || !formData.website_url
                  ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white shadow-lg shadow-purple-900/20'
                  }`}
              >
                {extracting ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    Extracting...
                  </>
                ) : (
                  <>
                    <Sparkles size={16} />
                    Extract
                  </>
                )}
              </button>
            </div>
            {extractError && (
              <p className="text-xs text-red-400 flex items-center gap-1 mt-1">
                <AlertCircle size={12} />
                {extractError}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-500 uppercase">Default AI Response Style</label>
            <select
              className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-white outline-none focus:ring-2 focus:ring-indigo-500"
              value={formData.default_response_style || "empathetic"}
              onChange={e => setFormData({ ...formData, default_response_style: e.target.value })}
            >
              {Object.entries(STYLE_LABELS).map(([val, label]) => (
                <option key={val} value={val}>{label}</option>
              ))}
            </select>
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

          {/* Suggested Subreddits Section */}
          {suggestedSubs.length > 0 && (
            <div className="space-y-3 bg-indigo-500/5 border border-indigo-500/20 rounded-xl p-4">
              <div className="flex justify-between items-center">
                <label className="text-xs font-bold text-indigo-400 uppercase flex items-center gap-2">
                  <Sparkles size={14} />
                  Suggested Subreddits
                </label>
                <button
                  onClick={() => {
                    const newSubs = suggestedSubs.filter(s => !formData.target_subreddits.includes(s));
                    setFormData(prev => ({
                      ...prev,
                      target_subreddits: [...prev.target_subreddits, ...newSubs]
                    }));
                    setSuggestedSubs([]);
                  }}
                  className="text-xs font-bold text-indigo-400 hover:text-indigo-300 transition-colors"
                >
                  + Add All
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {suggestedSubs.map((sub, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      if (!formData.target_subreddits.includes(sub)) {
                        setFormData(prev => ({
                          ...prev,
                          target_subreddits: [...prev.target_subreddits, sub]
                        }));
                      }
                      setSuggestedSubs(prev => prev.filter(s => s !== sub));
                    }}
                    className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${formData.target_subreddits.includes(sub)
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      : 'bg-slate-800 text-slate-300 border border-slate-700 hover:border-indigo-500/50 hover:text-indigo-300'
                      }`}
                  >
                    r/{sub} {formData.target_subreddits.includes(sub) ? '✓' : '+'}
                  </button>
                ))}
              </div>
            </div>
          )}
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
                {p.website_url && (
                  <a
                    href={p.website_url.startsWith('http') ? p.website_url : `https://${p.website_url}`}
                    target="_blank"
                    rel="noreferrer"
                    className="text-[10px] text-indigo-400 hover:text-indigo-300 font-bold flex items-center gap-1 mt-0.5"
                  >
                    {p.website_url.replace(/^https?:\/\//, '')} <ExternalLink size={10} />
                  </a>
                )}
                <p className="text-sm text-slate-400 line-clamp-2 mt-1">{p.description}</p>
              </div>

              <div className="mt-2 space-y-3">
                <div className="flex items-center justify-between text-[10px] uppercase font-bold tracking-wider text-slate-500">
                  <span>AI Style</span>
                  <span className="text-purple-400 font-mono bg-purple-500/5 px-2 py-0.5 rounded-full">{STYLE_LABELS[p.default_response_style] || STYLE_LABELS.empathetic}</span>
                </div>
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

// Empty State Component - Shown when no leads have been found yet
const EmptyDashboard = ({ hasProducts, onCreateProduct, onStartSync }) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-6 animate-in fade-in duration-500">
      {/* Decorative background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-600/5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-indigo-600/5 rounded-full blur-3xl"></div>
      </div>

      <div className="relative z-10">
        {/* Icon */}
        <div className="mb-6 p-6 bg-gradient-to-br from-purple-500/10 to-indigo-500/10 rounded-3xl border border-purple-500/20 inline-block">
          <Radar size={48} className="text-purple-400" />
        </div>

        {/* Title */}
        <h2 className="text-3xl font-black text-white mb-3">
          {hasProducts ? "Ready to Find Your First Leads!" : "Welcome to SonarPro"}
        </h2>

        {/* Subtitle */}
        <p className="text-slate-400 max-w-md mx-auto mb-8 leading-relaxed">
          {hasProducts
            ? "Your product is configured. Select some subreddits and run your first intelligence sync to discover leads."
            : "Set up your first product to start discovering sales opportunities on Reddit."
          }
        </p>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          {!hasProducts ? (
            <button
              onClick={onCreateProduct}
              className="px-8 py-4 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold rounded-xl shadow-lg shadow-purple-900/30 transition-all active:scale-95 flex items-center justify-center gap-2"
            >
              <PlusCircle size={20} />
              Add Your First Product
            </button>
          ) : (
            <>
              <button
                onClick={onStartSync}
                className="px-8 py-4 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold rounded-xl shadow-lg shadow-purple-900/30 transition-all active:scale-95 flex items-center justify-center gap-2"
              >
                <Activity size={20} />
                Run Intelligence Sync
              </button>
              <button
                onClick={onCreateProduct}
                className="px-6 py-4 bg-slate-800 hover:bg-slate-700 text-white font-bold rounded-xl border border-slate-700 transition-all flex items-center justify-center gap-2"
              >
                <Plus size={20} />
                Add Another Product
              </button>
            </>
          )}
        </div>

        {/* Quick tips */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-4 max-w-3xl mx-auto">
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 text-left">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle size={16} className="text-emerald-400" />
              <span className="text-xs font-bold text-slate-400 uppercase">Step 1</span>
            </div>
            <p className="text-sm text-slate-300">Configure your product with pain signals and keywords</p>
          </div>
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 text-left">
            <div className="flex items-center gap-2 mb-2">
              <Globe size={16} className="text-cyan-400" />
              <span className="text-xs font-bold text-slate-400 uppercase">Step 2</span>
            </div>
            <p className="text-sm text-slate-300">Select relevant subreddits where your audience hangs out</p>
          </div>
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 text-left">
            <div className="flex items-center gap-2 mb-2">
              <Sparkles size={16} className="text-purple-400" />
              <span className="text-xs font-bold text-slate-400 uppercase">Step 3</span>
            </div>
            <p className="text-sm text-slate-300">AI analyzes posts and surfaces the best leads for you</p>
          </div>
        </div>
      </div>
    </div>
  );
};

const GenerateResponseButton = ({ postId, productId, defaultStyle, onGenerated }) => {
  const [loading, setLoading] = useState(false);
  const { getToken } = useAuth();

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const token = await getToken();
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const resp = await axios.post(`${API_BASE}/api/responses/generate/${postId}`, {
        product_id: productId,
        style: defaultStyle
      }, { headers });
      onGenerated(resp.data);
    } catch (err) {

    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleGenerate}
      disabled={loading}
      className="w-full mt-4 flex items-center justify-center gap-2 px-4 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 text-white font-medium rounded-xl transition-all shadow-lg shadow-purple-900/20 active:scale-95"
    >
      {loading ? (
        <><Loader2 size={18} className="animate-spin" /> Generating with GPT-5.2...</>
      ) : (
        <><Sparkles size={18} /> Generate Suggested Response</>
      )}
    </button>
  );
};

const ResponseCard = ({ response, postUrl, onRegenerate, availableStyles, loading, error, postId, productId }) => {
  const [copied, setCopied] = useState(false);
  const [showStyles, setShowStyles] = useState(false);
  const [targetStyle, setTargetStyle] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [displayResponse, setDisplayResponse] = useState(response);
  const [editedText, setEditedText] = useState(response?.response_text || "");
  const [showHistory, setShowHistory] = useState(false);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    if (response) {
      setDisplayResponse(response);
      setEditedText(response.response_text);
    }
  }, [response]);

  useEffect(() => {
    if (!loading) {
      setTargetStyle(null);
    }
  }, [loading]);

  const handleCopy = async () => {
    if (loading || !displayResponse) return;
    await navigator.clipboard.writeText(editedText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
    // Explicitly log the copy action if no feedback given yet for THIS version
    if (!displayResponse.feedback) {
      axios.post(`${API_BASE}/api/responses/${displayResponse.id}/feedback`, { feedback: 'copied' });
    }
  };

  const handleFeedback = async (val) => {
    if (!displayResponse) return;

    // Optimistically update the active response and its reflected feedback in history if visible
    const updatedResp = { ...displayResponse, feedback: val };
    setDisplayResponse(updatedResp);
    if (history.length > 0) {
      setHistory(prev => prev.map(h => h.id === displayResponse.id ? updatedResp : h));
    }

    try {
      await axios.post(`${API_BASE}/api/responses/${displayResponse.id}/feedback`, { feedback: val });
    } catch (err) { }
  };

  const fetchHistory = async () => {
    if (!showHistory) {
      try {
        const res = await axios.get(`${API_BASE}/api/responses/history/${postId}?product_id=${productId}`);
        setHistory(res.data);
      } catch (err) { }
    }
    setShowHistory(!showHistory);
  };

  const handleStyleSelect = (style) => {
    setTargetStyle(style);
    onRegenerate(style);
    setShowStyles(false);
    setIsEditing(false);
  };

  return (
    <div className={`mt-6 bg-slate-900/80 border border-slate-700/50 rounded-2xl animate-in fade-in slide-in-from-bottom-4 duration-500 relative ${loading ? 'opacity-90' : ''}`}>
      {loading && (
        <div className="absolute inset-0 z-50 flex flex-col items-center justify-center bg-slate-900/90 backdrop-blur-md rounded-2xl">
          <div className="bg-purple-600/10 p-12 rounded-full absolute animate-ping duration-[3000ms]"></div>
          <Loader2 className="animate-spin text-purple-400 mb-4 z-10" size={40} />
          <div className="text-center z-10">
            <span className="block text-sm font-black text-white uppercase tracking-widest animate-pulse">
              Generating {targetStyle ? STYLE_LABELS[targetStyle].split(' ')[1] : 'Response'}...
            </span>
            <span className="block text-[10px] text-purple-400/60 mt-2 font-mono uppercase tracking-[0.2em] font-black">GPT-5.2 Deep Reasoning: active</span>
          </div>
        </div>
      )}

      {error && !loading && (
        <div className="bg-red-500/10 border-b border-red-500/20 px-4 py-2 flex items-center gap-2 text-red-400 text-[10px] font-bold uppercase tracking-wider animate-in slide-in-from-top-full">
          <AlertCircle size={14} /> {error}
        </div>
      )}

      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-700/50 bg-slate-800/40 rounded-t-2xl">
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 text-purple-400">
            <MessageSquare size={16} />
            <span className="text-sm font-bold uppercase tracking-wider">Suggested Response</span>
          </div>
          <button
            onClick={fetchHistory}
            className="text-[10px] text-slate-500 hover:text-indigo-400 font-bold uppercase tracking-tighter transition-colors bg-slate-900/40 px-2 py-0.5 rounded border border-slate-700/50 ml-2"
          >
            {showHistory ? "Close History" : "View History"}
          </button>
        </div>
        <div className="relative flex items-center gap-2">
          <button
            onClick={() => setIsEditing(!isEditing)}
            className={`px-3 py-1.5 text-xs font-bold rounded-lg border transition-all ${isEditing ? 'bg-indigo-600 border-indigo-500 text-white' : 'bg-slate-800 border-slate-700 text-slate-400 hover:bg-slate-700'}`}
          >
            {isEditing ? 'Save View' : 'Edit'}
          </button>
          <div className="relative">
            <button
              onClick={() => !loading && setShowStyles(!showStyles)}
              disabled={loading}
              className="flex items-center gap-2 px-3 py-1.5 text-xs font-bold bg-slate-800 hover:bg-slate-700 rounded-lg border border-slate-700 transition-colors disabled:opacity-50"
            >
              {STYLE_LABELS[displayResponse?.style || response.style]}
              <ChevronDown size={14} className={`transition-transform ${showStyles ? 'rotate-180' : ''}`} />
            </button>
            {showStyles && (
              <div className="absolute right-0 top-full mt-2 w-48 bg-slate-800 border border-slate-700 rounded-xl shadow-2xl z-[60] py-2 overflow-hidden ring-1 ring-white/5">
                {availableStyles.map(s => (
                  <button
                    key={s}
                    onClick={() => handleStyleSelect(s)}
                    className="w-full px-4 py-2 text-left text-xs font-medium hover:bg-purple-600/20 hover:text-purple-300 transition-colors"
                  >
                    {STYLE_LABELS[s]}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {showHistory && (
        <div className="bg-slate-950/60 border-b border-slate-700/50 p-4 max-h-48 overflow-y-auto space-y-2 animate-in slide-in-from-top-4">
          <p className="text-[10px] font-black text-slate-600 uppercase tracking-widest mb-3">Previous Generations</p>
          {history.length === 0 ? <p className="text-xs italic text-slate-600">No previous versions found.</p> :
            history.map((h, i) => (
              <div key={h.id} className={`p-3 rounded-lg border transition-all cursor-pointer ${h.id === displayResponse?.id ? 'bg-purple-600/10 border-purple-500/50' : 'bg-slate-900/40 border-slate-800 hover:border-slate-700'}`}
                onClick={() => {
                  setDisplayResponse(h);
                  setEditedText(h.response_text);
                  setIsEditing(false);
                }}
              >
                <div className="flex justify-between items-center mb-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold text-slate-400 capitalize">{h.style.replace('_', ' ')}</span>
                    {h.feedback === 'good' && <ThumbsUp size={10} className="text-emerald-500" />}
                    {h.feedback === 'bad' && <ThumbsDown size={10} className="text-red-500" />}
                  </div>
                  <span className="text-[10px] text-slate-600 font-mono">{new Date(h.created_at).toLocaleString()}</span>
                </div>
                <p className="text-xs text-slate-500 line-clamp-1 italic">"{h.response_text}"</p>
              </div>
            ))
          }
        </div>
      )}

      <div className="p-5">
        {isEditing ? (
          <textarea
            className="w-full bg-slate-950/80 border border-indigo-500/30 rounded-xl p-4 text-sm text-slate-200 leading-relaxed outline-none focus:ring-2 focus:ring-indigo-600 h-48 transition-all scrollbar-thin scrollbar-thumb-slate-800"
            value={editedText}
            onChange={(e) => setEditedText(e.target.value)}
            placeholder="Edit the suggested response..."
          />
        ) : (
          <div className="bg-slate-950/50 rounded-xl p-4 text-sm text-slate-300 leading-relaxed border border-white/5 whitespace-pre-wrap min-h-[100px] relative">
            {editedText}
            {displayResponse && editedText !== displayResponse.response_text && (
              <span className="absolute top-2 right-2 px-1.5 py-0.5 bg-indigo-600 text-[8px] font-black uppercase text-white rounded">Edited</span>
            )}
          </div>
        )}
        <div className="mt-3 flex items-center justify-between text-[10px] text-slate-500 font-mono">
          <div className="flex gap-4">
            <span>GPT-5.2 Reasoning: X-High</span>
            <span>{displayResponse?.tokens_used || response.tokens_used} tokens</span>
          </div>
          {(displayResponse?.created_at || response.created_at) && (
            <span>Generated {new Date(displayResponse?.created_at || response.created_at).toLocaleTimeString()}</span>
          )}
        </div>
      </div>

      <div className="flex items-center gap-2 px-4 py-3 bg-slate-800/40 border-t border-slate-700/50 rounded-b-2xl">
        <button
          onClick={handleCopy}
          disabled={loading}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white text-xs font-bold rounded-lg transition-all active:scale-95 disabled:bg-purple-800/50"
        >
          {copied ? <><Check size={14} /> Copied!</> : <><Copy size={14} /> Copy to Clipboard</>}
        </button>

        <div className="flex items-center gap-1 bg-slate-900/60 p-1 rounded-lg border border-slate-700/50">
          <button
            onClick={() => handleFeedback('good')}
            className={`p-1.5 rounded transition-all ${displayResponse?.feedback === 'good' ? 'bg-green-600 text-white shadow-lg shadow-green-900/20' : 'text-slate-500 hover:text-green-400 hover:bg-slate-800'}`}
            title="Good Response"
          >
            <ThumbsUp size={14} />
          </button>
          <button
            onClick={() => handleFeedback('bad')}
            className={`p-1.5 rounded transition-all ${displayResponse?.feedback === 'bad' ? 'bg-red-600 text-white shadow-lg shadow-red-900/20' : 'text-slate-500 hover:text-red-400 hover:bg-slate-800'}`}
            title="Poor Response"
          >
            <ThumbsDown size={14} />
          </button>
        </div>

        <button
          onClick={() => {
            setTargetStyle(displayResponse?.style || response.style);
            onRegenerate(displayResponse?.style || response.style);
            setIsEditing(false);
          }}
          disabled={loading}
          className="p-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg transition-colors disabled:opacity-50"
          title="Regenerate"
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
        </button>
        <a
          href={postUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="p-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg transition-colors"
          title="Open in Reddit"
        >
          <ExternalLink size={14} />
        </a>
      </div>
    </div>
  );
};

function MainApp() {
  // ALL hooks must be called at the top, before any conditional returns
  const [config, setConfig] = useState({ products: [], subreddits: [] });
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [activeFilter, setActiveFilter] = useState("all"); // all, priority, intensity, untriaged
  const [selectedSubs, setSelectedSubs] = useState([]);
  const [days, setDays] = useState(3);
  const [threads, setThreads] = useState([]);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [syncStatus, setSyncStatus] = useState({ is_running: false, current_step: "Idle", progress: 0 });
  const [expandedThread, setExpandedThread] = useState(null);
  const [sortBy, setSortBy] = useState("highest");
  const [history, setHistory] = useState([]);
  const [view, setView] = useState("dashboard");
  const [products, setProducts] = useState([]);
  const [editingProduct, setEditingProduct] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isChangelogOpen, setIsChangelogOpen] = useState(false);
  const [showOnboarding, setShowOnboarding] = useState(false);

  // Advanced Filters
  const [filterSubreddit, setFilterSubreddit] = useState("all");
  const [filterTag, setFilterTag] = useState("all");
  const [filterDateRange, setFilterDateRange] = useState("all"); // all, 1d, 7d, 30d

  const { isLoaded, isSignedIn, getToken } = useAuth();
  const { openSignUp, openSignIn } = useClerk();

  // Helper to get auth headers
  const getAuthHeaders = async () => {
    const token = await getToken();
    if (!token) {
      console.warn("No auth token available");
      return {};
    }
    return { Authorization: `Bearer ${token}` };
  };

  const fetchConfig = async () => {
    try {
      const headers = await getAuthHeaders();
      const res = await axios.get(`${API_BASE}/api/config`, { headers });
      setConfig(res.data);
      if (res.data.products?.length > 0 && !res.data.products.includes(selectedProduct)) {
        setSelectedProduct(res.data.products[0]);
      }
    } catch (err) {

    }
  };

  const fetchProducts = async () => {
    try {
      const headers = await getAuthHeaders();
      const res = await axios.get(`${API_BASE}/api/products`, { headers });
      setProducts(res.data);
    } catch (err) {

    }
  };

  const fetchHistory = async () => {
    try {
      const headers = await getAuthHeaders();
      const res = await axios.get(`${API_BASE}/api/sync/history`, { headers });
      setHistory(res.data);
    } catch (err) {

    }
  };

  const fetchThreads = async () => {
    setLoading(true);
    try {
      const headers = await getAuthHeaders();
      const res = await axios.get(`${API_BASE}/api/threads?product=${selectedProduct}`, { headers });
      setThreads(prev => {
        const regeneratingStates = prev.reduce((acc, t) => {
          if (t.isRegenerating) acc[t.id] = t;
          return acc;
        }, {});

        return res.data.map(newThread => {
          if (regeneratingStates[newThread.id]) {
            return {
              ...newThread,
              isRegenerating: true,
              generatedResponse: regeneratingStates[newThread.id].generatedResponse
            };
          }
          return { ...newThread, isRegenerating: false };
        });
      });
    } catch (err) {

    }
    setLoading(false);
  };

  // Effect: Check onboarding status
  useEffect(() => {
    if (!isLoaded || !isSignedIn) return;
    const checkOnboarding = async () => {
      try {
        const headers = await getAuthHeaders();
        const res = await axios.get(`${API_BASE}/api/settings/onboarding_discovery_completed`, { headers });
        if (!res.data.value || res.data.value === 'false') {
          setShowOnboarding(true);
        }
      } catch (err) {

      }
    };
    checkOnboarding();
  }, [isLoaded, isSignedIn]);

  // Effect: Fetch data when product changes
  useEffect(() => {
    if (!isLoaded || !isSignedIn) return;

    // Check if sync is already running (persists across page reloads)
    const checkSyncStatus = async () => {
      try {
        const headers = await getAuthHeaders();
        const res = await axios.get(`${API_BASE}/api/sync/status`, { headers });
        if (res.data.is_running) {
          setSyncing(true);
          setSyncStatus(res.data);
          // If already running, fetch history to sync the sidebar status too
          fetchHistory();
        }
      } catch (err) { }
    };
    checkSyncStatus();

    fetchConfig();
    fetchThreads();
    fetchHistory();
    fetchProducts();
  }, [selectedProduct, isLoaded, isSignedIn]);

  // Effect: Status Polling
  useEffect(() => {
    let interval;
    if (syncing) {
      // Immediate fetch on start/reload to avoid 5s delay
      const poll = async () => {
        try {
          const headers = await getAuthHeaders();
          // If headers is empty (token missing), skip this tick but don't stop syncing
          if (Object.keys(headers).length === 0) return;

          const res = await axios.get(`${API_BASE}/api/sync/status`, { headers });
          setSyncStatus(res.data);

          // Only stop if explicitly Success or Error, or if the backend says definitely not running
          // AND we haven't just had a transient error
          if (!res.data.is_running && (res.data.progress === 100 || res.data.error)) {
            setSyncing(false);
            fetchThreads();
            fetchHistory(); // Final refresh
            clearInterval(interval);
          }
        } catch (err) {
          // On network error, keep syncing state true to avoid unlocking button prematurely
          console.error("Polling error, continuing...", err);
        }
      };

      poll();
      interval = setInterval(poll, 10000); // Reduced from 5s to 10s for less server load
    }
    return () => clearInterval(interval);
  }, [syncing]);

  // Early return AFTER all hooks
  if (!isLoaded) {
    return (
      <div className="h-screen bg-slate-950 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <RefreshCw className="animate-spin text-indigo-500" size={32} />
          <p className="text-slate-500 font-mono text-xs uppercase tracking-widest">Initializing SonarPro Auth...</p>
        </div>
      </div>
    );
  }

  const discoverySteps = [
    { title: "Welcome to SonarPro", content: "We've analyzed Reddit to find the best sales opportunities for you. Let's show you around!" },
    { title: "Product Alignment", content: "The 'Fit %' represents how well a post aligns with your product goals based on AI analysis of pain points." },
    { title: "Intensity Matters", content: "High Intensity means the user is actively looking for a solution RIGHT NOW." },
    { title: "Social Selling", content: "Use the 'Suggested Response' to engage authentically. GPT-5.2 will help you sound like a genuine community member." }
  ];

  const handleOnboardingComplete = async () => {
    setShowOnboarding(false);
    try {
      const headers = await getAuthHeaders();
      await axios.post(`${API_BASE}/api/settings`, {
        key: 'onboarding_discovery_completed',
        value: 'true'
      }, { headers });
    } catch (err) {

    }
  };

  const handleSaveProduct = async (pData) => {
    try {
      const headers = await getAuthHeaders();
      const isNewProduct = !editingProduct;

      if (editingProduct) {
        await axios.put(`${API_BASE}/api/products/${editingProduct.id}`, pData, { headers });
      } else {
        await axios.post(`${API_BASE}/api/products`, pData, { headers });
      }

      setIsModalOpen(false);
      setEditingProduct(null);
      await fetchProducts();
      await fetchConfig();

      // Auto-sync for new products with subreddits
      if (isNewProduct && pData.target_subreddits?.length > 0) {
        const firstSub = pData.target_subreddits[0];
        setSelectedProduct(pData.id);
        setSelectedSubs([firstSub]);

        try {
          await axios.post(`${API_BASE}/api/sync`, null, {
            params: { subreddits: [firstSub], days: 1, product: pData.id },
            headers
          });

          // Show informative toast
          alert(`🔍 Analyzing r/${firstSub}...\n\nThis may take 2-3 minutes. You'll see the results appear in the Discovery Dashboard.\n\n💡 Tip: Use "Run Intelligence Sync" in the sidebar to analyze more subreddits or refresh data.`);
        } catch (syncErr) {
          console.warn("Auto-sync failed, user can trigger manually", syncErr);
        }
      }
    } catch (err) {
      alert("Failed to save product");
    }
  };

  const handleDeleteProduct = async (id) => {
    if (window.confirm("Delete this product and all its analysis?")) {
      try {
        const headers = await getAuthHeaders();
        await axios.delete(`${API_BASE}/api/products/${id}`, { headers });
        fetchProducts();
        fetchConfig();
        if (selectedProduct === id) setSelectedProduct(products[0]?.id || "");
      } catch (err) {

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
    if (sortBy === "newest") {
      return new Date(b.created_at) - new Date(a.created_at);
    }
    // Default to "highest" logic
    if (activeFilter === "intensity" || sortBy === "intensity") return b.community_score - a.community_score;
    if (activeFilter === "fit" || sortBy === "fit") return b.semantic_similarity - a.semantic_similarity;
    return b.relevance_score - a.relevance_score;
  });

  const filteredThreads = sortedThreads.filter(t => {
    // Existing stat filters
    if (activeFilter === "fit" && t.semantic_similarity <= 0.5) return false;
    if (activeFilter === "intensity" && t.community_score <= 3.0) return false;
    if (activeFilter === "score" && t.relevance_score <= 15.0) return false;
    if (activeFilter === "untriaged" && t.triage_status) return false;

    // Subreddit filter
    if (filterSubreddit !== "all" && t.source !== filterSubreddit) return false;

    // Tag filter (intent signals) - signals.intents is an ARRAY like ["complaint", "seeking_tool"]
    if (filterTag !== "all") {
      const signals = t.signals_json ? JSON.parse(t.signals_json) : {};
      const intents = signals.intents || [];
      if (!intents.includes(filterTag)) return false;
    }

    // Date range filter
    if (filterDateRange !== "all") {
      const postDate = new Date(t.created_at);
      const now = new Date();
      const diffDays = (now - postDate) / (1000 * 60 * 60 * 24);
      if (filterDateRange === "1d" && diffDays > 1) return false;
      if (filterDateRange === "7d" && diffDays > 7) return false;
      if (filterDateRange === "30d" && diffDays > 30) return false;
    }

    return true;
  });

  // Compute available subreddits and tags for filter dropdowns
  const availableSubreddits = [...new Set(threads.map(t => t.source))].sort();
  const availableTags = ["seeking_tool", "complaint", "comparison"];

  const productDefaultStyle = products.find(p => p.id === selectedProduct)?.default_response_style || "empathetic";

  const handleTriage = async (postId, status) => {
    try {
      const headers = await getAuthHeaders();
      const currentThread = threads.find(t => t.id === postId);
      const newStatus = currentThread.triage_status === status ? 'null' : status;

      await axios.post(`${API_BASE}/api/threads/${postId}/triage?status=${newStatus}&product_id=${selectedProduct}`, {}, { headers });

      setThreads(prev => prev.map(t =>
        t.id === postId ? { ...t, triage_status: newStatus === 'null' ? null : newStatus } : t
      ));
    } catch (err) {

      alert("Failed to save feedback.");
    }
  };

  const handleSync = async () => {
    if (selectedSubs.length === 0) {
      alert("Please select at least one subreddit.");
      return;
    }
    setSyncing(true);
    setSyncStatus({ is_running: true, current_step: "Starting...", progress: 0 });
    try {
      const headers = await getAuthHeaders();
      const subParams = selectedSubs.map(s => `subreddits=${s}`).join('&');
      const url = `${API_BASE}/api/sync?${subParams}&days=${days}&product=${selectedProduct}`;
      await axios.post(url, {}, { headers });
      fetchConfig();
    } catch (err) {
      alert("Sync failed: " + (err.response?.data?.error || err.message));
      setSyncing(false);
      setSyncStatus({ is_running: false, current_step: "Idle", progress: 0 });
    }
  };


  return (
    <>
      <SignedOut>
        <LandingPage onGetStarted={() => openSignUp()} onSignIn={() => openSignIn()} />
      </SignedOut>
      <SignedIn>
        <div className="h-screen bg-slate-950 text-slate-200 flex overflow-hidden">
          {/* Sidebar */}
          <aside className="w-80 bg-slate-900 border-r border-slate-800 flex flex-col shadow-xl">
            <div className="p-6 border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm z-10 hover:bg-slate-800/50 transition-colors group cursor-default">
              <SonarLogo size={32} />
            </div>

            <div className="flex-1 overflow-y-auto p-6 custom-scrollbar space-y-8">
              <div className="flex flex-col gap-2">
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
                  <div className="grid grid-cols-1 gap-2 max-h-40 overflow-y-auto p-1 custom-scrollbar">
                    {(() => {
                      // Get subreddits for selected product
                      const selectedProductData = products.find(p => p.id === selectedProduct);
                      let productSubs = selectedProductData?.target_subreddits || [];
                      if (typeof productSubs === 'string') {
                        try { productSubs = JSON.parse(productSubs); } catch { productSubs = []; }
                      }
                      return productSubs.length > 0 ? productSubs.map(sub => (
                        <label key={sub} className="flex items-center gap-3 cursor-pointer hover:text-white transition-colors">
                          <input
                            type="checkbox"
                            checked={selectedSubs.includes(sub)}
                            onChange={() => setSelectedSubs(prev => prev.includes(sub) ? prev.filter(s => s !== sub) : [...prev, sub])}
                            className="rounded border-slate-700 bg-slate-800 text-indigo-600 focus:ring-offset-slate-900"
                          />
                          <span className="text-sm">r/{sub}</span>
                        </label>
                      )) : (
                        <p className="text-sm text-slate-500 italic">No subreddits configured for this product. Edit the product to add subreddits.</p>
                      );
                    })()}
                  </div>
                </section>

                {/* 
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
                */}

                <div className="flex justify-between items-center mb-2">
                  <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 block">Scraping Range</label>
                  <span className="text-[10px] font-bold text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">{days} {days === "1" || days === 1 ? 'Day' : 'Days'}</span>
                </div>
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

                <section className="border-t border-slate-800 pt-6">
                  <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-4 block flex items-center gap-2">
                    <RefreshCw size={14} /> Run History
                  </label>
                  <div className="space-y-3 max-h-80 overflow-y-auto pr-2 custom-scrollbar">
                    {history.filter(run => run.status === 'Success' || run.status.startsWith('Error')).length === 0 ? (
                      <p className="text-[10px] text-slate-600 italic">No past runs recorded.</p>
                    ) : (
                      history.filter(run => run.status === 'Success' || run.status.startsWith('Error')).map(run => (
                        <div key={run.id} className="bg-slate-800/30 border border-slate-800 p-3 rounded-xl hover:border-slate-600 transition-all cursor-pointer group active:scale-95">
                          <div className="flex justify-between items-start mb-2">
                            <span className="text-[10px] font-black text-indigo-400 truncate uppercase w-2/3 tracking-tighter">{run.product}</span>
                            <span className="text-[9px] text-slate-500 font-mono">{new Date(run.timestamp).toLocaleDateString([], { month: 'short', day: 'numeric' })}</span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-[9px] text-slate-400 truncate w-1/2 font-medium">r/{run.subreddits}</span>
                            <span className={`text-[8px] px-2 py-0.5 rounded-full font-black uppercase tracking-widest flex items-center gap-1.5 ${run.status === 'Success' ? 'bg-emerald-500/10 text-emerald-500' :
                              run.status.startsWith('Error') ? 'bg-red-500/10 text-red-500' : 'bg-indigo-500/10 text-indigo-400'
                              }`}>
                              {run.status !== 'Success' && !run.status.startsWith('Error') && <RefreshCw size={8} className="animate-spin" />}
                              {run.status.split(':')[0]}
                            </span>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </section>
              </div> {/* Closes the "space-y-6" div */}
            </div> {/* Closes the "flex-1 overflow-y-auto" div */}

            <div className="p-6 border-t border-slate-800 bg-slate-900/50">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3 text-slate-500 hover:text-slate-300 transition-colors cursor-pointer">
                  <Settings size={18} />
                  <span className="text-sm">Settings</span>
                </div>
                <UserButton afterSignOutUrl="/" />
              </div>
              <div className="flex flex-col items-center gap-1">
                <span className="text-[10px] text-slate-600 font-mono">SonarPro v0.0.4</span>
                <button
                  onClick={() => setIsChangelogOpen(true)}
                  className="text-[9px] text-indigo-400/60 hover:text-indigo-400 transition-colors uppercase tracking-widest font-bold"
                >
                  [ What's New ]
                </button>
              </div>
            </div>
          </aside>

          {/* Changelog Modal */}
          {isChangelogOpen && (
            <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
              <div className="bg-slate-900 border border-slate-700 w-full max-w-xl rounded-2xl overflow-hidden shadow-2xl animate-in fade-in zoom-in duration-200">
                <div className="p-6 border-b border-slate-800 flex justify-between items-center bg-slate-800/50">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-indigo-500/20 rounded-lg">
                      <Zap size={20} className="text-indigo-400" />
                    </div>
                    <h2 className="text-xl font-bold text-white">Changelog</h2>
                  </div>
                  <button onClick={() => setIsChangelogOpen(false)} className="text-slate-400 hover:text-white transition-colors">
                    <X size={24} />
                  </button>
                </div>
                <div className="p-8 max-h-[60vh] overflow-y-auto custom-scrollbar space-y-8">
                  <section>
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-bold text-white">v0.0.4</h3>
                      <span className="text-xs text-slate-500 font-mono italic">2026-01-16</span>
                    </div>
                    <div className="space-y-6">
                      <div className="group">
                        <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-widest mb-2 flex items-center gap-2">
                          🛡️ AI Response Guardrails
                        </h4>
                        <ul className="text-sm text-slate-300 space-y-2 list-disc pl-4 marker:text-indigo-500">
                          <li><strong className="text-slate-200">Product-Based Responses</strong>: AI now uses your actual product description.</li>
                          <li><strong className="text-slate-200">No Invented Features</strong>: AI only mentions capabilities from your registration.</li>
                        </ul>
                      </div>
                      <div className="group">
                        <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-widest mb-2 flex items-center gap-2">
                          🚀 Improved Onboarding
                        </h4>
                        <ul className="text-sm text-slate-300 space-y-2 list-disc pl-4 marker:text-emerald-500">
                          <li><strong className="text-slate-200">Auto-Sync</strong>: New products automatically trigger first subreddit analysis.</li>
                          <li><strong className="text-slate-200">Clear Instructions</strong>: Toast explains wait time and next steps.</li>
                        </ul>
                      </div>
                      <div className="group">
                        <h4 className="text-xs font-bold text-cyan-400 uppercase tracking-widest mb-2 flex items-center gap-2">
                          📂 Product-Specific Subreddits
                        </h4>
                        <ul className="text-sm text-slate-300 space-y-2 list-disc pl-4 marker:text-cyan-500">
                          <li>Sidebar shows only the selected product's subreddits.</li>
                          <li>Switching products updates the subreddit list.</li>
                        </ul>
                      </div>
                    </div>
                  </section>

                  <section className="pt-6 border-t border-slate-800">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-bold text-slate-400">v0.0.3</h3>
                      <span className="text-xs text-slate-600 font-mono">2026-01-16</span>
                    </div>
                    <ul className="text-sm text-slate-500 space-y-2 list-disc pl-4 border-l-2 border-slate-800">
                      <li>AI Ad & Spam Detection with intent analysis.</li>
                      <li>Pipeline robustness with per-post failsafes.</li>
                      <li>Warning badges for possible marketing content.</li>
                    </ul>
                  </section>

                  <section className="pt-6 border-t border-slate-800">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-bold text-slate-400">v0.0.2</h3>
                      <span className="text-xs text-slate-600 font-mono">2026-01-15</span>
                    </div>
                    <ul className="text-sm text-slate-500 space-y-2 list-disc pl-4 border-l-2 border-slate-800">
                      <li>Interactive Onboarding for new users.</li>
                      <li>Smart Product Setup with URL auto-extraction.</li>
                      <li>Celery + Redis async background processing.</li>
                    </ul>
                  </section>
                </div>
                <div className="p-4 bg-slate-950/50 border-t border-slate-800 text-center">
                  <button
                    onClick={() => setIsChangelogOpen(false)}
                    className="px-6 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-all text-sm font-bold"
                  >
                    Got it!
                  </button>
                </div>
              </div>
            </div>
          )}

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
                  </div>
                </header>

                {/* Show Empty State when no threads */}
                {!loading && threads.length === 0 ? (
                  <EmptyDashboard
                    hasProducts={products.length > 0}
                    onCreateProduct={openCreate}
                    onStartSync={() => {
                      // Scroll to sidebar sync section
                      document.querySelector('[data-sync-button]')?.click();
                    }}
                  />
                ) : (
                  <>
                    {/* Stats Grid */}
                    <div className="grid grid-cols-5 gap-4 mb-12">
                      <Tooltip text="Measures the depth and frequency of problem discussion. Click to filter hot topics.">
                        <div
                          onClick={() => {
                            const newVal = activeFilter === "intensity" ? "all" : "intensity";
                            setActiveFilter(newVal);
                            setSortBy("highest");
                          }}
                          className={`p-5 rounded-2xl border transition-all cursor-pointer flex items-center justify-between shadow-sm ${activeFilter === "intensity" ? "bg-indigo-600 border-indigo-400 shadow-indigo-500/20" : "bg-slate-900 border-slate-800 hover:border-indigo-500/30"
                            }`}
                        >
                          <div>
                            <p className={`text-[10px] uppercase tracking-widest mb-1 flex items-center gap-1 ${activeFilter === "intensity" ? "text-indigo-100" : "text-slate-500"}`}>
                              High Intensity <HelpCircle size={10} />
                            </p>
                            <h3 className={`text-2xl font-bold ${activeFilter === "intensity" ? "text-white" : "text-orange-400"}`}>
                              {threads.filter(t => t.community_score > 3.0).length}
                            </h3>
                          </div>
                          <BarChart3 size={24} className={activeFilter === "intensity" ? "text-white/40" : "text-slate-700"} />
                        </div>
                      </Tooltip>

                      <Tooltip text="Number of posts that directly match your product signals. Click to filter.">
                        <div
                          onClick={() => {
                            const newVal = activeFilter === "fit" ? "all" : "fit";
                            setActiveFilter(newVal);
                            setSortBy("highest");
                          }}
                          className={`p-5 rounded-2xl border transition-all cursor-pointer flex items-center justify-between shadow-sm ${activeFilter === "fit" ? "bg-indigo-600 border-indigo-400 shadow-indigo-500/20" : "bg-slate-900 border-slate-800 hover:border-indigo-500/30"
                            }`}
                        >
                          <div>
                            <p className={`text-[10px] uppercase tracking-widest mb-1 flex items-center gap-1 ${activeFilter === "fit" ? "text-indigo-100" : "text-slate-500"}`}>
                              High Fit Leads <HelpCircle size={10} />
                            </p>
                            <h3 className={`text-2xl font-bold ${activeFilter === "fit" ? "text-white" : "text-emerald-400"}`}>
                              {threads.filter(t => t.semantic_similarity > 0.5).length}
                            </h3>
                          </div>
                          <CheckCircle2 size={24} className={activeFilter === "fit" ? "text-white/40" : "text-slate-700"} />
                        </div>
                      </Tooltip>

                      <Tooltip text="Highly relevant leads based on combined score. Click to filter.">
                        <div
                          onClick={() => {
                            const newVal = activeFilter === "score" ? "all" : "score";
                            setActiveFilter(newVal);
                            setSortBy("highest");
                          }}
                          className={`p-5 rounded-2xl border transition-all cursor-pointer flex items-center justify-between shadow-sm ${activeFilter === "score" ? "bg-indigo-600 border-indigo-400 shadow-indigo-500/20" : "bg-slate-900 border-slate-800 hover:border-indigo-500/30"
                            }`}
                        >
                          <div>
                            <p className={`text-[10px] uppercase tracking-widest mb-1 flex items-center gap-1 ${activeFilter === "score" ? "text-indigo-100" : "text-slate-500"}`}>
                              High Score <HelpCircle size={10} />
                            </p>
                            <h3 className={`text-2xl font-bold ${activeFilter === "score" ? "text-white" : "text-indigo-400"}`}>
                              {threads.filter(t => t.relevance_score > 15.0).length}
                            </h3>
                          </div>
                          <Zap size={24} className={activeFilter === "score" ? "text-white/40" : "text-slate-700"} />
                        </div>
                      </Tooltip>

                      <Tooltip text="Maximum problem intensity detected in the current set.">
                        <div className="bg-slate-900 p-5 rounded-2xl border border-slate-800 flex items-center justify-between shadow-sm">
                          <div>
                            <p className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">Max Intensity</p>
                            <h3 className="text-2xl font-bold text-white">
                              {threads.length > 0 ? Math.max(...threads.map(t => t.community_score)).toFixed(1) : "0.0"}
                            </h3>
                          </div>
                          <TrendingUp size={24} className="text-slate-700" />
                        </div>
                      </Tooltip>

                      <Tooltip text="Average product alignment quality across pipeline.">
                        <div className="bg-slate-900 p-5 rounded-2xl border border-slate-800 flex items-center justify-between shadow-sm">
                          <div>
                            <p className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">Avg Fit</p>
                            <h3 className="text-2xl font-bold text-white">
                              {threads.length > 0 ? Math.round((threads.reduce((acc, t) => acc + t.semantic_similarity, 0) / threads.length) * 100) : 0}%
                            </h3>
                          </div>
                          <Radar size={24} className="text-slate-700" />
                        </div>
                      </Tooltip>
                    </div>

                    {/* Threads List */}
                    <div className="space-y-4">
                      {/* Filter Bar */}
                      <div className="flex flex-wrap items-center gap-3 mb-6 p-4 bg-slate-900/50 rounded-xl border border-slate-800">
                        {/* Subreddit Filter */}
                        <div className="flex items-center gap-2">
                          <label className="text-[10px] text-slate-500 uppercase tracking-widest">Subreddit</label>
                          <select
                            value={filterSubreddit}
                            onChange={(e) => setFilterSubreddit(e.target.value)}
                            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none"
                          >
                            <option value="all">All</option>
                            {availableSubreddits.map(sub => (
                              <option key={sub} value={sub}>r/{sub}</option>
                            ))}
                          </select>
                        </div>

                        {/* Tag Filter */}
                        <div className="flex items-center gap-2">
                          <label className="text-[10px] text-slate-500 uppercase tracking-widest">Tag</label>
                          <select
                            value={filterTag}
                            onChange={(e) => setFilterTag(e.target.value)}
                            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none"
                          >
                            <option value="all">All</option>
                            {availableTags.map(tag => (
                              <option key={tag} value={tag}>{tag.replace("_", " ").toUpperCase()}</option>
                            ))}
                          </select>
                        </div>

                        {/* Date Range Filter */}
                        <div className="flex items-center gap-2">
                          <label className="text-[10px] text-slate-500 uppercase tracking-widest">Date</label>
                          <select
                            value={filterDateRange}
                            onChange={(e) => setFilterDateRange(e.target.value)}
                            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none"
                          >
                            <option value="all">All Time</option>
                            <option value="1d">Last 24h</option>
                            <option value="7d">Last 7 Days</option>
                            <option value="30d">Last 30 Days</option>
                          </select>
                        </div>

                        {/* Spacer */}
                        <div className="flex-1" />

                        {/* Clear Filters Button */}
                        {(filterSubreddit !== "all" || filterTag !== "all" || filterDateRange !== "all" || activeFilter !== "all") && (
                          <button
                            onClick={() => {
                              setFilterSubreddit("all");
                              setFilterTag("all");
                              setFilterDateRange("all");
                              setActiveFilter("all");
                            }}
                            className="px-3 py-1.5 text-xs text-red-400 hover:text-red-300 font-bold transition-colors"
                          >
                            Clear Filters
                          </button>
                        )}

                        {/* Sort Buttons */}
                        <div className="flex bg-slate-800 p-1 rounded-lg border border-slate-700">
                          <button
                            onClick={() => setSortBy("highest")}
                            className={`px-3 py-1 rounded-md text-xs font-bold transition-all ${sortBy === "highest" ? "bg-indigo-600 text-white" : "text-slate-500 hover:text-slate-300"}`}
                          >
                            Highest
                          </button>
                          <button
                            onClick={() => setSortBy("newest")}
                            className={`px-3 py-1 rounded-md text-xs font-bold transition-all ${sortBy === "newest" ? "bg-indigo-600 text-white" : "text-slate-500 hover:text-slate-300"}`}
                          >
                            Newest
                          </button>
                        </div>

                        {/* Results Count */}
                        <span className="text-xs text-slate-500">
                          {filteredThreads.length} of {threads.length}
                        </span>
                      </div>

                      {loading ? (
                        <div className="h-64 flex items-center justify-center text-slate-500">Loading intelligence...</div>
                      ) : filteredThreads.length === 0 ? (
                        <div className="h-64 flex flex-col items-center justify-center text-slate-500 bg-slate-900/50 rounded-2xl border border-dashed border-slate-800">
                          <Search className="mb-4 opacity-20" size={48} />
                          <p className="text-lg font-medium">No results match this filter</p>
                          <button
                            onClick={() => {
                              setFilterSubreddit("all");
                              setFilterTag("all");
                              setFilterDateRange("all");
                              setActiveFilter("all");
                            }}
                            className="mt-4 text-indigo-400 hover:text-indigo-300 font-bold"
                          >
                            Clear all filters
                          </button>
                        </div>
                      ) : (
                        filteredThreads.map((thread) => {
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
                                    {/* Intent Tags */}
                                    {signals && signals.intents && signals.intents.length > 0 && (
                                      <>
                                        <span className="text-[10px] text-slate-500">●</span>
                                        {signals.intents.map(intent => (
                                          <span key={intent} className="px-2 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-[9px] font-bold text-cyan-400 uppercase">
                                            {intent.replace("_", " ")}
                                          </span>
                                        ))}
                                      </>
                                    )}
                                    {/* Product-specific intents */}
                                    {signals && signals.product_matches && signals.product_matches[selectedProduct?.toLowerCase?.()] && signals.product_matches[selectedProduct.toLowerCase()].intents?.length > 0 && (
                                      signals.product_matches[selectedProduct.toLowerCase()].intents.map(p_intent => (
                                        <span key={p_intent} className="px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-[9px] font-bold text-emerald-400 uppercase">
                                          {p_intent}
                                        </span>
                                      ))
                                    )}
                                    {/* Product-specific pain points */}
                                    {signals && signals.product_matches && signals.product_matches[selectedProduct?.toLowerCase?.()] && signals.product_matches[selectedProduct.toLowerCase()].pain_points?.length > 0 && (
                                      signals.product_matches[selectedProduct.toLowerCase()].pain_points.map(p_point => (
                                        <span key={p_point} className="px-2 py-0.5 rounded-full bg-orange-500/10 border border-orange-500/20 text-[9px] font-bold text-orange-400 uppercase">
                                          {p_point}
                                        </span>
                                      ))
                                    )}
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

                                    {thread.is_stale === 1 && (
                                      <div
                                        className="flex items-center gap-1 px-2 py-1 bg-amber-500/10 border border-amber-500/20 rounded-lg animate-pulse"
                                        title={`Metrics changed significantly since last review (Previous Score: ${thread.triage_relevance_snapshot?.toFixed(1)})`}
                                      >
                                        <AlertTriangle size={12} className="text-amber-500" />
                                        <span className="text-[9px] font-black text-amber-500 uppercase tracking-tighter">Review Needed</span>
                                      </div>
                                    )}
                                    {/* Spam/AD Warning Badge */}
                                    {(() => {
                                      try {
                                        const ai = thread.ai_analysis ? JSON.parse(thread.ai_analysis) : null;
                                        if (ai && ai.is_spam_or_ad) {
                                          return (
                                            <div
                                              className="flex items-center gap-1 px-2 py-1 bg-red-500/10 border border-red-500/20 rounded-lg"
                                              title={ai.spam_indicators?.join(', ') || 'Suspected promotional or AI-generated content'}
                                            >
                                              <AlertTriangle size={12} className="text-red-400" />
                                              <span className="text-[9px] font-black text-red-400 uppercase tracking-tighter">Possible AD</span>
                                            </div>
                                          );
                                        }
                                        return null;
                                      } catch { return null; }
                                    })()}
                                    <div className="flex items-center gap-1.5 p-1 bg-slate-900/80 border border-slate-700/50 rounded-lg ml-2">
                                      <button
                                        onClick={(e) => { e.stopPropagation(); handleTriage(thread.id, 'agree'); }}
                                        className={`p-1.5 rounded-md transition-all ${thread.triage_status === 'agree' ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/20' : 'text-slate-500 hover:bg-slate-800 hover:text-emerald-400'}`}
                                        title="Agree with this lead"
                                      >
                                        <ThumbsUp size={14} />
                                      </button>
                                      <button
                                        onClick={(e) => { e.stopPropagation(); handleTriage(thread.id, 'disagree'); }}
                                        className={`p-1.5 rounded-md transition-all ${thread.triage_status === 'disagree' ? 'bg-red-500 text-white shadow-lg shadow-red-500/20' : 'text-slate-500 hover:bg-slate-800 hover:text-red-400'}`}
                                        title="Disagree with this lead"
                                      >
                                        <ThumbsDown size={14} />
                                      </button>
                                    </div>
                                  </div>
                                </div>
                              </div>

                              {isExpanded && (
                                <div className="px-6 pb-6 pt-0 animate-in fade-in slide-in-from-top-2 duration-300">
                                  <div className="border-t border-slate-800 pt-6 space-y-6">

                                    {/* Analysis Section */}
                                    <div className="grid grid-cols-2 gap-8">
                                      <div className="space-y-3">
                                        <h5 className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                                          <FileText size={14} /> Full Thread Content
                                        </h5>
                                        <div className="text-sm text-slate-300 bg-slate-800/50 p-4 rounded-xl border border-slate-800 leading-relaxed max-h-64 overflow-y-auto custom-scrollbar">
                                          {thread.body}
                                          <div className="mt-4 pt-4 border-t border-slate-800">
                                            <a href={thread.url} target="_blank" rel="noreferrer" className="text-indigo-400 hover:text-indigo-300 font-bold flex items-center gap-1">
                                              Open Original Post <ExternalLink size={14} />
                                            </a>
                                          </div>
                                        </div>

                                        <h5 className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2 mt-8">
                                          <Sparkles size={14} className="text-purple-500" /> Profile Intelligence
                                        </h5>
                                        {thread.generatedResponse ? (
                                          <ResponseCard
                                            response={thread.generatedResponse}
                                            postUrl={thread.url}
                                            postId={thread.id}
                                            productId={selectedProduct}
                                            loading={thread.isRegenerating}
                                            error={thread.genError}
                                            availableStyles={['empathetic', 'helpful_expert', 'casual', 'technical', 'brief', 'product_referral']}
                                            onRegenerate={(style) => {
                                              const handleGen = async () => {
                                                setThreads(prev => prev.map(t =>
                                                  t.id === thread.id ? { ...t, isRegenerating: true, genError: null } : t
                                                ));

                                                try {
                                                  const headers = await getAuthHeaders();
                                                  const resp = await axios.post(`${API_BASE}/api/responses/generate/${thread.id}`, {
                                                    product_id: selectedProduct,
                                                    style: style
                                                  }, { headers });
                                                  setThreads(prev => prev.map(t =>
                                                    t.id === thread.id ? { ...t, generatedResponse: resp.data, isRegenerating: false, genError: null } : t
                                                  ));
                                                } catch (err) {
                                                  setThreads(prev => prev.map(t =>
                                                    t.id === thread.id ? { ...t, isRegenerating: false, genError: "Failed to generate. Try again." } : t
                                                  ));
                                                }
                                              };
                                              handleGen();
                                            }}
                                          />
                                        ) : (
                                          <GenerateResponseButton
                                            postId={thread.id}
                                            productId={selectedProduct}
                                            defaultStyle={productDefaultStyle}
                                            onGenerated={(res) => {
                                              setThreads(prev => prev.map(t =>
                                                t.id === thread.id ? { ...t, generatedResponse: res, isRegenerating: false, genError: null } : t
                                              ));
                                            }}
                                          />
                                        )}
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
                                                      <div className="flex items-center gap-2 mb-3">
                                                        <div className="p-1 rounded bg-indigo-500/10 border border-indigo-500/20">
                                                          <User size={10} className="text-indigo-400" />
                                                        </div>
                                                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">u/{ai.pain_author || thread.author}</span>
                                                        {ai.is_from_comment ? (
                                                          <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-slate-800 text-slate-500 border border-slate-700 font-medium">Commenter</span>
                                                        ) : (
                                                          <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-medium">Author</span>
                                                        )}
                                                      </div>
                                                      <p className="font-bold text-indigo-300 text-lg mb-1 leading-snug">{ai.pain_point_summary}</p>
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
                                                      {/* Spam Warning in AI Section */}
                                                      {ai.is_spam_or_ad && (
                                                        <div className="px-2 py-1 rounded-md bg-red-500/20 border border-red-500/30">
                                                          <span className="text-[10px] font-black text-red-400 uppercase tracking-tighter flex items-center gap-1">
                                                            <AlertTriangle size={10} /> Possible AD
                                                          </span>
                                                        </div>
                                                      )}
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
                                                    {/* Spam Indicators Warning */}
                                                    {ai.is_spam_or_ad && ai.spam_indicators && ai.spam_indicators.length > 0 && (
                                                      <div className="bg-red-500/10 p-3 rounded-xl border border-red-500/20 mt-2">
                                                        <p className="text-[10px] font-bold text-red-400 uppercase mb-2 flex items-center gap-1">
                                                          <AlertTriangle size={12} /> Warning: Possible Promotional Content
                                                        </p>
                                                        <ul className="text-[11px] text-red-300/80 space-y-1">
                                                          {ai.spam_indicators.map((indicator, idx) => (
                                                            <li key={idx} className="flex items-start gap-1.5">
                                                              <span className="text-red-400 mt-0.5">•</span>
                                                              <span>{indicator}</span>
                                                            </li>
                                                          ))}
                                                        </ul>
                                                      </div>
                                                    )}
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
                )}
              </>
            ) : (
              <ProductManagement
                products={products}
                onEdit={openEdit}
                onDelete={handleDeleteProduct}
                onCreate={openCreate}
              />
            )}
            {showOnboarding && (
              <InteractiveOnboarding
                onComplete={handleOnboardingComplete}
                onOpenProductModal={() => {
                  setShowOnboarding(false);
                  openCreate();
                }}
                hasProducts={products.length > 0}
                onStartSync={() => {
                  setShowOnboarding(false);
                  handleOnboardingComplete();
                }}
              />
            )}
          </main>
        </div >
      </SignedIn >
    </>
  );
}

function App() {
  return <MainApp />;
}

export default App;
