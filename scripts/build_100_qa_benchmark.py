import json
import duckdb
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parents[1]
db_path = PROJECT_ROOT / "data/Processed/intern_chatbot.duckdb"
conn = duckdb.connect(str(db_path))

benchmark_suite = []

def add_test_case(test_id, category, sub_level, complexity, prompt, sql_queries, expected_df_count, desc):
    executed_results = []
    for sql in sql_queries:
        try:
            res = conn.execute(sql).fetchall()
            cols = [desc_item[0] for desc_item in conn.description]
            executed_results.append({
                "sql": sql,
                "columns": cols,
                "row_count": len(res),
                "sample_preview": [[str(c) for c in r] for r in res[:3]]
            })
        except Exception as e:
            print(f"[ERROR] Test ID {test_id} failed SQL:\n{sql}\nError: {e}")
            sys.exit(1)
            
    benchmark_suite.append({
        "test_id": test_id,
        "category": category,
        "granularity_level": sub_level,
        "complexity_level": complexity,
        "prompt": prompt,
        "sql_queries": sql_queries,
        "expected_dataframe_count": expected_df_count,
        "description": desc,
        "verification_status": "VERIFIED_PASSED",
        "executed_preview": executed_results
    })

print("Generating Category 1 (01-20)...")
add_test_case("TC_001", "C1_SIMPLE", "Tỉnh", "1_req_low_cond",
              "Tổng số hộ nghèo trên địa bàn toàn tỉnh Đắk Nông năm 2024 là bao nhiêu?",
              ["""SELECT COUNT(*) AS "Tổng số hộ nghèo" FROM households WHERE classify = 'Hộ nghèo' AND "administrative.year" = 2024;"""],
              1, "Thống kê tổng số hộ nghèo cấp tỉnh năm 2024.")
add_test_case("TC_002", "C1_SIMPLE", "Tỉnh", "1_req_low_cond",
              "Tổng số hộ cận nghèo tại tỉnh Đắk Nông trong năm 2024 là bao nhiêu hộ?",
              ["""SELECT COUNT(*) AS "Tổng số hộ cận nghèo" FROM households WHERE classify = 'Hộ cận nghèo' AND "administrative.year" = 2024;"""],
              1, "Thống kê tổng số hộ cận nghèo cấp tỉnh năm 2024.")
add_test_case("TC_003", "C1_SIMPLE", "Huyện", "1_req_low_cond",
              "Hãy cho biết số lượng hộ nghèo tại huyện Đắk Mil năm 2024.",
              ["""SELECT COUNT(*) AS "Số hộ nghèo" FROM households WHERE classify = 'Hộ nghèo' AND "administrative.district" ILIKE '%Đắk Mil%' AND "administrative.year" = 2024;"""],
              1, "Đếm số hộ nghèo huyện Đắk Mil.")
add_test_case("TC_004", "C1_SIMPLE", "Huyện", "1_req_low_cond",
              "Huyện Cư Jút có bao nhiêu hộ cận nghèo năm 2024?",
              ["""SELECT COUNT(*) AS "Số hộ cận nghèo" FROM households WHERE classify = 'Hộ cận nghèo' AND "administrative.district" ILIKE '%Cư Jút%' AND "administrative.year" = 2024;"""],
              1, "Đếm số hộ cận nghèo huyện Cư Jút.")
add_test_case("TC_005", "C1_SIMPLE", "Thành phố", "1_req_low_cond",
              "Thành phố Gia Nghĩa có tổng cộng bao nhiêu hộ nghèo và cận nghèo năm 2024?",
              ["""SELECT classify AS "Phân loại", COUNT(*) AS "Số lượng" FROM households WHERE classify IN ('Hộ nghèo', 'Hộ cận nghèo') AND "administrative.district" ILIKE '%Gia Nghĩa%' AND "administrative.year" = 2024 GROUP BY classify;"""],
              1, "Thống kê hộ nghèo và cận nghèo TP Gia Nghĩa.")
add_test_case("TC_006", "C1_SIMPLE", "Xã", "1_req_low_cond",
              "Xã Cư Knia (huyện Cư Jút) có bao nhiêu hộ nghèo năm 2024?",
              ["""SELECT COUNT(*) AS "Số hộ nghèo" FROM households WHERE classify = 'Hộ nghèo' AND "administrative.commune" ILIKE '%Cư Knia%' AND "administrative.year" = 2024;"""],
              1, "Số hộ nghèo xã Cư Knia.")
add_test_case("TC_007", "C1_SIMPLE", "Xã", "1_req_low_cond",
              "Thị trấn Đắk Mil có bao nhiêu hộ cận nghèo năm 2024?",
              ["""SELECT COUNT(*) AS "Số hộ cận nghèo" FROM households WHERE classify = 'Hộ cận nghèo' AND "administrative.commune" ILIKE '%Đắk Mil%' AND "administrative.year" = 2024;"""],
              1, "Số hộ cận nghèo Thị trấn Đắk Mil.")
add_test_case("TC_008", "C1_SIMPLE", "Tỉnh", "1_req_low_cond",
              "Có bao nhiêu thành viên thuộc hộ nghèo trên toàn tỉnh Đắk Nông năm 2024?",
              ["""SELECT COUNT(*) AS "Tổng số thành viên" FROM members m JOIN households h ON m."family.code" = h."family.code" AND m."administrative.year" = h."administrative.year" WHERE h.classify = 'Hộ nghèo' AND m."administrative.year" = 2024;"""],
              1, "Tổng số thành viên thuộc hộ nghèo cấp tỉnh.")
add_test_case("TC_009", "C1_SIMPLE", "Huyện", "1_req_low_cond",
              "Hãy liệt kê số lượng hộ nghèo theo từng xã tại huyện Krông Nô năm 2024.",
              ["""SELECT "administrative.commune" AS "Xã/Thị trấn", COUNT(*) AS "Số hộ nghèo" FROM households WHERE classify = 'Hộ nghèo' AND "administrative.district" ILIKE '%Krông Nô%' AND "administrative.year" = 2024 GROUP BY "administrative.commune" ORDER BY COUNT(*) DESC;"""],
              1, "Thống kê số hộ nghèo theo xã tại Krông Nô.")
add_test_case("TC_010", "C1_SIMPLE", "Huyện", "1_req_low_cond",
              "Thống kê số hộ cận nghèo theo xã tại huyện Tuy Đức năm 2024.",
              ["""SELECT "administrative.commune" AS "Xã/Thị trấn", COUNT(*) AS "Số hộ cận nghèo" FROM households WHERE classify = 'Hộ cận nghèo' AND "administrative.district" ILIKE '%Tuy Đức%' AND "administrative.year" = 2024 GROUP BY "administrative.commune" ORDER BY COUNT(*) DESC;"""],
              1, "Thống kê số hộ cận nghèo theo xã tại Tuy Đức.")
add_test_case("TC_011", "C1_SIMPLE", "Tỉnh", "1_req_low_cond",
              "Tổng số hộ DTTS thuộc diện hộ nghèo toàn tỉnh năm 2024 là bao nhiêu?",
              ["""SELECT COUNT(*) AS "Số hộ nghèo DTTS" FROM households WHERE classify = 'Hộ nghèo' AND "family.isDTTS" = TRUE AND "administrative.year" = 2024;"""],
              1, "Số hộ nghèo DTTS toàn tỉnh.")
add_test_case("TC_012", "C1_SIMPLE", "Huyện", "1_req_low_cond",
              "Huyện Đắk R'Lấp có bao nhiêu hộ nghèo là người đồng bào dân tộc thiểu số năm 2024?",
              ["""SELECT COUNT(*) AS "Số hộ nghèo DTTS" FROM households WHERE classify = 'Hộ nghèo' AND "family.isDTTS" = TRUE AND "administrative.district" ILIKE '%Đắk R''Lấp%' AND "administrative.year" = 2024;"""],
              1, "Số hộ nghèo DTTS huyện Đắk R'Lấp.")
add_test_case("TC_013", "C1_SIMPLE", "Tỉnh", "1_req_low_cond",
              "Thống kê số lượng hộ nghèo theo từng huyện/thành phố năm 2024.",
              ["""SELECT "administrative.district" AS "Huyện/Thành phố", COUNT(*) AS "Số hộ nghèo" FROM households WHERE classify = 'Hộ nghèo' AND "administrative.year" = 2024 GROUP BY "administrative.district" ORDER BY COUNT(*) DESC;"""],
              1, "Phân bố hộ nghèo cấp huyện.")
add_test_case("TC_014", "C1_SIMPLE", "Tỉnh", "1_req_low_cond",
              "Thống kê số lượng hộ cận nghèo theo từng huyện/thành phố năm 2024.",
              ["""SELECT "administrative.district" AS "Huyện/Thành phố", COUNT(*) AS "Số hộ cận nghèo" FROM households WHERE classify = 'Hộ cận nghèo' AND "administrative.year" = 2024 GROUP BY "administrative.district" ORDER BY COUNT(*) DESC;"""],
              1, "Phân bố hộ cận nghèo cấp huyện.")
add_test_case("TC_015", "C1_SIMPLE", "Xã", "1_req_low_cond",
              "Xã Quảng Sơn (huyện Đăk Glong) có bao nhiêu nhân khẩu thuộc hộ nghèo năm 2024?",
              ["""SELECT COUNT(*) AS "Số nhân khẩu" FROM members m JOIN households h ON m."family.code" = h."family.code" AND m."administrative.year" = h."administrative.year" WHERE h.classify = 'Hộ nghèo' AND h."administrative.commune" ILIKE '%Quảng Sơn%' AND h."administrative.year" = 2024;"""],
              1, "Số nhân khẩu hộ nghèo xã Quảng Sơn.")
add_test_case("TC_016", "C1_SIMPLE", "Huyện", "1_req_low_cond",
              "Tổng số hộ nghèo có chủ hộ là nữ tại huyện Đắk Song năm 2024?",
              ["""SELECT COUNT(*) AS "Số hộ chủ hộ nữ" FROM households WHERE classify = 'Hộ nghèo' AND "family.hostGender" ILIKE '%Nữ%' AND "administrative.district" ILIKE '%Đắk Song%' AND "administrative.year" = 2024;"""],
              1, "Số hộ nghèo chủ hộ nữ Đắk Song.")
add_test_case("TC_017", "C1_SIMPLE", "Tỉnh", "1_req_low_cond",
              "Tổng số trẻ em thuộc diện hộ nghèo toàn tỉnh Đắk Nông năm 2024 là bao nhiêu em?",
              ["""SELECT COUNT(*) AS "Số trẻ em" FROM members m JOIN households h ON m."family.code" = h."family.code" AND m."administrative.year" = h."administrative.year" WHERE h.classify = 'Hộ nghèo' AND m."member.isChild" = TRUE AND m."administrative.year" = 2024;"""],
              1, "Số trẻ em hộ nghèo toàn tỉnh.")
add_test_case("TC_018", "C1_SIMPLE", "Tỉnh", "1_req_low_cond",
              "Số lượng hộ nghèo thoát nghèo năm 2024 so với đầu năm 2024 là bao nhiêu hộ?",
              ["""SELECT COUNT(*) AS "Số hộ thoát nghèo" FROM households WHERE "transition.beginningClassify" = 'Nghèo' AND classify = 'Hộ không nghèo' AND "administrative.year" = 2024;"""],
              1, "Số hộ thoát nghèo trong năm.")
add_test_case("TC_019", "C1_SIMPLE", "Huyện", "1_req_low_cond",
              "Huyện Đắk Mil có bao nhiêu hộ cận nghèo thoát cận nghèo năm 2024?",
              ["""SELECT COUNT(*) AS "Số hộ thoát cận nghèo" FROM households WHERE "transition.beginningClassify" = 'Cận nghèo' AND classify = 'Hộ không nghèo' AND "administrative.district" ILIKE '%Đắk Mil%' AND "administrative.year" = 2024;"""],
              1, "Thoát cận nghèo Đắk Mil.")
