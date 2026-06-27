# -*- coding: utf-8 -*-
from __future__ import annotations
import duckdb
import pandas as pd
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = PROJECT_ROOT / "data" / "Processed" / "intern_chatbot.duckdb"

# Tên biểu mẫu chuẩn Chính phủ
REPORT_TITLES = {
    1: "TỔNG HỢP KẾT QUẢ CHÍNH THỨC RÀ SOÁT HỘ NGHÈO; HỘ CẬN NGHÈO; HỘ LÀM NÔNG, LÂM, NGƯ NGHIỆP CÓ MỨC SỐNG TRUNG BÌNH",
    2: "TỔNG HỢP DIỄN BIẾN HỘ NGHÈO",
    3: "TỔNG HỢP DIỄN BIẾN HỘ CẬN NGHÈO",
    4: "PHÂN TÍCH CÁC CHỈ SỐ THIẾU HỤT DỊCH VỤ XÃ HỘI CƠ BẢN CỦA HỘ NGHÈO",
    5: "PHÂN TÍCH TỶ LỆ CÁC CHỈ SỐ THIẾU HỤT DỊCH VỤ XÃ HỘI CƠ BẢN CỦA HỘ NGHÈO",
    6: "PHÂN TÍCH CÁC CHỈ SỐ THIẾU HỤT DỊCH VỤ XÃ HỘI CƠ BẢN CỦA HỘ CẬN NGHÈO",
    7: "PHÂN TÍCH TỶ LỆ CÁC CHỈ SỐ THIẾU HỤT DỊCH VỤ XÃ HỘI CƠ BẢN CỦA HỘ CẬN NGHÈO",
    8: "PHÂN TÍCH HỘ NGHÈO, HỘ CẬN NGHÈO THEO CÁC NHÓM ĐỐI TƯỢNG",
    9: "PHÂN TÍCH HỘ NGHÈO, HỘ CẬN NGHÈO THEO DÂN TỘC",
    10: "PHÂN NHÓM HỘ NGHÈO, HỘ CẬN NGHÈO THEO CÁC NGUYÊN NHÂN NGHÈO",
    11: "TỔNG HỢP CHỈ TIÊU THIẾU HỤT CỦA TRẺ EM THUỘC HỘ NGHÈO, HỘ CẬN NGHÈO",
    12: "TỔNG HỢP KẾT QUẢ RÀ SOÁT HỘ NGHÈO THEO CHUẨN NGHÈO ĐA CHIỀU",
    13: "TỔNG HỢP KẾT QUẢ RÀ SOÁT HỘ CẬN NGHÈO THEO CHUẨN NGHÈO ĐA CHIỀU",
    14: "DANH SÁCH CHI TIẾT HỘ CẬN NGHÈO",
    15: "DANH SÁCH CHI TIẾT HỘ NGHÈO"
}

