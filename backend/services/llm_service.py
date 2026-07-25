"""
Arbiter AI — LLM Service
Abstraction over multiple LLM providers (Gemini, Groq) with retry logic,
rate limiting, and multi-model consensus support.
"""

import asyncio
import json
import time
import traceback
from config import settings


class LLMProvider:
    """Base interface for LLM providers."""
    
    def __init__(self, name: str):
        self.name = name
        self.last_call_time = 0
        self.call_count = 0
    
    async def generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
        raise NotImplementedError


class GeminiProvider(LLMProvider):
    """Google Gemini API provider."""
    
    def __init__(self):
        super().__init__("gemini")
        self.client = None
        self.model = settings.GEMINI_MODEL
        self.min_interval = 60.0 / settings.GEMINI_RPM  # Seconds between calls
    
    def _ensure_client(self):
        if self.client is None:
            from google import genai
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    async def generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
        self._ensure_client()
        
        # Rate limiting
        now = time.time()
        elapsed = now - self.last_call_time
        if elapsed < self.min_interval:
            await asyncio.sleep(self.min_interval - elapsed)
        
        try:
            from google.genai import types
            
            config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=4096,
            )
            if system_prompt:
                config.system_instruction = system_prompt
            
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=prompt,
                config=config,
            )
            
            self.last_call_time = time.time()
            self.call_count += 1
            
            return response.text or ""
        except Exception as e:
            print(f"[ERROR] Gemini error: {e}")
            traceback.print_exc()
            raise


class GroqProvider(LLMProvider):
    """Groq API provider (LLaMA models)."""
    
    def __init__(self):
        super().__init__("groq")
        self.client = None
        self.model = settings.GROQ_MODEL
        self.min_interval = 60.0 / settings.GROQ_RPM
    
    def _ensure_client(self):
        if self.client is None:
            from groq import Groq
            self.client = Groq(api_key=settings.GROQ_API_KEY)
    
    async def generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
        self._ensure_client()
        
        # Rate limiting
        now = time.time()
        elapsed = now - self.last_call_time
        if elapsed < self.min_interval:
            await asyncio.sleep(self.min_interval - elapsed)
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=4096,
            )
            
            self.last_call_time = time.time()
            self.call_count += 1
            
            return response.choices[0].message.content or ""
        except Exception as e:
            print(f"[ERROR] Groq error: {e}")
            traceback.print_exc()
            raise


