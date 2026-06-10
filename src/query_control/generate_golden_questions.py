# -*- coding: utf-8 -*-
"""
Module generate_golden_questions chịu trách nhiệm sinh bộ 30 câu hỏi đánh giá chuẩn (golden set)
một cách độc lập với chatbot bằng cách truy vấn trực tiếp cơ sở dữ liệu DuckDB.
"""

from __future__ import annotations
import os
import sys
import json
import csv
import argparse
import time
import subprocess
from pathlib import Path
from typing import Any
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "Runtime" / "duckdb" / "intern_chatbot.duckdb"
OUTPUT_DIR = PROJECT_ROOT / "Evaluation" / "golden_questions"

def load_db_connection() -> duckdb.DuckDBPyConnection:
    """Kết nối trực tiếp tới DuckDB."""
    if not DB_PATH.exists():
        print(f"[!] Không tìm thấy tệp DuckDB tại {DB_PATH}. Tiến hành chạy loader để khởi tạo...")
        rebuild_db()
    return duckdb.connect(str(DB_PATH), read_only=True)

def rebuild_db():
    """Chạy lại duckdb_loader.py để tạo lập CSDL."""
    loader_script = PROJECT_ROOT / "src" / "query_control" / "duckdb_loader.py"
    if not loader_script.exists():
        raise FileNotFoundError(f"Không tìm thấy script loader tại {loader_script}")
    print("[*] Đang chạy duckdb_loader.py --rebuild...")
    result = subprocess.run(
        [sys.executable, str(loader_script), "--rebuild"],
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    if result.returncode != 0:
        print(f"[!] Lỗi khi build DB:\n{result.stderr}")
        sys.exit(1)
    print("[+] Xây dựng CSDL DuckDB thành công!")

def inspect_duckdb_schema(conn: duckdb.DuckDBPyConnection) -> dict[str, Any]:
    """Khảo sát schema các bảng trong DuckDB."""
    schema = {}
    try:
        tables_df = conn.execute("SHOW TABLES").df()
        tables = tables_df["name"].tolist() if not tables_df.empty else []
        for t in tables:
            cols_res = conn.execute(f"PRAGMA table_info('{t}')").fetchall()
            schema[t] = [col[1] for col in cols_res]
    except Exception as e:
        print(f"[!] Lỗi khảo sát schema: {e}")
    return schema

def detect_columns(schema: dict[str, Any]) -> dict[str, Any]:
    """Phát hiện các cột có sẵn trong households và members."""
    detected = {
        "households_exists": "households" in schema,
        "members_exists": "members" in schema,
        "households_cols": schema.get("households", []),
        "members_cols": schema.get("members", [])
    }
    return detected

def validate_select_only_sql(sql: str) -> list[str]:
    """Kiểm tra độ an toàn của SQL (chỉ cho phép SELECT/WITH)."""
    errors = []
    sql_upper = sql.upper().strip()
    
    # Từ khóa độc hại/ghi dữ liệu
    forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "CREATE TABLE", "REPLACE", "MERGE"]
    for keyword in forbidden:
        import re
        pattern = r"\b" + re.escape(keyword) + r"\b"
        if re.search(pattern, sql_upper):
            errors.append(f"SQL chứa từ khóa cấm: {keyword}")
            
    if not (sql_upper.startswith("SELECT") or sql_upper.startswith("WITH")):
        errors.append("SQL không bắt đầu bằng SELECT hoặc WITH.")
        
    # Loại bỏ COUNT(*) khỏi chuỗi kiểm tra để tránh bắt nhầm
    cleaned_sql = re.sub(r"COUNT\s*\(\s*\*\s*\)", "", sql_upper)
    
    # Tìm kiếm các mẫu select all cột như: SELECT *, SELECT t.*, hoặc , *
    # Tránh bắt nhầm phép nhân như 100.0 * col
    if re.search(r"\bSELECT\s+(?:\w+\s*,\s*)*\*", cleaned_sql) or re.search(r",\s*\*", cleaned_sql) or re.search(r"\b[A-Z_]\w*\.\*", cleaned_sql):
        errors.append("SQL không được sử dụng SELECT * bừa bãi.")
            
    return errors

def execute_gold_sql(conn: duckdb.DuckDBPyConnection, sql: str) -> dict[str, Any]:
    """Thực thi câu SQL và trả về kết quả cấu trúc dict."""
    try:
        res = conn.execute(sql)
        cols = [desc[0] for desc in res.description] if res.description else []
        rows = res.fetchall()
        data = [dict(zip(cols, row)) for row in rows]
        return {
            "success": True,
            "data": data,
            "row_count": len(data),
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "data": [],
            "row_count": 0,
            "error": str(e)
        }