def get_report_sql(report_id: int, year: int = 2024, district: str | None = None) -> str:
    """
    Sinh câu truy vấn SQL DuckDB tĩnh cho từng biểu mẫu báo cáo chuẩn Chính phủ,
    bổ sung trường administrative.district để phục vụ phân cấp Huyện -> Xã.
    """
    where_clause = f'WHERE "administrative.year" = {year}'
    if district:
        where_clause += f' AND "administrative.district" ILIKE \'%{district}%\''

    if report_id == 1:
        return f"""
        SELECT 
            "administrative.district" AS "District",
            "administrative.commune" AS "Phường/Xã",
            COUNT(*) AS "Số hộ",
            SUM(COALESCE("family.numberOfMembers", 1)) AS "Nhân khẩu",
            SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 ELSE 0 END) AS "Tổng số hộ nghèo",
            SUM(CASE WHEN classify = 'Hộ cận nghèo' THEN 1 ELSE 0 END) AS "Tổng số hộ cận nghèo",
            SUM(CASE WHEN "family.isAgricultureForestryFisherySaltMediumLivingStandard" = true THEN 1 ELSE 0 END) AS "Tổng số hộ nông, lâm, ngư nghiệp",
            SUM(CASE WHEN classify = 'Hộ nghèo' THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "Tổng số khẩu nghèo",
            SUM(CASE WHEN classify = 'Hộ cận nghèo' THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "Tổng số khẩu cận nghèo",
            SUM(CASE WHEN "family.isAgricultureForestryFisherySaltMediumLivingStandard" = true THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "Tổng số khẩu nông, lâm, ngư nghiệp"
        FROM households
        {where_clause}
        GROUP BY "administrative.district", "administrative.commune"
        ORDER BY "administrative.district", "administrative.commune";
        """
    elif report_id == 2:
        return f"""
        SELECT 
            "District", "Phường/Xã", "Phân tổ",
            "Tổng số hộ nghèo đầu kỳ", "Trở thành hộ cận nghèo", "Vượt chuẩn cận nghèo",
            "Số hộ khác giảm", "Số hộ cận nghèo trở thành", "Tái nghèo", "Phát sinh mới", "Số hộ khác tăng",
            ("Tổng số hộ nghèo đầu kỳ" - "Trở thành hộ cận nghèo" - "Vượt chuẩn cận nghèo" - "Số hộ khác giảm" + "Số hộ cận nghèo trở thành" + "Tái nghèo" + "Phát sinh mới" + "Số hộ khác tăng") AS "Tổng số hộ nghèo cuối kỳ"
        FROM (
            SELECT 
                "administrative.district" AS "District",
                "administrative.commune" AS "Phường/Xã",
                'Hộ' AS "Phân tổ",
                SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Nghèo%' AND NOT "transition.beginningClassify" ILIKE '%Cận nghèo%' THEN 1 ELSE 0 END) AS "Tổng số hộ nghèo đầu kỳ",
                SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Nghèo%' AND NOT "transition.beginningClassify" ILIKE '%Cận nghèo%' AND "transition.endingClassify" ILIKE '%Cận nghèo%' THEN 1 ELSE 0 END) AS "Trở thành hộ cận nghèo",
                SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Nghèo%' AND NOT "transition.beginningClassify" ILIKE '%Cận nghèo%' AND "transition.endingClassify" ILIKE '%Không nghèo%' THEN 1 ELSE 0 END) AS "Vượt chuẩn cận nghèo",
                0 AS "Số hộ khác giảm",
                SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Cận nghèo%' AND classify = 'Hộ nghèo' THEN 1 ELSE 0 END) AS "Số hộ cận nghèo trở thành",
                0 AS "Tái nghèo",
                SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Không nghèo%' AND classify = 'Hộ nghèo' THEN 1 ELSE 0 END) AS "Phát sinh mới",
                0 AS "Số hộ khác tăng"
            FROM households
            {where_clause}
            GROUP BY "administrative.district", "administrative.commune"
            
            UNION ALL
            
            SELECT 
                "administrative.district" AS "District",
                "administrative.commune" AS "Phường/Xã",
                'Nhân khẩu' AS "Phân tổ",
                SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Nghèo%' AND NOT "transition.beginningClassify" ILIKE '%Cận nghèo%' THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "Tổng số hộ nghèo đầu kỳ",
                SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Nghèo%' AND NOT "transition.beginningClassify" ILIKE '%Cận nghèo%' AND "transition.endingClassify" ILIKE '%Cận nghèo%' THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "Trở thành hộ cận nghèo",
                SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Nghèo%' AND NOT "transition.beginningClassify" ILIKE '%Cận nghèo%' AND "transition.endingClassify" ILIKE '%Không nghèo%' THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "Vượt chuẩn cận nghèo",
                0 AS "Số hộ khác giảm",
                SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Cận nghèo%' AND classify = 'Hộ nghèo' THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "Số hộ cận nghèo trở thành",
                0 AS "Tái nghèo",
                SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Không nghèo%' AND classify = 'Hộ nghèo' THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "Phát sinh mới",
                0 AS "Số hộ khác tăng"
            FROM households
            {where_clause}
            GROUP BY "administrative.district", "administrative.commune"
        ) AS subquery
        ORDER BY "District", "Phường/Xã", "Phân tổ";
        """
    elif report_id == 3:
        return f"""
        SELECT 
            "District", "Phường/Xã", "Phân tổ",
            "Tổng số hộ cận nghèo đầu kỳ", "Trở thành hộ nghèo", "Vượt chuẩn cận nghèo",
            "Số hộ khác giảm", "Số hộ nghèo trở thành hộ cận nghèo", "Tái cận nghèo", "Phát sinh mới", "Số hộ khác tăng",
            ("Tổng số hộ cận nghèo đầu kỳ" - "Trở thành hộ nghèo" - "Vượt chuẩn cận nghèo" - "Số hộ khác giảm" + "Số hộ nghèo trở thành hộ cận nghèo" + "Tái cận nghèo" + "Phát sinh mới" + "Số hộ khác tăng") AS "Tổng số hộ cận nghèo cuối kỳ"
        FROM (
            SELECT 
                "administrative.district" AS "District",
                "administrative.commune" AS "Phường/Xã",
                'Hộ' AS "Phân tổ",
                SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Cận nghèo%' THEN 1 ELSE 0 END) AS "Tổng số hộ cận nghèo đầu kỳ",
                SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Cận nghèo%' AND ("transition.endingClassify" ILIKE '%Hộ nghèo%' OR "transition.endingClassify" = 'Nghèo') THEN 1 ELSE 0 END) AS "Trở thành hộ nghèo",
                SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Cận nghèo%' AND "transition.endingClassify" ILIKE '%Không nghèo%' THEN 1 ELSE 0 END) AS "Vượt chuẩn cận nghèo",
                0 AS "Số hộ khác giảm",
                SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Nghèo%' AND NOT "transition.beginningClassify" ILIKE '%Cận nghèo%' AND classify = 'Hộ cận nghèo' THEN 1 ELSE 0 END) AS "Số hộ nghèo trở thành hộ cận nghèo",
                0 AS "Tái cận nghèo",
                SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Không nghèo%' AND classify = 'Hộ cận nghèo' THEN 1 ELSE 0 END) AS "Phát sinh mới",
                0 AS "Số hộ khác tăng"
            FROM households
            {where_clause}
            GROUP BY "administrative.district", "administrative.commune"
            
            UNION ALL
            
            SELECT 
                "administrative.district" AS "District",
                "administrative.commune" AS "Phường/Xã",
                'Nhân khẩu' AS "Phân tổ",
                SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Cận nghèo%' THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "Tổng số hộ cận nghèo đầu kỳ",
                SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Cận nghèo%' AND ("transition.endingClassify" ILIKE '%Hộ nghèo%' OR "transition.endingClassify" = 'Nghèo') THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "Trở thành hộ nghèo",
                SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Cận nghèo%' AND "transition.endingClassify" ILIKE '%Không nghèo%' THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "Vượt chuẩn cận nghèo",
                0 AS "Số hộ khác giảm",
                SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Nghèo%' AND NOT "transition.beginningClassify" ILIKE '%Cận nghèo%' AND classify = 'Hộ cận nghèo' THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "Số hộ nghèo trở thành hộ cận nghèo",
                0 AS "Tái cận nghèo",
                SUM(CASE WHEN "transition.beginningClassify" ILIKE '%Không nghèo%' AND classify = 'Hộ cận nghèo' THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "Phát sinh mới",
                0 AS "Số hộ khác tăng"
            FROM households
            {where_clause}
            GROUP BY "administrative.district", "administrative.commune"
        ) AS subquery
        ORDER BY "District", "Phường/Xã", "Phân tổ";
        """
    elif report_id in [4, 5, 6, 7]:
        target_classify = "Hộ nghèo" if report_id in [4, 5] else "Hộ cận nghèo"
        where_cond = where_clause + f" AND classify = '{target_classify}'"
        col_total = "Tổng số hộ nghèo" if report_id in [4, 5] else "Tổng số hộ cận nghèo"
        return f"""
        SELECT 
            "administrative.district" AS "District",
            "administrative.commune" AS "Phường/Xã",
            COUNT(*) AS "{col_total}",
            SUM(
                (CASE WHEN "deprivation.employment" = true THEN 1 ELSE 0 END) +
                (CASE WHEN "deprivation.dependentPerson" = true THEN 1 ELSE 0 END) +
                (CASE WHEN "deprivation.nutrition" = true THEN 1 ELSE 0 END) +
                (CASE WHEN "deprivation.healthInsurance" = true THEN 1 ELSE 0 END) +
                (CASE WHEN "deprivation.adultEducation" = true THEN 1 ELSE 0 END) +
                (CASE WHEN "deprivation.childSchoolAttendance" = true THEN 1 ELSE 0 END) +
                (CASE WHEN "deprivation.housingQuality" = true THEN 1 ELSE 0 END) +
                (CASE WHEN "deprivation.housingArea" = true THEN 1 ELSE 0 END) +
                (CASE WHEN "deprivation.cleanWater" = true THEN 1 ELSE 0 END) +
                (CASE WHEN "deprivation.hygienicToilet" = true THEN 1 ELSE 0 END) +
                (CASE WHEN "deprivation.telecommunication" = true THEN 1 ELSE 0 END) +
                (CASE WHEN "deprivation.informationAccessAssets" = true THEN 1 ELSE 0 END)
            ) AS "Tổng số thiếu hụt",
            SUM(CASE WHEN "deprivation.employment" = true THEN 1 ELSE 0 END) AS "1. Việc làm",
            SUM(CASE WHEN "deprivation.dependentPerson" = true THEN 1 ELSE 0 END) AS "2. Người phụ thuộc",
            SUM(CASE WHEN "deprivation.nutrition" = true THEN 1 ELSE 0 END) AS "3. Dinh dưỡng",
            SUM(CASE WHEN "deprivation.healthInsurance" = true THEN 1 ELSE 0 END) AS "4. Bảo hiểm y tế",
            SUM(CASE WHEN "deprivation.adultEducation" = true THEN 1 ELSE 0 END) AS "5. Trình độ giáo dục của người lớn",
            SUM(CASE WHEN "deprivation.childSchoolAttendance" = true THEN 1 ELSE 0 END) AS "6. Tình trạng đi học của trẻ em",
            SUM(CASE WHEN "deprivation.housingQuality" = true THEN 1 ELSE 0 END) AS "7. Chất lượng nhà ở",
            SUM(CASE WHEN "deprivation.housingArea" = true THEN 1 ELSE 0 END) AS "8. Diện tích nhà ở",
            SUM(CASE WHEN "deprivation.cleanWater" = true THEN 1 ELSE 0 END) AS "9. Nguồn nước sinh hoạt",
            SUM(CASE WHEN "deprivation.hygienicToilet" = true THEN 1 ELSE 0 END) AS "10. Nhà tiêu hợp vệ sinh",
            SUM(CASE WHEN "deprivation.telecommunication" = true THEN 1 ELSE 0 END) AS "11. Dịch vụ viễn thông",
            SUM(CASE WHEN "deprivation.informationAccessAssets" = true THEN 1 ELSE 0 END) AS "12. Phương tiện tiếp cận thông tin"
        FROM households
        {where_cond}
        GROUP BY "administrative.district", "administrative.commune"
        ORDER BY "administrative.district", "administrative.commune";
        """
    elif report_id == 8:
        return f"""
        SELECT 
            "District", "Phường/Xã", "Phân tổ",
            "Tổng số hộ nghèo", "HN - Hộ DTTS", "HN - Hộ không có khả năng lao động", "HN - Hộ có người có công", "HN - Khác",
            "Tổng số hộ cận nghèo", "CN - Hộ DTTS", "CN - Hộ không có khả năng lao động", "CN - Hộ có người có công", "CN - Khác"
        FROM (
            SELECT 
                "administrative.district" AS "District",
                "administrative.commune" AS "Phường/Xã",
                'Hộ' AS "Phân tổ",
                SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 ELSE 0 END) AS "Tổng số hộ nghèo",
                SUM(CASE WHEN classify = 'Hộ nghèo' AND "family.isDTTS" = true THEN 1 ELSE 0 END) AS "HN - Hộ DTTS",
                SUM(CASE WHEN classify = 'Hộ nghèo' AND "family.hasNoLaborCapacity" = true THEN 1 ELSE 0 END) AS "HN - Hộ không có khả năng lao động",
                SUM(CASE WHEN classify = 'Hộ nghèo' AND "family.hasRevolutionMeritPolicy" = true THEN 1 ELSE 0 END) AS "HN - Hộ có người có công",
                SUM(CASE WHEN classify = 'Hộ nghèo' AND ("family.isDTTS" IS NULL OR "family.isDTTS" = false) AND ("family.hasNoLaborCapacity" IS NULL OR "family.hasNoLaborCapacity" = false) AND ("family.hasRevolutionMeritPolicy" IS NULL OR "family.hasRevolutionMeritPolicy" = false) THEN 1 ELSE 0 END) AS "HN - Khác",
                SUM(CASE WHEN classify = 'Hộ cận nghèo' THEN 1 ELSE 0 END) AS "Tổng số hộ cận nghèo",
                SUM(CASE WHEN classify = 'Hộ cận nghèo' AND "family.isDTTS" = true THEN 1 ELSE 0 END) AS "CN - Hộ DTTS",
                SUM(CASE WHEN classify = 'Hộ cận nghèo' AND "family.hasNoLaborCapacity" = true THEN 1 ELSE 0 END) AS "CN - Hộ không có khả năng lao động",
                SUM(CASE WHEN classify = 'Hộ cận nghèo' AND "family.hasRevolutionMeritPolicy" = true THEN 1 ELSE 0 END) AS "CN - Hộ có người có công",
                SUM(CASE WHEN classify = 'Hộ cận nghèo' AND ("family.isDTTS" IS NULL OR "family.isDTTS" = false) AND ("family.hasNoLaborCapacity" IS NULL OR "family.hasNoLaborCapacity" = false) AND ("family.hasRevolutionMeritPolicy" IS NULL OR "family.hasRevolutionMeritPolicy" = false) THEN 1 ELSE 0 END) AS "CN - Khác"
            FROM households
            {where_clause}
            GROUP BY "administrative.district", "administrative.commune"
            
            UNION ALL
            
            SELECT 
                "administrative.district" AS "District",
                "administrative.commune" AS "Phường/Xã",
                'Nhân khẩu' AS "Phân tổ",
                SUM(CASE WHEN classify = 'Hộ nghèo' THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "Tổng số hộ nghèo",
                SUM(CASE WHEN classify = 'Hộ nghèo' AND "family.isDTTS" = true THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "HN - Hộ DTTS",
                SUM(CASE WHEN classify = 'Hộ nghèo' AND "family.hasNoLaborCapacity" = true THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "HN - Hộ không có khả năng lao động",
                SUM(CASE WHEN classify = 'Hộ nghèo' AND "family.hasRevolutionMeritPolicy" = true THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "HN - Hộ có người có công",
                SUM(CASE WHEN classify = 'Hộ nghèo' AND ("family.isDTTS" IS NULL OR "family.isDTTS" = false) AND ("family.hasNoLaborCapacity" IS NULL OR "family.hasNoLaborCapacity" = false) AND ("family.hasRevolutionMeritPolicy" IS NULL OR "family.hasRevolutionMeritPolicy" = false) THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "HN - Khác",
                SUM(CASE WHEN classify = 'Hộ cận nghèo' THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "Tổng số hộ cận nghèo",
                SUM(CASE WHEN classify = 'Hộ cận nghèo' AND "family.isDTTS" = true THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "CN - Hộ DTTS",
                SUM(CASE WHEN classify = 'Hộ cận nghèo' AND "family.hasNoLaborCapacity" = true THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "CN - Hộ không có khả năng lao động",
                SUM(CASE WHEN classify = 'Hộ cận nghèo' AND "family.hasRevolutionMeritPolicy" = true THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "CN - Hộ có người có công",
                SUM(CASE WHEN classify = 'Hộ cận nghèo' AND ("family.isDTTS" IS NULL OR "family.isDTTS" = false) AND ("family.hasNoLaborCapacity" IS NULL OR "family.hasNoLaborCapacity" = false) AND ("family.hasRevolutionMeritPolicy" IS NULL OR "family.hasRevolutionMeritPolicy" = false) THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "CN - Khác"
            FROM households
            {where_clause}
            GROUP BY "administrative.district", "administrative.commune"
        ) AS subquery
        ORDER BY "District", "Phường/Xã", "Phân tổ";
        """
    elif report_id == 9:
        return f"""
        SELECT 
            "administrative.district" AS "District",
            "administrative.commune" AS "Phường/Xã",
            SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 ELSE 0 END) AS "Tổng số hộ nghèo",
            SUM(CASE WHEN classify = 'Hộ nghèo' AND "family.ethnicity" = 'Kinh' THEN 1 ELSE 0 END) AS "HN - Kinh",
            SUM(CASE WHEN classify = 'Hộ nghèo' AND "family.isDTTS" = true THEN 1 ELSE 0 END) AS "HN - Tổng DTTS",
            SUM(CASE WHEN classify = 'Hộ nghèo' AND "family.ethnicity" = 'Ê đê' THEN 1 ELSE 0 END) AS "HN - Ê đê",
            SUM(CASE WHEN classify = 'Hộ nghèo' AND "family.ethnicity" = 'Mạ' THEN 1 ELSE 0 END) AS "HN - Mạ",
            SUM(CASE WHEN classify = 'Hộ nghèo' AND "family.ethnicity" = 'Mường' THEN 1 ELSE 0 END) AS "HN - Mường",
            SUM(CASE WHEN classify = 'Hộ nghèo' AND "family.ethnicity" = 'Thái' THEN 1 ELSE 0 END) AS "HN - Thái",
            SUM(CASE WHEN classify = 'Hộ nghèo' AND "family.ethnicity" = 'M''Nông' THEN 1 ELSE 0 END) AS "HN - M'Nông",
            SUM(CASE WHEN classify = 'Hộ nghèo' AND "family.ethnicity" = 'Tày' THEN 1 ELSE 0 END) AS "HN - Tày",
            SUM(CASE WHEN classify = 'Hộ nghèo' AND "family.ethnicity" = 'Nùng' THEN 1 ELSE 0 END) AS "HN - Nùng",
            SUM(CASE WHEN classify = 'Hộ nghèo' AND "family.ethnicity" = 'Mông' THEN 1 ELSE 0 END) AS "HN - Mông",
            SUM(CASE WHEN classify = 'Hộ nghèo' AND "family.ethnicity" = 'Dao' THEN 1 ELSE 0 END) AS "HN - Dao",
            SUM(CASE WHEN classify = 'Hộ nghèo' AND "family.ethnicity" NOT IN ('Kinh', 'Ê đê', 'Mạ', 'Mường', 'Thái', 'M''Nông', 'Tày', 'Nùng', 'Mông', 'Dao') THEN 1 ELSE 0 END) AS "HN - Khác",
            SUM(CASE WHEN classify = 'Hộ cận nghèo' THEN 1 ELSE 0 END) AS "Tổng số hộ cận nghèo",
            SUM(CASE WHEN classify = 'Hộ cận nghèo' AND "family.ethnicity" = 'Kinh' THEN 1 ELSE 0 END) AS "CN - Kinh",
            SUM(CASE WHEN classify = 'Hộ cận nghèo' AND "family.isDTTS" = true THEN 1 ELSE 0 END) AS "CN - Tổng DTTS",
            SUM(CASE WHEN classify = 'Hộ cận nghèo' AND "family.ethnicity" = 'Ê đê' THEN 1 ELSE 0 END) AS "CN - Ê đê",
            SUM(CASE WHEN classify = 'Hộ cận nghèo' AND "family.ethnicity" = 'Mạ' THEN 1 ELSE 0 END) AS "CN - Mạ",
            SUM(CASE WHEN classify = 'Hộ cận nghèo' AND "family.ethnicity" = 'Mường' THEN 1 ELSE 0 END) AS "CN - Mường",
            SUM(CASE WHEN classify = 'Hộ cận nghèo' AND "family.ethnicity" = 'Thái' THEN 1 ELSE 0 END) AS "CN - Thái",
            SUM(CASE WHEN classify = 'Hộ cận nghèo' AND "family.ethnicity" = 'M''Nông' THEN 1 ELSE 0 END) AS "CN - M'Nông",
            SUM(CASE WHEN classify = 'Hộ cận nghèo' AND "family.ethnicity" = 'Tày' THEN 1 ELSE 0 END) AS "CN - Tày",
            SUM(CASE WHEN classify = 'Hộ cận nghèo' AND "family.ethnicity" = 'Nùng' THEN 1 ELSE 0 END) AS "CN - Nùng",
            SUM(CASE WHEN classify = 'Hộ cận nghèo' AND "family.ethnicity" = 'Mông' THEN 1 ELSE 0 END) AS "CN - Mông",
            SUM(CASE WHEN classify = 'Hộ cận nghèo' AND "family.ethnicity" = 'Dao' THEN 1 ELSE 0 END) AS "CN - Dao",
            SUM(CASE WHEN classify = 'Hộ cận nghèo' AND "family.ethnicity" NOT IN ('Kinh', 'Ê đê', 'Mạ', 'Mường', 'Thái', 'M''Nông', 'Tày', 'Nùng', 'Mông', 'Dao') THEN 1 ELSE 0 END) AS "CN - Khác"
        FROM households
        {where_clause}
        GROUP BY "administrative.district", "administrative.commune"
        ORDER BY "administrative.district", "administrative.commune";
        """
    elif report_id == 10:
        return f"""
        SELECT 
            "administrative.district" AS "District",
            "administrative.commune" AS "Phường/Xã",
            SUM(CASE WHEN "reason.lackProductionLand" = true THEN 1 ELSE 0 END) AS "1. Thiếu đất sản xuất",
            SUM(CASE WHEN "reason.lackCapital" = true THEN 1 ELSE 0 END) AS "2. Thiếu vốn",
            SUM(CASE WHEN "reason.lackLabor" = true THEN 1 ELSE 0 END) AS "3. Thiếu lao động",
            SUM(CASE WHEN "reason.lackProductionTools" = true THEN 1 ELSE 0 END) AS "4. Thiếu công cụ sản xuất",
            SUM(CASE WHEN "reason.lackProductionKnowledge" = true THEN 1 ELSE 0 END) AS "5. Thiếu kiến thức sản xuất",
            SUM(CASE WHEN "reason.lackLaborSkill" = true THEN 1 ELSE 0 END) AS "6. Thiếu kỹ năng lao động",
            SUM(CASE WHEN "reason.illnessOrAccident" = true THEN 1 ELSE 0 END) AS "7. Ốm đau, tai nạn",
            SUM(CASE WHEN ("reason.lackProductionLand" IS NULL OR "reason.lackProductionLand" = false) AND ("reason.lackCapital" IS NULL OR "reason.lackCapital" = false) AND ("reason.lackLabor" IS NULL OR "reason.lackLabor" = false) AND ("reason.lackProductionTools" IS NULL OR "reason.lackProductionTools" = false) AND ("reason.lackProductionKnowledge" IS NULL OR "reason.lackProductionKnowledge" = false) AND ("reason.lackLaborSkill" IS NULL OR "reason.lackLaborSkill" = false) AND ("reason.illnessOrAccident" IS NULL OR "reason.illnessOrAccident" = false) THEN 1 ELSE 0 END) AS "8. Khác"
        FROM households
        {where_clause}
        GROUP BY "administrative.district", "administrative.commune"
        ORDER BY "administrative.district", "administrative.commune";
        """
    elif report_id == 11:
        return f"""
        SELECT 
            "administrative.district" AS "District",
            "administrative.commune" AS "Phường/Xã",
            SUM(CASE WHEN classify = 'Hộ nghèo' THEN "children.totalCount" ELSE 0 END) AS "1. Tổng số trẻ em hộ nghèo",
            SUM(CASE WHEN classify = 'Hộ nghèo' THEN ("children.lackHealthInsuranceCount" + "children.nutritionDeprivedCount") ELSE 0 END) AS "2. Y tế hộ nghèo",
            SUM(CASE WHEN classify = 'Hộ nghèo' THEN "children.schoolAttendanceDeprivedCount" ELSE 0 END) AS "3. Giáo dục hộ nghèo",
            SUM(CASE WHEN classify = 'Hộ cận nghèo' THEN "children.totalCount" ELSE 0 END) AS "4. Tổng số trẻ em hộ cận nghèo",
            SUM(CASE WHEN classify = 'Hộ cận nghèo' THEN ("children.lackHealthInsuranceCount" + "children.nutritionDeprivedCount") ELSE 0 END) AS "5. Y tế hộ cận nghèo",
            SUM(CASE WHEN classify = 'Hộ cận nghèo' THEN "children.schoolAttendanceDeprivedCount" ELSE 0 END) AS "6. Giáo dục hộ cận nghèo"
        FROM households
        {where_clause}
        GROUP BY "administrative.district", "administrative.commune"
        ORDER BY "administrative.district", "administrative.commune";
        """
    elif report_id in [12, 13]:
        target_classify = 'Hộ nghèo' if report_id == 12 else 'Hộ cận nghèo'
        return f"""
        SELECT 
            "administrative.district" AS "District",
            "administrative.commune" AS "Phường/Xã",
            COUNT(*) AS "Tổng số hộ",
            SUM(CASE WHEN "family.isKinh" = true THEN 1 ELSE 0 END) AS "Hộ Kinh",
            SUM(CASE WHEN "family.isDTTS" = true THEN 1 ELSE 0 END) AS "Hộ DTTS chung",
            SUM(CASE WHEN "family.isDTTC" = true OR "family.coDanTocTaiCho" = 'Có' THEN 1 ELSE 0 END) AS "Hộ DT Tại chỗ",
            SUM(COALESCE("family.numberOfMembers", 1)) AS "Tổng số khẩu",
            SUM(CASE WHEN "family.isKinh" = true THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "Khẩu Kinh",
            SUM(CASE WHEN "family.isDTTS" = true THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "Khẩu DTTS chung",
            SUM(CASE WHEN "family.isDTTC" = true OR "family.coDanTocTaiCho" = 'Có' THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "Khẩu DT Tại chỗ",
            SUM(CASE WHEN classify = '{target_classify}' THEN 1 ELSE 0 END) AS "Tổng số hộ nghèo/cận nghèo",
            SUM(CASE WHEN classify = '{target_classify}' AND "family.isKinh" = true THEN 1 ELSE 0 END) AS "Hộ nghèo/cận nghèo Kinh",
            SUM(CASE WHEN classify = '{target_classify}' AND "family.isDTTS" = true THEN 1 ELSE 0 END) AS "Hộ nghèo/cận nghèo DTTS",
            SUM(CASE WHEN classify = '{target_classify}' AND ("family.isDTTC" = true OR "family.coDanTocTaiCho" = 'Có') THEN 1 ELSE 0 END) AS "Hộ nghèo/cận nghèo DTTC",
            SUM(CASE WHEN classify = '{target_classify}' AND "family.hasRevolutionMeritPolicy" = true THEN 1 ELSE 0 END) AS "Hộ CSCC",
            SUM(CASE WHEN classify = '{target_classify}' AND "family.hasNoLaborCapacity" = true THEN 1 ELSE 0 END) AS "Hộ KCKNLĐ",
            SUM(CASE WHEN classify = '{target_classify}' AND "family.hostGender" = 'Nữ' THEN 1 ELSE 0 END) AS "Chủ hộ là nữ",
            SUM(CASE WHEN classify = '{target_classify}' THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "Tổng số khẩu nghèo/cận nghèo",
            SUM(CASE WHEN classify = '{target_classify}' AND "family.isKinh" = true THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "Khẩu nghèo/cận nghèo Kinh",
            SUM(CASE WHEN classify = '{target_classify}' AND "family.isDTTS" = true THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "Khẩu nghèo/cận nghèo DTTS",
            SUM(CASE WHEN classify = '{target_classify}' AND ("family.isDTTC" = true OR "family.coDanTocTaiCho" = 'Có') THEN COALESCE("family.numberOfMembers", 1) ELSE 0 END) AS "Khẩu nghèo/cận nghèo DTTC"
        FROM households
        {where_clause}
        GROUP BY "administrative.district", "administrative.commune"
        ORDER BY "administrative.district", "administrative.commune";
        """
    elif report_id in [14, 15]:
        target_classify = 'Hộ cận nghèo' if report_id == 14 else 'Hộ nghèo'
        m_where_clause = where_clause.replace('"administrative.year"', 'h."administrative.year"').replace('"administrative.district"', 'h."administrative.district"')
        return f"""
        SELECT 
            m."administrative.district" AS "District",
            m."administrative.commune" AS "Phường/Xã",
            h."member.householdOrder" AS "STT chủ hộ",
            m."member.orderInHousehold" AS "STT thành viên hộ",
            m."member.fullName" AS "Họ tên",
            CASE WHEN m."member.gender" = 'Nam' THEN COALESCE(CAST(m."member.birthYear" AS VARCHAR), m."member.birthDate", '') ELSE '' END AS "Nam",
            CASE WHEN m."member.gender" = 'Nữ' THEN COALESCE(CAST(m."member.birthYear" AS VARCHAR), m."member.birthDate", '') ELSE '' END AS "Nữ",
            m."member.ethnicity" AS "Dân tộc",
            m."member.relationshipToHost" AS "Quan hệ với chủ hộ",
            CASE WHEN h."transition.poorChangeType" = 'Nghèo mới' OR h."transition.nearPoorChangeType" = 'Cận nghèo mới' THEN 'x' ELSE '' END AS "Nghèo mới",
            CASE WHEN h."transition.poorChangeType" = 'Tái nghèo' OR h."transition.nearPoorChangeType" = 'Tái cận nghèo' THEN 'x' ELSE '' END AS "Tái nghèo",
            CASE WHEN h."transition.poorChangeType" = 'Nghèo cũ' OR h."transition.nearPoorChangeType" = 'Cận nghèo cũ' THEN 'x' ELSE '' END AS "Nghèo cũ",
            CASE WHEN h."family.hasRevolutionMeritPolicy" = true THEN 'x' ELSE '' END AS "Hộ CSCC",
            CASE WHEN h."family.isDTTC" = true OR h."family.coDanTocTaiCho" = 'Có' THEN 'x' ELSE '' END AS "Hộ DTTC",
            CASE WHEN h."family.hasNoLaborCapacity" = true THEN 'x' ELSE '' END AS "Hộ KCKNLĐ",
            CASE WHEN h."support.health" = true THEN 'x' ELSE '' END AS "Hỗ trợ y tế",
            CASE WHEN h."support.education" = true THEN 'x' ELSE '' END AS "Hỗ trợ giáo dục",
            CASE WHEN h."support.production" = true THEN 'x' ELSE '' END AS "Hỗ trợ sản xuất",
            CASE WHEN h."support.credit" = true THEN 'x' ELSE '' END AS "Hỗ trợ vay vốn tín dụng",
            CASE WHEN h."support.housing" = true THEN 'x' ELSE '' END AS "Hỗ trợ nhà ở",
            CASE WHEN h."support.other" = true THEN 'x' ELSE '' END AS "Khác"
        FROM members m
        JOIN households h ON m."family.code" = h."family.code" AND m."administrative.year" = h."administrative.year"
        {m_where_clause} AND h.classify = '{target_classify}'
        ORDER BY m."administrative.district", m."administrative.commune", h."member.householdOrder", m."member.orderInHousehold";
        """
    else:
        raise ValueError(f"Biểu mẫu số {report_id} chưa được hỗ trợ.")