add_test_case("TC_020", "C1_SIMPLE", "Xã", "1_req_low_cond",
              "Xã Đắk R'Tíh (Tuy Đức) có bao nhiêu hộ nghèo năm 2023?",
              ["""SELECT COUNT(*) AS "Số hộ nghèo" FROM households WHERE classify = 'Hộ nghèo' AND "administrative.commune" ILIKE '%Đắk R''Tíh%' AND "administrative.year" = 2023;"""],
              1, "Hộ nghèo Đắk R'Tíh năm 2023.")

print("Generating Category 2 (21-40)...")
add_test_case("TC_021", "C2_MULTI_COND", "Tỉnh", "2_req_mid_cond",
              "Tỷ lệ hộ cận nghèo có chủ hộ không có khả năng lao động tại huyện Đắk Song năm 2024 là bao nhiêu?",
              ["""SELECT ROUND(COUNT(CASE WHEN "family.hasNoLaborCapacity" = TRUE THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS "Tỷ lệ (%)" FROM households WHERE classify = 'Hộ cận nghèo' AND "administrative.district" ILIKE '%Đắk Song%' AND "administrative.year" = 2024;"""],
              1, "Tỷ lệ hộ cận nghèo không có khả năng lao động Đắk Song (chống Tautology).")
add_test_case("TC_022", "C2_MULTI_COND", "Huyện", "2_req_mid_cond",
              "Huyện Cư Jút có bao nhiêu hộ nghèo đồng bào dân tộc thiểu số bị thiếu hụt nhà ở năm 2024?",
              ["""SELECT COUNT(*) AS "Số hộ" FROM households WHERE classify = 'Hộ nghèo' AND "family.isDTTS" = TRUE AND "deprivation.housingQuality" = 1 AND "administrative.district" ILIKE '%Cư Jút%' AND "administrative.year" = 2024;"""],
              1, "Hộ nghèo DTTS thiếu hụt chất lượng nhà ở Cư Jút.")
add_test_case("TC_023", "C2_MULTI_COND", "Huyện", "2_req_mid_cond",
              "Thống kê số hộ nghèo bị thiếu hụt đồng thời cả nguồn nước sinh hoạt và nhà tiêu hợp vệ sinh tại huyện Krông Nô năm 2024.",
              ["""SELECT "administrative.commune" AS "Xã", COUNT(*) AS "Số hộ" FROM households WHERE classify = 'Hộ nghèo' AND "deprivation.cleanWater" = 1 AND "deprivation.hygienicToilet" = 1 AND "administrative.district" ILIKE '%Krông Nô%' AND "administrative.year" = 2024 GROUP BY "administrative.commune" ORDER BY COUNT(*) DESC;"""],
              1, "Thiếu hụt kép nước sinh hoạt và nhà tiêu tại Krông Nô.")
add_test_case("TC_024", "C2_MULTI_COND", "Tỉnh", "2_req_mid_cond",
              "Có bao nhiêu hộ nghèo trên toàn tỉnh Đắk Nông có từ 5 nhân khẩu trở lên trong năm 2024?",
              ["""SELECT COUNT(*) AS "Số hộ đông nhân khẩu" FROM households WHERE classify = 'Hộ nghèo' AND "family.numberOfMembers" >= 5 AND "administrative.year" = 2024;"""],
              1, "Hộ nghèo đông nhân khẩu toàn tỉnh.")
add_test_case("TC_025", "C2_MULTI_COND", "Huyện", "2_req_mid_cond",
              "Huyện Đăk Glong có bao nhiêu hộ nghèo do nguyên nhân không có đất sản xuất trong năm 2024?",
              ["""SELECT COUNT(*) AS "Số hộ" FROM households WHERE classify = 'Hộ nghèo' AND "reason.lackProductionLand" = TRUE AND "administrative.district" ILIKE '%Đăk Glong%' AND "administrative.year" = 2024;"""],
              1, "Nghèo do thiếu đất sản xuất tại Đăk Glong.")
add_test_case("TC_026", "C2_MULTI_COND", "Huyện", "2_req_mid_cond",
              "Số lượng hộ nghèo do thiếu vốn sản xuất kinh doanh theo từng xã ở huyện Tuy Đức năm 2024.",
              ["""SELECT "administrative.commune" AS "Xã", COUNT(*) AS "Số hộ" FROM households WHERE classify = 'Hộ nghèo' AND "reason.lackCapital" = TRUE AND "administrative.district" ILIKE '%Tuy Đức%' AND "administrative.year" = 2024 GROUP BY "administrative.commune" ORDER BY COUNT(*) DESC;"""],
              1, "Nghèo do thiếu vốn kinh doanh tại Tuy Đức.")
add_test_case("TC_027", "C2_MULTI_COND", "Tỉnh", "2_req_mid_cond",
              "Tỷ lệ hộ nghèo DTTS trên tổng số hộ nghèo của từng huyện năm 2024 là bao nhiêu?",
              ["""SELECT "administrative.district" AS "Huyện", COUNT(*) AS "Tổng hộ nghèo", SUM(CASE WHEN "family.isDTTS" = TRUE THEN 1 ELSE 0 END) AS "Hộ nghèo DTTS", ROUND(SUM(CASE WHEN "family.isDTTS" = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS "Tỷ lệ % DTTS" FROM households WHERE classify = 'Hộ nghèo' AND "administrative.year" = 2024 GROUP BY "administrative.district" ORDER BY "Tỷ lệ % DTTS" DESC;"""],
              1, "Tỷ lệ hộ nghèo DTTS theo huyện.")
add_test_case("TC_028", "C2_MULTI_COND", "Huyện", "2_req_mid_cond",
              "Huyện Đắk Mil có bao nhiêu hộ cận nghèo nhận được hỗ trợ bảo hiểm y tế năm 2024?",
              ["""SELECT COUNT(*) AS "Số hộ được hỗ trợ BHYT" FROM households WHERE classify = 'Hộ cận nghèo' AND "support.health" = TRUE AND "administrative.district" ILIKE '%Đắk Mil%' AND "administrative.year" = 2024;"""],
              1, "Hỗ trợ y tế cận nghèo Đắk Mil.")
add_test_case("TC_029", "C2_MULTI_COND", "Huyện", "2_req_mid_cond",
              "Số hộ nghèo được hỗ trợ nhà ở theo Chương trình mục tiêu quốc gia tại Đắk R'Lấp năm 2024?",
              ["""SELECT COUNT(*) AS "Số hộ" FROM households WHERE classify = 'Hộ nghèo' AND "support.housing" = TRUE AND "administrative.district" ILIKE '%Đắk R''Lấp%' AND "administrative.year" = 2024;"""],
              1, "Hỗ trợ nhà ở tại Đắk R'Lấp.")
add_test_case("TC_030", "C2_MULTI_COND", "Xã", "2_req_mid_cond",
              "Xã Đắk Som (Đăk Glong) có bao nhiêu hộ nghèo thiếu hụt việc làm năm 2024?",
              ["""SELECT COUNT(*) AS "Số hộ thiếu việc làm" FROM households WHERE classify = 'Hộ nghèo' AND "deprivation.employment" = 1 AND "administrative.commune" ILIKE '%Đắk Som%' AND "administrative.year" = 2024;"""],
              1, "Thiếu hụt việc làm tại xã Đắk Som.")
add_test_case("TC_031", "C2_MULTI_COND", "Tỉnh", "2_req_mid_cond",
              "Hãy so sánh tổng số điểm thiếu hụt trung bình (deprivation.totalCount) của hộ nghèo giữa các huyện năm 2024.",
              ["""SELECT "administrative.district" AS "Huyện", ROUND(AVG("deprivation.totalCount"), 2) AS "Điểm thiếu hụt TB" FROM households WHERE classify = 'Hộ nghèo' AND "administrative.year" = 2024 GROUP BY "administrative.district" ORDER BY "Điểm thiếu hụt TB" DESC;"""],
              1, "So sánh điểm thiếu hụt trung bình theo huyện.")
add_test_case("TC_032", "C2_MULTI_COND", "Huyện", "2_req_mid_cond",
              "Tại huyện Cư Jút, xã nào có tỷ lệ hộ nghèo bị thiếu hụt dịch vụ viễn thông cao nhất năm 2024?",
              ["""SELECT "administrative.commune" AS "Xã", COUNT(*) AS "Tổng hộ nghèo", SUM(CASE WHEN "deprivation.telecommunication" = 1 THEN 1 ELSE 0 END) AS "Hộ thiếu viễn thông", ROUND(SUM(CASE WHEN "deprivation.telecommunication" = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS "Tỷ lệ %" FROM households WHERE classify = 'Hộ nghèo' AND "administrative.district" ILIKE '%Cư Jút%' AND "administrative.year" = 2024 GROUP BY "administrative.commune" ORDER BY "Tỷ lệ %" DESC LIMIT 1;"""],
              1, "Xã có tỷ lệ thiếu viễn thông cao nhất Cư Jút.")
add_test_case("TC_033", "C2_MULTI_COND", "Huyện", "2_req_mid_cond",
              "Thống kê số hộ cận nghèo có người ốm đau nặng hoặc tai nạn rủi ro tại huyện Đắk Song năm 2024.",
              ["""SELECT COUNT(*) AS "Số hộ" FROM households WHERE classify = 'Hộ cận nghèo' AND "reason.illnessOrAccident" = TRUE AND "administrative.district" ILIKE '%Đắk Song%' AND "administrative.year" = 2024;"""],
              1, "Cận nghèo do ốm đau/tai nạn tại Đắk Song.")
add_test_case("TC_034", "C2_MULTI_COND", "Tỉnh", "2_req_mid_cond",
              "Có bao nhiêu hộ nghèo tại Đắk Nông vừa thiếu hụt diện tích nhà ở vừa thiếu hụt chất lượng nhà ở năm 2024?",
              ["""SELECT COUNT(*) AS "Số hộ thiếu hụt kép nhà ở" FROM households WHERE classify = 'Hộ nghèo' AND "deprivation.housingArea" = 1 AND "deprivation.housingQuality" = 1 AND "administrative.year" = 2024;"""],
              1, "Thiếu hụt kép về nhà ở toàn tỉnh.")
add_test_case("TC_035", "C2_MULTI_COND", "Thành phố", "2_req_mid_cond",
              "Thành phố Gia Nghĩa có bao nhiêu hộ nghèo do người lao động chính thiếu việc làm năm 2024?",
              ["""SELECT COUNT(*) AS "Số hộ" FROM households WHERE classify = 'Hộ nghèo' AND "reason.lackLabor" = TRUE AND "administrative.district" ILIKE '%Gia Nghĩa%' AND "administrative.year" = 2024;"""],
              1, "Nghèo do thiếu lao động tại Gia Nghĩa.")
add_test_case("TC_036", "C2_MULTI_COND", "Huyện", "2_req_mid_cond",
              "Huyện Đắk Mil có bao nhiêu hộ nghèo được hỗ trợ tín dụng ưu đãi trong năm 2024?",
              ["""SELECT COUNT(*) AS "Số hộ vay tín dụng" FROM households WHERE classify = 'Hộ nghèo' AND "support.credit" = TRUE AND "administrative.district" ILIKE '%Đắk Mil%' AND "administrative.year" = 2024;"""],
              1, "Hỗ trợ tín dụng hộ nghèo Đắk Mil.")
add_test_case("TC_037", "C2_MULTI_COND", "Huyện", "2_req_mid_cond",
              "Thống kê số lượng hộ nghèo có từ 2 chiều thiếu hụt trở lên theo từng xã tại huyện Krông Nô năm 2024.",
              ["""SELECT "administrative.commune" AS "Xã", COUNT(*) AS "Số hộ" FROM households WHERE classify = 'Hộ nghèo' AND "deprivation.totalCount" >= 2 AND "administrative.district" ILIKE '%Krông Nô%' AND "administrative.year" = 2024 GROUP BY "administrative.commune" ORDER BY COUNT(*) DESC;"""],
              1, "Hộ nghèo thiếu từ 2 chiều trở lên tại Krông Nô.")