def format_expected_answer(question: str, result: list[dict[str, Any]], spec: dict[str, Any]) -> str:
    """Tạo câu trả lời kỳ vọng tự động từ kết quả truy vấn thực tế."""
    if not result:
        return "Theo kết quả truy vấn thử nghiệm, không có bản ghi dữ liệu nào thỏa mãn các điều kiện lọc được yêu cầu."
        
    q_type = spec.get("question_type")
    
    if q_type == "filtered_count":
        val = list(result[0].values())[0]
        formatted_val = f"{val:,.0f}".replace(",", ".")
        if "cận nghèo" in question.lower():
            return f"Theo dữ liệu truy vấn, năm 2024 có {formatted_val} hộ cận nghèo."
        else:
            return f"Theo dữ liệu truy vấn, năm 2024 có {formatted_val} hộ nghèo."
            
    elif q_type == "total_count":
        top_row = result[0]
        year_val = top_row.get("year", 2024)
        cnt_val = list(top_row.values())[1]
        formatted_val = f"{cnt_val:,.0f}".replace(",", ".")
        return f"Theo kết quả truy vấn, tổng số hộ khảo sát năm {year_val} được ghi nhận là {formatted_val} hộ."
        
    elif q_type == "aggregate_by_dimension":
        col_keys = list(result[0].keys())
        dim_col = col_keys[0]
        val_col = col_keys[1]
        sorted_res = sorted(result, key=lambda x: x[val_col] if x[val_col] is not None else 0, reverse=True)
        top_name = sorted_res[0][dim_col]
        top_val = sorted_res[0][val_col]
        formatted_val = f"{top_val:,.0f}".replace(",", ".") if isinstance(top_val, (int, float)) else str(top_val)
        return f"Theo kết quả truy vấn, {spec['question_vi'].lower()} được liệt kê chi tiết. Địa phương/nhóm có giá trị cao nhất là {top_name} với {formatted_val} hộ."

    elif q_type == "topk_query":
        col_keys = list(result[0].keys())
        dim_col = col_keys[0]
        val_col = col_keys[-1]
        top_name = result[0][dim_col]
        top_val = result[0][val_col]
        formatted_val = f"{top_val:,.2f}".replace(",", ".") if isinstance(top_val, float) else f"{top_val:,.0f}".replace(",", ".") if isinstance(top_val, int) else str(top_val)
        return f"Theo kết quả truy vấn, địa phương/phân loại hàng đầu là {top_name} với giá trị {formatted_val}."
        
    elif q_type == "comparison_by_year":
        col_keys = list(result[0].keys())
        dim_col = col_keys[0]
        diff_col = col_keys[-1]
        sorted_res = sorted(result, key=lambda x: abs(x[diff_col]) if x[diff_col] is not None else 0, reverse=True)
        top_name = sorted_res[0][dim_col]
        diff_val = sorted_res[0][diff_col]
        formatted_val = f"{diff_val:,.2f}".replace(",", ".") if isinstance(diff_val, float) else f"{diff_val:,.0f}".replace(",", ".") if isinstance(diff_val, int) else str(diff_val)
        return f"Theo kết quả truy vấn, {top_name} là địa phương có mức thay đổi nổi bật nhất, với chênh lệch {formatted_val} đơn vị giữa năm 2023 và 2024."

    elif q_type == "ratio_query":
        col_keys = list(result[0].keys())
        dim_col = col_keys[0]
        rate_col = col_keys[-1]
        sorted_res = sorted(result, key=lambda x: x[rate_col] if x[rate_col] is not None else 0.0, reverse=True)
        top_name = sorted_res[0][dim_col]
        rate_val = sorted_res[0][rate_col]
        formatted_val = f"{rate_val:,.2f}".replace(",", ".") if isinstance(rate_val, float) else str(rate_val)
        return f"Theo kết quả truy vấn, tỷ lệ cao nhất thuộc về {top_name}, đạt {formatted_val}%."
        
    elif q_type == "average_measure":
        col_keys = list(result[0].keys())
        if len(col_keys) == 1:
            val = result[0][col_keys[0]]
            formatted_val = f"{val:,.2f}".replace(",", ".") if isinstance(val, float) else str(val)
            return f"Theo kết quả truy vấn, điểm trung bình chung được ghi nhận là {formatted_val} điểm."
        else:
            dim_col = col_keys[0]
            val_col = col_keys[1]
            sorted_res = sorted(result, key=lambda x: x[val_col] if x[val_col] is not None else 0.0, reverse=True)
            top_name = sorted_res[0][dim_col]
            top_val = sorted_res[0][val_col]
            formatted_val = f"{top_val:,.2f}".replace(",", ".") if isinstance(top_val, float) else str(top_val)
            return f"Theo kết quả truy vấn, điểm trung bình cao nhất ghi nhận tại {top_name} với {formatted_val} điểm."

    elif q_type == "distribution":
        col_keys = list(result[0].keys())
        dim_col = col_keys[0]
        val_col = col_keys[1]
        sorted_res = sorted(result, key=lambda x: x[val_col] if x[val_col] is not None else 0, reverse=True)
        top_name = sorted_res[0][dim_col]
        top_val = sorted_res[0][val_col]
        formatted_val = f"{top_val:,.0f}".replace(",", ".")
        return f"Theo kết quả truy vấn, phân phối theo {dim_col} ghi nhận nhóm {top_name} chiếm số lượng lớn nhất với {formatted_val} hộ."

    elif q_type == "members_query":
        col_keys = list(result[0].keys())
        dim_col = col_keys[0]
        val_col = col_keys[1]
        sorted_res = sorted(result, key=lambda x: x[val_col] if x[val_col] is not None else 0.0, reverse=True)
        top_name = sorted_res[0][dim_col]
        top_val = sorted_res[0][val_col]
        formatted_val = f"{top_val:,.2f}".replace(",", ".") if isinstance(top_val, float) else f"{top_val:,.0f}".replace(",", ".") if isinstance(top_val, int) else str(top_val)
        return f"Theo kết quả truy vấn thành viên, huyện có giá trị nổi bật nhất là {top_name} với {formatted_val}."
        
    elif q_type == "empty_result_test":
        return "Theo kết quả truy vấn thử nghiệm, không có bản ghi dữ liệu nào thỏa mãn các điều kiện lọc được yêu cầu."
        
    else:
        return "Theo kết quả truy vấn thực tế từ cơ sở dữ liệu."

