"""
URL Extractor Service - Fetches and parses website content for product extraction.
"""
import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
import re

class WebsiteExtractor:
    """Extracts relevant content from a product website URL."""
    
    # Common boilerplate patterns to filter out
    BOILERPLATE_PATTERNS = [
        r'cookie', r'privacy policy', r'terms of service', r'terms and conditions',
        r'accept all', r'subscribe to', r'newsletter', r'©\s*\d{4}',
        r'all rights reserved', r'follow us', r'social media'
    ]
    
    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout
        # Simplified headers - let httpx handle encoding automatically
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
    
    async def extract(self, url: str) -> Dict[str, Any]:
        """
        Fetch URL and extract relevant content.
        
        Returns:
            Dict containing: title, meta_description, og_tags, h1, h2s, hero_text, features, full_text
        """
        try:
            async with httpx.AsyncClient(
                headers=self.headers, 
                timeout=self.timeout, 
                follow_redirects=True
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                # Get the text content - httpx handles encoding
                html = response.text
                
                # Check if we got valid HTML (not binary junk)
                if not html or len(html) < 100 or not any(tag in html.lower() for tag in ['<html', '<head', '<body']):
                    return {
                        "error": "Could not extract valid HTML content. The page may be using JavaScript to render content.",
                        "url": url,
                        "is_spa": True
                    }
                
                soup = BeautifulSoup(html, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                result = {
                    "url": url,
                    "title": self._get_title(soup),
                    "meta_description": self._get_meta_description(soup),
                    "og_tags": self._get_og_tags(soup),
                    "h1": self._get_h1(soup),
                    "h2s": self._get_h2s(soup),
                    "hero_text": self._get_hero_text(soup),
                    "features": self._get_features(soup),
                    "full_text": self._get_clean_text(soup),
                }
                
                return result
                
        except httpx.HTTPError as e:
            return {"error": f"HTTP Error: {str(e)}", "url": url}
        except Exception as e:
            return {"error": f"Extraction Error: {str(e)}", "url": url}
    
    def _get_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title_tag = soup.find('title')
        if title_tag:
            # Clean up common suffixes like " | Company Name"
            title = title_tag.get_text().strip()
            # Remove everything after common separators
            for sep in [' | ', ' - ', ' — ', ' :: ']:
                if sep in title:
                    title = title.split(sep)[0].strip()
            return title
        return ""
    
    def _get_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description."""
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta and meta.get('content'):
            return meta['content'].strip()
        return ""
    
    def _get_og_tags(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract Open Graph tags."""
        og_tags = {}
        for meta in soup.find_all('meta', property=lambda x: x and x.startswith('og:')):
            key = meta.get('property', '').replace('og:', '')
            value = meta.get('content', '')
            if key and value:
                og_tags[key] = value
        return og_tags
    
    def _get_h1(self, soup: BeautifulSoup) -> str:
        """Extract first H1."""
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        return ""
    
    def _get_h2s(self, soup: BeautifulSoup) -> list:
        """Extract all H2s (often feature sections)."""
        h2s = []
        for h2 in soup.find_all('h2'):
            text = h2.get_text().strip()
            if text and len(text) < 200 and not self._is_boilerplate(text):
                h2s.append(text)
        return h2s[:10]  # Limit to 10
    
    def _get_hero_text(self, soup: BeautifulSoup) -> str:
        """
        Extract hero section text (usually the main value proposition).
        Look for large text near the top of the page.
        """
        # Try common hero patterns
        hero_selectors = [
            '.hero', '.hero-section', '.banner', '.jumbotron',
            '[class*="hero"]', '[class*="banner"]',
            'main > section:first-child', '.landing'
        ]
        
        for selector in hero_selectors:
            hero = soup.select_one(selector)
            if hero:
                text = hero.get_text(separator=' ', strip=True)
                if len(text) > 50:
                    return text[:500]
        
        # Fallback: get first large paragraph
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if len(text) > 100 and not self._is_boilerplate(text):
                return text[:500]
        
        return ""
    
    def _get_features(self, soup: BeautifulSoup) -> list:
        """Extract feature list items."""
        features = []
        
        # Look for common feature list patterns
        feature_selectors = [
            '.features li', '.feature-list li', '[class*="feature"] li',
            '.benefits li', '[class*="benefit"] li',
            'ul.checklist li', '.checklist li'
        ]
        
        for selector in feature_selectors:
            items = soup.select(selector)
            for item in items:
                text = item.get_text().strip()
                if text and len(text) < 200 and not self._is_boilerplate(text):
                    features.append(text)
        
        # Deduplicate and limit
        return list(dict.fromkeys(features))[:15]
    
    def _get_clean_text(self, soup: BeautifulSoup) -> str:
        """Get clean body text, filtered of boilerplate."""
        text = soup.get_text(separator='\n', strip=True)
        
        # Split into lines and filter
        lines = text.split('\n')
        clean_lines = []
        
        for line in lines:
            line = line.strip()
            if len(line) < 10:
                continue
            if self._is_boilerplate(line):
                continue
            clean_lines.append(line)
        
        # Join and truncate
        full_text = '\n'.join(clean_lines)
        return full_text[:5000]  # Limit to ~5k chars
    
    def _is_boilerplate(self, text: str) -> bool:
        """Check if text is likely boilerplate content."""
        text_lower = text.lower()
        for pattern in self.BOILERPLATE_PATTERNS:
            if re.search(pattern, text_lower):
                return True
        return False


# Synchronous wrapper for easy use
def extract_website_sync(url: str) -> Dict[str, Any]:
    """Synchronous wrapper for website extraction."""
    import asyncio
    extractor = WebsiteExtractor()
    return asyncio.run(extractor.extract(url))
