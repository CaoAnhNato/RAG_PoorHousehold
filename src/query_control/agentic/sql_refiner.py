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
        
        # Chuẩn hóa tên các huyện/thành phố trong SQL để khớp chính xác với CSDL DuckDB
        replacements = {
            "Đắk Glong": "Đăk Glong",
            "Đăk Mil": "Đắk Mil",
            "Đăk RLấp": "Đắk RLấp",
            "Đăk Rlấp": "Đắk RLấp",
            "Đăk Song": "Đắk Song"
        }
        for wrong, correct in replacements.items():
            current_sql = current_sql.replace(wrong, correct)
            
        for attempt in range(max_retries):
            try:
                # Mở connection read-only để tránh file lock
                with duckdb.connect(str(self.db_path), read_only=True) as con:
                    df = con.execute(current_sql).df()
                    
                    # TỰ KIỂM TRA LỖI LOGIC TỔNG QUÁT (SELF-CORRECTION FOR ALL LOGIC ERRORS)
                    # 1. Bắt lỗi GROUP BY thiếu trong SELECT cho TẤT CẢ các trường
                    sql_upper = current_sql.upper()
                    if "GROUP BY" in sql_upper:
                        import re
                        group_by_clause = sql_upper.split("GROUP BY")[1].split("ORDER BY")[0].split("LIMIT")[0].split("HAVING")[0]
                        # Tìm tất cả các từ có vẻ là tên cột (bỏ qua số, khoảng trắng)
                        gb_tokens = re.findall(r'"?([a-zA-Z0-9_\.]+)"?', group_by_clause)
                        gb_fields = [token for token in gb_tokens if not token.isnumeric() and token.lower() not in ('asc', 'desc')]
                        
                        # Kiểm tra tổng quát: Từng trường trong GROUP BY phải xuất hiện trong mệnh đề SELECT
                        select_clause = sql_upper.split("FROM")[0]
                        missing_fields = []
                        for field in gb_fields:
                            clean_field = field.replace('"', '').strip()
                            if clean_field not in select_clause:
                                missing_fields.append(clean_field)
                        if missing_fields:
                            raise ValueError(f"LỖI LOGIC: SQL dùng GROUP BY với các trường ({', '.join(missing_fields)}) nhưng QUÊN đưa vào mệnh đề SELECT. Theo quy tắc hiển thị dữ liệu biểu đồ/báo cáo, tất cả các trường GROUP BY phải có mặt trong SELECT (kèm AS alias phù hợp). Yêu cầu thêm vào SELECT ngay!")

                    # 2. Bắt lỗi truy vấn trả về 0 dòng dữ liệu (DataFrame rỗng)
                    if df.empty:
                        raise ValueError("LỖI LOGIC: Truy vấn thực thi thành công nhưng trả về 0 dòng dữ liệu (DataFrame rỗng)! Nguyên nhân do điều kiện WHERE lọc sai giá trị thực tế trong CSDL. LƯU Ý QUAN TRỌNG: Trong CSDL, cột administrative.district bắt buộc phải có chữ 'Huyện' hoặc 'Thành phố' phía trước (ví dụ: 'Huyện Cư Jút', 'Huyện Đắk Mil', 'Thành phố Gia Nghĩa'), cột administrative.commune phải có chữ 'Xã' hoặc 'Thị trấn' phía trước. Hãy sửa lại điều kiện WHERE cho đúng!")

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
  + Tên huyện phải có chữ 'Huyện' hoặc 'Thành phố' (vd: 'Huyện Cư Jút', 'Huyện Đắk Mil'). Tên xã phải có chữ 'Xã' hoặc 'Thị trấn'.

Câu lệnh SQL bị lỗi:
{current_sql}

Thông báo lỗi từ hệ thống DuckDB:
{error_msg}
"""
                raw_sql = call_llm(
                    system_prompt=system_prompt,
                    user_prompt="Hãy sửa câu SQL bị lỗi và chỉ trả về câu SQL đã sửa.",
                    temperature=0.0,
                    max_tokens=1200,
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