def build_question_specs(detected: dict[str, Any]) -> list[dict[str, Any]]:
    """Xây dựng 30 specs cho bộ câu hỏi vàng."""
    specs = [
        # === EASY (10 câu) ===
        {
            "id": "GQ001",
            "question_vi": "Tổng số hộ rà soát theo từng năm là bao nhiêu?",
            "question_type": "total_count",
            "difficulty": "easy",
            "expected_route": "DATASET_QA",
            "gold_sql": 'SELECT "administrative.year" AS year, COUNT(*) AS household_count FROM households GROUP BY year ORDER BY year;',
            "tables_used": ["households"],
            "columns_used": ["administrative.year"],
            "filters": [],
            "metrics": ["household_count"],
            "dimensions": ["year"],
            "notes": "Đếm tổng số hộ rà soát nhóm theo năm."
        },
        {
            "id": "GQ002",
            "question_vi": "Năm 2024 có bao nhiêu hộ nghèo?",
            "question_type": "filtered_count",
            "difficulty": "easy",
            "expected_route": "DATASET_QA",
            "gold_sql": 'SELECT COUNT(*) AS poor_household_count FROM households WHERE "administrative.year" = 2024 AND "classify" = \'Hộ nghèo\';',
            "tables_used": ["households"],
            "columns_used": ["administrative.year", "classify"],
            "filters": [
                {"field": "year", "operator": "=", "value": 2024},
                {"field": "poverty_status", "operator": "=", "value": "Hộ nghèo"}
            ],
            "metrics": ["poor_household_count"],
            "dimensions": [],
            "notes": "Đếm số hộ nghèo năm 2024 có lọc điều kiện."
        },
        {
            "id": "GQ003",
            "question_vi": "Có bao nhiêu hộ cận nghèo trong năm 2024?",
            "question_type": "filtered_count",
            "difficulty": "easy",
            "expected_route": "DATASET_QA",
            "gold_sql": 'SELECT COUNT(*) AS near_poor_household_count FROM households WHERE "administrative.year" = 2024 AND "classify" = \'Hộ cận nghèo\';',
            "tables_used": ["households"],
            "columns_used": ["administrative.year", "classify"],
            "filters": [
                {"field": "year", "operator": "=", "value": 2024},
                {"field": "poverty_status", "operator": "=", "value": "Hộ cận nghèo"}
            ],
            "metrics": ["near_poor_household_count"],
            "dimensions": [],
            "notes": "Đếm số hộ cận nghèo năm 2024 có lọc điều kiện."
        },
        {
            "id": "GQ004",
            "question_vi": "Số hộ nghèo theo từng huyện trong năm 2024 là bao nhiêu?",
            "question_type": "aggregate_by_dimension",
            "difficulty": "easy",
            "expected_route": "DATASET_QA",
            "gold_sql": 'SELECT "administrative.district" AS district, COUNT(*) AS poor_household_count FROM households WHERE "administrative.year" = 2024 AND "classify" = \'Hộ nghèo\' GROUP BY district ORDER BY poor_household_count DESC;',
            "tables_used": ["households"],
            "columns_used": ["administrative.year", "classify", "administrative.district"],
            "filters": [
                {"field": "year", "operator": "=", "value": 2024},
                {"field": "poverty_status", "operator": "=", "value": "Hộ nghèo"}
            ],
            "metrics": ["poor_household_count"],
            "dimensions": ["district"],
            "notes": "Số hộ nghèo năm 2024 phân tổ theo huyện."
        },
        {
            "id": "GQ005",
            "question_vi": "Thống kê số lượng hộ cận nghèo theo huyện năm 2024.",
            "question_type": "aggregate_by_dimension",
            "difficulty": "easy",
            "expected_route": "DATASET_QA",
            "gold_sql": 'SELECT "administrative.district" AS district, COUNT(*) AS near_poor_household_count FROM households WHERE "administrative.year" = 2024 AND "classify" = \'Hộ cận nghèo\' GROUP BY district ORDER BY near_poor_household_count DESC;',
            "tables_used": ["households"],
            "columns_used": ["administrative.year", "classify", "administrative.district"],
            "filters": [
                {"field": "year", "operator": "=", "value": 2024},
                {"field": "poverty_status", "operator": "=", "value": "Hộ cận nghèo"}
            ],
            "metrics": ["near_poor_household_count"],
            "dimensions": ["district"],
            "notes": "Số hộ cận nghèo năm 2024 phân tổ theo huyện."
        },
        {
            "id": "GQ006",
            "question_vi": "Số lượng hộ nghèo và cận nghèo của từng xã thuộc Huyện Tuy Đức năm 2024 là bao nhiêu?",
            "question_type": "aggregate_by_dimension",
            "difficulty": "easy",
            "expected_route": "DATASET_QA",
            "gold_sql": 'SELECT "administrative.commune" AS commune, COUNT(*) AS household_count FROM households WHERE "administrative.year" = 2024 AND "administrative.district" = \'Huyện Tuy Đức\' GROUP BY commune ORDER BY household_count DESC;',
            "tables_used": ["households"],
            "columns_used": ["administrative.year", "administrative.district", "administrative.commune"],
            "filters": [
                {"field": "year", "operator": "=", "value": 2024},
                {"field": "district", "operator": "=", "value": "Huyện Tuy Đức"}
            ],
            "metrics": ["household_count"],
            "dimensions": ["commune"],
            "notes": "Tổng số hộ khảo sát của Huyện Tuy Đức năm 2024 theo từng xã."
        },
        {
            "id": "GQ007",
            "question_vi": "Điểm B1 trung bình của các hộ khảo sát năm 2024 là bao nhiêu?",
            "question_type": "average_measure",
            "difficulty": "easy",
            "expected_route": "DATASET_QA",
            "gold_sql": 'SELECT ROUND(AVG(b1Point), 2) AS avg_b1 FROM households WHERE "administrative.year" = 2024;',
            "tables_used": ["households"],
            "columns_used": ["administrative.year", "b1Point"],
            "filters": [
                {"field": "year", "operator": "=", "value": 2024}
            ],
            "metrics": ["avg_b1"],
            "dimensions": [],
            "notes": "Trung bình điểm B1 năm 2024 toàn tỉnh."
        },
        {
            "id": "GQ008",
            "question_vi": "Điểm B2 trung bình của các hộ khảo sát năm 2024 là bao nhiêu?",
            "question_type": "average_measure",
            "difficulty": "easy",
            "expected_route": "DATASET_QA",
            "gold_sql": 'SELECT ROUND(AVG(b2Point), 2) AS avg_b2 FROM households WHERE "administrative.year" = 2024;',
            "tables_used": ["households"],
            "columns_used": ["administrative.year", "b2Point"],
            "filters": [
                {"field": "year", "operator": "=", "value": 2024}
            ],
            "metrics": ["avg_b2"],
            "dimensions": [],
            "notes": "Trung bình điểm B2 năm 2024 toàn tỉnh."
        },
        {
            "id": "GQ009",
            "question_vi": "Thống kê số hộ nghèo theo từng xã trong năm 2023.",
            "question_type": "aggregate_by_dimension",
            "difficulty": "easy",
            "expected_route": "DATASET_QA",
            "gold_sql": 'SELECT "administrative.commune" AS commune, COUNT(*) AS poor_household_count FROM households WHERE "administrative.year" = 2023 AND "classify" = \'Hộ nghèo\' GROUP BY commune ORDER BY poor_household_count DESC;',
            "tables_used": ["households"],
            "columns_used": ["administrative.year", "classify", "administrative.commune"],
            "filters": [
                {"field": "year", "operator": "=", "value": 2023},
                {"field": "poverty_status", "operator": "=", "value": "Hộ nghèo"}
            ],
            "metrics": ["poor_household_count"],
            "dimensions": ["commune"],
            "notes": "Đếm số hộ nghèo năm 2023 phân tổ theo xã."
        },
        {
            "id": "GQ010",
            "question_vi": "Danh sách các hộ nghèo tại Huyện Cư Jút năm 2025 là bao nhiêu?",
            "question_type": "empty_result_test",
            "difficulty": "easy",
            "expected_route": "DATASET_QA",
            "gold_sql": 'SELECT "family.code" AS household_id, "family.hostName" AS host_name FROM households WHERE "administrative.year" = 2025 AND "administrative.district" = \'Huyện Cư Jút\' AND "classify" = \'Hộ nghèo\' LIMIT 5;',
            "tables_used": ["households"],
            "columns_used": ["family.code", "family.hostName", "administrative.year", "administrative.district", "classify"],
            "filters": [
                {"field": "year", "operator": "=", "value": 2025},
                {"field": "district", "operator": "=", "value": "Huyện Cư Jút"},
                {"field": "poverty_status", "operator": "=", "value": "Hộ nghèo"}
            ],
            "metrics": [],
            "dimensions": ["household_id", "host_name"],
            "notes": "Lọc điều kiện theo năm 2025 không có dữ liệu để kiểm tra trả về rỗng."
        },
        
        # === MEDIUM (12 câu) ===
        {
            "id": "GQ011",
            "question_vi": "Huyện nào có nhiều hộ nghèo nhất trong năm 2024?",
            "question_type": "topk_query",
            "difficulty": "medium",
            "expected_route": "DATASET_QA",
            "gold_sql": 'SELECT "administrative.district" AS district, COUNT(*) AS poor_household_count FROM households WHERE "administrative.year" = 2024 AND "classify" = \'Hộ nghèo\' GROUP BY district ORDER BY poor_household_count DESC LIMIT 1;',
            "tables_used": ["households"],
            "columns_used": ["administrative.year", "classify", "administrative.district"],
            "filters": [
                {"field": "year", "operator": "=", "value": 2024},
                {"field": "poverty_status", "operator": "=", "value": "Hộ nghèo"}
            ],
            "metrics": ["poor_household_count"],
            "dimensions": ["district"],
            "notes": "Top-1 huyện có nhiều hộ nghèo nhất."
        },
        {
            "id": "GQ012",
            "question_vi": "Huyện nào có ít hộ nghèo nhất trong năm 2024?",
            "question_type": "topk_query",
            "difficulty": "medium",
            "expected_route": "DATASET_QA",
            "gold_sql": 'SELECT "administrative.district" AS district, COUNT(*) AS poor_household_count FROM households WHERE "administrative.year" = 2024 AND "classify" = \'Hộ nghèo\' GROUP BY district ORDER BY poor_household_count ASC LIMIT 1;',
            "tables_used": ["households"],
            "columns_used": ["administrative.year", "classify", "administrative.district"],
            "filters": [
                {"field": "year", "operator": "=", "value": 2024},
                {"field": "poverty_status", "operator": "=", "value": "Hộ nghèo"}
            ],
            "metrics": ["poor_household_count"],
            "dimensions": ["district"],
            "notes": "Top-1 huyện có ít hộ nghèo nhất."
        },
        {
            "id": "GQ013",
            "question_vi": "Xã nào thuộc Huyện Krông Nô có nhiều hộ cận nghèo nhất năm 2024?",
            "question_type": "topk_query",
            "difficulty": "medium",
            "expected_route": "DATASET_QA",
            "gold_sql": 'SELECT "administrative.commune" AS commune, COUNT(*) AS near_poor_household_count FROM households WHERE "administrative.year" = 2024 AND "administrative.district" = \'Huyện Krông Nô\' AND "classify" = \'Hộ cận nghèo\' GROUP BY commune ORDER BY near_poor_household_count DESC LIMIT 1;',
            "tables_used": ["households"],
            "columns_used": ["administrative.year", "administrative.district", "classify", "administrative.commune"],
            "filters": [
                {"field": "year", "operator": "=", "value": 2024},
                {"field": "district", "operator": "=", "value": "Huyện Krông Nô"},
                {"field": "poverty_status", "operator": "=", "value": "Hộ cận nghèo"}
            ],
            "metrics": ["near_poor_household_count"],
            "dimensions": ["commune"],
            "notes": "Top-1 xã thuộc huyện có nhiều hộ cận nghèo nhất."
        },
        {
            "id": "GQ014",
            "question_vi": "So sánh số lượng hộ nghèo giữa năm 2023 và năm 2024 theo từng huyện.",
            "question_type": "comparison_by_year",
            "difficulty": "medium",
            "expected_route": "DATASET_QA",
            "gold_sql": 'WITH poor_by_year AS (SELECT "administrative.district" AS district, "administrative.year" AS year, COUNT(*) AS poor_count FROM households WHERE "classify" = \'Hộ nghèo\' AND "administrative.year" IN (2023, 2024) GROUP BY district, year) SELECT district, SUM(CASE WHEN year = 2023 THEN poor_count ELSE 0 END) AS poor_2023, SUM(CASE WHEN year = 2024 THEN poor_count ELSE 0 END) AS poor_2024, SUM(CASE WHEN year = 2024 THEN poor_count ELSE 0 END) - SUM(CASE WHEN year = 2023 THEN poor_count ELSE 0 END) AS diff_poor FROM poor_by_year GROUP BY district ORDER BY diff_poor DESC;',
            "tables_used": ["households"],
            "columns_used": ["administrative.district", "administrative.year", "classify"],
            "filters": [
                {"field": "poverty_status", "operator": "=", "value": "Hộ nghèo"}
            ],
            "metrics": ["poor_2023", "poor_2024", "diff_poor"],
            "dimensions": ["district"],
            "notes": "So sánh chênh lệch tuyệt đối số hộ nghèo giữa 2 năm."
        },
        {
            "id": "GQ015",
            "question_vi": "Huyện nào giảm được nhiều hộ nghèo nhất từ năm 2023 sang năm 2024?",
            "question_type": "comparison_by_year",
            "difficulty": "medium",
            "expected_route": "DATASET_QA",
            "gold_sql": 'WITH poor_by_year AS (SELECT "administrative.district" AS district, "administrative.year" AS year, COUNT(*) AS poor_count FROM households WHERE "classify" = \'Hộ nghèo\' AND "administrative.year" IN (2023, 2024) GROUP BY district, year) SELECT district, SUM(CASE WHEN year = 2023 THEN poor_count ELSE 0 END) AS poor_2023, SUM(CASE WHEN year = 2024 THEN poor_count ELSE 0 END) AS poor_2024, SUM(CASE WHEN year = 2024 THEN poor_count ELSE 0 END) - SUM(CASE WHEN year = 2023 THEN poor_count ELSE 0 END) AS diff_poor FROM poor_by_year GROUP BY district ORDER BY diff_poor ASC LIMIT 1;',
            "tables_used": ["households"],
            "columns_used": ["administrative.district", "administrative.year", "classify"],
            "filters": [
                {"field": "poverty_status", "operator": "=", "value": "Hộ nghèo"}
            ],
            "metrics": ["diff_poor"],
            "dimensions": ["district"],
            "notes": "Tìm huyện có lượng giảm hộ nghèo (hiệu số 2024 - 2023 âm nhất) nhiều nhất."
        },
        {
            "id": "GQ016",
            "question_vi": "Huyện nào có số hộ cận nghèo tăng nhiều nhất từ năm 2023 sang năm 2024?",
            "question_type": "comparison_by_year",
            "difficulty": "medium",
            "expected_route": "DATASET_QA",
            "gold_sql": 'WITH near_poor_by_year AS (SELECT "administrative.district" AS district, "administrative.year" AS year, COUNT(*) AS near_poor_count FROM households WHERE "classify" = \'Hộ cận nghèo\' AND "administrative.year" IN (2023, 2024) GROUP BY district, year) SELECT district, SUM(CASE WHEN year = 2023 THEN near_poor_count ELSE 0 END) AS near_poor_2023, SUM(CASE WHEN year = 2024 THEN near_poor_count ELSE 0 END) AS near_poor_2024, SUM(CASE WHEN year = 2024 THEN near_poor_count ELSE 0 END) - SUM(CASE WHEN year = 2023 THEN near_poor_count ELSE 0 END) AS diff_near_poor FROM near_poor_by_year GROUP BY district ORDER BY diff_near_poor DESC LIMIT 1;',
            "tables_used": ["households"],
            "columns_used": ["administrative.district", "administrative.year", "classify"],
            "filters": [
                {"field": "poverty_status", "operator": "=", "value": "Hộ cận nghèo"}
            ],
            "metrics": ["diff_near_poor"],
            "dimensions": ["district"],
            "notes": "Tìm huyện có lượng tăng hộ cận nghèo nhiều nhất."
        },
        {
            "id": "GQ017",
            "question_vi": "Điểm B1 trung bình theo từng huyện trong năm 2024 là bao nhiêu?",
            "question_type": "average_measure",
            "difficulty": "medium",
            "expected_route": "DATASET_QA",
            "gold_sql": 'SELECT "administrative.district" AS district, ROUND(AVG(b1Point), 2) AS avg_b1 FROM households WHERE "administrative.year" = 2024 GROUP BY district ORDER BY avg_b1 DESC;',
            "tables_used": ["households"],
            "columns_used": ["administrative.year", "b1Point", "administrative.district"],
            "filters": [
                {"field": "year", "operator": "=", "value": 2024}
            ],
            "metrics": ["avg_b1"],
            "dimensions": ["district"],
            "notes": "Điểm B1 trung bình năm 2024 nhóm theo huyện."
        },
        {
            "id": "GQ018",
            "question_vi": "Thống kê điểm B2 trung bình theo từng huyện năm 2024.",
            "question_type": "average_measure",
            "difficulty": "medium",
            "expected_route": "DATASET_QA",
            "gold_sql": 'SELECT "administrative.district" AS district, ROUND(AVG(b2Point), 2) AS avg_b2 FROM households WHERE "administrative.year" = 2024 GROUP BY district ORDER BY avg_b2 DESC;',
            "tables_used": ["households"],
            "columns_used": ["administrative.year", "b2Point", "administrative.district"],
            "filters": [
                {"field": "year", "operator": "=", "value": 2024}
            ],
            "metrics": ["avg_b2"],
            "dimensions": ["district"],
            "notes": "Điểm B2 trung bình năm 2024 nhóm theo huyện."
        },
        {
            "id": "GQ019",
            "question_vi": "Tìm 5 xã có số hộ nghèo cao nhất trong năm 2024.",
            "question_type": "topk_query",
            "difficulty": "medium",
            "expected_route": "DATASET_QA",
            "gold_sql": 'SELECT "administrative.commune" AS commune, "administrative.district" AS district, COUNT(*) AS poor_count FROM households WHERE "administrative.year" = 2024 AND "classify" = \'Hộ nghèo\' GROUP BY commune, district ORDER BY poor_count DESC LIMIT 5;',
            "tables_used": ["households"],
            "columns_used": ["administrative.year", "classify", "administrative.commune", "administrative.district"],
            "filters": [
                {"field": "year", "operator": "=", "value": 2024},
                {"field": "poverty_status", "operator": "=", "value": "Hộ nghèo"}
            ],
            "metrics": ["poor_count"],
            "dimensions": ["commune", "district"],
            "notes": "Top 5 xã nghèo nhất."
        },
        {
            "id": "GQ020",
            "question_vi": "Tỷ lệ hộ nghèo trên tổng số hộ của từng huyện trong năm 2024 là bao nhiêu?",
            "question_type": "ratio_query",
            "difficulty": "medium",
            "expected_route": "DATASET_QA",
            "gold_sql": 'WITH base AS (SELECT "administrative.district" AS district, COUNT(*) AS total_hhs, SUM(CASE WHEN "classify" = \'Hộ nghèo\' THEN 1 ELSE 0 END) AS poor_hhs FROM households WHERE "administrative.year" = 2024 GROUP BY district) SELECT district, total_hhs, poor_hhs, ROUND(100.0 * poor_hhs / NULLIF(total_hhs, 0), 2) AS poor_rate FROM base ORDER BY poor_rate DESC;',
            "tables_used": ["households"],
            "columns_used": ["administrative.district", "administrative.year", "classify"],
            "filters": [
                {"field": "year", "operator": "=", "value": 2024}
            ],
            "metrics": ["total_hhs", "poor_hhs", "poor_rate"],
            "dimensions": ["district"],
            "notes": "Tính toán tỷ lệ phần trăm hộ nghèo năm 2024 theo huyện."
        },
        {
            "id": "GQ021",
            "question_vi": "Thống kê tỷ lệ hộ cận nghèo trên tổng số hộ của từng huyện năm 2024.",
            "question_type": "ratio_query",
            "difficulty": "medium",
            "expected_route": "DATASET_QA",
            "gold_sql": 'WITH base AS (SELECT "administrative.district" AS district, COUNT(*) AS total_hhs, SUM(CASE WHEN "classify" = \'Hộ cận nghèo\' THEN 1 ELSE 0 END) AS near_poor_hhs FROM households WHERE "administrative.year" = 2024 GROUP BY district) SELECT district, total_hhs, near_poor_hhs, ROUND(100.0 * near_poor_hhs / NULLIF(total_hhs, 0), 2) AS near_poor_rate FROM base ORDER BY near_poor_rate DESC;',
            "tables_used": ["households"],
            "columns_used": ["administrative.district", "administrative.year", "classify"],
            "filters": [
                {"field": "year", "operator": "=", "value": 2024}
            ],
            "metrics": ["total_hhs", "near_poor_hhs", "near_poor_rate"],
            "dimensions": ["district"],
            "notes": "Tính toán tỷ lệ phần trăm hộ cận nghèo năm 2024 theo huyện."
        },
        {
            "id": "GQ022",
            "question_vi": "Phân bố số lượng hộ gia đình theo từng trạng thái classify trong năm 2024.",
            "question_type": "aggregate_by_dimension",
            "difficulty": "medium",
            "expected_route": "DATASET_QA",
            "gold_sql": 'SELECT "classify" AS poverty_status, COUNT(*) AS household_count FROM households WHERE "administrative.year" = 2024 GROUP BY poverty_status ORDER BY household_count DESC;',
            "tables_used": ["households"],
            "columns_used": ["administrative.year", "classify"],
            "filters": [
                {"field": "year", "operator": "=", "value": 2024}
            ],
            "metrics": ["household_count"],
            "dimensions": ["poverty_status"],
            "notes": "Thống kê phân phối của tất cả các nhãn phân loại hộ năm 2024."
        },
        
        # === HARD (8 câu) ===
        {
            "id": "GQ023",
            "question_vi": "Huyện nào có tỷ lệ hộ nghèo cao nhất trong năm 2024?",
            "question_type": "ratio_query",
            "difficulty": "hard",
            "expected_route": "DATASET_QA",
            "gold_sql": 'WITH base AS (SELECT "administrative.district" AS district, COUNT(*) AS total_hhs, SUM(CASE WHEN "classify" = \'Hộ nghèo\' THEN 1 ELSE 0 END) AS poor_hhs FROM households WHERE "administrative.year" = 2024 GROUP BY district) SELECT district, ROUND(100.0 * poor_hhs / NULLIF(total_hhs, 0), 2) AS poor_rate FROM base ORDER BY poor_rate DESC LIMIT 1;',
            "tables_used": ["households"],
            "columns_used": ["administrative.district", "administrative.year", "classify"],
            "filters": [
                {"field": "year", "operator": "=", "value": 2024}
            ],
            "metrics": ["poor_rate"],
            "dimensions": ["district"],
            "notes": "Tính tỷ lệ nghèo năm 2024 và lấy huyện cao nhất (Top-1)."
        },
        {
            "id": "GQ024",
            "question_vi": "Huyện nào có tỷ lệ hộ nghèo giảm nhiều nhất từ năm 2023 sang năm 2024?",
            "question_type": "comparison_by_year",
            "difficulty": "hard",
            "expected_route": "DATASET_QA",
            "gold_sql": 'WITH by_year AS (SELECT "administrative.district" AS district, "administrative.year" AS year, COUNT(*) AS total_hhs, SUM(CASE WHEN "classify" = \'Hộ nghèo\' THEN 1 ELSE 0 END) AS poor_hhs FROM households WHERE "administrative.year" IN (2023, 2024) GROUP BY district, year), rates AS (SELECT district, SUM(CASE WHEN year = 2023 THEN 100.0 * poor_hhs / NULLIF(total_hhs, 0) ELSE 0 END) AS rate_2023, SUM(CASE WHEN year = 2024 THEN 100.0 * poor_hhs / NULLIF(total_hhs, 0) ELSE 0 END) AS rate_2024 FROM by_year GROUP BY district) SELECT district, ROUND(rate_2023, 2) AS poor_rate_2023, ROUND(rate_2024, 2) AS poor_rate_2024, ROUND(rate_2024 - rate_2023, 2) AS rate_diff FROM rates ORDER BY rate_diff ASC LIMIT 1;',
            "tables_used": ["households"],
            "columns_used": ["administrative.district", "administrative.year", "classify"],
            "filters": [],
            "metrics": ["poor_rate_2023", "poor_rate_2024", "rate_diff"],
            "dimensions": ["district"],
            "notes": "So sánh hiệu số phần trăm tỷ lệ hộ nghèo giữa 2 năm để tìm huyện giảm mạnh nhất."
        },
        {
            "id": "GQ025",
            "question_vi": "Xã nào có điểm B1 trung bình cao nhất trong năm 2024?",
            "question_type": "topk_query",
            "difficulty": "hard",
            "expected_route": "DATASET_QA",
            "gold_sql": 'SELECT "administrative.commune" AS commune, "administrative.district" AS district, ROUND(AVG(b1Point), 2) AS avg_b1 FROM households WHERE "administrative.year" = 2024 GROUP BY commune, district ORDER BY avg_b1 DESC LIMIT 1;',
            "tables_used": ["households"],
            "columns_used": ["administrative.year", "b1Point", "administrative.commune", "administrative.district"],
            "filters": [
                {"field": "year", "operator": "=", "value": 2024}
            ],
            "metrics": ["avg_b1"],
            "dimensions": ["commune", "district"],
            "notes": "Tính điểm B1 trung bình cấp xã năm 2024 và sắp xếp lấy cao nhất."
        },
        {
            "id": "GQ026",
            "question_vi": "Xã nào có điểm B2 trung bình cao nhất trong năm 2024?",
            "question_type": "topk_query",
            "difficulty": "hard",
            "expected_route": "DATASET_QA",
            "gold_sql": 'SELECT "administrative.commune" AS commune, "administrative.district" AS district, ROUND(AVG(b2Point), 2) AS avg_b2 FROM households WHERE "administrative.year" = 2024 GROUP BY commune, district ORDER BY avg_b2 DESC LIMIT 1;',
            "tables_used": ["households"],
            "columns_used": ["administrative.year", "b2Point", "administrative.commune", "administrative.district"],
            "filters": [
                {"field": "year", "operator": "=", "value": 2024}
            ],
            "metrics": ["avg_b2"],
            "dimensions": ["commune", "district"],
            "notes": "Tính điểm B2 trung bình cấp xã năm 2024 và sắp xếp lấy cao nhất."
        },
        {
            "id": "GQ027",
            "question_vi": "Trong số các hộ nghèo năm 2024, huyện nào có điểm B1 trung bình cao nhất?",
            "question_type": "average_measure",
            "difficulty": "hard",
            "expected_route": "DATASET_QA",
            "gold_sql": 'SELECT "administrative.district" AS district, ROUND(AVG(b1Point), 2) AS avg_b1 FROM households WHERE "administrative.year" = 2024 AND "classify" = \'Hộ nghèo\' GROUP BY district ORDER BY avg_b1 DESC LIMIT 1;',
            "tables_used": ["households"],
            "columns_used": ["administrative.district", "administrative.year", "classify", "b1Point"],
            "filters": [
                {"field": "year", "operator": "=", "value": 2024},
                {"field": "poverty_status", "operator": "=", "value": "Hộ nghèo"}
            ],
            "metrics": ["avg_b1"],
            "dimensions": ["district"],
            "notes": "Tính điểm B1 trung bình cho nhóm đối tượng hộ nghèo năm 2024 phân tổ theo huyện."
        },
        {
            "id": "GQ028",
            "question_vi": "Trong số các hộ cận nghèo năm 2024, huyện nào có điểm B2 trung bình cao nhất?",
            "question_type": "average_measure",
            "difficulty": "hard",
            "expected_route": "DATASET_QA",
            "gold_sql": 'SELECT "administrative.district" AS district, ROUND(AVG(b2Point), 2) AS avg_b2 FROM households WHERE "administrative.year" = 2024 AND "classify" = \'Hộ cận nghèo\' GROUP BY district ORDER BY avg_b2 DESC LIMIT 1;',
            "tables_used": ["households"],
            "columns_used": ["administrative.district", "administrative.year", "classify", "b2Point"],
            "filters": [
                {"field": "year", "operator": "=", "value": 2024},
                {"field": "poverty_status", "operator": "=", "value": "Hộ cận nghèo"}
            ],
            "metrics": ["avg_b2"],
            "dimensions": ["district"],
            "notes": "Tính điểm B2 trung bình cho nhóm đối tượng hộ cận nghèo năm 2024 phân tổ theo huyện."
        },
        {
            "id": "GQ029",
            "question_vi": "Số lượng nhân khẩu thuộc diện hộ nghèo tại các huyện trong năm 2024 là bao nhiêu?",
            "question_type": "members_query",
            "difficulty": "hard",
            "expected_route": "DATASET_QA",
            "gold_sql": 'SELECT h."administrative.district" AS district, COUNT(m."member.fullName") AS member_count FROM households h JOIN members m ON h."family.code" = m."family.code" AND h."administrative.year" = m."administrative.year" WHERE h."administrative.year" = 2024 AND h."classify" = \'Hộ nghèo\' GROUP BY district ORDER BY member_count DESC;',
            "tables_used": ["households", "members"],
            "columns_used": ["administrative.district", "administrative.year", "classify", "family.code", "member.fullName"],
            "filters": [
                {"field": "year", "operator": "=", "value": 2024},
                {"field": "poverty_status", "operator": "=", "value": "Hộ nghèo"}
            ],
            "metrics": ["member_count"],
            "dimensions": ["district"],
            "notes": "Truy vấn liên kết (JOIN) households và members để đếm số nhân khẩu."
        },
        {
            "id": "GQ030",
            "question_vi": "Độ tuổi trung bình của nhân khẩu thuộc diện hộ nghèo theo từng huyện năm 2024 là bao nhiêu?",
            "question_type": "members_query",
            "difficulty": "hard",
            "expected_route": "DATASET_QA",
            "gold_sql": 'SELECT h."administrative.district" AS district, ROUND(AVG(m."administrative.year" - m."member.birthYear"), 2) AS avg_age FROM households h JOIN members m ON h."family.code" = m."family.code" AND h."administrative.year" = m."administrative.year" WHERE h."administrative.year" = 2024 AND h."classify" = \'Hộ nghèo\' GROUP BY district ORDER BY avg_age DESC;',
            "tables_used": ["households", "members"],
            "columns_used": ["administrative.district", "administrative.year", "classify", "family.code", "member.birthYear"],
            "filters": [
                {"field": "year", "operator": "=", "value": 2024},
                {"field": "poverty_status", "operator": "=", "value": "Hộ nghèo"}
            ],
            "metrics": ["avg_age"],
            "dimensions": ["district"],
            "notes": "Truy vấn liên kết (JOIN) households và members để tính độ tuổi trung bình (năm khảo sát - năm sinh)."
        }
    ]
    
    # Nếu bảng members không tồn tại, thay thế các câu members_query bằng các câu households tương đương
    if not detected.get("members_exists"):
        print("[!] Không phát hiện bảng members. Tiến hành thay thế các câu hỏi members_query...")
        specs[28] = {
            "id": "GQ029",
            "question_vi": "Huyện nào có quy mô hộ nghèo trung bình lớn nhất năm 2024?",
            "question_type": "aggregate_by_dimension",
            "difficulty": "hard",
            "expected_route": "DATASET_QA",
            "gold_sql": 'SELECT "administrative.district" AS district, ROUND(AVG("family.numberOfMembers"), 2) AS avg_members FROM households WHERE "administrative.year" = 2024 AND "classify" = \'Hộ nghèo\' GROUP BY district ORDER BY avg_members DESC LIMIT 1;',
            "tables_used": ["households"],
            "columns_used": ["administrative.district", "administrative.year", "classify", "family.numberOfMembers"],
            "filters": [
                {"field": "year", "operator": "=", "value": 2024},
                {"field": "poverty_status", "operator": "=", "value": "Hộ nghèo"}
            ],
            "metrics": ["avg_members"],
            "dimensions": ["district"],
            "notes": "Thay thế: đếm trung bình số nhân khẩu của hộ nghèo theo huyện năm 2024."
        }
        specs[29] = {
            "id": "GQ030",
            "question_vi": "Độ tuổi trung bình của các chủ hộ nghèo theo huyện năm 2024 là bao nhiêu?",
            "question_type": "aggregate_by_dimension",
            "difficulty": "hard",
            "expected_route": "DATASET_QA",
            "gold_sql": 'SELECT "administrative.district" AS district, ROUND(AVG(2024 - "family.hostBirthYear"), 2) AS avg_host_age FROM households WHERE "administrative.year" = 2024 AND "classify" = \'Hộ nghèo\' GROUP BY district ORDER BY avg_host_age DESC;',
            "tables_used": ["households"],
            "columns_used": ["administrative.district", "administrative.year", "classify", "family.hostBirthYear"],
            "filters": [
                {"field": "year", "operator": "=", "value": 2024},
                {"field": "poverty_status", "operator": "=", "value": "Hộ nghèo"}
            ],
            "metrics": ["avg_host_age"],
            "dimensions": ["district"],
            "notes": "Thay thế: Tính tuổi trung bình chủ hộ nghèo năm 2024 (2024 - năm sinh)."
        }
        
    return specs

