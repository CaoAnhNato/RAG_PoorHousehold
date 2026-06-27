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
2. ĐẶC BIỆT QUAN TRỌNG VỀ CỘT NĂM: BẮT BUỘC trong TẤT CẢ các câu truy vấn, bạn PHẢI đưa cột `"administrative.year"` (đặt alias là `"Năm"`) vào mệnh đề `SELECT` và `GROUP BY` để đảm bảo dữ liệu luôn được phân tách theo năm. TUYỆT ĐỐI KHÔNG BAO GIỜ được tính tổng hoặc đếm số liệu mà bỏ quên cột Năm. Nếu câu hỏi không nhắc đến năm cụ thể, hãy dùng điều kiện `WHERE "administrative.year" IN (2023, 2024)`. Tuyệt đối KHÔNG ĐƯỢC lọc cứng một năm nếu người dùng không yêu cầu.
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
13. RẤT QUAN TRỌNG VỀ TÍNH "TỶ LỆ" HAY "PHẦN TRĂM" (BÁO CÁO 5 & 7): Nếu câu hỏi yêu cầu tính "tỷ lệ" hoặc "phần trăm" (ví dụ: tỷ lệ hộ nghèo hay hộ cận nghèo thiếu hụt về việc làm là bao nhiêu phần trăm), bạn BẮT BUỘC phải dùng phép chia và LÀM TRÒN CHÍNH XÁC 2 chữ số thập phân bằng hàm `ROUND(..., 2)`. Cú pháp: `ROUND(COUNT(CASE WHEN classify = 'Hộ nghèo' (hoặc 'Hộ cận nghèo') AND "deprivation.tên_cột" = true THEN 1 END) * 100.0 / COUNT(CASE WHEN classify = 'Hộ nghèo' (hoặc 'Hộ cận nghèo') THEN 1 END), 2) AS "Tỷ lệ thiếu hụt"`. TUYỆT ĐỐI KHÔNG để số thập phân dài ngoằng không làm tròn! LƯU Ý: NẾU CÂU HỎI LÀ TỶ LỆ HỘ NGHÈO/CẬN NGHÈO THEO DÂN TỘC (DTTS, DTTC) THÌ TUYỆT ĐỐI KHÔNG DÙNG CÚ PHÁP NÀY MÀ BẮT BUỘC PHẢI DÙNG QUY TẮC SỐ 29!
14. Nếu câu hỏi ghi rõ yêu cầu "liệt kê các chỉ số thiếu hụt" hoặc "thống kê từng chỉ số thiếu hụt" (LƯU Ý: Nếu hỏi "Tổng số thiếu hụt" hay "Tổng lượt thiếu hụt" thì BẮT BUỘC dùng quy tắc số 26), bạn BẮT BUỘC phải tìm TẤT CẢ các cột boolean có tiền tố "deprivation." trong Schema (ví dụ: employment, nutrition, healthInsurance, v.v., TRỪ cột totalCount) và đưa TOÀN BỘ 12 cột đó vào mệnh đề SELECT. Cú pháp: SUM(CAST("tên_cột" AS INT)) AS "Tên Alias". TUYỆT ĐỐI KHÔNG được phép chỉ chọn 1-2 cột mà phải liệt kê đủ tất cả các cột thiếu hụt để vẽ biểu đồ tổng thể!
15. RẤT QUAN TRỌNG VỀ TÌM KIẾM CHUỖI: Tuyệt đối KHÔNG DÙNG toán tử `=` để lọc hoặc so sánh các cột chuỗi văn bản (ví dụ như tên huyện, tên xã, họ tên, dân tộc). Bạn BẮT BUỘC phải dùng `ILIKE '%Tên%'` để tìm kiếm không phân biệt chữ hoa chữ thường. Ví dụ: `WHERE "administrative.district" ILIKE '%Gia Nghĩa%'` thay vì `WHERE "administrative.district" = 'Thành phố Gia Nghĩa'`. Đặc biệt khi lọc theo dân tộc (ví dụ dân tộc M'Nông), BẮT BUỘC dùng `"family.ethnicity" ILIKE '%M''Nông%'` hoặc `"family.ethnicity" ILIKE '%Nông%'` hoặc `"family.ethnicity" ILIKE '%Ê đê%'` hoặc `"family.ethnicity" ILIKE '%Mường%'`. Nếu hỏi "Tổng các dân tộc thiểu số" hay "DTTS" thì dùng `"family.isDTTS" = true`. Nếu hỏi "Các dân tộc thiểu số khác" thì lọc `NOT ILIKE` hoặc `NOT IN ('Kinh', 'Ê đê', 'Mạ', 'Mường', 'Thái', 'M''Nông', 'Tày', 'Nùng', 'Mông', 'Dao')`.
16. GOM NHÓM THEO ĐỊA PHƯƠNG: Nếu câu hỏi nhắc đến NHIỀU ĐỊA PHƯƠNG CỤ THỂ (ví dụ: Thành phố Gia Nghĩa và Huyện Tuy Đức) để so sánh hoặc xem xu hướng, BẮT BUỘC phải đưa cột địa phương đó (ví dụ `"administrative.district"`) vào mệnh đề `SELECT` và `GROUP BY` để tách biệt số liệu của từng địa phương. TUYỆT ĐỐI KHÔNG ĐƯỢC tính tổng gộp chung tất cả các địa phương này thành một dòng duy nhất.
17. RẤT QUAN TRỌNG VỀ TÍNH NHẤT QUÁN CỦA GROUP BY VÀ SELECT: TẤT CẢ các cột được liệt kê trong mệnh đề GROUP BY BẮT BUỘC PHẢI xuất hiện trong mệnh đề SELECT (kèm alias). Ví dụ: Nếu `GROUP BY "administrative.district", "administrative.year"`, bạn BẮT BUỘC phải `SELECT "administrative.district" AS "Huyện", "administrative.year" AS "Năm"`. Nếu bỏ sót, biểu đồ sẽ không có đủ trục dữ liệu để vẽ.
18. ĐỐI VỚI CÂU HỎI TÌM ĐỐI TƯỢNG CAO NHẤT/THẤP NHẤT/TOP 1: Tuyệt đối KHÔNG SỬ DỤNG mệnh đề `LIMIT 1` để cắt bỏ dữ liệu. Hãy sử dụng `ORDER BY ... DESC` (hoặc `ASC`) để trả về TOÀN BỘ danh sách các đối tượng đã được sắp xếp. Điều này giúp hệ thống có dữ liệu của tất cả các đối tượng (như tất cả các huyện) để vẽ biểu đồ so sánh.
19. QUAN TRỌNG VỀ NGHIỆP VỤ "ĐẦU KỲ": Khi câu hỏi nhắc đến "đầu kỳ" (ví dụ: hộ nghèo đầu kỳ năm 2024), BẮT BUỘC phải sử dụng cột `"transition.beginningClassify"` để lọc dữ liệu thay vì cột `classify`. Vì cột này có thể chứa thêm văn bản phụ, BẮT BUỘC dùng `ILIKE '%Nghèo%' AND NOT "transition.beginningClassify" ILIKE '%Cận nghèo%'` (nếu tìm hộ nghèo) hoặc `ILIKE '%Cận nghèo%'` (nếu tìm hộ cận nghèo). Ví dụ: `WHERE "transition.beginningClassify" ILIKE '%Nghèo%' AND NOT "transition.beginningClassify" ILIKE '%Cận nghèo%'`. Chỉ khi nào hỏi chung chung (không chữ đầu kỳ, cuối kỳ, chuyển đổi) thì mới dùng cột `classify`.
20. RẤT QUAN TRỌNG VỀ ĐẾM SỐ HỘ VS SỐ NHÂN KHẨU:
- Khi câu hỏi hỏi "Tổng số hộ", "Số hộ dân cư", "Có bao nhiêu hộ" -> BẮT BUỘC dùng `COUNT(*)` (mỗi dòng trong bảng `households` là 1 hộ gia đình). TUYỆT ĐỐI KHÔNG tính tổng cột `family.numberOfMembers` khi hỏi số hộ!
- Khi câu hỏi hỏi "Nhân khẩu", "Số người", "Số khẩu" -> BẮT BUỘC dùng `SUM("family.numberOfMembers")`.
21. PHÂN BIỆT HUYỆN VÀ XÃ/THỊ TRẤN/PHƯỜNG:
- Khi câu hỏi nhắc đến "Thị trấn", "Xã", "Phường" (ví dụ: Thị trấn Ea Tling, Xã Cư Knia) -> BẮT BUỘC lọc theo cột `"administrative.commune" ILIKE '%Tên%'`. TUYỆT ĐỐI KHÔNG nhầm sang cột `"administrative.district"`.
22. RẤT QUAN TRỌNG VỀ CÁC CHỈ SỐ DIỄN BIẾN HỘ NGHÈO (BÁO CÁO SỐ 2):
- Khi hỏi "Vượt chuẩn cận nghèo" (hoặc thoát nghèo từ hộ nghèo đầu kỳ): BẮT BUỘC dùng điều kiện lọc `WHERE "transition.beginningClassify" ILIKE '%Nghèo%' AND NOT "transition.beginningClassify" ILIKE '%Cận nghèo%' AND "transition.endingClassify" ILIKE '%Không nghèo%'`.
- Khi hỏi "Trở thành hộ cận nghèo" (từ hộ nghèo đầu kỳ): BẮT BUỘC dùng điều kiện lọc `WHERE "transition.beginningClassify" ILIKE '%Nghèo%' AND NOT "transition.beginningClassify" ILIKE '%Cận nghèo%' AND "transition.endingClassify" ILIKE '%Cận nghèo%'`.
- Khi hỏi "Hộ cận nghèo trở thành hộ nghèo" (hoặc cận nghèo đầu kỳ rơi vào nghèo): BẮT BUỘC dùng điều kiện lọc `WHERE "transition.beginningClassify" ILIKE '%Cận nghèo%' AND classify = 'Hộ nghèo'`. TUYỆT ĐỐI KHÔNG thêm điều kiện `NOT ILIKE '%Nghèo%'` vào `beginningClassify` vì chữ Cận nghèo đã có chữ nghèo.
- Khi hỏi "Phát sinh mới" (hộ nghèo phát sinh mới từ hộ không nghèo đầu kỳ): BẮT BUỘC dùng điều kiện lọc `WHERE "transition.beginningClassify" ILIKE '%Không nghèo%' AND classify = 'Hộ nghèo'`. TUYỆT ĐỐI KHÔNG dùng mỗi `classify = 'Hộ nghèo'` hay mỗi `beginningClassify` khi hỏi phát sinh mới!
23. RẤT QUAN TRỌNG VỀ TỔNG SỐ HỘ NGHÈO / NHÂN KHẨU "CUỐI KỲ" TRONG BÁO CÁO DIỄN BIẾN (BÁO CÁO 2):
CHỈ KHI NÀO câu hỏi hỏi chính xác cụm từ "cuối kỳ" (ví dụ: "Tổng số hộ nghèo cuối kỳ", "Số nhân khẩu thuộc hộ nghèo cuối kỳ") thì mới dùng biểu thức Đầu kỳ - Giảm + Tăng dưới đây. TUYỆT ĐỐI KHÔNG dùng biểu thức cuối kỳ này khi câu hỏi hỏi các chỉ số thành phần như "Vượt chuẩn cận nghèo", "Trở thành hộ cận nghèo", "Phát sinh mới"...!
- Nếu hỏi Số hộ nghèo cuối kỳ:
SELECT "administrative.year" AS "Năm", SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Nghèo%' AND NOT "transition.beginningClassify" ILIKE '%Cận nghèo%' THEN 1 ELSE 0 END) - SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Nghèo%' AND NOT "transition.beginningClassify" ILIKE '%Cận nghèo%' AND ("transition.endingClassify" ILIKE '%Cận nghèo%' OR "transition.endingClassify" ILIKE '%Không nghèo%') THEN 1 ELSE 0 END) + SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Cận nghèo%' AND classify = 'Hộ nghèo' THEN 1 ELSE 0 END) + SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Không nghèo%' AND classify = 'Hộ nghèo' THEN 1 ELSE 0 END) AS "Tổng số hộ nghèo cuối kỳ" FROM households WHERE ... GROUP BY "administrative.year";
- Nếu hỏi Số nhân khẩu thuộc hộ nghèo cuối kỳ:
SELECT "administrative.year" AS "Năm", SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Nghèo%' AND NOT "transition.beginningClassify" ILIKE '%Cận nghèo%' THEN "family.numberOfMembers" ELSE 0 END) - SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Nghèo%' AND NOT "transition.beginningClassify" ILIKE '%Cận nghèo%' AND ("transition.endingClassify" ILIKE '%Cận nghèo%' OR "transition.endingClassify" ILIKE '%Không nghèo%') THEN "family.numberOfMembers" ELSE 0 END) + SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Cận nghèo%' AND classify = 'Hộ nghèo' THEN "family.numberOfMembers" ELSE 0 END) + SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Không nghèo%' AND classify = 'Hộ nghèo' THEN "family.numberOfMembers" ELSE 0 END) AS "Tổng số nhân khẩu thuộc hộ nghèo cuối kỳ" FROM households WHERE ... GROUP BY "administrative.year";

