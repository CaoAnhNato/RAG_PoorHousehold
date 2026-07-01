# -*- coding: utf-8 -*-
"""
Module semantic_cache quản lý cơ chế Caching hai lớp (Two-tier Caching Layer)
kết hợp In-memory/File Canonical Hashing và Qdrant Vector DB Semantic Similarity (>0.95)
nhằm giảm thời gian phản hồi (latency) xuống <10ms cho các câu hỏi trùng lặp hoặc tương đương.
"""

from __future__ import annotations
import os
import sys
import json
import uuid
import re
import hashlib
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as qmodels
except ImportError:
    QdrantClient = None

from src.query_control.build_qdrant_semantic_index import EmbeddingClient, load_qdrant_config

CACHE_DIR = PROJECT_ROOT / "data" / "Processed" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
LOCAL_CACHE_FILE = CACHE_DIR / "semantic_sql_cache.json"

class SemanticCacheManager:
    """Quản lý bộ đệm kết hợp Local JSON (Canonical Hash) và Qdrant Vector (Semantic Matching)."""
    
    def __init__(self, collection_name: str = "agentic_semantic_cache", similarity_threshold: float = 0.95):
        self.collection_name = collection_name
        self.similarity_threshold = similarity_threshold
        self.local_cache: dict[str, dict[str, Any]] = {}
        self.qclient = None
        self.emb_client = None
        self.initialized_qdrant = False
        self._load_local_cache()
        
    def _load_local_cache(self) -> None:
        """Tải bộ đệm cục bộ từ tệp JSON."""
        if LOCAL_CACHE_FILE.exists():
            try:
                with open(LOCAL_CACHE_FILE, "r", encoding="utf-8") as f:
                    self.local_cache = json.load(f)
            except Exception:
                self.local_cache = {}
        else:
            self.local_cache = {}

    def _save_local_cache(self) -> None:
        """Lưu bộ đệm cục bộ ra tệp JSON."""
        try:
            with open(LOCAL_CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.local_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Cache Warning] Không thể lưu local cache: {e}")

    def _init_qdrant(self) -> None:
        """Khởi tạo QdrantClient và EmbeddingClient (Lazy load)."""
        if self.initialized_qdrant:
            return
        self.initialized_qdrant = True
        
        if QdrantClient is None:
            print("[Cache Warning] qdrant_client chưa được cài đặt. Chỉ sử dụng local canonical cache.")
            return

        try:
            try:
                qconfig = load_qdrant_config()
                qurl = qconfig.get("qdrant_url", "http://localhost:6333")
                emb_model = os.environ.get("EMBEDDING_MODEL", qconfig.get("embedding_model", "text-embedding-3-small"))
            except Exception:
                qurl = os.environ.get("QDRANT_URL", "http://localhost:6333")
                emb_model = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")

            self.qclient = QdrantClient(url=qurl, timeout=3.0)
            self.emb_client = EmbeddingClient(emb_model)
            vector_size = self.emb_client.get_dimension()

            # Kiểm tra hoặc tạo collection
            try:
                col_info = self.qclient.get_collection(self.collection_name)
                if col_info.config.params.vectors.size != vector_size:
                    print(f"[Cache Info] Kích thước vector thay đổi ({col_info.config.params.vectors.size} -> {vector_size}). Đang tạo lại collection '{self.collection_name}'...")
                    self.qclient.delete_collection(self.collection_name)
                    raise Exception("Force recreate")
            except Exception:
                # Collection chưa tồn tại hoặc cần tạo lại
                self.qclient.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=qmodels.VectorParams(
                        size=vector_size,
                        distance=qmodels.Distance.COSINE
                    )
                )
                print(f"[Cache Info] Đã tạo collection Qdrant '{self.collection_name}' (Size: {vector_size})")
        except Exception as e:
            print(f"[Cache Warning] Khởi tạo Qdrant thất bại ({e}). Tự động chuyển sang chế độ Local Cache 100%.")
            self.qclient = None
            self.emb_client = None

    def get_canonical_hash(self, question: str) -> str:
        """Chuẩn hóa câu hỏi thành Canonical Hash key."""
        text = question.lower().strip()
        # Loại bỏ các ký tự đặc biệt, dấu câu, chuẩn hóa khoảng trắng
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def get_exact_cache(self, question: str) -> dict[str, Any] | None:
        """
        Truy xuất bộ đệm Tier 1 (Exact Canonical Hash in Local Cache).
        Đảm bảo tốc độ Hit siêu tốc <1ms, phục vụ độc quyền cho Route 1.
        """
        self._load_local_cache()
        if not question or not question.strip():
            return None
            
        key = self.get_canonical_hash(question)
        if key in self.local_cache:
            print(f"   [Semantic Cache] HIT (Local Canonical Cache) | Key: {key}")
            return self.local_cache[key]
        return None

    def search_similar_questions(self, question: str, threshold: float = 0.86) -> list[dict[str, Any]]:
        """
        Truy vấn Qdrant Vector DB (Tier 2) để tìm các câu hỏi có cấu trúc tương tự (score >= threshold).
        Chỉ trả về danh sách SQL mẫu và metadata để phục vụ cho Route 2 (Few-shot SQL Repair).
        Tuyệt đối không trả về trực tiếp làm đáp án chính thức để tránh sai sót số liệu.
        """
        if not question or not question.strip():
            return []
            
        self._init_qdrant()
        results = []
        if self.qclient and self.emb_client:
            try:
                vector = self.emb_client.embed_text(question)
                if hasattr(self.qclient, 'query_points'):
                    search_result = self.qclient.query_points(
                        collection_name=self.collection_name,
                        query=vector,
                        limit=2
                    ).points
                else:
                    search_result = self.qclient.search(
                        collection_name=self.collection_name,
                        query_vector=vector,
                        limit=2,
                        score_threshold=threshold
                    )
                for hit in search_result:
                    if hit.score < threshold:
                        continue
                    payload = hit.payload or {}
                    print(f"   [Semantic Cache] Found Similar (Qdrant DB) | Similarity Score: {hit.score:.4f} | Old Q: {payload.get('question', '')}")
                    results.append({
                        "score": hit.score,
                        "question": payload.get("question", ""),
                        "sql": payload.get("sql", ""),
                        "answer": payload.get("answer", "")
                    })
            except Exception as e:
                print(f"   [Cache Warning] Lỗi truy vấn Qdrant similarity search: {e}")
        return results

    def get_cache(self, question: str) -> dict[str, Any] | None:
        """
        Hàm tương thích ngược (Backward Compatibility).
        Chỉ kiểm tra Exact Match (Route 1). Để dùng Qdrant, phải thông qua search_similar_questions.
        """
        return self.get_exact_cache(question)

    def set_cache(self, question: str, sql: str, answer: str, chart_code: str = "") -> None:
        """Lưu trữ kết quả vào Local Cache và Qdrant Vector DB."""
        if not question or not question.strip():
            return

        key = self.get_canonical_hash(question)
        cache_data = {
            "question": question,
            "sql": sql,
            "answer": answer
        }
        if chart_code:
            cache_data["chart_code"] = chart_code
        
        # 1. Update Local Cache
        self.local_cache[key] = cache_data
        self._save_local_cache()

        # 2. Update Qdrant
        self._init_qdrant()
        if self.qclient and self.emb_client:
            try:
                vector = self.emb_client.embed_text(question)
                point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"cache_{key}"))
                self.qclient.upsert(
                    collection_name=self.collection_name,
                    points=[qmodels.PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=cache_data
                    )]
                )
                print(f"   [Semantic Cache] Đã lưu vào Qdrant (Collection: {self.collection_name})")
            except Exception as e:
                print(f"   [Cache Warning] Lỗi upsert vào Qdrant cache: {e}")

# Biến toàn cục Singleton quản lý Cache
cache_manager = SemanticCacheManager()

def get_cached_result(question: str) -> dict[str, Any] | None:
    return cache_manager.get_cache(question)

def set_cached_result(question: str, sql: str, answer: str, chart_code: str = "") -> None:
    cache_manager.set_cache(question, sql, answer, chart_code=chart_code)