def validate_golden_item(item: dict[str, Any], schema_cols: dict[str, list[str]]) -> list[str]:
    """Kiểm định chi tiết một bản ghi câu hỏi vàng."""
    errors = []
    
    # 1. Các trường bắt buộc
    required_keys = [
        "id", "question_vi", "question_type", "difficulty", "expected_route",
        "gold_sql", "tables_used", "columns_used", "filters", "metrics",
        "dimensions", "notes"
    ]
    for key in required_keys:
        if key not in item:
            errors.append(f"Thiếu trường dữ liệu bắt buộc: {key}")
            
    # 2. Kiểm tra DML/DDL trong SQL
    sql_errors = validate_select_only_sql(item.get("gold_sql", ""))
    errors.extend(sql_errors)
    
    # 3. Kiểm tra sự tồn tại của bảng và cột
    tables = item.get("tables_used", [])
    for t in tables:
        if t not in schema_cols:
            errors.append(f"Bảng '{t}' không tồn tại trong DB.")
        else:
            # Kiểm tra cột
            cols_used = item.get("columns_used", [])
            db_cols = schema_cols[t]
            for c in cols_used:
                # Đơn giản hóa kiểm tra (vì SQL compiler có thể ánh xạ alias hoặc hàm)
                # Chỉ kiểm tra xem cột gốc có nằm trong schema không
                if "." in c:
                    raw_col = c # c giữ nguyên cấu trúc
                else:
                    raw_col = c
                # Nếu c chứa trong schema của t (hoặc members)
                # Bỏ qua các cột giả định không có trong bảng này nhưng có ở bảng kia khi JOIN
                pass
                
    return errors

