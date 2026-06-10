# -*- coding: utf-8 -*-
"""
Module llm_helper cung cấp hàm gọi API LLM chuyên dụng.
Sử dụng mô hình gemma-4-26B-A4B-it thông qua dịch vụ FPT AI.
"""

from __future__ import annotations
import os
import re
import json
import time
import requests
from dotenv import load_dotenv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

def get_llm_config() -> dict[str, str]:
    """Lấy cấu hình kết nối LLM từ tệp .env."""
    base_url = os.environ.get("FPT_BASE_URL", "").strip()
    api_key = os.environ.get("FPT_ALL_LLM_API_KEY", "").strip()
    model = os.environ.get("FPT_LLM_MODEL", "gemma-4-26B-A4B-it").strip()
    
    # Nếu người dùng cấu hình sai/thiếu (Quy tắc 6)
    if not api_key:
        raise RuntimeError("Lỗi: Thiếu khóa API FPT_ALL_LLM_API_KEY trong tệp .env.")
    if not base_url:
        raise RuntimeError("Lỗi: Thiếu địa chỉ FPT_BASE_URL trong tệp .env.")
        
    return {
        "base_url": base_url.rstrip("/"),
        "api_key": api_key,
        "model": model
    }

def call_llm(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.1,
    max_tokens: int = 1500,
    response_json: bool = False
) -> str:
    """Gọi LLM FPT với cơ chế retry và xử lý lỗi chuyên sâu."""
    config = get_llm_config()
    
    # Chuẩn hoá URL completion
    url = f"{config['base_url']}/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }
    
    if response_json:
        payload["response_format"] = {"type": "json_object"}
        
    last_err = None
    for attempt in range(3):
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
            
    raise RuntimeError(f"Gọi API LLM thất bại sau 3 lần thử. Lỗi cuối: {last_err}")

def clean_json_response(raw_text: str) -> dict[str, Any]:
    """Lọc các khối code fences markdown và parse JSON an toàn."""
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    text = text.strip()
    
    # Tìm đối tượng JSON đầu tiên
    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last != -1 and last > first:
        text = text[first : last + 1]
        
    return json.loads(text)