class LLMService:
    """
    Unified LLM service that manages multiple providers.
    Supports single-provider calls and multi-model consensus.
    """
    
    def __init__(self):
        self.providers: dict[str, LLMProvider] = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available providers based on API keys."""
        if settings.has_gemini:
            self.providers["gemini"] = GeminiProvider()
            print("[OK] Gemini provider initialized")
        
        if settings.has_groq:
            self.providers["groq"] = GroqProvider()
            print("[OK] Groq provider initialized")
        
        if not self.providers:
            print("[WARNING] No LLM providers configured! Set GEMINI_API_KEY or GROQ_API_KEY")
    
    @property
    def primary_provider(self) -> str:
        """Get the primary provider name."""
        if "gemini" in self.providers:
            return "gemini"
        if "groq" in self.providers:
            return "groq"
        raise RuntimeError("No LLM providers available")
    
    @property
    def available_providers(self) -> list[str]:
        """Get list of available provider names."""
        return list(self.providers.keys())
    
    async def generate(
        self, 
        prompt: str, 
        system_prompt: str = "",
        provider: str | None = None,
        temperature: float = 0.7,
        retries: int = 3,
        retry_delay: float = 2.0
    ) -> str:
        """
        Generate text using a single provider.
        Falls back to other providers on failure.
        """
        provider_name = provider or self.primary_provider
        
        for attempt in range(retries):
            try:
                if provider_name in self.providers:
                    result = await self.providers[provider_name].generate(
                        prompt, system_prompt, temperature
                    )
                    return result
                else:
                    # Fall back to any available provider
                    for fallback_name, fallback_provider in self.providers.items():
                        try:
                            result = await fallback_provider.generate(
                                prompt, system_prompt, temperature
                            )
                            return result
                        except Exception:
                            continue
                    raise RuntimeError(f"No providers available (requested: {provider_name})")
            except Exception as e:
                if attempt < retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    print(f"[WARNING] LLM call failed (attempt {attempt + 1}/{retries}), retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                    # Try a different provider on retry
                    other_providers = [p for p in self.providers.keys() if p != provider_name]
                    if other_providers:
                        provider_name = other_providers[0]
                else:
                    raise
        
        raise RuntimeError("All LLM generation attempts failed")
    
    async def generate_json(
        self,
        prompt: str,
        system_prompt: str = "",
        provider: str | None = None,
        temperature: float = 0.3,
        retries: int = 3
    ) -> dict | list:
        """
        Generate structured JSON output.
        Automatically parses the response and retries on parse failure.
        """
        json_system = (system_prompt + "\n\n" if system_prompt else "")
        json_system += "IMPORTANT: Respond with ONLY valid JSON. No markdown, no code blocks, no explanations. Just the raw JSON."
        
        for attempt in range(retries):
            try:
                raw = await self.generate(prompt, json_system, provider, temperature)
                # Clean the response
                cleaned = raw.strip()
                # Remove markdown code blocks if present
                if cleaned.startswith("```"):
                    lines = cleaned.split("\n")
                    # Remove first and last lines (```json and ```)
                    lines = [l for l in lines if not l.strip().startswith("```")]
                    cleaned = "\n".join(lines)
                
                return json.loads(cleaned)
            except json.JSONDecodeError as e:
                if attempt < retries - 1:
                    print(f"[WARNING] JSON parse failed (attempt {attempt + 1}), retrying: {e}")
                    await asyncio.sleep(1)
                else:
                    print(f"[ERROR] JSON parse failed after {retries} attempts. Raw: {raw[:200]}")
                    # Return a safe default
                    return {}
    
    async def multi_model_generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.3
    ) -> dict[str, str]:
        """
        Send the same prompt to all available providers simultaneously.
        Returns a dict of {provider_name: response}.
        """
        if len(self.providers) < 2 and settings.ENABLE_MULTI_MODEL:
            # If only one provider, still return its result
            provider_name = self.primary_provider
            result = await self.generate(prompt, system_prompt, provider_name, temperature)
            return {provider_name: result}
        
        tasks = {}
        for name, provider in self.providers.items():
            tasks[name] = asyncio.create_task(
                provider.generate(prompt, system_prompt, temperature)
            )
        
        results = {}
        for name, task in tasks.items():
            try:
                results[name] = await task
            except Exception as e:
                print(f"[WARNING] Provider {name} failed in multi-model: {e}")
                results[name] = ""
        
        return results
    
    async def multi_model_consensus(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.3
    ) -> list[dict]:
        """
        Get structured verdicts from all models for consensus voting.
        Each model returns {verdict, confidence, reasoning}.
        """
        consensus_prompt = prompt + """

Respond with ONLY valid JSON in this exact format:
{
    "verdict": "verified" or "disputed" or "uncertain",
    "confidence": <number 0-100>,
    "reasoning": "<brief explanation>"
}"""
        
        raw_results = await self.multi_model_generate(
            consensus_prompt, system_prompt, temperature
        )
        
        votes = []
        for provider_name, raw_response in raw_results.items():
            try:
                cleaned = raw_response.strip()
                if cleaned.startswith("```"):
                    lines = cleaned.split("\n")
                    lines = [l for l in lines if not l.strip().startswith("```")]
                    cleaned = "\n".join(lines)
                
                parsed = json.loads(cleaned)
                votes.append({
                    "provider": provider_name,
                    "model": self.providers[provider_name].model if provider_name in self.providers else "unknown",
                    "verdict": parsed.get("verdict", "uncertain"),
                    "confidence": float(parsed.get("confidence", 50)),
                    "reasoning": parsed.get("reasoning", "")
                })
            except (json.JSONDecodeError, ValueError, AttributeError) as e:
                print(f"[WARNING] Failed to parse consensus from {provider_name}: {e}")
                votes.append({
                    "provider": provider_name,
                    "model": "unknown",
                    "verdict": "uncertain",
                    "confidence": 50,
                    "reasoning": f"Failed to parse response: {str(e)[:100]}"
                })
        
        return votes


# Singleton instance
llm_service = LLMService()