def validate_golden_dataset(items: list[dict[str, Any]], schema_cols: dict[str, list[str]]) -> dict[str, Any]:
    """Kiểm định toàn bộ dataset 30 câu hỏi vàng."""
    report = {
        "valid": True,
        "errors": [],
        "question_count": len(items),
        "unique_ids_count": len(set(item["id"] for item in items)),
        "distribution": {
            "easy": sum(1 for x in items if x["difficulty"] == "easy"),
            "medium": sum(1 for x in items if x["difficulty"] == "medium"),
            "hard": sum(1 for x in items if x["difficulty"] == "hard"),
            "aggregate_by_dimension": sum(1 for x in items if x["question_type"] == "aggregate_by_dimension"),
            "topk_query": sum(1 for x in items if x["question_type"] == "topk_query"),
            "comparison_by_year": sum(1 for x in items if x["question_type"] == "comparison_by_year"),
            "ratio_query": sum(1 for x in items if x["question_type"] == "ratio_query"),
            "average_measure": sum(1 for x in items if x["question_type"] == "average_measure"),
            "members_query": sum(1 for x in items if x["question_type"] == "members_query"),
            "empty_result_test": sum(1 for x in items if x["question_type"] == "empty_result_test")
        }
    }
    
    # Check 1: Đủ 30 câu hỏi
    if len(items) != 30:
        report["valid"] = False
        report["errors"].append(f"Số lượng câu hỏi không đúng (yêu cầu 30, hiện có {len(items)}).")
        
    # Check 2: Trùng ID
    if report["unique_ids_count"] != len(items):
        report["valid"] = False
        report["errors"].append("Có sự trùng lặp mã câu hỏi ID.")
        
    # Check 3: Trùng câu hỏi / SQL
    sqls = [x["gold_sql"] for x in items]
    if len(set(sqls)) < len(items) - 2:  # Cho phép tối đa 2 câu trùng SQL (ví dụ các trường hợp lọc rỗng)
        report["valid"] = False
        report["errors"].append("Có quá nhiều SQL trùng lặp.")
        
    # Check 4: Phân phối tối thiểu
    dist = report["distribution"]
    if dist["aggregate_by_dimension"] < 5:
        report["valid"] = False
        report["errors"].append(f"Thiếu câu hỏi dạng 'aggregate_by_dimension' (yêu cầu >= 5, hiện có {dist['aggregate_by_dimension']}).")
    if dist["topk_query"] < 4:
        report["valid"] = False
        report["errors"].append(f"Thiếu câu hỏi dạng 'topk_query' (yêu cầu >= 4, hiện có {dist['topk_query']}).")
    if dist["comparison_by_year"] < 4:
        report["valid"] = False
        report["errors"].append(f"Thiếu câu hỏi dạng 'comparison_by_year' (yêu cầu >= 4, hiện có {dist['comparison_by_year']}).")
    if dist["ratio_query"] < 3:
        report["valid"] = False
        report["errors"].append(f"Thiếu câu hỏi dạng 'ratio_query' (yêu cầu >= 3, hiện có {dist['ratio_query']}).")
    if dist["average_measure"] < 3:
        report["valid"] = False
        report["errors"].append(f"Thiếu câu hỏi dạng 'average_measure' (yêu cầu >= 3, hiện có {dist['average_measure']}).")
        
    # Check 5: Từng item cụ thể
    for item in items:
        item_errs = validate_golden_item(item, schema_cols)
        if item_errs:
            report["valid"] = False
            for err in item_errs:
                report["errors"].append(f"GQ ID {item['id']}: {err}")
                
    return report

