# -*- coding: utf-8 -*-
"""
Module Query Cache lưu trữ và truy xuất kết quả dựa trên Canonical Query Plan.
Sử dụng MD5 hash để cache kết quả SQL và exact-match cho Query Plan.
"""

from __future__ import annotations
import os
import json
import hashlib
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]

class QueryCache:
    def __init__(self, config_path: str):
        """Khởi tạo Query Cache từ tệp cấu hình."""
        self.config_path = Path(config_path)
        if not self.config_path.is_absolute():
            self.config_path = PROJECT_ROOT / self.config_path

        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.cache_dir = PROJECT_ROOT / self.config.get("cache_dir", "Runtime/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.enabled = self.config.get("enabled", True)
        self.ttl = self.config.get("ttl_seconds", 86400)
        self.max_entries = self.config.get("max_entries", 1000)

        # Khởi tạo tệp index của cache
        self.index_path = self.cache_dir / "cache_index.json"
        self._load_index()

        # Tự động invalidate nếu database DuckDB bị rebuild
        if self.config.get("invalidate_on_data_rebuild", True):
            db_path = PROJECT_ROOT / "Runtime" / "duckdb" / "intern_chatbot.duckdb"
            if db_path.exists():
                db_mtime = str(db_path.stat().st_mtime)
                self.invalidate_if_data_changed(db_mtime)

    def _load_index(self):
        """Tải mục lục cache từ đĩa."""
        if self.index_path.exists():
            try:
                with open(self.index_path, "r", encoding="utf-8") as f:
                    self.index = json.load(f)
            except Exception:
                self.index = {"entries": {}, "data_version": ""}
        else:
            self.index = {"entries": {}, "data_version": ""}

    def _save_index(self):
        """Lưu mục lục cache xuống đĩa."""
        try:
            with open(self.index_path, "w", encoding="utf-8") as f:
                json.dump(self.index, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def make_query_plan_hash(self, query_plan: dict[str, Any]) -> str:
        """Tạo khóa hash MD5 duy nhất cho Query Plan dựa trên các trường cấu hình."""
        hash_dict = {}
        hash_fields = self.config.get("hash_fields", [
            "task_type", "metrics", "dimensions", "filters", "sort", "limit", "output_type"
        ])
        
        for field in hash_fields:
            if field in query_plan:
                val = query_plan[field]
                if isinstance(val, list):
                    str_list = []
                    for item in val:
                        if isinstance(item, dict):
                            str_list.append(json.dumps(item, sort_keys=True))
                        else:
                            str_list.append(str(item))
                    hash_dict[field] = sorted(str_list)
                elif isinstance(val, dict):
                    hash_dict[field] = sorted(val.items())
                else:
                    hash_dict[field] = val
                    
        serialized = json.dumps(hash_dict, sort_keys=True)
        return hashlib.md5(serialized.encode("utf-8")).hexdigest()

    def get_sql_result(self, query_plan: dict[str, Any]) -> dict[str, Any] | None:
        """Lấy kết quả SQL từ cache dựa trên Query Plan."""
        if not self.enabled or not self.config.get("cache_layers", {}).get("sql_result_cache", True):
            return None
            
        cache_key = self.make_query_plan_hash(query_plan)
        entry = self.index["entries"].get(cache_key)
        
        if not entry:
            return None
            
        # Kiểm tra TTL (Time to Live)
        created_at = entry.get("created_at", 0)
        if time.time() - created_at > self.ttl:
            self._delete_entry(cache_key)
            return None
            
        cache_file = self.cache_dir / f"{cache_key}.json"
        if not cache_file.exists():
            return None
            
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
                
            cached_data["cache_metadata"] = {
                "cache_hit": True,
                "cache_key": cache_key,
                "cached_at": entry.get("cached_at_str"),
                "ttl_seconds": self.ttl
            }
            return cached_data
        except Exception:
            return None

    def set_sql_result(self, query_plan: dict[str, Any], result: dict[str, Any], metadata: dict[str, Any] | None = None):
        """Lưu kết quả truy vấn SQL vào cache."""
        if not self.enabled or not self.config.get("cache_layers", {}).get("sql_result_cache", True):
            return
            
        if not result.get("success", True):
            return
            
        cache_key = self.make_query_plan_hash(query_plan)
        
        if len(self.index["entries"]) >= self.max_entries:
            oldest_key = min(self.index["entries"].keys(), key=lambda k: self.index["entries"][k]["created_at"])
            self._delete_entry(oldest_key)
            
        cache_file = self.cache_dir / f"{cache_key}.json"
        now = time.time()
        
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False)
                
            self.index["entries"][cache_key] = {
                "created_at": now,
                "cached_at_str": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now)),
                "type": "sql_result"
            }
            self._save_index()
        except Exception:
            pass

    def get_query_plan(self, normalized_question: str) -> dict[str, Any] | None:
        """Lấy Query Plan đã phân tích từ cache dựa trên câu hỏi (Exact match)."""
        if not self.enabled or not self.config.get("cache_layers", {}).get("query_plan_cache", True):
            return None

        # Exact Match theo MD5 hash của câu hỏi đã chuẩn hoá
        q_hash = hashlib.md5(normalized_question.strip().lower().encode("utf-8")).hexdigest()
        entry = self.index["entries"].get(q_hash)

        if entry:
            created_at = entry.get("created_at", 0)
            if time.time() - created_at <= self.ttl:
                cache_file = self.cache_dir / f"{q_hash}.json"
                if cache_file.exists():
                    try:
                        with open(cache_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if isinstance(data, dict) and "query_plan" in data:
                                return data["query_plan"]
                            return data
                    except Exception:
                        pass

        return None

    def set_query_plan(self, normalized_question: str, query_plan: dict[str, Any]):
        """Lưu trữ Query Plan đã phân tích cho câu hỏi tương ứng."""
        if not self.enabled or not self.config.get("cache_layers", {}).get("query_plan_cache", True):
            return

        q_hash = hashlib.md5(normalized_question.strip().lower().encode("utf-8")).hexdigest()

        if len(self.index["entries"]) >= self.max_entries:
            oldest_key = min(self.index["entries"].keys(), key=lambda k: self.index["entries"][k]["created_at"])
            self._delete_entry(oldest_key)

        cache_file = self.cache_dir / f"{q_hash}.json"
        now = time.time()

        cache_payload = {
            "question": normalized_question,
            "query_plan": query_plan
        }

        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_payload, f, ensure_ascii=False, indent=2)

            self.index["entries"][q_hash] = {
                "created_at": now,
                "cached_at_str": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now)),
                "type": "query_plan"
            }
            self._save_index()
        except Exception:
            pass

    def _delete_entry(self, key: str):
        """Xóa một entry khỏi cache index và xóa file vật lý tương ứng."""
        if key in self.index["entries"]:
            del self.index["entries"][key]

        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                os.remove(cache_file)
            except Exception:
                pass
        self._save_index()

    def clear(self):
        """Xóa toàn bộ các tệp tin cache."""
        for key in list(self.index["entries"].keys()):
            self._delete_entry(key)
        self.index = {"entries": {}, "data_version": ""}
        self._save_index()

    def invalidate_if_data_changed(self, data_version: str):
        """Xóa toàn bộ cache nếu phiên bản dữ liệu thay đổi."""
        if self.index.get("data_version") != data_version:
            self.clear()
            self.index["data_version"] = data_version
            self._save_index()