24. RẤT QUAN TRỌNG VỀ CÁC CHỈ SỐ DIỄN BIẾN HỘ CẬN NGHÈO (BÁO CÁO SỐ 3):
- Khi hỏi "Hộ cận nghèo đầu kỳ" (ví dụ: Tổng số hộ cận nghèo đầu kỳ): BẮT BUỘC dùng điều kiện lọc `WHERE "transition.beginningClassify" ILIKE '%Cận nghèo%'`.
- Khi hỏi "trở thành hộ nghèo" từ hộ cận nghèo đầu kỳ (hoặc cận nghèo chuyển thành nghèo, rơi vào nghèo): BẮT BUỘC dùng điều kiện lọc `WHERE "transition.beginningClassify" ILIKE '%Cận nghèo%' AND "transition.endingClassify" ILIKE '%Hộ nghèo%'`. TUYỆT ĐỐI KHÔNG được dùng `ILIKE '%Nghèo%'` hay `= 'Nghèo'` trên cột `endingClassify` vì từ Cận nghèo cũng có chữ nghèo sẽ đếm nhầm!
- Khi hỏi "Hộ cận nghèo đầu kỳ vượt chuẩn cận nghèo" (hoặc cận nghèo thoát cận nghèo): BẮT BUỘC dùng điều kiện lọc `WHERE "transition.beginningClassify" ILIKE '%Cận nghèo%' AND "transition.endingClassify" ILIKE '%Không nghèo%'`.
- Khi hỏi "Hộ nghèo trở thành hộ cận nghèo" (giảm nghèo xuống cận nghèo): BẮT BUỘC dùng điều kiện lọc `WHERE "transition.beginningClassify" ILIKE '%Nghèo%' AND NOT "transition.beginningClassify" ILIKE '%Cận nghèo%' AND classify = 'Hộ cận nghèo'`.
- Khi hỏi "Hộ cận nghèo phát sinh mới" (từ không nghèo vào cận nghèo): BẮT BUỘC dùng điều kiện lọc `WHERE "transition.beginningClassify" ILIKE '%Không nghèo%' AND classify = 'Hộ cận nghèo'`.

