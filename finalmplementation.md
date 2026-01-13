# SonarPro - Launch Package Complete

Este documento contém:
1. Arquitetura de Auth com Clerk (SSO compartilhado multi-produto)
2. Landing Page Copy completa
3. Pricing Tiers e estratégia de monetização

---

# PARTE 1: AUTENTICAÇÃO E BILLING

## 1.1 Arquitetura Clerk (Standalone)

SonarPro terá sua própria instância Clerk, independente do SocialGenius.

```
┌─────────────────────────────────────────────────────────────────┐
│                    SONARPRO CLERK INSTANCE                      │
│                                                                 │
│  Domain: sonarpro.app                                          │
│  Auth: Email + Google OAuth                                     │
│  Billing: Stripe integration via webhooks                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Implementação Básica

```typescript
// .env.local
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_xxx
CLERK_SECRET_KEY=sk_live_xxx
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
```

```typescript
// middleware.ts
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

const isPublicRoute = createRouteMatcher([
  '/',
  '/pricing',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/webhooks/(.*)',
])

export default clerkMiddleware((auth, request) => {
  if (!isPublicRoute(request)) {
    auth().protect()
  }
})
```

---

## 1.2 Subscription Management

### Modelo de Dados

```typescript
// User metadata no Clerk
interface UserPublicMetadata {
  subscription: {
    plan: 'free' | 'starter' | 'pro' | 'team';
    stripe_customer_id: string;
    stripe_subscription_id: string;
    current_period_end: string;
    usage: {
      responses_used: number;
      responses_reset_at: string;
    }
  }
}
```

### Check de Limites

```typescript
// lib/subscription.ts
import { currentUser } from '@clerk/nextjs/server'

const PLAN_LIMITS = {
  free: { responses: 5, subreddits: 3, products: 1 },
  starter: { responses: 20, subreddits: 10, products: 3 },
  pro: { responses: 100, subreddits: -1, products: 10 },
  team: { responses: -1, subreddits: -1, products: -1 },
}

export async function checkResponseLimit() {
  const user = await currentUser()
  const sub = user?.publicMetadata?.subscription as any
  const plan = sub?.plan || 'free'
  const used = sub?.usage?.responses_used || 0
  const limit = PLAN_LIMITS[plan].responses
  
  return {
    canGenerate: limit === -1 || used < limit,
    used,
    limit,
    plan
  }
}
```

---

## 1.3 Futuro: Bundle com SocialGenius

Quando quiser unificar os produtos, o Clerk suporta **Satellite Domains**:
- Um Clerk = múltiplos domínios
- SSO compartilhado
- Billing unificado

Por ora, mantemos separado para simplicidade. A migração futura é straightforward.

---

# PARTE 2: LANDING PAGE COPY

## 2.1 Estrutura da Landing Page

```
SECTIONS:
├── Hero
├── Problem
├── Solution (3 pillars)
├── How It Works
├── Features Grid
├── Social Proof (quando tiver)
├── Pricing
├── FAQ
└── CTA Final
```

---

## 2.2 Hero Section

### Headline Options

**Option A (Direct)**
```
Find customers complaining about problems you solve.
Respond before competitors even know they exist.
```

**Option B (Outcome)**
```
Turn Reddit discussions into qualified leads.
In minutes, not hours.
```

**Option C (Pain-focused)** ⭐ Recomendado
```
Your ideal customers are on Reddit right now,
asking for exactly what you sell.

You're just not finding them fast enough.
```

### Subheadline
```
SonarPro detects high-intent discussions across Reddit,
analyzes them with AI, and generates authentic responses
that convert lurkers into customers.
```

### CTA
```
[Start Finding Leads Free] → No credit card required
```

### Hero Visual
```
Split screen:
LEFT: Reddit post asking "What tools do you use for X?"
RIGHT: SonarPro dashboard showing the lead with AI insight
       and generated response ready to copy
```

---

## 2.3 Problem Section

### Headline
```
The best leads are hidden in plain sight.
```

### Body
```
Every day, thousands of potential customers go to Reddit
to ask for recommendations, complain about existing tools,
and describe exactly what they need.

But manually finding these conversations is:

❌ Time-consuming – Hours lost digging through irrelevant posts
❌ Hit-or-miss – You find them too late, or never at all
❌ Awkward – Responding feels spammy without the right angle
❌ Unscalable – You can't monitor 10+ subreddits consistently

