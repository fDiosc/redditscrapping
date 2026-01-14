# SonarPro Smart Product Setup - Implementation Plan

## Overview

This feature allows users to paste a URL (their product or competitor) and have SonarPro automatically extract product information and suggest relevant subreddits.

**End Goal**: User pastes URL → Gets pre-filled product config + subreddit suggestions → Starts finding leads in under 2 minutes.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SMART PRODUCT SETUP                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────┐               │
│  │  URL     │───▶│  Scraper     │───▶│  LLM         │               │
│  │  Input   │    │  Service     │    │  Extractor   │               │
│  └──────────┘    └──────────────┘    └──────────────┘               │
│                                              │                       │
│                                              ▼                       │
│                                    ┌──────────────┐                  │
│                                    │  Product     │                  │
│                                    │  Draft       │                  │
│                                    └──────────────┘                  │
│                                              │                       │
│                         ┌────────────────────┼────────────────────┐  │
│                         ▼                    ▼                    ▼  │
│               ┌──────────────┐    ┌──────────────┐    ┌──────────┐  │
│               │  Subreddit   │    │  Category    │    │  Live    │  │
│               │  Database    │    │  Matcher     │    │  Search  │  │
│               └──────────────┘    └──────────────┘    └──────────┘  │
│                         │                    │                    │  │
│                         └────────────────────┼────────────────────┘  │
│                                              ▼                       │
│                                    ┌──────────────┐                  │
│                                    │  Ranked      │                  │
│                                    │  Suggestions │                  │
│                                    └──────────────┘                  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

# PHASE 1: URL Extraction (MVP)

**Duration**: 1-2 days
**Goal**: User pastes URL, gets auto-filled product fields

## 1.1 Backend: Scraper Service

### File: `radar/services/url_extractor.py`

```python
"""
URL Extractor Service
Fetches and parses website content for product information extraction.
"""

import httpx
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional, List
import re


@dataclass
class ExtractedContent:
    """Raw content extracted from a webpage."""
    url: str
    title: str
    meta_description: str
    og_title: Optional[str]
    og_description: Optional[str]
    h1_texts: List[str]
    h2_texts: List[str]
    hero_text: str
    features_text: str
    full_text: str  # Truncated to ~5000 chars


class WebsiteExtractor:
    """Extracts structured content from a website URL."""
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout
    
    async def extract(self, url: str) -> ExtractedContent:
        """
        Fetch URL and extract relevant content.
        
        Args:
            url: The website URL to extract from
            
        Returns:
            ExtractedContent with parsed information
        """
        # Normalize URL
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
        
        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            headers=self.HEADERS
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            html = response.text
        
        return self._parse_html(url, html)
    
    def _parse_html(self, url: str, html: str) -> ExtractedContent:
        """Parse HTML and extract structured content."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        # Extract meta information
        title = self._get_title(soup)
        meta_desc = self._get_meta_description(soup)
        og_title = self._get_og_tag(soup, 'og:title')
        og_desc = self._get_og_tag(soup, 'og:description')
        
        # Extract headings
        h1_texts = [h.get_text(strip=True) for h in soup.find_all('h1')][:5]
        h2_texts = [h.get_text(strip=True) for h in soup.find_all('h2')][:10]
        
        # Extract hero section (usually first major content block)
        hero_text = self._extract_hero(soup)
        
        # Extract features section
        features_text = self._extract_features(soup)
        
        # Get full text (truncated)
        full_text = soup.get_text(separator=' ', strip=True)
        full_text = self._clean_text(full_text)[:5000]
        
        return ExtractedContent(
            url=url,
            title=title,
            meta_description=meta_desc,
            og_title=og_title,
            og_description=og_desc,
            h1_texts=h1_texts,
            h2_texts=h2_texts,
            hero_text=hero_text,
            features_text=features_text,
            full_text=full_text
        )
    
    def _get_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title_tag = soup.find('title')
        return title_tag.get_text(strip=True) if title_tag else ''
    
    def _get_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description."""
        meta = soup.find('meta', attrs={'name': 'description'})
        return meta.get('content', '') if meta else ''
    
    def _get_og_tag(self, soup: BeautifulSoup, property_name: str) -> Optional[str]:
        """Extract Open Graph tag."""
        og = soup.find('meta', attrs={'property': property_name})
        return og.get('content') if og else None
    
    def _extract_hero(self, soup: BeautifulSoup) -> str:
        """Extract hero/above-fold content."""
        # Try common hero selectors
        hero_selectors = [
            'section.hero', 'div.hero', '[class*="hero"]',
            'main > section:first-child', 'main > div:first-child',
            '[class*="landing"]', '[class*="banner"]'
        ]
        
        for selector in hero_selectors:
            hero = soup.select_one(selector)
            if hero:
                text = hero.get_text(separator=' ', strip=True)
                if len(text) > 50:  # Meaningful content
                    return self._clean_text(text)[:1500]
        
        # Fallback: first 1500 chars of body
        body = soup.find('body')
        if body:
            return self._clean_text(body.get_text(separator=' ', strip=True))[:1500]
        return ''
    
    def _extract_features(self, soup: BeautifulSoup) -> str:
        """Extract features section."""
        feature_selectors = [
            '[class*="feature"]', '[class*="benefit"]',
            '[class*="why"]', '[class*="solution"]',
            'section:has(h2)', 'div:has(h3)'
        ]
        
        features_text = []
        for selector in feature_selectors:
            try:
                elements = soup.select(selector)[:5]
                for el in elements:
                    text = el.get_text(separator=' ', strip=True)
                    if 20 < len(text) < 500:
                        features_text.append(text)
            except:
                continue
        
        return ' '.join(features_text)[:2000]
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove common boilerplate
        boilerplate = ['cookie', 'privacy policy', 'terms of service', 
                       'all rights reserved', 'subscribe to newsletter']
        for bp in boilerplate:
            text = re.sub(rf'\b{bp}\b.*?\.', '', text, flags=re.IGNORECASE)
        return text.strip()
```