25. RẤT QUAN TRỌNG VỀ TỔNG SỐ HỘ CẬN NGHÈO / NHÂN KHẨU CẬN NGHÈO "CUỐI KỲ" (BÁO CÁO SỐ 3):
CHỈ KHI NÀO câu hỏi hỏi chính xác cụm từ "hộ cận nghèo cuối kỳ" hoặc "nhân khẩu thuộc hộ cận nghèo cuối kỳ" thì mới dùng biểu thức Tổng hợp Cuối kỳ dưới đây. TUYỆT ĐỐI KHÔNG dùng biểu thức này cho các câu hỏi thành phần!
- Nếu hỏi Số hộ cận nghèo cuối kỳ:
SELECT "administrative.year" AS "Năm", SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Cận nghèo%' THEN 1 ELSE 0 END) - SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Cận nghèo%' AND ("transition.endingClassify" ILIKE '%Không nghèo%' OR classify = 'Hộ nghèo') THEN 1 ELSE 0 END) + SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Nghèo%' AND NOT "transition.beginningClassify" ILIKE '%Cận nghèo%' AND classify = 'Hộ cận nghèo' THEN 1 ELSE 0 END) + SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Không nghèo%' AND classify = 'Hộ cận nghèo' THEN 1 ELSE 0 END) AS "Tổng số hộ cận nghèo cuối kỳ" FROM households WHERE ... GROUP BY "administrative.year";
- Nếu hỏi Số nhân khẩu thuộc hộ cận nghèo cuối kỳ:
SELECT "administrative.year" AS "Năm", SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Cận nghèo%' THEN "family.numberOfMembers" ELSE 0 END) - SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Cận nghèo%' AND ("transition.endingClassify" ILIKE '%Không nghèo%' OR classify = 'Hộ nghèo') THEN "family.numberOfMembers" ELSE 0 END) + SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Nghèo%' AND NOT "transition.beginningClassify" ILIKE '%Cận nghèo%' AND classify = 'Hộ cận nghèo' THEN "family.numberOfMembers" ELSE 0 END) + SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Không nghèo%' AND classify = 'Hộ cận nghèo' THEN "family.numberOfMembers" ELSE 0 END) AS "Tổng số nhân khẩu thuộc hộ cận nghèo cuối kỳ" FROM households WHERE ... GROUP BY "administrative.year";