Meanwhile, your competitors who DO find these leads first
are closing deals you never knew existed.
```

---

## 2.4 Solution Section (3 Pillars)

### Headline
```
Three engines. One mission: Find customers before they find alternatives.
```

### Pillar 1: DETECT
```
🎯 DETECT
Semantic Intelligence Engine

SonarPro doesn't just search keywords—it understands meaning.
Our AI matches your product to discussions where people
describe problems you solve, even if they don't use your words.

• Monitors unlimited subreddits 24/7
• Detects pain signals, not just mentions
• Surfaces leads competitors miss
```

### Pillar 2: ANALYZE
```
🧠 ANALYZE  
AI Lead Qualification

Every lead gets a structured breakdown:
Who's hurting, how much, and why your product fits.

• Pain point extraction with exact quotes
• Urgency scoring (High/Medium/Low)
• Product-market fit score (1-10)
• Recommended engagement angle
```

### Pillar 3: RESPOND
```
💬 RESPOND
Profile Intelligence Engine

Generate responses that feel human, not salesy.
Our AI crafts messages that reference their specific situation,
offer genuine value first, and open conversation naturally.

• 5 tone presets (Empathetic, Expert, Casual, Technical, Brief)
• References their exact words
• Never mentions your product directly
• Ends with engaging follow-up questions
```

---

## 2.5 How It Works

### Headline
```
From noise to leads in 3 steps.
```

### Step 1
```
1. CONFIGURE YOUR RADAR

Tell SonarPro what you sell:
• Product description
• Problems you solve (pain signals)
• How customers search for solutions (intent signals)
• Which subreddits to monitor

Takes 5 minutes. Powers everything else.
```

### Step 2
```
2. RUN INTELLIGENCE SYNC

Hit one button. SonarPro:
• Scans your target subreddits
• Ingests posts AND all comments
• Scores every discussion for relevance
• Generates AI insights for top matches

50+ qualified leads in under 3 minutes.
```

### Step 3
```
3. ENGAGE WITH CONFIDENCE

For each high-intent lead:
• Read the AI-generated insight
• Click "Generate Response"
• Review, copy, and post to Reddit

Turn a cold thread into a warm conversation.
```

---

## 2.6 Features Grid

### Headline
```
Discover leads. Validate ideas. Save hours.
```

### Features (2x4 grid)

```
┌────────────────────────────┬────────────────────────────┐
│ 🎯 3 Discovery Modes       │ 📊 Smart Scoring           │
│                            │                            │
│ Direct Fit: Exact matches  │ Fit + Intensity + Intent   │
│ Opportunity: Adjacent pain │ See why each lead matters  │
│ Intensity: Hot discussions │ Filter by what counts      │
└────────────────────────────┴────────────────────────────┘
┌────────────────────────────┬────────────────────────────┐
│ 🧠 AI Insights             │ 💬 Response Generator      │
│                            │                            │
│ Pain summary + exact quote │ AI-powered, human tone     │
│ Urgency level              │ 5 style presets            │
│ Engagement angle           │ Never feels like marketing │
└────────────────────────────┴────────────────────────────┘
┌────────────────────────────┬────────────────────────────┐
│ 📦 Multi-Product Support   │ 📈 Export & History        │
│                            │                            │
│ Configure multiple products│ CSV/PDF exports            │
│ Switch context instantly   │ Track what you've sent     │
│ Separate signals per product│ Measure engagement        │
└────────────────────────────┴────────────────────────────┘
┌────────────────────────────┬────────────────────────────┐
│ 🔒 No API Keys Needed      │ ⚡ Fast Setup              │
│                            │                            │
│ We handle Reddit access    │ 5 min to first leads       │
│ Works with or without API  │ No code required           │
│ Scraper fallback included  │ Start free, upgrade later  │
└────────────────────────────┴────────────────────────────┘
```

---

## 2.7 Social Proof (Placeholder)

### When you have testimonials
```
"I found 3 customers in my first week using SonarPro.
One of them became a $2k/month client."
— Indie hacker, SaaS founder

"Finally, a Reddit tool that doesn't feel like spam.
The AI responses actually sound like me."
— Agency owner
```

### Before testimonials (use metrics)
```
Trusted by marketers, founders, and sales teams.

• 50+ leads per sync
• <3 min processing time
• AI responses that feel human
• Works for any product or service

