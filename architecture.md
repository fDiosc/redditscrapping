# Radar Project Deep Architecture & Technical Specification

This document provides a 100% transparent view of how Radar operates, answering every detail of the ingestion, processing, and intelligence pipeline.

---

## 1. INGESTION (The "Harvester")

### 1.1 Comment Ingestion Limits
*   **Quantity**: Radar currently ingests **all** comments loaded on the Reddit page. We removed the previous limit of 3 to capture the full community discussion.
*   **Depth**: We scrape all visible comments on `old.reddit.com`. This includes nested replies (replies of replies) as long as they are rendered in the initial page view.

### 1.2 Anti-Ban Protection (Phase 1 MVP)
The scraper includes comprehensive anti-ban measures:

*   **User-Agent Rotation**: Pool of 7 modern browser User-Agents (Chrome, Firefox, Safari) rotated per request.
*   **Complete Headers**: Full browser fingerprint including `Accept`, `Accept-Language`, `DNT`, `Sec-Fetch-*`, `Cache-Control`.
*   **Rate Limiting with Jitter**: 
    *   Base delay: 2-5 seconds between requests
    *   Burst mode: 15% chance of 2.5x longer delay (simulates human distraction)
    *   Micro-jitter: ±10% on all delays
*   **Exponential Backoff**: On errors, delay doubles each retry (2s → 4s → 8s...) up to 60s max.
*   **Retry Handler**: 3 automatic retries for 429, 5xx, and timeouts.
*   **Adaptive Throttling**: On 429 (rate limit), future delays increase by 1.5x automatically.

### 1.3 Duplicates & Reposts
*   **Deduplication**: We use the unique Reddit ID (e.g., `t3_xyz`). The database uses an `INSERT OR REPLACE` policy. If a post is ingested twice, it is updated (refreshing its score and comment count) rather than duplicated.

### 1.4 Frequency & Automation
*   **Frequency**: Currently **Manual/On-Demand**. Triggered via the "Sync" button in the Dashboard or the `ingest` CLI command.
*   **Typical Interval**: Users typically run it once per day or per session.

---

## 2. PROCESSING (The "Engine")

### 2.1 Unified Context & Smart Truncation
*   **The Context**: We concatenate `TITLE + AUTHOR + BODY + [COMMENT BY u/username]`.
*   **Targeted Awareness**: Each piece of content is tagged with its author (Post Author vs. Commenter) to allow the AI to pinpoint the exact lead.
*   **Smart Truncation**: We no longer rely on implicit LLM truncation. We use `tiktoken` to strictly manage the **8,192 token limit** (Target: 7,500 for safety).
*   **Priority Logic**:
    1.  **Title**: Always included in full.
    2.  **Body**: Included next; truncated only if it exceeds ~6,000 tokens.
    3.  **Comments**: Sorted by score and included until the token limit is hit.

### 2.2 Embedding Strategy
*   **Model**: `text-embedding-3-small` (OpenAI).
*   **Dimensionality**: 1,536 dimensions.
*   **Product Embeddings**: Generated using a **Rich Context** generator that combines:
    *   Product Name & Description.
    *   All defined **Pain Points** (Problems solved).
    *   All defined **Intent Signals** (How users search for it).
*   **Refresh**: These are stored in the `products` table (`embedding_context`) and refreshed immediately via the UI when a product is updated.

### 2.3 Performance
*   **Batching**: CLI processes posts in batches of **50**.
*   **Pipeline Speed**: Ingesting and processing 100 posts takes approximately **2-3 minutes** if AI analysis is enabled (AI is the bottleneck). Without AI, it takes seconds.

---

## 3. SCORING (The "Judge")

Radar uses a hybrid scoring system to rank leads.

### 3.1 Fit Score (Semantic Relevance)
*   **Formula**: Cosine Similarity between the Post Embedding and the Product Embedding.
*   **Adjustment**: No manual adjustment; pure semantic distance.

### 3.2 Intensity Score (Community Heat)
*   **Formula**: `intensity = (log10(comments + 1) * 3.0) + log10(max(score, 0) + 1)`
*   **Logic**: We prioritize comments (weight 3.0) over upvotes (weight 1.0) because discussion signifies a more active pain point. The log scale prevents a post with 5,000 upvotes from dwarfing everything else.

### 3.3 Total Relevance (The "Gold" Score)
*   **Formula**: `Relevance = (Fit * 15.0) + Intensity + Intent_Bonus`
*   **Weights**: Fit represents the "Core Match" and is weighted heavily (multiplier 15).
*   **Intent Bonuses**: 
    *   **Seeking Tool**: +5.0
    *   **Complaint**: +3.0
    *   **Comparison**: +2.0
*   **Normalization**: Scores are **not** normalized to 0-1. They are absolute values where a score > 20 indicates a "Hot Lead."

---

## 4. AI INSIGHTS (The "Analyst")

