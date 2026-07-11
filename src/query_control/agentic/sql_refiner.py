# -*- coding: utf-8 -*-
from __future__ import annotations
import sys
import duckdb
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))
from src.query_control.llm_helper import call_llm

from src.query_control.agentic.canonical_normalizer import CanonicalNormalizer

class SQLRefiner:
    """Agent thực thi SQL và tự sửa lỗi nếu cần."""
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.normalizer = CanonicalNormalizer()
        
    def _apply_column_fixes(self, sql: str) -> str:
        """Chuẩn hóa tên huyện, xã và các cột thường bị LLM hoặc user viết nhầm."""
        replacements = {
            "Đắk Glong": "Đăk Glong",
            "Đăk Mil": "Đắk Mil",
            "Đăk RLấp": "Đắk RLấp",
            "Đăk Rlấp": "Đắk RLấp",
            "Đắk R'Lấp": "Đắk RLấp",
            "Đăk R'Lấp": "Đắk RLấp",
            "Đắk R’Lấp": "Đắk RLấp",
            "Đăk Song": "Đắk Song",
            '"administrative.town"': '"administrative.commune"',
            "'administrative.town'": "'administrative.commune'",
            "administrative.town": "administrative.commune",
            '"administrative.ward"': '"administrative.commune"',
            "'administrative.ward'": "'administrative.commune'",
            "administrative.ward": "administrative.commune",
            '"reason.noLand"': '"reason.lackProductionLand"',
            "reason.noLand": "reason.lackProductionLand",
            '"reason.lackLand"': '"reason.lackProductionLand"',
            "reason.lackLand": "reason.lackProductionLand",
            '"reason.noProductionLand"': '"reason.lackProductionLand"',
            "reason.noProductionLand": "reason.lackProductionLand",
            "Xã Đắk Lao": "Xã  Đắk Lao",
            "Xã Dak Lao": "Xã  Đắk Lao",
            "Xã Đak Lao": "Xã  Đắk Lao",
            "Đắk N'Drót": "Đắk NDrót",
            "Đắk N’Drót": "Đắk NDrót",
            "Đắk N\\'Drót": "Đắk NDrót",
            "Đắk N''Drót": "Đắk NDrót",
            "Đắk NDrót": "Đắk NDrót",
            "Đắk R'lấp": "Đắk RLấp",
            "Đắk R''lấp": "Đắk RLấp",
            "Đắk R'Lấp": "Đắk RLấp",
            "Đắk R''Lấp": "Đắk RLấp",
            "Đắk D'Rông": "Đắk DRông",
            "Đắk D''Rông": "Đắk DRông",
            "Đắk D’Rông": "Đắk DRông",
            "Xã Đắk D'Rông": "Xã Đắk DRông",
            "classify = 'Nghèo'": "classify = 'Hộ nghèo'",
            "classify = 'Cận nghèo'": "classify = 'Hộ cận nghèo'",
            "classify ILIKE '%Nghèo%'": "classify = 'Hộ nghèo'",
            "classify ILIKE '%Cận nghèo%'": "classify = 'Hộ cận nghèo'"
        }
        for wrong, correct in replacements.items():
            sql = sql.replace(wrong, correct)
            
        import re
        sql = re.sub(r'"?householdName"?', '"family.hostName"', sql)
        sql = re.sub(r'(?<!family\.)(?<!family\.")"?\bhostName"?', '"family.hostName"', sql)
        sql = re.sub(r'"?member\.name"?', '"member.fullName"', sql)
        sql = re.sub(r'"?member\.relationship(?!\w)(?!ToHost)"?', '"member.relationshipToHost"', sql)
        return sql

    def execute_and_refine(self, sql_query: str, user_question: str, schema_info: dict, max_retries: int = 3) -> tuple[pd.DataFrame | None, str]:
        """Thực thi SQL. Nếu lỗi, yêu cầu LLM sửa lại."""
        current_sql = self.normalizer.sanitize_sql(sql_query)
        current_sql = self._apply_column_fixes(current_sql)
        
        for attempt in range(max_retries):
            try:
                # Mở connection read-only để tránh file lock
                with duckdb.connect(str(self.db_path), read_only=True) as con:
                    df = con.execute(current_sql).df()
                    
                    # TỰ KIỂM TRA LỖI LOGIC TỔNG QUÁT (SELF-CORRECTION FOR ALL LOGIC ERRORS)
                    # 1. Bắt lỗi GROUP BY thiếu trong SELECT cho TẤT CẢ các trường
                    for raw_stmt in current_sql.split(';'):
                        stmt = raw_stmt.strip()
                        if not stmt:
                            continue
                        stmt_upper = stmt.upper()
                        if "GROUP BY" in stmt_upper:
                            import re
                            gb_part = stmt_upper.split("GROUP BY")[-1].split("ORDER BY")[0].split("LIMIT")[0].split("HAVING")[0]
                            # Loại bỏ các chuỗi text trong nháy đơn để không bị hiểu nhầm là cột (vd: 'Hộ DTTS')
                            gb_part_clean = re.sub(r"'[^']*'", "", gb_part)
                            gb_tokens = re.findall(r'"?([a-zA-Z0-9_\.]+)"?', gb_part_clean)
                            sql_keywords = ('ASC', 'DESC', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'TRUE', 'FALSE', 'AND', 'OR', 'IS', 'NOT', 'NULL', 'COALESCE', 'ROUND', 'SUM', 'COUNT', 'AVG', 'MIN', 'MAX', 'CAST', 'AS', 'BETWEEN', 'ILIKE', 'LIKE', 'IN', 'ON', 'FROM', 'WHERE', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'SELECT', 'UNION', 'ALL')
                            gb_fields = [token for token in gb_tokens if not token.isnumeric() and token.upper() not in sql_keywords]
                            
                            select_clause = stmt_upper.split("FROM")[0]
                            missing_fields = []
                            for field in gb_fields:
                                clean_field = field.replace('"', '').strip()
                                # Chỉ kiểm tra các trường là tên cột thực tế (có dấu chấm hoặc là 'CLASSIFY')
                                if clean_field and ('.' in clean_field or clean_field == 'CLASSIFY') and clean_field not in select_clause:
                                    missing_fields.append(clean_field)
                            if missing_fields:
                                raise ValueError(f"LỖI LOGIC: SQL dùng GROUP BY với các trường ({', '.join(missing_fields)}) nhưng QUÊN đưa vào mệnh đề SELECT. Theo quy tắc hiển thị dữ liệu biểu đồ/báo cáo, tất cả các trường GROUP BY phải có mặt trong SELECT (kèm AS alias phù hợp). Yêu cầu thêm vào SELECT ngay!")

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
  + CSDL CHỈ CÓ 2 BẢNG là households và members. TẤT CẢ các tên như deprivation, reason, support, transition, children, policy ĐỀU LÀ TIỀN TỐ CỦA CỘT trong bảng households, TUYỆT ĐỐI KHÔNG PHẢI TÊN BẢNG! Khi gặp lỗi "Referenced table not found", đó là do bạn đã viết tên cột (vd: deprivation.healthInsurance) mà QUÊN bọc trong ngoặc kép! Hãy bọc trong ngoặc kép: "deprivation.healthInsurance".
  + Cột chứa dấu chấm (vd: administrative.year) phải bọc trong ngoặc kép: "administrative.year"
  + Kiểm tra lỗi chính tả tên cột. Bảng households có trạng thái nghèo là "classify", địa phương "administrative.district", "administrative.commune", tên chủ hộ là "family.hostName" (TUYỆT ĐỐI KHÔNG dùng householdName hay hostName). Bảng members có tên thành viên là "member.fullName" và quan hệ với chủ hộ là "member.relationshipToHost".
  + Các giá trị text khi so sánh phải dùng dấu nháy đơn.
  + Tên huyện trong CSDL có dạng 'Huyện Cư Jút', 'Huyện Đắk Mil', 'Huyện Đắk RLấp'. Khi dùng ILIKE với Đắk R'Lấp hãy dùng `ILIKE '%RLấp%'` (TUYỆT ĐỐI KHÔNG dùng '%Huyện RLấp%'). Nếu hỏi tỉnh Đắk Nông thì KHÔNG lọc huyện/xã.
  + Các cột boolean như `"support.credit"`, `"reason.*"`, `"deprivation.*"` phải so sánh `= true`, KHÔNG dùng LIKE.
  + Cột `transition.endingClassify` có các giá trị chuẩn: `'Hộ không nghèo'`, `'Hộ nghèo'`, `'Hộ cận nghèo'`.

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
                    model="gpt-4o-mini",
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
                current_sql = self.normalizer.sanitize_sql(sql.strip())
                current_sql = self._apply_column_fixes(current_sql)
                
        return None, current_sql