Currently in private beta.
[Join the waitlist]
```

---

## 2.8 Pricing Section

### Headline
```
Start finding leads today.
Upgrade when you're closing deals.
```

---

# PARTE 3: PRICING TIERS

## 3.1 Tier Structure

### FREE ($0/forever)
```
FREE
$0/month

For: Testing the waters

LIMITS:
• 3 subreddits monitored
• 500 posts/month
• 10 searches/month
• 1 product configured
• AI insights included
• ✅ 5 response generations/month
• ❌ No exports
• ❌ No reports

[Start Free]
```

### STARTER ($29/month)
```
STARTER
$29/month
(or $278/year — save 20%)

For: Indie hackers validating product-market fit

LIMITS:
• 10 subreddits monitored
• 5,000 posts/month
• 100 searches/month
• 3 products configured
• AI insights included
• ✅ 20 response generations/month
• ✅ 3 basic reports/month
• ✅ CSV export
• ✅ 30-day history

[Start 7-Day Trial]
```

### PRO ($79/month) ⭐ Most Popular
```
PRO
$79/month
(or $758/year — save 20%)

For: Founders & marketers with active GTM

LIMITS:
• Unlimited subreddits
• 25,000 posts/month
• Unlimited searches
• 10 products configured
• AI insights included
• ✅ 100 response generations/month
• ✅ 10 advanced reports/month
• ✅ CSV + PDF export
• ✅ 1-year history
• ✅ Real-time alerts (coming soon)
• ✅ Priority support

[Start 7-Day Trial]
```

### TEAM ($199/month)
```
TEAM
$199/month
(or $1,910/year — save 20%)

For: Agencies & growth teams

INCLUDES:
• Everything in Pro
• 5 team members (+$30/user)
• 100,000 posts/month
• Unlimited response generations
• 10 workspaces
• White-label reports
• API access
• Dedicated support

[Contact Sales]
```

---

## 3.3 Feature Comparison Table

```
┌─────────────────────────┬────────┬─────────┬────────┬────────┐
│ Feature                 │ Free   │ Starter │ Pro    │ Team   │
├─────────────────────────┼────────┼─────────┼────────┼────────┤
│ Subreddits              │ 3      │ 10      │ ∞      │ ∞      │
│ Posts/month             │ 500    │ 5,000   │ 25,000 │ 100,000│
│ Searches/month          │ 10     │ 100     │ ∞      │ ∞      │
│ Products configured     │ 1      │ 3       │ 10     │ ∞      │
├─────────────────────────┼────────┼─────────┼────────┼────────┤
│ AI Insights             │ ✅     │ ✅      │ ✅     │ ✅     │
│ Response Generation     │ 5/mo   │ 20/mo   │ 100/mo │ ∞      │
│ Reports                 │ ❌     │ 3/mo    │ 10/mo  │ ∞      │
│ Export                  │ ❌     │ CSV     │ CSV+PDF│ All    │
├─────────────────────────┼────────┼─────────┼────────┼────────┤
│ History                 │ 7 days │ 30 days │ 1 year │ ∞      │
│ Team members            │ 1      │ 1       │ 1      │ 5+     │
│ API Access              │ ❌     │ ❌      │ ❌     │ ✅     │
│ Priority Support        │ ❌     │ ❌      │ ✅     │ ✅     │
├─────────────────────────┼────────┼─────────┼────────┼────────┤
│ Price                   │ $0     │ $29     │ $79    │ $199   │
└─────────────────────────┴────────┴─────────┴────────┴────────┘
```

---

## 3.4 FAQ

```
Q: Do I need a Reddit account?
A: No. SonarPro handles all Reddit access. You only need an account
   when you're ready to post your response.

Q: Will my responses look spammy?
A: No. Our AI is specifically trained to sound like a helpful
   community member, not a marketer. It never mentions your product
   directly and always leads with value.

Q: How is this different from GummySearch?
A: GummySearch shut down in Nov 2025 due to Reddit API costs.
   SonarPro uses a hybrid approach (API + scraper) that's more
   resilient. Plus, we have AI response generation built-in.

Q: Can I monitor competitors?
A: Yes! Configure a "product" with your competitor's name and
   pain signals. You'll find people complaining about them.

Q: What if I hit my limits?
A: You'll see a notification. You can upgrade anytime or wait
   for the next billing cycle. We never cut off mid-sync.

