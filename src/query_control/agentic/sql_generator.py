# -*- coding: utf-8 -*-
from __future__ import annotations
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))
from src.query_control.llm_helper import call_llm

class SQLGenerator:
    """Agent sinh lệnh DuckDB SQL trực tiếp với Ultra-Compressed Prompting."""
    def __init__(self):
        # Từ điển quy tắc thu gọn cực đại (Nguyên tắc: Ngắn gọn, súc tích, chính xác 100%)
        self.RULE_INDEX = {
            "core": """1. CẤU TRÚC BẢNG & TÊN CỘT (CỰC KÌ QUAN TRỌNG): Trong CSDL DuckDB này, CHỈ CÓ 2 BẢNG duy nhất là `households` (bảng hộ gia đình) và `members` (bảng thành viên). TẤT CẢ các chỉ số đo lường như thiếu hụt dịch vụ (`"deprivation.*"`), nguyên nhân nghèo (`"reason.*"`), hỗ trợ (`"support.*"`), diễn biến (`"transition.*"`), trẻ em (`"children.*"`), chính sách (`"policy.*"`) ĐỀU LÀ CỘT nằm trong bảng `households`. TUYỆT ĐỐI KHÔNG BỊA RA TÊN BẢNG MỚI (như bảng `deprivation`, `reason`, `support`, `transition`... KHÔNG HỀ TỒN TẠI!). Tên cột có dấu chấm BẮT BUỘC phải bọc trong ngoặc kép (VD: `"deprivation.healthInsurance"`, `"administrative.year"`).
1b. TÊN CHỦ HỘ & TRA CỨU HỘ: Khi hỏi về tên chủ hộ hay tìm kiếm thông tin theo tên chủ hộ/hộ gia đình (VD: 'hộ phùng thị ánh', 'chủ hộ nguyễn văn a'), BẮT BUỘC lọc theo cột `"family.hostName" ILIKE '%Phùng Thị Ánh%'` trong bảng `households`. TUYỆT ĐỐI KHÔNG DÙNG `"householdName"` hay `"hostName"` (các cột này KHÔNG HỀ TỒN TẠI!). Khi hỏi về tên thành viên trong bảng `members`, dùng cột `m."member.name" ILIKE '%...%'`.
2. LUÔN BẮT BUỘC có cột `"administrative.year"` AS `"Năm"` trong SELECT và GROUP BY (nếu JOIN bảng thì ghi rõ `h."administrative.year"`). Nếu không hỏi năm cụ thể, mặc định `WHERE "administrative.year" IN (2023, 2024)`.
3. Cột `classify` trong bảng `households` CHỈ nhận giá trị `'Hộ nghèo'` hoặc `'Hộ cận nghèo'`.
4. BẮT BUỘC đặt alias tiếng Việt có dấu cho TẤT CẢ cột SELECT (VD: AS `"Số hộ nghèo"`).
5. TÌM KIẾM CHUỖI & ĐỊA DANH: BẮT BUỘC dùng `ILIKE '%Tên%'`. CSDL ĐÃ BỎ dấu nháy đơn trong địa danh. TUYỆT ĐỐI KHÔNG ghép từ 'Huyện' hoặc 'Xã' liền trước từ khóa viết tắt khi dùng ILIKE (VD: "Đắk R'lấp" -> `ILIKE '%RLấp%'` hoặc `ILIKE '%Đắk RLấp%'`, TUYỆT ĐỐI KHÔNG dùng `ILIKE '%Huyện RLấp%'`; "Đắk N'Drót" -> `ILIKE '%NDrót%'`). Nếu hỏi toàn tỉnh Đắk Nông thì KHÔNG lọc theo district hay commune.
6. Phân biệt Huyện và Xã (CỰC KÌ QUAN TRỌNG): Huyện/Thành phố/Thị xã (như Thành phố Gia Nghĩa, Huyện Tuy Đức, Huyện Đắk Glong...) BẮT BUỘC lọc theo `"administrative.district"`. Xã/Phường/Thị trấn BẮT BUỘC lọc theo `"administrative.commune"`. TUYỆT ĐỐI KHÔNG lọc Thành phố Gia Nghĩa trong cột commune!
7. Đếm hộ -> `COUNT(*)`, Đếm nhân khẩu -> `SUM("family.numberOfMembers")`. Khi đếm gộp nghèo và cận nghèo theo nhiều chiều thì tách 2 cột bằng SUM(CASE).
8. TẤT CẢ các cột trong GROUP BY BẮT BUỘC phải xuất hiện trong SELECT.""",

            "join": """9. TRUY VẤN THÀNH VIÊN (BẮT BUỘC JOIN): Khi hỏi về ĐẶC ĐIỂM CỦA TỪNG THÀNH VIÊN (dân tộc thành viên m."member.ethnicity", năm sinh thành viên m."member.birthYear", độ tuổi thành viên), BẮT BUỘC JOIN bảng members m với households h qua: m."administrative.district" = h."administrative.district" AND m."administrative.commune" = h."administrative.commune" AND m."family.hostName" = h."family.hostName" AND m."administrative.year" = h."administrative.year". Khi JOIN LUÔN ghi rõ tiền tố bảng h. hoặc m. cho tất cả các cột (ví dụ h."administrative.year"). Khi đếm số thành viên dùng COUNT(m.*) hoặc SUM(CASE...). TUYỆT ĐỐI KHÔNG lấy cột của chủ hộ (như family.hostBirthYear hay family.ethnicity) khi hỏi về thành viên. LƯU Ý: Tên thành viên trong bảng members là cột `m."member.fullName"`, quan hệ với chủ hộ là `m."member.relationshipToHost"`.""",

            "deprivation": """10. THIẾU HỤT DỊCH VỤ CƠ BẢN: Liệt kê chỉ số dùng các cột boolean `"deprivation.*" = true`. Tỷ lệ %: `ROUND(COUNT(CASE WHEN "col" = true THEN 1 END) * 100.0 / COUNT(*), 2)`. Tổng lượt thiếu hụt: cộng gộp cả 12 cột boolean.""",

            "transition": """11. DIỄN BIẾN / ĐẦU KỲ: Dùng `"transition.beginningClassify"` và `"transition.endingClassify"`. Giá trị chuẩn là `'Hộ nghèo'`, `'Hộ cận nghèo'`, hoặc `'Hộ không nghèo'` (BẮT BUỘC có chữ 'Hộ' phía trước, VD: `'Hộ không nghèo'`, TUYỆT ĐỐI KHÔNG dùng `'Không nghèo'`). Vượt chuẩn cận nghèo: đầu kỳ Nghèo -> cuối Không nghèo. Trở thành cận nghèo: đầu Nghèo -> cuối Cận nghèo. Phát sinh mới: đầu Không nghèo -> cuối Nghèo/Cận nghèo.""",

            "demographics": """12. DÂN TỘC / ĐA CHIỀU: Tổng hộ -> `COUNT(*)`. Hộ Kinh -> `SUM(CASE WHEN "family.isKinh" = true THEN 1 ELSE 0 END)`. Hộ DTTS -> `"family.isDTTS" = true`. Hộ DTTC -> `"family.isDTTC" = true OR "family.coDanTocTaiCho" = 'Có'` (LƯU Ý: Khi SELECT đếm số hộ DTTC trong bảng tổng hợp dân tộc, BẮT BUỘC đặt alias là AS "Hộ DTTC (thuộc DTTS)" để làm rõ DTTC là tập con nằm trong DTTS, tránh người đọc hiểu lầm khi cộng tổng). Tỷ lệ % dân tộc BẮT BUỘC dùng phép chia `ROUND(SUM(DTTS) * 100.0 / SUM(Tổng), 2)`. CSCC: `"policy.hasRevolutionMeritPolicy" = true`. Chủ hộ nữ / hộ nghèo là nữ: `"family.hostGender" = 'Nữ'`. LƯU Ý: Nếu hỏi cơ cấu dân tộc của THÀNH VIÊN thì dùng cột `m."member.ethnicity"` trong bảng `members`.""",

            "children": """13. TRẺ EM: Tổng trẻ em -> `SUM("children.totalCount")`. Trẻ em thiếu hụt y tế -> `SUM("children.lackHealthInsuranceCount" + "children.nutritionDeprivedCount")`. Trẻ thiếu hụt giáo dục -> `SUM("children.schoolAttendanceDeprivedCount")`.""",

            "reason": """14. NGUYÊN NHÂN NGHÈO & HỖ TRỢ: Lọc theo cột boolean nguyên nhân (`"reason.*" = true`) hoặc hỗ trợ (`"support.*" = true`). VD: Hỗ trợ tín dụng ưu đãi -> `"support.credit" = true` (TUYỆT ĐỐI KHÔNG dùng `reason.lackCapital LIKE` hay text search cho các cột boolean này). Nguyên nhân khác: tất cả cột lý do chính = false.""",

            "sort": """15. NHẤT (cao nhất, thấp nhất, nhiều nhất, ít nhất): Dùng `ORDER BY ... DESC/ASC LIMIT 1`."""
        }
        # Thư viện Khung Cấu Trúc Động (Dynamic Skeleton Library) bao phủ 100% các câu hỏi kiểm thử
        self.SKELETON_LIBRARY = {
            "AGGREGATION": 'SELECT "administrative.year" AS "Năm", <dimension> AS "<Alias>", COUNT(*) AS "Số hộ nghèo" FROM households WHERE <conditions> GROUP BY "administrative.year", <dimension> ORDER BY "administrative.year";',
            "RANKING_TOP_N": 'SELECT "administrative.year" AS "Năm", <dimension> AS "<Alias>", COUNT(*) AS "Số lượng hộ" FROM households WHERE <conditions> GROUP BY "administrative.year", <dimension> ORDER BY COUNT(*) DESC LIMIT <N>;',
            "LONGITUDINAL_TRANSITION": 'SELECT "administrative.year" AS "Năm", "transition.beginningClassify" AS "Phân loại đầu kỳ", "transition.endingClassify" AS "Phân loại cuối kỳ", COUNT(*) AS "Số lượng hộ" FROM households WHERE <conditions> GROUP BY "administrative.year", "transition.beginningClassify", "transition.endingClassify" ORDER BY "administrative.year";',
            "MEMBER_JOIN": 'SELECT h."administrative.year" AS "Năm", m."member.fullName" AS "Tên thành viên", m."member.relationshipToHost" AS "Quan hệ với chủ hộ", <member_and_household_attributes> FROM households h JOIN members m ON h."administrative.district" = m."administrative.district" AND h."administrative.commune" = m."administrative.commune" AND h."family.hostName" = m."family.hostName" AND h."administrative.year" = m."administrative.year" WHERE <conditions> LIMIT 50;',
            "DEPRIVATION_MULTIDIMENSIONAL": 'SELECT "administrative.year" AS "Năm", <dimension> AS "<Alias>", COUNT(CASE WHEN "<deprivation_col>" = true THEN 1 END) AS "Số hộ thiếu hụt", ROUND(COUNT(CASE WHEN "<deprivation_col>" = true THEN 1 END) * 100.0 / COUNT(*), 2) AS "Tỷ lệ % thiếu hụt" FROM households WHERE <conditions> GROUP BY "administrative.year", <dimension>;',
            "REASONS_AND_SUPPORT": 'SELECT "administrative.year" AS "Năm", <dimension> AS "<Alias>", COUNT(CASE WHEN "<reason_or_support_col>" = true THEN 1 END) AS "Số hộ" FROM households WHERE <conditions> GROUP BY "administrative.year", <dimension>;',
            "LIST_DETAILS": 'SELECT "administrative.year" AS "Năm", "administrative.district" AS "Huyện/TP", "administrative.commune" AS "Xã/Phường", "family.hostName" AS "Tên chủ hộ", "classify" AS "Phân loại", <requested_attributes> FROM households WHERE <conditions> LIMIT 50;'
        }

    def _select_dynamic_skeleton(self, query: str, schema_info: dict = None) -> tuple[str, str]:
        """Phân loại ý định (Intent) từ câu hỏi và schema để chọn Khung SQL Động phù hợp nhất."""
        q = query.lower()
        relevant_tables = schema_info.get("relevant_tables", []) if schema_info else []
        relevant_columns = schema_info.get("relevant_columns", []) if schema_info else []
        
        # 1. Member JOIN
        if "members" in relevant_tables or any(w in q for w in ["thành viên", "nhân khẩu", "từng người", "vợ/chồng", "con của"]):
            return "MEMBER_JOIN", self.SKELETON_LIBRARY["MEMBER_JOIN"]
            
        # 2. List Details / Household Lookup (Liệt kê chi tiết hộ hoặc tra cứu thông tin cụ thể của 1/nhiều hộ)
        if any(w in q for w in ["danh sách", "liệt kê", "ai là chủ hộ", "tên những hộ", "những hộ nào", "mã hộ", "chủ hộ", "tìm hộ", "thông tin hộ"]) or ("hộ " in q and any(w in q for w in ["nguyễn", "trần", "lê", "phạm", "phùng", "hoàng", "huỳnh", "phan", "vũ", "võ", "đặng", "bùi", "đỗ", "hồ", "ngô", "dương", "lý", "giàng", "lầu", "hầu", "vàng", "sùng", "sung", "thị", "văn", "mã", "id"])):
            if not any(w in q for w in ["tỷ lệ", "bao nhiêu hộ", "biểu đồ", "vẽ", "tổng số hộ", "số lượng hộ", "thống kê"]):
                return "LIST_DETAILS", self.SKELETON_LIBRARY["LIST_DETAILS"]
            
        # 3. Longitudinal / Transition (Diễn biến qua các năm)
        if any(w in q for w in ["diễn biến", "thoát nghèo", "vượt chuẩn", "trở thành", "phát sinh", "đầu kỳ", "cuối kỳ"]):
            return "LONGITUDINAL_TRANSITION", self.SKELETON_LIBRARY["LONGITUDINAL_TRANSITION"]
            
        # 4. Deprivation Multidimensional (Thiếu hụt dịch vụ)
        if any(c.startswith("deprivation.") for c in relevant_columns) or any(w in q for w in ["thiếu hụt", "dịch vụ cơ bản", "chiều thiếu hụt", "nước sạch", "nhà tiêu", "việc làm", "bảo hiểm", "dinh dưỡng", "giáo dục", "nhà ở", "viễn thông", "thông tin"]):
            return "DEPRIVATION_MULTIDIMENSIONAL", self.SKELETON_LIBRARY["DEPRIVATION_MULTIDIMENSIONAL"]
            
        # 5. Reasons and Support
        if any(c.startswith("reason.") or c.startswith("support.") for c in relevant_columns) or any(w in q for w in ["nguyên nhân", "lý do", "thiếu đất", "thiếu vốn", "thiếu lao động", "ốm đau", "hỗ trợ", "tín dụng", "vay vốn"]):
            return "REASONS_AND_SUPPORT", self.SKELETON_LIBRARY["REASONS_AND_SUPPORT"]
            
        # 6. Ranking Top N
        if any(w in q for w in ["top", "cao nhất", "thấp nhất", "nhiều nhất", "ít nhất", "lớn nhất", "nhỏ nhất", "đứng đầu"]):
            return "RANKING_TOP_N", self.SKELETON_LIBRARY["RANKING_TOP_N"]
            
        # 7. Default Aggregation / Count / Chart
        return "AGGREGATION", self.SKELETON_LIBRARY["AGGREGATION"]
        
    def _prune_rules(self, query: str, schema_info: dict = None) -> list[str]:
        q = query.lower()
        active = [self.RULE_INDEX["core"]]
        
        relevant_tables = schema_info.get("relevant_tables", []) if schema_info else []
        relevant_columns = schema_info.get("relevant_columns", []) if schema_info else []
        
        # Bảng members CHỈ được JOIN khi relevant_tables có chứa "members" (hoặc từ khóa rõ ràng về thành viên)
        # Tuyệt đối KHÔNG kích hoạt rule join khi hỏi về chủ hộ (tên, năm sinh, dân tộc) vì đã có sẵn trong households!
        if "members" in relevant_tables or any(w in q for w in ["thành viên", "nhân khẩu", "từng người", "vợ/chồng", "con của"]):
            active.append(self.RULE_INDEX["join"])
            
        # Kích hoạt rule deprivation khi cụm cột deprivation được kích hoạt hoặc có từ khóa
        if any(c.startswith("deprivation.") for c in relevant_columns) or any(w in q for w in ["thiếu hụt", "dịch vụ", "cơ bản", "chỉ số", "nước", "nhà tiêu", "việc làm", "bảo hiểm", "dinh dưỡng", "giáo dục", "nhà ở", "viễn thông", "thông tin", "chiều"]):
            active.append(self.RULE_INDEX["deprivation"])
            
        if any(w in q for w in ["đầu kỳ", "cuối kỳ", "diễn biến", "thoát nghèo", "vượt chuẩn", "trở thành", "phát sinh"]):
            active.append(self.RULE_INDEX["transition"])
            
        # Kích hoạt rule demographics khi hỏi về chủ hộ, dân tộc, mức sống
        if any(c.startswith("family.") or c.startswith("policy.") for c in relevant_columns) or any(w in q for w in ["dân tộc", "kinh", "dtts", "thiểu số", "tại chỗ", "cscc", "công", "chủ hộ", "nam", "nữ", "tuổi", "mức sống", "trung bình", "năm sinh", "liệt kê"]):
            active.append(self.RULE_INDEX["demographics"])
            
        if any(c.startswith("children.") for c in relevant_columns) or any(w in q for w in ["trẻ em", "bhyt", "giáo dục", "y tế", "dinh dưỡng"]):
            active.append(self.RULE_INDEX["children"])
            
        if any(c.startswith("reason.") for c in relevant_columns) or any(w in q for w in ["nguyên nhân", "lý do", "thiếu đất", "thiếu vốn", "thiếu lao động", "ốm đau", "công cụ", "kiến thức", "kỹ năng"]):
            active.append(self.RULE_INDEX["reason"])
            
        if any(w in q for w in ["nhất", "cao", "nhiều", "thấp", "ít", "limit", "order by", "top"]):
            active.append(self.RULE_INDEX["sort"])
            
        return active

    def generate(self, user_question: str, schema_info: dict) -> str:
        """Sinh câu lệnh SQL siêu tốc dựa trên schema thu gọn, Dynamic Skeleton và Ultra-Compressed Rules."""
        tables = ", ".join(schema_info.get("relevant_tables", []))
        schema_context = schema_info.get("schema_context", "")
        
        # Priority 1: Planner Cache Hit (Explicit Skeleton) vs Priority 2: Cache Miss (Dynamic Core Skeleton)
        if "similar_sql_template" in schema_info and schema_info["similar_sql_template"].get("old_sql"):
            t = schema_info["similar_sql_template"]
            skeleton_name = "PLANNER_CACHE_HIT_EXPLICIT_SKELETON"
            skeleton_sql = t.get('old_sql', '')
            skeleton_instruction = f"""[PLANNER CACHE HIT - EXPLICIT SKELETON (ƯU TIÊN TUYỆT ĐỐI)]:
Dưới đây là câu lệnh SQL đã chạy thành công cho câu hỏi tương tự ({t.get('old_q', '')}):
SKELETON TO FOLLOW: {skeleton_sql}
CHỈ THỊ: Hãy giữ NGUYÊN cấu trúc và logic của câu SQL trên. CHỈ thay đổi các giá trị điều kiện (huyện, xã, năm, phân loại, tên chỉ tiêu...) để khớp chính xác với câu hỏi mới."""
        else:
            skeleton_name, skeleton_sql = self._select_dynamic_skeleton(user_question, schema_info)
            skeleton_instruction = f"""[DYNAMIC SKELETON - {skeleton_name}]:
SKELETON TO FOLLOW: {skeleton_sql}
CHỈ THỊ: Dùng khung SQL trên làm mẫu chuẩn. Thay thế các placeholder (<dimension>, <conditions>, <Alias>...) bằng đúng tên cột và điều kiện trong schema dưới đây."""

        active_rules = self._prune_rules(user_question, schema_info)
        rules_str = "\n\n".join(active_rules)

        system_prompt = f"""ROLE: High-Speed DuckDB SQL Engine. Output ONLY raw executable SQL without markdown or explanation.
Tables: {tables}
{schema_context}

{skeleton_instruction}

GUARDRAIL CONSTRAINTS (BẮT BUỘC TUÂN THỦ):
{rules_str}"""
        print(f"\n[SQLGenerator] Dynamic Skeleton Selected: [{skeleton_name}]. Active Rules: {len(active_rules)} groups. Prompt Length: {len(system_prompt)} chars.")
        
        raw_sql = call_llm(
            system_prompt=system_prompt,
            user_prompt=f"Câu hỏi: {user_question}",
            temperature=0.0,
            max_tokens=500,
            model="gpt-4o-mini",
            response_json=False
        )
        
        sql = raw_sql.strip()
        if sql.startswith("```sql"): sql = sql[6:]
        if sql.startswith("```"): sql = sql[3:]
        if sql.endswith("```"): sql = sql[:-3]
            
        return sql.strip()

    def repair_sql_from_template(self, old_question: str, old_sql: str, new_question: str) -> str:
        """
        [Route 2: Few-shot SQL Repair]
        Sử dụng câu hỏi cũ và câu SQL chuẩn của nó làm template (few-shot example),
        đối chiếu với câu hỏi mới để điều chỉnh các tham số (năm, địa danh, mã chỉ tiêu).
        Sử dụng model gpt-4o-mini siêu nhanh theo chỉ định của người dùng.
        """
        system_prompt = f"""Bạn là chuyên gia sửa đổi và tối ưu DuckDB SQL siêu tốc.
Dưới đây là một cặp Câu hỏi cũ và câu lệnh SQL chuẩn 100% của nó (Ground Truth Template).
Nhiệm vụ của bạn là so sánh Câu hỏi mới với Câu hỏi cũ, từ đó thay đổi các giá trị điều kiện trong mệnh đề WHERE (như năm, tên huyện, tên xã, tên chủ hộ, tên chỉ tiêu) cho phù hợp với Câu hỏi mới.
TUYỆT ĐỐI KHÔNG thay đổi cấu trúc JOIN, không đổi bí danh (alias) và không bịa ra tên bảng/cột mới.

LƯU Ý QUAN TRỌNG:
1. Cột `classify` CHỈ có 2 giá trị là 'Hộ nghèo' hoặc 'Hộ cận nghèo'. KHÔNG DÙNG 'nghèo', 'cận nghèo' hay 'thoát nghèo' cho cột này.
2. Nếu câu hỏi mới yêu cầu lấy giá trị "nhất" (cao nhất, nhiều nhất, thấp nhất...), BẮT BUỘC phải thêm hoặc giữ lại mệnh đề `ORDER BY ... LIMIT 1` (hoặc LIMIT 5) ở cuối câu lệnh SQL để tránh trả về quá nhiều dữ liệu.
3. Cột `transition.endingClassify` có các giá trị: `'Hộ không nghèo'`, `'Hộ nghèo'`, `'Hộ cận nghèo'` (BẮT BUỘC có chữ 'Hộ').
4. Các cột boolean như `"support.credit"`, `"reason.*"`, `"deprivation.*"` phải so sánh `= true`, KHÔNG dùng LIKE.
5. CHỈ CÓ 2 BẢNG là households và members. Các tên như deprivation, reason, support, transition, children, policy LÀ TIỀN TỐ CỦA CỘT trong bảng households, KHÔNG PHẢI TÊN BẢNG! Khi dùng các cột này BẮT BUỘC phải bọc trong ngoặc kép (VD: "deprivation.healthInsurance" = true).

[CÂU HỎI CŨ]: {old_question}
[SQL CHUẨN CŨ]: {old_sql}

ĐỐI VỚI CÁC ĐỊA DANH CÓ DẤU NHÁY ĐƠN: Trong CSDL, các địa danh ĐÃ BỊ LOẠI BỎ dấu nháy đơn. Do đó, TUYỆT ĐỐI KHÔNG SỬ DỤNG dấu nháy đơn bên trong tên địa danh. Ví dụ: "Đắk N'Drót" PHẢI viết là "Đắk NDrót", "Đắk R'lấp" PHẢI viết là "Đắk RLấp". Đặc biệt với hàm ILIKE, hãy truyền vào '%NDrót%' hoặc '%RLấp%' (TUYỆT ĐỐI KHÔNG ghép từ Huyện/Xã liền trước như '%Huyện RLấp%'). Nếu hỏi toàn tỉnh Đắk Nông thì KHÔNG lọc theo district hay commune.

Hãy trả về DUY NHẤT câu lệnh SQL đã được chỉnh sửa cho Câu hỏi mới. Không giải thích, không kèm code block markdown (không dùng ```sql ... ```)."""

        raw_sql = call_llm(
            system_prompt=system_prompt,
            user_prompt=f"[CÂU HỎI MỚI]: {new_question}\n[SQL MỚI]:",
            temperature=0.0,
            max_tokens=1000,
            model="gpt-4o-mini"
        )
        
        sql = raw_sql.strip()
        if sql.startswith("```sql"): sql = sql[6:]
        if sql.startswith("```"): sql = sql[3:]
        if sql.endswith("```"): sql = sql[:-3]
        return sql.strip()
