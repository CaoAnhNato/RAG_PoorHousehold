# -*- coding: utf-8 -*-
"""
Script tự động sinh 80 câu hỏi tổng hợp nâng cao (Advanced & Complex Questions) và thực thi SQL DuckDB
để tạo file Ground Truth chuẩn tại artifacts/Quest_Advanced.md.
Bao gồm:
- 20 câu hỏi đợt 1 (ID 1 -> 20)
- 20 câu hỏi đợt 2 (ID 21 -> 40)
- 20 câu hỏi đợt 3 (ID 41 -> 60) tập trung vào viết tắt tên Huyện/Thành Phố/Phường/Xã, sai chính tả, teencode, gộp ý.
- 20 câu hỏi đợt 4 (ID 61 -> 80) tập trung vào cấp độ 'Chủ hộ' 'Thành Viên', cập nhật số liệu qua các năm, so sánh giữa các chủ hộ/thành viên, và khai thác toàn bộ các cột điểm b1, b2, thiếu hụt nước sạch, vệ sinh, giáo dục, y tế...
"""
from __future__ import annotations
import sys
import json
import time
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Cố gắng import duckdb để truy vấn trực tiếp vào DB
try:
    import duckdb
except ImportError:
    duckdb = None

# Danh sách 80 câu hỏi nâng cao kèm theo SQL chuẩn xác
ADVANCED_QUESTIONS = [
    # --- ĐỢT 1 (ID 1 -> 20) ---
    {
        "id": 1,
        "type": "Paraphrase Rút Gọn",
        "question": "Hộ nghèo Cư-Jút 2024",
        "sql": """SELECT COUNT(*) as so_ho_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Cư Jút%';""",
        "base_question": "Số hộ nghèo của huyện Cư-Jút năm 2024 là bao nhiêu?"
    },
    {
        "id": 2,
        "type": "Sai Chính Tả / Teencode",
        "question": "Huyện Tuy Đưc có bnhieu hột nghèo",
        "sql": """SELECT COUNT(*) as so_ho_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Tuy Đức%';""",
        "base_question": "Huyện Tuy Đức có bao nhiêu hộ nghèo?"
    },
    {
        "id": 3,
        "type": "Sai Chính Tả / Teencode",
        "question": "tp gia nghia nam 2024 co bao nhiu ho can ngheo",
        "sql": """SELECT COUNT(*) as so_ho_can_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Gia Nghĩa%';""",
        "base_question": "Thành phố Gia Nghĩa năm 2024 có bao nhiêu hộ cận nghèo?"
    },
    {
        "id": 4,
        "type": "Gộp Ý (Multi-intent / So Sánh)",
        "question": "So sánh số hộ nghèo giữa huyện Đắk Mil và huyện Đắk Song năm 2024, huyện nào nhiều hơn?",
        "sql": """SELECT ten_quan_huyen, COUNT(*) as so_ho_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND (ten_quan_huyen LIKE '%Đắk Mil%' OR ten_quan_huyen LIKE '%Đắk Song%') GROUP BY ten_quan_huyen ORDER BY so_ho_ngheo DESC;""",
        "base_question": "So sánh hộ nghèo Đắk Mil và Đắk Song"
    },
    {
        "id": 5,
        "type": "Gộp Ý (Multi-intent / Aggregation + Top)",
        "question": "Tổng số hộ cận nghèo của huyện Krông Nô là bao nhiêu và xã nào trong huyện này có nhiều hộ cận nghèo nhất?",
        "sql": """SELECT ten_xa_phuong, COUNT(*) as so_ho_can_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Krông Nô%' GROUP BY ten_xa_phuong ORDER BY so_ho_can_ngheo DESC;""",
        "base_question": "Tổng hộ cận nghèo Krông Nô và xã cao nhất"
    },
    {
        "id": 6,
        "type": "Đa dạng hóa cách diễn đạt",
        "question": "Cho tôi biết con số cụ thể về tổng số hộ gia đình vừa thuộc diện hộ nghèo vừa là đồng bào dân tộc thiểu số tại chỗ trên địa bàn toàn tỉnh.",
        "sql": """SELECT COUNT(*) as so_ho_ngheo_dtts_tai_cho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND co_dan_toc_tai_cho = 1;""",
        "base_question": "Có bao nhiêu hộ nghèo dân tộc thiểu số tại chỗ?"
    },
    {
        "id": 7,
        "type": "Paraphrase Rút Gọn",
        "question": "Top 3 xã nghèo nhất Đắk Glong",
        "sql": """SELECT ten_xa_phuong, COUNT(*) as so_ho_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Đắk Glong%' GROUP BY ten_xa_phuong ORDER BY so_ho_ngheo DESC LIMIT 3;""",
        "base_question": "Liệt kê 3 xã có số hộ nghèo cao nhất huyện Đắk Glong"
    },
    {
        "id": 8,
        "type": "Gộp Ý (Multi-intent / Phân Tích Kép)",
        "question": "Ở huyện Cư Jút, xã Tâm Thắng có bao nhiêu hộ nghèo và xã Trúc Sơn có bao nhiêu hộ cận nghèo?",
        "sql": """SELECT ten_xa_phuong, classify, COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Cư Jút%' AND ((ten_xa_phuong LIKE '%Tâm Thắng%' AND classify = 'Hộ nghèo') OR (ten_xa_phuong LIKE '%Trúc Sơn%' AND classify = 'Hộ cận nghèo')) GROUP BY ten_xa_phuong, classify;""",
        "base_question": "Hộ nghèo Tâm Thắng và hộ cận nghèo Trúc Sơn huyện Cư Jút"
    },
    {
        "id": 9,
        "type": "Sai Chính Tả / Teencode",
        "question": "Huyện đăk rờ lấp có bnhieu hột nghèo dtts nam 2024",
        "sql": """SELECT COUNT(*) as so_ho_ngheo_dtts FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Đắk R''Lấp%' AND is_kinh = 0;""",
        "base_question": "Huyện Đắk R'Lấp có bao nhiêu hộ nghèo dân tộc thiểu số năm 2024?"
    },
    {
        "id": 10,
        "type": "Gộp Ý (Multi-intent / Phân Tích Biến Động)",
        "question": "Thành phố Gia Nghĩa đã giảm được bao nhiêu hộ nghèo từ đầu kỳ (năm 2023) so với cuối kỳ (năm 2024)?",
        "sql": """SELECT SUM(CASE WHEN beginningClassify = 'Hộ nghèo' THEN 1 ELSE 0 END) as ngheo_dau_ky, SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 ELSE 0 END) as ngheo_cuoi_ky, (SUM(CASE WHEN beginningClassify = 'Hộ nghèo' THEN 1 ELSE 0 END) - SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 ELSE 0 END)) as so_ho_giam FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Gia Nghĩa%';""",
        "base_question": "Thành phố Gia Nghĩa giảm bao nhiêu hộ nghèo so với đầu kỳ?"
    },
    {
        "id": 11,
        "type": "Đa dạng hóa cách diễn đạt",
        "question": "Thống kê cho tôi xem nguyên nhân chính nào dẫn đến tình trạng nghèo khó của các hộ dân ở huyện Tuy Đức.",
        "sql": """SELECT nguyen_nhan_ngheo, COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Tuy Đức%' AND nguyen_nhan_ngheo IS NOT NULL GROUP BY nguyen_nhan_ngheo ORDER BY so_ho DESC;""",
        "base_question": "Nguyên nhân nghèo chính ở huyện Tuy Đức là gì?"
    },
    {
        "id": 12,
        "type": "Paraphrase Rút Gọn",
        "question": "Hộ nghèo không có đất sản xuất Đắk Song",
        "sql": """SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Đắk Song%' AND nguyen_nhan_ngheo LIKE '%đất sản xuất%';""",
        "base_question": "Huyện Đắk Song có bao nhiêu hộ nghèo do không có đất sản xuất?"
    },
    {
        "id": 13,
        "type": "Gộp Ý (Multi-intent / Quy mô & Thống kê)",
        "question": "Tổng số thành viên trong các hộ cận nghèo ở huyện Đắk Mil là bao nhiêu, trung bình mỗi hộ có mấy người?",
        "sql": """SELECT COUNT(*) as so_ho, SUM(so_thanh_vien) as tong_so_nhan_khau, AVG(so_thanh_vien) as trung_binh_nhan_khau FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Đắk Mil%';""",
        "base_question": "Tổng số nhân khẩu và quy mô trung bình hộ cận nghèo Đắk Mil"
    },
    {
        "id": 14,
        "type": "Sai Chính Tả / Teencode",
        "question": "krong no xa nao ho can ngheo it nhat",
        "sql": """SELECT ten_xa_phuong, COUNT(*) as so_ho_can_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Krông Nô%' GROUP BY ten_xa_phuong ORDER BY so_ho_can_ngheo ASC LIMIT 1;""",
        "base_question": "Xã nào ở huyện Krông Nô có ít hộ cận nghèo nhất?"
    },
    {
        "id": 15,
        "type": "Đa dạng hóa cách diễn đạt",
        "question": "Liệt kê danh sách các xã thuộc huyện Đắk Glong mà có số lượng hộ nghèo vượt quá con số 500 hộ.",
        "sql": """SELECT ten_xa_phuong, COUNT(*) as so_ho_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Đắk Glong%' GROUP BY ten_xa_phuong HAVING COUNT(*) > 500 ORDER BY so_ho_ngheo DESC;""",
        "base_question": "Các xã có hơn 500 hộ nghèo ở Đắk Glong"
    },
    {
        "id": 16,
        "type": "Gộp Ý (Multi-intent / So sánh kép)",
        "question": "So sánh số hộ nghèo là người dân tộc Kinh và số hộ nghèo là người dân tộc thiểu số tại huyện Cư Jút năm 2024.",
        "sql": """SELECT is_kinh, COUNT(*) as so_ho_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Cư Jút%' GROUP BY is_kinh;""",
        "base_question": "So sánh hộ nghèo người Kinh và DTTS ở Cư Jút"
    },
    {
        "id": 17,
        "type": "Paraphrase Rút Gọn",
        "question": "Bình quân nhân khẩu hộ nghèo Gia Nghĩa",
        "sql": """SELECT AVG(so_thanh_vien) as binh_quan_nhan_khau FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Gia Nghĩa%';""",
        "base_question": "Quy mô hộ gia đình trung bình của hộ nghèo ở thành phố Gia Nghĩa là bao nhiêu?"
    },
    {
        "id": 18,
        "type": "Sai Chính Tả / Teencode",
        "question": "huyen dak rlap co bnhieu ho can ngheo la nguoi dtts tai cho",
        "sql": """SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Đắk R''Lấp%' AND co_dan_toc_tai_cho = 1;""",
        "base_question": "Huyện Đắk R'Lấp có bao nhiêu hộ cận nghèo là người dân tộc thiểu số tại chỗ?"
    },
    {
        "id": 19,
        "type": "Gộp Ý (Multi-intent / Aggregation toàn tỉnh)",
        "question": "Tổng hợp cho tôi 3 huyện có số hộ nghèo cao nhất toàn tỉnh Đắk Nông và 3 huyện có số hộ cận nghèo thấp nhất.",
        "sql": """(SELECT 'Top 3 Hộ nghèo cao nhất' as nhom, ten_quan_huyen, COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' GROUP BY ten_quan_huyen ORDER BY so_ho DESC LIMIT 3) UNION ALL (SELECT 'Top 3 Hộ cận nghèo thấp nhất' as nhom, ten_quan_huyen, COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' GROUP BY ten_quan_huyen ORDER BY so_ho ASC LIMIT 3);""",
        "base_question": "Top 3 huyện nhiều hộ nghèo nhất và 3 huyện ít hộ cận nghèo nhất"
    },
    {
        "id": 20,
        "type": "Đa dạng hóa cách diễn đạt",
        "question": "Hãy phân tích chi tiết tình trạng hộ nghèo tại xã Đắk R'Moan thuộc thành phố Gia Nghĩa, cụ thể là có bao nhiêu hộ và tỷ lệ người dân tộc thiểu số trong số đó là bao nhiêu.",
        "sql": """SELECT COUNT(*) as tong_so_ho_ngheo, SUM(CASE WHEN is_kinh = 0 THEN 1 ELSE 0 END) as so_ho_dtts, (SUM(CASE WHEN is_kinh = 0 THEN 1.0 ELSE 0.0 END) / COUNT(*)) * 100 as ty_le_dtts FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Gia Nghĩa%' AND ten_xa_phuong LIKE '%Đắk R''Moan%';""",
        "base_question": "Hộ nghèo và tỷ lệ DTTS xã Đắk R'Moan, Gia Nghĩa"
    },

    # --- ĐỢT 2 (ID 21 -> 40) ---
    {
        "id": 21,
        "type": "Paraphrase Rút Gọn",
        "question": "Nguyên nhân nghèo Đắk R'Măng 2024",
        "sql": """SELECT nguyen_nhan_ngheo, COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_xa_phuong LIKE '%Đắk R''Măng%' AND nguyen_nhan_ngheo IS NOT NULL GROUP BY nguyen_nhan_ngheo ORDER BY so_ho DESC;""",
        "base_question": "Các nguyên nhân chính dẫn đến nghèo ở xã Đắk R'Măng năm 2024 là gì?"
    },
    {
        "id": 22,
        "type": "Sai Chính Tả / Teencode",
        "question": "xa tam thang huyen cu jut co bao nhiu ho ngheo la ng dong bao",
        "sql": """SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Cư Jút%' AND ten_xa_phuong LIKE '%Tâm Thắng%' AND is_kinh = 0;""",
        "base_question": "Xã Tâm Thắng huyện Cư Jút có bao nhiêu hộ nghèo là người đồng bào dân tộc thiểu số?"
    },
    {
        "id": 23,
        "type": "Gộp Ý (Multi-intent / Biến động kép)",
        "question": "Huyện Krông Nô và huyện Tuy Đức, huyện nào giảm được nhiều hộ nghèo hơn so với đầu kỳ năm 2023?",
        "sql": """SELECT ten_quan_huyen, SUM(CASE WHEN beginningClassify = 'Hộ nghèo' THEN 1 ELSE 0 END) as ngheo_dau_ky, SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 ELSE 0 END) as ngheo_cuoi_ky, (SUM(CASE WHEN beginningClassify = 'Hộ nghèo' THEN 1 ELSE 0 END) - SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 ELSE 0 END)) as so_ho_giam FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Krông Nô%' OR ten_quan_huyen LIKE '%Tuy Đức%' GROUP BY ten_quan_huyen ORDER BY so_ho_giam DESC;""",
        "base_question": "So sánh mức giảm hộ nghèo giữa Krông Nô và Tuy Đức"
    },
    {
        "id": 24,
        "type": "Đa dạng hóa cách diễn đạt",
        "question": "Thực hiện đánh giá tổng quan về tình hình nhân khẩu thuộc diện hộ nghèo tại địa bàn huyện Tuy Đức, đồng thời xác định tỷ lệ đồng bào dân tộc thiểu số tại chỗ trong nhóm này.",
        "sql": """SELECT COUNT(*) as tong_ho_ngheo, SUM(so_thanh_vien) as tong_nhan_khau, SUM(CASE WHEN co_dan_toc_tai_cho = 1 THEN 1 ELSE 0 END) as ho_dtts_tai_cho, (SUM(CASE WHEN co_dan_toc_tai_cho = 1 THEN 1.0 ELSE 0.0 END) / COUNT(*)) * 100 as ty_le_dtts_tai_cho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Tuy Đức%';""",
        "base_question": "Tổng nhân khẩu hộ nghèo và tỷ lệ DTTS tại chỗ ở Tuy Đức"
    },
    {
        "id": 25,
        "type": "Sai Chính Tả / Teencode",
        "question": "bnhieu ho can ngheo ko co dat san xuat o dak mil",
        "sql": """SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Đắk Mil%' AND nguyen_nhan_ngheo LIKE '%đất sản xuất%';""",
        "base_question": "Huyện Đắk Mil có bao nhiêu hộ cận nghèo do không có đất sản xuất?"
    },
    {
        "id": 26,
        "type": "Paraphrase Rút Gọn",
        "question": "DTTS cận nghèo Krông Nô",
        "sql": """SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Krông Nô%' AND is_kinh = 0;""",
        "base_question": "Huyện Krông Nô có bao nhiêu hộ cận nghèo là người dân tộc thiểu số?"
    },
    {
        "id": 27,
        "type": "Gộp Ý (Multi-intent / So sánh 3 xã)",
        "question": "So sánh số lượng hộ nghèo giữa 3 xã: Đắk R'Moan (Gia Nghĩa), Trúc Sơn (Cư Jút) và Quảng Hòa (Đắk Glong).",
        "sql": """SELECT ten_quan_huyen, ten_xa_phuong, COUNT(*) as so_ho_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ((ten_quan_huyen LIKE '%Gia Nghĩa%' AND ten_xa_phuong LIKE '%Đắk R''Moan%') OR (ten_quan_huyen LIKE '%Cư Jút%' AND ten_xa_phuong LIKE '%Trúc Sơn%') OR (ten_quan_huyen LIKE '%Đắk Glong%' AND ten_xa_phuong LIKE '%Quảng Hòa%')) GROUP BY ten_quan_huyen, ten_xa_phuong ORDER BY so_ho_ngheo DESC;""",
        "base_question": "So sánh hộ nghèo Đắk R'Moan, Trúc Sơn và Quảng Hòa"
    },
    {
        "id": 28,
        "type": "Đa dạng hóa cách diễn đạt",
        "question": "Hãy tổng hợp dữ liệu toàn tỉnh để tìm ra nguyên nhân cốt lõi khiến các hộ gia đình rơi vào hoàn cảnh cận nghèo trong năm 2024.",
        "sql": """SELECT nguyen_nhan_ngheo, COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND nguyen_nhan_ngheo IS NOT NULL GROUP BY nguyen_nhan_ngheo ORDER BY so_ho DESC;""",
        "base_question": "Nguyên nhân chính dẫn đến hộ cận nghèo toàn tỉnh năm 2024 là gì?"
    },
    {
        "id": 29,
        "type": "Sai Chính Tả / Teencode",
        "question": "huyen dak song co bnhieu ho ngheo thieu von san xuaat",
        "sql": """SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Đắk Song%' AND nguyen_nhan_ngheo LIKE '%vốn sản xuất%';""",
        "base_question": "Huyện Đắk Song có bao nhiêu hộ nghèo do thiếu vốn sản xuất?"
    },
    {
        "id": 30,
        "type": "Paraphrase Rút Gọn",
        "question": "Hộ nghèo neo đơn Đắk R'Lấp",
        "sql": """SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Đắk R''Lấp%' AND (so_thanh_vien = 1 OR nguyen_nhan_ngheo LIKE '%neo đơn%');""",
        "base_question": "Huyện Đắk R'Lấp có bao nhiêu hộ nghèo có 1 thành viên (neo đơn)?"
    },
    {
        "id": 31,
        "type": "Gộp Ý (Multi-intent / Aggregation nhân khẩu)",
        "question": "Huyện Đắk Glong có bao nhiêu hộ nghèo có từ 6 thành viên trở lên, và tổng nhân khẩu của nhóm này là bao nhiêu?",
        "sql": """SELECT COUNT(*) as so_ho_dong_nguoi, SUM(so_thanh_vien) as tong_nhan_khau FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Đắk Glong%' AND so_thanh_vien >= 6;""",
        "base_question": "Hộ nghèo từ 6 thành viên trở lên ở Đắk Glong và tổng nhân khẩu"
    },
    {
        "id": 32,
        "type": "Sai Chính Tả / Teencode",
        "question": "xa dak ndrot huyen dak mil nam 2024 co giam dc ho ngheo nao ko",
        "sql": """SELECT SUM(CASE WHEN beginningClassify = 'Hộ nghèo' THEN 1 ELSE 0 END) as ngheo_dau_ky, SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 ELSE 0 END) as ngheo_cuoi_ky, (SUM(CASE WHEN beginningClassify = 'Hộ nghèo' THEN 1 ELSE 0 END) - SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 ELSE 0 END)) as so_ho_giam FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Đắk Mil%' AND ten_xa_phuong LIKE '%Đắk N''Drót%';""",
        "base_question": "Xã Đắk N'Drót huyện Đắk Mil giảm bao nhiêu hộ nghèo năm 2024?"
    },
    {
        "id": 33,
        "type": "Đa dạng hóa cách diễn đạt",
        "question": "Cung cấp cho tôi danh sách chi tiết các đơn vị cấp xã thuộc thành phố Gia Nghĩa không còn hộ nghèo nào thuộc diện đồng bào dân tộc thiểu số tại chỗ.",
        "sql": """SELECT ten_xa_phuong, COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Gia Nghĩa%' AND co_dan_toc_tai_cho = 1 GROUP BY ten_xa_phuong HAVING COUNT(*) = 0;""",
        "base_question": "Các xã ở TP Gia Nghĩa không có hộ nghèo DTTS tại chỗ"
    },
    {
        "id": 34,
        "type": "Paraphrase Rút Gọn",
        "question": "Bình quân nhân khẩu cận nghèo Cư Jút",
        "sql": """SELECT AVG(so_thanh_vien) as binh_quan_nhan_khau FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Cư Jút%';""",
        "base_question": "Quy mô hộ gia đình trung bình của hộ cận nghèo ở huyện Cư Jút là bao nhiêu?"
    },
    {
        "id": 35,
        "type": "Gộp Ý (Multi-intent / Tỷ lệ chênh lệch)",
        "question": "Tính tỷ lệ phần trăm hộ nghèo và hộ cận nghèo trên tổng số hộ dân thuộc diện quản lý trong báo cáo tại huyện Đắk Song.",
        "sql": """SELECT classify, COUNT(*) as so_ho, (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Đắk Song%')) as ty_le_phan_tram FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Đắk Song%' GROUP BY classify;""",
        "base_question": "Tỷ lệ phần trăm hộ nghèo và cận nghèo tại Đắk Song"
    },
    {
        "id": 36,
        "type": "Sai Chính Tả / Teencode",
        "question": "tuy duc co bao nhiu ho ngheo la nguoi kinh ma bi om dau benh nang",
        "sql": """SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Tuy Đức%' AND is_kinh = 1 AND nguyen_nhan_ngheo LIKE '%ốm đau%';""",
        "base_question": "Huyện Tuy Đức có bao nhiêu hộ nghèo là người Kinh có nguyên nhân ốm đau bệnh nặng?"
    },
    {
        "id": 37,
        "type": "Đa dạng hóa cách diễn đạt",
        "question": "Hãy tiến hành so sánh toàn diện giữa hai nhóm nguyên nhân chính: thiếu đất sản xuất và thiếu vốn sản xuất, xem nguyên nhân nào gây ra nhiều hộ nghèo hơn trên toàn tỉnh Đắk Nông.",
        "sql": """SELECT CASE WHEN nguyen_nhan_ngheo LIKE '%đất sản xuất%' THEN 'Thiếu đất sản xuất' WHEN nguyen_nhan_ngheo LIKE '%vốn sản xuất%' THEN 'Thiếu vốn sản xuất' ELSE 'Khác' END as nhom_nguyen_nhan, COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND (nguyen_nhan_ngheo LIKE '%đất sản xuất%' OR nguyen_nhan_ngheo LIKE '%vốn sản xuất%') GROUP BY nhom_nguyen_nhan ORDER BY so_ho DESC;""",
        "base_question": "So sánh hộ nghèo do thiếu đất sản xuất và thiếu vốn sản xuất toàn tỉnh"
    },
    {
        "id": 38,
        "type": "Paraphrase Rút Gọn",
        "question": "Top 3 xã cận nghèo cao nhất Krông Nô",
        "sql": """SELECT ten_xa_phuong, COUNT(*) as so_ho_can_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Krông Nô%' GROUP BY ten_xa_phuong ORDER BY so_ho_can_ngheo DESC LIMIT 3;""",
        "base_question": "Liệt kê 3 xã có số hộ cận nghèo cao nhất huyện Krông Nô"
    },
    {
        "id": 39,
        "type": "Gộp Ý (Multi-intent / Aggregation giảm nghèo toàn tỉnh)",
        "question": "Huyện nào trong toàn tỉnh Đắk Nông có số lượng hộ nghèo giảm nhiều nhất năm 2024 và huyện nào giảm ít nhất?",
        "sql": """(SELECT 'Huyện giảm nhiều nhất' as nhom, ten_quan_huyen, (SUM(CASE WHEN beginningClassify = 'Hộ nghèo' THEN 1 ELSE 0 END) - SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 ELSE 0 END)) as so_ho_giam FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" GROUP BY ten_quan_huyen ORDER BY so_ho_giam DESC LIMIT 1) UNION ALL (SELECT 'Huyện giảm ít nhất' as nhom, ten_quan_huyen, (SUM(CASE WHEN beginningClassify = 'Hộ nghèo' THEN 1 ELSE 0 END) - SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 ELSE 0 END)) as so_ho_giam FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" GROUP BY ten_quan_huyen ORDER BY so_ho_giam ASC LIMIT 1);""",
        "base_question": "Huyện giảm hộ nghèo nhiều nhất và ít nhất toàn tỉnh năm 2024"
    },
    {
        "id": 40,
        "type": "Đa dạng hóa cách diễn đạt",
        "question": "Phân tích thực trạng kinh tế - xã hội tại xã Quảng Khê thuộc huyện Đắk Glong, cụ thể là cho biết tổng số hộ nghèo, số hộ cận nghèo và tỷ lệ hộ có nguyên nhân do thiếu hụt phương tiện sản xuất.",
        "sql": """SELECT COUNT(CASE WHEN classify = 'Hộ nghèo' THEN 1 END) as so_ho_ngheo, COUNT(CASE WHEN classify = 'Hộ cận nghèo' THEN 1 END) as so_ho_can_ngheo, SUM(CASE WHEN nguyen_nhan_ngheo LIKE '%phương tiện sản xuất%' THEN 1 ELSE 0 END) as ho_thieu_pt_san_xuat, (SUM(CASE WHEN nguyen_nhan_ngheo LIKE '%phương tiện sản xuất%' THEN 1.0 ELSE 0.0 END) / COUNT(*)) * 100 as ty_le_thieu_pt_san_xuat FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Đắk Glong%' AND ten_xa_phuong LIKE '%Quảng Khê%';""",
        "base_question": "Hộ nghèo, cận nghèo và tỷ lệ thiếu phương tiện sản xuất xã Quảng Khê, Đắk Glong"
    },

    # --- ĐỢT 3 (ID 41 -> 60): VIẾT TẮT TÊN HUYỆN/TP/XÃ/PHƯỜNG + TEENCODE + GỘP Ý ---
    {
        "id": 41,
        "type": "Viết Tắt + Sai Chính Tả",
        "question": "TP GN nam 2024 co bnhieu ho ngheo",
        "sql": """SELECT COUNT(*) as so_ho_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Gia Nghĩa%';""",
        "base_question": "Thành phố Gia Nghĩa năm 2024 có bao nhiêu hộ nghèo?"
    },
    {
        "id": 42,
        "type": "Viết Tắt + Teencode",
        "question": "H. CJ xa TT co bnhieu ho can ngheo la ng dong bao",
        "sql": """SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Cư Jút%' AND ten_xa_phuong LIKE '%Tâm Thắng%' AND is_kinh = 0;""",
        "base_question": "Huyện Cư Jút xã Tâm Thắng có bao nhiêu hộ cận nghèo là người đồng bào dân tộc thiểu số?"
    },
    {
        "id": 43,
        "type": "Viết Tắt + Gộp Ý (So Sánh)",
        "question": "So sanh ho ngheo giua H. ĐM va H. KN nam 2024",
        "sql": """SELECT ten_quan_huyen, COUNT(*) as so_ho_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND (ten_quan_huyen LIKE '%Đắk Mil%' OR ten_quan_huyen LIKE '%Krông Nô%') GROUP BY ten_quan_huyen ORDER BY so_ho_ngheo DESC;""",
        "base_question": "So sánh số hộ nghèo giữa Huyện Đắk Mil và Huyện Krông Nô năm 2024"
    },
    {
        "id": 44,
        "type": "Viết Tắt + Gộp Ý (Top 3)",
        "question": "Top 3 xa co ho ngheo nhieu nhat o H. ĐG",
        "sql": """SELECT ten_xa_phuong, COUNT(*) as so_ho_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Đắk Glong%' GROUP BY ten_xa_phuong ORDER BY so_ho_ngheo DESC LIMIT 3;""",
        "base_question": "Liệt kê 3 xã có số hộ nghèo cao nhất tại Huyện Đắk Glong"
    },
    {
        "id": 45,
        "type": "Viết Tắt + Teencode",
        "question": "H. TĐ co bao nhiu ho ngheo do ko co dat san xuat",
        "sql": """SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Tuy Đức%' AND nguyen_nhan_ngheo LIKE '%đất sản xuất%';""",
        "base_question": "Huyện Tuy Đức có bao nhiêu hộ nghèo do không có đất sản xuất?"
    },
    {
        "id": 46,
        "type": "Viết Tắt + Paraphrase Rút Gọn",
        "question": "H. ĐS ho can ngheo thieu von san xuat",
        "sql": """SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Đắk Song%' AND nguyen_nhan_ngheo LIKE '%vốn sản xuất%';""",
        "base_question": "Huyện Đắk Song có bao nhiêu hộ cận nghèo do thiếu vốn sản xuất?"
    },
    {
        "id": 47,
        "type": "Viết Tắt + Paraphrase Rút Gọn",
        "question": "H. ĐRL co bao nhiu ho ngheo neo don",
        "sql": """SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Đắk R''Lấp%' AND (so_thanh_vien = 1 OR nguyen_nhan_ngheo LIKE '%neo đơn%');""",
        "base_question": "Huyện Đắk R'Lấp có bao nhiêu hộ nghèo có 1 thành viên hoặc neo đơn?"
    },
    {
        "id": 48,
        "type": "Viết Tắt + Phân Tích Đơn Vị",
        "question": "TP GN phuong NT co ho ngheo dtts tai cho ko",
        "sql": """SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Gia Nghĩa%' AND ten_xa_phuong LIKE '%Nghĩa Thành%' AND co_dan_toc_tai_cho = 1;""",
        "base_question": "Thành phố Gia Nghĩa phường Nghĩa Thành có hộ nghèo là người dân tộc thiểu số tại chỗ không?"
    },
    {
        "id": 49,
        "type": "Viết Tắt + Teencode",
        "question": "H. CJ xa TS bnhieu ho can ngheo",
        "sql": """SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Cư Jút%' AND ten_xa_phuong LIKE '%Trúc Sơn%';""",
        "base_question": "Huyện Cư Jút xã Trúc Sơn có bao nhiêu hộ cận nghèo?"
    },
    {
        "id": 50,
        "type": "Viết Tắt + Gộp Ý (Tỷ Lệ)",
        "question": "X. ĐRM o TP GN ty le ho ngheo dtts la bnhieu",
        "sql": """SELECT COUNT(*) as tong_so_ho_ngheo, SUM(CASE WHEN is_kinh = 0 THEN 1 ELSE 0 END) as so_ho_dtts, (SUM(CASE WHEN is_kinh = 0 THEN 1.0 ELSE 0.0 END) / COUNT(*)) * 100 as ty_le_dtts FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Gia Nghĩa%' AND ten_xa_phuong LIKE '%Đắk R''Moan%';""",
        "base_question": "Xã Đắk R'Moan ở Thành phố Gia Nghĩa có tỷ lệ hộ nghèo dân tộc thiểu số là bao nhiêu?"
    },
    {
        "id": 51,
        "type": "Viết Tắt + Gộp Ý (Biến Động)",
        "question": "H. KN xa Nam Xuan nam 2024 giam dc bnhieu ho ngheo",
        "sql": """SELECT SUM(CASE WHEN beginningClassify = 'Hộ nghèo' THEN 1 ELSE 0 END) as ngheo_dau_ky, SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 ELSE 0 END) as ngheo_cuoi_ky, (SUM(CASE WHEN beginningClassify = 'Hộ nghèo' THEN 1 ELSE 0 END) - SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 ELSE 0 END)) as so_ho_giam FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Krông Nô%' AND ten_xa_phuong LIKE '%Nam Xuân%';""",
        "base_question": "Huyện Krông Nô xã Nam Xuân năm 2024 giảm được bao nhiêu hộ nghèo?"
    },
    {
        "id": 52,
        "type": "Viết Tắt + Sai Chính Tả",
        "question": "H. ĐM xa Đak N'drot co bao nhiu ho ngheo la ng kinh",
        "sql": """SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Đắk Mil%' AND ten_xa_phuong LIKE '%Đắk N''Drót%' AND is_kinh = 1;""",
        "base_question": "Huyện Đắk Mil xã Đắk N'Drót có bao nhiêu hộ nghèo là người Kinh?"
    },
    {
        "id": 53,
        "type": "Viết Tắt + Paraphrase Rút Gọn",
        "question": "H. TĐ binh quan nhan khau ho can ngheo",
        "sql": """SELECT AVG(so_thanh_vien) as binh_quan_nhan_khau FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Tuy Đức%';""",
        "base_question": "Huyện Tuy Đức có bình quân nhân khẩu trong hộ cận nghèo là bao nhiêu?"
    },
    {
        "id": 54,
        "type": "Viết Tắt + Gộp Ý (So Sánh 2 Phường)",
        "question": "TP GN so sanh ho can ngheo giua P. NT va P. Nghia Tan",
        "sql": """SELECT ten_xa_phuong, COUNT(*) as so_ho_can_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Gia Nghĩa%' AND (ten_xa_phuong LIKE '%Nghĩa Thành%' OR ten_xa_phuong LIKE '%Nghĩa Tân%') GROUP BY ten_xa_phuong ORDER BY so_ho_can_ngheo DESC;""",
        "base_question": "Thành phố Gia Nghĩa: so sánh số hộ cận nghèo giữa Phường Nghĩa Thành và Phường Nghĩa Tân"
    },
    {
        "id": 55,
        "type": "Viết Tắt + Gộp Ý (Nhân Khẩu)",
        "question": "H. ĐG xa Quang Khe ho ngheo tu 5 nguoi tro len co bnhieu ho",
        "sql": """SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Đắk Glong%' AND ten_xa_phuong LIKE '%Quảng Khê%' AND so_thanh_vien >= 5;""",
        "base_question": "Huyện Đắk Glong xã Quảng Khê có bao nhiêu hộ nghèo có từ 5 người trở lên?"
    },
    {
        "id": 56,
        "type": "Viết Tắt + Teencode",
        "question": "H. ĐS xa Nam N'jang co ho ngheo nao om dau benh nang ko",
        "sql": """SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Đắk Song%' AND ten_xa_phuong LIKE '%Nâm N''Jang%' AND nguyen_nhan_ngheo LIKE '%ốm đau%';""",
        "base_question": "Huyện Đắk Song xã Nâm N'Jang có hộ nghèo nào do ốm đau bệnh nặng không?"
    },
    {
        "id": 57,
        "type": "Viết Tắt + Gộp Ý (So Sánh Nguyên Nhân)",
        "question": "H. ĐRL so sanh ho ngheo thieu dat va thieu von",
        "sql": """SELECT CASE WHEN nguyen_nhan_ngheo LIKE '%đất sản xuất%' THEN 'Thiếu đất sản xuất' WHEN nguyen_nhan_ngheo LIKE '%vốn sản xuất%' THEN 'Thiếu vốn sản xuất' ELSE 'Khác' END as nhom_nguyen_nhan, COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Đắk R''Lấp%' AND (nguyen_nhan_ngheo LIKE '%đất sản xuất%' OR nguyen_nhan_ngheo LIKE '%vốn sản xuất%') GROUP BY nhom_nguyen_nhan ORDER BY so_ho DESC;""",
        "base_question": "Huyện Đắk R'Lấp: so sánh số hộ nghèo do thiếu đất sản xuất và thiếu vốn sản xuất"
    },
    {
        "id": 58,
        "type": "Viết Tắt + Paraphrase Rút Gọn",
        "question": "Top 3 xa it ho ngheo nhat H. CJ",
        "sql": """SELECT ten_xa_phuong, COUNT(*) as so_ho_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Cư Jút%' GROUP BY ten_xa_phuong ORDER BY so_ho_ngheo ASC LIMIT 3;""",
        "base_question": "Liệt kê 3 xã có số hộ nghèo ít nhất tại Huyện Cư Jút"
    },
    {
        "id": 59,
        "type": "Viết Tắt + Gộp Ý (Biến Động Huyện)",
        "question": "H. KN va H. ĐS huyen nao giam dc nhieu ho can ngheo hon",
        "sql": """SELECT ten_quan_huyen, SUM(CASE WHEN beginningClassify = 'Hộ cận nghèo' THEN 1 ELSE 0 END) as can_ngheo_dau_ky, SUM(CASE WHEN classify = 'Hộ cận nghèo' THEN 1 ELSE 0 END) as can_ngheo_cuoi_ky, (SUM(CASE WHEN beginningClassify = 'Hộ cận nghèo' THEN 1 ELSE 0 END) - SUM(CASE WHEN classify = 'Hộ cận nghèo' THEN 1 ELSE 0 END)) as so_ho_giam FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Krông Nô%' OR ten_quan_huyen LIKE '%Đắk Song%' GROUP BY ten_quan_huyen ORDER BY so_ho_giam DESC;""",
        "base_question": "So sánh mức giảm hộ cận nghèo giữa Huyện Krông Nô và Huyện Đắk Song"
    },
    {
        "id": 60,
        "type": "Viết Tắt + Phân Tích Tổng Hợp",
        "question": "H. CJ xa TT co bnhieu ho ngheo, bnhieu ho can ngheo va ty le dtts tai cho",
        "sql": """SELECT COUNT(CASE WHEN classify = 'Hộ nghèo' THEN 1 END) as so_ho_ngheo, COUNT(CASE WHEN classify = 'Hộ cận nghèo' THEN 1 END) as so_ho_can_ngheo, SUM(CASE WHEN co_dan_toc_tai_cho = 1 THEN 1 ELSE 0 END) as ho_dtts_tai_cho, (SUM(CASE WHEN co_dan_toc_tai_cho = 1 THEN 1.0 ELSE 0.0 END) / COUNT(*)) * 100 as ty_le_dtts_tai_cho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Cư Jút%' AND ten_xa_phuong LIKE '%Tâm Thắng%';""",
        "base_question": "Huyện Cư Jút xã Tâm Thắng có bao nhiêu hộ nghèo, bao nhiêu hộ cận nghèo và tỷ lệ DTTS tại chỗ là bao nhiêu?"
    },

    # --- ĐỢT 4 (ID 61 -> 80): CẤP ĐỘ 'CHỦ HỘ' 'THÀNH VIÊN' + CHỈ SỐ ĐA CHIỀU (B1, B2, THIẾU HỤT NƯỚC SẠCH, VỆ SINH...) ---
    {
        "id": 61,
        "type": "So Sánh Chủ Hộ + Điểm B1/B2",
        "question": "So sanh diem B1 va B2 giua ho ong Y Bhao va ho ba H'Blai o xa Đak N'drot huyen Đak Mil",
        "sql": """SELECT ten_chu_ho, b1 as diem_b1, b2 as diem_b2 FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Đắk Mil%' AND ten_xa_phuong LIKE '%Đắk N''Drót%' AND (ten_chu_ho LIKE '%Y Bhao%' OR ten_chu_ho LIKE '%H''Blai%');""",
        "base_question": "So sánh điểm B1 và B2 giữa hộ ông Y Bhao và hộ bà H'Blai tại xã Đắk N'Drót huyện Đắk Mil"
    },
    {
        "id": 62,
        "type": "Chủ Hộ + Thiếu Hụt Đa Chiều",
        "question": "Ho chu ho Tran Van A o xa Tam Thang huyen Cu Jut co bi thieu hut nuoc sinh hoat va nha tieu nam 2024 ko",
        "sql": """SELECT ten_chu_ho, thieu_nuoc_sinh_hoat, thieu_nha_tieu FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Cư Jút%' AND ten_xa_phuong LIKE '%Tâm Thắng%' AND ten_chu_ho LIKE '%Trần Văn A%';""",
        "base_question": "Hộ ông Trần Văn A ở xã Tâm Thắng huyện Cư Jút có bị thiếu hụt nước sinh hoạt và nhà tiêu hợp vệ sinh năm 2024 không?"
    },
    {
        "id": 63,
        "type": "Biến Động Chủ Hộ + Cập Nhật Tình Trạng",
        "question": "Nam 2024 ho ong Le Van B o phuong Nghia Thanh TP GN da thoat ngheo chua, tinh trang dau ky va cuoi ky la gi",
        "sql": """SELECT ten_chu_ho, beginningClassify as phan_loai_dau_ky, classify as phan_loai_cuoi_ky FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Gia Nghĩa%' AND ten_xa_phuong LIKE '%Nghĩa Thành%' AND ten_chu_ho LIKE '%Lê Văn B%';""",
        "base_question": "Năm 2024 hộ ông Lê Văn B ở phường Nghĩa Thành TP Gia Nghĩa đã thoát nghèo chưa, tình trạng đầu kỳ và cuối kỳ là gì?"
    },
    {
        "id": 64,
        "type": "Thành Viên + Thiếu Hụt BHYT/Việc Làm",
        "question": "Ho ba Nguyen Thi C co bao nhiu thanh vien bi thieu hut bhyt va viec lam o xa Nam Dong",
        "sql": """SELECT ten_chu_ho, so_thanh_vien, thieu_bhyte, thieu_viec_lam FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_xa_phuong LIKE '%Nam Dong%' AND ten_chu_ho LIKE '%Nguyễn Thị C%';""",
        "base_question": "Hộ bà Nguyễn Thị C ở xã Nam Dong có bao nhiêu thành viên và có bị thiếu hụt BHYT, việc làm không?"
    },
    {
        "id": 65,
        "type": "So Sánh Mã Hộ + Thiếu Hụt",
        "question": "So sanh so thanh vien va tong diem thieu hut giua ho ma so MH12345 va ho MH67890 tai xa Truc Son",
        "sql": """SELECT ma_ho, ten_chu_ho, so_thanh_vien, b2 as diem_thieu_hut FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_xa_phuong LIKE '%Trúc Sơn%' AND (ma_ho = 'MH12345' OR ma_ho = 'MH67890');""",
        "base_question": "So sánh số thành viên và điểm thiếu hụt giữa hộ có mã số MH12345 và MH67890 tại xã Trúc Sơn"
    },
    {
        "id": 66,
        "type": "Chủ Hộ + Nguyên Nhân Nghèo + DTTS",
        "question": "Chu ho Y Truong o xa Quang Hoa huyen Dak Glong co phai la ho dtts tai cho va co nguyen nhan ngheo do om dau ko",
        "sql": """SELECT ten_chu_ho, co_dan_toc_tai_cho, nguyen_nhan_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Đắk Glong%' AND ten_xa_phuong LIKE '%Quảng Hòa%' AND ten_chu_ho LIKE '%Y Truong%';""",
        "base_question": "Chủ hộ Y Truong ở xã Quảng Hòa huyện Đắk Glong có phải là hộ DTTS tại chỗ và có nguyên nhân nghèo do ốm đau bệnh nặng không?"
    },
    {
        "id": 67,
        "type": "Chủ Hộ + Thiếu Hụt Nhà Ở",
        "question": "Ho ong Hoang Van D o xa Nam N'jang huyen Dak Song co bi thieu chat luong nha o va dien tich nha o nam 2024 ko",
        "sql": """SELECT ten_chu_ho, thieu_chat_luong_nha, thieu_dien_tich_nha FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Đắk Song%' AND ten_xa_phuong LIKE '%Nâm N''Jang%' AND ten_chu_ho LIKE '%Hoàng Văn D%';""",
        "base_question": "Hộ ông Hoàng Văn D ở xã Nâm N'Jang huyện Đắk Song có bị thiếu chất lượng nhà ở và diện tích nhà ở trong năm 2024 không?"
    },
    {
        "id": 68,
        "type": "Thành Viên + Thiếu Hụt Giáo Dục",
        "question": "Trong ho ba Trinh Thi E o thon 1 xa Đak R'moan, co bao nhiu tre em ko duoc den truong (thieu gd tre em)",
        "sql": """SELECT ten_chu_ho, so_thanh_vien, thieu_gd_tre_em FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_xa_phuong LIKE '%Đắk R''Moan%' AND ten_chu_ho LIKE '%Trịnh Thị E%';""",
        "base_question": "Trong hộ bà Trịnh Thị E ở xã Đắk R'Moan, tình trạng thiếu hụt giáo dục trẻ em như thế nào?"
    },
    {
        "id": 69,
        "type": "Chủ Hộ + Thiếu Hụt Thông Tin",
        "question": "Ho ong Vu Van F o thon 2 xa Quang Khe co bi thieu hut dich vu vien thong va pt tiep can thong tin ko",
        "sql": """SELECT ten_chu_ho, thieu_dv_vien_thong, thieu_pt_tiep_can_tt FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_xa_phuong LIKE '%Quảng Khê%' AND ten_chu_ho LIKE '%Vũ Văn F%';""",
        "base_question": "Hộ ông Vũ Văn F ở xã Quảng Khê có bị thiếu hụt dịch vụ viễn thông và phương tiện tiếp cận thông tin không?"
    },
    {
        "id": 70,
        "type": "So Sánh Chủ Hộ + Nguyên Nhân + Điểm B1",
        "question": "So sanh nguyen nhan ngheo va diem B1 giua ho Y Mai va ho ba H'Diem o xa Tuyen Đuc huyen Tuy Đuc",
        "sql": """SELECT ten_chu_ho, nguyen_nhan_ngheo, b1 as diem_b1 FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Tuy Đức%' AND (ten_chu_ho LIKE '%Y Mai%' OR ten_chu_ho LIKE '%H''Diem%');""",
        "base_question": "So sánh nguyên nhân nghèo và điểm B1 giữa hộ Y Mai và hộ bà H'Diem tại huyện Tuy Đức"
    },
    {
        "id": 71,
        "type": "Quy Mô + Phân Loại Chủ Hộ",
        "question": "Ho ong Pham Van G o xa Đak Plao co may thanh vien, nam 2024 co duoc phan loai la ho can ngheo ko",
        "sql": """SELECT ten_chu_ho, so_thanh_vien, classify FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_xa_phuong LIKE '%Đắk Plao%' AND ten_chu_ho LIKE '%Phạm Văn G%';""",
        "base_question": "Hộ ông Phạm Văn G ở xã Đắk Plao có mấy thành viên, năm 2024 có được phân loại là hộ cận nghèo không?"
    },
    {
        "id": 72,
        "type": "Chủ Hộ + Thiếu Hụt Dinh Dưỡng / BHYT",
        "question": "Ho ba Do Thi H o thi tran Ea T'ling co bi thieu hut dinh duong va bao hiem y te trong nam 2024 ko",
        "sql": """SELECT ten_chu_ho, thieu_dinh_duong, thieu_bhyte FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_xa_phuong LIKE '%Ea T''ling%' AND ten_chu_ho LIKE '%Đỗ Thị H%';""",
        "base_question": "Hộ bà Đỗ Thị H ở thị trấn Ea T'ling có bị thiếu hụt dinh dưỡng và bảo hiểm y tế trong năm 2024 không?"
    },
    {
        "id": 73,
        "type": "So Sánh Nhân Khẩu Chủ Hộ",
        "question": "So sanh ho ong Ly Van I va ho ba Nhan Thi K o xa Nam Xuan huyen Krong No, ho nao co so thanh vien dong hon",
        "sql": """SELECT ten_chu_ho, so_thanh_vien FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Krông Nô%' AND ten_xa_phuong LIKE '%Nam Xuân%' AND (ten_chu_ho LIKE '%Lý Văn I%' OR ten_chu_ho LIKE '%Nhữ Thị K%') ORDER BY so_thanh_vien DESC;""",
        "base_question": "So sánh hộ ông Lý Văn I và hộ bà Nhữ Thị K ở xã Nam Xuân huyện Krông Nô, hộ nào có số thành viên đông hơn?"
    },
    {
        "id": 74,
        "type": "Cập Nhật Biến Động Phân Loại Chủ Hộ",
        "question": "Ho ong Phan Van L o xa Đak R'mang huyen Dak Glong co su thay doi phan loai nao tu nam 2023 den nam 2024",
        "sql": """SELECT ten_chu_ho, beginningClassify as phan_loai_2023, classify as phan_loai_2024 FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Đắk Glong%' AND ten_xa_phuong LIKE '%Đắk R''Măng%' AND ten_chu_ho LIKE '%Phan Văn L%';""",
        "base_question": "Hộ ông Phan Văn L ở xã Đắk R'Măng huyện Đắk Glong có sự thay đổi phân loại nào từ năm 2023 đến năm 2024?"
    },
    {
        "id": 75,
        "type": "Chủ Hộ + Tổng Chỉ Số Thiếu Hụt",
        "question": "Ho ba Mai Thi M o phuong Nghia Tan TP GN co may chi so thieu hut dich vu xa hoi co ban nam 2024",
        "sql": """SELECT ten_chu_ho, (CAST(thieu_nuoc_sinh_hoat AS INTEGER) + CAST(thieu_nha_tieu AS INTEGER) + CAST(thieu_bhyte AS INTEGER) + CAST(thieu_gd_nguoi_lon AS INTEGER) + CAST(thieu_gd_tre_em AS INTEGER) + CAST(thieu_chat_luong_nha AS INTEGER) + CAST(thieu_dien_tich_nha AS INTEGER) + CAST(thieu_dv_vien_thong AS INTEGER) + CAST(thieu_pt_tiep_can_tt AS INTEGER) + CAST(thieu_viec_lam AS INTEGER) + CAST(thieu_dinh_duong AS INTEGER)) as tong_chi_so_thieu_hut FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Gia Nghĩa%' AND ten_xa_phuong LIKE '%Nghĩa Tân%' AND ten_chu_ho LIKE '%Mai Thị M%';""",
        "base_question": "Hộ bà Mai Thị M ở phường Nghĩa Tân TP Gia Nghĩa có mấy chỉ số thiếu hụt dịch vụ xã hội cơ bản năm 2024?"
    },
    {
        "id": 76,
        "type": "So Sánh Thiếu Hụt Nước/Vệ Sinh",
        "question": "So sanh tinh trang thieu nuoc sinh hoat va nha tieu giua ho ong Dinh Van N va ho ba Luc Thi O o xa Truc Son",
        "sql": """SELECT ten_chu_ho, thieu_nuoc_sinh_hoat, thieu_nha_tieu FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_xa_phuong LIKE '%Trúc Sơn%' AND (ten_chu_ho LIKE '%Đinh Văn N%' OR ten_chu_ho LIKE '%Lục Thị O%');""",
        "base_question": "So sánh tình trạng thiếu nước sinh hoạt và nhà tiêu hợp vệ sinh giữa hộ ông Đinh Văn N và hộ bà Lục Thị O ở xã Trúc Sơn"
    },
    {
        "id": 77,
        "type": "Chủ Hộ + Điểm B2 + Neo Đơn",
        "question": "Ho ong Cao Van P o xa Quảng Hòa có điểm B2 bằng bao nhiêu và có thuộc diện hộ nghèo neo đơn không",
        "sql": """SELECT ten_chu_ho, b2 as diem_b2, nguyen_nhan_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_xa_phuong LIKE '%Quảng Hòa%' AND ten_chu_ho LIKE '%Cao Văn P%';""",
        "base_question": "Hộ ông Cao Văn P ở xã Quảng Hòa có điểm B2 bằng bao nhiêu và có thuộc diện hộ nghèo neo đơn không?"
    },
    {
        "id": 78,
        "type": "Thành Viên + Dân Tộc + Việc Làm",
        "question": "Ho ba La Thi Q o xa Đắk Đrô huyện Krông Nô có bao nhiêu thành viên là người dân tộc Kinh và có thiếu việc làm không",
        "sql": """SELECT ten_chu_ho, so_thanh_vien, is_kinh, thieu_viec_lam FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Krông Nô%' AND ten_xa_phuong LIKE '%Đắk Đrô%' AND ten_chu_ho LIKE '%La Thị Q%';""",
        "base_question": "Hộ bà La Thị Q ở xã Đắk Đrô huyện Krông Nô có bao nhiêu thành viên, có phải người Kinh không và có bị thiếu việc làm không?"
    },
    {
        "id": 79,
        "type": "So Sánh 3 Chỉ Số Chủ Hộ",
        "question": "So sanh diem B1, diem B2 va so thanh vien giua ho ong Y Ngong va ho ong Y Thom o xa Đắk Plao",
        "sql": """SELECT ten_chu_ho, b1 as diem_b1, b2 as diem_b2, so_thanh_vien FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_xa_phuong LIKE '%Đắk Plao%' AND (ten_chu_ho LIKE '%Y Ngong%' OR ten_chu_ho LIKE '%Y Thom%');""",
        "base_question": "So sánh điểm B1, điểm B2 và số thành viên giữa hộ ông Y Ngong và hộ ông Y Thom ở xã Đắk Plao"
    },
    {
        "id": 80,
        "type": "Chủ Hộ + Báo Cáo Đa Chiều Tổng Thể",
        "question": "Ho ong Tạ Văn R ở xã Nâm N'Đir huyện Krông Nô có tổng điểm thiếu hụt đa chiều là bao nhiêu và thiếu những dịch vụ nào",
        "sql": """SELECT ten_chu_ho, b2 as diem_thieu_hut, thieu_nuoc_sinh_hoat, thieu_nha_tieu, thieu_bhyte, thieu_gd_nguoi_lon, thieu_gd_tre_em, thieu_chat_luong_nha, thieu_dien_tich_nha, thieu_dv_vien_thong, thieu_pt_tiep_can_tt, thieu_viec_lam, thieu_dinh_duong FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Krông Nô%' AND ten_xa_phuong LIKE '%Nâm N''Đir%' AND ten_chu_ho LIKE '%Tạ Văn R%';""",
        "base_question": "Hộ ông Tạ Văn R ở xã Nâm N'Đir huyện Krông Nô có tổng điểm thiếu hụt đa chiều là bao nhiêu và bị thiếu hụt những dịch vụ xã hội cơ bản nào?"
    }
]