Q: Is there a free trial?
A: Yes. Starter and Pro have a 7-day free trial with full features.
   No credit card required for the Free tier.

Q: Can I cancel anytime?
A: Yes. No contracts. Cancel from your dashboard in one click.
   You'll keep access until the end of your billing period.
```

---

## 3.5 CTA Final

### Headline
```
Your next customer is asking for help right now.
```

### Body
```
Every hour you wait, someone else finds them first.

Start with Free. Upgrade when you're closing deals.
```

### Buttons
```
[Start Free — No Credit Card] (primary)
[Watch Demo] (secondary)
```

---

# PARTE 4: MOAT / DIFERENCIAÇÃO

## 4.1 Competitive Moat

### Vs. Manual Reddit Browsing
```
┌────────────────────────┬───────────────┬────────────────┐
│ Aspect                 │ Manual        │ SonarPro       │
├────────────────────────┼───────────────┼────────────────┤
│ Time to find 50 leads  │ 5-10 hours    │ 3 minutes      │
│ Semantic understanding │ Your brain    │ AI embeddings  │
│ Consistency            │ Depends on you│ 24/7 automated │
│ Response quality       │ Variable      │ Optimized      │
│ Scalability            │ None          │ Unlimited subs │
└────────────────────────┴───────────────┴────────────────┘
```

### Vs. Competitors (Syften, Redreach)
```
┌────────────────────────┬───────────┬───────────┬────────────┐
│ Feature                │ Syften    │ Redreach  │ SonarPro   │
├────────────────────────┼───────────┼───────────┼────────────┤
│ Semantic matching      │ ❌ Keywords│ ✅ Basic  │ ✅ Advanced │
│ AI Insights            │ ❌        │ ✅ Basic  │ ✅ Detailed │
│ Response Generation    │ ❌        │ ❌        │ ✅ AI-powered│
│ Multiple products      │ ❌        │ ❌        │ ✅ Yes      │
│ Discovery modes        │ 1         │ 1         │ 3          │
│ Comment analysis       │ ❌ Titles │ ❌ Titles │ ✅ Full     │
│ Pricing                │ $19-99    │ $19-79    │ $0-79      │
└────────────────────────┴───────────┴───────────┴────────────┘
```

### Unique Differentiators

1. **Profile Intelligence** (Coming Soon)
   - Learns your writing style from your Reddit history
   - Generates responses that sound like YOU, not generic AI
   - No competitor has this

2. **3 Discovery Modes**
   - Direct Fit: Exact semantic matches
   - Opportunity: Adjacent problems (gold mine)
   - Intensity: Trending discussions
   - Others only have keyword matching

3. **Full Thread Analysis**
   - We analyze comments, not just titles
   - Pain points are often in replies, not posts
   - Competitors miss 70% of signals

4. **Human-Like Response Engine**
   - AI-generated responses that feel authentic
   - High-reasoning for natural conversation flow
   - Never sounds like marketing copy

---

## 4.2 Positioning Statement

### For Landing Page
```
SonarPro is the Reddit intelligence platform
that finds high-intent leads, qualifies them with AI,
and generates human-sounding responses—
so you can turn online discussions into customers
without the awkward cold outreach.
```

### For Elevator Pitch (30 sec)
```
Every day, your ideal customers go to Reddit asking
"what tool should I use for X?"

SonarPro finds those conversations in real-time,
tells you exactly why they're a good fit,
and writes a response that sounds helpful, not salesy.

It's like having a 24/7 sales assistant
that actually understands Reddit culture.
```

### For Twitter/X Bio
```
🔍 Find customers on Reddit before competitors do.
AI-powered lead detection + response generation.
Free to start.
```

---

## 4.3 Launch Checklist

### Before Launch
- [ ] Clerk instance configured
- [ ] Stripe integration complete
- [ ] Landing page live
- [ ] Free tier working
- [ ] Upgrade flow tested
- [ ] Email capture for waitlist

### Launch Day
- [ ] Product Hunt submission
- [ ] Indie Hackers post
- [ ] Twitter thread
- [ ] r/SaaS post (using SonarPro!)

### Week 1 Goals
- [ ] 100 free signups
- [ ] 10 paid conversions
- [ ] 5 testimonials collected
- [ ] 3 bug fixes shipped

---

*Document Version: 1.0*
*Created: January 2026*