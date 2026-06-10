# -*- coding: utf-8 -*-
"""
Module Query Planner thực thi Rule Extraction, gọi ngữ nghĩa để lấy candidates,
dựng prompt tinh gọn cho LLM Planner, sinh và kiểm định Canonical Query Plan.
"""

from __future__ import annotations
import os
import sys
import re
import json
from pathlib import Path
from typing import Any
from jsonschema import validate as json_validate

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "Processed"
METADATA_DIR = PROCESSED_DIR / "metadata"
QUERY_CONTROL_METADATA_DIR = METADATA_DIR / "query_control"

sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.query_control.llm_helper import call_llm, clean_json_response

class RuleExtractor:
    """
    Bộ rút trích đặc trưng dựa trên luật (Regex) chạy trước Qdrant và LLM.
    Giúp phát hiện năm khảo sát, các chiều gom nhóm (group-by), kiểu tác vụ, và bộ lọc địa lý.
    """
    def extract(self, user_question: str) -> dict[str, Any]:
        """
        Rút trích các thuộc tính từ câu hỏi của người dùng.

        Args:
            user_question (str): Câu hỏi tiếng Việt đầu vào.

        Returns:
            dict[str, Any]: Metadata đặc trưng rút trích được.
        """
        question_lower = user_question.strip().lower()
        import re
        
        # 1. Rút trích năm linh hoạt qua Regex (ví dụ: 2023, 2024, 2025)
        years = []
        found_years = re.findall(r"\b(20[0-2]\d)\b", question_lower)
        for y_str in found_years:
            y_val = int(y_str)
            if y_val not in years:
                years.append(y_val)
            
        # 2. Phát hiện group-by (các chiều gom nhóm)
        group_by = []
        if any(w in question_lower for w in ["theo huyện", "từng huyện", "huyện nào", "mỗi huyện"]):
            group_by.append("district")
        if any(w in question_lower for w in ["theo xã", "từng xã", "xã nào", "mỗi xã"]):
            group_by.append("commune")
        if any(w in question_lower for w in ["theo năm", "từng năm", "mỗi năm"]):
            group_by.append("year")
            
        # 3. Phát hiện kiểu đầu ra / tác vụ
        is_detail = any(w in question_lower for w in ["liệt kê", "danh sách", "chi tiết", "hiển thị hộ"])
        is_topk = any(w in question_lower for w in ["cao nhất", "nhiều nhất", "ít nhất", "thấp nhất", "top"])
        is_comparison = any(w in question_lower for w in ["so sánh", "chênh lệch", "tăng", "giảm", "so với"])
        is_aggregate = any(w in question_lower for w in ["bao nhiêu", "số lượng", "tổng", "trung bình", "tỉ lệ"])
        
        task_type = "aggregate_query"
        if is_detail:
            task_type = "detail_query"
        elif is_topk:
            task_type = "topk_query"
        elif is_comparison:
            task_type = "comparison_query"
            
        # 4. Xác định chiều hướng sắp xếp cho Top-K
        direction = None
        if is_topk:
            if any(w in question_lower for w in ["cao nhất", "nhiều nhất", "top"]):
                direction = "desc"
            elif any(w in question_lower for w in ["thấp nhất", "ít nhất"]):
                direction = "asc"
                
        # 5. Phát hiện bộ lọc huyện/xã trực tiếp từ tên huyện đã biết
        districts_daknong = [
            "cư jút", "krông nô", "tuy đức", "đăk glong", "đắk mil", "đắk rlấp", "đắk song", "gia nghĩa"
        ]
        detected_district = None
        for d in districts_daknong:
            if d in question_lower:
                # Chuẩn hoá tên huyện theo file thực tế
                if d == "cư jút": detected_district = "Huyện Cư Jút"
                elif d == "krông nô": detected_district = "Huyện Krông Nô"
                elif d == "tuy đức": detected_district = "Huyện Tuy Đức"
                elif d == "đăk glong": detected_district = "Huyện Đăk Glong"
                elif d == "đắk mil": detected_district = "Huyện Đắk Mil"
                elif d == "đắk rlấp": detected_district = "Huyện Đắk RLấp"
                elif d == "đắk song": detected_district = "Huyện Đắk Song"
                elif d == "gia nghĩa": detected_district = "Thành phố Gia Nghĩa"
                break
                
        # Nhận diện khi câu hỏi chứa cả hộ nghèo và cận nghèo
        has_both_poverty_types = "nghèo và cận nghèo" in question_lower or "nghèo và hộ cận nghèo" in question_lower
                
        return {
            "task_type": task_type,
            "years": years,
            "group_by": group_by,
            "is_topk": is_topk,
            "direction": direction,
            "is_comparison": is_comparison,
            "is_aggregate": is_aggregate,
            "detected_district": detected_district,
            "has_both_poverty_types": has_both_poverty_types
        }