### 4.1 Trigger Logic (Dual Threshold)
*   **Condition**: AI analysis is triggered ONLY if:
    1.  `Total Relevance >= 7.0` (Weighted lead score).
    2.  `Semantic Similarity >= 0.4` (Direct product-to-post fit).
*   **Efficiency**: This ensures we don't waste AI tokens on "intense" posts that have zero actual relationship to the product.

### 4.2 The Structured JSON Analyst
*   **Model**: `gpt-4o-mini` with `json_object` response format.
*   **Output Schema**:
    *   `pain_point_summary`: Concise summary of the user's struggle.
    *   `pain_quote`: Direct snippet from the thread.
    *   `pain_author`: Username of the specific lead who expressed the pain.
    *   `is_from_comment`: boolean (true if the lead is a commenter, false if the post author).
    *   `urgency`: High/Medium/Low.
    *   `product_relevance`: 1-10 numeric score.
    *   `relevance_explanation`: Rationale for the match.
    *   `response_angle`: Recommended social selling approach.
    *   `confidence`: AI's self-assessment (0-1).

### 4.3 Cost & Efficiency
*   **Cost**: Deeply optimized. Input is ~1k tokens ($0.00015). A typical run of 100 leads costs less than **$0.02**.
*   **Timing**: Done automatically during the `process` phase if the relevance threshold is met.

---

## 5. STORAGE & INFRASTRUCTURE

### 5.1 Database Schema (SQLite)

