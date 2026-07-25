"""
Arbiter AI — Source Credibility Service
Dynamic credibility scoring engine that ranks sources based on
domain authority, content signals, and cross-reference data.
"""

from urllib.parse import urlparse


# ─── Domain Authority Tiers ──────────────────────────────────────────
# These are configurable — not hardcoded scores, but tier classifications
# that feed into a formula. Scores are computed dynamically.

TIER_1_DOMAINS = {
    # Academic & Government
    ".gov", ".edu", ".ac.uk", ".gov.uk", ".europa.eu",
    # Major wire services & established news
    "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk",
    "nature.com", "science.org", "sciencedirect.com",
    "who.int", "un.org", "worldbank.org",
    "nih.gov", "cdc.gov", "nasa.gov",
    "pubmed.ncbi.nlm.nih.gov", "scholar.google.com",
    "ieee.org", "acm.org", "arxiv.org",
    "nytimes.com", "washingtonpost.com", "theguardian.com",
    "economist.com", "ft.com",
}

TIER_2_DOMAINS = {
    # Major publications & encyclopedias
    "wikipedia.org", "en.wikipedia.org", "britannica.com",
    "cnn.com", "nbcnews.com", "abcnews.go.com", "cbsnews.com",
    "forbes.com", "bloomberg.com", "cnbc.com",
    "techcrunch.com", "wired.com", "arstechnica.com",
    "scientificamerican.com", "nationalgeographic.com",
    "smithsonianmag.com", "pbs.org", "npr.org",
    "snopes.com", "factcheck.org", "politifact.com",
    "stackoverflow.com", "github.com",
    "statista.com", "pewresearch.org",
}

TIER_3_DOMAINS = {
    # Blogs, forums, social media
    "medium.com", "substack.com", "wordpress.com",
    "reddit.com", "quora.com",
    "youtube.com", "tiktok.com",
    "twitter.com", "x.com", "facebook.com",
    "buzzfeed.com", "huffpost.com",
}

# Base scores per tier
TIER_SCORES = {
    "TIER_1": 90,
    "TIER_2": 72,
    "TIER_3": 45,
    "UNKNOWN": 30,
}