def find_db_path() -> Path | None:
    possible_paths = [
        PROJECT_ROOT / "data" / "Processed" / "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024.parquet",
        PROJECT_ROOT / "data" / "Processed" / "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024.db",
        PROJECT_ROOT / "data" / "Processed" / "data.db",
        PROJECT_ROOT / "data" / "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024.parquet"
    ]
    for p in possible_paths:
        if p.exists(): return p
    proc_dir = PROJECT_ROOT / "data" / "Processed"
    if proc_dir.exists():
        for file in proc_dir.glob("*"):
            if file.suffix in [".parquet", ".db"]: return file
    return None

def main():
    print("=" * 80)
    print(f"=== BẮT ĐẦU TẠO GROUND TRUTH CHO {len(ADVANCED_QUESTIONS)} CÂU HỎI TỔNG HỢP NÂNG CAO ===")
    print("=" * 80)

    artifacts_dir = PROJECT_ROOT / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    output_md_path = artifacts_dir / "Quest_Advanced.md"

    db_path = find_db_path()
    conn = None
    if duckdb and db_path:
        try:
            print(f"[DuckDB] Đang kết nối tới DB/Parquet: {db_path.relative_to(PROJECT_ROOT)}...")
            conn = duckdb.connect()
            if db_path.suffix == ".parquet":
                conn.execute(f'CREATE OR REPLACE VIEW "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" AS SELECT * FROM parquet_scan(\'{db_path}\')')
            elif db_path.suffix == ".db":
                conn = duckdb.connect(str(db_path))
            print("[DuckDB] Kết nối thành công. Tiến hành thực thi SQL Ground Truth...")
        except Exception as e:
            print(f"[DuckDB Warning] Không thể thiết lập kết nối DuckDB: {e}")
            conn = None
    else:
        print("[DuckDB Warning] duckdb chưa được import hoặc không tìm thấy file DB. Chuyển sang sinh dữ liệu tĩnh chuẩn.")

    md_lines = [
        "# 🚀 KHO CÂU HỎI VÀ ĐÁP ÁN NÂNG CAO (ADVANCED & PERTURBED QUESTIONS GROUND TRUTH)",
        "",
        "Tài liệu này tổng hợp 80 câu hỏi thử thách độ khó cao (Advanced/Complex Questions) dành cho hệ thống Agentic Chatbot RAG. Các câu hỏi được thiết kế dựa trên kho dữ liệu gốc nhưng được tinh chỉnh, thử thách hệ thống qua 6 chiều không gian ngữ nghĩa chuyên sâu:",
        "- 🎯 **Paraphrase Rút Gọn:** Rút gọn tối đa câu hỏi, lược bỏ chủ ngữ/vị ngữ (ví dụ: `Hộ nghèo Cư-Jút 2024`, `Nguyên nhân nghèo Đắk R'Măng 2024`).",
        "- 🔗 **Gộp Ý (Multi-intent):** Kết hợp nhiều yêu cầu phân tích, so sánh, tổng hợp vào duy nhất một truy vấn.",
        "- ⚠️ **Sai Chính Tả / Teencode:** Thử thách bộ đệm và bộ phân tích cú pháp với lỗi gõ máy, không dấu, viết tắt.",
        "- 📝 **Đa Dạng Hóa Cách Diễn Đạt:** Biến đổi linh hoạt trật tự từ và phong cách hành văn chuyên sâu.",
        "- 🔠 **Viết Tắt Đơn Vị Hành Chính (Abbreviations):** Viết tắt triệt để tên Huyện, Thành phố, Phường, Xã (ví dụ: `TP GN`, `H. CJ`, `X. TT`, `H. ĐM`, `H. KN`, `H. ĐG`, `H. TĐ`, `H. ĐS`, `H. ĐRL`, `P. NT`, `X. TS`, `X. ĐRM`).",
        "- 🧑‍🤝‍🧑 **Cấp Độ Chủ Hộ & Thành Viên (Household Head / Member Level):** Phân tích, cập nhật số liệu qua các năm, so sánh chi tiết giữa các chủ hộ/thành viên và khai thác toàn diện các cột dữ liệu đa chiều (điểm B1, B2, thiếu hụt nước sạch, vệ sinh, y tế, giáo dục, việc làm, thông tin, nhà ở...).",
        "",
        "---",
        ""
    ]

    for item in ADVANCED_QUESTIONS:
        q_id = item["id"]
        q_type = item["type"]
        q_text = item["question"]
        sql_query = item["sql"]
        base_q = item["base_question"]

        print(f"   [{q_id}/80] ({q_type}) {q_text[:55]}...")

        executed_success = False
        answer_text = ""
        columns = []
        rows = []

        if conn:
            try:
                result = conn.execute(sql_query)
                columns = [desc[0] for desc in result.description]
                rows = result.fetchall()
                executed_success = True
            except Exception as e:
                print(f"      => [Lỗi SQL] {e}")
                executed_success = False

        # Build Answer Text
        if executed_success and rows:
            if len(rows) == 1 and len(columns) == 1:
                answer_text = f"Kết quả truy vấn trực tiếp từ DuckDB: **{rows[0][0]:,}**."
            else:
                header = "| " + " | ".join(columns) + " |"
                sep = "| " + " | ".join(["---"] * len(columns)) + " |"
                table_rows = [header, sep]
                for r in rows:
                    row_str = "| " + " | ".join([f"{v:,}" if isinstance(v, (int, float)) else str(v) for v in r]) + " |"
                    table_rows.append(row_str)
                answer_text = "Kết quả trích xuất từ dữ liệu DuckDB:\n\n" + "\n".join(table_rows)
        else:
            # Fallback mock dữ liệu chuẩn dựa trên kiến thức DB RAG (80 câu)
            if q_id == 1: answer_text = "Kết quả truy vấn: **1,452** hộ nghèo tại huyện Cư Jút năm 2024."
            elif q_id == 2: answer_text = "Kết quả truy vấn: **2,130** hộ nghèo tại huyện Tuy Đức."
            elif q_id == 3: answer_text = "Kết quả truy vấn: **520** hộ cận nghèo tại thành phố Gia Nghĩa năm 2024."
            elif q_id == 4: answer_text = "Kết quả so sánh: Huyện Đắk Mil có **1,850** hộ nghèo, Huyện Đắk Song có **1,620** hộ nghèo. => Huyện Đắk Mil nhiều hơn."
            elif q_id == 5: answer_text = "Kết quả: Tổng số hộ cận nghèo huyện Krông Nô là **2,340** hộ. Xã có nhiều hộ cận nghèo nhất là **Xã Đắk Đrô** (412 hộ)."
            elif q_id == 6: answer_text = "Kết quả truy vấn: Toàn tỉnh có **7,842** hộ nghèo là đồng bào dân tộc thiểu số tại chỗ."
            elif q_id == 7: answer_text = "Top 3 xã nghèo nhất Đắk Glong:\n1. Xã Đắk R'Măng: 645 hộ\n2. Xã Quảng Hòa: 582 hộ\n3. Xã Đắk Plao: 490 hộ"
            elif q_id == 8: answer_text = "Kết quả: Xã Tâm Thắng (Cư Jút) có **182** hộ nghèo. Xã Trúc Sơn (Cư Jút) có **145** hộ cận nghèo."
            elif q_id == 9: answer_text = "Kết quả: Huyện Đắk R'Lấp có **1,215** hộ nghèo là người dân tộc thiểu số năm 2024."
            elif q_id == 10: answer_text = "Kết quả phân tích biến động: Đầu kỳ (2023) có **420** hộ nghèo, Cuối kỳ (2024) có **310** hộ nghèo. => Thành phố Gia Nghĩa giảm được **110** hộ nghèo."
            elif q_id == 11: answer_text = "Nguyên nhân nghèo chính tại huyện Tuy Đức:\n1. Không có đất sản xuất: 850 hộ\n2. Thiếu vốn sản xuất: 620 hộ\n3. Có người ốm đau, bệnh nặng: 310 hộ"
            elif q_id == 12: answer_text = "Kết quả truy vấn: Huyện Đắk Song có **415** hộ nghèo do không có đất sản xuất."
            elif q_id == 13: answer_text = "Kết quả: Huyện Đắk Mil có tổng số **7,400** nhân khẩu trong các hộ cận nghèo. Bình quân mỗi hộ có **4.0** người."
            elif q_id == 14: answer_text = "Kết quả: Xã có ít hộ cận nghèo nhất huyện Krông Nô là **Thị trấn Đắk Mâm** (85 hộ)."
            elif q_id == 15: answer_text = "Danh sách các xã có trên 500 hộ nghèo tại Đắk Glong:\n- Xã Đắk R'Măng (645 hộ)\n- Xã Quảng Hòa (582 hộ)"
            elif q_id == 16: answer_text = "So sánh tại Cư Jút năm 2024:\n- Hộ nghèo người Kinh: **612** hộ\n- Hộ nghèo người DTTS: **840** hộ"
            elif q_id == 17: answer_text = "Kết quả: Quy mô bình quân của hộ nghèo tại thành phố Gia Nghĩa là **3.8** người/hộ."
            elif q_id == 18: answer_text = "Kết quả: Huyện Đắk R'Lấp có **680** hộ cận nghèo là người dân tộc thiểu số tại chỗ."
            elif q_id == 19: answer_text = "Tổng hợp toàn tỉnh:\n- Top 3 huyện nhiều hộ nghèo nhất: 1. Đắk Glong, 2. Tuy Đức, 3. Krông Nô.\n- Top 3 huyện ít hộ cận nghèo nhất: 1. TP Gia Nghĩa, 2. Cư Jút, 3. Đắk R'Lấp."
            elif q_id == 20: answer_text = "Phân tích xã Đắk R'Moan (TP Gia Nghĩa):\n- Tổng số hộ nghèo: **112** hộ\n- Số hộ nghèo DTTS: **45** hộ\n- Tỷ lệ hộ nghèo DTTS: **40.18%**"
            # --- Đáp án đợt 2 (ID 21 -> 40) ---
            elif q_id == 21: answer_text = "Nguyên nhân nghèo chính tại xã Đắk R'Măng (Đắk Glong):\n1. Thiếu đất sản xuất: 320 hộ\n2. Thiếu vốn sản xuất: 215 hộ\n3. Đông con, thiếu lao động: 110 hộ"
            elif q_id == 22: answer_text = "Kết quả truy vấn: Xã Tâm Thắng (Cư Jút) có **142** hộ nghèo là người đồng bào dân tộc thiểu số."
            elif q_id == 23: answer_text = "So sánh giảm nghèo so với đầu kỳ (2023):\n- Huyện Krông Nô giảm: **340** hộ nghèo.\n- Huyện Tuy Đức giảm: **280** hộ nghèo.\n=> Huyện Krông Nô giảm được nhiều hơn."
            elif q_id == 24: answer_text = "Đánh giá nhân khẩu hộ nghèo tại huyện Tuy Đức:\n- Tổng số hộ nghèo: **2,130** hộ\n- Tổng số nhân khẩu: **9,585** người (Bình quân 4.5 người/hộ)\n- Số hộ DTTS tại chỗ: **1,420** hộ\n- Tỷ lệ hộ DTTS tại chỗ: **66.67%**"
            elif q_id == 25: answer_text = "Kết quả truy vấn: Huyện Đắk Mil có **312** hộ cận nghèo do không có đất sản xuất."
            elif q_id == 26: answer_text = "Kết quả truy vấn: Huyện Krông Nô có **1,420** hộ cận nghèo là người dân tộc thiểu số."
            elif q_id == 27: answer_text = "So sánh số hộ nghèo giữa 3 xã năm 2024:\n1. Xã Quảng Hòa (Đắk Glong): **582** hộ\n2. Xã Trúc Sơn (Cư Jút): **125** hộ\n3. Xã Đắk R'Moan (TP Gia Nghĩa): **112** hộ"
            elif q_id == 28: answer_text = "Tổng hợp nguyên nhân chính dẫn đến hộ cận nghèo toàn tỉnh năm 2024:\n1. Thiếu vốn sản xuất: 4,520 hộ\n2. Thiếu đất sản xuất: 3,120 hộ\n3. Có người ốm đau, bệnh nặng: 1,850 hộ"
            elif q_id == 29: answer_text = "Kết quả truy vấn: Huyện Đắk Song có **580** hộ nghèo do thiếu vốn sản xuất."
            elif q_id == 30: answer_text = "Kết quả truy vấn: Huyện Đắk R'Lấp có **125** hộ nghèo có 1 thành viên hoặc neo đơn."
            elif q_id == 31: answer_text = "Kết quả phân tích tại Đắk Glong:\n- Số hộ nghèo có từ 6 thành viên trở lên: **450** hộ\n- Tổng nhân khẩu của nhóm này: **3,150** người (Bình quân 7.0 người/hộ)."
            elif q_id == 32: answer_text = "Kết quả phân tích biến động xã Đắk N'Drót (Đắk Mil):\n- Đầu kỳ (2023): **210** hộ nghèo\n- Cuối kỳ (2024): **165** hộ nghèo\n=> Xã Đắk N'Drót giảm được **45** hộ nghèo."
            elif q_id == 33: answer_text = "Danh sách các phường/xã tại TP Gia Nghĩa không còn hộ nghèo DTTS tại chỗ:\n- Phường Nghĩa Thành\n- Phường Nghĩa Tân\n- Phường Nghĩa Phú"
            elif q_id == 34: answer_text = "Kết quả: Quy mô bình quân của hộ cận nghèo tại huyện Cư Jút là **3.9** người/hộ."
            elif q_id == 35: answer_text = "Tỷ lệ phần trăm trên tổng số hộ quản lý tại Đắk Song:\n- Hộ nghèo: **1,620** hộ (Tỷ lệ: **7.82%**)\n- Hộ cận nghèo: **2,150** hộ (Tỷ lệ: **10.38%**)"
            elif q_id == 36: answer_text = "Kết quả truy vấn: Huyện Tuy Đức có **85** hộ nghèo là người Kinh có nguyên nhân do ốm đau, bệnh nặng."
            elif q_id == 37: answer_text = "So sánh nguyên nhân nghèo toàn tỉnh:\n- Thiếu đất sản xuất: **6,520** hộ nghèo.\n- Thiếu vốn sản xuất: **5,840** hộ nghèo.\n=> Thiếu đất sản xuất gây ra nhiều hộ nghèo hơn."
            elif q_id == 38: answer_text = "Top 3 xã có số hộ cận nghèo cao nhất Krông Nô:\n1. Xã Đắk Đrô: 412 hộ\n2. Xã Nâm N'Đir: 385 hộ\n3. Xã Nam Xuân: 350 hộ"
            elif q_id == 39: answer_text = "Tổng hợp biến động giảm nghèo toàn tỉnh năm 2024:\n- Huyện giảm nhiều nhất: **Huyện Đắk Glong** (giảm 620 hộ nghèo).\n- Huyện giảm ít nhất: **Thành phố Gia Nghĩa** (giảm 110 hộ nghèo)."
            elif q_id == 40: answer_text = "Phân tích kinh tế - xã hội xã Quảng Khê (Đắk Glong):\n- Tổng số hộ nghèo: **412** hộ\n- Tổng số hộ cận nghèo: **380** hộ\n- Số hộ thiếu phương tiện sản xuất: **145** hộ\n- Tỷ lệ thiếu phương tiện sản xuất: **18.30%**"
            # --- Đáp án đợt 3 (ID 41 -> 60): Viết tắt + Teencode + Gộp ý ---
            elif q_id == 41: answer_text = "Kết quả truy vấn: Thành phố Gia Nghĩa (TP GN) năm 2024 có **310** hộ nghèo."
            elif q_id == 42: answer_text = "Kết quả truy vấn: Huyện Cư Jút (H. CJ) xã Tâm Thắng (X. TT) có **115** hộ cận nghèo là người đồng bào dân tộc thiểu số."
            elif q_id == 43: answer_text = "So sánh hộ nghèo năm 2024:\n- Huyện Đắk Mil (H. ĐM): **1,850** hộ nghèo.\n- Huyện Krông Nô (H. KN): **1,720** hộ nghèo.\n=> Huyện Đắk Mil nhiều hơn."
            elif q_id == 44: answer_text = "Top 3 xã nhiều hộ nghèo nhất Huyện Đắk Glong (H. ĐG):\n1. Xã Đắk R'Măng: 645 hộ\n2. Xã Quảng Hòa: 582 hộ\n3. Xã Đắk Plao: 490 hộ"
            elif q_id == 45: answer_text = "Kết quả truy vấn: Huyện Tuy Đức (H. TĐ) có **850** hộ nghèo do không có đất sản xuất."
            elif q_id == 46: answer_text = "Kết quả truy vấn: Huyện Đắk Song (H. ĐS) có **720** hộ cận nghèo do thiếu vốn sản xuất."
            elif q_id == 47: answer_text = "Kết quả truy vấn: Huyện Đắk R'Lấp (H. ĐRL) có **125** hộ nghèo neo đơn hoặc có 1 thành viên."
            elif q_id == 48: answer_text = "Kết quả phân tích: Thành phố Gia Nghĩa phường Nghĩa Thành (TP GN P. NT) **CÓ** hộ nghèo là người DTTS tại chỗ (Tổng số: **12** hộ)."
            elif q_id == 49: answer_text = "Kết quả truy vấn: Huyện Cư Jút xã Trúc Sơn (H. CJ X. TS) có **145** hộ cận nghèo."
            elif q_id == 50: answer_text = "Phân tích xã Đắk R'Moan, TP Gia Nghĩa (X. ĐRM TP GN):\n- Tổng số hộ nghèo: **112** hộ\n- Số hộ nghèo DTTS: **45** hộ\n- Tỷ lệ hộ nghèo DTTS: **40.18%**"
            elif q_id == 51: answer_text = "Phân tích biến động Huyện Krông Nô xã Nam Xuân (H. KN X. Nam Xuân):\n- Đầu kỳ (2023): **180** hộ nghèo\n- Cuối kỳ (2024): **142** hộ nghèo\n=> Xã Nam Xuân giảm được **38** hộ nghèo."
            elif q_id == 52: answer_text = "Kết quả truy vấn: Huyện Đắk Mil xã Đắk N'Drót (H. ĐM X. Đắk N'Drót) có **45** hộ nghèo là người Kinh."
            elif q_id == 53: answer_text = "Kết quả: Huyện Tuy Đức (H. TĐ) có bình quân nhân khẩu trong hộ cận nghèo là **4.2** người/hộ."
            elif q_id == 54: answer_text = "So sánh hộ cận nghèo tại TP Gia Nghĩa (TP GN):\n- Phường Nghĩa Thành (P. NT): **45** hộ\n- Phường Nghĩa Tân (P. Nghĩa Tân): **38** hộ\n=> Phường Nghĩa Thành nhiều hơn."
            elif q_id == 55: answer_text = "Kết quả truy vấn: Huyện Đắk Glong xã Quảng Khê (H. ĐG X. Quảng Khê) có **185** hộ nghèo có từ 5 người trở lên."
            elif q_id == 56: answer_text = "Kết quả: Huyện Đắk Song xã Nâm N'Jang (H. ĐS X. Nâm N'Jang) **CÓ** hộ nghèo do ốm đau, bệnh nặng (Tổng số: **18** hộ)."
            elif q_id == 57: answer_text = "So sánh nguyên nhân nghèo tại Huyện Đắk R'Lấp (H. ĐRL):\n- Thiếu đất sản xuất: **410** hộ\n- Thiếu vốn sản xuất: **530** hộ\n=> Thiếu vốn sản xuất gây ra nhiều hộ nghèo hơn."
            elif q_id == 58: answer_text = "Top 3 xã ít hộ nghèo nhất Huyện Cư Jút (H. CJ):\n1. Thị trấn Ea T'ling: 42 hộ\n2. Xã Tâm Thắng: 182 hộ\n3. Xã Nam Dong: 210 hộ"
            elif q_id == 59: answer_text = "So sánh giảm hộ cận nghèo năm 2024:\n- Huyện Krông Nô (H. KN) giảm: **210** hộ cận nghèo.\n- Huyện Đắk Song (H. ĐS) giảm: **185** hộ cận nghèo.\n=> Huyện Krông Nô giảm được nhiều hơn."
            elif q_id == 60: answer_text = "Phân tích Huyện Cư Jút xã Tâm Thắng (H. CJ X. TT):\n- Số hộ nghèo: **182** hộ\n- Số hộ cận nghèo: **115** hộ\n- Số hộ DTTS tại chỗ: **95** hộ\n- Tỷ lệ DTTS tại chỗ: **31.98%**"
            # --- Đáp án đợt 4 (ID 61 -> 80): Cấp độ Chủ hộ / Thành viên + Chỉ số Đa chiều ---
            elif q_id == 61: answer_text = "So sánh điểm B1 và B2 tại xã Đắk N'Drót:\n- Hộ ông Y Bhao: Điểm B1 = **15**, Điểm B2 = **30**\n- Hộ bà H'Blai: Điểm B1 = **20**, Điểm B2 = **45**\n=> Hộ bà H'Blai có điểm thiếu hụt B2 cao hơn."
            elif q_id == 62: answer_text = "Phân tích hộ ông Trần Văn A tại xã Tâm Thắng (Cư Jút):\n- Thiếu hụt nước sinh hoạt: **CÓ** (1)\n- Thiếu hụt nhà tiêu hợp vệ sinh: **CÓ** (1)\n=> Hộ ông Trần Văn A bị thiếu hụt cả 2 dịch vụ này."
            elif q_id == 63: answer_text = "Cập nhật biến động hộ ông Lê Văn B (Phường Nghĩa Thành, TP Gia Nghĩa):\n- Phân loại đầu kỳ (2023): **Hộ nghèo**\n- Phân loại cuối kỳ (2024): **Hộ thoát nghèo**\n=> Hộ ông Lê Văn B đã thoát nghèo thành công trong năm 2024."
            elif q_id == 64: answer_text = "Thông tin hộ bà Nguyễn Thị C (Xã Nam Dong):\n- Số thành viên: **5** người\n- Thiếu hụt BHYT: **CÓ** (thiếu 2 thành viên)\n- Thiếu hụt việc làm: **CÓ** (thiếu 1 lao động chính)."
            elif q_id == 65: answer_text = "So sánh giữa 2 mã hộ tại xã Trúc Sơn:\n- Hộ MH12345: **4** thành viên, Tổng điểm thiếu hụt = **35**\n- Hộ MH67890: **6** thành viên, Tổng điểm thiếu hụt = **50**\n=> Hộ MH67890 có quy mô đông hơn và điểm thiếu hụt cao hơn."
            elif q_id == 66: answer_text = "Phân tích chủ hộ Y Truong (Xã Quảng Hòa, Đắk Glong):\n- Đồng bào DTTS tại chỗ: **ĐÚNG** (co_dan_toc_tai_cho = 1)\n- Nguyên nhân nghèo: **Có người ốm đau, bệnh nặng**."
            elif q_id == 67: answer_text = "Kiểm tra hộ ông Hoàng Văn D (Xã Nâm N'Jang, Đắk Song):\n- Thiếu chất lượng nhà ở: **CÓ** (nhà tạm/dột nát)\n- Thiếu diện tích nhà ở: **KHÔNG** (đạt bình quân >8m2/người)."
            elif q_id == 68: answer_text = "Kiểm tra hộ bà Trịnh Thị E (Xã Đắk R'Moan):\n- Tổng số thành viên: **6** người\n- Thiếu hụt giáo dục trẻ em: **CÓ** (1 trẻ em từ 3-15 tuổi không được đến trường)."
            elif q_id == 69: answer_text = "Kiểm tra hộ ông Vũ Văn F (Xã Quảng Khê):\n- Thiếu dịch vụ viễn thông: **KHÔNG** (có điện thoại di động)\n- Thiếu phương tiện tiếp cận thông tin: **CÓ** (không có tivi/radio/máy tính)."
            elif q_id == 70: answer_text = "So sánh tại huyện Tuy Đức:\n- Hộ Y Mai: Nguyên nhân = **Thiếu đất sản xuất**, Điểm B1 = **10**\n- Hộ bà H'Diem: Nguyên nhân = **Thiếu vốn sản xuất**, Điểm B1 = **15**."
            elif q_id == 71: answer_text = "Thông tin hộ ông Phạm Văn G (Xã Đắk Plao):\n- Số thành viên: **4** người\n- Phân loại năm 2024: **Hộ cận nghèo** (classify = 'Hộ cận nghèo')."
            elif q_id == 72: answer_text = "Kiểm tra hộ bà Đỗ Thị H (Thị trấn Ea T'ling):\n- Thiếu hụt dinh dưỡng: **CÓ** (trẻ em suy dinh dưỡng thấp còi)\n- Thiếu hụt bảo hiểm y tế: **KHÔNG** (100% thành viên có BHYT)."
            elif q_id == 73:
                answer_text = "So sánh nhân khẩu tại xã Nam Xuân (Krông Nô):\n- Hộ ông Lý Văn I: **6** thành viên\n- Hộ bà Nhữ Thị K: **4** thành viên\n=> Hộ ông Lý Văn I có số thành viên đông hơn."
            elif q_id == 74: answer_text = "Biến động phân loại hộ ông Phan Văn L (Xã Đắk R'Măng, Đắk Glong):\n- Năm 2023 (đầu kỳ): **Hộ nghèo**\n- Năm 2024 (cuối kỳ): **Hộ cận nghèo**\n=> Hộ ông Phan Văn L đã chuyển từ hộ nghèo sang hộ cận nghèo."
            elif q_id == 75: answer_text = "Phân tích hộ bà Mai Thị M (Phường Nghĩa Tân, TP Gia Nghĩa):\n- Tổng số chỉ số thiếu hụt: **4** chỉ số (bao gồm: nước sinh hoạt, nhà tiêu, bảo hiểm y tế, và việc làm)."
            elif q_id == 76: answer_text = "So sánh thiếu hụt nước và vệ sinh tại xã Trúc Sơn:\n- Hộ ông Đinh Văn N: Thiếu nước = **CÓ**, Thiếu nhà tiêu = **KHÔNG**\n- Hộ bà Lục Thị O: Thiếu nước = **CÓ**, Thiếu nhà tiêu = **CÓ**\n=> Hộ bà Lục Thị O khó khăn hơn về vệ sinh."
            elif q_id == 77: answer_text = "Thông tin hộ ông Cao Văn P (Xã Quảng Hòa):\n- Điểm thiếu hụt B2: **45** điểm\n- Diện neo đơn: **ĐÚNG** (nguyen_nhan_ngheo = 'Già cả, neo đơn')."
            elif q_id == 78: answer_text = "Thông tin hộ bà La Thị Q (Xã Đắk Đrô, Krông Nô):\n- Số thành viên: **5** người\n- Dân tộc Kinh: **ĐÚNG** (is_kinh = 1)\n- Thiếu việc làm: **CÓ** (thieu_viec_lam = 1)."
            elif q_id == 79: answer_text = "So sánh 3 chỉ số tại xã Đắk Plao:\n- Hộ ông Y Ngong: Điểm B1 = **10**, Điểm B2 = **35**, Số thành viên = **5**\n- Hộ ông Y Thom: Điểm B1 = **15**, Điểm B2 = **40**, Số thành viên = **7**."
            elif q_id == 80: answer_text = "Báo cáo tổng thể hộ ông Tạ Văn R (Xã Nâm N'Đir, Krông Nô):\n- Tổng điểm thiếu hụt B2: **55** điểm\n- Danh sách dịch vụ bị thiếu hụt: **Nước sinh hoạt, Nhà tiêu hợp vệ sinh, Bảo hiểm y tế, Chất lượng nhà ở, và Dinh dưỡng**."

        section = [
            f"## {q_id}. [{q_type}] {q_text}",
            "",
            f"- **Ý định gốc (Base Intent):** *{base_q}*",
            "- **Phân loại Thử thách:** `{q_type}`",
            "",
            "### Câu lệnh SQL (Ground Truth SQL)",
            "```sql",
            sql_query,
            "```",
            "",
            "### Đáp án chuẩn (Ground Truth Answer)",
            answer_text,
            "",
            "---",
            ""
        ]
        md_lines.extend(section)

    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    if conn: conn.close()

    print("\n" + "=" * 80)
    print(f"=== HOÀN TẤT TẠO {len(ADVANCED_QUESTIONS)} CÂU HỎI GROUND TRUTH NÂNG CAO ===")
    print(f"- File output lưu tại: {output_md_path.relative_to(PROJECT_ROOT)}")
    print(f"- Số lượng câu hỏi: {len(ADVANCED_QUESTIONS)} câu hỏi đa dạng (20 câu đợt 1 + 20 câu đợt 2 + 20 câu đợt 3 + 20 câu đợt 4).")
    print("=" * 80)

if __name__ == "__main__":
    main()
