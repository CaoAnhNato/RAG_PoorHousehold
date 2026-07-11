# -*- coding: utf-8 -*-
"""
Module llm_helper cung cấp hàm gọi API LLM chuyên dụng.
Hỗ trợ cả đồng bộ (Sync), Bất đồng bộ (Async qua httpx) và Streaming token trực tiếp
với cơ chế retry và xử lý lỗi chuyên sâu.
"""

from __future__ import annotations
import os
import re
import json
import time
import requests
import asyncio
from typing import Any, AsyncGenerator, Generator
from dotenv import load_dotenv
from pathlib import Path

try:
    import httpx
except ImportError:
    httpx = None

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

def get_llm_config() -> dict[str, str]:
    """Lấy cấu hình kết nối LLM từ tệp .env."""
    base_url = os.environ.get("SHOPAPI_BASE_URL", "").strip()
    auth_token = os.environ.get("SHOPAPI_LLM_" + "API_" + "KEY", "").strip()
    model = os.environ.get("SHOPAPI_MODEL_LLM", "gpt-4o-mini").strip()
    
    if not auth_token:
        raise RuntimeError("Lỗi: Thiếu khóa cấu hình LLM trong tệp .env.")
    if not base_url:
        raise RuntimeError("Lỗi: Thiếu địa chỉ SHOPAPI_BASE_URL trong tệp .env.")
        
    return {
        "base_url": base_url.rstrip("/"),
        "auth_token": auth_token,
        "model": model
    }

def get_research_llm_config() -> dict[str, str]:
    """Lấy cấu hình kết nối LLM cho Deep Research (CHIASEGPU) từ tệp .env."""
    base_url = os.environ.get("CHIASEGPU_BASE_URL", "").strip()
    auth_token = os.environ.get("CHIASEGPU_API_KEY", "").strip()
    model = os.environ.get("CHIASEGPU_MODEL", "").strip()
    
    if not auth_token or not base_url:
        raise RuntimeError("Lỗi: Thiếu cấu hình CHIASEGPU_API_KEY hoặc CHIASEGPU_BASE_URL trong tệp .env cho Deep Research.")
    if not model:
        raise RuntimeError("Lỗi: Thiếu cấu hình CHIASEGPU_MODEL trong tệp .env cho Deep Research.")
        
    return {
        "base_url": base_url.rstrip("/"),
        "auth_token": auth_token,
        "model": model
    }

def _build_payload(config: dict[str, str], system_prompt: str, user_prompt: str, temperature: float, max_tokens: int, response_json: bool, stream: bool = False, model: str | None = None) -> tuple[str, dict[str, str], dict[str, Any]]:
    base = config['base_url']
    if base.endswith('/v1'):
        url = f"{base}/chat/completions"
    else:
        url = f"{base}/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {config['auth_token']}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model if model else config["model"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": stream
    }
    
    if response_json:
        payload["response_format"] = {"type": "json_object"}
        payload["messages"][1]["content"] = str(payload["messages"][1]["content"]) + "\n\nPlease output valid json."
        
    return url, headers, payload

def call_llm(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.1,
    max_tokens: int = 1500,
    response_json: bool = False,
    model: str | None = None,
    config: dict[str, str] | None = None
) -> str:
    """Gọi LLM đồng bộ với cơ chế retry."""
    if config is None:
        config = get_llm_config()
    url, headers, payload = _build_payload(config, system_prompt, user_prompt, temperature, max_tokens, response_json, stream=False, model=model)
    
    last_err = None
    for attempt in range(8):
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=60.0)
            if resp.status_code in {429, 500, 502, 503, 504}:
                time.sleep(min(2 ** attempt, 5))
                last_err = f"HTTP {resp.status_code}: {resp.text}"
                continue
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            last_err = str(e)
            time.sleep(min(2 ** attempt, 5))
            
    raise RuntimeError(f"Gọi API LLM thất bại sau 8 lần thử. Lỗi cuối: {last_err}")

async def call_llm_async(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.1,
    max_tokens: int = 1500,
    response_json: bool = False,
    model: str | None = None,
    config: dict[str, str] | None = None
) -> str:
    """Gọi LLM bất đồng bộ (Async) sử dụng httpx."""
    if httpx is None:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, call_llm, system_prompt, user_prompt, temperature, max_tokens, response_json, model, config)

    if config is None:
        config = get_llm_config()
    url, headers, payload = _build_payload(config, system_prompt, user_prompt, temperature, max_tokens, response_json, stream=False, model=model)
    
    last_err = None
    async with httpx.AsyncClient(timeout=60.0) as client:
        for attempt in range(8):
            try:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code in {429, 500, 502, 503, 504}:
                    await asyncio.sleep(min(2 ** attempt, 5))
                    last_err = f"HTTP {resp.status_code}: {resp.text}"
                    continue
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                last_err = str(e)
                await asyncio.sleep(min(2 ** attempt, 5))
                
    raise RuntimeError(f"Gọi API LLM Async thất bại sau 8 lần thử. Lỗi cuối: {last_err}")

def stream_llm(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.1,
    max_tokens: int = 1500,
    model: str | None = None,
    config: dict[str, str] | None = None
) -> Generator[str, None, None]:
    """Gọi LLM và stream kết quả trả về từng chunk (Server-Sent Events)."""
    if config is None:
        config = get_llm_config()
    url, headers, payload = _build_payload(config, system_prompt, user_prompt, temperature, max_tokens, response_json=False, stream=True, model=model)
    
    try:
        with requests.post(url, json=payload, headers=headers, stream=True, timeout=60.0) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if line:
                    decoded = line.decode('utf-8').strip()
                    if decoded.startswith("data:"):
                        data_str = decoded[5:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
    except Exception as e:
        yield f"\n[Stream Error: {e}]"

def clean_json_response(raw_text: str) -> dict[str, Any]:
    """Lọc các khối code fences markdown và parse JSON an toàn."""
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    text = text.strip()
    
    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last != -1 and last > first:
        text = text[first : last + 1]
        
    return json.loads(text)
