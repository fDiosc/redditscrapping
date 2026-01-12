# Radar Project Deep Architecture & Technical Specification

This document provides a 100% transparent view of how Radar operates, answering every detail of the ingestion, processing, and intelligence pipeline.

---

## 1. INGESTION (The "Harvester")

### 1.1 Comment Ingestion Limits
*   **Quantity**: Radar currently ingests **all** comments loaded on the Reddit page. We removed the previous limit of 3 to capture the full community discussion.
*   **Depth**: We scrape all visible comments on `old.reddit.com`. This includes nested replies (replies of replies) as long as they are rendered in the initial page view.

### 1.2 Rate Limiting & Reliability
*   **Reddit API**: Managed via `PRAW`. It respects the official Reddit rate limits (60 requests per minute) and handles retries with exponential backoff automatically.
*   **Scraper Fallback**: Activated via the `--scraper` flag in CLI or automatically in the API if the main Reddit credentials fail. Currently, the scraper uses a 10-second timeout per request without explicit delay between subreddits.

### 1.3 Duplicates & Reposts
*   **Deduplication**: We use the unique Reddit ID (e.g., `t3_xyz`). The database uses an `INSERT OR REPLACE` policy. If a post is ingested twice, it is updated (refreshing its score and comment count) rather than duplicated.

### 1.4 Frequency & Automation
*   **Frequency**: Currently **Manual/On-Demand**. Triggered via the "Sync" button in the Dashboard or the `ingest` CLI command.
*   **Typical Interval**: Users typically run it once per day or per session.

---

## 2. PROCESSING (The "Engine")

### 2.1 Unified Context & Smart Truncation
*   **The Context**: We concatenate `Title + Body + [Top Comments]`.
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
*   **Posts**: `id, title, body, author, score, num_comments, embedding_id, last_processed_score, last_processed_comments`.
*   **Comments**: `id, post_id, body, author, score, depth`.
*   **Products**: `id, name, description, pain_signals, intent_signals, target_subreddits, embedding_context`.
*   **Post_Analysis**: Stores per-product relevance scores and the **structured JSON** AI analysis.

### 5.2 Storage Size
*   **Current State**: ~500KB for ~30-50 posts.
*   **Path**: `data/radar.db`.
*   **Retention**: No automated cleanup currently. Data stays until manual deletion.

### 5.3 Vector Database (ChromaDB)
*   **Mode**: Persistent on disk at `data/chroma`.
*   **Function**: Stores embeddings and allows semantic similarity lookups.

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
*   **Discovery Dashboard**: The main Lead-focused view. Includes semantic sorting (Relevance vs Intensity), thread expansion, and the **Structured AI Insight Card**.
*   **Product Settings**: A dedicated configuration view. Allows CRUD operations (Create, Read, Update, Delete) on products.
*   **Product Modal**: Interactive form with dynamic tag management for Pain/Intent signals and Subreddits.

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
