# -*- coding: utf-8 -*-
"""
Module Conversation Memory quản lý bộ nhớ hội thoại, lưu vết lịch sử chat theo phiên (session)
và giải quyết các câu hỏi kế thừa (follow-up questions) bằng cách trích xuất ngữ cảnh cũ.
"""

from __future__ import annotations
import os
import json
import re
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]

class ConversationMemory:
    def __init__(self, config_path: str, session_id: str):
        """Khởi tạo Bộ nhớ Hội thoại."""
        self.config_path = Path(config_path)
        if not self.config_path.is_absolute():
            self.config_path = PROJECT_ROOT / self.config_path
            
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
            
        self.session_id = session_id
        self.memory_dir = PROJECT_ROOT / self.config.get("memory_dir", "Runtime/conversations")
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = self.memory_dir / f"{self.session_id}.json"
        
        self.max_turns = self.config.get("max_turns", 10)
        self.enabled = self.config.get("enabled", True)
        
        # Load hoặc tạo mới phiên hội thoại
        self.history = self.load()

    def load(self) -> dict[str, Any]:
        """Tải lịch sử hội thoại từ đĩa."""
        if self.enabled and self.session_file.exists():
            try:
                with open(self.session_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "session_id": self.session_id,
            "turns": [],
            "last_route": None,
            "last_query_plan": None,
            "last_sql": None,
            "last_result_summary": None,
            "last_clarification": None,
            "active_filters": [],
            "active_metric": None,
            "active_dimensions": []
        }

    def save(self):
        """Lưu lịch sử hội thoại xuống đĩa."""
        if not self.enabled:
            return
        try:
            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def add_turn(self, user_question: str, assistant_response: dict[str, Any]):
        """Thêm một lượt trao đổi vào lịch sử và cập nhật trạng thái hoạt động (active state)."""
        if not self.enabled:
            return
            
        # Tóm tắt kết quả để lưu trữ nhẹ nhàng
        result_summary = {
            "success": assistant_response.get("success", True),
            "row_count": assistant_response.get("row_count", 0),
            "columns": assistant_response.get("columns", []),
            "top_rows": assistant_response.get("result_preview", [])[:3]
        }
        
        turn = {
            "user_question": user_question,
            "route": assistant_response.get("route"),
            "query_plan": assistant_response.get("query_plan"),
            "sql": assistant_response.get("sql"),
            "result_summary": result_summary,
            "errors": assistant_response.get("errors", []),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }
        
        # Đẩy vào danh sách turns và cắt bớt nếu vượt quá giới hạn
        self.history["turns"].append(turn)
        if len(self.history["turns"]) > self.max_turns:
            self.history["turns"] = self.history["turns"][-self.max_turns:]
            
        # Cập nhật các trường vết nhanh (track fields)
        self.history["last_route"] = assistant_response.get("route")
        if assistant_response.get("query_plan"):
            qp = assistant_response["query_plan"]
            self.history["last_query_plan"] = qp
            
            # Cập nhật các tham số hoạt động (active states) để kế thừa lượt sau
            if qp.get("metrics"):
                self.history["active_metric"] = qp["metrics"][0]
            if qp.get("dimensions"):
                self.history["active_dimensions"] = qp["dimensions"]
            if qp.get("filters"):
                self.history["active_filters"] = qp["filters"]
                
        self.history["last_sql"] = assistant_response.get("sql")
        self.history["last_result_summary"] = result_summary
        
        # Nếu có clarification
        if assistant_response.get("needs_clarification"):
            self.history["last_clarification"] = assistant_response
        else:
            self.history["last_clarification"] = None
            
        self.save()

    def get_last_query_plan(self) -> dict[str, Any] | None:
        """Lấy Query Plan ở lượt truy vấn thành công gần nhất."""
        return self.history.get("last_query_plan")

    def resolve_follow_up(self, user_question: str, rule_output: dict[str, Any]) -> dict[str, Any] | None:
        """
        Phát hiện câu hỏi kế thừa và trả về cấu trúc ngữ cảnh được kế thừa từ các lượt trước.
        Nếu không phải câu hỏi kế thừa, trả về None.
        """
        q_lower = user_question.lower().strip()
        last_plan = self.get_last_query_plan()
        
        if not last_plan:
            return None
            
        # 1. Phát hiện các mẫu tín hiệu của câu kế thừa (Follow-up Signals)
        is_follow_up = False
        
        # Mẫu: "còn ... thì sao", "thế còn ...", "còn ...", "so với ..."
        follow_up_patterns = [
            r"^còn\s+", r"^thế còn\s+", r"^so với\s+", r"thì sao\??$", 
            r"còn năm\s+\d{4}", r"còn huyện\s+", r"theo xã", r"chi tiết hơn",
            r"danh sách chi tiết", r"liệt kê"
        ]
        
        for pat in follow_up_patterns:
            if re.search(pat, q_lower):
                is_follow_up = True
                break
                
        # Nếu câu hỏi quá ngắn (ví dụ: "năm 2023", "Krông Nô", "Đắk Mil") và có plan trước đó
        if len(q_lower.split()) <= 4 and last_plan:
            is_follow_up = True
            
        if not is_follow_up:
            return None
            
        # 2. Thực hiện kế thừa ngữ cảnh (Inheritance logic)
        inherited_context = {
            "task_type": last_plan.get("task_type", "aggregate_query"),
            "metrics": last_plan.get("metrics", []),
            "dimensions": last_plan.get("dimensions", []),
            "filters": list(last_plan.get("filters", [])),
            "sort": last_plan.get("sort"),
            "limit": last_plan.get("limit"),
            "output_type": last_plan.get("output_type", "table")
        }
        
        # 3. Phân tích xem người dùng muốn thay đổi bộ phận nào
        
        # A. Thay đổi Năm (Year)
        year_match = re.search(r"\b(2023|2024)\b", q_lower)
        if year_match:
            target_year = int(year_match.group(1))
            # Thay thế hoặc cập nhật filter năm trong filters kế thừa
            new_filters = []
            for f in inherited_context["filters"]:
                if f.get("field") != "year":
                    new_filters.append(f)
            new_filters.append({"field": "year", "operator": "=", "value": target_year})
            inherited_context["filters"] = new_filters
            
        # B. Thay đổi đơn vị hành chính huyện/xã
        # Danh sách huyện cơ bản của Đắk Nông để khớp nhanh
        districts = ["cư jút", "krông nô", "tuy đức", "đăk glong", "đắk glong", "đắk mil", "đắk rlấp", "đắk r'lấp", "đắk song", "gia nghĩa"]
        matched_district = None
        for d in districts:
            if d in q_lower:
                matched_district = d
                break
                
        if matched_district:
            # Map chuẩn tên huyện viết hoa
            dict_map = {
                "cư jút": "Huyện Cư Jút", "krông nô": "Huyện Krông Nô", "tuy đức": "Huyện Tuy Đức",
                "đăk glong": "Huyện Đăk Glong", "đắk glong": "Huyện Đăk Glong", "đắk mil": "Huyện Đắk Mil",
                "đắk rlấp": "Huyện Đắk RLấp", "đắk r'lấp": "Huyện Đắk RLấp", "đắk song": "Huyện Đắk Song",
                "gia nghĩa": "Thành phố Gia Nghĩa"
            }
            standard_name = dict_map[matched_district]
            
            # Cập nhật filter huyện trong filters kế thừa
            new_filters = []
            for f in inherited_context["filters"]:
                if f.get("field") != "district":
                    new_filters.append(f)
            new_filters.append({"field": "district", "operator": "=", "value": standard_name})
            inherited_context["filters"] = new_filters
            
        # C. Thay đổi Dimension phân nhóm (ví dụ: "vậy theo xã thì sao", "theo năm")
        if "theo xã" in q_lower or "theo xã phường" in q_lower:
            inherited_context["dimensions"] = ["commune"]
        elif "theo huyện" in q_lower:
            inherited_context["dimensions"] = ["district"]
        elif "theo năm" in q_lower:
            inherited_context["dimensions"] = ["year"]
            
        # D. Yêu cầu chi tiết hơn ("chi tiết hơn", "danh sách", "liệt kê")
        if any(w in q_lower for w in ["chi tiết hơn", "danh sách", "liệt kê"]):
            inherited_context["task_type"] = "detail_query"
            inherited_context["output_type"] = "table"
            # Giới hạn limit để tránh SELECT * quá lớn
            inherited_context["limit"] = 100
            
        # E. Yêu cầu so sánh ("so với năm trước", "so sánh")
        if "so với" in q_lower or "so sánh" in q_lower:
            inherited_context["task_type"] = "comparison_query"
            
        return inherited_context

    def clear(self):
        """Xoá lịch sử hội thoại hiện tại."""
        self.history = {
            "session_id": self.session_id,
            "turns": [],
            "last_route": None,
            "last_query_plan": None,
            "last_sql": None,
            "last_result_summary": None,
            "last_clarification": None,
            "active_filters": [],
            "active_metric": None,
            "active_dimensions": []
        }
        self.save()
        
# Import time để lấy mốc thời gian
import time