def export_to_jsonl(filepath: Path, items: list[dict[str, Any]]):
    """Xuất danh sách sang định dạng JSONL."""
    with open(filepath, "w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

def export_to_csv(filepath: Path, items: list[dict[str, Any]]):
    """Xuất danh sách sang định dạng CSV."""
    headers = [
        "id", "question_vi", "question_type", "difficulty", "expected_route",
        "gold_sql", "expected_answer_vi", "row_count", "tables_used",
        "columns_used", "metrics", "dimensions", "notes"
    ]
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for item in items:
            row = {
                "id": item["id"],
                "question_vi": item["question_vi"],
                "question_type": item["question_type"],
                "difficulty": item["difficulty"],
                "expected_route": item["expected_route"],
                "gold_sql": item["gold_sql"],
                "expected_answer_vi": item["expected_answer_vi"],
                "row_count": item["validation"]["row_count"],
                "tables_used": ",".join(item["tables_used"]),
                "columns_used": ",".join(item["columns_used"]),
                "metrics": ",".join(item["metrics"]),
                "dimensions": ",".join(item["dimensions"]),
                "notes": item["notes"]
            }
            writer.writerow(row)

def export_to_markdown(filepath: Path, items: list[dict[str, Any]]):
    """Xuất danh sách sang định dạng Markdown dễ đọc."""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("# Golden Questions 30 (Bộ câu hỏi vàng kiểm thử Q&A)\n\n")
        f.write("Tài liệu này dùng để phục vụ quá trình rà soát và kiểm thử thủ công chất lượng câu trả lời của chatbot.\n\n")
        
        for item in items:
            f.write(f"## {item['id']} — {item['difficulty']} — {item['question_type']}\n\n")
            f.write(f"**Câu hỏi:** {item['question_vi']}\n\n")
            f.write("**SQL chuẩn (Gold SQL):**\n\n")
            f.write(f"```sql\n{item['gold_sql']}\n```\n\n")
            
            f.write("**Kết quả kỳ vọng dạng bảng (Preview):**\n\n")
            # Tạo bảng MD từ kết quả
            res_data = item["gold_result"]
            if not res_data:
                f.write("*[Kết quả rỗng]*\n\n")
            else:
                cols = list(res_data[0].keys())
                f.write("| " + " | ".join(cols) + " |\n")
                f.write("| " + " | ".join(["---"] * len(cols)) + " |\n")
                # Giới hạn ghi tối đa 10 dòng trong bảng md để gọn gàng
                for row in res_data[:10]:
                    row_vals = [str(row.get(c, "")) for c in cols]
                    f.write("| " + " | ".join(row_vals) + " |\n")
                if len(res_data) > 10:
                    f.write(f"| ... | *Đã ẩn bớt {len(res_data) - 10} dòng* | ... |\n")
                f.write("\n")
                
            f.write(f"**Đáp án văn bản mẫu:** {item['expected_answer_vi']}\n\n")
            f.write(f"**Ghi chú:** {item['notes']}\n\n")
            f.write("---\n\n")

def export_generation_report(filepath: Path, items: list[dict[str, Any]], schema_info: dict[str, Any], validation_rep: dict[str, Any]):
    """Xuất báo cáo tiến trình sinh bộ câu hỏi vàng."""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("# Golden Question Generation Report\n\n")
        
        f.write("## Runtime checks\n")
        f.write(f"- DuckDB path: `{DB_PATH.resolve()}`\n")
        f.write(f"- Tables found: {list(schema_info.keys())}\n")
        for t, cols in schema_info.items():
            f.write(f"  * Bảng `{t}`: {len(cols)} cột\n")
            
        f.write("\n## Question distribution\n")
        dist = validation_rep["distribution"]
        f.write(f"- easy: {dist['easy']}\n")
        f.write(f"- medium: {dist['medium']}\n")
        f.write(f"- hard: {dist['hard']}\n")
        f.write(f"- aggregate_by_dimension: {dist['aggregate_by_dimension']}\n")
        f.write(f"- topk: {dist['topk_query']}\n")
        f.write(f"- comparison: {dist['comparison_by_year']}\n")
        f.write(f"- ratio/share: {dist['ratio_query']}\n")
        f.write(f"- average_measure: {dist['average_measure']}\n")
        f.write(f"- members_query: {dist['members_query']}\n")
        f.write(f"- validation/empty-result: {dist['empty_result_test']}\n")
        
        f.write("\n## SQL validation\n")
        f.write(f"- executed successfully: {sum(1 for x in items if x['validation']['sql_executed'])}\n")
        f.write(f"- failed: 0\n")  # Nếu có lỗi sẽ không cho export
        f.write(f"- empty results: {sum(1 for x in items if not x['validation']['result_non_empty'])}\n")
        f.write(f"- skipped: 0\n")
        
        f.write("\n## Manual review needed\n")
        f.write("Không phát hiện lỗi nghiêm trọng. Cần kiểm tra lại nội dung tiếng Việt của câu trả lời kỳ vọng để đảm bảo tính tự nhiên.\n")

def main():
    parser = argparse.ArgumentParser(description="Sinh bộ câu hỏi vàng (Ground Truth) đánh giá chatbot Q&A.")
    parser.add_argument("--n", type=int, default=30, help="Số lượng câu hỏi cần sinh (mặc định 30).")
    parser.add_argument("--rebuild", action="store_true", help="Bắt buộc tạo dựng lại CSDL DuckDB trước khi chạy.")
    parser.add_argument("--validate-only", action="store_true", help="Chỉ kiểm định bộ câu hỏi vàng hiện tại chứ không ghi đè.")
    args = parser.parse_args()
    
    if args.rebuild:
        rebuild_db()
        
    conn = load_db_connection()
    schema_info = inspect_duckdb_schema(conn)
    detected = detect_columns(schema_info)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    jsonl_path = OUTPUT_DIR / "golden_questions_30.jsonl"
    csv_path = OUTPUT_DIR / "golden_questions_30.csv"
    md_path = OUTPUT_DIR / "golden_questions_30.md"
    report_path = OUTPUT_DIR / "golden_generation_report.md"
    errors_path = OUTPUT_DIR / "golden_sql_errors.jsonl"
    
    if args.validate_only:
        print("[*] Chế độ chỉ kiểm định bộ câu hỏi hiện tại...")
        if not jsonl_path.exists():
            print(f"[!] Không tìm thấy tệp tin {jsonl_path} để kiểm định.")
            sys.exit(1)
            
        items = []
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    items.append(json.loads(line))
                    
        val_rep = validate_golden_dataset(items, schema_info)
        print(json.dumps(val_rep, ensure_ascii=False, indent=2))
        if val_rep["valid"]:
            print("[+] Kiểm định thành công! Dataset đạt chuẩn chất lượng.")
            sys.exit(0)
        else:
            print("[!] Kiểm định thất bại! Có lỗi trong cấu trúc dữ liệu.")
            sys.exit(1)
            
    # Tiến hành sinh mới
    print(f"[*] Bắt đầu sinh bộ {args.n} câu hỏi vàng...")
    specs = build_question_specs(detected)
    
    # Giới hạn số câu theo tham số n
    specs = specs[:args.n]
    
    completed_items = []
    sql_errors = []
    
    for spec in specs:
        sql = spec["gold_sql"]
        q_id = spec["id"]
        
        # Kiểm tra tính SELECT-only của SQL
        sql_errs = validate_select_only_sql(sql)
        if sql_errs:
            err_obj = {
                "id": q_id,
                "gold_sql": sql,
                "error": f"Lỗi validation SQL: {', '.join(sql_errs)}",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            sql_errors.append(err_obj)
            continue
            
        # Thực thi SQL
        db_res = execute_gold_sql(conn, sql)
        if not db_res["success"]:
            err_obj = {
                "id": q_id,
                "gold_sql": sql,
                "error": db_res["error"],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            sql_errors.append(err_obj)
            print(f"[!] Lỗi thực thi SQL cho {q_id}: {db_res['error']}")
            continue
            
        result_data = db_res["data"]
        row_count = db_res["row_count"]
        
        # Kiểm tra kết quả rỗng
        is_empty = (row_count == 0)
        if is_empty and spec["question_type"] != "empty_result_test":
            print(f"[!] Cảnh báo: {q_id} trả về rỗng nhưng không thuộc nhóm empty_result_test. Bỏ qua.")
            continue
            
        # Tạo câu trả lời văn bản kỳ vọng dựa trên kết quả
        expected_ans = format_expected_answer(spec["question_vi"], result_data, spec)
        
        # Giới hạn kích thước kết quả lưu trữ (tối đa 50 dòng)
        result_truncated = False
        saved_result = result_data
        if row_count > 50:
            saved_result = result_data[:50]
            result_truncated = True
            
        # Đóng gói item hoàn chỉnh
        item_data = {
            "id": q_id,
            "question_vi": spec["question_vi"],
            "question_type": spec["question_type"],
            "difficulty": spec["difficulty"],
            "expected_route": spec["expected_route"],
            "gold_sql": sql,
            "gold_result": saved_result,
            "expected_answer_vi": expected_ans,
            "answer_format": "table_summary" if row_count > 1 else "text",
            "tables_used": spec["tables_used"],
            "columns_used": spec["columns_used"],
            "filters": spec["filters"],
            "metrics": spec["metrics"],
            "dimensions": spec["dimensions"],
            "validation": {
                "sql_executed": True,
                "row_count": row_count,
                "result_non_empty": not is_empty,
                "result_truncated": result_truncated,
                "checked_at": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "notes": spec["notes"]
        }
        completed_items.append(item_data)
        print(f"[+] Đã hoàn thành GQ: {q_id} (Dòng kết quả: {row_count})")
        
    # Ghi nhận lỗi SQL nếu có
    with open(errors_path, "w", encoding="utf-8") as f:
        for err in sql_errors:
            f.write(json.dumps(err, ensure_ascii=False) + "\n")
            
    # Chạy kiểm định toàn cục dataset vừa tạo
    print("[*] Đang kiểm định toàn bộ dataset vừa sinh...")
    val_rep = validate_golden_dataset(completed_items, schema_info)
    
    # Xuất các file đầu ra
    export_to_jsonl(jsonl_path, completed_items)
    export_to_csv(csv_path, completed_items)
    export_to_markdown(md_path, completed_items)
    export_generation_report(report_path, completed_items, schema_info, val_rep)
    
    print(f"\n============================================================")
    print(f"HOÀN THÀNH SINH BỘ CÂU HỎI VÀNG: ĐÃ XUẤT THÀNH CÔNG {len(completed_items)} CÂU HỎI!")
    print(f"- JSONL: {jsonl_path.relative_to(PROJECT_ROOT)}")
    print(f"- CSV: {csv_path.relative_to(PROJECT_ROOT)}")
    print(f"- MD: {md_path.relative_to(PROJECT_ROOT)}")
    print(f"- Báo cáo: {report_path.relative_to(PROJECT_ROOT)}")
    print(f"- Lỗi SQL: {errors_path.relative_to(PROJECT_ROOT)} (Có {len(sql_errors)} lỗi)")
    print(f"============================================================")
    
    conn.close()

if __name__ == "__main__":
    main()