class QueryPlanner:
    def __init__(
        self,
        schema_graph_path: Path,
        semantic_layer_path: Path,
        query_plan_schema_path: Path,
        semantic_retriever: Any
    ):
        self.schema_graph_path = schema_graph_path
        self.semantic_layer_path = semantic_layer_path
        self.query_plan_schema_path = query_plan_schema_path
        self.semantic_retriever = semantic_retriever
        
        with open(semantic_layer_path, "r", encoding="utf-8") as f:
            self.semantic_layer = json.load(f)
            
        with open(query_plan_schema_path, "r", encoding="utf-8") as f:
            self.query_plan_schema = json.load(f)
            
        # Tải planner prompt template
        planner_prompt_path = QUERY_CONTROL_METADATA_DIR / "planner_prompt.md"
        with open(planner_prompt_path, "r", encoding="utf-8") as f:
            self.planner_prompt_tmpl = f.read()
            
    def apply_rule_extraction(self, user_question: str) -> dict[str, Any]:
        return RuleExtractor().extract(user_question)
        
    def build_planner_context(self, user_question: str, rule_output: dict[str, Any]) -> dict[str, Any]:
        """Gọi Qdrant SemanticRetriever để tìm các candidates và cấu trúc lại thông tin cho prompt."""
        ret = self.semantic_retriever.retrieve(user_question, top_k=5, rule_output=rule_output)
        
        # Tạo phiên bản compact của candidates
        metric_candidates_compact = []
        for m in ret.get("metric_candidates", []):
            metric_candidates_compact.append({
                "id": m["id"],
                "name_vi": m["name_vi"],
                "definition": m["definition"],
                "score": m["score"]
            })
            
        dimension_candidates_compact = []
        for d in ret.get("dimension_candidates", []):
            dimension_candidates_compact.append({
                "id": d["id"],
                "name_vi": d["name_vi"],
                "allowed_for_group_by": d["payload"].get("allowed_for_group_by", True),
                "allowed_for_filter": d["payload"].get("allowed_for_filter", True),
                "score": d["score"]
            })
            
        business_term_candidates_compact = []
        for b in ret.get("business_term_candidates", []):
            business_term_candidates_compact.append({
                "term": b["id"],
                "maps_to": b["payload"].get("maps_to", {}),
                "score": b["score"]
            })
            
        query_example_candidates_compact = []
        for qe in ret.get("query_example_candidates", []):
            query_example_candidates_compact.append({
                "text": qe["name_vi"],
                "maps_to": qe["payload"].get("maps_to", {}),
                "score": qe["score"]
            })
            
        return {
            "metric_candidates_compact": metric_candidates_compact,
            "dimension_candidates_compact": dimension_candidates_compact,
            "business_term_candidates_compact": business_term_candidates_compact,
            "query_example_candidates_compact": query_example_candidates_compact,
            "warnings": ret.get("warnings", [])
        }
        
    def plan(self, user_question: str) -> dict[str, Any]:
        """Điều phối toàn bộ quá trình lập kế hoạch truy vấn và kiểm định kế hoạch."""
        # 1. Rút trích luật
        rule_output = self.apply_rule_extraction(user_question)
        
        # 2. Truy xuất ngữ nghĩa từ Qdrant
        ret_context = self.build_planner_context(user_question, rule_output)
        
        # Check warnings độ tin cậy
        for w in ret_context.get("warnings", []):
            if w.get("code") == "LOW_RETRIEVAL_CONFIDENCE":
                # Fallback nhanh
                return {
                    "task_type": "unknown",
                    "metrics": [],
                    "dimensions": [],
                    "filters": [],
                    "sort": None,
                    "limit": None,
                    "output_type": "text",
                    "ambiguities": ["Không tìm thấy định nghĩa nghiệp vụ phù hợp trong cơ sở dữ liệu ngữ nghĩa."]
                }
                
        # 3. Dựng prompt gửi LLM
        system_prompt = self.planner_prompt_tmpl
        system_prompt = system_prompt.replace("{rule_signals}", json.dumps(rule_output, ensure_ascii=False, indent=2))
        system_prompt = system_prompt.replace("{metric_candidates_compact}", json.dumps(ret_context["metric_candidates_compact"], ensure_ascii=False, indent=2))
        system_prompt = system_prompt.replace("{dimension_candidates_compact}", json.dumps(ret_context["dimension_candidates_compact"], ensure_ascii=False, indent=2))
        system_prompt = system_prompt.replace("{business_term_candidates_compact}", json.dumps(ret_context["business_term_candidates_compact"], ensure_ascii=False, indent=2))
        system_prompt = system_prompt.replace("{query_example_candidates_compact}", json.dumps(ret_context["query_example_candidates_compact"], ensure_ascii=False, indent=2))
        system_prompt = system_prompt.replace("{user_question}", user_question)
        
        # Gọi LLM FPT
        try:
            raw_res = call_llm(
                system_prompt=system_prompt,
                user_prompt=f"Câu hỏi: {user_question}",
                temperature=0.1,
                max_tokens=250, # Giới hạn tối ưu max_tokens sinh
                response_json=True
            )
            llm_plan = clean_json_response(raw_res)
        except Exception as e:
            return {
                "task_type": "unknown",
                "metrics": [],
                "dimensions": [],
                "filters": [],
                "sort": None,
                "limit": None,
                "output_type": "text",
                "ambiguities": [f"Lỗi gọi LLM Planner: {e}"]
            }
            
        # 4. Chuẩn hoá và sửa chữa kế hoạch tự động
        ret_context["user_question"] = user_question
        normalized_plan = self.normalize_llm_output(llm_plan, rule_output, ret_context)
        
        # 5. Kiểm định kế hoạch
        errors = self.validate_query_plan(normalized_plan)
        if errors:
            # Tiến hành tự sửa chữa
            normalized_plan = self.repair_query_plan(normalized_plan, errors)
            # Kiểm định lại
            errors = self.validate_query_plan(normalized_plan)
            if errors:
                normalized_plan["task_type"] = "unknown"
                normalized_plan["ambiguities"] = normalized_plan.get("ambiguities", []) + [e["message"] for e in errors]
                
        return normalized_plan

    def normalize_llm_output(self, llm_output: dict[str, Any], rule_output: dict[str, Any], ret_context: dict[str, Any]) -> dict[str, Any]:
        """
        Đồng bộ hoá và chuẩn hoá các thông tin từ LLM Output với Rule Extractor và danh mục chuẩn.
        """
        plan = llm_output.copy()
        user_question = ret_context.get("user_question", "")
        plan["original_question"] = user_question
        
        # Mappings chuẩn hóa chỉ số và chiều dữ liệu
        METRIC_NORM_MAP = {
            "poor_household_count": "poor_household_count",
            "poor_count": "poor_household_count",
            "poor_hhs": "poor_household_count",
            "near_poor_household_count": "near_poor_household_count",
            "near_poor_hhs": "near_poor_household_count",
            "household_count": "household_count",
            "total_hhs": "household_count",
            "avg_b1": "avg_b1_score",
            "avg_b1_score": "avg_b1_score",
            "avg_b2": "avg_b2_score",
            "avg_b2_score": "avg_b2_score",
            "poor_rate": "poor_rate",
            "poor_household_rate": "poor_rate",
            "near_poor_rate": "near_poor_rate",
            "near_poor_household_rate": "near_poor_rate",
            "avg_age": "avg_age",
            "avg_member_age": "avg_age",
        }

        DIM_NORM_MAP = {
            "classify": "poverty_status",
            "poverty_status": "poverty_status",
            "classification_status": "poverty_status",
            "classification": "poverty_status",  # Bổ sung chuẩn hóa classification cho câu hỏi GQ022
            "household_type": "poverty_status",
            "district": "district",
            "district_name": "district",
            "commune": "commune",
            "commune_name": "commune",
            "year": "year",
            "host_name": "host_name",
            "household_id": "household_id"
        }

        # Nhận diện đặc biệt cho câu hỏi gộp cả nghèo + cận nghèo
        if rule_output.get("has_both_poverty_types"):
            plan["metrics"] = ["household_count"]
        
        # Nếu rule_extractor tin cậy phát hiện là detail_query (qua từ khóa danh sách, liệt kê) thì ghi đè task_type của LLM
        if rule_output.get("task_type") == "detail_query" or any(w in user_question.lower() for w in ["danh sách", "liệt kê", "chi tiết"]):
            plan["task_type"] = "detail_query"
            if not plan.get("dimensions"):
                plan["dimensions"] = ["household_id", "host_name"]
            plan["metrics"] = []
        
        # Tự động điều chỉnh metrics cho các câu hỏi tỷ lệ (ratio_query)
        if "tỷ lệ" in user_question.lower() or "tỉ lệ" in user_question.lower():
            is_top1 = plan.get("limit") == 1 or "huyện nào" in user_question.lower() or "xã nào" in user_question.lower()
            if "nghèo" in user_question.lower() and "cận nghèo" not in user_question.lower():
                if is_top1:
                    plan["metrics"] = ["poor_rate"]
                else:
                    plan["metrics"] = ["household_count", "poor_household_count", "poor_rate"]
            elif "cận nghèo" in user_question.lower():
                if is_top1:
                    plan["metrics"] = ["near_poor_rate"]
                else:
                    plan["metrics"] = ["household_count", "near_poor_household_count", "near_poor_rate"]

        # Merge task_type từ rule nếu LLM không chắc chắn hoặc sai lệch
        if plan.get("task_type") == "unknown" or not plan.get("task_type"):
            plan["task_type"] = rule_output.get("task_type", "aggregate_query")
            
        # Chuẩn hóa metrics
        norm_metrics = []
        for m in plan.get("metrics", []):
            mapped_m = METRIC_NORM_MAP.get(m.lower(), m)
            if mapped_m not in norm_metrics:
                norm_metrics.append(mapped_m)
        plan["metrics"] = norm_metrics
        
        # Chuẩn hóa dimensions
        norm_dims = []
        for d in plan.get("dimensions", []):
            mapped_d = DIM_NORM_MAP.get(d.lower(), d)
            if mapped_d not in norm_dims:
                norm_dims.append(mapped_d)
        plan["dimensions"] = norm_dims

        # Điền các filter tự động từ Rule Extractor (như Năm) nếu LLM bỏ sót
        existing_filters = plan.get("filters", [])
        if not isinstance(existing_filters, list):
            existing_filters = []
            
        # Chuẩn hóa các bộ lọc hiện có
        norm_filters = []
        for f in existing_filters:
            if not isinstance(f, dict):
                continue
            field = f.get("field", "")
            mapped_field = DIM_NORM_MAP.get(field.lower(), field)
            f["field"] = mapped_field
            
            # Chuẩn hóa value của bộ lọc
            val = f.get("value")
            if mapped_field == "poverty_status" and isinstance(val, str):
                val_lower = val.lower()
                if "cận nghèo" in val_lower or "near" in val_lower:
                    f["value"] = "Hộ cận nghèo"
                elif "nghèo" in val_lower or "poor" in val_lower:
                    f["value"] = "Hộ nghèo"
            
            # Sửa lỗi so sánh năm bằng toán tử so sánh chuỗi
            if mapped_field == "year" and isinstance(val, str) and val.isdigit():
                f["value"] = int(val)
                
            norm_filters.append(f)
        existing_filters = norm_filters
        existing_fields = [f.get("field") for f in existing_filters]
        
        # Thêm filter năm từ rule_output
        if "year" not in existing_fields and rule_output.get("years"):
            if len(rule_output["years"]) >= 2:
                existing_filters.append({
                    "field": "year",
                    "operator": "IN",
                    "value": rule_output["years"]
                })
            else:
                existing_filters.append({
                    "field": "year",
                    "operator": "=",
                    "value": rule_output["years"][0]
                })
                
        # Thêm filter district nếu phát hiện
        if "district" not in existing_fields and rule_output.get("detected_district"):
            existing_filters.append({
                "field": "district",
                "operator": "=",
                "value": rule_output["detected_district"]
            })
            
        plan["filters"] = existing_filters
        
        # Merge group_by / dimensions
        for d in rule_output.get("group_by", []):
            mapped_d = DIM_NORM_MAP.get(d.lower(), d)
            if mapped_d not in plan["dimensions"]:
                plan["dimensions"].append(mapped_d)
                
        # Chuẩn hóa sort field
        if plan.get("sort") and isinstance(plan["sort"], dict):
            sf = plan["sort"].get("field", "")
            mapped_sf = METRIC_NORM_MAP.get(sf.lower(), DIM_NORM_MAP.get(sf.lower(), sf))
            plan["sort"]["field"] = mapped_sf
        
        # Sửa lỗi kiểu dữ liệu và trường mặc định
        if "metrics" not in plan or not isinstance(plan["metrics"], list):
            plan["metrics"] = []
        if "dimensions" not in plan or not isinstance(plan["dimensions"], list):
            plan["dimensions"] = []
        if "filters" not in plan or not isinstance(plan["filters"], list):
            plan["filters"] = []
        if "ambiguities" not in plan or not isinstance(plan["ambiguities"], list):
            plan["ambiguities"] = []
            
        return plan
        
    def validate_query_plan(self, query_plan: dict[str, Any]) -> list[dict[str, Any]]:
        """Kiểm định kế hoạch dựa trên cấu trúc JSON Schema và logic nghiệp vụ."""
        errors = []
        
        # 1. Kiểm định cấu trúc schema
        try:
            json_validate(instance=query_plan, schema=self.query_plan_schema)
        except Exception as e:
            errors.append({"code": "SCHEMA_COMPLIANCE_ERROR", "message": f"Kế hoạch sai cấu trúc Schema: {e}"})
            return errors
            
        task_type = query_plan["task_type"]
        if task_type == "unknown":
            errors.append({"code": "UNKNOWN_TASK_TYPE", "message": "Kiểu tác vụ chưa được xác định."})
            return errors
            
        # 2. Kiểm tra metric bắt buộc phải có cho các loại query thống kê
        metrics = query_plan["metrics"]
        if task_type in ["aggregate_query", "topk_query", "comparison_query"] and not metrics:
            errors.append({"code": "METRICS_EMPTY", "message": f"Các tác vụ thống kê '{task_type}' bắt buộc phải khai báo metrics."})
            
        # 3. Kiểm định sự tồn tại và sẵn sàng của Metrics
        semantic_metrics = self.semantic_layer.get("metrics", {})
        for m in metrics:
            if m not in semantic_metrics:
                errors.append({"code": "METRIC_NOT_FOUND", "message": f"Metric '{m}' không tồn tại trong Semantic Layer."})
            elif semantic_metrics[m].get("status") != "ready":
                errors.append({"code": "METRIC_NOT_READY", "message": f"Metric '{m}' đang ở trạng thái chưa sẵn sàng: {semantic_metrics[m].get('reason')}"})
                
        # 4. Kiểm định sự tồn tại và sẵn sàng của Dimensions
        dimensions = query_plan["dimensions"]
        semantic_dims = self.semantic_layer.get("dimensions", {})
        for d in dimensions:
            if d not in semantic_dims:
                errors.append({"code": "DIMENSION_NOT_FOUND", "message": f"Dimension '{d}' không tồn tại trong Semantic Layer."})
            elif semantic_dims[d].get("status") != "ready":
                errors.append({"code": "DIMENSION_NOT_READY", "message": f"Dimension '{d}' đang ở trạng thái chưa sẵn sàng: {semantic_dims[d].get('reason')}"})
                
        # 5. Kiểm tra tính hợp lệ của trường lọc
        for f in query_plan["filters"]:
            f_field = f.get("field")
            if f_field not in semantic_dims and f_field not in self.semantic_layer.get("measures", {}):
                errors.append({"code": "INVALID_FILTER_FIELD", "message": f"Trường lọc '{f_field}' không thuộc dimensions hay measures hợp lệ."})
                
        # 6. Kiểm định ràng buộc Top-K
        if task_type == "topk_query":
            if not query_plan.get("sort"):
                errors.append({"code": "TOPK_MISSING_SORT", "message": "Tác vụ Top-K yêu cầu cấu hình trường sắp xếp (sort)."})
            if not query_plan.get("limit"):
                errors.append({"code": "TOPK_MISSING_LIMIT", "message": "Tác vụ Top-K yêu cầu cấu hình giới hạn kết quả (limit)."})
                
        # 7. Kiểm tra thiếu bộ lọc năm (year filter) cho các truy vấn dữ liệu
        has_year = False
        for f in query_plan.get("filters", []):
            if isinstance(f, dict) and f.get("field") == "year":
                has_year = True
                break
        # Nếu group by theo year hoặc là truy vấn so sánh qua các năm, không yêu cầu filter year đơn lẻ
        if "year" in dimensions or task_type in ["comparison_query", "comparison_by_year"]:
            has_year = True
            
        if not has_year and task_type != "unknown":
            errors.append({"code": "MISSING_TIME_FILTER", "message": "Truy vấn thiếu bộ lọc năm khảo sát (2023 hoặc 2024)."})
            
        return errors
        
    def repair_query_plan(self, query_plan: dict[str, Any], errors: list[dict[str, Any]]) -> dict[str, Any]:
        """Tự động sửa lỗi hoặc bổ sung các trường mặc định nếu thiếu sót nhẹ."""
        repaired = query_plan.copy()
        
        for err in errors:
            code = err["code"]
            
            # Sửa lỗi detail_query thiếu limit
            if code == "SCHEMA_COMPLIANCE_ERROR" and repaired["task_type"] == "detail_query":
                repaired["limit"] = 100
                
            # Sửa lỗi thiếu sort hoặc limit cho topk_query
            if code == "TOPK_MISSING_SORT" and repaired["metrics"]:
                repaired["sort"] = {
                    "field": repaired["metrics"][0],
                    "direction": "desc"
                }
            if code == "TOPK_MISSING_LIMIT":
                repaired["limit"] = 5
                
            # Thêm limit mặc định cho detail_query
            if repaired["task_type"] == "detail_query" and not repaired.get("limit"):
                repaired["limit"] = 100
                
        return repaired
