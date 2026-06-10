# -*- coding: utf-8 -*-
"""
Module xây dựng Semantic Layer cho chatbot Q&A.
Tải Schema Graph để kiểm tra sự tồn tại của các cột vật lý,
từ đó định nghĩa các Dimensions, Measures, Metrics, Business Terms và các ví dụ truy vấn mẫu.
"""

from __future__ import annotations
import json
import os
from pathlib import Path
import datetime as dt
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROCESSED_DIR = PROJECT_ROOT / "Intern" / "Processed"
METADATA_DIR = PROCESSED_DIR / "metadata"
QUERY_CONTROL_METADATA_DIR = METADATA_DIR / "query_control"
SCHEMA_GRAPH_PATH = QUERY_CONTROL_METADATA_DIR / "schema_graph.json"
SEMANTIC_LAYER_PATH = QUERY_CONTROL_METADATA_DIR / "semantic_layer.json"
REPORT_PATH = QUERY_CONTROL_METADATA_DIR / "metadata_build_report.md"

def load_schema_graph() -> dict[str, Any]:
    """Tải Schema Graph từ file JSON."""
    if not SCHEMA_GRAPH_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy Schema Graph tại {SCHEMA_GRAPH_PATH}. Vui lòng chạy build_schema_graph.py trước.")
    with open(SCHEMA_GRAPH_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def check_columns_exist(schema_graph: dict[str, Any], table_name: str, required_cols: list[str]) -> tuple[bool, list[str]]:
    """Kiểm tra xem các cột yêu cầu có tồn tại trong bảng tương ứng của Schema Graph hay không."""
    nodes = schema_graph.get("nodes", {})
    if table_name not in nodes:
        return False, required_cols
    
    existing_cols = nodes[table_name].get("columns", {})
    missing_cols = []
    for col in required_cols:
        if col not in existing_cols:
            missing_cols.append(col)
            
    return len(missing_cols) == 0, missing_cols

def main() -> None:
    schema_graph = load_schema_graph()
    
    # 1. Định nghĩa Dimensions và ánh xạ vật lý
    dimensions_def = {
        "year": {
            "name_vi": "Năm dữ liệu",
            "definition": "Năm rà soát, khảo sát",
            "semantic_type": "time",
            "base_table": "households",
            "physical_columns": ["administrative.year"],
            "allowed_for_group_by": True,
            "allowed_for_filter": True,
            "query_examples": ["năm 2024", "theo năm", "năm 2023", "năm nào"]
        },
        "district": {
            "name_vi": "Huyện/Thành phố",
            "definition": "Đơn vị hành chính cấp huyện tỉnh Đắk Nông",
            "semantic_type": "geography",
            "base_table": "households",
            "physical_columns": ["administrative.district"],
            "allowed_for_group_by": True,
            "allowed_for_filter": True,
            "query_examples": ["theo huyện", "từng huyện", "huyện nào"]
        },
        "commune": {
            "name_vi": "Xã/Phường/Thị trấn",
            "definition": "Đơn vị hành chính cấp xã tỉnh Đắk Nông",
            "semantic_type": "geography",
            "base_table": "households",
            "physical_columns": ["administrative.commune"],
            "allowed_for_group_by": True,
            "allowed_for_filter": True,
            "query_examples": ["theo xã", "xã nào", "ở xã", "xã thuộc huyện"]
        },
        "poverty_status": {
            "name_vi": "Phân loại hộ nghèo/cận nghèo",
            "definition": "Phân loại hộ rà soát (Nghèo, Cận nghèo, Hộ không nghèo...)",
            "semantic_type": "category",
            "base_table": "households",
            "physical_columns": ["classify"],
            "allowed_for_group_by": True,
            "allowed_for_filter": True,
            "query_examples": ["hộ nghèo", "hộ cận nghèo", "trạng thái nghèo"]
        },
        "household_id": {
            "name_vi": "Mã hộ gia đình",
            "definition": "Mã số định danh duy nhất của hộ gia đình",
            "semantic_type": "id",
            "base_table": "households",
            "physical_columns": ["family.code"],
            "allowed_for_group_by": False,
            "allowed_for_filter": True,
            "query_examples": ["mã hộ", "hộ gia đình có mã"]
        },
        "gender": {
            "name_vi": "Giới tính chủ hộ",
            "definition": "Giới tính của chủ hộ (Nam/Nữ)",
            "semantic_type": "category",
            "base_table": "households",
            "physical_columns": ["family.hostGender"],
            "allowed_for_group_by": True,
            "allowed_for_filter": True,
            "query_examples": ["chủ hộ là nam", "giới tính chủ hộ"]
        },
        "ethnicity": {
            "name_vi": "Dân tộc chủ hộ",
            "definition": "Thành phần dân tộc của chủ hộ",
            "semantic_type": "category",
            "base_table": "households",
            "physical_columns": ["family.ethnicity"],
            "allowed_for_group_by": True,
            "allowed_for_filter": True,
            "query_examples": ["theo dân tộc", "dân tộc thiểu số"]
        },
        "local_ethnicity": {
            "name_vi": "Dân tộc tại chỗ",
            "definition": "Chỉ số xác định hộ có phải dân tộc thiểu số tại chỗ hay không (True/False)",
            "semantic_type": "boolean",
            "base_table": "households",
            "physical_columns": ["family.isDTTC"],
            "allowed_for_group_by": True,
            "allowed_for_filter": True,
            "query_examples": ["dân tộc tại chỗ", "đồng bào tại chỗ"]
        },
        "age_group": {
            "name_vi": "Năm sinh chủ hộ",
            "definition": "Năm sinh của chủ hộ để tính độ tuổi",
            "semantic_type": "time",
            "base_table": "households",
            "physical_columns": ["family.hostBirthYear"],
            "allowed_for_group_by": True,
            "allowed_for_filter": True,
            "query_examples": ["chủ hộ sinh năm"]
        },
        "host_name": {
            "name_vi": "Tên chủ hộ",
            "definition": "Họ và tên của chủ hộ gia đình",
            "semantic_type": "text",
            "base_table": "households",
            "physical_columns": ["family.hostName"],
            "allowed_for_group_by": False,
            "allowed_for_filter": True,
            "query_examples": ["tên chủ hộ", "chủ hộ tên là", "tên của chủ hộ"]
        }
    }
    
    # 2. Định nghĩa Measures
    measures_def = {
        "b1_score": {
            "name_vi": "Điểm B1",
            "definition": "Điểm phiếu rà soát thông tin B1",
            "base_table": "households",
            "physical_columns": ["b1Point"],
            "default_aggregation": "avg",
            "allowed_aggregations": ["avg", "min", "max", "sum"],
            "query_examples": ["điểm B1", "trung bình điểm B1"]
        },
        "b2_score": {
            "name_vi": "Điểm B2",
            "definition": "Điểm phiếu rà soát thông tin B2",
            "base_table": "households",
            "physical_columns": ["b2Point"],
            "default_aggregation": "avg",
            "allowed_aggregations": ["avg", "min", "max", "sum"],
            "query_examples": ["điểm B2", "trung bình điểm B2"]
        },
        "deprivation_count": {
            "name_vi": "Số chỉ số thiếu hụt",
            "definition": "Tổng số chỉ số thiếu hụt dịch vụ xã hội cơ bản của hộ",
            "base_table": "households",
            "physical_columns": ["deprivation.totalCount"],
            "default_aggregation": "avg",
            "allowed_aggregations": ["avg", "min", "max", "sum"],
            "query_examples": ["số chỉ số thiếu hụt", "thiếu hụt trung bình"]
        },
        "household_size": {
            "name_vi": "Số thành viên hộ",
            "definition": "Số nhân khẩu trong hộ gia đình",
            "base_table": "households",
            "physical_columns": ["family.numberOfMembers"],
            "default_aggregation": "avg",
            "allowed_aggregations": ["avg", "sum", "min", "max"],
            "query_examples": ["quy mô hộ", "số nhân khẩu"]
        }
    }
    
    # Kiểm tra và ánh xạ Dimensions sang định dạng đầu ra
    dimensions = {}
    for k, d in dimensions_def.items():
        ok, missing = check_columns_exist(schema_graph, d["base_table"], d["physical_columns"])
        d_out = d.copy()
        if ok:
            d_out["status"] = "ready"
        else:
            d_out["status"] = "ambiguous"
            d_out["candidate_columns"] = d["physical_columns"]
            d_out["reason"] = f"Không tìm thấy các cột vật lý: {missing}"
        dimensions[k] = d_out
        
    # Kiểm tra và ánh xạ Measures sang định dạng đầu ra
    measures = {}
    for k, m in measures_def.items():
        ok, missing = check_columns_exist(schema_graph, m["base_table"], m["physical_columns"])
        m_out = m.copy()
        if ok:
            m_out["status"] = "ready"
        else:
            m_out["status"] = "ambiguous"
            m_out["candidate_columns"] = m["physical_columns"]
            m_out["reason"] = f"Không tìm thấy các cột vật lý: {missing}"
        measures[k] = m_out
        
    # 3. Định nghĩa Metrics
    metrics_def = {
        "household_count": {
            "name_vi": "Số hộ gia đình",
            "definition": "Đếm tổng số hộ gia đình trong danh sách",
            "base_table": "households",
            "expression": "COUNT(*)",
            "filters": [],
            "allowed_dimensions": ["year", "district", "commune", "poverty_status"],
            "required_columns": ["family.code"],
            "query_examples": ["tổng số hộ", "bao nhiêu hộ gia đình", "thống kê số hộ theo huyện"]
        },
        "poor_household_count": {
            "name_vi": "Số hộ nghèo",
            "definition": "Đếm số hộ có trạng thái phân loại là Nghèo",
            "base_table": "households",
            "expression": "COUNT(*)",
            "filters": [
                {
                    "field": "classify",
                    "operator": "=",
                    "value": "Hộ nghèo"
                }
            ],
            "allowed_dimensions": ["year", "district", "commune"],
            "required_columns": ["classify"],
            "query_examples": ["số hộ nghèo", "bao nhiêu hộ nghèo", "hộ nghèo theo huyện"]
        },
        "near_poor_household_count": {
            "name_vi": "Số hộ cận nghèo",
            "definition": "Đếm số hộ có trạng thái phân loại là Cận nghèo",
            "base_table": "households",
            "expression": "COUNT(*)",
            "filters": [
                {
                    "field": "classify",
                    "operator": "=",
                    "value": "Hộ cận nghèo"
                }
            ],
            "allowed_dimensions": ["year", "district", "commune"],
            "required_columns": ["classify"],
            "query_examples": ["số hộ cận nghèo", "bao nhiêu hộ cận nghèo", "hộ cận nghèo theo huyện"]
        },
        "avg_b1_score": {
            "name_vi": "Điểm B1 trung bình",
            "definition": "Tính điểm trung bình phiếu B1",
            "base_table": "households",
            "expression": "AVG(CAST(b1Point AS FLOAT))",
            "filters": [],
            "allowed_dimensions": ["year", "district", "commune", "poverty_status"],
            "required_columns": ["b1Point"],
            "query_examples": ["điểm B1 trung bình", "bản điểm B1 trung bình theo xã"]
        },
        "avg_b2_score": {
            "name_vi": "Điểm B2 trung bình",
            "definition": "Tính điểm trung bình phiếu B2",
            "base_table": "households",
            "expression": "AVG(CAST(b2Point AS FLOAT))",
            "filters": [],
            "allowed_dimensions": ["year", "district", "commune", "poverty_status"],
            "required_columns": ["b2Point"],
            "query_examples": ["điểm B2 trung bình", "điểm B2 trung bình theo xã"]
        },
        "member_count": {
            "name_vi": "Số nhân khẩu",
            "definition": "Tính tổng số nhân khẩu/thành viên",
            "base_table": "members",
            "expression": "COUNT(*)",
            "filters": [],
            "allowed_dimensions": ["year", "district", "commune"],
            "required_columns": ["family.code"],
            "query_examples": ["tổng số nhân khẩu", "bao nhiêu thành viên", "số dân theo huyện"]
        },
        "avg_age": {
            "name_vi": "Độ tuổi trung bình",
            "definition": "Độ tuổi trung bình của các nhân khẩu (năm rà soát - năm sinh)",
            "base_table": "members",
            "expression": "ROUND(AVG(members.\"administrative.year\" - members.\"member.birthYear\"), 2)",
            "filters": [],
            "allowed_dimensions": ["year", "district", "commune"],
            "required_columns": ["administrative.year", "member.birthYear"],
            "query_examples": ["độ tuổi trung bình", "tuổi trung bình của nhân khẩu", "độ tuổi trung bình của thành viên"]
        },
        "poor_rate": {
            "name_vi": "Tỷ lệ hộ nghèo",
            "definition": "Tỷ lệ phần trăm hộ nghèo trên tổng số hộ",
            "base_table": "households",
            "expression": "ROUND(100.0 * SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 ELSE 0 END) / COUNT(*), 2)",
            "filters": [],
            "allowed_dimensions": ["year", "district", "commune"],
            "required_columns": ["classify"],
            "query_examples": ["tỷ lệ hộ nghèo", "tỉ lệ nghèo", "tỷ lệ nghèo theo huyện"]
        },
        "near_poor_rate": {
            "name_vi": "Tỷ lệ hộ cận nghèo",
            "definition": "Tỷ lệ phần trăm hộ cận nghèo trên tổng số hộ",
            "base_table": "households",
            "expression": "ROUND(100.0 * SUM(CASE WHEN classify = 'Hộ cận nghèo' THEN 1 ELSE 0 END) / COUNT(*), 2)",
            "filters": [],
            "allowed_dimensions": ["year", "district", "commune"],
            "required_columns": ["classify"],
            "query_examples": ["tỷ lệ hộ cận nghèo", "tỉ lệ cận nghèo", "tỷ lệ cận nghèo theo huyện"]
        }
    }
    
    # Kiểm tra và ánh xạ Metrics sang định dạng đầu ra
    metrics = {}
    for k, m in metrics_def.items():
        ok, missing = check_columns_exist(schema_graph, m["base_table"], m["required_columns"])
        m_out = m.copy()
        if ok:
            m_out["status"] = "ready"
        else:
            m_out["status"] = "incomplete"
            m_out["missing"] = missing
            m_out["reason"] = f"Thiếu cột vật lý bắt buộc để tính toán metric: {missing}"
        metrics[k] = m_out
        
    # 4. Định nghĩa Business Terms
    business_terms = {
        "hộ nghèo": {
            "definition": "Thuật ngữ chỉ nhóm hộ gia đình được phân loại là Nghèo",
            "maps_to": {
                "metric": "poor_household_count",
                "dimension": "poverty_status",
                "filter_value": "Hộ nghèo"
            },
            "examples": ["số hộ nghèo", "hộ nghèo theo huyện", "danh sách hộ nghèo"]
        },
        "hộ cận nghèo": {
            "definition": "Thuật ngữ chỉ nhóm hộ gia đình được phân loại là Cận nghèo",
            "maps_to": {
                "metric": "near_poor_household_count",
                "dimension": "poverty_status",
                "filter_value": "Hộ cận nghèo"
            },
            "examples": ["số hộ cận nghèo", "hộ cận nghèo theo xã", "danh sách hộ cận nghèo"]
        },
        "theo huyện": {
            "definition": "Nhóm kết quả theo đơn vị hành chính cấp huyện",
            "maps_to": {
                "dimension": "district"
            }
        },
        "theo xã": {
            "definition": "Nhóm kết quả theo đơn vị hành chính cấp xã",
            "maps_to": {
                "dimension": "commune"
            }
        },
        "theo năm": {
            "definition": "Nhóm kết quả theo năm rà soát",
            "maps_to": {
                "dimension": "year"
            }
        },
        "chủ hộ là nam": {
            "definition": "Bộ lọc giới tính chủ hộ là Nam",
            "maps_to": {
                "dimension": "gender",
                "filter_value": "Nam"
            }
        },
        "chủ hộ là nữ": {
            "definition": "Bộ lọc giới tính chủ hộ là Nữ",
            "maps_to": {
                "dimension": "gender",
                "filter_value": "Nữ"
            }
        },
        "dân tộc thiểu số": {
            "definition": "Hộ gia đình có chủ hộ là người dân tộc thiểu số (khác Kinh)",
            "maps_to": {
                "dimension": "ethnicity",
                "operator": "!=",
                "filter_value": "Kinh"
            }
        }
    }
    
    # 5. Định nghĩa Query Examples
    query_examples = [
        {
            "example_id": "qe_poor_by_district_2024",
            "text": "Số hộ nghèo theo huyện năm 2024",
            "maps_to": {
                "task_type": "aggregate_query",
                "metrics": ["poor_household_count"],
                "dimensions": ["district"],
                "filters": [
                    {"field": "year", "operator": "=", "value": 2024}
                ],
                "sort": None,
                "limit": None,
                "output_type": "table"
            }
        },
        {
            "example_id": "qe_top_poor_district_2024",
            "text": "Huyện nào có nhiều hộ nghèo nhất năm 2024",
            "maps_to": {
                "task_type": "topk_query",
                "metrics": ["poor_household_count"],
                "dimensions": ["district"],
                "filters": [
                    {"field": "year", "operator": "=", "value": 2024}
                ],
                "sort": {"field": "poor_household_count", "direction": "desc"},
                "limit": 1,
                "output_type": "text"
            }
        },
        {
            "example_id": "qe_near_poor_list_tuy_duc_2023",
            "text": "Danh sách hộ cận nghèo ở huyện Tuy Đức năm 2023",
            "maps_to": {
                "task_type": "detail_query",
                "metrics": ["near_poor_household_count"],
                "dimensions": ["household_id", "commune"],
                "filters": [
                    {"field": "year", "operator": "=", "value": 2023},
                    {"field": "district", "operator": "=", "value": "Huyện Tuy Đức"}
                ],
                "sort": None,
                "limit": 100,
                "output_type": "table"
            }
        },
        {
            "example_id": "qe_compare_poor_2023_2024",
            "text": "So sánh số lượng hộ nghèo giữa năm 2023 và 2024",
            "maps_to": {
                "task_type": "comparison_query",
                "metrics": ["poor_household_count"],
                "dimensions": ["year"],
                "filters": [
                    {"field": "year", "operator": "IN", "value": [2023, 2024]}
                ],
                "sort": {"field": "year", "direction": "asc"},
                "limit": None,
                "output_type": "table"
            }
        }
    ]
    
    semantic_layer = {
        "version": "1.0",
        "generated_at": dt.datetime.now().isoformat(),
        "dimensions": dimensions,
        "measures": measures,
        "metrics": metrics,
        "business_terms": business_terms,
        "query_examples": query_examples
    }
    
    with open(SEMANTIC_LAYER_PATH, "w", encoding="utf-8") as f:
        json.dump(semantic_layer, f, ensure_ascii=False, indent=2)
    print(f"Đã lưu Semantic Layer tại: {SEMANTIC_LAYER_PATH}")
    
    # 6. Ghi tiếp báo cáo vào metadata_build_report.md
    report_additions = []
    report_additions.append("\n## 3. Kết quả ánh xạ Semantic Layer")
    report_additions.append(f"- **Tổng số Dimensions đã tạo:** {len(dimensions)}")
    report_additions.append(f"- **Tổng số Measures đã tạo:** {len(measures)}")
    report_additions.append(f"- **Tổng số Metrics đã định nghĩa:** {len(metrics)}")
    report_additions.append(f"- **Tổng số Business Terms định nghĩa:** {len(business_terms)}")
    report_additions.append(f"- **Tổng số Query Examples để test/embed:** {len(query_examples)}\n")
    
    report_additions.append("### Trạng thái các Metrics:")
    for m_id, m_val in metrics.items():
        report_additions.append(f"- **{m_id}**: {m_val['status']} (Lý do: {m_val.get('reason', 'Đầy đủ cột vật lý')})")
        
    report_additions.append("\n### Trạng thái các Dimensions:")
    for d_id, d_val in dimensions.items():
        report_additions.append(f"- **{d_id}**: {d_val['status']} (Lý do: {d_val.get('reason', 'Đầy đủ cột vật lý')})")
        
    with open(REPORT_PATH, "a", encoding="utf-8") as f:
        f.write("\n" + "\n".join(report_additions))
    print(f"Đã cập nhật báo cáo metadata tại: {REPORT_PATH}")

if __name__ == "__main__":
    main()
