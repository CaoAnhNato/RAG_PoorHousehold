# -*- coding: utf-8 -*-
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
quest_ans_path = PROJECT_ROOT / "artifacts" / "quest_ans.md"

test_cases = [
    {
        "id": 41,
        "question": "thống kê sl hộ nghèo vs cận nghèo dtts năm 2024 ở các huyện xem thế nào",
        "sql": 'SELECT "administrative.district" AS district, SUM(CASE WHEN "classify" = \'Hộ nghèo\' THEN 1 ELSE 0 END) AS poor_dtts, SUM(CASE WHEN "classify" = \'Hộ cận nghèo\' THEN 1 ELSE 0 END) AS near_poor_dtts FROM households WHERE "family.isDTTS" = true AND "administrative.year" = 2024 AND "classify" IN (\'Hộ nghèo\', \'Hộ cận nghèo\') GROUP BY district ORDER BY poor_dtts DESC;',
        "db_res": [
          { "district": "Huyện Tuy Đức", "poor_dtts": 829, "near_poor_dtts": 917 },
          { "district": "Huyện Đăk Glong", "poor_dtts": 538, "near_poor_dtts": 485 },
          { "district": "Huyện Đắk Song", "poor_dtts": 279, "near_poor_dtts": 510 },
          { "district": "Huyện Đắk Mil", "poor_dtts": 221, "near_poor_dtts": 466 },
          { "district": "Huyện Cư Jút", "poor_dtts": 204, "near_poor_dtts": 304 },
          { "district": "Huyện Krông Nô", "poor_dtts": 189, "near_poor_dtts": 588 },
          { "district": "Huyện Đắk RLấp", "poor_dtts": 135, "near_poor_dtts": 271 },
          { "district": "Thành phố Gia Nghĩa", "poor_dtts": 51, "near_poor_dtts": 142 }
        ],
        "headers": ["district", "poor_dtts", "near_poor_dtts"]
    },
    {
        "id": 42,
        "question": "huyện krông nô 2024 có bao nhiêu hn bị thiếu vốn sx với thiếu đất sx?",
        "sql": 'SELECT SUM(CASE WHEN "reason.lackCapital" = true THEN 1 ELSE 0 END) AS lack_capital, SUM(CASE WHEN "reason.lackProductionLand" = true THEN 1 ELSE 0 END) AS lack_land FROM households WHERE "administrative.district" ILIKE \'%Krông Nô%\' AND "classify" = \'Hộ nghèo\' AND "administrative.year" = 2024;',
        "db_res": [
          { "lack_capital": 80, "lack_land": 60 }
        ],
        "headers": ["lack_capital", "lack_land"]
    },
    {
        "id": 43,
        "question": "năm 2024 khu vực thành thị hay nông thôn có số hộ thoát nghèo nhiều hơn?",
        "sql": 'SELECT "administrative.areaType" AS area_type, COUNT(*) AS escaped_count FROM households WHERE "transition.isEscapedPoverty" = true AND "administrative.year" = 2024 GROUP BY area_type ORDER BY escaped_count DESC;',
        "db_res": [
          { "area_type": "rural", "escaped_count": 1063 },
          { "area_type": "urban", "escaped_count": 70 }
        ],
        "headers": ["area_type", "escaped_count"]
    },
    {
        "id": 44,
        "question": "top 3 xã có trẻ em ko đi học nhiều nhất 2024 là xã nào?",
        "sql": 'SELECT "administrative.commune" AS commune, SUM("children.schoolAttendanceDeprivedCount") AS deprived_children FROM households WHERE "administrative.year" = 2024 AND "children.schoolAttendanceDeprivedCount" > 0 GROUP BY commune ORDER BY deprived_children DESC LIMIT 3;',
        "db_res": [
          { "commune": "Xã Quảng Tân", "deprived_children": 71 },
          { "commune": "Xã Đắk Ngo", "deprived_children": 69 },
          { "commune": "Xã Đắk RTíh", "deprived_children": 65 }
        ],
        "headers": ["commune", "deprived_children"]
    },
    {
        "id": 45,
        "question": "ở tp gia nghĩa bn hộ nghèo bị thiếu hụt chất lượng nhà ở với diện tích nhà ở năm 2024",
        "sql": 'SELECT SUM(CASE WHEN "deprivation.housingQuality" = true THEN 1 ELSE 0 END) AS poor_quality_housing, SUM(CASE WHEN "deprivation.housingArea" = true THEN 1 ELSE 0 END) AS small_area_housing FROM households WHERE "administrative.district" ILIKE \'%Gia Nghĩa%\' AND "classify" = \'Hộ nghèo\' AND "administrative.year" = 2024;',
        "db_res": [
          { "poor_quality_housing": 34, "small_area_housing": 12 }
        ],
        "headers": ["poor_quality_housing", "small_area_housing"]
    },
    {
        "id": 46,
        "question": "tính tỷ lệ chủ hộ nam vs nữ trong các hcn năm 2024 toàn tỉnh",
        "sql": 'SELECT "family.hostGender" AS gender, COUNT(*) AS count, ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage FROM households WHERE "classify" = \'Hộ cận nghèo\' AND "administrative.year" = 2024 AND "family.hostGender" IN (\'Nam\', \'Nữ\') GROUP BY gender;',
        "db_res": [
          { "gender": "Nữ", "count": 1089, "percentage": 29.57 },
          { "gender": "Nam", "count": 2594, "percentage": 70.43 }
        ],
        "headers": ["gender", "count", "percentage"]
    },
    {
        "id": 47,
        "question": "so sánh sl hộ nghèo ko có khả năng lao động ở đắk mil giữa 2 năm 2023 vs 2024",
        "sql": 'SELECT "administrative.year" AS year, COUNT(*) AS no_labor_capacity_count FROM households WHERE "administrative.district" ILIKE \'%Đắk Mil%\' AND "classify" = \'Hộ nghèo\' AND "family.hasNoLaborCapacity" = true AND "administrative.year" IN (2023, 2024) GROUP BY year ORDER BY year;',
        "db_res": [
          { "year": 2023, "no_labor_capacity_count": 137 },
          { "year": 2024, "no_labor_capacity_count": 67 }
        ],
        "headers": ["year", "no_labor_capacity_count"]
    },
    {
        "id": 48,
        "question": "đăk glong 2024 có bn hộ nghèo cần hỗ trợ về y tế và giáo dục?",
        "sql": 'SELECT SUM(CASE WHEN "support.health" = true THEN 1 ELSE 0 END) AS need_health_support, SUM(CASE WHEN "support.education" = true THEN 1 ELSE 0 END) AS need_edu_support FROM households WHERE "administrative.district" ILIKE \'%Đăk Glong%\' AND "classify" = \'Hộ nghèo\' AND "administrative.year" = 2024;',
        "db_res": [
          { "need_health_support": 538, "need_edu_support": 470 }
        ],
        "headers": ["need_health_support", "need_edu_support"]
    },
    {
        "id": 49,
        "question": "huyện nào có nhiều hộ nghèo bị ốm đau tai nạn nhất năm 2024?",
        "sql": 'SELECT "administrative.district" AS district, COUNT(*) AS illness_count FROM households WHERE "classify" = \'Hộ nghèo\' AND "reason.illnessOrAccident" = true AND "administrative.year" = 2024 GROUP BY district ORDER BY illness_count DESC;',
        "db_res": [
          { "district": "Huyện Tuy Đức", "illness_count": 386 },
          { "district": "Huyện Đăk Glong", "illness_count": 265 },
          { "district": "Huyện Đắk Song", "illness_count": 127 },
          { "district": "Huyện Đắk Mil", "illness_count": 97 },
          { "district": "Huyện Cư Jút", "illness_count": 94 },
          { "district": "Huyện Krông Nô", "illness_count": 83 },
          { "district": "Huyện Đắk RLấp", "illness_count": 69 },
          { "district": "Thành phố Gia Nghĩa", "illness_count": 26 }
        ],
        "headers": ["district", "illness_count"]
    },
    {
        "id": 50,
        "question": "check xem cư jút 2024 có bn hộ nghèo thiếu nước sạch vs nhà vệ sinh",
        "sql": 'SELECT SUM(CASE WHEN "deprivation.cleanWater" = true THEN 1 ELSE 0 END) AS lack_clean_water, SUM(CASE WHEN "deprivation.hygienicToilet" = true THEN 1 ELSE 0 END) AS lack_toilet FROM households WHERE "administrative.district" ILIKE \'%Cư Jút%\' AND "classify" = \'Hộ nghèo\' AND "administrative.year" = 2024;',
        "db_res": [
          { "lack_clean_water": 0, "lack_toilet": 1 }
        ],
        "headers": ["lack_clean_water", "lack_toilet"]
    }
]

