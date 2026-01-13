# SonarPro Brand Identity Guide

## 1. Brand Essence

### Name: SonarPro
**Meaning**: Sonar detects signals in depth. Pro indicates professional-grade tool.

**Tagline**: "Discover leads. Validate ideas. Save hours."

**Brand Voice**: 
- Confident but not arrogant
- Technical but accessible  
- Direct, no fluff
- Helpful, like a smart colleague

---

## 2. Visual Identity

### 2.1 Color Palette

**Primary Colors**

```css
:root {
  /* Core Brand */
  --brand-primary: #6366F1;      /* Indigo - main accent */
  --brand-primary-light: #818CF8; /* Indigo light - hover states */
  --brand-primary-dark: #4F46E5;  /* Indigo dark - pressed states */
  
  /* Backgrounds */
  --bg-base: #09090B;            /* Near black - main background */
  --bg-elevated: #18181B;        /* Zinc 900 - cards, modals */
  --bg-surface: #27272A;         /* Zinc 800 - inputs, hover */
  
  /* Text */
  --text-primary: #FAFAFA;       /* Zinc 50 - headings */
  --text-secondary: #A1A1AA;     /* Zinc 400 - body text */
  --text-muted: #71717A;         /* Zinc 500 - captions */
  
  /* Accents */
  --accent-success: #22C55E;     /* Green - positive states */
  --accent-warning: #F59E0B;     /* Amber - medium urgency */
  --accent-danger: #EF4444;      /* Red - high urgency, errors */
  --accent-info: #3B82F6;        /* Blue - informational */
  
  /* Gradients */
  --gradient-brand: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
  --gradient-glow: radial-gradient(circle at 50% 0%, rgba(99, 102, 241, 0.15) 0%, transparent 50%);
}
```

**Color Usage**

| Element | Color | Purpose |
|---------|-------|---------|
| Background | `--bg-base` | Main page background |
| Cards | `--bg-elevated` | Elevated surfaces |
| Primary CTA | `--brand-primary` | Main actions |
| Secondary CTA | `--bg-surface` | Secondary actions |
| Headings | `--text-primary` | H1, H2, H3 |
| Body | `--text-secondary` | Paragraphs |
| High Urgency | `--accent-danger` | Urgent leads |
| Medium Urgency | `--accent-warning` | Medium priority |
| Success | `--accent-success` | Confirmations |

---

### 2.2 Typography

**Font Stack**

```css
:root {
  /* Display - Headlines */
  --font-display: 'Outfit', sans-serif;
  
  /* Body - Content */
  --font-body: 'DM Sans', sans-serif;
  
  /* Mono - Code, numbers */
  --font-mono: 'JetBrains Mono', monospace;
}
```

**Why These Fonts?**

| Font | Why | Usage |
|------|-----|-------|
| **Outfit** | Modern, geometric, confident. Not overused like Inter. Variable weight. | Headlines, hero text, CTAs |
| **DM Sans** | Clean, friendly, highly readable. Pairs well with geometric fonts. | Body text, descriptions |
| **JetBrains Mono** | Technical credibility. Great for scores, metrics, code. | Numbers, scores, code snippets |

**Type Scale**

```css
/* Headings */
.h1 { font-size: 3.5rem; font-weight: 700; line-height: 1.1; letter-spacing: -0.02em; }
.h2 { font-size: 2.5rem; font-weight: 600; line-height: 1.2; letter-spacing: -0.01em; }
.h3 { font-size: 1.5rem; font-weight: 600; line-height: 1.3; }
.h4 { font-size: 1.25rem; font-weight: 500; line-height: 1.4; }

/* Body */
.body-lg { font-size: 1.125rem; line-height: 1.6; }
.body { font-size: 1rem; line-height: 1.6; }
.body-sm { font-size: 0.875rem; line-height: 1.5; }
.caption { font-size: 0.75rem; line-height: 1.4; text-transform: uppercase; letter-spacing: 0.05em; }
```

---

### 2.3 Logo

**Concept**: Sonar wave emanating from a point, suggesting detection and signal discovery.

**Primary Logo (Horizontal)**