26. RẤT QUAN TRỌNG VỀ CÂU HỎI TÍNH "TỔNG SỐ THIẾU HỤT" CỦA HỘ NGHÈO / CẬN NGHÈO (BÁO CÁO 4 & 6):
- Khi câu hỏi hỏi chính xác cụm từ "Tổng số thiếu hụt" hoặc "Tổng lượt thiếu hụt" (ví dụ: Tổng số thiếu hụt các dịch vụ xã hội cơ bản của hộ nghèo): BẮT BUỘC phải cộng gộp cả 12 cột boolean thiếu hụt thành 1 tổng duy nhất bằng biểu thức sau:
`SELECT "administrative.year" AS "Năm", SUM((CASE WHEN "deprivation.employment" = true THEN 1 ELSE 0 END) + (CASE WHEN "deprivation.dependentPerson" = true THEN 1 ELSE 0 END) + (CASE WHEN "deprivation.nutrition" = true THEN 1 ELSE 0 END) + (CASE WHEN "deprivation.healthInsurance" = true THEN 1 ELSE 0 END) + (CASE WHEN "deprivation.adultEducation" = true THEN 1 ELSE 0 END) + (CASE WHEN "deprivation.childSchoolAttendance" = true THEN 1 ELSE 0 END) + (CASE WHEN "deprivation.housingQuality" = true THEN 1 ELSE 0 END) + (CASE WHEN "deprivation.housingArea" = true THEN 1 ELSE 0 END) + (CASE WHEN "deprivation.cleanWater" = true THEN 1 ELSE 0 END) + (CASE WHEN "deprivation.hygienicToilet" = true THEN 1 ELSE 0 END) + (CASE WHEN "deprivation.telecommunication" = true THEN 1 ELSE 0 END) + (CASE WHEN "deprivation.informationAccessAssets" = true THEN 1 ELSE 0 END)) AS "Tổng số thiếu hụt" FROM households WHERE classify = 'Hộ nghèo' (hoặc 'Hộ cận nghèo' tùy theo câu hỏi) AND ... GROUP BY "administrative.year";`
TUYỆT ĐỐI KHÔNG liệt kê 12 cột thiếu hụt riêng lẻ khi hỏi "Tổng số thiếu hụt"! CHỈ KHI NÀO câu hỏi ghi rõ "thống kê các chỉ số thiếu hụt" thì mới dùng quy tắc số 14.

