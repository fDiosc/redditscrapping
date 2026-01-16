# SonarPro Release Notes

## v0.0.3 (2026-01-16)

### 🚨 AI Ad & Spam Detection
- **Intent-Based Analysis**: New AI logic that distinguishes between "Hard Ads" (generic marketing) and "Insightful Founders" (legitimate leads).
- **Spam Indicators**: Detailed reasons for flagging posts (e.g., "Generic script", "CTA to waiting list").
- **UI Warning Badges**: Visual "Possible AD" identification in the dashboard.

### 🛠️ Pipeline Robustness
- **Error Resiliency**: Added per-post failsafes; a single analysis error no longer stops the entire batch sync.
- **NoneType Safety**: Fixed crashes when processing posts with empty/None content or comments.
- **Database unique constraint**: Added unique index to `post_analysis` to prevent duplicate results and improve data integrity.

### 🔧 Bug Fixes
- **Score Collision Fix**: Resolved SQL column naming collision that caused scores to display as 0.0 in some views.
- **CP1252 Fixes**: Removed special characters from internal CLI tools to prevent encoding crashes on Windows.

---

## v0.0.2 (2026-01-16)

### 🚀 New Features

#### Interactive Onboarding
- Added 5-step guided onboarding for new users
- Empty dashboard with CTAs to help users get started

#### Smart Product Setup
- **URL Auto-Extraction**: Paste your website URL and AI extracts product info automatically
- SPA detection for JavaScript-heavy sites
- Enhanced 3-4 sentence descriptions instead of brief summaries

#### Subreddit Suggestions
- AI-powered suggestions based on product category
- Category-based mapping (SaaS → startup subs, ecommerce → shopify subs, etc.)

#### Async Processing
- Celery + Redis integration for background sync
- Non-blocking sync operations

### ⚡ Performance Improvements

- **Polling reduced**: 5s → 10s to decrease server load
- **Embedding cache**: Product embeddings stored in database, loaded on startup
- **Connection pooling**: Thread-local SQLite connections for better concurrency
- **Bulk comments query**: N+1 query fix for comment loading
- **ChromaDB native query**: Using native `query()` for vector search

### 🔧 Bug Fixes

- Fixed URL extractor receiving corrupted binary content (Accept-Encoding issue)
- Added anti-hallucination rules to prevent LLM from inventing product info
- Fixed stuck sync button when another user triggers sync (15-minute timeout)
- Fixed onboarding modal blocking ProductModal visibility

### 🛡️ Infrastructure

- Rate limiting with slowapi (graceful fallback if not installed)
- Health check endpoint (`/health`)
- Stuck sync detection with automatic timeout after 15 minutes

### 📦 New Dependencies

- `slowapi` - API rate limiting
- `celery[redis]` - Async task processing

---

## v0.0.1 (Initial Release)

- Core Reddit scraping functionality
- Multi-tenant user support with Clerk
- AI-powered lead scoring
- Response generation with multiple styles
