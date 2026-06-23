# -*- coding: utf-8 -*-
from __future__ import annotations
import sys
import duckdb
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))
from src.query_control.llm_helper import call_llm

class SQLRefiner:
    """Agent thực thi SQL và tự sửa lỗi nếu cần."""
    def __init__(self, db_path: Path):
        self.db_path = db_path
        
    def execute_and_refine(self, sql_query: str, user_question: str, schema_info: dict, max_retries: int = 3) -> tuple[pd.DataFrame | None, str]:
        """Thực thi SQL. Nếu lỗi, yêu cầu LLM sửa lại."""
        current_sql = sql_query
        
        for attempt in range(max_retries):
            try:
                # Mở connection read-only để tránh file lock
                with duckdb.connect(str(self.db_path), read_only=True) as con:
                    df = con.execute(current_sql).df()
                    return df, current_sql
            except Exception as e:
                error_msg = str(e)
                print(f"[SQLRefiner] Lỗi thực thi lần {attempt+1}: {error_msg}")
                if attempt == max_retries - 1:
                    print("[SQLRefiner] Hết số lần thử lại.")
                    return None, current_sql
                    
                # Nhờ LLM sửa lỗi
                system_prompt = f"""Bạn là một chuyên gia DuckDB SQL. Câu lệnh SQL dưới đây đã bị lỗi khi thực thi.
Nhiệm vụ của bạn là SỬA LỖI và trả về DUY NHẤT một câu lệnh SQL mới đã sửa (không markdown, không giải thích).

Bối cảnh:
- Câu hỏi của người dùng: {user_question}
{schema_info.get('schema_context', '')}

LƯU Ý QUAN TRỌNG:
  + Cột chứa dấu chấm (vd: administrative.year) phải bọc trong ngoặc kép: "administrative.year"
  + Kiểm tra lỗi chính tả tên cột. Bảng households có trạng thái nghèo là "classify", địa phương "administrative.district", "administrative.commune", "family.hostName". Bảng members có "member.fullName".
  + Các giá trị text khi so sánh phải dùng dấu nháy đơn.

Câu lệnh SQL bị lỗi:
{current_sql}

Thông báo lỗi từ hệ thống DuckDB:
{error_msg}
"""
                raw_sql = call_llm(
                    system_prompt=system_prompt,
                    user_prompt="Hãy sửa câu SQL bị lỗi và chỉ trả về câu SQL đã sửa.",
                    temperature=0.0,
                    max_tokens=400,
                    response_json=False
                )
                
                # Làm sạch markdown nếu có
                sql = raw_sql.strip()
                if sql.startswith("```sql"):
                    sql = sql[6:]
                if sql.startswith("```"):
                    sql = sql[3:]
                if sql.endswith("```"):
                    sql = sql[:-3]
                current_sql = sql.strip()
                
        return None, current_sql
