"""
Arbiter AI — Search Service
Web search via DuckDuckGo and Wikipedia for source gathering.
No API keys required — completely free.
"""

import asyncio
import re
from urllib.parse import urlparse
from config import settings


class SearchService:
    """Handles web searching via DuckDuckGo and Wikipedia."""
    
    def __init__(self):
        self.search_delay = settings.SEARCH_DELAY_SECONDS
    
    async def search_web(self, query: str, max_results: int = 8) -> list[dict]:
        """
        Search the web using DuckDuckGo.
        Returns list of {title, url, snippet, domain}.
        """
        try:
            from duckduckgo_search import DDGS
            
            results = await asyncio.to_thread(
                self._do_ddg_search, query, max_results
            )
            
            # Add delay to be respectful
            await asyncio.sleep(self.search_delay)
            
            return results
        except Exception as e:
            print(f"⚠️ DuckDuckGo search failed: {e}")
            return []
    
    def _do_ddg_search(self, query: str, max_results: int) -> list[dict]:
        """Synchronous DuckDuckGo search."""
        from duckduckgo_search import DDGS
        
        results = []
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    domain = urlparse(r.get("href", "")).netloc
                    results.append({
                        "title": r.get("title", ""),
                        "url": r.get("href", ""),
                        "snippet": r.get("body", ""),
                        "domain": domain
                    })
        except Exception as e:
            print(f"⚠️ DDG search error: {e}")
        
        return results
    
    async def search_news(self, query: str, max_results: int = 5) -> list[dict]:
        """
        Search recent news using DuckDuckGo News.
        Returns list of {title, url, snippet, domain, date}.
        """
        try:
            results = await asyncio.to_thread(
                self._do_ddg_news_search, query, max_results
            )
            await asyncio.sleep(self.search_delay)
            return results
        except Exception as e:
            print(f"⚠️ DuckDuckGo news search failed: {e}")
            return []
    
    def _do_ddg_news_search(self, query: str, max_results: int) -> list[dict]:
        """Synchronous DuckDuckGo news search."""
        from duckduckgo_search import DDGS
        
        results = []
        try:
            with DDGS() as ddgs:
                for r in ddgs.news(query, max_results=max_results):
                    domain = urlparse(r.get("url", "")).netloc
                    results.append({
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "snippet": r.get("body", ""),
                        "domain": domain,
                        "date": r.get("date", "")
                    })
        except Exception as e:
            print(f"⚠️ DDG news error: {e}")
        
        return results
    
    async def search_wikipedia(self, query: str) -> dict | None:
        """
        Search Wikipedia for a topic.
        Returns {title, url, summary, content} or None.
        """
        try:
            import httpx
            
            # Use Wikipedia API
            params = {
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": query,
                "srlimit": 3,
                "utf8": 1
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://en.wikipedia.org/w/api.php",
                    params=params,
                    timeout=10
                )
                data = response.json()
            
            search_results = data.get("query", {}).get("search", [])
            if not search_results:
                return None
            
            # Get the top result's content
            page_title = search_results[0]["title"]
            page_snippet = search_results[0].get("snippet", "")
            # Clean HTML from snippet
            page_snippet = re.sub(r'<[^>]+>', '', page_snippet)
            
            # Get full page summary
            summary_params = {
                "action": "query",
                "format": "json",
                "titles": page_title,
                "prop": "extracts",
                "exintro": True,
                "explaintext": True,
                "exsectionformat": "plain"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://en.wikipedia.org/w/api.php",
                    params=summary_params,
                    timeout=10
                )
                summary_data = response.json()
            
            pages = summary_data.get("query", {}).get("pages", {})
            page_content = ""
            for page_id, page_info in pages.items():
                if page_id != "-1":
                    page_content = page_info.get("extract", page_snippet)
                    break
            
            return {
                "title": page_title,
                "url": f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}",
                "summary": page_content[:1000] if page_content else page_snippet,
                "domain": "en.wikipedia.org"
            }
        except Exception as e:
            print(f"⚠️ Wikipedia search failed: {e}")
            return None
    
    async def fetch_page_content(self, url: str, max_chars: int = 3000) -> str:
        """
        Fetch and extract text content from a URL.
        Returns cleaned text content.
        """
        try:
            import httpx
            from bs4 import BeautifulSoup
            
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(
                    url,
                    timeout=10,
                    headers={
                        "User-Agent": "ArbiterAI/1.0 (Research Bot)"
                    }
                )
                response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove scripts, styles, nav, footer
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()
            
            # Get text
            text = soup.get_text(separator="\n", strip=True)
            
            # Clean up whitespace
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            text = "\n".join(lines)
            
            return text[:max_chars]
        except Exception as e:
            print(f"⚠️ Failed to fetch {url}: {e}")
            return ""
    
    async def comprehensive_search(self, query: str, max_results: int = 8) -> list[dict]:
        """
        Perform comprehensive search across web and Wikipedia.
        Deduplicates results by domain.
        """
        # Run web search and Wikipedia search concurrently
        web_task = asyncio.create_task(self.search_web(query, max_results))
        wiki_task = asyncio.create_task(self.search_wikipedia(query))
        news_task = asyncio.create_task(self.search_news(query, 3))
        
        web_results = await web_task
        wiki_result = await wiki_task
        news_results = await news_task
        
        all_results = []
        seen_domains = set()
        
        # Add Wikipedia first (high credibility)
        if wiki_result:
            all_results.append(wiki_result)
            seen_domains.add("en.wikipedia.org")
        
        # Add web results, deduplicating by domain
        for result in web_results:
            domain = result.get("domain", "")
            if domain and domain not in seen_domains:
                all_results.append(result)
                seen_domains.add(domain)
        
        # Add news results
        for result in news_results:
            domain = result.get("domain", "")
            if domain and domain not in seen_domains:
                all_results.append(result)
                seen_domains.add(domain)
        
        return all_results[:max_results + 3]  # Allow a few extra for Wikipedia + news


# Singleton instance
search_service = SearchService()
