# -*- coding: utf-8 -*-
"""
Module Domain Gate / Router phân loại câu hỏi người dùng.
Định tuyến câu hỏi vào nhánh tương ứng (Dataset Q&A, General Knowledge, Out of Scope, Clarification...).
Kết hợp luật từ khoá, exact match business terms, Qdrant Retriever và LLM Fallback.
"""

from __future__ import annotations
import os
import sys
import json
import re
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))
from src.query_control.llm_helper import call_llm, clean_json_response


class DomainGate:
    def __init__(self, config_path: Path, semantic_layer_path: Path, semantic_retriever: Any = None):
        """
        Khởi tạo DomainGate với cấu hình định tuyến và lớp ngữ nghĩa.

        Args:
            config_path (Path): Đường dẫn đến tệp cấu hình domain_gate_config.json.
            semantic_layer_path (Path): Đường dẫn đến tệp semantic_layer.json.
            semantic_retriever (Any, optional): Module tìm kiếm ngữ nghĩa Qdrant (tùy chọn).
        """
        self.semantic_retriever = semantic_retriever

        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        with open(semantic_layer_path, "r", encoding="utf-8") as f:
            self.semantic_layer = json.load(f)

    def classify(self, user_question: str) -> dict[str, Any]:
        """
        Phân loại câu hỏi của người dùng thành một trong các nhãn định tuyến chuẩn.

        Args:
            user_question (str): Câu hỏi tiếng Việt của người dùng.

        Returns:
            dict[str, Any]: Kết quả định tuyến gồm route, confidence, reason,
                            detected_signals, retrieval_summary, suggested_next_action.
        """
        question_lower = user_question.strip().lower()

        # 1. Từ khoá dành cho Dataset Q&A (thống kê, số liệu cụ thể)
        qa_keywords = [
            "bao nhiêu", "số lượng", "tổng số", "tổng cộng", "thống kê", "danh sách", "liệt kê",
            "trung bình", "cao nhất", "ít nhất", "nhiều nhất", "so sánh", "chênh lệch", "tăng", "giảm",
            "tỉ lệ", "tỷ lệ", "phần trăm", "ở đâu", "huyện nào", "xã nào", "năm 2023", "năm 2024",
            "có thiếu", "có bị", "có phải", "có nghèo", "bị nghèo", "thiếu nước", "thiếu vốn", "dân tộc", "nguyên nhân",
            "bao người", "nước sạch", "nhà tiêu", "thiếu đất", "ốm đau", "tai nạn", "tình hình", "biểu đồ", "thay đổi", "xu hướng", "cơ cấu", "số hộ"
        ]

        # 2. Từ khoá dành cho General Knowledge (định nghĩa, giải thích)
        gk_keywords = [
            "là gì", "thế nào", "nghĩa là gì", "giải thích", "chuẩn nghèo", "đa chiều", "tiêu chí",
            "quy định", "bước", "quy trình", "nguyên tắc", "hướng dẫn", "bản chất"
        ]

        has_qa_signal = any(kw in question_lower for kw in qa_keywords)
        has_gk_signal = any(kw in question_lower for kw in gk_keywords)

        # 3. Kiểm tra exact match với business terms trong semantic layer
        matched_terms = []
        for term in self.semantic_layer.get("business_terms", {}).keys():
            if term in question_lower:
                matched_terms.append(term)

        # 4. Gọi Qdrant Retriever nếu có để lấy điểm tương đồng ngữ nghĩa
        retrieval_summary = {}
        top_retrieval_score = 0.0
        if self.semantic_retriever:
            try:
                ret_res = self.semantic_retriever.retrieve(user_question, top_k=5)
                raw_hits = ret_res.get("raw_hits", [])
                if raw_hits:
                    top_retrieval_score = float(raw_hits[0]["score"])
                retrieval_summary = {
                    "top_score": top_retrieval_score,
                    "metrics": [m["id"] for m in ret_res.get("metric_candidates", [])],
                    "dimensions": [d["id"] for d in ret_res.get("dimension_candidates", [])]
                }
            except Exception as e:
                retrieval_summary = {"error": str(e)}

        # 5. Kiểm tra nội dung có liên quan đến nghiệp vụ hộ nghèo không
        poverty_related = [
            "nghèo", "cận nghèo", "b1", "b2", "hộ", "nhân khẩu", "đắk nông", "thiếu hụt",
            "dân tộc", "tại chỗ", "kinh", "nam", "nữ", "dân số", "gia đình", "tài sản", "thu nhập",
            "nước sạch", "nhà tiêu", "đất sản xuất", "ốm đau", "tai nạn", "vốn", "lao động"
        ]
        is_related = any(w in question_lower for w in poverty_related) or len(matched_terms) > 0

        # 6. Nếu không liên quan nghiệp vụ → dùng LLM Fallback
        if not is_related:
            route, confidence, reason = self._llm_classify(user_question)
            return {
                "route": route,
                "confidence": confidence,
                "reason": reason,
                "detected_signals": ["llm_fallback_unrelated"],
                "retrieval_summary": retrieval_summary,
                "suggested_next_action": "Đi theo kết quả định tuyến của LLM do thiếu từ khóa liên quan."
            }

        # 7. Câu hỏi quá ngắn hoặc mơ hồ → CLARIFICATION_NEEDED
        if len(question_lower.split()) <= 3 and not matched_terms:
            return {
                "route": "CLARIFICATION_NEEDED",
                "confidence": 0.85,
                "reason": "Câu hỏi quá ngắn hoặc mơ hồ, thiếu thực thể.",
                "detected_signals": ["short_query"],
                "retrieval_summary": retrieval_summary,
                "suggested_next_action": "Yêu cầu người dùng làm rõ."
            }

        # 8. Xác định route từ tín hiệu kết hợp
        if has_qa_signal and has_gk_signal:
            route = "HYBRID"
            confidence = 0.8
        elif has_qa_signal:
            route = "DATASET_QA"
            confidence = 0.85
        elif has_gk_signal:
            route = "GENERAL_KNOWLEDGE"
            confidence = 0.85
        else:
            # Không đủ tín hiệu rõ ràng → dùng Qdrant score hoặc LLM fallback
            if top_retrieval_score >= 0.55:
                route = "DATASET_QA"
                confidence = float(top_retrieval_score)
            else:
                # LLM Fallback Classifier
                route, confidence, reason = self._llm_classify(user_question)
                return {
                    "route": route,
                    "confidence": confidence,
                    "reason": reason,
                    "detected_signals": ["llm_fallback"],
                    "retrieval_summary": retrieval_summary,
                    "suggested_next_action": "Đi theo kết quả định tuyến của LLM."
                }

        return {
            "route": route,
            "confidence": confidence,
            "reason": f"Phân loại dựa trên từ khoá và bộ lọc ngữ nghĩa (QA={has_qa_signal}, GK={has_gk_signal}).",
            "detected_signals": matched_terms,
            "retrieval_summary": retrieval_summary,
            "suggested_next_action": f"Chuyển tiếp câu hỏi tới luồng {route}."
        }

    def _llm_classify(self, question: str) -> tuple[str, float, str]:
        """
        Sử dụng LLM để phân loại câu hỏi khi luật và Qdrant không đủ độ tin cậy.

        Args:
            question (str): Câu hỏi tiếng Việt cần phân loại.

        Returns:
            tuple[str, float, str]: (route, confidence, reason)
        """
        system_prompt = (
            "Bạn là Router phân loại câu hỏi của chatbot dữ liệu hộ nghèo tỉnh Đắk Nông.\n"
            "Hãy phân tích câu hỏi người dùng và phân loại vào một trong các nhãn:\n"
            "1. DATASET_QA: Yêu cầu số liệu thống kê cụ thể, đếm số lượng, so sánh, hoặc liệt kê thông tin từ cơ sở dữ liệu.\n"
            "2. GENERAL_KNOWLEDGE: Yêu cầu định nghĩa, giải thích khái niệm hộ nghèo, cận nghèo, chỉ số thiếu hụt hoặc quy định pháp lý.\n"
            "3. HYBRID: Câu hỏi vừa hỏi lý thuyết/định nghĩa vừa yêu cầu số liệu thống kê.\n"
            "4. CLARIFICATION_NEEDED: Câu hỏi mơ hồ, thiếu thông tin để xử lý (ví dụ: 'tình hình sao rồi', 'cho tôi xem thông tin').\n"
            "5. OUT_OF_SCOPE: Câu hỏi không liên quan gì đến nghèo đói, nhân khẩu, Đắk Nông (ví dụ: công nghệ, nấu ăn, thời tiết).\n\n"
            "Định dạng đầu ra bắt buộc là JSON dạng:\n"
            "{\n"
            "  \"route\": \"DATASET_QA | GENERAL_KNOWLEDGE | HYBRID | CLARIFICATION_NEEDED | OUT_OF_SCOPE\",\n"
            "  \"confidence\": 0.0-1.0,\n"
            "  \"reason\": \"Giải thích ngắn gọn lý do phân loại\"\n"
            "}"
        )
        try:
            raw_res = call_llm(system_prompt, f"Câu hỏi: {question}", temperature=0.1, max_tokens=150, response_json=True)
            res = clean_json_response(raw_res)
            return res.get("route", "OUT_OF_SCOPE"), float(res.get("confidence", 0.5)), res.get("reason", "")
        except Exception as e:
            return "CLARIFICATION_NEEDED", 0.5, f"Lỗi gọi LLM Classifier: {e}"