The database uses a **multi-tenant architecture** where Reddit content is shared globally, but user-specific data is isolated by `user_id` (Clerk's unique identifier).

#### Global Tables (Shared)
*   **Posts**: `id, title, body, author, score, num_comments, embedding_id, last_processed_score, last_processed_comments`.
*   **Comments**: `id, post_id, body, author, score, depth`.

#### Per-User Tables (Isolated by `user_id`)
*   **Products**: `id, user_id, name, description, pain_signals, intent_signals, target_subreddits, embedding_context`.
*   **Post_Analysis**: `post_id, product_id, user_id, relevance_score, semantic_similarity, community_score, ai_analysis, signals_json` - per-user analysis of shared posts.
*   **Generated_Responses**: `id, user_id, post_id, product_id, style, response_text, tokens_used, feedback` - AI-generated replies.
*   **Sync_Runs**: `id, user_id, timestamp, product, subreddits, status, progress` - per-user sync history.
*   **User_Settings**: `user_id, key, value` - per-user preferences (onboarding state, etc.).

### 5.2 Storage Size
*   **Current State**: ~500KB for ~30-50 posts.
*   **Path**: `data/radar.db`.
*   **Retention**: No automated cleanup currently. Data stays until manual deletion.

### 5.3 Vector Database (ChromaDB)
*   **Mode**: Persistent on disk at `data/chroma`.
*   **Function**: Stores embeddings and allows semantic similarity lookups.
*   **Scope**: Global (embeddings are shared across users).

---

## 5A. AUTHENTICATION & AUTHORIZATION

### 5A.1 Clerk Integration
*   **Frontend**: Uses `@clerk/clerk-react` with `ClerkProvider` wrapping the app.
*   **Backend**: JWT verification via `radar/api/auth.py`.
*   **Token Flow**: Frontend calls `getToken()` and includes `Authorization: Bearer <token>` header on all API requests.

### 5A.2 API Endpoint Protection

| Endpoint | Auth | Scope |
|----------|------|-------|
| `GET /config` | ✅ Required | Returns user's products and subreddits |
| `GET /threads` | ✅ Required | Returns user's analysis for a product |
| `POST /sync` | ✅ Required | Triggers sync for user's products |
| `GET /sync/status` | ❌ Public | Returns current sync state |
| `GET /sync/history` | ✅ Required | Returns user's sync runs |
| `GET /api/products` | ✅ Required | Lists user's products |
| `GET /api/products/{id}` | ✅ Required | Gets user's specific product |
| `POST /api/products` | ✅ Required | Creates product for user |
| `PUT /api/products/{id}` | ✅ Required | Updates user's product |
| `DELETE /api/products/{id}` | ✅ Required | Deletes user's product |
| `GET /threads/{id}/comments` | ❌ Public | Shared Reddit comments |
| `POST /api/responses/generate/{id}` | ✅ Required | Generates response for user |
| `GET /api/responses/history/{id}` | ✅ Required | User's response history |
| `POST /api/responses/{id}/feedback` | ❌ Public | Submit feedback (id-based) |
| `GET /api/settings/{key}` | ✅ Required | User's setting value |
| `POST /api/settings` | ✅ Required | Save user setting |
| `GET /reports` | ❌ Public | List available reports |
| `GET /reports/download/{file}` | ❌ Public | Download report file |

---

## 6. DISCOVERY MODES (Report Types)

Radar allows you to generate reports using three distinct calibration modes. These are **combinable** (you can run all three in one sync session).

### A. DIRECT FIT (The "Sniper")
*   **Philosophy**: Finds users who are describing your exact product category.
*   **Logic**: `semantic_similarity >= 0.3`.
*   **Priority**: Similarity FIRST, Community Score SECOND.

### B. INTENSITY (The "Trend")
*   **Philosophy**: Finds where the community is hurting the most, regardless of perfect product fit.
*   **Logic**: `community_score >= 0.5`.
*   **Priority**: Community Score FIRST, Similarity SECOND.

### C. OPPORTUNITY (The "Gold Mine")
*   **Philosophy**: This is the "sweet spot." It looks for people with **adjacent problems** who have high engagement or specific intents.
*   **Logic**: `semantic_similarity BETWEEN 0.15 AND 0.4`.
*   **Priority**: **Total Relevance** (which includes Intent Bonuses like `seeking_tool`). 
*   **Why?**: By capping similarity at 0.4, it forces the engine to find leads that are mathematically relevant due to their **urgency** (Intents/Intensity) rather than just keyword matches.

---

## 7. DASHBOARD & UI

### 7.1 Technology
*   **Framework**: React (SPA) built with Vite and Tailwind CSS.
*   **Icons**: Lucide-react for a premium, high-density interface.
*   **API**: FastAPI (Python) backend using Uvicorn.

### 7.2 Views
*   **Discovery Dashboard**: The main Lead-focused view. Includes semantic sorting (Relevance vs Intensity) and the **Interactive Stats Grid**.
*   **Interactive Filtering**: Clickable stat cards (High Fit, High Score, High Intensity) that instantly filter and re-sort the lead list.
*   **AI Insight Card**: Displays detailed analysis including the "Signal Source" (Author vs Commenter) and targeted response options.
*   **Onboarding Wizard**: A discovery tour to guide new users through the dashboard's core metrics and features.
*   **Product Settings**: A dedicated configuration view. Allows CRUD operations (Create, Read, Update, Delete) on products.

### 7.2 Data Fetching
*   **Sync Status**: Polled every 1s from the frontend to show live progress bars and current processing steps.

---

## 8. DYNAMIC CONFIGURATION (Product CRUD)

### 8.1 The Switch from Static to Dynamic
Radar has successfully migrated from hardcoded constants (`products.py`) to a fully **database-driven architecture**.

### 8.2 Product Record Lifecycle
1.  **Creation/Edit**: User provides Name, Description, and Signals via UI.
2.  **Service Layer**: `radar/services/product_service.py` handles the logic.
3.  **Context Generation**: Signals and metadata are flattened into a "Rich Context" string.
4.  **Embedding Sync**: The `SemanticEngine` is notified (or lazy-loads on next run) to regenerate the product's 1536D embedding using the new context.
5.  **Persistence**: The product and its calculated context are stored in the SQLite `products` table.

---

## 9. EDGE CASES & SAFETY

### 7.1 Deletions & Removed Content
*   **Reddit Deletes**: If a post is deleted *after* we ingest it, we keep our copy in the DB.
*   **Ingested Deletes**: If we scrape a post that says `[removed]`, it will have a very low **Fit Score** because its meaning is null.

### 7.2 Safety
*   **NSFW**: Not filtered by default (Business subreddits are rarely NSFW).
*   **Bots**: We use community scores to naturally de-prioritize bot posts (they usually have low Fit/Intensity).
*   **AI Failure**: If OpenAI fails, the post is saved without embedding/score and will be retried on the next `process` run.

---

## 10. PROFILE INTELLIGENCE (RGIG Phase 1)

Radar now includes a high-reasoning response generation engine to facilitate direct social selling.

### 10.1 Flagship Integration (GPT-5.2)
*   **Model**: Utilizing the flagship `gpt-5.2` model for all response generations.
*   **Reasoning Effort**: Fixed at `xhigh`. This ensures the AI deeply understands the nuances of Reddit culture, avoids spammy patterns, and creates logical connections between the user's pain and the solution.
*   **Context Layer**: The generator receives the "Target User" metadata (`pain_author`) and "Source Location" (`is_from_comment`) to ensure the reply is context-correct.

### 10.2 Targeted Reply Logic
*   **Recipient Awareness**:
    *   **Post Replies**: Tone is general and addresses the thread's core topic.
    *   **Comment Replies**: Tone is specific and directly replies to the commenter, acknowledging their unique perspective.
*   **Safety Constraints**: The "Reddit Community Member" system prompt strictly forbids direct mentions of the product name or marketing buzzwords, ensuring 100% human-like delivery.

### 10.3 Feedback & Iteration
*   **The Loop**: User feedback (Thumbs Up/Down) is saved in the `generated_responses` table.
*   **Styles**: Supports 5 distinct presets (`empathetic`, `helpful_expert`, `casual`, `technical`, `brief`) to match different community vibes.