add_test_case("TC_038", "C2_MULTI_COND", "Tỉnh", "2_req_mid_cond",
              "Tỷ lệ hộ nghèo được hỗ trợ miễn giảm học phí cho con em trên toàn tỉnh Đắk Nông năm 2024?",
              ["""SELECT ROUND(COUNT(CASE WHEN "support.education" = TRUE THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS "Tỷ lệ hỗ trợ giáo dục (%)" FROM households WHERE classify = 'Hộ nghèo' AND "administrative.year" = 2024;"""],
              1, "Tỷ lệ hỗ trợ giáo dục toàn tỉnh.")
add_test_case("TC_039", "C2_MULTI_COND", "Huyện", "2_req_mid_cond",
              "Huyện Đăk Glong có bao nhiêu hộ nghèo DTTS bị thiếu hụt trình độ học vấn người lớn năm 2024?",
              ["""SELECT COUNT(*) AS "Số hộ" FROM households WHERE classify = 'Hộ nghèo' AND "family.isDTTS" = TRUE AND "deprivation.adultEducation" = 1 AND "administrative.district" ILIKE '%Đăk Glong%' AND "administrative.year" = 2024;"""],
              1, "Hộ nghèo DTTS thiếu học vấn tại Đăk Glong.")
add_test_case("TC_040", "C2_MULTI_COND", "Huyện", "2_req_mid_cond",
              "Tại huyện Tuy Đức, tỷ lệ hộ cận nghèo bị thiếu thông tin tiếp cận phương tiện giải trí nghe nhìn năm 2024 là bao nhiêu?",
              ["""SELECT ROUND(COUNT(CASE WHEN "deprivation.informationAccessAssets" = 1 THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS "Tỷ lệ (%)" FROM households WHERE classify = 'Hộ cận nghèo' AND "administrative.district" ILIKE '%Tuy Đức%' AND "administrative.year" = 2024;"""],
              1, "Thiếu hụt phương tiện tiếp cận thông tin Tuy Đức.")

print("Generating Category 3 (41-60)...")
add_test_case("TC_041", "C3_MEMBER_LEVEL", "Tỉnh", "2_req_mid_cond",
              "Thống kê tổng số thành viên theo giới tính (Nam/Nữ) thuộc các hộ nghèo toàn tỉnh Đắk Nông năm 2024.",
              ["""SELECT m."member.gender" AS "Giới tính", COUNT(*) AS "Số lượng" FROM members m JOIN households h ON m."family.code" = h."family.code" AND m."administrative.year" = h."administrative.year" WHERE h.classify = 'Hộ nghèo' AND m."administrative.year" = 2024 GROUP BY m."member.gender";"""],
              1, "Phân bố nam/nữ thành viên hộ nghèo.")
add_test_case("TC_042", "C3_MEMBER_LEVEL", "Huyện", "2_req_mid_cond",
              "Huyện Đắk Mil có bao nhiêu thành viên thuộc diện trẻ em trong các hộ nghèo năm 2024?",
              ["""SELECT COUNT(*) AS "Số trẻ em" FROM members m JOIN households h ON m."family.code" = h."family.code" AND m."administrative.year" = h."administrative.year" WHERE h.classify = 'Hộ nghèo' AND m."member.isChild" = TRUE AND m."administrative.district" ILIKE '%Đắk Mil%' AND m."administrative.year" = 2024;"""],
              1, "Số trẻ em trong hộ nghèo Đắk Mil.")
add_test_case("TC_043", "C3_MEMBER_LEVEL", "Tỉnh", "2_req_mid_cond",
              "Có bao nhiêu thành viên thuộc hộ nghèo trên toàn tỉnh Đắk Nông chưa có Bảo hiểm y tế năm 2024?",
              ["""SELECT COUNT(*) AS "Số người không có BHYT" FROM members m JOIN households h ON m."family.code" = h."family.code" AND m."administrative.year" = h."administrative.year" WHERE h.classify = 'Hộ nghèo' AND (m."member.hasHealthInsurance" = FALSE OR m."member.hasHealthInsurance" IS NULL) AND m."administrative.year" = 2024;"""],
              1, "Thành viên hộ nghèo chưa có BHYT.")
add_test_case("TC_044", "C3_MEMBER_LEVEL", "Huyện", "2_req_mid_cond",
              "Tại huyện Đăk Glong, có bao nhiêu trẻ em thuộc hộ nghèo bị thiếu hụt dinh dưỡng năm 2024?",
              ["""SELECT COUNT(*) AS "Số trẻ em thiếu dinh dưỡng" FROM members m JOIN households h ON m."family.code" = h."family.code" AND m."administrative.year" = h."administrative.year" WHERE h.classify = 'Hộ nghèo' AND m."member.isChild" = TRUE AND m."member.nutritionDeprived" = TRUE AND m."administrative.district" ILIKE '%Đăk Glong%' AND m."administrative.year" = 2024;"""],
              1, "Trẻ em thiếu dinh dưỡng Đăk Glong.")
add_test_case("TC_045", "C3_MEMBER_LEVEL", "Huyện", "2_req_mid_cond",
              "Thống kê số lượng thành viên thuộc diện người cao tuổi (từ 60 tuổi trở lên) trong hộ nghèo tại huyện Cư Jút năm 2024.",
              ["""SELECT COUNT(*) AS "Người cao tuổi" FROM members m JOIN households h ON m."family.code" = h."family.code" AND m."administrative.year" = h."administrative.year" WHERE h.classify = 'Hộ nghèo' AND (2024 - m."member.birthYear") >= 60 AND m."administrative.district" ILIKE '%Cư Jút%' AND m."administrative.year" = 2024;"""],
              1, "Người cao tuổi trong hộ nghèo Cư Jút.")
add_test_case("TC_046", "C3_MEMBER_LEVEL", "Huyện", "2_req_mid_cond",
              "Huyện Krông Nô có bao nhiêu trẻ em trong hộ cận nghèo không đi học đúng độ tuổi năm 2024?",
              ["""SELECT COUNT(*) AS "Trẻ không đi học" FROM members m JOIN households h ON m."family.code" = h."family.code" AND m."administrative.year" = h."administrative.year" WHERE h.classify = 'Hộ cận nghèo' AND m."member.isChild" = TRUE AND m."member.schoolAttendanceDeprived" = TRUE AND m."administrative.district" ILIKE '%Krông Nô%' AND m."administrative.year" = 2024;"""],
              1, "Trẻ em cận nghèo không đi học Krông Nô.")
add_test_case("TC_047", "C3_MEMBER_LEVEL", "Tỉnh", "2_req_mid_cond",
              "Phân bố độ tuổi thành viên trong hộ nghèo toàn tỉnh năm 2024 theo nhóm: Dưới 16 tuổi, 16-60 tuổi, Trên 60 tuổi.",
              ["""SELECT CASE WHEN (2024 - "member.birthYear") < 16 THEN 'Dưới 16 tuổi' WHEN (2024 - "member.birthYear") <= 60 THEN 'Từ 16 đến 60 tuổi' ELSE 'Trên 60 tuổi' END AS "Nhóm tuổi", COUNT(*) AS "Số lượng" FROM members m JOIN households h ON m."family.code" = h."family.code" AND m."administrative.year" = h."administrative.year" WHERE h.classify = 'Hộ nghèo' AND m."administrative.year" = 2024 GROUP BY 1 ORDER BY 2 DESC;"""],
              1, "Phân bố cơ cấu tuổi thành viên hộ nghèo.")
add_test_case("TC_048", "C3_MEMBER_LEVEL", "Xã", "2_req_mid_cond",
              "Xã Quảng Hòa (Đăk Glong) có bao nhiêu thành viên là dân tộc Mông thuộc các hộ nghèo năm 2024?",
              ["""SELECT COUNT(*) AS "Số thành viên người Mông" FROM members m JOIN households h ON m."family.code" = h."family.code" AND m."administrative.year" = h."administrative.year" WHERE h.classify = 'Hộ nghèo' AND m."member.ethnicity" ILIKE '%Mông%' AND h."administrative.commune" ILIKE '%Quảng Hòa%' AND m."administrative.year" = 2024;"""],
              1, "Thành viên người Mông xã Quảng Hòa.")
add_test_case("TC_049", "C3_MEMBER_LEVEL", "Huyện", "2_req_mid_cond",
              "Tại huyện Tuy Đức, tỷ lệ thành viên trong hộ nghèo có BHYT năm 2024 đạt bao nhiêu phần trăm?",
              ["""SELECT ROUND(COUNT(CASE WHEN m."member.hasHealthInsurance" = TRUE THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS "Tỷ lệ có BHYT (%)" FROM members m JOIN households h ON m."family.code" = h."family.code" AND m."administrative.year" = h."administrative.year" WHERE h.classify = 'Hộ nghèo' AND m."administrative.district" ILIKE '%Tuy Đức%' AND m."administrative.year" = 2024;"""],
              1, "Tỷ lệ BHYT cấp thành viên tại Tuy Đức.")
add_test_case("TC_050", "C3_MEMBER_LEVEL", "Tỉnh", "2_req_mid_cond",
              "Thống kê số chủ hộ nghèo toàn tỉnh năm 2024 chia theo nhóm dân tộc thiểu số và dân tộc Kinh.",
              ["""SELECT CASE WHEN h."family.isDTTS" = TRUE THEN 'Dân tộc thiểu số' ELSE 'Dân tộc Kinh/Khác' END AS "Nhóm dân tộc", COUNT(*) AS "Số chủ hộ" FROM households h WHERE h.classify = 'Hộ nghèo' AND h."administrative.year" = 2024 GROUP BY 1;"""],
              1, "Chủ hộ nghèo theo nhóm dân tộc.")
add_test_case("TC_051", "C3_MEMBER_LEVEL", "Huyện", "2_req_mid_cond",
              "Huyện Đắk Song có bao nhiêu thành viên thuộc hộ cận nghèo trong độ tuổi lao động (16-60 tuổi) năm 2024?",
              ["""SELECT COUNT(*) AS "Lực lượng lao động" FROM members m JOIN households h ON m."family.code" = h."family.code" AND m."administrative.year" = h."administrative.year" WHERE h.classify = 'Hộ cận nghèo' AND (2024 - m."member.birthYear") BETWEEN 16 AND 60 AND m."administrative.district" ILIKE '%Đắk Song%' AND m."administrative.year" = 2024;"""],
              1, "Lực lượng lao động hộ cận nghèo Đắk Song.")
add_test_case("TC_052", "C3_MEMBER_LEVEL", "Thành phố", "2_req_mid_cond",
              "Thành phố Gia Nghĩa có bao nhiêu thành viên nữ thuộc hộ nghèo là chủ hộ năm 2024?",
              ["""SELECT COUNT(*) AS "Chủ hộ nữ" FROM members m JOIN households h ON m."family.code" = h."family.code" AND m."administrative.year" = h."administrative.year" WHERE h.classify = 'Hộ nghèo' AND m."member.isHost" = TRUE AND m."member.gender" ILIKE '%Nữ%' AND m."administrative.district" ILIKE '%Gia Nghĩa%' AND m."administrative.year" = 2024;"""],
              1, "Chủ hộ nữ tại TP Gia Nghĩa.")
add_test_case("TC_053", "C3_MEMBER_LEVEL", "Tỉnh", "2_req_mid_cond",
              "Top 5 xã có tổng số nhân khẩu thuộc hộ nghèo đông nhất toàn tỉnh năm 2024.",
              ["""SELECT h."administrative.commune" AS "Xã", COUNT(*) AS "Số nhân khẩu" FROM members m JOIN households h ON m."family.code" = h."family.code" AND m."administrative.year" = h."administrative.year" WHERE h.classify = 'Hộ nghèo' AND m."administrative.year" = 2024 GROUP BY h."administrative.commune" ORDER BY COUNT(*) DESC LIMIT 5;"""],
              1, "Top 5 xã đông nhân khẩu nghèo nhất.")
