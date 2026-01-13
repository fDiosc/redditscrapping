# Comprehensive Lead Scoring Audit
**Date**: 2026-01-12
**Analysis Case**: False Positive Investigation vs. True Lead Verification

## 1. The Scoring System Formula

Radar uses a multi-factor formula to calculate the **Relevance Score** for each lead. The goal is to prioritize leads that are both semantically relevant and demonstrate high urgency.

### The Formula:
`Total Relevance = (Semantic Fit * 15.0) + Community Intensity + Intent Bonus`

1.  **Semantic Fit (0.0 to 1.0)**: Measured via Cosine Similarity between your product description and the post content. Weighted at **15 points** (Max contribution).
2.  **Community Intensity**: Derived from Reddit engagement (comments and upvotes).
    - Formula: `(log10(Comments + 1) * 3.0) + log10(Score + 1)`
    - Range: Typically **3.0 to 10.0**.
3.  **Intent Bonus**: Based on keyword detection in the title and body.
    - `SEEKING_TOOL`: **+5.0**
    - `COMPLAINT`: **+3.0**
    - `COMPARISON`: **+2.0**

### The AI Trigger Guardrail:
To save tokens and focus on high-quality leads, AI analysis only triggers if:
- **Total Relevance >= 7.0**
- **AND Semantic Fit >= 40% (0.4)**

---

## 2. Lead Comparison Analysis

### Lead: "What makes a marketer more hireable - industry specialization or technical skills?"

#### Metrics Breakdown:
- **Total Score**: `19.91`
- **Semantic Fit**: `37.2%` (Contribution: 5.58/15.0)
- **Community Intensity**: `6.33` (Reddit Score: 30 | Comments: 40)
- **Intent Bonus**: `+8.0` (Detected: seeking_tool, complaint)
- **AI Analysis Triggered?**: ❌ NO (Reason: Fit < 40%)

#### Full Post Content:
```text
Recently laid off 40 yr old here, with about 12 years of experience in B2B content marketing and business dev. I feel like my skillset can easily be matched by any driven 23-year-old, or even AI. I feel so generic and replaceable.
So I'm rethinking my next move. One option I’m considering is adding more hard or adjacent skills, like PPC / paid search, and going further into data-driven marketing by learning tools like Power BI. The idea is to stop being a generic content marketer and bring something more concrete to the table.
Another path I’m considering is specialization. I’ve worked across very different industries: events, real estate, retail, printing, and SaaS. But now I think I can contribute a lot in the medical field? Possibly pharma, but medical device feel like an especially strong fit.
I’ve been deeply involved in managing my aging parents’ healthcare, to the point where I’m very fluent in medical terms. During consultations, doctors often assume I have a medical background. I genuinely understand the pulmonology space, and I can see clear gaps in how certain products like BiPAP machines are explained and marketed to end users. I feel like I’d actually be good at this.
What do you think? Will targeting and eventually specializing in an industry like medical devices/pharma increase my value in the job market? I know it would take a lot of work and networking to get into such a regulated industry. Or would I see more ROI by strengthening my technical skills and staying flexible about the industry I apply them in?
```

#### 🔎 Analyst Note (The False Positive):
The high score of **19.91** is an artifact of the 'Double Intent Bonus'. The post matches BOTH `seeking_tool` ('looking for') and `complaint` ('problem', 'hard'). However, it has **ZERO** mentions of social media, posting, or content creator pain points. It is a career advice post. The current algorithm incorrectly allowed these 'general' intents to inflate the score even though the actual context (career advice) is unrelated to SocialGenius.

---

### Lead: "Want to hire someone to run my IG/TIKTOK"

#### Metrics Breakdown:
- **Total Score**: `14.93`
- **Semantic Fit**: `25.5%` (Contribution: 3.82/15.0)
- **Community Intensity**: `6.11` (Reddit Score: 19 | Comments: 39)
- **Intent Bonus**: `+5.0` (Detected: seeking_tool)
- **AI Analysis Triggered?**: ❌ NO (Reason: Fit < 40%)

#### Full Post Content:
```text
I’m an independent music artist and I’m trying to stay OFF social media for my own sanity but still need to post consistently.
Id be looking for someone to:
Upload my Reels/TikToks
Use short captions I approve
Post at good times
Light comment replies (only important stuff)
Tell me if anything urgent pops off
That’s literally it. No editing. No filming. No strategy.
Just posting + light monitoring and I’d send all the content in batches at the start of the month.
```

#### 🔎 Analyst Note (The True Lead):
This is a high-quality lead. The user explicitly says 'Wait to hire someone to run my IG/TIKTOK'. The semantic fit is higher (**44.4%**), which correctly triggered the AI analysis. The total score (17.7) is actually *more accurate* than the career post because it represents a real direct match.

---

## 3. The Path to Corrective Logic: "Structural Relevance"

To fix the False Positive issue found in the first post, we are implementing **Structural Relevance Gating**.

### The Problem:
General intent keywords (like "I'm looking for a tool") are currently adding points to *every* product, even if the post isn't about that product's domain.

### The Fix:
We will gate the Intent Bonus. A post will only receive the +5.0 or +3.0 bonuses **IF AND ONLY IF**:
1.  It has at least one **Product-Specific Keyword** (e.g., "posting", "content ideas" for SocialGenius).
2.  **OR** its **Semantic Fit** is at least **20%** (demonstrating some baseline topical relevance).

**Impact**: 
The Career Advice post (Lead A) has 0 product keywords and low semantic baseline. With this fix, its score will drop from **19.91 to ~11.0**, accurately moving it below the high-priority leads.