def execute_report_query(report_id: int, year: int = 2024, district: str | None = None) -> tuple[pd.DataFrame, str, str]:
    """
    Thực thi câu truy vấn SQL trên DuckDB, thực hiện phân cấp Huyện -> Xã (Hierarchical Rollup),
    tính toán các dòng tổng Huyện và định dạng DataFrame chuẩn biểu mẫu Chính phủ.
    """
    sql = get_report_sql(report_id, year, district)
    title = REPORT_TITLES.get(report_id, f"BÁO CÁO SỐ {report_id}")
    if district:
        title += f" - HUYỆN/THÀNH PHỐ {district.upper()}"
    title += f" NĂM {year}"
    
    with duckdb.connect(str(DB_PATH), read_only=True) as con:
        raw_df = con.execute(sql).df()
        
    # Thực hiện Rollup Phân cấp Huyện -> Xã
    final_rows = []
    districts = raw_df["District"].unique() if "District" in raw_df.columns else []
    
    for d_idx, dist_name in enumerate(districts, 1):
        dist_df = raw_df[raw_df["District"] == dist_name]
        display_dist = f"Huyện {dist_name}" if not any(dist_name.lower().startswith(x) for x in ["huyện", "thành phố", "thị xã"]) else dist_name
        
        if report_id == 1:
            # Tính dòng tổng Huyện cho Báo cáo 1
            sum_ho = dist_df["Số hộ"].sum()
            sum_nk = dist_df["Nhân khẩu"].sum()
            sum_hn = dist_df["Tổng số hộ nghèo"].sum()
            sum_cn = dist_df["Tổng số hộ cận nghèo"].sum()
            sum_nn = dist_df["Tổng số hộ nông, lâm, ngư nghiệp"].sum()
            sum_khn = dist_df["Tổng số khẩu nghèo"].sum()
            sum_kcn = dist_df["Tổng số khẩu cận nghèo"].sum()
            sum_knn = dist_df["Tổng số khẩu nông, lâm, ngư nghiệp"].sum()
            
            final_rows.append({
                "STT": str(d_idx),
                "Phường/Xã": display_dist,
                "Số hộ": sum_ho,
                "Nhân khẩu": sum_nk,
                "Tổng số hộ nghèo": sum_hn,
                "Tỷ lệ hộ nghèo (%)": round(sum_hn * 100.0 / sum_ho, 2) if sum_ho > 0 else 0.0,
                "Tổng số hộ cận nghèo": sum_cn,
                "Tỷ lệ hộ cận nghèo (%)": round(sum_cn * 100.0 / sum_ho, 2) if sum_ho > 0 else 0.0,
                "Tổng số hộ nông, lâm, ngư nghiệp": sum_nn,
                "Tỷ lệ hộ nông, lâm, ngư nghiệp (%)": round(sum_nn * 100.0 / sum_ho, 2) if sum_ho > 0 else 0.0,
                "Tổng số khẩu nghèo": sum_khn,
                "Tỷ lệ khẩu nghèo (%)": round(sum_khn * 100.0 / sum_nk, 2) if sum_nk > 0 else 0.0,
                "Tổng số khẩu cận nghèo": sum_kcn,
                "Tỷ lệ khẩu cận nghèo (%)": round(sum_kcn * 100.0 / sum_nk, 2) if sum_nk > 0 else 0.0,
                "Tổng số khẩu nông, lâm, ngư nghiệp": sum_knn,
                "Tỷ lệ khẩu nông, lâm, ngư nghiệp (%)": round(sum_knn * 100.0 / sum_nk, 2) if sum_nk > 0 else 0.0
            })
            
            # Các dòng Xã
            for c_idx, (_, row) in enumerate(dist_df.iterrows(), 1):
                ho = row["Số hộ"]
                nk = row["Nhân khẩu"]
                hn = row["Tổng số hộ nghèo"]
                cn = row["Tổng số hộ cận nghèo"]
                nn = row["Tổng số hộ nông, lâm, ngư nghiệp"]
                khn = row["Tổng số khẩu nghèo"]
                kcn = row["Tổng số khẩu cận nghèo"]
                knn = row["Tổng số khẩu nông, lâm, ngư nghiệp"]
                
                final_rows.append({
                    "STT": f"{d_idx}.{c_idx}",
                    "Phường/Xã": row["Phường/Xã"],
                    "Số hộ": ho,
                    "Nhân khẩu": nk,
                    "Tổng số hộ nghèo": hn,
                    "Tỷ lệ hộ nghèo (%)": round(hn * 100.0 / ho, 2) if ho > 0 else 0.0,
                    "Tổng số hộ cận nghèo": cn,
                    "Tỷ lệ hộ cận nghèo (%)": round(cn * 100.0 / ho, 2) if ho > 0 else 0.0,
                    "Tổng số hộ nông, lâm, ngư nghiệp": nn,
                    "Tỷ lệ hộ nông, lâm, ngư nghiệp (%)": round(nn * 100.0 / ho, 2) if ho > 0 else 0.0,
                    "Tổng số khẩu nghèo": khn,
                    "Tỷ lệ khẩu nghèo (%)": round(khn * 100.0 / nk, 2) if nk > 0 else 0.0,
                    "Tổng số khẩu cận nghèo": kcn,
                    "Tỷ lệ khẩu cận nghèo (%)": round(kcn * 100.0 / nk, 2) if nk > 0 else 0.0,
                    "Tổng số khẩu nông, lâm, ngư nghiệp": knn,
                    "Tỷ lệ khẩu nông, lâm, ngư nghiệp (%)": round(knn * 100.0 / nk, 2) if nk > 0 else 0.0
                })
                
        elif report_id in [2, 3]:
            # Báo cáo 2 & 3 (Hỗ trợ 2 dòng Phân tổ: Hộ và Nhân khẩu)
            for phan_to in ["Hộ", "Nhân khẩu"]:
                pt_df = dist_df[dist_df["Phân tổ"] == phan_to]
                if pt_df.empty:
                    continue
                
                col_prefix = "Tổng số hộ nghèo" if report_id == 2 else "Tổng số hộ cận nghèo"
                col_dk = f"{col_prefix} đầu kỳ"
                col_ck = f"{col_prefix} cuối kỳ"
                col_tro_thanh = "Trở thành hộ cận nghèo" if report_id == 2 else "Trở thành hộ nghèo"
                col_bs = "Số hộ cận nghèo trở thành" if report_id == 2 else "Số hộ nghèo trở thành hộ cận nghèo"
                col_tai = "Tái nghèo" if report_id == 2 else "Tái cận nghèo"
                
                sum_dk = pt_df[col_dk].sum()
                sum_tt = pt_df[col_tro_thanh].sum()
                sum_vc = pt_df["Vượt chuẩn cận nghèo"].sum()
                sum_kg = pt_df["Số hộ khác giảm"].sum()
                sum_bs = pt_df[col_bs].sum()
                sum_tai = pt_df[col_tai].sum()
                sum_ps = pt_df["Phát sinh mới"].sum()
                sum_kt = pt_df["Số hộ khác tăng"].sum()
                sum_ck = pt_df[col_ck].sum()
                
                final_rows.append({
                    "STT": str(d_idx),
                    "Phường/Xã": display_dist,
                    "Phân tổ": phan_to,
                    col_dk: sum_dk,
                    col_tro_thanh: sum_tt,
                    "Vượt chuẩn cận nghèo": sum_vc,
                    "Số hộ khác giảm": sum_kg,
                    col_bs: sum_bs,
                    col_tai: sum_tai,
                    "Phát sinh mới": sum_ps,
                    "Số hộ khác tăng": sum_kt,
                    col_ck: sum_ck
                })
                
                # Các dòng Xã
                for c_idx, (_, row) in enumerate(pt_df.iterrows(), 1):
                    final_rows.append({
                        "STT": f"{d_idx}.{c_idx}",
                        "Phường/Xã": row["Phường/Xã"],
                        "Phân tổ": phan_to,
                        col_dk: row[col_dk],
                        col_tro_thanh: row[col_tro_thanh],
                        "Vượt chuẩn cận nghèo": row["Vượt chuẩn cận nghèo"],
                        "Số hộ khác giảm": row["Số hộ khác giảm"],
                        col_bs: row[col_bs],
                        col_tai: row[col_tai],
                        "Phát sinh mới": row["Phát sinh mới"],
                        "Số hộ khác tăng": row["Số hộ khác tăng"],
                        col_ck: row[col_ck]
                    })
                    
        elif report_id in [4, 6]:
            # Báo cáo 4 & 6 (16 cột đếm tổng)
            col_total = "Tổng số hộ nghèo" if report_id == 4 else "Tổng số hộ cận nghèo"
            cols_to_sum = [col_total, "Tổng số thiếu hụt", "1. Việc làm", "2. Người phụ thuộc", "3. Dinh dưỡng", "4. Bảo hiểm y tế", "5. Trình độ giáo dục của người lớn", "6. Tình trạng đi học của trẻ em", "7. Chất lượng nhà ở", "8. Diện tích nhà ở", "9. Nguồn nước sinh hoạt", "10. Nhà tiêu hợp vệ sinh", "11. Dịch vụ viễn thông", "12. Phương tiện tiếp cận thông tin"]
            dist_row = {"STT": str(d_idx), "Phường/Xã": display_dist}
            for col in cols_to_sum:
                dist_row[col] = dist_df[col].sum()
            final_rows.append(dist_row)
            
            for c_idx, (_, row) in enumerate(dist_df.iterrows(), 1):
                soc_row = {"STT": f"{d_idx}.{c_idx}", "Phường/Xã": row["Phường/Xã"]}
                for col in cols_to_sum:
                    soc_row[col] = row[col]
                final_rows.append(soc_row)
                
        elif report_id in [5, 7]:
            # Báo cáo 5 & 7 (15 cột tỷ lệ %)
            col_total = "Tổng số hộ nghèo" if report_id == 5 else "Tổng số hộ cận nghèo"
            dep_cols = ["1. Việc làm", "2. Người phụ thuộc", "3. Dinh dưỡng", "4. Bảo hiểm y tế", "5. Trình độ giáo dục của người lớn", "6. Tình trạng đi học của trẻ em", "7. Chất lượng nhà ở", "8. Diện tích nhà ở", "9. Nguồn nước sinh hoạt", "10. Nhà tiêu hợp vệ sinh", "11. Dịch vụ viễn thông", "12. Phương tiện tiếp cận thông tin"]
            sum_h = dist_df[col_total].sum()
            dist_row = {"STT": str(d_idx), "Phường/Xã": display_dist, col_total: sum_h}
            for col in dep_cols:
                sum_dep = dist_df[col].sum()
                dist_row[f"{col} (%)"] = round(sum_dep * 100.0 / sum_h, 2) if sum_h > 0 else 0.0
            final_rows.append(dist_row)
            
            for c_idx, (_, row) in enumerate(dist_df.iterrows(), 1):
                h_val = row[col_total]
                soc_row = {"STT": f"{d_idx}.{c_idx}", "Phường/Xã": row["Phường/Xã"], col_total: h_val}
                for col in dep_cols:
                    dep_val = row[col]
                    soc_row[f"{col} (%)"] = round(dep_val * 100.0 / h_val, 2) if h_val > 0 else 0.0
                final_rows.append(soc_row)

        elif report_id == 8:
            # Báo cáo 8 (Phân tổ Hộ và Nhân khẩu, 12 cột)
            for phan_to in ["Hộ", "Nhân khẩu"]:
                pt_df = dist_df[dist_df["Phân tổ"] == phan_to]
                if pt_df.empty:
                    continue
                cols = ["Tổng số hộ nghèo", "HN - Hộ DTTS", "HN - Hộ không có khả năng lao động", "HN - Hộ có người có công", "HN - Khác", "Tổng số hộ cận nghèo", "CN - Hộ DTTS", "CN - Hộ không có khả năng lao động", "CN - Hộ có người có công", "CN - Khác"]
                dist_row = {"STT": str(d_idx), "Phường/Xã": display_dist, "Phân tổ": phan_to}
                for col in cols:
                    dist_row[col] = pt_df[col].sum()
                final_rows.append(dist_row)
                
                for c_idx, (_, row) in enumerate(pt_df.iterrows(), 1):
                    soc_row = {"STT": f"{d_idx}.{c_idx}", "Phường/Xã": row["Phường/Xã"], "Phân tổ": phan_to}
                    for col in cols:
                        soc_row[col] = row[col]
                    final_rows.append(soc_row)

        elif report_id == 9:
            # Báo cáo 9 (28 cột dân tộc)
            cols = [c for c in dist_df.columns if c not in ["District", "Phường/Xã"]]
            dist_row = {"STT": str(d_idx), "Phường/Xã": display_dist}
            for col in cols:
                dist_row[col] = dist_df[col].sum()
            final_rows.append(dist_row)
            
            for c_idx, (_, row) in enumerate(dist_df.iterrows(), 1):
                soc_row = {"STT": f"{d_idx}.{c_idx}", "Phường/Xã": row["Phường/Xã"]}
                for col in cols:
                    soc_row[col] = row[col]
                final_rows.append(soc_row)

        elif report_id == 10:
            # Báo cáo 10 (10 cột nguyên nhân nghèo)
            cols = [c for c in dist_df.columns if c not in ["District", "Phường/Xã"]]
            dist_row = {"STT": str(d_idx), "Phường/Xã": display_dist}
            for col in cols:
                dist_row[col] = dist_df[col].sum()
            final_rows.append(dist_row)
            
            for c_idx, (_, row) in enumerate(dist_df.iterrows(), 1):
                soc_row = {"STT": f"{d_idx}.{c_idx}", "Phường/Xã": row["Phường/Xã"]}
                for col in cols:
                    soc_row[col] = row[col]
                final_rows.append(soc_row)

        elif report_id == 11:
            # Báo cáo 11 (6 cột tổng)
            cols = ["1. Tổng số trẻ em hộ nghèo", "2. Y tế hộ nghèo", "3. Giáo dục hộ nghèo", "4. Tổng số trẻ em hộ cận nghèo", "5. Y tế hộ cận nghèo", "6. Giáo dục hộ cận nghèo"]
            dist_row = {"STT": str(d_idx), "Phường/Xã": display_dist}
            for col in cols:
                dist_row[col] = dist_df[col].sum()
            final_rows.append(dist_row)
            
            for c_idx, (_, row) in enumerate(dist_df.iterrows(), 1):
                soc_row = {"STT": f"{d_idx}.{c_idx}", "Phường/Xã": row["Phường/Xã"]}
                for col in cols:
                    soc_row[col] = row[col]
                final_rows.append(soc_row)

        elif report_id in [12, 13]:
            # Báo cáo 12, 13 (22 cột + tỷ lệ)
            cols_sum = ["Tổng số hộ", "Hộ Kinh", "Hộ DTTS chung", "Hộ DT Tại chỗ", "Tổng số khẩu", "Khẩu Kinh", "Khẩu DTTS chung", "Khẩu DT Tại chỗ", "Tổng số hộ nghèo/cận nghèo", "Hộ nghèo/cận nghèo Kinh", "Hộ nghèo/cận nghèo DTTS", "Hộ nghèo/cận nghèo DTTC", "Hộ CSCC", "Hộ KCKNLĐ", "Chủ hộ là nữ", "Tổng số khẩu nghèo/cận nghèo", "Khẩu nghèo/cận nghèo Kinh", "Khẩu nghèo/cận nghèo DTTS", "Khẩu nghèo/cận nghèo DTTC"]
            
            dist_row = {"STT": str(d_idx), "Phường/Xã": display_dist}
            for col in cols_sum:
                dist_row[col] = dist_df[col].sum()
            
            # Tính tỷ lệ Huyện
            tsh = dist_row["Tổng số hộ"]
            ts_dtts = dist_row["Hộ DTTS chung"]
            ts_dttc = dist_row["Hộ DT Tại chỗ"]
            dist_row["Tỷ lệ (%)"] = round(dist_row["Tổng số hộ nghèo/cận nghèo"] * 100.0 / tsh, 2) if tsh > 0 else 0.0
            dist_row["Tỷ lệ DTTS chung (%)"] = round(dist_row["Hộ nghèo/cận nghèo DTTS"] * 100.0 / ts_dtts, 2) if ts_dtts > 0 else 0.0
            dist_row["Tỷ lệ DTTSTC (%)"] = round(dist_row["Hộ nghèo/cận nghèo DTTC"] * 100.0 / ts_dttc, 2) if ts_dttc > 0 else 0.0
            
            final_rows.append(dist_row)
            
            for c_idx, (_, row) in enumerate(dist_df.iterrows(), 1):
                soc_row = {"STT": f"{d_idx}.{c_idx}", "Phường/Xã": row["Phường/Xã"]}
                for col in cols_sum:
                    soc_row[col] = row[col]
                    
                tsh = soc_row["Tổng số hộ"]
                ts_dtts = soc_row["Hộ DTTS chung"]
                ts_dttc = soc_row["Hộ DT Tại chỗ"]
                soc_row["Tỷ lệ (%)"] = round(soc_row["Tổng số hộ nghèo/cận nghèo"] * 100.0 / tsh, 2) if tsh > 0 else 0.0
                soc_row["Tỷ lệ DTTS chung (%)"] = round(soc_row["Hộ nghèo/cận nghèo DTTS"] * 100.0 / ts_dtts, 2) if ts_dtts > 0 else 0.0
                soc_row["Tỷ lệ DTTSTC (%)"] = round(soc_row["Hộ nghèo/cận nghèo DTTC"] * 100.0 / ts_dttc, 2) if ts_dttc > 0 else 0.0
                
                final_rows.append(soc_row)

        elif report_id in [14, 15]:
            # Báo cáo 14, 15 (Danh sách chi tiết)
            communes = dist_df["Phường/Xã"].unique() if "Phường/Xã" in dist_df.columns else []
            for commune in communes:
                # Add commune header row
                commune_df = dist_df[dist_df["Phường/Xã"] == commune]
                header_row = {"STT chủ hộ": str(commune).upper(), "is_commune_header": True}
                for col in commune_df.columns:
                    if col not in ["District", "Phường/Xã", "STT chủ hộ", "is_commune_header"]:
                        header_row[col] = ""
                final_rows.append(header_row)
                
                for _, row in commune_df.iterrows():
                    soc_row = {k: v for k, v in row.items() if k not in ["District", "Phường/Xã"]}
                    soc_row["is_commune_header"] = False
                    final_rows.append(soc_row)

    df_out = pd.DataFrame(final_rows)
    return df_out, sql, title