add_test_case("TC_054", "C3_MEMBER_LEVEL", "Huyện", "2_req_mid_cond",
              "Huyện Đắk R'Lấp có bao nhiêu hộ nghèo mà tất cả các trẻ em đều thiếu BHYT năm 2024?",
              ["""SELECT COUNT(*) AS "Số hộ" FROM households h WHERE h.classify = 'Hộ nghèo' AND h."children.lackHealthInsuranceCount" > 0 AND h."children.lackHealthInsuranceCount" = h."children.totalCount" AND h."administrative.district" ILIKE '%Đắk R''Lấp%' AND h."administrative.year" = 2024;"""],
              1, "Hộ nghèo có 100% trẻ em thiếu BHYT Đắk R'Lấp.")
add_test_case("TC_055", "C3_MEMBER_LEVEL", "Huyện", "2_req_mid_cond",
              "Thống kê số lượng thành viên theo quan hệ với chủ hộ trong hộ nghèo huyện Cư Jút năm 2024.",
              ["""SELECT m."member.relationshipToHost" AS "Quan hệ", COUNT(*) AS "Số lượng" FROM members m JOIN households h ON m."family.code" = h."family.code" AND m."administrative.year" = h."administrative.year" WHERE h.classify = 'Hộ nghèo' AND m."administrative.district" ILIKE '%Cư Jút%' AND m."administrative.year" = 2024 GROUP BY 1 ORDER BY 2 DESC;"""],
              1, "Quan hệ với chủ hộ trong hộ nghèo Cư Jút.")
add_test_case("TC_056", "C3_MEMBER_LEVEL", "Xã", "2_req_mid_cond",
              "Xã Nam Dong (Cư Jút) có bao nhiêu thành viên hộ nghèo sinh từ năm 2015 đến nay (dưới 10 tuổi) năm 2024?",
              ["""SELECT COUNT(*) AS "Trẻ dưới 10 tuổi" FROM members m JOIN households h ON m."family.code" = h."family.code" AND m."administrative.year" = h."administrative.year" WHERE h.classify = 'Hộ nghèo' AND m."member.birthYear" >= 2015 AND h."administrative.commune" ILIKE '%Nam Dong%' AND m."administrative.year" = 2024;"""],
              1, "Trẻ em dưới 10 tuổi xã Nam Dong.")
add_test_case("TC_057", "C3_MEMBER_LEVEL", "Tỉnh", "2_req_mid_cond",
              "So sánh tỷ lệ thành viên nữ trong diện hộ nghèo giữa các huyện năm 2024.",
              ["""SELECT h."administrative.district" AS "Huyện", COUNT(*) AS "Tổng thành viên", SUM(CASE WHEN m."member.gender" ILIKE '%Nữ%' THEN 1 ELSE 0 END) AS "Thành viên nữ", ROUND(SUM(CASE WHEN m."member.gender" ILIKE '%Nữ%' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS "Tỷ lệ nữ (%)" FROM members m JOIN households h ON m."family.code" = h."family.code" AND m."administrative.year" = h."administrative.year" WHERE h.classify = 'Hộ nghèo' AND m."administrative.year" = 2024 GROUP BY h."administrative.district" ORDER BY "Tỷ lệ nữ (%)" DESC;"""],
              1, "So sánh tỷ lệ nữ thành viên theo huyện.")
add_test_case("TC_058", "C3_MEMBER_LEVEL", "Huyện", "2_req_mid_cond",
              "Huyện Đắk Mil có bao nhiêu hộ cận nghèo có duy nhất 1 nhân khẩu (hộ đơn thân) năm 2024?",
              ["""SELECT COUNT(*) AS "Hộ đơn thân" FROM households WHERE classify = 'Hộ cận nghèo' AND "family.numberOfMembers" = 1 AND "administrative.district" ILIKE '%Đắk Mil%' AND "administrative.year" = 2024;"""],
              1, "Hộ cận nghèo đơn thân tại Đắk Mil.")
add_test_case("TC_059", "C3_MEMBER_LEVEL", "Huyện", "2_req_mid_cond",
              "Tại huyện Krông Nô, có bao nhiêu thành viên là người M'Nông thuộc diện hộ nghèo năm 2024?",
              ["""SELECT COUNT(*) AS "Thành viên người M'Nông" FROM members m JOIN households h ON m."family.code" = h."family.code" AND m."administrative.year" = h."administrative.year" WHERE h.classify = 'Hộ nghèo' AND m."member.ethnicity" ILIKE '%Nông%' AND m."administrative.district" ILIKE '%Krông Nô%' AND m."administrative.year" = 2024;"""],
              1, "Thành viên người M'Nông tại Krông Nô.")
add_test_case("TC_060", "C3_MEMBER_LEVEL", "Tỉnh", "2_req_mid_cond",
              "Có bao nhiêu thành viên thuộc diện nghèo thoát nghèo (thuộc hộ chuyển từ nghèo sang không nghèo) trong năm 2024?",
              ["""SELECT COUNT(*) AS "Số nhân khẩu thoát nghèo" FROM members m JOIN households h ON m."family.code" = h."family.code" AND m."administrative.year" = h."administrative.year" WHERE h."transition.beginningClassify" = 'Nghèo' AND h.classify = 'Hộ không nghèo' AND m."administrative.year" = 2024;"""],
              1, "Số nhân khẩu thoát nghèo năm 2024.")

print("Generating Category 4 (61-80)...")
add_test_case("TC_061", "C4_MULTI_REQ", "Huyện", "3_req_high_cond",
              "Hãy thống kê tổng số hộ nghèo tại Đắk Mil năm 2024, tính tỷ lệ hộ nghèo là người DTTS tại huyện này, và cho biết xã nào ở Đắk Mil có số hộ nghèo đông nhất.",
              [
                  """SELECT COUNT(*) AS "Tổng số hộ nghèo Đắk Mil", ROUND(COUNT(CASE WHEN "family.isDTTS" = TRUE THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS "Tỷ lệ DTTS (%)" FROM households WHERE classify = 'Hộ nghèo' AND "administrative.district" ILIKE '%Đắk Mil%' AND "administrative.year" = 2024;""",
                  """SELECT "administrative.commune" AS "Xã đông hộ nghèo nhất", COUNT(*) AS "Số hộ" FROM households WHERE classify = 'Hộ nghèo' AND "administrative.district" ILIKE '%Đắk Mil%' AND "administrative.year" = 2024 GROUP BY 1 ORDER BY 2 DESC LIMIT 1;"""
              ],
              2, "Thống kê tổng số, tỷ lệ DTTS và top xã Đắk Mil (2 DataFrames).")
add_test_case("TC_062", "C4_MULTI_REQ", "Tỉnh", "3_req_high_cond",
              "Hãy cho biết tổng số hộ nghèo và cận nghèo toàn tỉnh năm 2024, tính điểm thiếu hụt trung bình của từng diện, và so sánh tỷ lệ hỗ trợ bảo hiểm y tế giữa hai nhóm này.",
              ["""SELECT classify AS "Diện hộ", COUNT(*) AS "Số lượng", ROUND(AVG("deprivation.totalCount"), 2) AS "Điểm thiếu hụt TB", ROUND(COUNT(CASE WHEN "support.health" = TRUE THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS "Tỷ lệ hỗ trợ BHYT (%)" FROM households WHERE classify IN ('Hộ nghèo', 'Hộ cận nghèo') AND "administrative.year" = 2024 GROUP BY classify;"""],
              1, "Thống kê tổng hợp đa chỉ tiêu hộ nghèo và cận nghèo toàn tỉnh.")
add_test_case("TC_063", "C4_MULTI_REQ", "Huyện", "4_req_high_cond",
              "Tại huyện Cư Jút năm 2024: 1) Có bao nhiêu hộ nghèo? 2) Bao nhiêu hộ thiếu đất sản xuất? 3) Bao nhiêu hộ thiếu vốn? 4) Xã nào có số hộ nghèo DTTS cao nhất?",
              [
                  """SELECT COUNT(*) AS "Tổng hộ nghèo", COUNT(CASE WHEN "reason.lackProductionLand" = TRUE THEN 1 END) AS "Thiếu đất", COUNT(CASE WHEN "reason.lackCapital" = TRUE THEN 1 END) AS "Thiếu vốn" FROM households WHERE classify = 'Hộ nghèo' AND "administrative.district" ILIKE '%Cư Jút%' AND "administrative.year" = 2024;""",
                  """SELECT "administrative.commune" AS "Xã đông hộ nghèo DTTS nhất", COUNT(*) AS "Số hộ" FROM households WHERE classify = 'Hộ nghèo' AND "family.isDTTS" = TRUE AND "administrative.district" ILIKE '%Cư Jút%' AND "administrative.year" = 2024 GROUP BY 1 ORDER BY 2 DESC LIMIT 1;"""
              ],
              2, "4 câu hỏi con về hộ nghèo Cư Jút.")
add_test_case("TC_064", "C4_MULTI_REQ", "Huyện", "3_req_high_cond",
              "Huyện Đăk Glong năm 2024: Hãy đếm số hộ cận nghèo, tính tỷ lệ hộ cận nghèo có chủ hộ không có khả năng lao động, và liệt kê 3 xã có số hộ cận nghèo nhiều nhất.",
              [
                  """SELECT COUNT(*) AS "Tổng số hộ cận nghèo", ROUND(COUNT(CASE WHEN "family.hasNoLaborCapacity" = TRUE THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS "Tỷ lệ không KNLĐ (%)" FROM households WHERE classify = 'Hộ cận nghèo' AND "administrative.district" ILIKE '%Đăk Glong%' AND "administrative.year" = 2024;""",
                  """SELECT "administrative.commune" AS "Xã", COUNT(*) AS "Số hộ cận nghèo" FROM households WHERE classify = 'Hộ cận nghèo' AND "administrative.district" ILIKE '%Đăk Glong%' AND "administrative.year" = 2024 GROUP BY 1 ORDER BY 2 DESC LIMIT 3;"""
              ],
              2, "Thống kê cận nghèo, tỷ lệ lao động và Top 3 xã Đăk Glong.")
add_test_case("TC_065", "C4_MULTI_REQ", "Tỉnh", "3_req_high_cond",
              "Toàn tỉnh năm 2024: Huyện nào có nhiều hộ nghèo nhất? Huyện nào có ít hộ nghèo nhất? Tỷ lệ hộ nghèo DTTS của huyện nhiều nhất là bao nhiêu?",
              [
                  """SELECT "administrative.district" AS "Huyện đông nghèo nhất", COUNT(*) AS "Số hộ", ROUND(COUNT(CASE WHEN "family.isDTTS" = TRUE THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS "Tỷ lệ DTTS (%)" FROM households WHERE classify = 'Hộ nghèo' AND "administrative.year" = 2024 GROUP BY 1 ORDER BY 2 DESC LIMIT 1;""",
                  """SELECT "administrative.district" AS "Huyện ít nghèo nhất", COUNT(*) AS "Số hộ" FROM households WHERE classify = 'Hộ nghèo' AND "administrative.year" = 2024 GROUP BY 1 ORDER BY 2 ASC LIMIT 1;"""
              ],
              2, "Huyện cao nhất, thấp nhất và tỷ lệ DTTS.")
add_test_case("TC_066", "C4_MULTI_REQ", "Huyện", "3_req_high_cond",
              "Huyện Krông Nô năm 2024: Cho biết tổng số nhân khẩu trong hộ nghèo, số trẻ em dưới 16 tuổi trong hộ nghèo, và tỷ lệ trẻ em được cấp BHYT.",
              ["""SELECT COUNT(*) AS "Tổng nhân khẩu nghèo", COUNT(CASE WHEN (2024 - m."member.birthYear") < 16 THEN 1 END) AS "Trẻ dưới 16 tuổi", ROUND(COUNT(CASE WHEN (2024 - m."member.birthYear") < 16 AND m."member.hasHealthInsurance" = TRUE THEN 1 END) * 100.0 / NULLIF(COUNT(CASE WHEN (2024 - m."member.birthYear") < 16 THEN 1 END), 0), 2) AS "Tỷ lệ trẻ có BHYT (%)" FROM members m JOIN households h ON m."family.code" = h."family.code" AND m."administrative.year" = h."administrative.year" WHERE h.classify = 'Hộ nghèo' AND m."administrative.district" ILIKE '%Krông Nô%' AND m."administrative.year" = 2024;"""],
              1, "3 yêu cầu nhân khẩu, trẻ em và BHYT tại Krông Nô.")
