"""
Multi-provider LLM adapter with key rotation and resilient JSON extraction.
Supports Groq, Cerebras, OpenRouter, and Google Gemini with automatic failover.
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any, List, Optional

from brain_core.config import Config

log = logging.getLogger("brain_core.llm")


def clean_json_array(text: str) -> list[dict]:
    """Cleans markdown fences or surrounding commentary and parses JSON array.

    Resilient against:
    - Conversational text before/after markdown fences
    - Trailing commas before closing brackets
    - Truncated arrays (extracts completed individual JSON objects via brace tracking)
    - Single-quoted JSON or unescaped characters
    """
    if not text:
        return []

    # 1. Strip markdown code fences if present
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    cleaned = fence_match.group(1).strip() if fence_match else text.strip()

    # 2. Strip trailing commas before closing brackets/braces
    cleaned_no_commas = re.sub(r",\s*([\]}])", r"\1", cleaned)

    # 3. Direct parse attempt
    try:
        data = json.loads(cleaned_no_commas)
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        elif isinstance(data, dict):
            return [data]
    except (json.JSONDecodeError, ValueError):
        pass

    # 4. Regex array extraction attempt
    match = re.search(r"\[\s*\{[\s\S]*\}\s*\]", cleaned_no_commas)
    if match:
        try:
            data = json.loads(match.group(0))
            if isinstance(data, list):
                return [item for item in data if isinstance(item, dict)]
        except Exception:
            pass

    # 5. Resilient individual JSON object extractor (balanced-brace parsing)
    results: list[dict] = []
    brace_depth = 0
    start_idx = -1
    for idx, ch in enumerate(cleaned):
        if ch == "{":
            if brace_depth == 0:
                start_idx = idx
            brace_depth += 1
        elif ch == "}":
            if brace_depth > 0:
                brace_depth -= 1
                if brace_depth == 0 and start_idx != -1:
                    chunk = cleaned[start_idx : idx + 1]
                    try:
                        chunk_clean = re.sub(r",\s*([\]}])", r"\1", chunk)
                        item = json.loads(chunk_clean)
                        if isinstance(item, dict) and "expression" in item:
                            results.append(item)
                    except Exception:
                        try:
                            item = json.loads(chunk.replace("'", '"'))
                            if isinstance(item, dict) and "expression" in item:
                                results.append(item)
                        except Exception:
                            pass
                    start_idx = -1

    if results:
        log.info("Recovered %d candidate objects via resilient brace parser.", len(results))
        return results

    log.warning("clean_json_array: Failed to parse or recover any JSON objects from response (length=%d).", len(text))
    return []


class LLMAdapter:
    """Stateful round-robin multi-provider LLM adapter."""

    def __init__(self, config: Config):
        self.config = config
        self._key_indices = {
            "groq": 0,
            "cerebras": 0,
            "openrouter": 0,
            "gemini": 0,
        }

    def _rotate_keys(self, provider: str, keys: list[str]) -> list[str]:
        if not keys:
            return []
        start_idx = self._key_indices.get(provider, 0) % len(keys)
        self._key_indices[provider] = (start_idx + 1) % len(keys)
        return keys[start_idx:] + keys[:start_idx]

    def _call_openai_compatible(
        self, base_url: str, api_key: str, model: str, prompt: str, system_prompt: str, temperature: float = 0.7
    ) -> Optional[str]:
        try:
            from openai import OpenAI
            client = OpenAI(base_url=base_url, api_key=api_key, timeout=25.0, max_retries=0)
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
            )
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content.strip()
        except Exception as e:
            log.warning("Call to %s (%s) failed: %s", base_url, model, e)
        return None

    def _call_gemini(
        self, api_key: str, model: str, prompt: str, system_prompt: str, temperature: float = 0.7
    ) -> Optional[str]:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            full_prompt = f"{system_prompt}\n\nUser Task:\n{prompt}"
            resp = client.models.generate_content(
                model=model,
                contents=full_prompt,
                config={"temperature": temperature},
            )
            if resp and resp.text:
                return resp.text.strip()
        except ImportError:
            pass
        except Exception as e:
            log.warning("Native Gemini call failed (%s): %s", model, e)

        return self._call_openai_compatible(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=api_key,
            model=model,
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
        )

    async def generate_async(self, prompt: str, system_prompt: str, temperature: float = 0.7) -> Optional[str]:
        """Asynchronous wrapper that offloads synchronous HTTP generation to a worker thread."""
        return await asyncio.to_thread(self.generate, prompt, system_prompt, temperature)

    def generate(self, prompt: str, system_prompt: str, temperature: float = 0.7) -> Optional[str]:
        """Tries configured providers sequentially with stateful round-robin key rotation."""
        # 1. Groq
        for key in self._rotate_keys("groq", self.config.groq_keys):
            for model in [
                "qwen/qwen3.8-27b",
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
            ]:
                res = self._call_openai_compatible(
                    base_url="https://api.groq.com/openai/v1",
                    api_key=key,
                    model=model,
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                )
                if res:
                    return res

        # 2. Cerebras
        for key in self._rotate_keys("cerebras", self.config.cerebras_keys):
            for model in ["llama-3.3-70b", "llama3.1-70b", "llama3.1-8b"]:
                res = self._call_openai_compatible(
                    base_url="https://api.cerebras.ai/v1",
                    api_key=key,
                    model=model,
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                )
                if res:
                    return res

        # 3. OpenRouter
        for key in self._rotate_keys("openrouter", self.config.openrouter_keys):
            for model in [
                "meta-llama/llama-3.3-70b-instruct",
                "meta-llama/llama-3.2-3b-instruct:free",
                "google/gemini-2.0-flash-exp:free",
                "qwen/qwen-2.5-72b-instruct",
                "mistralai/mistral-small-24b-instruct-2501:free",
            ]:
                res = self._call_openai_compatible(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=key,
                    model=model,
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                )
                if res:
                    return res

        # 4. Google Gemini
        for key in self._rotate_keys("gemini", self.config.gemini_keys):
            for model in ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]:
                res = self._call_gemini(
                    api_key=key,
                    model=model,
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                )
                if res:
                    return res

        log.error("All LLM providers and keys failed for generation request.")
        return None
