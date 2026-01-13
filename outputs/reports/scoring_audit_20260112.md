# Radar Scoring & AI Trigger Audit
**Date**: 2026-01-12
**Product**: SocialGenius

## 1. Audit Target Comparison

The user identified two leads that seem inconsistently processed:

| Metric | Lead A (Image 0) | Lead B (Image 1) |
| :--- | :--- | :--- |
| **Title** | "What makes a marketer more hireable..." | "Want to hire someone to run my IG/TIKTOK" |
| **Overall Score** | **19.91** (Higher) | **17.77** (Lower) |
| **Semantic Fit** | 37.0% | 44.4% |
| **Intensity** | 6.36 | 6.11 |
| **Signals** | `SEEKING_TOOL`, `COMPLAINT` | `SEEKING_TOOL` |
| **AI Triggered?** | **❌ NO** | **✅ YES** |

---

## 2. Technical Analysis: Why did this happen?

Radar uses a **Dual-Threshold Logic** to trigger expensive AI analysis:
1.  **Total Relevance >= 7.0**: Passed by both.
2.  **Semantic Fit >= 40% (0.4)**: **FAILED** by Lead A (37.0%).

### Lead A (19.91)
Even though the overall score is very high, it is driven by the **Double Bonus** of two intent signals (`SEEKING_TOOL` + `COMPLAINT`) and a high community intensity. 
The AI trigger logic currently considers 37% "Fit" too low to spend tokens on. However, in this case, the combination of "High Score" + "Decent Fit" indicates a **missed opportunity**.

### Lead B (17.77)
Even though the score is lower, its **direct semantic match (44.4%)** is above the 40% hard threshold, so it triggered the AI.

---

## 3. Recommended Logic Adjustment

The current logic is too rigid. We should implement a **"Safety Bypass"** for high-relevance leads. 

**Current Logic**:
`Trigger AI if (Relevance >= 7.0 AND Fit >= 0.40)`

**Proposed Logic**:
`Trigger AI if (Relevance >= 15.0) OR (Relevance >= 7.0 AND Fit >= 0.40)`

This change ensures that any "Super-Relevance" lead (like Lead A) triggers the AI regardless of whether its semantic fit is slightly below 40%.

---

## 4. Action Plan
1. Update `radar/cli.py` to implement the safety bypass.
2. Re-run `process` for the affected posts to generate AI insights.