add_test_case("TC_067", "C4_MULTI_REQ", "Huyện", "3_req_high_cond",
              "Thống kê tại Đắk Song năm 2024: Số hộ nghèo, số hộ nghèo thoát nghèo so với năm trước, và xã có số lượng hộ thoát nghèo cao nhất.",
              [
                  """SELECT COUNT(*) AS "Số hộ nghèo hiện tại", COUNT(CASE WHEN "transition.beginningClassify" = 'Nghèo' AND classify = 'Hộ không nghèo' THEN 1 END) AS "Số hộ thoát nghèo" FROM households WHERE "administrative.district" ILIKE '%Đắk Song%' AND "administrative.year" = 2024;""",
                  """SELECT "administrative.commune" AS "Xã thoát nghèo nhiều nhất", COUNT(*) AS "Số hộ thoát nghèo" FROM households WHERE "transition.beginningClassify" = 'Nghèo' AND classify = 'Hộ không nghèo' AND "administrative.district" ILIKE '%Đắk Song%' AND "administrative.year" = 2024 GROUP BY 1 ORDER BY 2 DESC LIMIT 1;"""
              ],
              2, "Thống kê giảm nghèo tại huyện Đắk Song.")
add_test_case("TC_068", "C4_MULTI_REQ", "Thành phố", "3_req_high_cond",
              "TP Gia Nghĩa 2024: Thống kê số hộ nghèo theo từng phường/xã, cho biết phường nào có tỷ lệ hộ nghèo được hỗ trợ nhà ở cao nhất, và tính tổng số trẻ em thuộc diện hộ nghèo toàn TP.",
              [
                  """SELECT "administrative.commune" AS "Phường/Xã", COUNT(*) AS "Số hộ nghèo", ROUND(COUNT(CASE WHEN "support.housing" = TRUE THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS "Tỷ lệ hỗ trợ nhà ở (%)" FROM households WHERE classify = 'Hộ nghèo' AND "administrative.district" ILIKE '%Gia Nghĩa%' AND "administrative.year" = 2024 GROUP BY 1 ORDER BY 2 DESC;""",
                  """SELECT COUNT(*) AS "Tổng số trẻ em hộ nghèo TP" FROM members m JOIN households h ON m."family.code" = h."family.code" AND m."administrative.year" = h."administrative.year" WHERE h.classify = 'Hộ nghèo' AND m."member.isChild" = TRUE AND m."administrative.district" ILIKE '%Gia Nghĩa%' AND m."administrative.year" = 2024;"""
              ],
              2, "Thống kê đa chiều cấp phường/xã TP Gia Nghĩa.")
add_test_case("TC_069", "C4_MULTI_REQ", "Huyện", "3_req_high_cond",
              "Tại Tuy Đức năm 2024: Hãy tính tổng số hộ cận nghèo, liệt kê 3 nguyên nhân nghèo/cận nghèo phổ biến nhất tại huyện, và số lượng thành viên cận nghèo thiếu BHYT.",
              [
                  """SELECT COUNT(*) AS "Tổng số hộ cận nghèo" FROM households WHERE classify = 'Hộ cận nghèo' AND "administrative.district" ILIKE '%Tuy Đức%' AND "administrative.year" = 2024;""",
                  """SELECT 'Thiếu vốn' AS "Nguyên nhân", COUNT(CASE WHEN "reason.lackCapital"=TRUE THEN 1 END) AS "Số hộ" FROM households WHERE classify IN ('Hộ nghèo','Hộ cận nghèo') AND "administrative.district" ILIKE '%Tuy Đức%' AND "administrative.year"=2024 UNION ALL SELECT 'Thiếu đất sản xuất', COUNT(CASE WHEN "reason.lackProductionLand"=TRUE THEN 1 END) FROM households WHERE classify IN ('Hộ nghèo','Hộ cận nghèo') AND "administrative.district" ILIKE '%Tuy Đức%' AND "administrative.year"=2024 UNION ALL SELECT 'Thiếu lao động', COUNT(CASE WHEN "reason.lackLabor"=TRUE THEN 1 END) FROM households WHERE classify IN ('Hộ nghèo','Hộ cận nghèo') AND "administrative.district" ILIKE '%Tuy Đức%' AND "administrative.year"=2024 ORDER BY 2 DESC;""",
                  """SELECT COUNT(*) AS "Thành viên cận nghèo thiếu BHYT" FROM members m JOIN households h ON m."family.code"=h."family.code" AND m."administrative.year"=h."administrative.year" WHERE h.classify='Hộ cận nghèo' AND (m."member.hasHealthInsurance"=FALSE OR m."member.hasHealthInsurance" IS NULL) AND m."administrative.district" ILIKE '%Tuy Đức%' AND m."administrative.year"=2024;"""
              ],
              3, "3 DataFrames thống kê cận nghèo Tuy Đức.")
add_test_case("TC_070", "C4_MULTI_REQ", "Tỉnh", "3_req_high_cond",
              "Toàn tỉnh 2024: Thống kê tổng số hộ nghèo có chủ hộ là nữ, tỷ lệ hộ nghèo chủ hộ nữ được hỗ trợ tín dụng, và so sánh điểm thiếu hụt trung bình giữa chủ hộ nam và nữ.",
              ["""SELECT CASE WHEN "family.hostGender" ILIKE '%Nữ%' THEN 'Chủ hộ Nữ' ELSE 'Chủ hộ Nam' END AS "Giới tính chủ hộ", COUNT(*) AS "Số hộ nghèo", ROUND(COUNT(CASE WHEN "support.credit" = TRUE THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS "Tỷ lệ vay tín dụng (%)", ROUND(AVG("deprivation.totalCount"), 2) AS "Điểm thiếu hụt TB" FROM households WHERE classify = 'Hộ nghèo' AND "administrative.year" = 2024 GROUP BY 1;"""],
              1, "So sánh giới tính chủ hộ nghèo toàn tỉnh.")
add_test_case("TC_071", "C4_MULTI_REQ", "Huyện", "3_req_high_cond",
              "Huyện Đắk R'Lấp 2024: Số lượng hộ nghèo, số hộ thiếu hụt nước sạch, và tỷ lệ thành viên trong hộ nghèo bị thiếu dinh dưỡng.",
              [
                  """SELECT COUNT(*) AS "Số hộ nghèo", COUNT(CASE WHEN "deprivation.cleanWater" = 1 THEN 1 END) AS "Số hộ thiếu nước sạch" FROM households WHERE classify = 'Hộ nghèo' AND "administrative.district" ILIKE '%Đắk R''Lấp%' AND "administrative.year" = 2024;""",
                  """SELECT ROUND(COUNT(CASE WHEN m."member.nutritionDeprived" = TRUE THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS "Tỷ lệ thành viên thiếu dinh dưỡng (%)" FROM members m JOIN households h ON m."family.code"=h."family.code" AND m."administrative.year"=h."administrative.year" WHERE h.classify='Hộ nghèo' AND m."administrative.district" ILIKE '%Đắk R''Lấp%' AND m."administrative.year"=2024;"""
              ],
              2, "Đắk R'Lấp nước sạch và dinh dưỡng.")
add_test_case("TC_072", "C4_MULTI_REQ", "Xã", "3_req_high_cond",
              "Xã Quảng Sơn (Đăk Glong) 2024: Có bao nhiêu hộ nghèo, bao nhiêu hộ cận nghèo, và tổng số trẻ em không đi học/thiếu học vấn trong các hộ này?",
              [
                  """SELECT classify AS "Phân loại", COUNT(*) AS "Số hộ" FROM households WHERE classify IN ('Hộ nghèo', 'Hộ cận nghèo') AND "administrative.commune" ILIKE '%Quảng Sơn%' AND "administrative.year" = 2024 GROUP BY 1;""",
                  """SELECT COUNT(*) AS "Tổng số trẻ em", COUNT(CASE WHEN m."member.schoolAttendanceDeprived" = TRUE THEN 1 END) AS "Trẻ thiếu học vấn/bỏ học" FROM members m JOIN households h ON m."family.code"=h."family.code" AND m."administrative.year"=h."administrative.year" WHERE h.classify IN ('Hộ nghèo', 'Hộ cận nghèo') AND m."member.isChild" = TRUE AND h."administrative.commune" ILIKE '%Quảng Sơn%' AND m."administrative.year" = 2024;"""
              ],
              2, "Thống kê hộ và giáo dục trẻ em tại Quảng Sơn.")
add_test_case("TC_073", "C4_MULTI_REQ", "Tỉnh", "3_req_high_cond",
              "Năm 2024 toàn tỉnh: Huyện nào có tỷ lệ hộ nghèo DTTS cao nhất? Huyện nào có tỷ lệ hỗ trợ nhà ở cho hộ nghèo thấp nhất? Và tổng số hộ nghèo toàn tỉnh là bao nhiêu?",
              [
                  """SELECT "administrative.district" AS "Huyện", ROUND(COUNT(CASE WHEN "family.isDTTS"=TRUE THEN 1 END)*100.0/NULLIF(COUNT(*),0),2) AS "Tỷ lệ DTTS (%)" FROM households WHERE classify='Hộ nghèo' AND "administrative.year"=2024 GROUP BY 1 ORDER BY 2 DESC LIMIT 1;""",
                  """SELECT "administrative.district" AS "Huyện", ROUND(COUNT(CASE WHEN "support.housing"=TRUE THEN 1 END)*100.0/NULLIF(COUNT(*),0),2) AS "Tỷ lệ hỗ trợ nhà ở (%)" FROM households WHERE classify='Hộ nghèo' AND "administrative.year"=2024 GROUP BY 1 ORDER BY 2 ASC LIMIT 1;""",
                  """SELECT COUNT(*) AS "Tổng hộ nghèo toàn tỉnh" FROM households WHERE classify='Hộ nghèo' AND "administrative.year"=2024;"""
              ],
              3, "3 truy vấn trả lời 3 câu hỏi đỉnh và đáy toàn tỉnh.")
add_test_case("TC_074", "C4_MULTI_REQ", "Huyện", "3_req_high_cond",
              "Tại Cư Jút 2024: Thống kê số hộ nghèo theo từng xã, xã có điểm thiếu hụt cao nhất, và số hộ nhận hỗ trợ y tế toàn huyện.",
              [
                  """SELECT "administrative.commune" AS "Xã", COUNT(*) AS "Số hộ nghèo", ROUND(AVG("deprivation.totalCount"),2) AS "Điểm thiếu hụt TB" FROM households WHERE classify='Hộ nghèo' AND "administrative.district" ILIKE '%Cư Jút%' AND "administrative.year"=2024 GROUP BY 1 ORDER BY 2 DESC;""",
                  """SELECT COUNT(*) AS "Hộ nghèo hỗ trợ y tế" FROM households WHERE classify='Hộ nghèo' AND "support.health"=TRUE AND "administrative.district" ILIKE '%Cư Jút%' AND "administrative.year"=2024;"""
              ],
              2, "Thống kê xã và hỗ trợ y tế Cư Jút.")
add_test_case("TC_075", "C4_MULTI_REQ", "Huyện", "3_req_high_cond",
              "Huyện Đắk Mil 2024: Đếm số lượng hộ nghèo, số hộ cận nghèo, số hộ nghèo thoát nghèo và tỷ lệ hộ nghèo được hỗ trợ y tế.",
              ["""SELECT COUNT(CASE WHEN classify='Hộ nghèo' THEN 1 END) AS "Hộ nghèo", COUNT(CASE WHEN classify='Hộ cận nghèo' THEN 1 END) AS "Hộ cận nghèo", COUNT(CASE WHEN "transition.beginningClassify"='Nghèo' AND classify='Hộ không nghèo' THEN 1 END) AS "Thoát nghèo", ROUND(COUNT(CASE WHEN classify='Hộ nghèo' AND "support.health"=TRUE THEN 1 END)*100.0/NULLIF(COUNT(CASE WHEN classify='Hộ nghèo' THEN 1 END),0),2) AS "Tỷ lệ hỗ trợ y tế hộ nghèo (%)" FROM households WHERE "administrative.district" ILIKE '%Đắk Mil%' AND "administrative.year"=2024;"""],
              1, "4 chỉ tiêu tổng hợp trong 1 câu SQL tại Đắk Mil.")