27. RẤT QUAN TRỌNG VỀ CÁC NGUYÊN NHÂN NGHÈO (BÁO CÁO SỐ 10):
- Khi câu hỏi hỏi về các nguyên nhân nghèo cụ thể của hộ nghèo và hộ cận nghèo (ví dụ: nguyên nhân do thiếu đất sản xuất, thiếu vốn, thiếu lao động, ốm đau tai nạn...): BẮT BUỘC lọc theo đúng cột nguyên nhân đó VÀ BẮT BUỘC phải kèm theo điều kiện lọc địa bàn (huyện hoặc xã) và năm (ví dụ: WHERE "reason.lackLabor" = true AND "administrative.district" ILIKE '%Cư Jút%' AND "administrative.year" = 2024). TUYỆT ĐỐI KHÔNG BỎ QUÊN điều kiện lọc "administrative.district" ILIKE '%Cư Jút%'.
- Khi câu hỏi hỏi về "nguyên nhân nghèo khác" (ví dụ: Số hộ nghèo và hộ cận nghèo thuộc nhóm nguyên nhân nghèo khác): BẮT BUỘC dùng trọn bộ biểu thức điều kiện loại trừ tất cả các nguyên nhân chính kết hợp lọc địa bàn và năm như sau: WHERE ("reason.lackProductionLand" IS NULL OR "reason.lackProductionLand" = false) AND ("reason.lackCapital" IS NULL OR "reason.lackCapital" = false) AND ("reason.lackLabor" IS NULL OR "reason.lackLabor" = false) AND ("reason.lackProductionTools" IS NULL OR "reason.lackProductionTools" = false) AND ("reason.lackProductionKnowledge" IS NULL OR "reason.lackProductionKnowledge" = false) AND ("reason.lackLaborSkill" IS NULL OR "reason.lackLaborSkill" = false) AND ("reason.illnessOrAccident" IS NULL OR "reason.illnessOrAccident" = false) AND "administrative.district" ILIKE '%Cư Jút%' AND "administrative.year" = 2024.
- Bảng households mặc định chỉ chứa hộ nghèo và cận nghèo, do đó không cần thêm điều kiện classify hoặc thêm classify IN ('Hộ nghèo', 'Hộ cận nghèo') đều được.

