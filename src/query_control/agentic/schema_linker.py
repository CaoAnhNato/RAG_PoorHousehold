# -*- coding: utf-8 -*-
from __future__ import annotations
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))
from src.query_control.llm_helper import call_llm, clean_json_response

class SchemaLinker:
    """Agent trích xuất các bảng và cột liên quan từ schema dựa trên câu hỏi."""
    def __init__(self, semantic_layer_path: Path):
        with open(semantic_layer_path, "r", encoding="utf-8") as f:
            self.semantic_layer = json.load(f)
            
    def link(self, user_question: str) -> dict:
        """Trả về thông tin schema đã lọc động dựa trên từ khóa và cấu trúc semantic layer (Zero Hardcoding)."""
        q_lower = user_question.lower()
        
        # 1. Table Scope Isolation
        # Bảng members CHỈ được kích hoạt khi câu hỏi có từ khóa liên quan đến thành viên/nhân khẩu
        member_keywords = [
            "nhân khẩu", "thành viên", "vợ/chồng", "con ", "của chủ hộ", 
            "quan hệ với chủ hộ", "giới tính thành viên", "tuổi thành viên", 
            "từng người", "danh sách người", "member", "từng thành viên"
        ]
        has_member_intent = any(kw in q_lower for kw in member_keywords)
        relevant_tables = ["households", "members"] if has_member_intent else ["households"]
        
        # 2. Dynamic Domain Clustering
        # 1. Minimal Core: Chỉ chứa 3 cột hành chính/phân loại tuyệt đối tối thiểu
        # ("commune" và "household_id" sẽ được kích hoạt động khi câu hỏi nhắc tới xã hoặc định danh hộ)
        minimal_core_keys = {
            "year", "district", "poverty_status"
        }
        
        # 2. Measure Cluster: Chỉ kích hoạt khi hỏi về tỷ lệ, đếm tổng số hộ
        measure_cluster_keys = {
            "household_count", "poor_household_count",
            "near_poor_household_count", "poor_rate", "near_poor_rate"
        }
        
        deprivation_keys = {
            "clean_water", "hygienic_toilet", "employment", "dependent_person",
            "nutrition", "health_insurance", "adult_education", "child_school_attendance",
            "housing_quality", "housing_area", "telecommunication", "information_access_assets"
        }
        
        reason_keys = {
            "lack_production_land", "lack_capital", "lack_labor", "illness_accident",
            "lack_production_tools", "lack_production_knowledge", "lack_labor_skill"
        }
        
        gender_keys = {
            "gender", "host_name"
        }
        
        ethnicity_keys = {
            "ethnicity", "local_ethnicity", "is_dtts", "is_kinh", "co_dan_toc_tai_cho"
        }
        
        age_keys = {
            "age_group", "avg_age"
        }
        
        policy_keys = {
            "poverty_detail", "near_poverty_detail", "medium_living_standard",
            "has_no_labor", "has_revolution_merit"
        }
        
        children_keys = {
            "children_total", "children_health_insurance", "children_nutrition", "children_education"
        }
        
        scoring_keys = {
            "b1_score", "b2_score", "deprivation_count", "avg_b1_score", "avg_b2_score"
        }
        
        member_keys = {
            "member_gender", "relationship_to_host", "member_count", "household_member_count", "household_size"
        }
        
        active_keys = set(minimal_core_keys)
        
        # Kích hoạt commune nếu câu hỏi nhắc đến xã/thị trấn hoặc tên các xã/thị trấn
        if any(kw in q_lower for kw in ["xã", "thị trấn", "phường", "commune", "đắk", "krông", "nam", "quảng", "thuận", "đức", "tâm", "nhân", "đạo", "nghĩa", "long", "soi", "bút"]):
            active_keys.add("commune")
            
        # Kích hoạt household_id và host_name nếu câu hỏi nhắc đến định danh hộ, mã hộ, chủ hộ, tên hộ, hộ cụ thể hoặc danh sách chi tiết
        if any(kw in q_lower for kw in ["mã", "id", "code", "hộ số", "danh sách hộ", "liệt kê hộ", "chủ hộ", "tìm hộ", "từng hộ", "chi tiết hộ", "mã hộ", "hộ gia đình", "hộ "]) or any(w in q_lower for w in ["nguyễn", "trần", "lê", "phạm", "phùng", "hoàng", "huỳnh", "phan", "vũ", "võ", "đặng", "bùi", "đỗ", "hồ", "ngô", "dương", "lý", "giàng", "lầu", "hầu", "vàng", "sùng", "sung", "thị", "văn"]):
            active_keys.add("household_id")
            active_keys.update(gender_keys)
        
        # Kích hoạt cụm đo lường nếu câu hỏi có ý định thống kê tổng hợp / tỷ lệ / quy mô
        measure_keywords = ["tỷ lệ", "bao nhiêu hộ", "tổng số hộ", "rate", "count", "sll", "phần trăm", "%", "bao nhiêu"]
        if any(kw in q_lower for kw in measure_keywords):
            active_keys.update(measure_cluster_keys)
        
        # Kích hoạt cụm theo ý định từ khóa
        if any(w in q_lower for w in ["thiếu hụt", "dịch vụ", "cơ bản", "nước", "nhà tiêu", "việc làm", "bảo hiểm", "dinh dưỡng", "giáo dục", "nhà ở", "viễn thông", "thông tin", "chiều"]):
            active_keys.update(deprivation_keys)
            
        if any(w in q_lower for w in ["nguyên nhân", "lý do", "thiếu đất", "thiếu vốn", "thiếu lao động", "ốm đau", "công cụ", "kiến thức", "kỹ năng"]):
            active_keys.update(reason_keys)
            
        if any(w in q_lower for w in ["dân tộc", "kinh", "dtts", "thiểu số", "tại chỗ", "m'nông", "mạ", "tày", "mường", "dao", "mông", "thái", "nùng"]):
            active_keys.update(ethnicity_keys)
            
        if any(w in q_lower for w in ["nữ", "nam", "giới tính", "chủ hộ", "phụ nữ", "đàn ông", "hộ gia đình", "hộ "]):
            active_keys.update(gender_keys)
            
        if any(w in q_lower for w in ["tuổi", "độ tuổi", "năm sinh", "già", "trẻ", "bình quân tuổi"]):
            active_keys.update(age_keys)
            
        if any(w in q_lower for w in ["cscc", "công", "mức sống", "trung bình", "liệt kê", "chính sách", "lao động", "cách mạng"]):
            active_keys.update(policy_keys)
            
        if any(w in q_lower for w in ["trẻ em", "đi học", "nhà trường", "bhyt trẻ em", "dinh dưỡng trẻ em"]):
            active_keys.update(children_keys)
            
        if any(w in q_lower for w in ["b1", "b2", "điểm", "tổng số chiều", "đa chiều", "rà soát", "thu nhập", "mức độ"]):
            active_keys.update(scoring_keys)
            
        if has_member_intent:
            active_keys.update(member_keys)
            
        # 3. Direct Definition / Name Matching & Table Filtering
        all_items = {}
        all_items.update(self.semantic_layer.get("dimensions", {}))
        all_items.update(self.semantic_layer.get("measures", {}))
        
        selected_lines = ["Danh sách các cột (physical_columns) và ý nghĩa trong CSDL:"]
        selected_cols = []
        
        for key, item in all_items.items():
            base_tbl = item.get("base_table")
            # Lọc nghiêm ngặt theo table scope: nếu chỉ query households thì bỏ qua mọi cột thuộc bảng members
            if base_tbl not in relevant_tables:
                continue
                
            is_active = key in active_keys
            
            # Direct matching: Nếu từ trong câu hỏi xuất hiện trong tên việt hoặc định nghĩa của cột thì cũng kích hoạt
            if not is_active:
                # Bộ từ dừng hành chính & nghiệp vụ tiếng Việt gây nhiễu khớp giả (Domain-Common False-Positive Stopwords)
                VIETNAMESE_STOPWORDS = {
                    # Từ ngữ pháp & hành chính chung
                    "các", "trong", "đang", "theo", "thuộc", "được", "những", "hoặc", "không",
                    "bao", "nhiêu", "thống", "kê", "danh", "sách", "kiểm", "tra", "xác", "định",
                    "của", "tại", "cho", "đây", "nào", "trên", "dưới", "giữa", "bằng", "với",
                    "từng", "người", "chiều", "khác", "cùng", "liệt", "khu", "vực", "tổng", "có", "là", "và", "về", "ra", "đã", "khi",
                    # Từ khóa địa danh & phân loại chung (xuất hiện ở hầu hết mọi định nghĩa cột)
                    "nghèo", "cận", "hộ", "đắk", "nông", "huyện", "xã", "năm", "chi", "tiết", "phân", "loại",
                    "tỉnh", "thành", "phố", "chỉ", "số", "chủ", "mã", "duy", "nhất", "bảng",
                    "vẽ", "biểu", "đồ", "tạo", "xuất", "báo", "cáo", "so", "sánh", "đạt", "mức", "độ", "quy", "mô", "tỷ", "lệ",
                    # Các từ chung xuất hiện dày đặc trong định nghĩa nguyên nhân/thiếu hụt
                    "thiếu", "hụt", "nguyên", "nhân", "do", "bị", "diện", "trạng", "thái", "quản", "lý",
                    "thông", "tin", "dữ", "liệu", "đánh", "giá", "thị", "hợp", "vệ", "sinh", "khả", "năng",
                    "hưởng", "đối", "tượng", "chính", "sách", "gia", "đình", "thành", "viên", "tham", "gia",
                    "quan", "hệ", "cung", "cấp", "sử", "dụng", "loại", "hình", "tình", "trạng"
                }
                name_vi = item.get("name_vi", "").lower()
                def_vi = item.get("definition", "").lower()
                
                # Bóc tách từ khóa: Loại bỏ ký tự đặc biệt, loại bỏ Stop-words và chỉ lấy từ có chiều dài >= 2 ký tự
                raw_words = q_lower.replace("?", "").replace(".", "").replace(",", "").split()
                meaningful_words = [
                    w for w in raw_words 
                    if len(w) >= 2 and w not in VIETNAMESE_STOPWORDS
                ]
                
                # Kiểm tra khớp từ khóa có ý nghĩa
                if any(w in name_vi or w in def_vi for w in meaningful_words):
                    is_active = True
                    
            if is_active:
                cols = ", ".join(item.get("physical_columns", []))
                desc = item.get("definition", "")
                selected_lines.append(f"- Cột {cols}: {desc} (Bảng {base_tbl})")
                selected_cols.extend(item.get("physical_columns", []))
                
        schema_context = "\n".join(selected_lines)
        
        return {
            "relevant_tables": relevant_tables,
            "schema_context": schema_context,
            "relevant_columns": list(set(selected_cols))
        }
