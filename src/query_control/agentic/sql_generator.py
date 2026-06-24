# -*- coding: utf-8 -*-
from __future__ import annotations
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))
from src.query_control.llm_helper import call_llm

class SQLGenerator:
    """Agent sinh lệnh DuckDB SQL trực tiếp."""
    def __init__(self):
        pass
        
    def generate(self, user_question: str, schema_info: dict) -> str:
        """Sinh câu lệnh SQL dựa trên schema và câu hỏi."""
        
        tables = ", ".join(schema_info.get("relevant_tables", []))
        schema_context = schema_info.get("schema_context", "")
        
        system_prompt = f"""Bạn là chuyên gia về DuckDB SQL. Hãy viết MỘT câu lệnh SQL để trả lời câu hỏi của người dùng.
Thông tin Schema thu gọn:
- Các bảng liên quan: {tables}

{schema_context}

Quy tắc sinh SQL:
1. LUÔN LUÔN bọc tên cột có dấu chấm trong ngoặc kép. Ví dụ: "administrative.year" thay vì administrative.year.
2. Nếu câu hỏi không nhắc đến năm cụ thể, hãy mặc định lấy dữ liệu cho cả hai năm 2023 và 2024 (Ví dụ: thêm cột "administrative.year" vào SELECT và dùng GROUP BY "administrative.year", hoặc dùng IN (2023, 2024)). Tuyệt đối KHÔNG ĐƯỢC lọc cứng một năm nếu người dùng không yêu cầu.
3. Trong bảng `households`, trạng thái nghèo là cột `classify`, có giá trị là 'Hộ nghèo' hoặc 'Hộ cận nghèo'.
4. Trả về DUY NHẤT một câu lệnh SQL, không kèm markdown code block (không dùng ```sql ... ```), không giải thích. Bắt đầu bằng SELECT.
5. Nếu câu hỏi yêu cầu liệt kê (danh sách), hãy SELECT rõ tên chủ hộ ("family.hostName") hoặc thành viên ("member.fullName").
6. Khi JOIN `households` và `members`, hãy join qua các cột: "administrative.district", "administrative.commune", "family.hostName", "administrative.year" để đảm bảo đúng chủ hộ ở đúng địa phương và đúng năm.
7. Toàn bộ cơ sở dữ liệu này là của tỉnh Đắk Nông. Nếu câu hỏi nhắc đến "Đắk Nông", KHÔNG CẦN thêm điều kiện lọc theo tên tỉnh/địa phương. Mặc định tính tổng cho toàn tỉnh.
8. Đối với các cột mang tính chất boolean (thiếu hụt, nguyên nhân nghèo...), hãy dùng `WHERE "column_name" = true` hoặc `WHERE "column_name" = 1`.
9. CHỈ SỬ DỤNG các cột được liệt kê trong phần schema. Không bịa ra tên cột khác.
10. RẤT QUAN TRỌNG: Nếu câu hỏi yêu cầu so sánh (ví dụ: nam và nữ, nghèo và cận nghèo), TUYỆT ĐỐI KHÔNG dùng mệnh đề WHERE để lọc cứng một giá trị (như WHERE gender='Nữ'). Hãy đưa cột cần so sánh vào SELECT và dùng GROUP BY để đếm cho cả hai bên.
11. ĐỂ HIỂN THỊ ĐẸP CHO NGƯỜI DÙNG: BẮT BUỘC đặt bí danh (alias) bằng Tiếng Việt có dấu cho TẤT CẢ các cột trong mệnh đề SELECT bằng từ khóa AS (ví dụ: AS "Số hộ nghèo", AS "Huyện", AS "Tên chủ hộ").
12. VỀ PHÂN TÁCH CỘT KHI ĐẾM CẢ 2 LOẠI: Nếu đếm "hộ nghèo" và "hộ cận nghèo" qua nhiều chiều (ví dụ theo từng huyện, từng năm) thì BẮT BUỘC tách 2 cột (dùng SUM(CASE...)). NHƯNG nếu hỏi "cơ cấu", "tỷ trọng" giữa nghèo và cận nghèo mà không có chiều nào khác, hãy dùng GROUP BY "classify".
13. Nếu câu hỏi yêu cầu tính "tỷ lệ" (ví dụ: tỷ lệ hộ cận nghèo), BẮT BUỘC phải dùng phép chia: COUNT(CASE WHEN classify = 'Hộ cận nghèo' THEN 1 END) * 100.0 / COUNT(*) AS "Tỷ lệ hộ cận nghèo" hoặc tương tự.
14. Nếu câu hỏi yêu cầu đếm/thống kê "những thiếu hụt" hoặc "những lý do" nào xuất hiện nhiều nhất (dựa trên các cột boolean), bạn PHẢI dùng SUM() ép kiểu cho từng cột thay vì GROUP BY. Ví dụ: SUM(CAST("deprivation.cleanWater" AS INT)) AS "Thiếu nước sinh hoạt", SUM(CAST("deprivation.hygienicToilet" AS INT)) AS "Thiếu nhà tiêu hợp vệ sinh".
15. RẤT QUAN TRỌNG VỀ TÌM KIẾM CHUỖI: Tuyệt đối KHÔNG DÙNG toán tử `=` để lọc hoặc so sánh các cột chuỗi văn bản (ví dụ như tên huyện, tên xã, họ tên). Bạn BẮT BUỘC phải dùng `ILIKE '%Tên%'` để tìm kiếm không phân biệt chữ hoa chữ thường. Ví dụ: `WHERE "administrative.district" ILIKE '%Gia Nghĩa%'` thay vì `WHERE "administrative.district" = 'Thành phố Gia Nghĩa'`. Nếu không, hệ thống sẽ bị lỗi rỗng dữ liệu (0 dòng).
16. GOM NHÓM THEO ĐỊA PHƯƠNG: Nếu câu hỏi nhắc đến NHIỀU ĐỊA PHƯƠNG CỤ THỂ (ví dụ: Thành phố Gia Nghĩa và Huyện Tuy Đức) để so sánh hoặc xem xu hướng, BẮT BUỘC phải đưa cột địa phương đó (ví dụ `"administrative.district"`) vào mệnh đề `SELECT` và `GROUP BY` để tách biệt số liệu của từng địa phương. TUYỆT ĐỐI KHÔNG ĐƯỢC tính tổng gộp chung tất cả các địa phương này thành một dòng duy nhất.
17. RẤT QUAN TRỌNG VỀ TÍNH NHẤT QUÁN CỦA GROUP BY VÀ SELECT: TẤT CẢ các cột được liệt kê trong mệnh đề GROUP BY BẮT BUỘC PHẢI xuất hiện trong mệnh đề SELECT (kèm alias). Ví dụ: Nếu `GROUP BY "administrative.district", "administrative.year"`, bạn BẮT BUỘC phải `SELECT "administrative.district" AS "Huyện", "administrative.year" AS "Năm"`. Nếu bỏ sót, biểu đồ sẽ không có đủ trục dữ liệu để vẽ.

Ví dụ:
Câu hỏi: "Có bao nhiêu hộ nghèo ở huyện Đắk Song năm 2024?"
SQL: SELECT COUNT(*) AS "Số hộ nghèo" FROM households WHERE classify = 'Hộ nghèo' AND "administrative.district" ILIKE '%Đắk Song%' AND "administrative.year" = 2024;
"""
        
        raw_sql = call_llm(
            system_prompt=system_prompt,
            user_prompt=f"Câu hỏi: {user_question}",
            temperature=0.0,
            max_tokens=500,
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
            
        return sql.strip()