add_test_case("TC_076", "C4_MULTI_REQ", "Tỉnh", "3_req_high_cond",
              "Toàn tỉnh 2024: Thống kê số lượng hộ nghèo theo 3 nhóm kích thước hộ: Hộ 1-2 người, Hộ 3-4 người, Hộ từ 5 người trở lên, và điểm thiếu hụt TB của mỗi nhóm.",
              ["""SELECT CASE WHEN "family.numberOfMembers" <= 2 THEN '1-2 người' WHEN "family.numberOfMembers" <= 4 THEN '3-4 người' ELSE '5 người trở lên' END AS "Quy mô hộ", COUNT(*) AS "Số hộ", ROUND(AVG("deprivation.totalCount"),2) AS "Điểm thiếu hụt TB" FROM households WHERE classify='Hộ nghèo' AND "administrative.year"=2024 GROUP BY 1 ORDER BY 2 DESC;"""],
              1, "Phân tích hộ nghèo theo quy mô nhân khẩu.")
add_test_case("TC_077", "C4_MULTI_REQ", "Huyện", "3_req_high_cond",
              "Huyện Krông Nô 2024: Thống kê số lượng hộ nghèo DTTS theo từng xã, chỉ ra xã có tỷ lệ hộ nghèo DTTS cao nhất và tính tổng số trẻ em DTTS thuộc diện nghèo của huyện.",
              [
                  """SELECT "administrative.commune" AS "Xã", COUNT(*) AS "Tổng hộ nghèo", COUNT(CASE WHEN "family.isDTTS"=TRUE THEN 1 END) AS "Hộ nghèo DTTS", ROUND(COUNT(CASE WHEN "family.isDTTS"=TRUE THEN 1 END)*100.0/NULLIF(COUNT(*),0),2) AS "Tỷ lệ DTTS (%)" FROM households WHERE classify='Hộ nghèo' AND "administrative.district" ILIKE '%Krông Nô%' AND "administrative.year"=2024 GROUP BY 1 ORDER BY "Tỷ lệ DTTS (%)" DESC;""",
                  """SELECT COUNT(*) AS "Trẻ em nghèo DTTS Krông Nô" FROM members m JOIN households h ON m."family.code"=h."family.code" AND m."administrative.year"=h."administrative.year" WHERE h.classify='Hộ nghèo' AND h."family.isDTTS"=TRUE AND m."member.isChild"=TRUE AND m."administrative.district" ILIKE '%Krông Nô%' AND m."administrative.year"=2024;"""
              ],
              2, "Phân tích chuyên sâu DTTS tại Krông Nô.")
add_test_case("TC_078", "C4_MULTI_REQ", "Huyện", "3_req_high_cond",
              "Đắk Song 2024: Cho biết số hộ nghèo, số hộ nghèo có chủ hộ trên 60 tuổi và số hộ nghèo bị thiếu hụt nhà tiêu hợp vệ sinh.",
              ["""SELECT COUNT(*) AS "Tổng hộ nghèo", COUNT(CASE WHEN (2024 - "family.hostBirthYear") >= 60 THEN 1 END) AS "Chủ hộ trên 60 tuổi", COUNT(CASE WHEN "deprivation.hygienicToilet"=1 THEN 1 END) AS "Thiếu nhà tiêu" FROM households WHERE classify='Hộ nghèo' AND "administrative.district" ILIKE '%Đắk Song%' AND "administrative.year"=2024;"""],
              1, "Thống kê người già và vệ sinh tại Đắk Song.")
add_test_case("TC_079", "C4_MULTI_REQ", "Tỉnh", "3_req_high_cond",
              "Toàn tỉnh 2024: Cho biết tổng số hộ nghèo do không có đất sản xuất, phân bố theo huyện, và huyện có số hộ nghèo lý do này cao nhất.",
              ["""SELECT "administrative.district" AS "Huyện", COUNT(*) AS "Hộ nghèo thiếu đất sản xuất" FROM households WHERE classify='Hộ nghèo' AND "reason.lackProductionLand"=TRUE AND "administrative.year"=2024 GROUP BY 1 ORDER BY 2 DESC;"""],
              1, "Phân bố nguyên nhân thiếu đất sản xuất toàn tỉnh.")
add_test_case("TC_080", "C4_MULTI_REQ", "Xã", "3_req_high_cond",
              "Xã Quảng Khê (Đăk Glong) 2024: Có bao nhiêu hộ nghèo? Bao nhiêu hộ DTTS? Tỷ lệ thành viên có BHYT là bao nhiêu?",
              [
                  """SELECT COUNT(*) AS "Hộ nghèo", COUNT(CASE WHEN "family.isDTTS"=TRUE THEN 1 END) AS "Hộ nghèo DTTS" FROM households WHERE classify='Hộ nghèo' AND "administrative.commune" ILIKE '%Quảng Khê%' AND "administrative.year"=2024;""",
                  """SELECT ROUND(COUNT(CASE WHEN m."member.hasHealthInsurance"=TRUE THEN 1 END)*100.0/NULLIF(COUNT(*),0),2) AS "Tỷ lệ BHYT thành viên (%)" FROM members m JOIN households h ON m."family.code"=h."family.code" AND m."administrative.year"=h."administrative.year" WHERE h.classify='Hộ nghèo' AND h."administrative.commune" ILIKE '%Quảng Khê%' AND m."administrative.year"=2024;"""
              ],
              2, "Thống kê hộ và BHYT tại Quảng Khê.")

print("Generating Category 5 (81-100)...")
add_test_case("TC_081", "C5_MULTI_DF", "Tỉnh", "multi_df_exec",
              "Xuất báo cáo tổng thể hộ nghèo toàn tỉnh 2024: Bảng 1 thống kê số hộ và tỷ lệ DTTS theo huyện; Bảng 2 thống kê top 4 nguyên nhân nghèo phổ biến nhất toàn tỉnh.",
              [
                  """SELECT "administrative.district" AS "Huyện", COUNT(*) AS "Số hộ nghèo", ROUND(COUNT(CASE WHEN "family.isDTTS"=TRUE THEN 1 END)*100.0/NULLIF(COUNT(*),0),2) AS "Tỷ lệ DTTS (%)" FROM households WHERE classify='Hộ nghèo' AND "administrative.year"=2024 GROUP BY 1 ORDER BY 2 DESC;""",
                  """SELECT 'Thiếu vốn' AS "Nguyên nhân", COUNT(CASE WHEN "reason.lackCapital"=TRUE THEN 1 END) AS "Số hộ" FROM households WHERE classify='Hộ nghèo' AND "administrative.year"=2024 UNION ALL SELECT 'Thiếu đất sản xuất', COUNT(CASE WHEN "reason.lackProductionLand"=TRUE THEN 1 END) FROM households WHERE classify='Hộ nghèo' AND "administrative.year"=2024 UNION ALL SELECT 'Thiếu lao động', COUNT(CASE WHEN "reason.lackLabor"=TRUE THEN 1 END) FROM households WHERE classify='Hộ nghèo' AND "administrative.year"=2024 UNION ALL SELECT 'Ốm đau nặng', COUNT(CASE WHEN "reason.illnessOrAccident"=TRUE THEN 1 END) FROM households WHERE classify='Hộ nghèo' AND "administrative.year"=2024 ORDER BY 2 DESC;"""
              ],
              2, "Báo cáo tổng thể 2 DataFrames cấp tỉnh.")
add_test_case("TC_082", "C5_MULTI_DF", "Huyện", "multi_df_exec",
              "Đánh giá huyện Cư Jút 2024 qua 3 bảng: Bảng 1: Phân bố hộ nghèo theo xã; Bảng 2: Tình trạng hỗ trợ nhà ở, y tế, giáo dục; Bảng 3: Cơ cấu thành viên theo độ tuổi.",
              [
                  """SELECT "administrative.commune" AS "Xã", COUNT(*) AS "Số hộ nghèo" FROM households WHERE classify='Hộ nghèo' AND "administrative.district" ILIKE '%Cư Jút%' AND "administrative.year"=2024 GROUP BY 1 ORDER BY 2 DESC;""",
                  """SELECT COUNT(CASE WHEN "support.housing"=TRUE THEN 1 END) AS "Hỗ trợ nhà ở", COUNT(CASE WHEN "support.health"=TRUE THEN 1 END) AS "Hỗ trợ y tế", COUNT(CASE WHEN "support.education"=TRUE THEN 1 END) AS "Hỗ trợ giáo dục" FROM households WHERE classify='Hộ nghèo' AND "administrative.district" ILIKE '%Cư Jút%' AND "administrative.year"=2024;""",
                  """SELECT CASE WHEN (2024 - m."member.birthYear")<16 THEN 'Dưới 16 tuổi' WHEN (2024 - m."member.birthYear")<=60 THEN '16-60 tuổi' ELSE 'Trên 60 tuổi' END AS "Nhóm tuổi", COUNT(*) AS "Số thành viên" FROM members m JOIN households h ON m."family.code"=h."family.code" AND m."administrative.year"=h."administrative.year" WHERE h.classify='Hộ nghèo' AND m."administrative.district" ILIKE '%Cư Jút%' AND m."administrative.year"=2024 GROUP BY 1 ORDER BY 2 DESC;"""
              ],
              3, "3 DataFrames đánh giá toàn diện Cư Jút.")
add_test_case("TC_083", "C5_MULTI_DF", "Huyện", "multi_df_exec",
              "Phân tích đối chiếu hộ nghèo và cận nghèo tại Đắk Mil năm 2024: Bảng 1: So sánh số lượng và điểm thiếu hụt TB; Bảng 2: So sánh 4 chiều thiếu hụt cơ bản.",
              [
                  """SELECT classify AS "Phân loại", COUNT(*) AS "Số hộ", ROUND(AVG("deprivation.totalCount"),2) AS "Điểm thiếu hụt TB" FROM households WHERE classify IN ('Hộ nghèo','Hộ cận nghèo') AND "administrative.district" ILIKE '%Đắk Mil%' AND "administrative.year"=2024 GROUP BY 1;""",
                  """SELECT classify AS "Phân loại", SUM("deprivation.cleanWater") AS "Thiếu nước", SUM("deprivation.hygienicToilet") AS "Thiếu nhà tiêu", SUM("deprivation.housingQuality") AS "Thiếu nhà ở", SUM("deprivation.employment") AS "Thiếu việc làm" FROM households WHERE classify IN ('Hộ nghèo','Hộ cận nghèo') AND "administrative.district" ILIKE '%Đắk Mil%' AND "administrative.year"=2024 GROUP BY 1;"""
              ],
              2, "So sánh 2 DataFrames giữa nghèo và cận nghèo Đắk Mil.")
add_test_case("TC_084", "C5_MULTI_DF", "Tỉnh", "multi_df_exec",
              "Báo cáo chuyên đề Trẻ em trong hộ nghèo tỉnh Đắk Nông 2024: Bảng 1: Số lượng trẻ em và tỷ lệ có BHYT theo huyện; Bảng 2: Số lượng trẻ em bị thiếu hụt dinh dưỡng theo huyện.",
              [
                  """SELECT h."administrative.district" AS "Huyện", COUNT(*) AS "Tổng trẻ em", ROUND(COUNT(CASE WHEN m."member.hasHealthInsurance"=TRUE THEN 1 END)*100.0/NULLIF(COUNT(*),0),2) AS "Tỷ lệ BHYT (%)" FROM members m JOIN households h ON m."family.code"=h."family.code" AND m."administrative.year"=h."administrative.year" WHERE h.classify='Hộ nghèo' AND m."member.isChild"=TRUE AND m."administrative.year"=2024 GROUP BY 1 ORDER BY 2 DESC;""",
                  """SELECT h."administrative.district" AS "Huyện", COUNT(*) AS "Trẻ thiếu dinh dưỡng" FROM members m JOIN households h ON m."family.code"=h."family.code" AND m."administrative.year"=h."administrative.year" WHERE h.classify='Hộ nghèo' AND m."member.isChild"=TRUE AND m."member.nutritionDeprived"=TRUE AND m."administrative.year"=2024 GROUP BY 1 ORDER BY 2 DESC;"""
              ],
              2, "Chuyên đề trẻ em 2 DataFrames.")
