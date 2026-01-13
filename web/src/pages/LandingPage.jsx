import React, { useState } from 'react';
import {
    Activity,
    Zap,
    MessageSquare,
    Target,
    ArrowRight,
    CheckCircle2,
    ChevronRight,
    ShieldCheck,
    ZapIcon,
    Search,
    Users
} from 'lucide-react';
import SonarLogo from '../components/SonarLogo';

const LandingPage = ({ onGetStarted, onSignIn }) => {
    const [activeTab, setActiveTab] = useState('detect');
    const [isAnnual, setIsAnnual] = useState(false);

    const pillars = {
        detect: {
            title: "DETECT",
            subtitle: "Semantic Intelligence Engine",
            description: "SonarPro doesn't just search keywords—it understands meaning. Our AI matches your product to discussions where people describe problems you solve, even if they don't use your words.",
            bullets: ["Monitors unlimited subreddits 24/7", "Detects pain signals, not just mentions", "Surfaces leads competitors miss"],
            icon: <Target className="text-indigo-400" size={24} />
        },
        analyze: {
            title: "ANALYZE",
            subtitle: "AI Lead Qualification",
            description: "Every lead gets a structured breakdown: Who's hurting, how much, and why your product fits. No more manual digging.",
            bullets: ["Pain point extraction with exact quotes", "Urgency scoring (High/Medium/Low)", "Product-market fit score (1-10)"],
            icon: <Zap className="text-indigo-400" size={24} />
        },
        respond: {
            title: "RESPOND",
            subtitle: "Profile Intelligence Engine",
            description: "Generate responses that feel human, not salesy. Our AI crafts messages that reference their specific situation and open conversation naturally.",
            bullets: ["5 tone presets (Empathetic, Expert, Casual, etc.)", "References their exact words", "Never mentions product directly"],
            icon: <MessageSquare className="text-indigo-400" size={24} />
        }
    };

    return (
        <div className="min-h-screen bg-slate-950 text-slate-200 selection:bg-indigo-500/30">
            {/* Navigation */}
            <nav className="fixed top-0 w-full z-50 bg-slate-950/80 backdrop-blur-md border-b border-white/5">
                <div className="max-w-[1440px] mx-auto px-6 h-20 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <SonarLogo size={40} />
                    </div>
                    <div className="hidden md:flex items-center gap-8">
                        <a href="#features" className="text-sm font-medium text-slate-400 hover:text-white transition-colors">Features</a>
                        <a href="#pricing" className="text-sm font-medium text-slate-400 hover:text-white transition-colors">Pricing</a>
                        <button
                            onClick={onSignIn || onGetStarted}
                            className="bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-2 rounded-lg text-sm font-bold transition-all"
                        >
                            Sign In
                        </button>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="relative pt-32 pb-20 px-6 overflow-hidden">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[500px] bg-indigo-500/10 blur-[120px] rounded-full opacity-30 pointer-events-none"></div>
                <div className="max-w-7xl mx-auto text-center relative z-10">
                    <div className="inline-flex items-center gap-2 bg-indigo-500/10 border border-indigo-500/20 px-4 py-1.5 rounded-full mb-8">
                        <span className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-pulse"></span>
                        <span className="text-[10px] font-bold uppercase tracking-widest text-indigo-400">Discover leads. Validate ideas. Save hours.</span>
                    </div>
                    <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 font-display tracking-tight leading-[1.1]">
                        Your ideal customers are online right now <br />
                        <span className="text-indigo-500">asking for exactly what you sell.</span>
                    </h1>
                    <p className="text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed font-body">
                        SonarPro detects high-intent discussions on <span className="text-white border-b border-indigo-500/50">Reddit</span>, <span className="text-slate-500">Quora</span>, and <span className="text-slate-500">Forums</span>. <br />
                        Start with Reddit. More platforms coming soon.
                    </p>
                    <div className="flex flex-col md:flex-row items-center justify-center gap-4">
                        <button
                            onClick={onGetStarted}
                            className="group bg-indigo-600 hover:bg-indigo-500 text-white px-8 py-4 rounded-xl font-bold text-lg shadow-xl shadow-indigo-600/20 transition-all flex items-center gap-2"
                        >
                            Get Started Now
                            <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                        </button>
                        <button
                            onClick={() => document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })}
                            className="px-8 py-4 rounded-xl font-bold text-lg text-slate-400 hover:text-white transition-all flex items-center gap-2"
                        >
                            Watch Demo
                        </button>
                    </div>

                </div>
            </section>

            {/* How It Works Section */}
            <section id="how-it-works" className="py-24 px-6 border-b border-white/5">
                <div className="max-w-7xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl font-bold text-white mb-4 font-display">How it works</h2>
                        <p className="text-slate-400 text-lg">From zero to high-intent leads in 3 steps.</p>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-12 mb-20">
                        {[
                            { step: "01", title: "Configure Your Radar", desc: "Define your product, keywords, and target subreddits in under 5 minutes.", icon: <Search size={24} className="text-indigo-400" /> },
                            { step: "02", title: "Run Intelligence Sync", desc: "One click to scan thousands of discussions with neural semantic matching.", icon: <Activity size={24} className="text-indigo-400" /> },
                            { step: "03", title: "Engage & Close", desc: "Review AI-qualified insights and generate authentic, tone-matched responses.", icon: <Zap size={24} className="text-indigo-400" /> }
                        ].map((item, i) => (
                            <div key={i} className="relative group">
                                <div className="text-[120px] font-black text-indigo-500/5 absolute -top-16 -left-8 z-0 group-hover:text-indigo-500/10 transition-colors pointer-events-none">
                                    {item.step}
                                </div>
                                <div className="relative z-10">
                                    <div className="w-12 h-12 rounded-xl bg-slate-900 border border-white/5 flex items-center justify-center mb-6 shadow-inner">
                                        {item.icon}
                                    </div>
                                    <h4 className="text-xl font-bold text-white mb-3 font-display">{item.title}</h4>
                                    <p className="text-slate-400 text-sm leading-relaxed">{item.desc}</p>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Storylane Container */}
                    <div className="aspect-video w-full max-w-5xl mx-auto bg-slate-900/50 rounded-2xl border border-white/10 flex flex-col items-center justify-center relative overflow-hidden group">
                        <div className="absolute inset-0 bg-indigo-500/5 blur-3xl opacity-50"></div>
                        <div className="relative z-10 text-center px-6">
                            <div className="w-20 h-20 bg-indigo-600/20 rounded-full flex items-center justify-center mb-6 mx-auto border border-indigo-500/30 group-hover:scale-110 transition-transform duration-500">
                                <Zap size={40} className="text-indigo-400" />
                            </div>
                            <h3 className="text-2xl font-bold text-white mb-2 font-display">See SonarPro in Action</h3>
                            <p className="text-slate-400 mb-8 max-w-md mx-auto">Watch how we find a high-intent marketing lead and generate a response in under 60 seconds.</p>
                            <div className="inline-flex items-center gap-2 bg-indigo-500/20 border border-indigo-500/50 px-6 py-3 rounded-xl text-white font-bold cursor-pointer hover:bg-indigo-500/30 transition-all">
                                <Activity size={16} />
                                [ Storylane Demo Placeholder ]
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Comparison Section */}
            <section className="py-24 px-6 border-y border-white/5 bg-slate-900/10">
                <div className="max-w-4xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl font-bold text-white mb-4 font-display text-indigo-100 italic">"GummySearch shut down. We're just getting started."</h2>
                        <h3 className="text-xl text-slate-400">Be among the first to try SonarPro for free.</h3>
                    </div>

                    <div className="overflow-x-auto rounded-2xl border border-white/5 bg-slate-900/40 backdrop-blur-sm">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="border-b border-white/10">
                                    <th className="py-6 px-8 text-xs font-black text-slate-500 uppercase tracking-[0.2em]">Strategy</th>
                                    <th className="py-6 px-8 text-xs font-black text-slate-500 uppercase tracking-[0.2em] text-center">Manual Search</th>
                                    <th className="py-6 px-8 text-xs font-black text-indigo-400 uppercase tracking-[0.2em] text-center">SonarPro AI</th>
                                </tr>
                            </thead>
                            <tbody className="text-sm">
                                {[
                                    { label: "Lead Discovery Speed", manual: "5-10 hours / week", pro: "3 minutes / day" },
                                    { label: "Content Analysis", manual: "Human reading", pro: "Neural Semantic Matching" },
                                    { label: "Engagement Quality", manual: "Hit or Miss", pro: "Tone-Matched Precision" },
                                    { label: "Consistency", manual: "Manual & Tiring", pro: "24/7 Automated Radar" }
                                ].map((row, i) => (
                                    <tr key={i} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                                        <td className="py-5 px-8 font-medium text-slate-300">{row.label}</td>
                                        <td className="py-5 px-8 text-center text-slate-500 italic">{row.manual}</td>
                                        <td className="py-5 px-8 text-center text-indigo-400 font-bold">{row.pro}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </section>

            {/* Pillars Section */}
            <section id="features" className="py-24 px-6 bg-slate-950/50">
                <div className="max-w-7xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl font-bold text-white mb-4 font-display">Three engines. One mission.</h2>
                        <p className="text-slate-400 text-lg">Find customers before they find alternatives.</p>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {Object.entries(pillars).map(([key, pillar]) => (
                            <div
                                key={key}
                                onMouseEnter={() => setActiveTab(key)}
                                className={`p-8 rounded-2xl border transition-all cursor-default ${activeTab === key
                                    ? 'bg-indigo-600/5 border-indigo-500/30 shadow-lg shadow-indigo-500/5'
                                    : 'bg-slate-900/30 border-white/5 hover:border-white/10'
                                    }`}
                            >
                                <div className="w-12 h-12 rounded-xl bg-indigo-500/10 flex items-center justify-center mb-6">
                                    {pillar.icon}
                                </div>
                                <h3 className="text-sm font-black text-indigo-400 tracking-widest uppercase mb-2">{pillar.title}</h3>
                                <h4 className="text-xl font-bold text-white mb-4 font-display">{pillar.subtitle}</h4>
                                <p className="text-slate-400 text-sm leading-relaxed mb-6">{pillar.description}</p>
                                <ul className="space-y-3">
                                    {pillar.bullets.map(bullet => (
                                        <li key={bullet} className="flex items-start gap-3 text-[13px] text-slate-300">
                                            <CheckCircle2 size={16} className="text-indigo-500 shrink-0 mt-0.5" />
                                            {bullet}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Pricing Section */}
            <section id="pricing" className="py-24 px-6 relative overflow-hidden">
                <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-full h-[600px] bg-indigo-500/5 blur-[120px] rounded-full opacity-30 pointer-events-none"></div>
                <div className="max-w-7xl mx-auto relative z-10">
                    <div className="text-center mb-12">
                        <h2 className="text-4xl font-bold text-white mb-4 font-display">Simple, transparent pricing</h2>
                        <p className="text-slate-400 text-lg mb-8 text-center max-w-lg mx-auto">Get high-intent leads on autopilot. <br />Choose the plan that fits your growth stage.</p>

                        {/* Billing Switcher */}
                        <div className="flex items-center justify-center gap-4">
                            <span className={`text-sm ${!isAnnual ? 'text-white font-bold' : 'text-slate-500'}`}>Monthly</span>
                            <button
                                onClick={() => setIsAnnual(!isAnnual)}
                                className="w-14 h-7 rounded-full bg-slate-900 border border-white/10 p-1 flex items-center transition-all relative"
                            >
                                <div className={`w-5 h-5 rounded-full bg-indigo-500 transition-all ${isAnnual ? 'translate-x-7' : 'translate-x-0'}`}></div>
                            </button>
                            <div className="flex items-center gap-2">
                                <span className={`text-sm ${isAnnual ? 'text-white font-bold' : 'text-slate-500'}`}>Annual</span>
                                <span className="bg-indigo-500/20 text-indigo-400 text-[10px] font-black px-2 py-0.5 rounded-full uppercase tracking-tighter shadow-lg shadow-indigo-500/10">Save 20%</span>
                            </div>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        {/* Free */}
                        <div className="p-8 rounded-2xl bg-slate-900/50 border border-white/5 flex flex-col hover:border-indigo-500/20 transition-colors">
                            <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-4">Free</h3>
                            <div className="mb-6">
                                <span className="text-4xl font-bold text-white">$0</span>
                                <span className="text-slate-500 text-sm">/month</span>
                            </div>
                            <p className="text-xs text-slate-500 mb-8 border-b border-white/5 pb-4">For testing the waters</p>
                            <ul className="space-y-4 mb-10 flex-1">
                                <li className="flex items-center gap-3 text-sm text-slate-400"><CheckCircle2 size={16} className="text-indigo-500" /> 2 subreddits</li>
                                <li className="flex items-center gap-3 text-sm text-slate-400"><CheckCircle2 size={16} className="text-indigo-500" /> 1 product config</li>
                                <li className="flex items-center gap-3 text-sm text-slate-400"><CheckCircle2 size={16} className="text-indigo-500" /> 10 responses/mo</li>
                            </ul>
                            <button
                                onClick={onGetStarted}
                                className="w-full py-3 rounded-lg border border-white/10 hover:bg-white/5 font-bold transition-all text-sm"
                            >
                                Start Free
                            </button>
                        </div>

                        {/* Starter */}
                        <div className="p-8 rounded-2xl bg-slate-900/50 border border-white/5 flex flex-col hover:border-indigo-500/20 transition-colors">
                            <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-4">Starter</h3>
                            <div className="mb-6">
                                <span className="text-4xl font-bold text-white">${isAnnual ? '290' : '29'}</span>
                                <span className="text-slate-500 text-sm">{isAnnual ? '/year' : '/month'}</span>
                            </div>
                            <p className="text-xs text-indigo-300/50 mb-8 border-b border-white/5 pb-4">For active validation</p>
                            <ul className="space-y-4 mb-10 flex-1">
                                <li className="flex items-center gap-3 text-sm text-slate-400"><CheckCircle2 size={16} className="text-indigo-500" /> 10 subreddits</li>
                                <li className="flex items-center gap-3 text-sm text-slate-400"><CheckCircle2 size={16} className="text-indigo-500" /> 3 product configs</li>
                                <li className="flex items-center gap-3 text-sm text-slate-400"><CheckCircle2 size={16} className="text-indigo-500" /> 100 responses/mo</li>
                                <li className="flex items-center gap-3 text-sm text-slate-400"><CheckCircle2 size={16} className="text-indigo-500" /> CSV Export</li>
                            </ul>
                            <button
                                onClick={onGetStarted}
                                className="w-full py-3 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-bold transition-all text-sm"
                            >
                                Get Started Now
                            </button>
                        </div>

                        {/* Pro */}
                        <div className="p-8 rounded-3xl bg-indigo-600/5 border-2 border-indigo-500/40 flex flex-col relative shadow-2xl shadow-indigo-500/10 scale-105 z-10">
                            <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-indigo-500 text-white text-[10px] font-black px-4 py-1.5 rounded-full uppercase tracking-widest shadow-lg shadow-indigo-500/20">Most Popular</div>
                            <h3 className="text-sm font-bold text-indigo-400 uppercase tracking-widest mb-4">Pro</h3>
                            <div className="mb-6">
                                <span className="text-4xl font-bold text-white">${isAnnual ? '790' : '79'}</span>
                                <span className="text-slate-500 text-sm">{isAnnual ? '/year' : '/month'}</span>
                            </div>
                            <p className="text-xs text-indigo-300/50 mb-8 border-b border-white/5 pb-4">For scaling founders</p>
                            <ul className="space-y-4 mb-10 flex-1">
                                <li className="flex items-center gap-3 text-sm text-slate-200"><CheckCircle2 size={16} className="text-indigo-500" /> Unlimited subreddits</li>
                                <li className="flex items-center gap-3 text-sm text-slate-200"><CheckCircle2 size={16} className="text-indigo-500" /> 10 product configs</li>
                                <li className="flex items-center gap-3 text-sm text-slate-200"><CheckCircle2 size={16} className="text-indigo-500" /> 300 responses/mo</li>
                                <li className="flex items-center gap-3 text-sm text-slate-200"><CheckCircle2 size={16} className="text-indigo-500" /> Advanced Reports</li>
                            </ul>
                            <button
                                onClick={onGetStarted}
                                className="w-full py-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white shadow-xl shadow-indigo-600/30 font-bold transition-all text-base"
                            >
                                Get Started Now
                            </button>
                        </div>

                        {/* Team */}
                        <div className="p-8 rounded-2xl bg-slate-900/50 border border-white/5 flex flex-col hover:border-indigo-500/20 transition-colors">
                            <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-4">Team</h3>
                            <div className="mb-6">
                                <span className="text-4xl font-bold text-white">${isAnnual ? '1990' : '199'}</span>
                                <span className="text-slate-500 text-sm">{isAnnual ? '/year' : '/month'}</span>
                            </div>
                            <p className="text-xs text-slate-500 mb-8 border-b border-white/5 pb-4">For agencies & growth teams</p>
                            <ul className="space-y-4 mb-10 flex-1">
                                <li className="flex items-center gap-3 text-sm text-slate-400"><CheckCircle2 size={16} className="text-indigo-500" /> Everything in Pro</li>
                                <li className="flex items-center gap-3 text-sm text-slate-400"><CheckCircle2 size={16} className="text-indigo-500" /> 5 team members</li>
                                <li className="flex items-center gap-3 text-sm text-slate-400"><CheckCircle2 size={16} className="text-indigo-500" /> White-label reports</li>
                                <li className="flex items-center gap-3 text-sm text-slate-400"><CheckCircle2 size={16} className="text-indigo-500" /> API Access</li>
                            </ul>
                            <button
                                onClick={onGetStarted}
                                className="w-full py-3 rounded-lg border border-white/10 hover:bg-white/5 font-bold transition-all text-sm"
                            >
                                Get Started Now
                            </button>
                        </div>
                    </div>
                </div>
            </section>

            {/* FAQ Section */}
            <section className="py-24 px-6 bg-slate-950/50">
                <div className="max-w-3xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl font-bold text-white mb-4 font-display">Frequently Asked Questions</h2>
                    </div>
                    <div className="space-y-8">
                        {[
                            { q: "Do I need a Reddit account?", a: "No. SonarPro handles all Reddit access. You only need an account when you're ready to post your response." },
                            { q: "Will my responses look spammy?", a: "No. Our AI is specifically trained to sound like a helpful community member. It focuses on the user's pain first." },
                            { q: "How is this different from keyword alerts?", a: "Keywords find mentions. SonarPro finds intent. We understand the context of the entire discussion." },
                            { q: "What if I hit my limits?", a: "You can upgrade to a higher tier at any time. We'll notify you when you reach 80% and 100% of your monthly response limit." },
                            { q: "Can I monitor competitors?", a: "Yes. You can add your competitors' names as keywords to track where they are being mentioned and join those conversations." },
                            { q: "Can I try SonarPro for free?", a: "Yes. For those just starting out, we have a forever-free tier with 10 responses per month. Our paid plans (Starter, Pro, and Team) offer immediate access to more subreddits and advanced features." },
                            { q: "Can I cancel anytime?", a: "Yes. There are no long-term contracts. You can cancel your subscription at any time from your dashboard." }
                        ].map((faq, i) => (
                            <div key={i} className="bg-slate-900/50 border border-white/5 p-6 rounded-2xl">
                                <h4 className="text-lg font-bold text-white mb-2">{faq.q}</h4>
                                <p className="text-sm text-slate-400 leading-relaxed">{faq.a}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-20 border-t border-white/5 bg-slate-950">
                <div className="max-w-7xl mx-auto px-6">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-16">
                        <div className="col-span-2">
                            <div className="mb-6">
                                <SonarLogo size={36} />
                            </div>
                            <p className="text-sm text-slate-500 font-body mb-6 max-w-sm">
                                Discover leads. Validate ideas. Save hours. <br />
                                The ultimate intelligence platform for social selling.
                            </p>
                            <div className="flex items-center gap-4">
                                <div className="w-8 h-8 rounded-lg bg-slate-900 border border-white/5 flex items-center justify-center text-slate-500 hover:text-white transition-colors cursor-pointer">
                                    <Users size={16} />
                                </div>
                                <div className="w-8 h-8 rounded-lg bg-slate-900 border border-white/5 flex items-center justify-center text-slate-500 hover:text-white transition-colors cursor-pointer" onClick={() => window.location.href = 'mailto:hello@sonarpro.app'}>
                                    <MessageSquare size={16} />
                                </div>
                            </div>
                        </div>

                        <div>
                            <h4 className="text-xs font-black text-white uppercase tracking-widest mb-6">Roadmap</h4>
                            <ul className="space-y-4">
                                <li className="flex items-center gap-2 text-sm text-indigo-400 font-bold">
                                    <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse"></div>
                                    Reddit (Live)
                                </li>
                                <li className="text-sm text-slate-600 italic">Quora (Coming Soon)</li>
                                <li className="text-sm text-slate-600 italic">G2 & Capterra</li>
                                <li className="text-sm text-slate-600 italic">Indie Hackers</li>
                            </ul>
                        </div>

                        <div>
                            <h4 className="text-xs font-black text-white uppercase tracking-widest mb-6">Legal</h4>
                            <ul className="space-y-4">
                                <li><a href="#" className="text-sm text-slate-500 hover:text-white transition-colors">Terms of Service</a></li>
                                <li><a href="#" className="text-sm text-slate-500 hover:text-white transition-colors">Privacy Policy</a></li>
                                <li><a href="#" className="text-sm text-slate-500 hover:text-white transition-colors">Cookie Policy</a></li>
                            </ul>
                        </div>
                    </div>

                    <div className="pt-8 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-4">
                        <p className="text-xs text-slate-600 font-mono">© 2026 SonarPro Project. Made with ❤️ by ProductLab.</p>
                        <p className="text-[10px] text-slate-700 font-mono uppercase tracking-[0.2em]">Detect. Analyze. Respond.</p>
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default LandingPage;