---

## 1.2 Backend: LLM Product Extractor

### File: `radar/services/product_extractor.py`

```python
"""
Product Extractor Service
Uses LLM to extract structured product information from website content.
"""

import json
from dataclasses import dataclass, asdict
from typing import List, Optional
from openai import AsyncOpenAI

from .url_extractor import ExtractedContent


@dataclass
class ProductDraft:
    """Extracted product information ready for review."""
    name: str
    description: str
    pain_signals: List[str]
    intent_signals: List[str]
    target_audience: str
    category: str
    competitors: List[str]
    confidence: float  # 0-1, how confident the extraction is
    
    def to_dict(self):
        return asdict(self)


class ProductExtractor:
    """Extracts structured product information using LLM."""
    
    EXTRACTION_PROMPT = '''You are an expert product analyst. Analyze the following website content and extract structured product information.

WEBSITE CONTENT:
---
URL: {url}
Title: {title}
Meta Description: {meta_description}
Headlines (H1): {h1_texts}
Headlines (H2): {h2_texts}
Hero Section: {hero_text}
Features: {features_text}
---

Extract the following information in JSON format:

{{
    "name": "The product/company name (just the name, no taglines)",
    "description": "2-3 sentence description of what the product does, who it's for, and its main value proposition",
    "pain_signals": [
        "List 3-5 problems/frustrations this product solves",
        "Write them as a user would describe their pain",
        "Use natural language like: 'spending too much time on X', 'losing money because of Y'",
        "Focus on emotional and practical pain points"
    ],
    "intent_signals": [
        "List 3-5 search terms someone would use to find this solution",
        "Include both problem-focused ('how to fix X') and solution-focused ('best tool for Y') queries",
        "Use natural search language"
    ],
    "target_audience": "Brief description of the ideal customer (role, company size, industry)",
    "category": "One of: saas, ecommerce, marketing, developer_tools, productivity, finance, ai_tools, agency, education, health, other",
    "competitors": ["List any competitors mentioned or implied, or similar well-known tools"],
    "confidence": 0.85
}}

IMPORTANT:
- For pain_signals, think about what would make someone search for this product
- For intent_signals, think about actual Reddit post titles or search queries
- Be specific, not generic. "Saving time" is too vague. "Spending 5 hours/week on manual data entry" is specific.
- If information is unclear, make reasonable inferences based on the product type
- Set confidence lower (0.5-0.7) if the website content is limited

Return ONLY valid JSON, no markdown or explanation.'''

    def __init__(self, client: AsyncOpenAI = None):
        self.client = client or AsyncOpenAI()
    
    async def extract(self, content: ExtractedContent) -> ProductDraft:
        """
        Extract product information from website content.
        
        Args:
            content: ExtractedContent from WebsiteExtractor
            
        Returns:
            ProductDraft with structured product information
        """
        prompt = self.EXTRACTION_PROMPT.format(
            url=content.url,
            title=content.title,
            meta_description=content.meta_description,
            h1_texts=', '.join(content.h1_texts) or 'N/A',
            h2_texts=', '.join(content.h2_texts[:5]) or 'N/A',
            hero_text=content.hero_text[:1000] or 'N/A',
            features_text=content.features_text[:1000] or 'N/A'
        )
        
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a product analyst. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        return ProductDraft(
            name=result.get('name', ''),
            description=result.get('description', ''),
            pain_signals=result.get('pain_signals', [])[:5],
            intent_signals=result.get('intent_signals', [])[:5],
            target_audience=result.get('target_audience', ''),
            category=result.get('category', 'other'),
            competitors=result.get('competitors', [])[:5],
            confidence=float(result.get('confidence', 0.7))
        )
```

---

## 1.3 Backend: API Endpoint

### File: `radar/api/routes/extraction.py`