def format_table(headers, rows):
    header_str = "| " + " | ".join(headers) + " |"
    sep_str = "| " + " | ".join([":---" if i == 0 else "---:" for i in range(len(headers))]) + " |"
    row_strs = []
    for row in rows:
        row_strs.append("| " + " | ".join([str(row.get(h, "")) for h in headers]) + " |")
    return "\n".join([header_str, sep_str] + row_strs)

def append_to_md():
    content = quest_ans_path.read_text(encoding="utf-8")
    
    # Ensure no duplicate addition
    if "### Câu 41:" in content:
        print("Đã tồn tại Câu 41 trong file quest_ans.md!")
        return

    new_blocks = []
    for tc in test_cases:
        block = f"### Câu {tc['id']}: {tc['question']}\n\n"
        block += "**SQL:**\n\n```sql\n" + tc["sql"] + "\n```\n\n"
        block += "**DataFrame:**\n\n" + format_table(tc["headers"], tc["db_res"]) + "\n\n"
        block += "**Kết quả DB:**\n\n```json\n" + json.dumps(tc["db_res"], ensure_ascii=False, indent=2) + "\n```\n\n---\n"
        new_blocks.append(block)

    appended_text = "\n" + "\n".join(new_blocks) + "\n"
    quest_ans_path.write_text(content.rstrip() + "\n\n---\n" + appended_text, encoding="utf-8")
    print("Đã thêm thành công 10 câu test case vào cuối file quest_ans.md!")

if __name__ == "__main__":
    append_to_md()
