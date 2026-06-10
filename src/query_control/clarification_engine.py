# -*- coding: utf-8 -*-
"""
Module Clarification Engine chịu trách nhiệm phát hiện sự mơ hồ trong câu hỏi của người dùng,
ngăn chặn việc sinh SQL sai lệch và đưa ra các câu hỏi gợi ý/lựa chọn để làm rõ yêu cầu.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]

class ClarificationEngine:
    def __init__(self, config_path: str, semantic_layer_path: str):
        """Khởi tạo Clarification Engine từ cấu hình và Semantic Layer."""
        self.config_path = Path(config_path)
        if not self.config_path.is_absolute():
            self.config_path = PROJECT_ROOT / self.config_path
            
        self.semantic_layer_path = Path(semantic_layer_path)
        if not self.semantic_layer_path.is_absolute():
            self.semantic_layer_path = PROJECT_ROOT / self.semantic_layer_path
            
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
            
        with open(self.semantic_layer_path, "r", encoding="utf-8") as f:
            self.semantic_layer = json.load(f)
            
        self.max_options = self.config.get("max_options", 4)
        self.default_questions = self.config.get("default_questions", {})

    def build_clarification(self, error_codes: list[str] | list[dict[str, Any]], context: dict[str, Any]) -> dict[str, Any]:
        """
        Xây dựng câu hỏi gợi ý làm rõ yêu cầu dựa trên danh sách mã lỗi và ngữ cảnh.
        """
        output = {
            "needs_clarification": True,
            "message": "",
            "options": [],
            "reason": "",
            "error_codes": []
        }
        
        # Chuẩn hóa danh sách mã lỗi (chấp nhận cả chuỗi lỗi hoặc cấu trúc lỗi chứa trường 'code')
        codes = []
        for e in error_codes:
            if isinstance(e, dict):
                codes.append(e.get("code", "UNKNOWN"))
            else:
                codes.append(str(e))
                
        output["error_codes"] = codes
        
        # 1. ROUTE_UNCERTAIN hoặc AMBIGUOUS_ROUTE
        if "ROUTE_UNCERTAIN" in codes:
            output["reason"] = "Không thể phân loại rõ định tuyến câu hỏi"
            output["message"] = self.default_questions.get("ambiguous_route", "Bạn muốn truy vấn số liệu trong dataset hay hỏi giải thích kiến thức chung?")
            output["options"] = [
                {"label": "Truy vấn số liệu rà soát nghèo trong cơ sở dữ liệu", "value": {"route_override": "DATASET_QA"}},
                {"label": "Hỏi đáp kiến thức, quy chế, khái niệm chung", "value": {"route_override": "GENERAL_KNOWLEDGE"}}
            ]
            return output
            
        # 2. METRIC_NOT_FOUND
        if "METRIC_NOT_FOUND" in codes or "METRIC_EMPTY" in codes:
            output["reason"] = "Thiếu hoặc không xác định được chỉ số (metric) cần tính toán"
            output["message"] = self.default_questions.get("missing_metric", "Bạn muốn thống kê chỉ số nào?")
            
            # Gợi ý một số metric có sẵn từ semantic layer
            available_metrics = self.semantic_layer.get("metrics", {})
            count = 0
            for m_id, m_meta in available_metrics.items():
                if count >= self.max_options:
                    break
                # Trích xuất tên tiếng Việt
                name = m_meta.get("name_vi", m_id)
                output["options"].append({
                    "label": f"Xem {name.lower()}",
                    "value": {"metrics": [m_id]}
                })
                count += 1
            return output

        # 3. MISSING_TIME_FILTER
        if "MISSING_TIME_FILTER" in codes:
            output["reason"] = "Không tìm thấy bộ lọc năm khảo sát"
            output["message"] = self.default_questions.get("missing_time", "Bạn muốn xem dữ liệu thuộc năm khảo sát nào?")
            output["options"] = [
                {"label": "Năm rà soát 2023", "value": {"filters": [{"field": "year", "operator": "=", "value": 2023}]}},
                {"label": "Năm rà soát 2024", "value": {"filters": [{"field": "year", "operator": "=", "value": 2024}]}},
                {"label": "Cả hai năm 2023 và 2024", "value": {"filters": []}} # Sẽ tự động gộp hoặc hiển thị cả hai
            ]
            return output

        # 4. DIMENSION_NOT_FOUND
        if "DIMENSION_NOT_FOUND" in codes:
            output["reason"] = "Thiếu chiều phân nhóm dữ liệu (dimension)"
            output["message"] = self.default_questions.get("missing_dimension", "Bạn muốn nhóm kết quả theo đơn vị nào?")
            output["options"] = [
                {"label": "Theo đơn vị cấp Huyện", "value": {"dimensions": ["district"]}},
                {"label": "Theo đơn vị cấp Xã", "value": {"dimensions": ["commune"]}},
                {"label": "Theo Năm khảo sát", "value": {"dimensions": ["year"]}}
            ]
            return output

        # 5. LOW_RETRIEVAL_CONFIDENCE
        if "LOW_RETRIEVAL_CONFIDENCE" in codes:
            output["reason"] = "Độ tự tin tìm kiếm ngữ nghĩa quá thấp"
            output["message"] = self.default_questions.get("low_retrieval_confidence", "Mình chưa rõ bạn cần hỏi về chủ đề nào trong các ý sau:")
            output["options"] = [
                {"label": "Thống kê hộ nghèo", "value": {"metrics": ["poor_household_count"]}},
                {"label": "Thống kê hộ cận nghèo", "value": {"metrics": ["near_poor_household_count"]}},
                {"label": "Điểm rà soát trung bình (B1/B2)", "value": {"metrics": ["avg_b1_score"]}}
            ]
            return output

        # Default Fallback
        output["reason"] = "Câu hỏi chưa rõ ràng hoặc lỗi kiểm định kế hoạch"
        output["message"] = "Câu hỏi của bạn cần thêm một số thông tin để mình có thể truy vấn chính xác. Vui lòng chọn một trong các gợi ý dưới đây:"
        output["options"] = [
            {"label": "Thống kê số lượng hộ nghèo theo huyện năm 2024", "value": {"metrics": ["poor_household_count"], "dimensions": ["district"], "filters": [{"field": "year", "operator": "=", "value": 2024}]}},
            {"label": "Thống kê số lượng hộ cận nghèo theo huyện năm 2024", "value": {"metrics": ["near_poor_household_count"], "dimensions": ["district"], "filters": [{"field": "year", "operator": "=", "value": 2024}]}},
            {"label": "Hỏi đáp kiến thức chung về hộ nghèo", "value": {"route_override": "GENERAL_KNOWLEDGE"}}
        ]
        return output

    def apply_user_selection(self, previous_query_plan: dict[str, Any], selection: dict[str, Any]) -> dict[str, Any]:
        """
        Hợp nhất lựa chọn đã chọn của người dùng vào Query Plan của lượt hỏi trước.
        """
        updated_plan = previous_query_plan.copy()
        
        # Override route nếu được yêu cầu
        if "route_override" in selection:
            updated_plan["route_override"] = selection["route_override"]
            
        # Hợp nhất các metrics
        if "metrics" in selection:
            updated_plan["metrics"] = list(set(updated_plan.get("metrics", []) + selection["metrics"]))
            
        # Hợp nhất các dimensions
        if "dimensions" in selection:
            updated_plan["dimensions"] = list(set(updated_plan.get("dimensions", []) + selection["dimensions"]))
            
        # Hợp nhất các bộ lọc
        if "filters" in selection:
            current_filters = updated_plan.get("filters", [])
            for sf in selection["filters"]:
                # Kiểm tra tránh trùng lặp filter trên cùng một trường
                dup = False
                for cf in current_filters:
                    if cf.get("field") == sf.get("field"):
                        cf["value"] = sf["value"]
                        cf["operator"] = sf.get("operator", "=")
                        dup = True
                        break
                if not dup:
                    current_filters.append(sf)
            updated_plan["filters"] = current_filters
            
        return updated_plan