```python
"""
URL Extraction API endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from typing import List, Optional

from radar.services.url_extractor import WebsiteExtractor
from radar.services.product_extractor import ProductExtractor
from radar.api.auth import get_current_user

router = APIRouter(prefix="/api/extract", tags=["extraction"])


class ExtractionRequest(BaseModel):
    url: str
    
class ExtractionResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None


# Initialize services
website_extractor = WebsiteExtractor()
product_extractor = ProductExtractor()


@router.post("/url", response_model=ExtractionResponse)
async def extract_from_url(
    request: ExtractionRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Extract product information from a URL.
    
    This endpoint:
    1. Fetches the webpage
    2. Extracts relevant content
    3. Uses AI to structure the information
    4. Returns a draft product configuration
    """
    try:
        # Step 1: Fetch and parse website
        content = await website_extractor.extract(request.url)
        
        # Step 2: Extract product info using LLM
        product_draft = await product_extractor.extract(content)
        
        # Step 3: Return structured data
        return ExtractionResponse(
            success=True,
            data=product_draft.to_dict()
        )
        
    except httpx.HTTPError as e:
        return ExtractionResponse(
            success=False,
            error=f"Could not fetch URL: {str(e)}"
        )
    except Exception as e:
        return ExtractionResponse(
            success=False,
            error=f"Extraction failed: {str(e)}"
        )
```

### Register in main router

```python
# In radar/api/main.py
from radar.api.routes import extraction

app.include_router(extraction.router)
```

---

## 1.4 Frontend: Updated Product Modal

### File: `src/components/ProductModal.jsx`