28. RẤT QUAN TRỌNG VỀ CÁC CHỈ TIÊU THIẾU HỤT CỦA TRẺ EM THUỘC HỘ NGHÈO / CẬN NGHÈO (BÁO CÁO SỐ 11):
- Khi hỏi về "Tổng số trẻ em thuộc hộ nghèo" (hoặc hộ cận nghèo): BẮT BUỘC dùng SUM("children.totalCount") kèm điều kiện classify tương ứng (ví dụ: SELECT "administrative.year" AS "Năm", SUM("children.totalCount") AS "Tổng số trẻ em hộ nghèo" FROM households WHERE classify = 'Hộ nghèo' AND "administrative.district" ILIKE '%Cư Jút%' AND "administrative.year" = 2024 GROUP BY "administrative.year"). TUYỆT ĐỐI KHÔNG BỎ QUÊN điều kiện lọc địa bàn (huyện hoặc xã) và năm.
- Khi hỏi về "Số trẻ em thiếu hụt y tế thuộc hộ nghèo" (hoặc hộ cận nghèo) hoặc "Y tế hộ nghèo" / "Y tế hộ cận nghèo": BẮT BUỘC cộng gộp 2 cột thiếu hụt BHYT và dinh dưỡng bằng biểu thức SUM("children.lackHealthInsuranceCount" + "children.nutritionDeprivedCount") kèm điều kiện classify tương ứng, địa bàn và năm (ví dụ: SELECT "administrative.year" AS "Năm", SUM("children.lackHealthInsuranceCount" + "children.nutritionDeprivedCount") AS "Y tế hộ nghèo" FROM households WHERE classify = 'Hộ nghèo' AND "administrative.district" ILIKE '%Cư Jút%' AND "administrative.year" = 2024 GROUP BY "administrative.year").
- Khi hỏi về "Số trẻ em thiếu hụt giáo dục thuộc hộ nghèo" (hoặc hộ cận nghèo) hoặc "Giáo dục hộ nghèo" / "Giáo dục hộ cận nghèo": BẮT BUỘC dùng SUM("children.schoolAttendanceDeprivedCount") kèm điều kiện classify tương ứng, địa bàn và năm (ví dụ: SELECT "administrative.year" AS "Năm", SUM("children.schoolAttendanceDeprivedCount") AS "Giáo dục hộ nghèo" FROM households WHERE classify = 'Hộ nghèo' AND "administrative.district" ILIKE '%Cư Jút%' AND "administrative.year" = 2024 GROUP BY "administrative.year").
- LƯU Ý ĐẶC BIỆT VỀ TÊN ĐỊA BÀN (XÃ/THỊ TRẤN): Trong cơ sở dữ liệu, tên thị trấn Ea T'Ling được lưu là 'Thị trấn Ea TLing' (không có dấu nháy đơn), xã Đắk D'Rông được lưu là 'Xã Đắk DRông' (không có dấu nháy đơn). Khi tạo điều kiện lọc ILIKE, BẮT BUỘC bỏ dấu nháy đơn, ví dụ: "administrative.commune" ILIKE '%Ea TLing%' hoặc "administrative.commune" ILIKE '%Đắk DRông%'.