class CredibilityService:
    """Scores source credibility based on multiple signals."""
    
    def score_source(self, url: str, title: str = "", snippet: str = "") -> dict:
        """
        Calculate credibility score for a source.
        Returns {credibility_score, credibility_tier, signals}.
        """
        domain = self._extract_domain(url)
        
        # 1. Domain tier scoring (50% weight)
        tier = self._get_domain_tier(domain)
        domain_score = TIER_SCORES[tier]
        
        # 2. Content signals (30% weight)
        content_signals = self._analyze_content_signals(title, snippet, url)
        content_score = self._calculate_content_score(content_signals)
        
        # 3. URL structure signals (20% weight)
        url_score = self._analyze_url_structure(url)
        
        # Weighted combination
        final_score = (domain_score * 0.5) + (content_score * 0.3) + (url_score * 0.2)
        final_score = max(0, min(100, final_score))
        
        return {
            "credibility_score": round(final_score, 1),
            "credibility_tier": tier,
            "signals": {
                "domain_authority": domain_score,
                "content_quality": round(content_score, 1),
                "url_structure": round(url_score, 1),
                **content_signals
            }
        }
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Remove www. prefix
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except Exception:
            return ""
    
    def _get_domain_tier(self, domain: str) -> str:
        """Determine the credibility tier of a domain."""
        if not domain:
            return "UNKNOWN"
        
        # Check exact domain match
        if domain in TIER_1_DOMAINS:
            return "TIER_1"
        if domain in TIER_2_DOMAINS:
            return "TIER_2"
        if domain in TIER_3_DOMAINS:
            return "TIER_3"
        
        # Check TLD-based tiers
        for tld in [".gov", ".edu", ".ac.uk", ".gov.uk"]:
            if domain.endswith(tld):
                return "TIER_1"
        
        # Check if it's a subdomain of a known domain
        for known_domain in TIER_1_DOMAINS:
            if not known_domain.startswith(".") and domain.endswith("." + known_domain):
                return "TIER_1"
        for known_domain in TIER_2_DOMAINS:
            if not known_domain.startswith(".") and domain.endswith("." + known_domain):
                return "TIER_2"
        
        return "UNKNOWN"
    
    def _analyze_content_signals(self, title: str, snippet: str, url: str) -> dict:
        """Analyze content quality signals from title and snippet."""
        text = f"{title} {snippet}".lower()
        
        signals = {
            "has_specific_data": False,
            "has_hedging_language": False,
            "has_sensational_language": False,
            "has_citations_mentioned": False,
            "has_date_reference": False,
        }
        
        # Check for specific data (numbers, percentages, dates)
        import re
        if re.search(r'\d+\.?\d*\s*(%|percent|million|billion|trillion)', text):
            signals["has_specific_data"] = True
        
        # Check for hedging language (indicates nuance — positive signal)
        hedging_words = ["may", "might", "suggests", "indicates", "according to", 
                         "research shows", "studies suggest", "evidence indicates"]
        if any(word in text for word in hedging_words):
            signals["has_hedging_language"] = True
        
        # Check for sensational language (negative signal)
        sensational_words = ["shocking", "unbelievable", "you won't believe", 
                            "mind-blowing", "insane", "crazy", "destroyed",
                            "slammed", "blasted", "bombshell", "exposed"]
        if any(word in text for word in sensational_words):
            signals["has_sensational_language"] = True
        
        # Check for citation mentions
        citation_words = ["study", "research", "journal", "published", "peer-reviewed",
                         "university", "professor", "dr.", "report", "survey"]
        if any(word in text for word in citation_words):
            signals["has_citations_mentioned"] = True
        
        # Check for date references
        if re.search(r'(20\d{2}|19\d{2}|january|february|march|april|may|june|july|august|september|october|november|december)', text):
            signals["has_date_reference"] = True
        
        return signals
    
    def _calculate_content_score(self, signals: dict) -> float:
        """Calculate content quality score from signals."""
        score = 50  # Base score
        
        if signals.get("has_specific_data"):
            score += 15
        if signals.get("has_hedging_language"):
            score += 10
        if signals.get("has_sensational_language"):
            score -= 20
        if signals.get("has_citations_mentioned"):
            score += 15
        if signals.get("has_date_reference"):
            score += 10
        
        return max(0, min(100, score))
    
    def _analyze_url_structure(self, url: str) -> float:
        """Score URL structure for credibility signals."""
        score = 50
        
        try:
            parsed = urlparse(url)
            path = parsed.path.lower()
            
            # HTTPS is expected
            if parsed.scheme == "https":
                score += 10
            
            # Academic/research paths
            research_paths = ["/research", "/study", "/paper", "/article", 
                            "/report", "/publication", "/journal"]
            if any(p in path for p in research_paths):
                score += 15
            
            # Blog/opinion paths (slightly lower)
            blog_paths = ["/blog", "/opinion", "/editorial", "/comment"]
            if any(p in path for p in blog_paths):
                score -= 10
            
            # Very long URLs with many parameters often indicate low quality
            if len(url) > 200:
                score -= 5
            
            # Has meaningful path segments (not just a root page)
            segments = [s for s in path.split("/") if s]
            if len(segments) >= 2:
                score += 5  # More specific content
            
        except Exception:
            pass
        
        return max(0, min(100, score))
    
    def get_tier_label(self, tier: str) -> str:
        """Get human-readable label for a tier."""
        labels = {
            "TIER_1": "Highly Credible",
            "TIER_2": "Credible",
            "TIER_3": "Low Credibility",
            "UNKNOWN": "Unknown Credibility"
        }
        return labels.get(tier, "Unknown")


# Singleton instance
credibility_service = CredibilityService()
