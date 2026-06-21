# -*- coding: utf-8 -*-
"""
Module Semantic Retriever thực hiện tìm kiếm và xếp hạng các ứng viên ngữ nghĩa từ Qdrant.
Kết hợp điểm số vector cosine, khớp chuỗi ký tự chính xác (exact anchor) và tín hiệu từ Rule Extractor.
"""

from __future__ import annotations
import os
import sys
from pathlib import Path
from typing import Any
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

# Thêm đường dẫn để import
sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.query_control.build_qdrant_semantic_index import EmbeddingClient

class SemanticRetriever:
    def __init__(self, qdrant_url: str, collection_name: str, embedding_model: str, score_threshold: float | None = None):
        self.qdrant_url = qdrant_url
        self.collection_name = collection_name
        self.embedding_client = EmbeddingClient(embedding_model)
        self.qclient = QdrantClient(url=qdrant_url, timeout=5.0)
        
        # Ngưỡng điểm số tin cậy động dựa theo mô hình embedding (Quy tắc 2: Chú thích tiếng Việt)
        if score_threshold is not None:
            self.score_threshold = score_threshold
        elif "e5" in embedding_model.lower():
            self.score_threshold = 0.35
        else:
            self.score_threshold = 0.15  # Ngưỡng thấp hơn cho các model khác như Vietnamese_Embedding
        
    def retrieve(self, user_question: str, top_k: int = 8, rule_output: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Tìm kiếm các ứng viên ngữ nghĩa từ Qdrant và xếp hạng lại.
        Return:
        {
          "metric_candidates": [...],
          "dimension_candidates": [...],
          "business_term_candidates": [...],
          "query_example_candidates": [...],
          "raw_hits": [...],
          "warnings": [...]
        }
        """
        warnings = []
        
        # 1. Sinh vector embedding cho câu hỏi
        try:
            query_vector = self.embedding_client.embed_text(user_question)
        except Exception as e:
            return {
                "metric_candidates": [],
                "dimension_candidates": [],
                "business_term_candidates": [],
                "query_example_candidates": [],
                "raw_hits": [],
                "warnings": [{"code": "EMBEDDING_FAILED", "message": f"Không thể sinh embedding: {e}"}]
            }
            
        # 2. Tìm kiếm trong Qdrant sử dụng phương thức query_points (thay thế search đã bị loại bỏ ở các phiên bản qdrant-client mới)
        try:
            query_response = self.qclient.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=top_k * 2  # Lấy dư ra để phân loại và chấm điểm
            )
            hits = query_response.points
        except Exception as e:
            return {
                "metric_candidates": [],
                "dimension_candidates": [],
                "business_term_candidates": [],
                "query_example_candidates": [],
                "raw_hits": [],
                "warnings": [{"code": "QDRANT_SEARCH_FAILED", "message": f"Tìm kiếm Qdrant thất bại: {e}"}]
            }
            
        # 3. Phân loại và xếp hạng lại bằng công thức kết hợp
        metric_candidates = []
        dimension_candidates = []
        business_term_candidates = []
        query_example_candidates = []
        raw_hits = []
        
        question_lower = user_question.lower()
        
        for hit in hits:
            payload = hit.payload or {}
            doc_type = payload.get("doc_type")
            semantic_id = payload.get("semantic_id")
            name_vi = payload.get("name_vi", "").lower()
            status = payload.get("status", "ready")
            
            raw_hits.append({
                "id": hit.id,
                "score": hit.score,
                "payload": payload
            })
            
            # Tính exact_anchor_score: Khớp chính xác cụm từ hoặc ID
            exact_anchor_score = 0.0
            if semantic_id and semantic_id.lower() in question_lower:
                exact_anchor_score = 1.0
            elif name_vi and name_vi in question_lower:
                exact_anchor_score = 1.0
                
            # Tính rule_signal_score
            rule_signal_score = 0.0
            if rule_output:
                # Nếu rule extractor phát hiện năm và candidate liên quan đến năm
                if "year" in semantic_id.lower() and rule_output.get("years"):
                    rule_signal_score = 1.0
                # Nếu phát hiện top-k và candidate là topk query
                if rule_output.get("is_topk") and doc_type == "query_example" and payload.get("maps_to", {}).get("task_type") == "topk_query":
                    rule_signal_score = 1.0
                # Nếu phát hiện so sánh
                if rule_output.get("is_comparison") and doc_type == "query_example" and payload.get("maps_to", {}).get("task_type") == "comparison_query":
                    rule_signal_score = 1.0
                    
            # Tính status_score
            status_score = 1.0
            if status == "ambiguous":
                status_score = 0.5
            elif status == "incomplete":
                status_score = 0.0
                
            # Công thức tính final_score đề xuất
            # final_score = 0.65 * vector_score + 0.20 * exact_anchor_score + 0.10 * rule_signal_score + 0.05 * status_score
            # hit.score thường nằm trong khoảng [-1, 1], chuẩn hoá vector_score về [0, 1] nếu là Cosine (thường > 0)
            vector_score = max(0.0, float(hit.score))
            final_score = (
                0.65 * vector_score
                + 0.20 * exact_anchor_score
                + 0.10 * rule_signal_score
                + 0.05 * status_score
            )
            
            candidate = {
                "id": semantic_id,
                "name_vi": payload.get("name_vi"),
                "definition": payload.get("definition"),
                "status": status,
                "score": round(final_score, 4),
                "payload": payload
            }
            
            # Chỉ ưu tiên các ứng viên có status khác incomplete (score > 0)
            if status == "incomplete" and exact_anchor_score == 0:
                continue
                
            if doc_type == "metric_definition":
                metric_candidates.append(candidate)
            elif doc_type == "dimension_definition":
                dimension_candidates.append(candidate)
            elif doc_type == "business_term":
                business_term_candidates.append(candidate)
            elif doc_type == "query_example":
                query_example_candidates.append(candidate)
                
        # Sắp xếp candidates theo điểm giảm dần và giới hạn số lượng
        metric_candidates.sort(key=lambda x: x["score"], reverse=True)
        dimension_candidates.sort(key=lambda x: x["score"], reverse=True)
        business_term_candidates.sort(key=lambda x: x["score"], reverse=True)
        query_example_candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Cảnh báo nếu độ tin cậy thấp
        top_score = max([hit.score for hit in hits]) if hits else 0.0
        if top_score < self.score_threshold:
            warnings.append({
                "code": "LOW_RETRIEVAL_CONFIDENCE",
                "message": f"Không tìm thấy metric/dimension đủ tin cậy từ Qdrant (top_score={top_score:.4f} < threshold={self.score_threshold})"
            })
            
        return {
            "metric_candidates": metric_candidates[:5],
            "dimension_candidates": dimension_candidates[:5],
            "business_term_candidates": business_term_candidates[:5],
            "query_example_candidates": query_example_candidates[:3],
            "raw_hits": raw_hits,
            "warnings": warnings
        }