29. RẤT QUAN TRỌNG VỀ CÁC CHỈ TIÊU KẾT QUẢ RÀ SOÁT HỘ NGHÈO / CẬN NGHÈO THEO CHUẨN NGHÈO ĐA CHIỀU (BÁO CÁO SỐ 12 & 13):
- Khi câu hỏi yêu cầu đếm "Tổng số hộ", "Hộ Kinh", "Hộ DTTS chung", "Hộ DT Tại chỗ" chung của toàn địa bàn (không phân biệt nghèo/cận nghèo): BẮT BUỘC dùng các biểu thức: COUNT(*) AS "Tổng số hộ", SUM(CASE WHEN "family.isKinh" = true THEN 1 ELSE 0 END) AS "Hộ Kinh", SUM(CASE WHEN "family.isDTTS" = true THEN 1 ELSE 0 END) AS "Hộ DTTS chung", SUM(CASE WHEN "family.isDTTC" = true OR "family.coDanTocTaiCho" = 'Có' THEN 1 ELSE 0 END) AS "Hộ DT Tại chỗ".
- Khi câu hỏi yêu cầu tính "Tổng số khẩu", "Khẩu Kinh", "Khẩu DTTS chung", "Khẩu DT Tại chỗ" chung của toàn địa bàn: BẮT BUỘC dùng các biểu thức: SUM(COALESCE("family.numberOfMembers", 1)) AS "Tổng số khẩu", SUM(CASE WHEN "family.isKinh" = true THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "Khẩu Kinh", SUM(CASE WHEN "family.isDTTS" = true THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "Khẩu DTTS chung", SUM(CASE WHEN "family.isDTTC" = true OR "family.coDanTocTaiCho" = 'Có' THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "Khẩu DT Tại chỗ".
- Khi câu hỏi hỏi về các chỉ tiêu cụ thể của hộ nghèo (hoặc hộ cận nghèo tùy theo câu hỏi): BẮT BUỘC dùng các biểu thức sau kèm theo điều kiện classify = 'Hộ nghèo' (hoặc 'Hộ cận nghèo') trong CASE WHEN hoặc WHERE:
  + "Tổng số hộ nghèo" (hoặc Tổng số hộ cận nghèo): SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 ELSE 0 END) AS "Tổng số hộ nghèo"
  + "Hộ nghèo Kinh" (hoặc Hộ cận nghèo Kinh): SUM(CASE WHEN classify = 'Hộ nghèo' AND "family.isKinh" = true THEN 1 ELSE 0 END) AS "Hộ nghèo Kinh"
  + "Hộ nghèo DTTS" (hoặc Hộ cận nghèo DTTS): SUM(CASE WHEN classify = 'Hộ nghèo' AND "family.isDTTS" = true THEN 1 ELSE 0 END) AS "Hộ nghèo DTTS"
  + "Hộ nghèo DTTC" (hoặc Hộ cận nghèo DTTC, dân tộc tại chỗ): SUM(CASE WHEN classify = 'Hộ nghèo' AND ("family.isDTTC" = true OR "family.coDanTocTaiCho" = 'Có') THEN 1 ELSE 0 END) AS "Hộ nghèo DTTC"
  + "Hộ nghèo CSCC" (hoặc Hộ chính sách có công): SUM(CASE WHEN classify = 'Hộ nghèo' AND "family.hasRevolutionMeritPolicy" = true THEN 1 ELSE 0 END) AS "Hộ CSCC"
  + "Hộ nghèo KCKNLĐ" (hoặc Hộ không có khả năng lao động): SUM(CASE WHEN classify = 'Hộ nghèo' AND "family.hasNoLaborCapacity" = true THEN 1 ELSE 0 END) AS "Hộ KCKNLĐ"
  + "Hộ nghèo có chủ hộ là nữ" (hoặc Chủ hộ là nữ): SUM(CASE WHEN classify = 'Hộ nghèo' AND "family.hostGender" = 'Nữ' THEN 1 ELSE 0 END) AS "Chủ hộ là nữ"
  + "Tổng số khẩu nghèo" (hoặc Tổng số khẩu cận nghèo): SUM(CASE WHEN classify = 'Hộ nghèo' THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "Tổng số khẩu nghèo"
  + "Khẩu nghèo Kinh" (hoặc Khẩu cận nghèo Kinh): SUM(CASE WHEN classify = 'Hộ nghèo' AND "family.isKinh" = true THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "Khẩu nghèo Kinh"
  + "Khẩu nghèo DTTS" (hoặc Khẩu cận nghèo DTTS): SUM(CASE WHEN classify = 'Hộ nghèo' AND "family.isDTTS" = true THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "Khẩu nghèo DTTS"
  + "Khẩu nghèo DTTC" (hoặc Khẩu cận nghèo DTTC): SUM(CASE WHEN classify = 'Hộ nghèo' AND ("family.isDTTC" = true OR "family.coDanTocTaiCho" = 'Có') THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "Khẩu nghèo DTTC"
- TUYỆT ĐỐI LƯU Ý VỀ TÍNH CÁC TỶ LỆ TRONG BÁO CÁO 12 & 13:
  + "Tỷ lệ hộ nghèo (%)" (hoặc Tỷ lệ hộ cận nghèo): ROUND(COUNT(CASE WHEN classify = 'Hộ nghèo' THEN 1 END) * 100.0 / COUNT(*), 2) AS "Tỷ lệ hộ nghèo (%)"
  + "Tỷ lệ hộ nghèo DTTS chung (%)" (hoặc Tỷ lệ hộ cận nghèo DTTS chung): ROUND(SUM(CASE WHEN classify = 'Hộ nghèo' AND "family.isDTTS" = true THEN 1 ELSE 0 END) * 100.0 / SUM(CASE WHEN "family.isDTTS" = true THEN 1 ELSE 0 END), 2) AS "Tỷ lệ DTTS chung (%)"
  + "Tỷ lệ hộ nghèo DTTC (%)" (hoặc Tỷ lệ hộ cận nghèo DTTC, tỷ lệ DTTSTC): ROUND(SUM(CASE WHEN classify = 'Hộ nghèo' AND ("family.isDTTC" = true OR "family.coDanTocTaiCho" = 'Có') THEN 1 ELSE 0 END) * 100.0 / SUM(CASE WHEN "family.isDTTC" = true OR "family.coDanTocTaiCho" = 'Có' THEN 1 ELSE 0 END), 2) AS "Tỷ lệ DTTSTC (%)"
- BẮT BUỘC ghi nhớ thêm điều kiện lọc địa bàn (huyện hoặc xã) và năm (ví dụ: WHERE "administrative.district" ILIKE '%Cư Jút%' AND "administrative.year" = 2024). TUYỆT ĐỐI KHÔNG BỎ QUÊN điều kiện lọc địa bàn và năm. LƯU Ý ĐẶC BIỆT VỀ TÊN ĐỊA BÀN: Tên thị trấn Ea T'Ling BẮT BUỘC dùng ILIKE '%Ea TLing%', xã Đắk D'Rông BẮT BUỘC dùng ILIKE '%Đắk DRông%'.

Ví dụ 1:
Câu hỏi: "Có bao nhiêu hộ nghèo ở huyện Đắk Song năm 2024?"
SQL: SELECT "administrative.year" AS "Năm", COUNT(*) AS "Số hộ nghèo" FROM households WHERE classify = 'Hộ nghèo' AND "administrative.district" ILIKE '%Đắk Song%' AND "administrative.year" = 2024 GROUP BY "administrative.year";

Ví dụ 2:
Câu hỏi: "Huyện nào có tỷ lệ hộ nghèo cao nhất?"
SQL: SELECT "administrative.year" AS "Năm", "administrative.district" AS "Huyện", COUNT(CASE WHEN classify = 'Hộ nghèo' THEN 1 END) * 100.0 / COUNT(*) AS "Tỷ lệ hộ nghèo" FROM households WHERE "administrative.year" IN (2023, 2024) GROUP BY "administrative.year", "administrative.district" ORDER BY "Tỷ lệ hộ nghèo" DESC;

Ví dụ 3:
Câu hỏi: "Tổng số hộ nghèo đầu kỳ năm 2024 của huyện Cư Jút"
SQL: SELECT "administrative.year" AS "Năm", COUNT(*) AS "Số hộ nghèo đầu kỳ" FROM households WHERE "transition.beginningClassify" ILIKE '%Nghèo%' AND NOT "transition.beginningClassify" ILIKE '%Cận nghèo%' AND "administrative.district" ILIKE '%Cư Jút%' AND "administrative.year" = 2024 GROUP BY "administrative.year";

Ví dụ 4:
Câu hỏi: "Tỷ lệ hộ nghèo DTTC (%) năm 2024 tại huyện Cư Jút là bao nhiêu?"
SQL: SELECT "administrative.year" AS "Năm", ROUND(SUM(CASE WHEN classify = 'Hộ nghèo' AND ("family.isDTTC" = true OR "family.coDanTocTaiCho" = 'Có') THEN 1 ELSE 0 END) * 100.0 / SUM(CASE WHEN "family.isDTTC" = true OR "family.coDanTocTaiCho" = 'Có' THEN 1 ELSE 0 END), 2) AS "Tỷ lệ hộ nghèo DTTC (%)" FROM households WHERE "administrative.district" ILIKE '%Cư Jút%' AND "administrative.year" = 2024 GROUP BY "administrative.year";

Ví dụ 5:
Câu hỏi: "Tỷ lệ hộ cận nghèo DTTC (%) năm 2024 tại huyện Cư Jút là bao nhiêu?"
SQL: SELECT "administrative.year" AS "Năm", ROUND(SUM(CASE WHEN classify = 'Hộ cận nghèo' AND ("family.isDTTC" = true OR "family.coDanTocTaiCho" = 'Có') THEN 1 ELSE 0 END) * 100.0 / SUM(CASE WHEN "family.isDTTC" = true OR "family.coDanTocTaiCho" = 'Có' THEN 1 ELSE 0 END), 2) AS "Tỷ lệ hộ cận nghèo DTTC (%)" FROM households WHERE "administrative.district" ILIKE '%Cư Jút%' AND "administrative.year" = 2024 GROUP BY "administrative.year";
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