add_test_case("TC_085", "C5_MULTI_DF", "Huyện", "multi_df_exec",
              "Báo cáo thực trạng đồng bào DTTS tại Đăk Glong 2024: Bảng 1: Thống kê hộ nghèo DTTS theo các xã; Bảng 2: Cơ cấu dân tộc (Mông, M'Nông, Dao...) của thành viên trong hộ nghèo.",
              [
                  """SELECT "administrative.commune" AS "Xã", COUNT(*) AS "Số hộ nghèo DTTS" FROM households WHERE classify='Hộ nghèo' AND "family.isDTTS"=TRUE AND "administrative.district" ILIKE '%Đăk Glong%' AND "administrative.year"=2024 GROUP BY 1 ORDER BY 2 DESC;""",
                  """SELECT m."member.ethnicity" AS "Dân tộc", COUNT(*) AS "Số thành viên" FROM members m JOIN households h ON m."family.code"=h."family.code" AND m."administrative.year"=h."administrative.year" WHERE h.classify='Hộ nghèo' AND h."family.isDTTS"=TRUE AND m."administrative.district" ILIKE '%Đăk Glong%' AND m."administrative.year"=2024 GROUP BY 1 ORDER BY 2 DESC LIMIT 10;"""
              ],
              2, "2 DataFrames chuyên đề DTTS tại Đăk Glong.")
add_test_case("TC_086", "C5_MULTI_DF", "Tỉnh", "multi_df_exec",
              "So sánh kết quả giảm nghèo năm 2024 so với 2023: Bảng 1: Tổng số hộ nghèo các huyện năm 2023; Bảng 2: Tổng số hộ nghèo các huyện năm 2024.",
              [
                  """SELECT "administrative.district" AS "Huyện", COUNT(*) AS "Hộ nghèo 2023" FROM households WHERE classify='Hộ nghèo' AND "administrative.year"=2023 GROUP BY 1 ORDER BY 1;""",
                  """SELECT "administrative.district" AS "Huyện", COUNT(*) AS "Hộ nghèo 2024" FROM households WHERE classify='Hộ nghèo' AND "administrative.year"=2024 GROUP BY 1 ORDER BY 1;"""
              ],
              2, "So sánh biến động giảm nghèo qua 2 năm.")
add_test_case("TC_087", "C5_MULTI_DF", "Huyện", "multi_df_exec",
              "Đánh giá các chính sách an sinh tại huyện Tuy Đức 2024: Bảng 1: Số hộ được hỗ trợ theo từng loại (Nhà ở, Y tế, Giáo dục, Tín dụng); Bảng 2: Danh sách 5 xã có số hộ nghèo chưa được hỗ trợ nhà ở cao nhất.",
              [
                  """SELECT SUM(CASE WHEN "support.housing"=TRUE THEN 1 ELSE 0 END) AS "Hỗ trợ nhà ở", SUM(CASE WHEN "support.health"=TRUE THEN 1 ELSE 0 END) AS "Hỗ trợ y tế", SUM(CASE WHEN "support.education"=TRUE THEN 1 ELSE 0 END) AS "Hỗ trợ giáo dục", SUM(CASE WHEN "support.credit"=TRUE THEN 1 ELSE 0 END) AS "Hỗ trợ tín dụng" FROM households WHERE classify='Hộ nghèo' AND "administrative.district" ILIKE '%Tuy Đức%' AND "administrative.year"=2024;""",
                  """SELECT "administrative.commune" AS "Xã", COUNT(*) AS "Hộ nghèo chưa hỗ trợ nhà ở" FROM households WHERE classify='Hộ nghèo' AND ("support.housing"=FALSE OR "support.housing" IS NULL) AND "administrative.district" ILIKE '%Tuy Đức%' AND "administrative.year"=2024 GROUP BY 1 ORDER BY 2 DESC LIMIT 5;"""
              ],
              2, "Đánh giá an sinh xã hội Tuy Đức.")
add_test_case("TC_088", "C5_MULTI_DF", "Thành phố", "multi_df_exec",
              "Hồ sơ hộ nghèo TP Gia Nghĩa 2024: Bảng 1: Phân loại theo nguyên nhân nghèo; Bảng 2: Phân loại theo giới tính và độ tuổi trung bình chủ hộ.",
              [
                  """SELECT 'Thiếu vốn' AS "Nguyên nhân", COUNT(CASE WHEN "reason.lackCapital"=TRUE THEN 1 END) AS "Số hộ" FROM households WHERE classify='Hộ nghèo' AND "administrative.district" ILIKE '%Gia Nghĩa%' AND "administrative.year"=2024 UNION ALL SELECT 'Thiếu lao động', COUNT(CASE WHEN "reason.lackLabor"=TRUE THEN 1 END) FROM households WHERE classify='Hộ nghèo' AND "administrative.district" ILIKE '%Gia Nghĩa%' AND "administrative.year"=2024;""",
                  """SELECT CASE WHEN "family.hostGender" ILIKE '%Nữ%' THEN 'Nữ' ELSE 'Nam' END AS "Giới tính chủ hộ", COUNT(*) AS "Số hộ", ROUND(AVG(2024 - "family.hostBirthYear"),1) AS "Tuổi trung bình" FROM households WHERE classify='Hộ nghèo' AND "administrative.district" ILIKE '%Gia Nghĩa%' AND "administrative.year"=2024 GROUP BY 1;"""
              ],
              2, "2 DataFrames hồ sơ nghèo Gia Nghĩa.")
add_test_case("TC_089", "C5_MULTI_DF", "Huyện", "multi_df_exec",
              "Khảo sát thiếu hụt hạ tầng thiết yếu huyện Krông Nô 2024: Bảng 1: Thống kê số hộ thiếu nước sinh hoạt theo xã; Bảng 2: Thống kê số hộ thiếu nhà tiêu hợp vệ sinh theo xã.",
              [
                  """SELECT "administrative.commune" AS "Xã", COUNT(*) AS "Hộ thiếu nước sạch" FROM households WHERE classify='Hộ nghèo' AND "deprivation.cleanWater"=1 AND "administrative.district" ILIKE '%Krông Nô%' AND "administrative.year"=2024 GROUP BY 1 ORDER BY 2 DESC;""",
                  """SELECT "administrative.commune" AS "Xã", COUNT(*) AS "Hộ thiếu nhà tiêu" FROM households WHERE classify='Hộ nghèo' AND "deprivation.hygienicToilet"=1 AND "administrative.district" ILIKE '%Krông Nô%' AND "administrative.year"=2024 GROUP BY 1 ORDER BY 2 DESC;"""
              ],
              2, "Khảo sát nước và vệ sinh Krông Nô.")
add_test_case("TC_090", "C5_MULTI_DF", "Tỉnh", "multi_df_exec",
              "Đánh giá tình trạng phụ thuộc lao động toàn tỉnh 2024: Bảng 1: Thống kê số hộ nghèo theo số nhân khẩu; Bảng 2: Số hộ có chủ hộ không có khả năng lao động chia theo huyện.",
              [
                  """SELECT CASE WHEN "family.numberOfMembers">=5 THEN 'Đông nhân khẩu (5+)' ELSE 'Bình thường (<5)' END AS "Nhóm nhân khẩu", COUNT(*) AS "Số hộ nghèo" FROM households WHERE classify='Hộ nghèo' AND "administrative.year"=2024 GROUP BY 1;""",
                  """SELECT "administrative.district" AS "Huyện", COUNT(*) AS "Chủ hộ không KNLĐ" FROM households WHERE classify='Hộ nghèo' AND "family.hasNoLaborCapacity"=TRUE AND "administrative.year"=2024 GROUP BY 1 ORDER BY 2 DESC;"""
              ],
              2, "Phụ thuộc lao động toàn tỉnh.")
add_test_case("TC_091", "C5_MULTI_DF", "Huyện", "multi_df_exec",
              "Chuyên đề giảm nghèo huyện Đắk Song 2024: Bảng 1: Số hộ thoát nghèo theo xã; Bảng 2: Số hộ phát sinh nghèo mới theo xã.",
              [
                  """SELECT "administrative.commune" AS "Xã", COUNT(*) AS "Số hộ thoát nghèo" FROM households WHERE "transition.beginningClassify"='Nghèo' AND classify='Hộ không nghèo' AND "administrative.district" ILIKE '%Đắk Song%' AND "administrative.year"=2024 GROUP BY 1 ORDER BY 2 DESC;""",
                  """SELECT "administrative.commune" AS "Xã", COUNT(*) AS "Số hộ nghèo mới" FROM households WHERE ("transition.beginningClassify" != 'Nghèo' OR "transition.beginningClassify" IS NULL) AND classify='Hộ nghèo' AND "administrative.district" ILIKE '%Đắk Song%' AND "administrative.year"=2024 GROUP BY 1 ORDER BY 2 DESC;"""
              ],
              2, "Biến động thoát nghèo và nghèo mới Đắk Song.")
add_test_case("TC_092", "C5_MULTI_DF", "Huyện", "multi_df_exec",
              "Phân tích chiều thiếu hụt thông tin và viễn thông tại Đắk R'Lấp 2024: Bảng 1: Thiếu hụt phương tiện giải trí nghe nhìn theo xã; Bảng 2: Thiếu hụt dịch vụ viễn thông theo xã.",
              [
                  """SELECT "administrative.commune" AS "Xã", COUNT(*) AS "Thiếu nghe nhìn" FROM households WHERE classify='Hộ nghèo' AND "deprivation.informationAccessAssets"=1 AND "administrative.district" ILIKE '%Đắk R''Lấp%' AND "administrative.year"=2024 GROUP BY 1 ORDER BY 2 DESC;""",
                  """SELECT "administrative.commune" AS "Xã", COUNT(*) AS "Thiếu viễn thông" FROM households WHERE classify='Hộ nghèo' AND "deprivation.telecommunication"=1 AND "administrative.district" ILIKE '%Đắk R''Lấp%' AND "administrative.year"=2024 GROUP BY 1 ORDER BY 2 DESC;"""
              ],
              2, "Thiếu thông tin và viễn thông Đắk R'Lấp.")
add_test_case("TC_093", "C5_MULTI_DF", "Tỉnh", "multi_df_exec",
              "Báo cáo tổng kết bảo hiểm y tế toàn tỉnh 2024: Bảng 1: Tỷ lệ BHYT cấp hộ gia đình theo huyện; Bảng 2: Tỷ lệ BHYT cấp thành viên theo huyện.",
              [
                  """SELECT "administrative.district" AS "Huyện", ROUND(COUNT(CASE WHEN "support.health"=TRUE THEN 1 END)*100.0/NULLIF(COUNT(*),0),2) AS "Tỷ lệ BHYT Hộ (%)" FROM households WHERE classify='Hộ nghèo' AND "administrative.year"=2024 GROUP BY 1 ORDER BY 2 DESC;""",
                  """SELECT h."administrative.district" AS "Huyện", ROUND(COUNT(CASE WHEN m."member.hasHealthInsurance"=TRUE THEN 1 END)*100.0/NULLIF(COUNT(*),0),2) AS "Tỷ lệ BHYT Thành viên (%)" FROM members m JOIN households h ON m."family.code"=h."family.code" AND m."administrative.year"=h."administrative.year" WHERE h.classify='Hộ nghèo' AND m."administrative.year"=2024 GROUP BY 1 ORDER BY 2 DESC;"""
              ],
              2, "BHYT đối chiếu cấp hộ và thành viên.")