```svg
<svg width="180" height="40" viewBox="0 0 180 40" fill="none" xmlns="http://www.w3.org/2000/svg">
  <!-- Sonar Icon -->
  <g>
    <!-- Center dot -->
    <circle cx="20" cy="20" r="4" fill="#6366F1"/>
    <!-- Wave 1 -->
    <path d="M20 8C26.627 8 32 13.373 32 20C32 26.627 26.627 32 20 32" 
          stroke="#6366F1" stroke-width="2.5" stroke-linecap="round" fill="none" opacity="0.9"/>
    <!-- Wave 2 -->
    <path d="M20 2C29.941 2 38 10.059 38 20C38 29.941 29.941 38 20 38" 
          stroke="#6366F1" stroke-width="2" stroke-linecap="round" fill="none" opacity="0.5"/>
  </g>
  <!-- Wordmark -->
  <text x="50" y="27" font-family="Outfit, sans-serif" font-weight="600" font-size="22" fill="#FAFAFA">
    Sonar<tspan fill="#6366F1">Pro</tspan>
  </text>
</svg>
```

**Icon Only (Square)**

```svg
<svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
  <!-- Center dot -->
  <circle cx="20" cy="20" r="5" fill="#6366F1"/>
  <!-- Wave 1 (strongest) -->
  <path d="M20 7C27.18 7 33 12.82 33 20C33 27.18 27.18 33 20 33" 
        stroke="#6366F1" stroke-width="3" stroke-linecap="round" fill="none"/>
  <!-- Wave 2 (medium) -->
  <path d="M20 1C30.493 1 39 9.507 39 20C39 30.493 30.493 39 20 39" 
        stroke="#6366F1" stroke-width="2" stroke-linecap="round" fill="none" opacity="0.5"/>
</svg>
```

**Favicon (Simple)**

```svg
<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="32" height="32" rx="8" fill="#09090B"/>
  <circle cx="16" cy="16" r="4" fill="#6366F1"/>
  <path d="M16 6C21.523 6 26 10.477 26 16C26 21.523 21.523 26 16 26" 
        stroke="#6366F1" stroke-width="2.5" stroke-linecap="round" fill="none"/>
</svg>
```

---

### 2.4 Logo Variations

| Variation | Background | Logo Color | Use Case |
|-----------|------------|------------|----------|
| Primary | Dark (#09090B) | Indigo + White | Default, website |
| Reversed | Light (#FAFAFA) | Indigo + Dark | Light backgrounds |
| Monochrome | Any | Single color | Partners, press |
| Icon Only | Any | Indigo | Favicon, app icon |

**Clear Space**: Minimum clear space = height of the "S" in Sonar

**Minimum Size**: 
- Horizontal logo: 120px wide
- Icon only: 24px

---

## 3. Landing Page Visual Direction

### 3.1 Aesthetic: "Precision Intelligence"

**Vibe**: Clean, dark, confident. Like a premium analytics dashboard meets a sophisticated radar system.

**NOT**: 
- ❌ Neon cyberpunk (too aggressive)
- ❌ Gradient soup (too generic AI)
- ❌ Flat boring (too safe)
- ❌ Purple everywhere (overdone)

**YES**:
- ✅ Controlled use of indigo accents
- ✅ Subtle glow effects
- ✅ Clean geometric shapes
- ✅ Professional but not corporate

### 3.2 Hero Section Design

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  [Logo]                              [Features] [Pricing] [CTA] │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                    ○)))                                         │
│              [Animated sonar pulse]                             │
│                                                                 │
│     Your ideal customers are on Reddit right now,               │
│     asking for exactly what you sell.                           │
│                                                                 │
│     You're just not finding them fast enough.                   │
│                                                                 │
│     [ Start Free — No Credit Card ]  [ Watch Demo ]             │
│                                                                 │
│                     ↓ Scroll to explore                         │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  [Product Screenshot / Demo Animation]                   │   │
│  │                                                          │   │
│  │  Showing: Dashboard with lead, AI insight, response      │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.3 Visual Elements

**Background**
```css
.hero-bg {
  background: var(--bg-base);
  background-image: 
    radial-gradient(circle at 50% 0%, rgba(99, 102, 241, 0.08) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(139, 92, 246, 0.05) 0%, transparent 40%);
}
```

**Grid Pattern (subtle)**
```css
.grid-pattern {
  background-image: 
    linear-gradient(rgba(99, 102, 241, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(99, 102, 241, 0.03) 1px, transparent 1px);
  background-size: 60px 60px;
}
```

**Glow Cards**
```css
.feature-card {
  background: var(--bg-elevated);
  border: 1px solid rgba(99, 102, 241, 0.1);
  border-radius: 16px;
  position: relative;
}

.feature-card::before {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: 17px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, transparent 50%);
  z-index: -1;
  opacity: 0;
  transition: opacity 0.3s;
}

.feature-card:hover::before {
  opacity: 1;
}
```