```jsx
import React, { useState } from 'react';
import { X, Link, Loader2, Sparkles, Plus, Trash2 } from 'lucide-react';

export default function ProductModal({ isOpen, onClose, onSave, initialData = null }) {
  // Form state
  const [name, setName] = useState(initialData?.name || '');
  const [description, setDescription] = useState(initialData?.description || '');
  const [painSignals, setPainSignals] = useState(initialData?.pain_signals || []);
  const [intentSignals, setIntentSignals] = useState(initialData?.intent_signals || []);
  const [subreddits, setSubreddits] = useState(initialData?.subreddits || []);
  
  // Extraction state
  const [extractUrl, setExtractUrl] = useState('');
  const [isExtracting, setIsExtracting] = useState(false);
  const [extractionError, setExtractionError] = useState(null);
  const [wasExtracted, setWasExtracted] = useState(false);
  
  // Input states for adding new items
  const [newPainSignal, setNewPainSignal] = useState('');
  const [newIntentSignal, setNewIntentSignal] = useState('');
  const [newSubreddit, setNewSubreddit] = useState('');

  const handleExtract = async () => {
    if (!extractUrl.trim()) return;
    
    setIsExtracting(true);
    setExtractionError(null);
    
    try {
      const response = await fetch('/api/extract/url', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await getToken()}`
        },
        body: JSON.stringify({ url: extractUrl })
      });
      
      const result = await response.json();
      
      if (result.success && result.data) {
        // Auto-fill form fields
        setName(result.data.name || '');
        setDescription(result.data.description || '');
        setPainSignals(result.data.pain_signals || []);
        setIntentSignals(result.data.intent_signals || []);
        setWasExtracted(true);
        
        // TODO: Trigger subreddit suggestions based on category
      } else {
        setExtractionError(result.error || 'Extraction failed');
      }
    } catch (error) {
      setExtractionError('Network error. Please try again.');
    } finally {
      setIsExtracting(false);
    }
  };

  const addItem = (list, setList, value, setValue) => {
    if (value.trim() && !list.includes(value.trim())) {
      setList([...list, value.trim()]);
      setValue('');
    }
  };

  const removeItem = (list, setList, index) => {
    setList(list.filter((_, i) => i !== index));
  };

  const handleSave = () => {
    onSave({
      name,
      description,
      pain_signals: painSignals,
      intent_signals: intentSignals,
      target_subreddits: subreddits
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-[#1a1a2e] rounded-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-800">
          <h2 className="text-xl font-semibold text-white">
            {initialData ? 'Edit Product' : 'Add New Product'}
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X size={24} />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Quick Setup Section */}
          <div className="bg-[#252542] rounded-lg p-4 border border-[#6366F1]/30">
            <div className="flex items-center gap-2 mb-3">
              <Sparkles size={18} className="text-[#6366F1]" />
              <span className="text-sm font-medium text-[#6366F1]">QUICK SETUP</span>
              <span className="text-xs text-gray-500">(Optional)</span>
            </div>
            
            <div className="flex gap-2">
              <div className="flex-1 relative">
                <Link size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                <input
                  type="text"
                  value={extractUrl}
                  onChange={(e) => setExtractUrl(e.target.value)}
                  placeholder="https://yourproduct.com"
                  className="w-full bg-[#1a1a2e] border border-gray-700 rounded-lg pl-10 pr-4 py-2.5 text-white placeholder-gray-500 focus:border-[#6366F1] focus:outline-none"
                  onKeyDown={(e) => e.key === 'Enter' && handleExtract()}
                />
              </div>
              <button
                onClick={handleExtract}
                disabled={isExtracting || !extractUrl.trim()}
                className="px-4 py-2.5 bg-[#6366F1] hover:bg-[#5558E3] disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg text-white font-medium flex items-center gap-2 transition-colors"
              >
                {isExtracting ? (
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
            
            <p className="text-xs text-gray-500 mt-2">
              Paste your website or a competitor's URL to auto-fill product details
            </p>
            
            {extractionError && (
              <p className="text-xs text-red-400 mt-2">{extractionError}</p>
            )}
            
            {wasExtracted && (
              <p className="text-xs text-green-400 mt-2">
                ✓ Fields auto-filled. Review and edit as needed.
              </p>
            )}
          </div>

          {/* Divider */}
          <div className="flex items-center gap-4">
            <div className="flex-1 border-t border-gray-800"></div>
            <span className="text-xs text-gray-600 uppercase">Product Details</span>
            <div className="flex-1 border-t border-gray-800"></div>
          </div>

          {/* Product Name */}
          <div>
            <label className="block text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">
              Product Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. ProfitDoctor"
              className="w-full bg-[#252542] border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:border-[#6366F1] focus:outline-none"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">
              Description <span className="text-gray-600">(Powers semantic matching)</span>
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Explain what the product does, who it's for, and why it matters..."
              rows={3}
              className="w-full bg-[#252542] border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:border-[#6366F1] focus:outline-none resize-none"
            />
          </div>

          {/* Pain Signals */}
          <div>
            <label className="block text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">
              Pain Signals <span className="text-gray-600">(Problems you solve)</span>
            </label>
            <div className="space-y-2">
              {painSignals.map((signal, index) => (
                <div key={index} className="flex items-center gap-2 bg-[#252542] border border-gray-700 rounded-lg px-4 py-2">
                  <span className="flex-1 text-white text-sm">{signal}</span>
                  <button
                    onClick={() => removeItem(painSignals, setPainSignals, index)}
                    className="text-gray-500 hover:text-red-400"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ))}
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newPainSignal}
                  onChange={(e) => setNewPainSignal(e.target.value)}
                  placeholder="e.g. losing money on ads"
                  className="flex-1 bg-[#252542] border border-gray-700 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:border-[#6366F1] focus:outline-none text-sm"
                  onKeyDown={(e) => e.key === 'Enter' && addItem(painSignals, setPainSignals, newPainSignal, setNewPainSignal)}
                />
                <button
                  onClick={() => addItem(painSignals, setPainSignals, newPainSignal, setNewPainSignal)}
                  className="p-2 bg-[#6366F1] hover:bg-[#5558E3] rounded-lg text-white"
                >
                  <Plus size={18} />
                </button>
              </div>
            </div>
          </div>

          {/* Intent Signals */}
          <div>
            <label className="block text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">
              Intent Signals <span className="text-gray-600">(How they search)</span>
            </label>
            <div className="space-y-2">
              {intentSignals.map((signal, index) => (
                <div key={index} className="flex items-center gap-2 bg-[#252542] border border-gray-700 rounded-lg px-4 py-2">
                  <span className="flex-1 text-white text-sm">{signal}</span>
                  <button
                    onClick={() => removeItem(intentSignals, setIntentSignals, index)}
                    className="text-gray-500 hover:text-red-400"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ))}
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newIntentSignal}
                  onChange={(e) => setNewIntentSignal(e.target.value)}
                  placeholder="e.g. best profit tracking tool"
                  className="flex-1 bg-[#252542] border border-gray-700 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:border-[#6366F1] focus:outline-none text-sm"
                  onKeyDown={(e) => e.key === 'Enter' && addItem(intentSignals, setIntentSignals, newIntentSignal, setNewIntentSignal)}
                />
                <button
                  onClick={() => addItem(intentSignals, setIntentSignals, newIntentSignal, setNewIntentSignal)}
                  className="p-2 bg-[#6366F1] hover:bg-[#5558E3] rounded-lg text-white"
                >
                  <Plus size={18} />
                </button>
              </div>
            </div>
          </div>

          {/* Target Subreddits */}
          <div>
            <label className="block text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">
              Target Subreddits
            </label>
            <div className="space-y-2">
              {subreddits.map((sub, index) => (
                <div key={index} className="flex items-center gap-2 bg-[#252542] border border-gray-700 rounded-lg px-4 py-2">
                  <span className="flex-1 text-white text-sm">r/{sub}</span>
                  <button
                    onClick={() => removeItem(subreddits, setSubreddits, index)}
                    className="text-gray-500 hover:text-red-400"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ))}
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newSubreddit}
                  onChange={(e) => setNewSubreddit(e.target.value.replace(/^r\//, ''))}
                  placeholder="e.g. shopify"
                  className="flex-1 bg-[#252542] border border-gray-700 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:border-[#6366F1] focus:outline-none text-sm"
                  onKeyDown={(e) => e.key === 'Enter' && addItem(subreddits, setSubreddits, newSubreddit, setNewSubreddit)}
                />
                <button
                  onClick={() => addItem(subreddits, setSubreddits, newSubreddit, setNewSubreddit)}
                  className="p-2 bg-[#6366F1] hover:bg-[#5558E3] rounded-lg text-white"
                >
                  <Plus size={18} />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-800">
          <button
            onClick={onClose}
            className="px-6 py-2.5 text-gray-400 hover:text-white transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={!name.trim()}
            className="px-6 py-2.5 bg-[#6366F1] hover:bg-[#5558E3] disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg text-white font-medium transition-colors"
          >
            Save Product
          </button>
        </div>
      </div>
    </div>
  );
}
```

---

## 1.5 Testing Phase 1

```bash
# Test extraction endpoint
curl -X POST http://localhost:8000/api/extract/url \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"url": "https://profitdoctor.app"}'

# Expected response:
{
  "success": true,
  "data": {
    "name": "ProfitDoctor",
    "description": "AI-powered profit diagnosis for Shopify stores...",
    "pain_signals": [
      "don't know my real profit margins",
      "losing money on unprofitable products",
      "spreadsheets are a nightmare"
    ],
    "intent_signals": [
      "shopify profit calculator",
      "best profit tracking app",
      "how to calculate real profit margins"
    ],
    "target_audience": "Shopify store owners",
    "category": "ecommerce",
    "competitors": ["BeProfit", "TrueProfit", "Lifetimely"],
    "confidence": 0.85
  }
}
```

---

# PHASE 2: Subreddit Database & Suggestions

**Duration**: 2-3 days
**Goal**: Suggest relevant subreddits based on product category and signals

## 2.1 Database Schema

### File: `radar/db/schema_subreddits.sql`

```sql
-- Subreddit index for suggestions
CREATE TABLE IF NOT EXISTS subreddit_index (
    name TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    description TEXT,
    subscribers INTEGER DEFAULT 0,
    posts_per_day REAL DEFAULT 0,
    avg_comments REAL DEFAULT 0,
    
    -- Categorization (JSON array)
    categories TEXT NOT NULL DEFAULT '[]',
    
    -- Keywords for matching (JSON array)
    keywords TEXT NOT NULL DEFAULT '[]',
    
    -- Quality indicators
    is_active BOOLEAN DEFAULT TRUE,
    quality_score REAL DEFAULT 0.5,  -- 0-1, based on engagement
    
    -- Metadata
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- For semantic search (optional, Phase 3)
    embedding_id TEXT
);

-- Index for category lookups
CREATE INDEX IF NOT EXISTS idx_subreddit_categories ON subreddit_index(categories);

-- View for quick category lookup
CREATE VIEW IF NOT EXISTS subreddit_by_category AS
SELECT 
    name,
    display_name,
    subscribers,
    posts_per_day,
    quality_score,
    json_each.value as category
FROM subreddit_index, json_each(categories);
```

---

## 2.2 Subreddit Suggester Service

### File: `radar/services/subreddit_suggester.py`

```python
"""
Subreddit Suggester Service
Suggests relevant subreddits based on product information.
"""

import json
import sqlite3
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path


@dataclass
class SubredditSuggestion:
    """A suggested subreddit with metadata."""
    name: str
    display_name: str
    description: Optional[str]
    subscribers: int
    posts_per_day: float
    relevance_score: float  # 0-1, how relevant to the product
    match_reason: str  # Why this was suggested
    
    def to_dict(self):
        return {
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'subscribers': self.subscribers,
            'posts_per_day': self.posts_per_day,
            'relevance_score': self.relevance_score,
            'match_reason': self.match_reason
        }


class SubredditSuggester:
    """Suggests subreddits based on product category and signals."""
    
    # Category mappings for quick lookup
    CATEGORY_WEIGHTS = {
        'primary': 1.0,    # Exact category match
        'secondary': 0.7,  # Related category
        'general': 0.4     # General business/tech
    }
    
    def __init__(self, db_path: str = "data/radar.db"):
        self.db_path = db_path
    
    def suggest(
        self,
        category: str,
        pain_signals: List[str] = None,
        intent_signals: List[str] = None,
        limit: int = 10
    ) -> List[SubredditSuggestion]:
        """
        Suggest subreddits based on product information.
        
        Args:
            category: Product category (e.g., 'ecommerce', 'saas')
            pain_signals: List of pain points
            intent_signals: List of search terms
            limit: Maximum suggestions to return
            
        Returns:
            List of SubredditSuggestion sorted by relevance
        """
        suggestions = []
        
        # 1. Get subreddits by category
        category_matches = self._get_by_category(category)
        for sub in category_matches:
            sub.match_reason = f"Matches category: {category}"
            suggestions.append(sub)
        
        # 2. Get subreddits by keywords (from signals)
        all_signals = (pain_signals or []) + (intent_signals or [])
        keyword_matches = self._get_by_keywords(all_signals)
        for sub in keyword_matches:
            # Avoid duplicates
            if not any(s.name == sub.name for s in suggestions):
                sub.match_reason = "Matches product keywords"
                suggestions.append(sub)
        
        # 3. Add general business subreddits if not enough
        if len(suggestions) < limit:
            general = self._get_general_subreddits()
            for sub in general:
                if not any(s.name == sub.name for s in suggestions):
                    sub.relevance_score *= 0.5  # Lower score for general
                    sub.match_reason = "Popular business community"
                    suggestions.append(sub)
        
        # 4. Sort by relevance and return top N
        suggestions.sort(key=lambda x: (x.relevance_score, x.subscribers), reverse=True)
        return suggestions[:limit]
    
    def _get_by_category(self, category: str) -> List[SubredditSuggestion]:
        """Get subreddits matching a category."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT name, display_name, description, subscribers, posts_per_day, quality_score
            FROM subreddit_index
            WHERE categories LIKE ?
            AND is_active = TRUE
            ORDER BY quality_score DESC, subscribers DESC
            LIMIT 20
        ''', (f'%"{category}"%',))
        
        results = []
        for row in cursor.fetchall():
            results.append(SubredditSuggestion(
                name=row[0],
                display_name=row[1],
                description=row[2],
                subscribers=row[3],
                posts_per_day=row[4],
                relevance_score=row[5],
                match_reason=""
            ))
        
        conn.close()
        return results
    
    def _get_by_keywords(self, keywords: List[str]) -> List[SubredditSuggestion]:
        """Get subreddits matching keywords."""
        if not keywords:
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build OR query for keywords
        conditions = []
        params = []
        for kw in keywords[:10]:  # Limit keywords
            kw_lower = kw.lower()
            conditions.append('(LOWER(keywords) LIKE ? OR LOWER(description) LIKE ?)')
            params.extend([f'%{kw_lower}%', f'%{kw_lower}%'])
        
        query = f'''
            SELECT name, display_name, description, subscribers, posts_per_day, quality_score
            FROM subreddit_index
            WHERE ({' OR '.join(conditions)})
            AND is_active = TRUE
            ORDER BY quality_score DESC, subscribers DESC
            LIMIT 15
        '''
        
        cursor.execute(query, params)
        
        results = []
        for row in cursor.fetchall():
            results.append(SubredditSuggestion(
                name=row[0],
                display_name=row[1],
                description=row[2],
                subscribers=row[3],
                posts_per_day=row[4],
                relevance_score=row[5] * 0.8,  # Slightly lower than category match
                match_reason=""
            ))
        
        conn.close()
        return results
    
    def _get_general_subreddits(self) -> List[SubredditSuggestion]:
        """Get general business/startup subreddits."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT name, display_name, description, subscribers, posts_per_day, quality_score
            FROM subreddit_index
            WHERE categories LIKE '%"general"%'
            AND is_active = TRUE
            ORDER BY subscribers DESC
            LIMIT 10
        ''')
        
        results = []
        for row in cursor.fetchall():
            results.append(SubredditSuggestion(
                name=row[0],
                display_name=row[1],
                description=row[2],
                subscribers=row[3],
                posts_per_day=row[4],
                relevance_score=row[5] * 0.4,
                match_reason=""
            ))
        
        conn.close()
        return results
```

---

## 2.3 API Endpoint for Suggestions

### File: `radar/api/routes/extraction.py` (add to existing)

```python
class SuggestionRequest(BaseModel):
    category: str
    pain_signals: List[str] = []
    intent_signals: List[str] = []
    
class SuggestionResponse(BaseModel):
    success: bool
    suggestions: List[dict] = []
    error: Optional[str] = None


subreddit_suggester = SubredditSuggester()


@router.post("/subreddits/suggest", response_model=SuggestionResponse)
async def suggest_subreddits(
    request: SuggestionRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Suggest relevant subreddits based on product information.
    
    Call this after extraction to get subreddit suggestions.
    """
    try:
        suggestions = subreddit_suggester.suggest(
            category=request.category,
            pain_signals=request.pain_signals,
            intent_signals=request.intent_signals,
            limit=10
        )
        
        return SuggestionResponse(
            success=True,
            suggestions=[s.to_dict() for s in suggestions]
        )
        
    except Exception as e:
        return SuggestionResponse(
            success=False,
            error=str(e)
        )
```

---

## 2.4 Updated Frontend with Suggestions

### Add to `ProductModal.jsx`:

```jsx
// Add state for suggestions
const [suggestedSubreddits, setSuggestedSubreddits] = useState([]);
const [loadingSuggestions, setLoadingSuggestions] = useState(false);

// After successful extraction, fetch suggestions
const handleExtract = async () => {
  // ... existing extraction code ...
  
  if (result.success && result.data) {
    // Auto-fill form fields (existing)
    setName(result.data.name || '');
    setDescription(result.data.description || '');
    setPainSignals(result.data.pain_signals || []);
    setIntentSignals(result.data.intent_signals || []);
    setWasExtracted(true);
    
    // NEW: Fetch subreddit suggestions
    await fetchSubredditSuggestions(
      result.data.category,
      result.data.pain_signals,
      result.data.intent_signals
    );
  }
};

const fetchSubredditSuggestions = async (category, painSignals, intentSignals) => {
  setLoadingSuggestions(true);
  try {
    const response = await fetch('/api/extract/subreddits/suggest', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${await getToken()}`
      },
      body: JSON.stringify({
        category,
        pain_signals: painSignals,
        intent_signals: intentSignals
      })
    });
    
    const result = await response.json();
    if (result.success) {
      setSuggestedSubreddits(result.suggestions);
    }
  } catch (error) {
    console.error('Failed to fetch suggestions:', error);
  } finally {
    setLoadingSuggestions(false);
  }
};

// Add suggestions UI after Target Subreddits section
{suggestedSubreddits.length > 0 && (
  <div className="bg-[#252542]/50 rounded-lg p-4 border border-dashed border-gray-700">
    <div className="flex items-center gap-2 mb-3">
      <Sparkles size={16} className="text-[#6366F1]" />
      <span className="text-sm font-medium text-gray-300">Suggested Subreddits</span>
    </div>
    <div className="space-y-2">
      {suggestedSubreddits.map((sub) => (
        <div 
          key={sub.name}
          className="flex items-center justify-between bg-[#1a1a2e] rounded-lg px-3 py-2"
        >
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <span className="text-white text-sm">r/{sub.name}</span>
              <span className="text-xs text-gray-500">
                {(sub.subscribers / 1000).toFixed(0)}k members
              </span>
            </div>
            <p className="text-xs text-gray-500 truncate">{sub.match_reason}</p>
          </div>
          <button
            onClick={() => {
              if (!subreddits.includes(sub.name)) {
                setSubreddits([...subreddits, sub.name]);
              }
            }}
            disabled={subreddits.includes(sub.name)}
            className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
              subreddits.includes(sub.name)
                ? 'bg-green-500/20 text-green-400 cursor-default'
                : 'bg-[#6366F1]/20 text-[#6366F1] hover:bg-[#6366F1]/30'
            }`}
          >
            {subreddits.includes(sub.name) ? '✓ Added' : '+ Add'}
          </button>
        </div>
      ))}
    </div>
  </div>
)}
```

---

# PHASE 3: Live Validation & Enhanced Discovery

**Duration**: 1 week
**Goal**: Validate subreddits in real-time, add semantic search

## 3.1 Live Subreddit Validator

### File: `radar/services/subreddit_validator.py`

```python
"""
Live Subreddit Validator
Validates and enriches subreddit data from Reddit in real-time.
"""

import httpx
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime, timedelta


@dataclass
class SubredditStats:
    """Real-time stats for a subreddit."""
    name: str
    subscribers: int
    active_users: int
    posts_per_day: float
    avg_comments: float
    is_nsfw: bool
    is_active: bool
    last_post_date: Optional[datetime]


class SubredditValidator:
    """Validates subreddits against live Reddit data."""
    
    REDDIT_BASE = "https://old.reddit.com"
    
    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; SonarPro/1.0)"
        }
    
    async def validate(self, subreddit_name: str) -> Optional[SubredditStats]:
        """
        Validate a subreddit and get current stats.
        
        Returns None if subreddit doesn't exist or is banned.
        """
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                headers=self.headers
            ) as client:
                # Fetch subreddit about page
                response = await client.get(
                    f"{self.REDDIT_BASE}/r/{subreddit_name}/about.json"
                )
                
                if response.status_code != 200:
                    return None
                
                data = response.json().get('data', {})
                
                # Check if banned or private
                if data.get('subreddit_type') in ['private', 'restricted']:
                    return None
                
                # Calculate posts per day (rough estimate)
                posts_per_day = await self._estimate_posts_per_day(client, subreddit_name)
                
                return SubredditStats(
                    name=subreddit_name,
                    subscribers=data.get('subscribers', 0),
                    active_users=data.get('accounts_active', 0),
                    posts_per_day=posts_per_day,
                    avg_comments=0,  # Would need more API calls
                    is_nsfw=data.get('over18', False),
                    is_active=data.get('subscribers', 0) > 100,
                    last_post_date=None
                )
                
        except Exception as e:
            print(f"Validation failed for r/{subreddit_name}: {e}")
            return None
    
    async def _estimate_posts_per_day(
        self, 
        client: httpx.AsyncClient, 
        subreddit_name: str
    ) -> float:
        """Estimate posts per day by checking recent posts."""
        try:
            response = await client.get(
                f"{self.REDDIT_BASE}/r/{subreddit_name}/new.json?limit=25"
            )
            
            if response.status_code != 200:
                return 0
            
            posts = response.json().get('data', {}).get('children', [])
            if len(posts) < 2:
                return 0
            
            # Get time range of posts
            first_time = posts[0]['data']['created_utc']
            last_time = posts[-1]['data']['created_utc']
            
            time_diff_hours = (first_time - last_time) / 3600
            if time_diff_hours <= 0:
                return 0
            
            posts_per_hour = len(posts) / time_diff_hours
            return round(posts_per_hour * 24, 1)
            
        except Exception:
            return 0
    
    async def validate_batch(
        self, 
        subreddit_names: List[str]
    ) -> List[SubredditStats]:
        """Validate multiple subreddits."""
        results = []
        for name in subreddit_names:
            stats = await self.validate(name)
            if stats and stats.is_active and not stats.is_nsfw:
                results.append(stats)
        return results
```

---

## 3.2 Background Refresh Job

### File: `radar/jobs/subreddit_refresh.py`

```python
"""
Background job to refresh subreddit statistics.
Run periodically (e.g., weekly) to keep data fresh.
"""

import asyncio
import sqlite3
from datetime import datetime
from radar.services.subreddit_validator import SubredditValidator


async def refresh_subreddit_stats(db_path: str = "data/radar.db"):
    """Refresh stats for all subreddits in database."""
    
    validator = SubredditValidator()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all subreddits
    cursor.execute('SELECT name FROM subreddit_index')
    subreddits = [row[0] for row in cursor.fetchall()]
    
    print(f"Refreshing {len(subreddits)} subreddits...")
    
    for i, name in enumerate(subreddits):
        try:
            stats = await validator.validate(name)
            
            if stats:
                cursor.execute('''
                    UPDATE subreddit_index
                    SET subscribers = ?,
                        posts_per_day = ?,
                        is_active = ?,
                        last_updated = ?
                    WHERE name = ?
                ''', (
                    stats.subscribers,
                    stats.posts_per_day,
                    stats.is_active,
                    datetime.now().isoformat(),
                    name
                ))
            else:
                # Mark as inactive if validation failed
                cursor.execute('''
                    UPDATE subreddit_index
                    SET is_active = FALSE, last_updated = ?
                    WHERE name = ?
                ''', (datetime.now().isoformat(), name))
            
            # Rate limit: 1 request per 2 seconds
            await asyncio.sleep(2)
            
            if (i + 1) % 10 == 0:
                print(f"Progress: {i + 1}/{len(subreddits)}")
                conn.commit()
                
        except Exception as e:
            print(f"Error refreshing r/{name}: {e}")
    
    conn.commit()
    conn.close()
    print("Refresh complete!")


if __name__ == "__main__":
    asyncio.run(refresh_subreddit_stats())
```

---

# PHASE 4: Competitor Intelligence (Future)

**Duration**: 1-2 weeks
**Goal**: Deep competitor analysis and differentiation suggestions

## 4.1 Concept

```python
@dataclass
class CompetitorAnalysis:
    """Analysis of a competitor product."""
    name: str
    url: str
    description: str
    key_features: List[str]
    pricing: Optional[str]
    weaknesses: List[str]  # From reviews, complaints
    differentiation_angles: List[str]  # How to position against them


class CompetitorIntelligence:
    """
    Analyzes competitors to find differentiation angles.
    
    Future capabilities:
    1. Extract competitor features from their website
    2. Find Reddit complaints about competitors
    3. Suggest response angles when someone mentions competitor
    4. Generate comparison content
    """
    
    async def analyze_competitor(self, url: str) -> CompetitorAnalysis:
        # Extract competitor info
        content = await self.extractor.extract(url)
        
        # Find complaints on Reddit
        complaints = await self.find_reddit_complaints(content.name)
        
        # Generate differentiation angles
        angles = await self.generate_angles(content, complaints)
        
        return CompetitorAnalysis(...)
```

---

# Implementation Checklist

## Phase 1: URL Extraction (Days 1-2)

### Backend
- [ ] Create `radar/services/url_extractor.py`
- [ ] Create `radar/services/product_extractor.py`
- [ ] Add `/api/extract/url` endpoint
- [ ] Add error handling for failed fetches
- [ ] Add rate limiting for extraction endpoint
- [ ] Write tests for extractor

### Frontend
- [ ] Update `ProductModal.jsx` with Quick Setup section
- [ ] Add extraction loading state
- [ ] Add success/error feedback
- [ ] Auto-fill form fields on extraction
- [ ] Style the extraction UI

### Testing
- [ ] Test with 10+ different product URLs
- [ ] Test with competitor URLs
- [ ] Test error cases (invalid URL, timeout, etc.)

---

## Phase 2: Subreddit Suggestions (Days 3-5)

### Database
- [ ] Create `subreddit_index` table
- [ ] Import initial subreddit database (see separate file)
- [ ] Add indexes for performance

### Backend
- [ ] Create `radar/services/subreddit_suggester.py`
- [ ] Add `/api/extract/subreddits/suggest` endpoint
- [ ] Implement category matching
- [ ] Implement keyword matching

### Frontend
- [ ] Add suggestions section to ProductModal
- [ ] Show subreddit stats (members, activity)
- [ ] Add "Add" button for each suggestion
- [ ] Visual feedback when added

### Testing
- [ ] Test suggestions for each category
- [ ] Verify no duplicate suggestions
- [ ] Test with empty categories

---

## Phase 3: Live Validation (Week 2)

### Backend
- [ ] Create `radar/services/subreddit_validator.py`
- [ ] Implement Reddit stats fetching
- [ ] Add caching layer
- [ ] Create background refresh job

### Integration
- [ ] Validate suggestions before showing
- [ ] Show real-time stats in UI
- [ ] Filter out inactive/NSFW subreddits

### Maintenance
- [ ] Set up weekly refresh job
- [ ] Add monitoring for failed validations

---

## Phase 4: Competitor Intelligence (Future)

- [ ] Multi-URL input support
- [ ] Competitor feature extraction
- [ ] Reddit complaint mining
- [ ] Differentiation angle generation
- [ ] Response templates based on competitor mentions

---

# Cost Estimates

| Phase | Component | Cost per Request |
|-------|-----------|------------------|
| 1 | Website fetch | ~$0 |
| 1 | LLM extraction (gpt-4o-mini) | ~$0.002 |
| 2 | Database lookup | ~$0 |
| 3 | Reddit validation (10 subs) | ~$0 |
| **Total per product setup** | | **~$0.002** |

---

# Success Metrics

| Metric | Target |
|--------|--------|
| Extraction success rate | >90% |
| Time to first suggestion | <5 seconds |
| Subreddit relevance (user keeps >50%) | >70% |
| Complete setup time reduction | 5 min → 1 min |

---

*Document Version: 1.0*
*Created: January 2026*