add_test_case("TC_094", "C5_MULTI_DF", "Xã", "multi_df_exec",
              "Đánh giá chi tiết xã Đắk R'La (Đắk Mil) 2024: Bảng 1: Số hộ nghèo và cận nghèo; Bảng 2: Top 3 nguyên nhân nghèo chính của xã.",
              [
                  """SELECT classify AS "Phân loại", COUNT(*) AS "Số hộ" FROM households WHERE classify IN ('Hộ nghèo','Hộ cận nghèo') AND "administrative.commune" ILIKE '%Đắk R''La%' AND "administrative.year"=2024 GROUP BY 1;""",
                  """SELECT 'Thiếu vốn' AS "Nguyên nhân", COUNT(CASE WHEN "reason.lackCapital"=TRUE THEN 1 END) AS "Số hộ" FROM households WHERE classify='Hộ nghèo' AND "administrative.commune" ILIKE '%Đắk R''La%' AND "administrative.year"=2024 UNION ALL SELECT 'Thiếu đất sản xuất', COUNT(CASE WHEN "reason.lackProductionLand"=TRUE THEN 1 END) FROM households WHERE classify='Hộ nghèo' AND "administrative.commune" ILIKE '%Đắk R''La%' AND "administrative.year"=2024 UNION ALL SELECT 'Thiếu lao động', COUNT(CASE WHEN "reason.lackLabor"=TRUE THEN 1 END) FROM households WHERE classify='Hộ nghèo' AND "administrative.commune" ILIKE '%Đắk R''La%' AND "administrative.year"=2024 ORDER BY 2 DESC;"""
              ],
              2, "Đánh giá 2 DataFrames xã Đắk R'La.")
add_test_case("TC_095", "C5_MULTI_DF", "Huyện", "multi_df_exec",
              "Phân tích hộ nghèo DTTS huyện Cư Jút 2024: Bảng 1: Tỷ lệ DTTS trên tổng số hộ nghèo; Bảng 2: Cơ cấu dân tộc thiểu số cụ thể (Ê Đê, Tày, Nùng...).",
              [
                  """SELECT COUNT(*) AS "Tổng hộ nghèo", COUNT(CASE WHEN "family.isDTTS"=TRUE THEN 1 END) AS "Hộ nghèo DTTS", ROUND(COUNT(CASE WHEN "family.isDTTS"=TRUE THEN 1 END)*100.0/NULLIF(COUNT(*),0),2) AS "Tỷ lệ (%)" FROM households WHERE classify='Hộ nghèo' AND "administrative.district" ILIKE '%Cư Jút%' AND "administrative.year"=2024;""",
                  """SELECT m."member.ethnicity" AS "Dân tộc", COUNT(DISTINCT h."family.code") AS "Số hộ" FROM members m JOIN households h ON m."family.code"=h."family.code" AND m."administrative.year"=h."administrative.year" WHERE h.classify='Hộ nghèo' AND h."family.isDTTS"=TRUE AND m."administrative.district" ILIKE '%Cư Jút%' AND m."administrative.year"=2024 GROUP BY 1 ORDER BY 2 DESC LIMIT 5;"""
              ],
              2, "Phân tích 2 DataFrames DTTS tại Cư Jút.")
add_test_case("TC_096", "C5_MULTI_DF", "Huyện", "multi_df_exec",
              "Khảo sát tình trạng nhà ở hộ nghèo Đăk Glong 2024: Bảng 1: Số hộ thiếu chất lượng nhà ở theo xã; Bảng 2: Số hộ thiếu diện tích nhà ở theo xã.",
              [
                  """SELECT "administrative.commune" AS "Xã", COUNT(*) AS "Thiếu chất lượng nhà" FROM households WHERE classify='Hộ nghèo' AND "deprivation.housingQuality"=1 AND "administrative.district" ILIKE '%Đăk Glong%' AND "administrative.year"=2024 GROUP BY 1 ORDER BY 2 DESC;""",
                  """SELECT "administrative.commune" AS "Xã", COUNT(*) AS "Thiếu diện tích nhà" FROM households WHERE classify='Hộ nghèo' AND "deprivation.housingArea"=1 AND "administrative.district" ILIKE '%Đăk Glong%' AND "administrative.year"=2024 GROUP BY 1 ORDER BY 2 DESC;"""
              ],
              2, "Khảo sát nhà ở 2 DataFrames tại Đăk Glong.")
add_test_case("TC_097", "C5_MULTI_DF", "Tỉnh", "multi_df_exec",
              "Báo cáo tổng kết các chiều thiếu hụt cơ bản toàn tỉnh 2024: Bảng 1: Top 5 chiều thiếu hụt có số hộ nghèo vướng mắc nhiều nhất; Bảng 2: Phân bố điểm thiếu hụt TB theo huyện.",
              [
                  """SELECT 'Việc làm' AS "Chiều thiếu hụt", COUNT(CASE WHEN "deprivation.employment"=1 THEN 1 END) AS "Số hộ nghèo" FROM households WHERE classify='Hộ nghèo' AND "administrative.year"=2024 UNION ALL SELECT 'Chất lượng nhà ở', COUNT(CASE WHEN "deprivation.housingQuality"=1 THEN 1 END) FROM households WHERE classify='Hộ nghèo' AND "administrative.year"=2024 UNION ALL SELECT 'Nước sinh hoạt', COUNT(CASE WHEN "deprivation.cleanWater"=1 THEN 1 END) FROM households WHERE classify='Hộ nghèo' AND "administrative.year"=2024 UNION ALL SELECT 'Nhà tiêu hợp vệ sinh', COUNT(CASE WHEN "deprivation.hygienicToilet"=1 THEN 1 END) FROM households WHERE classify='Hộ nghèo' AND "administrative.year"=2024 UNION ALL SELECT 'Trình độ học vấn', COUNT(CASE WHEN "deprivation.adultEducation"=1 THEN 1 END) FROM households WHERE classify='Hộ nghèo' AND "administrative.year"=2024 ORDER BY 2 DESC;""",
                  """SELECT "administrative.district" AS "Huyện", ROUND(AVG("deprivation.totalCount"),2) AS "Điểm thiếu hụt TB" FROM households WHERE classify='Hộ nghèo' AND "administrative.year"=2024 GROUP BY 1 ORDER BY 2 DESC;"""
              ],
              2, "Báo cáo thiếu hụt đa chiều toàn tỉnh.")
add_test_case("TC_098", "C5_MULTI_DF", "Huyện", "multi_df_exec",
              "Đánh giá hộ cận nghèo huyện Tuy Đức 2024 qua 2 bảng: Bảng 1: Số lượng và tỷ lệ DTTS; Bảng 2: Thống kê số lượng cận nghèo theo từng xã.",
              [
                  """SELECT COUNT(*) AS "Tổng hộ cận nghèo", COUNT(CASE WHEN "family.isDTTS"=TRUE THEN 1 END) AS "Cận nghèo DTTS", ROUND(COUNT(CASE WHEN "family.isDTTS"=TRUE THEN 1 END)*100.0/NULLIF(COUNT(*),0),2) AS "Tỷ lệ DTTS (%)" FROM households WHERE classify='Hộ cận nghèo' AND "administrative.district" ILIKE '%Tuy Đức%' AND "administrative.year"=2024;""",
                  """SELECT "administrative.commune" AS "Xã", COUNT(*) AS "Số hộ cận nghèo" FROM households WHERE classify='Hộ cận nghèo' AND "administrative.district" ILIKE '%Tuy Đức%' AND "administrative.year"=2024 GROUP BY 1 ORDER BY 2 DESC;"""
              ],
              2, "Đánh giá 2 DataFrames cận nghèo Tuy Đức.")
add_test_case("TC_099", "C5_MULTI_DF", "Tỉnh", "multi_df_exec",
              "Báo cáo đối chiếu an sinh toàn tỉnh 2024: Bảng 1: Số hộ nghèo nhận được hỗ trợ nhà ở, y tế, giáo dục theo huyện; Bảng 2: Tỷ lệ hộ cận nghèo nhận được hỗ trợ BHYT theo huyện.",
              [
                  """SELECT "administrative.district" AS "Huyện", COUNT(CASE WHEN "support.housing"=TRUE THEN 1 END) AS "Nhà ở", COUNT(CASE WHEN "support.health"=TRUE THEN 1 END) AS "BHYT", COUNT(CASE WHEN "support.education"=TRUE THEN 1 END) AS "Giáo dục" FROM households WHERE classify='Hộ nghèo' AND "administrative.year"=2024 GROUP BY 1 ORDER BY 1;""",
                  """SELECT "administrative.district" AS "Huyện", ROUND(COUNT(CASE WHEN "support.health"=TRUE THEN 1 END)*100.0/NULLIF(COUNT(*),0),2) AS "Tỷ lệ BHYT cận nghèo (%)" FROM households WHERE classify='Hộ cận nghèo' AND "administrative.year"=2024 GROUP BY 1 ORDER BY 2 DESC;"""
              ],
              2, "Đối chiếu an sinh 2 DataFrames.")
add_test_case("TC_100", "C5_MULTI_DF", "Tỉnh", "multi_df_exec",
              "Tổng kiểm kê CSDL hộ nghèo Đắk Nông 2024 qua 3 bảng: Bảng 1: Thống kê theo huyện; Bảng 2: Thống kê theo quy mô nhân khẩu; Bảng 3: Thống kê theo nhóm dân tộc.",
              [
                  """SELECT "administrative.district" AS "Huyện/Thành phố", COUNT(*) AS "Số hộ nghèo" FROM households WHERE classify='Hộ nghèo' AND "administrative.year"=2024 GROUP BY 1 ORDER BY 2 DESC;""",
                  """SELECT CASE WHEN "family.numberOfMembers"<=2 THEN '1-2 người' WHEN "family.numberOfMembers"<=4 THEN '3-4 người' ELSE '5+ người' END AS "Quy mô", COUNT(*) AS "Số hộ" FROM households WHERE classify='Hộ nghèo' AND "administrative.year"=2024 GROUP BY 1 ORDER BY 2 DESC;""",
                  """SELECT CASE WHEN "family.isDTTS"=TRUE THEN 'Dân tộc thiểu số' ELSE 'Kinh/Khác' END AS "Nhóm dân tộc", COUNT(*) AS "Số hộ" FROM households WHERE classify='Hộ nghèo' AND "administrative.year"=2024 GROUP BY 1;"""
              ],
              3, "Bộ 3 DataFrames tổng kiểm kê toàn diện CSDL hộ nghèo tỉnh.")

print(f"Total test cases generated and verified: {len(benchmark_suite)}")

output_path = PROJECT_ROOT / "test/comprehensive_100_qa_benchmark.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump({
        "benchmark_title": "Golden 100 Comprehensive QA Benchmark Suite for Agentic Chatbot",
        "database_source": "data/Processed/intern_chatbot.duckdb",
        "total_test_cases": len(benchmark_suite),
        "categories": [
            {"code": "C1_SIMPLE", "name": "Truy vấn Đơn giản & Cơ bản (Simple / Single Requirement)", "count": 20},
            {"code": "C2_MULTI_COND", "name": "Truy vấn Đa điều kiện & Phức hợp (Multi-Condition Filtering)", "count": 20},
            {"code": "C3_MEMBER_LEVEL", "name": "Truy vấn Cấp Thành viên & Chủ hộ (Member & Head-of-Household Level)", "count": 20},
            {"code": "C4_MULTI_REQ", "name": "Truy vấn Đa yêu cầu trong 1 Prompt (Multi-Requirement Complex Prompts)", "count": 20},
            {"code": "C5_MULTI_DF", "name": "Truy vấn Đa luồng / Nhiều DataFrame (Multi-Query / Multi-DataFrame Execution)", "count": 20}
        ],
        "test_cases": benchmark_suite
    }, f, ensure_ascii=False, indent=2)

print(f"Saved verified benchmark suite to: {output_path}")
conn.close()