**Sonar Animation**
```css
@keyframes sonar-pulse {
  0% {
    transform: scale(0.8);
    opacity: 1;
  }
  100% {
    transform: scale(2);
    opacity: 0;
  }
}

.sonar-wave {
  animation: sonar-pulse 2s ease-out infinite;
}

.sonar-wave:nth-child(2) {
  animation-delay: 0.5s;
}

.sonar-wave:nth-child(3) {
  animation-delay: 1s;
}
```

---

### 3.4 Section Styles

**Section Headers**
```css
.section-header {
  text-align: center;
  margin-bottom: 4rem;
}

.section-label {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--brand-primary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 1rem;
}

.section-title {
  font-family: var(--font-display);
  font-size: 2.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.section-subtitle {
  font-family: var(--font-body);
  font-size: 1.125rem;
  color: var(--text-secondary);
  max-width: 600px;
  margin: 0 auto;
}
```

**Feature Cards**
```
┌──────────────────────────────────┐
│  🎯                              │
│                                  │
│  3 Discovery Modes               │
│                                  │
│  Direct Fit, Opportunity,        │
│  and Intensity modes to find     │
│  leads your way.                 │
│                                  │
└──────────────────────────────────┘
```

**Pricing Cards**
```
┌──────────────────────────────────┐
│           STARTER                │
│                                  │
│           $29                    │
│          /month                  │
│                                  │
│  ✓ 10 subreddits                │
│  ✓ 20 responses/mo              │
│  ✓ 3 products                   │
│  ✓ CSV export                   │
│                                  │
│  [ Start 7-Day Trial ]          │
│                                  │
└──────────────────────────────────┘
```

---

### 3.5 Buttons

**Primary CTA**
```css
.btn-primary {
  background: var(--gradient-brand);
  color: white;
  font-family: var(--font-display);
  font-weight: 500;
  padding: 0.875rem 1.75rem;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 0 20px rgba(99, 102, 241, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 30px rgba(99, 102, 241, 0.5);
}
```

**Secondary CTA**
```css
.btn-secondary {
  background: transparent;
  color: var(--text-primary);
  font-family: var(--font-display);
  font-weight: 500;
  padding: 0.875rem 1.75rem;
  border-radius: 10px;
  border: 1px solid var(--bg-surface);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: var(--bg-surface);
  border-color: var(--brand-primary);
}
```

---

## 4. Component Library Preview

### 4.1 Stat Cards (from dashboard)

```css
.stat-card {
  background: var(--bg-elevated);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1.25rem;
}

.stat-value {
  font-family: var(--font-mono);
  font-size: 2rem;
  font-weight: 600;
  color: var(--text-primary);
}

.stat-label {
  font-family: var(--font-body);
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
```

### 4.2 Urgency Badges

```css
.badge-high {
  background: rgba(239, 68, 68, 0.15);
  color: #EF4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.badge-medium {
  background: rgba(245, 158, 11, 0.15);
  color: #F59E0B;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.badge-low {
  background: rgba(34, 197, 94, 0.15);
  color: #22C55E;
  border: 1px solid rgba(34, 197, 94, 0.3);
}
```

### 4.3 Score Display

```css
.score-display {
  font-family: var(--font-mono);
  font-size: 1.5rem;
  font-weight: 700;
  background: var(--gradient-brand);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
```

---

## 5. Don'ts

| Don't | Why |
|-------|-----|
| Use purple gradients everywhere | Overused AI aesthetic |
| Use Inter or system fonts | Generic, forgettable |
| Add too many colors | Dilutes brand |
| Use light backgrounds | Doesn't match product |
| Overuse animations | Distracting |
| Copy Linear/Stripe exactly | Needs own identity |

---

## 6. Implementation Notes

### Font Loading
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
```

### Tailwind Config (if using)
```js
module.exports = {
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#6366F1',
          light: '#818CF8',
          dark: '#4F46E5',
        },
        surface: {
          base: '#09090B',
          elevated: '#18181B',
          hover: '#27272A',
        }
      },
      fontFamily: {
        display: ['Outfit', 'sans-serif'],
        body: ['DM Sans', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      }
    }
  }
}
```

---

*Brand Guide Version: 1.0*
*Created: January 2026*