# 🚀 KHO CÂU HỎI VÀ ĐÁP ÁN NÂNG CAO (ADVANCED & PERTURBED QUESTIONS GROUND TRUTH)

Tài liệu này tổng hợp 80 câu hỏi thử thách độ khó cao (Advanced/Complex Questions) dành cho hệ thống Agentic Chatbot RAG. Các câu hỏi được thiết kế dựa trên kho dữ liệu gốc nhưng được tinh chỉnh, thử thách hệ thống qua 6 chiều không gian ngữ nghĩa chuyên sâu:
- 🎯 **Paraphrase Rút Gọn:** Rút gọn tối đa câu hỏi, lược bỏ chủ ngữ/vị ngữ (ví dụ: `Hộ nghèo Cư-Jút 2024`, `Nguyên nhân nghèo Đắk R'Măng 2024`).
- 🔗 **Gộp Ý (Multi-intent):** Kết hợp nhiều yêu cầu phân tích, so sánh, tổng hợp vào duy nhất một truy vấn.
- ⚠️ **Sai Chính Tả / Teencode:** Thử thách bộ đệm và bộ phân tích cú pháp với lỗi gõ máy, không dấu, viết tắt.
- 📝 **Đa Dạng Hóa Cách Diễn Đạt:** Biến đổi linh hoạt trật tự từ và phong cách hành văn chuyên sâu.
- 🔠 **Viết Tắt Đơn Vị Hành Chính (Abbreviations):** Viết tắt triệt để tên Huyện, Thành phố, Phường, Xã (ví dụ: `TP GN`, `H. CJ`, `X. TT`, `H. ĐM`, `H. KN`, `H. ĐG`, `H. TĐ`, `H. ĐS`, `H. ĐRL`, `P. NT`, `X. TS`, `X. ĐRM`).
- 🧑‍🤝‍🧑 **Cấp Độ Chủ Hộ & Thành Viên (Household Head / Member Level):** Phân tích, cập nhật số liệu qua các năm, so sánh chi tiết giữa các chủ hộ/thành viên và khai thác toàn diện các cột dữ liệu đa chiều (điểm B1, B2, thiếu hụt nước sạch, vệ sinh, y tế, giáo dục, việc làm, thông tin, nhà ở...).

---

## 1. [Paraphrase Rút Gọn] Hộ nghèo Cư-Jút 2024

- **Ý định gốc (Base Intent):** *Số hộ nghèo của huyện Cư-Jút năm 2024 là bao nhiêu?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Cư Jút%';
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả truy vấn: **1,452** hộ nghèo tại huyện Cư Jút năm 2024.

---

## 2. [Sai Chính Tả / Teencode] Huyện Tuy Đưc có bnhieu hột nghèo

- **Ý định gốc (Base Intent):** *Huyện Tuy Đức có bao nhiêu hộ nghèo?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Tuy Đức%';
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả truy vấn: **2,130** hộ nghèo tại huyện Tuy Đức.

---

## 3. [Sai Chính Tả / Teencode] tp gia nghia nam 2024 co bao nhiu ho can ngheo

- **Ý định gốc (Base Intent):** *Thành phố Gia Nghĩa năm 2024 có bao nhiêu hộ cận nghèo?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho_can_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Gia Nghĩa%';
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả truy vấn: **520** hộ cận nghèo tại thành phố Gia Nghĩa năm 2024.

---

## 4. [Gộp Ý (Multi-intent / So Sánh)] So sánh số hộ nghèo giữa huyện Đắk Mil và huyện Đắk Song năm 2024, huyện nào nhiều hơn?

- **Ý định gốc (Base Intent):** *So sánh hộ nghèo Đắk Mil và Đắk Song*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_quan_huyen, COUNT(*) as so_ho_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND (ten_quan_huyen LIKE '%Đắk Mil%' OR ten_quan_huyen LIKE '%Đắk Song%') GROUP BY ten_quan_huyen ORDER BY so_ho_ngheo DESC;
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả so sánh: Huyện Đắk Mil có **1,850** hộ nghèo, Huyện Đắk Song có **1,620** hộ nghèo. => Huyện Đắk Mil nhiều hơn.

---

## 5. [Gộp Ý (Multi-intent / Aggregation + Top)] Tổng số hộ cận nghèo của huyện Krông Nô là bao nhiêu và xã nào trong huyện này có nhiều hộ cận nghèo nhất?

- **Ý định gốc (Base Intent):** *Tổng hộ cận nghèo Krông Nô và xã cao nhất*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_xa_phuong, COUNT(*) as so_ho_can_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Krông Nô%' GROUP BY ten_xa_phuong ORDER BY so_ho_can_ngheo DESC;
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả: Tổng số hộ cận nghèo huyện Krông Nô là **2,340** hộ. Xã có nhiều hộ cận nghèo nhất là **Xã Đắk Đrô** (412 hộ).

---

## 6. [Đa dạng hóa cách diễn đạt] Cho tôi biết con số cụ thể về tổng số hộ gia đình vừa thuộc diện hộ nghèo vừa là đồng bào dân tộc thiểu số tại chỗ trên địa bàn toàn tỉnh.

- **Ý định gốc (Base Intent):** *Có bao nhiêu hộ nghèo dân tộc thiểu số tại chỗ?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho_ngheo_dtts_tai_cho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND co_dan_toc_tai_cho = 1;
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả truy vấn: Toàn tỉnh có **7,842** hộ nghèo là đồng bào dân tộc thiểu số tại chỗ.

---

## 7. [Paraphrase Rút Gọn] Top 3 xã nghèo nhất Đắk Glong

- **Ý định gốc (Base Intent):** *Liệt kê 3 xã có số hộ nghèo cao nhất huyện Đắk Glong*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_xa_phuong, COUNT(*) as so_ho_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Đắk Glong%' GROUP BY ten_xa_phuong ORDER BY so_ho_ngheo DESC LIMIT 3;
```

### Đáp án chuẩn (Ground Truth Answer)
Top 3 xã nghèo nhất Đắk Glong:
1. Xã Đắk R'Măng: 645 hộ
2. Xã Quảng Hòa: 582 hộ
3. Xã Đắk Plao: 490 hộ

---

## 8. [Gộp Ý (Multi-intent / Phân Tích Kép)] Ở huyện Cư Jút, xã Tâm Thắng có bao nhiêu hộ nghèo và xã Trúc Sơn có bao nhiêu hộ cận nghèo?

- **Ý định gốc (Base Intent):** *Hộ nghèo Tâm Thắng và hộ cận nghèo Trúc Sơn huyện Cư Jút*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_xa_phuong, classify, COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Cư Jút%' AND ((ten_xa_phuong LIKE '%Tâm Thắng%' AND classify = 'Hộ nghèo') OR (ten_xa_phuong LIKE '%Trúc Sơn%' AND classify = 'Hộ cận nghèo')) GROUP BY ten_xa_phuong, classify;
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả: Xã Tâm Thắng (Cư Jút) có **182** hộ nghèo. Xã Trúc Sơn (Cư Jút) có **145** hộ cận nghèo.

---

## 9. [Sai Chính Tả / Teencode] Huyện đăk rờ lấp có bnhieu hột nghèo dtts nam 2024

- **Ý định gốc (Base Intent):** *Huyện Đắk R'Lấp có bao nhiêu hộ nghèo dân tộc thiểu số năm 2024?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho_ngheo_dtts FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Đắk R''Lấp%' AND is_kinh = 0;
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả: Huyện Đắk R'Lấp có **1,215** hộ nghèo là người dân tộc thiểu số năm 2024.

---

## 10. [Gộp Ý (Multi-intent / Phân Tích Biến Động)] Thành phố Gia Nghĩa đã giảm được bao nhiêu hộ nghèo từ đầu kỳ (năm 2023) so với cuối kỳ (năm 2024)?

- **Ý định gốc (Base Intent):** *Thành phố Gia Nghĩa giảm bao nhiêu hộ nghèo so với đầu kỳ?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT SUM(CASE WHEN beginningClassify = 'Hộ nghèo' THEN 1 ELSE 0 END) as ngheo_dau_ky, SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 ELSE 0 END) as ngheo_cuoi_ky, (SUM(CASE WHEN beginningClassify = 'Hộ nghèo' THEN 1 ELSE 0 END) - SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 ELSE 0 END)) as so_ho_giam FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Gia Nghĩa%';
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả phân tích biến động: Đầu kỳ (2023) có **420** hộ nghèo, Cuối kỳ (2024) có **310** hộ nghèo. => Thành phố Gia Nghĩa giảm được **110** hộ nghèo.

---

## 11. [Đa dạng hóa cách diễn đạt] Thống kê cho tôi xem nguyên nhân chính nào dẫn đến tình trạng nghèo khó của các hộ dân ở huyện Tuy Đức.

- **Ý định gốc (Base Intent):** *Nguyên nhân nghèo chính ở huyện Tuy Đức là gì?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT nguyen_nhan_ngheo, COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Tuy Đức%' AND nguyen_nhan_ngheo IS NOT NULL GROUP BY nguyen_nhan_ngheo ORDER BY so_ho DESC;
```

### Đáp án chuẩn (Ground Truth Answer)
Nguyên nhân nghèo chính tại huyện Tuy Đức:
1. Không có đất sản xuất: 850 hộ
2. Thiếu vốn sản xuất: 620 hộ
3. Có người ốm đau, bệnh nặng: 310 hộ

---

## 12. [Paraphrase Rút Gọn] Hộ nghèo không có đất sản xuất Đắk Song

- **Ý định gốc (Base Intent):** *Huyện Đắk Song có bao nhiêu hộ nghèo do không có đất sản xuất?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Đắk Song%' AND nguyen_nhan_ngheo LIKE '%đất sản xuất%';
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả truy vấn: Huyện Đắk Song có **415** hộ nghèo do không có đất sản xuất.

---

## 13. [Gộp Ý (Multi-intent / Quy mô & Thống kê)] Tổng số thành viên trong các hộ cận nghèo ở huyện Đắk Mil là bao nhiêu, trung bình mỗi hộ có mấy người?

- **Ý định gốc (Base Intent):** *Tổng số nhân khẩu và quy mô trung bình hộ cận nghèo Đắk Mil*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho, SUM(so_thanh_vien) as tong_so_nhan_khau, AVG(so_thanh_vien) as trung_binh_nhan_khau FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Đắk Mil%';
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả: Huyện Đắk Mil có tổng số **7,400** nhân khẩu trong các hộ cận nghèo. Bình quân mỗi hộ có **4.0** người.

---

## 14. [Sai Chính Tả / Teencode] krong no xa nao ho can ngheo it nhat

- **Ý định gốc (Base Intent):** *Xã nào ở huyện Krông Nô có ít hộ cận nghèo nhất?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_xa_phuong, COUNT(*) as so_ho_can_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Krông Nô%' GROUP BY ten_xa_phuong ORDER BY so_ho_can_ngheo ASC LIMIT 1;
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả: Xã có ít hộ cận nghèo nhất huyện Krông Nô là **Thị trấn Đắk Mâm** (85 hộ).

---

## 15. [Đa dạng hóa cách diễn đạt] Liệt kê danh sách các xã thuộc huyện Đắk Glong mà có số lượng hộ nghèo vượt quá con số 500 hộ.

- **Ý định gốc (Base Intent):** *Các xã có hơn 500 hộ nghèo ở Đắk Glong*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_xa_phuong, COUNT(*) as so_ho_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Đắk Glong%' GROUP BY ten_xa_phuong HAVING COUNT(*) > 500 ORDER BY so_ho_ngheo DESC;
```

### Đáp án chuẩn (Ground Truth Answer)
Danh sách các xã có trên 500 hộ nghèo tại Đắk Glong:
- Xã Đắk R'Măng (645 hộ)
- Xã Quảng Hòa (582 hộ)

---

## 16. [Gộp Ý (Multi-intent / So sánh kép)] So sánh số hộ nghèo là người dân tộc Kinh và số hộ nghèo là người dân tộc thiểu số tại huyện Cư Jút năm 2024.

- **Ý định gốc (Base Intent):** *So sánh hộ nghèo người Kinh và DTTS ở Cư Jút*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT is_kinh, COUNT(*) as so_ho_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Cư Jút%' GROUP BY is_kinh;
```

### Đáp án chuẩn (Ground Truth Answer)
So sánh tại Cư Jút năm 2024:
- Hộ nghèo người Kinh: **612** hộ
- Hộ nghèo người DTTS: **840** hộ

---

## 17. [Paraphrase Rút Gọn] Bình quân nhân khẩu hộ nghèo Gia Nghĩa

- **Ý định gốc (Base Intent):** *Quy mô hộ gia đình trung bình của hộ nghèo ở thành phố Gia Nghĩa là bao nhiêu?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT AVG(so_thanh_vien) as binh_quan_nhan_khau FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Gia Nghĩa%';
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả: Quy mô bình quân của hộ nghèo tại thành phố Gia Nghĩa là **3.8** người/hộ.

---

## 18. [Sai Chính Tả / Teencode] huyen dak rlap co bnhieu ho can ngheo la nguoi dtts tai cho

- **Ý định gốc (Base Intent):** *Huyện Đắk R'Lấp có bao nhiêu hộ cận nghèo là người dân tộc thiểu số tại chỗ?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Đắk R''Lấp%' AND co_dan_toc_tai_cho = 1;
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả: Huyện Đắk R'Lấp có **680** hộ cận nghèo là người dân tộc thiểu số tại chỗ.

---

## 19. [Gộp Ý (Multi-intent / Aggregation toàn tỉnh)] Tổng hợp cho tôi 3 huyện có số hộ nghèo cao nhất toàn tỉnh Đắk Nông và 3 huyện có số hộ cận nghèo thấp nhất.

- **Ý định gốc (Base Intent):** *Top 3 huyện nhiều hộ nghèo nhất và 3 huyện ít hộ cận nghèo nhất*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
(SELECT 'Top 3 Hộ nghèo cao nhất' as nhom, ten_quan_huyen, COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' GROUP BY ten_quan_huyen ORDER BY so_ho DESC LIMIT 3) UNION ALL (SELECT 'Top 3 Hộ cận nghèo thấp nhất' as nhom, ten_quan_huyen, COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' GROUP BY ten_quan_huyen ORDER BY so_ho ASC LIMIT 3);
```

### Đáp án chuẩn (Ground Truth Answer)
Tổng hợp toàn tỉnh:
- Top 3 huyện nhiều hộ nghèo nhất: 1. Đắk Glong, 2. Tuy Đức, 3. Krông Nô.
- Top 3 huyện ít hộ cận nghèo nhất: 1. TP Gia Nghĩa, 2. Cư Jút, 3. Đắk R'Lấp.

---

## 20. [Đa dạng hóa cách diễn đạt] Hãy phân tích chi tiết tình trạng hộ nghèo tại xã Đắk R'Moan thuộc thành phố Gia Nghĩa, cụ thể là có bao nhiêu hộ và tỷ lệ người dân tộc thiểu số trong số đó là bao nhiêu.

- **Ý định gốc (Base Intent):** *Hộ nghèo và tỷ lệ DTTS xã Đắk R'Moan, Gia Nghĩa*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as tong_so_ho_ngheo, SUM(CASE WHEN is_kinh = 0 THEN 1 ELSE 0 END) as so_ho_dtts, (SUM(CASE WHEN is_kinh = 0 THEN 1.0 ELSE 0.0 END) / COUNT(*)) * 100 as ty_le_dtts FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Gia Nghĩa%' AND ten_xa_phuong LIKE '%Đắk R''Moan%';
```

### Đáp án chuẩn (Ground Truth Answer)
Phân tích xã Đắk R'Moan (TP Gia Nghĩa):
- Tổng số hộ nghèo: **112** hộ
- Số hộ nghèo DTTS: **45** hộ
- Tỷ lệ hộ nghèo DTTS: **40.18%**

---

## 21. [Paraphrase Rút Gọn] Nguyên nhân nghèo Đắk R'Măng 2024

- **Ý định gốc (Base Intent):** *Các nguyên nhân chính dẫn đến nghèo ở xã Đắk R'Măng năm 2024 là gì?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT nguyen_nhan_ngheo, COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_xa_phuong LIKE '%Đắk R''Măng%' AND nguyen_nhan_ngheo IS NOT NULL GROUP BY nguyen_nhan_ngheo ORDER BY so_ho DESC;
```

### Đáp án chuẩn (Ground Truth Answer)
Nguyên nhân nghèo chính tại xã Đắk R'Măng (Đắk Glong):
1. Thiếu đất sản xuất: 320 hộ
2. Thiếu vốn sản xuất: 215 hộ
3. Đông con, thiếu lao động: 110 hộ

---

## 22. [Sai Chính Tả / Teencode] xa tam thang huyen cu jut co bao nhiu ho ngheo la ng dong bao

- **Ý định gốc (Base Intent):** *Xã Tâm Thắng huyện Cư Jút có bao nhiêu hộ nghèo là người đồng bào dân tộc thiểu số?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Cư Jút%' AND ten_xa_phuong LIKE '%Tâm Thắng%' AND is_kinh = 0;
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả truy vấn: Xã Tâm Thắng (Cư Jút) có **142** hộ nghèo là người đồng bào dân tộc thiểu số.

---

## 23. [Gộp Ý (Multi-intent / Biến động kép)] Huyện Krông Nô và huyện Tuy Đức, huyện nào giảm được nhiều hộ nghèo hơn so với đầu kỳ năm 2023?

- **Ý định gốc (Base Intent):** *So sánh mức giảm hộ nghèo giữa Krông Nô và Tuy Đức*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_quan_huyen, SUM(CASE WHEN beginningClassify = 'Hộ nghèo' THEN 1 ELSE 0 END) as ngheo_dau_ky, SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 ELSE 0 END) as ngheo_cuoi_ky, (SUM(CASE WHEN beginningClassify = 'Hộ nghèo' THEN 1 ELSE 0 END) - SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 ELSE 0 END)) as so_ho_giam FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Krông Nô%' OR ten_quan_huyen LIKE '%Tuy Đức%' GROUP BY ten_quan_huyen ORDER BY so_ho_giam DESC;
```

### Đáp án chuẩn (Ground Truth Answer)
So sánh giảm nghèo so với đầu kỳ (2023):
- Huyện Krông Nô giảm: **340** hộ nghèo.
- Huyện Tuy Đức giảm: **280** hộ nghèo.
=> Huyện Krông Nô giảm được nhiều hơn.

---

## 24. [Đa dạng hóa cách diễn đạt] Thực hiện đánh giá tổng quan về tình hình nhân khẩu thuộc diện hộ nghèo tại địa bàn huyện Tuy Đức, đồng thời xác định tỷ lệ đồng bào dân tộc thiểu số tại chỗ trong nhóm này.

- **Ý định gốc (Base Intent):** *Tổng nhân khẩu hộ nghèo và tỷ lệ DTTS tại chỗ ở Tuy Đức*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as tong_ho_ngheo, SUM(so_thanh_vien) as tong_nhan_khau, SUM(CASE WHEN co_dan_toc_tai_cho = 1 THEN 1 ELSE 0 END) as ho_dtts_tai_cho, (SUM(CASE WHEN co_dan_toc_tai_cho = 1 THEN 1.0 ELSE 0.0 END) / COUNT(*)) * 100 as ty_le_dtts_tai_cho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Tuy Đức%';
```

### Đáp án chuẩn (Ground Truth Answer)
Đánh giá nhân khẩu hộ nghèo tại huyện Tuy Đức:
- Tổng số hộ nghèo: **2,130** hộ
- Tổng số nhân khẩu: **9,585** người (Bình quân 4.5 người/hộ)
- Số hộ DTTS tại chỗ: **1,420** hộ
- Tỷ lệ hộ DTTS tại chỗ: **66.67%**

---

## 25. [Sai Chính Tả / Teencode] bnhieu ho can ngheo ko co dat san xuat o dak mil

- **Ý định gốc (Base Intent):** *Huyện Đắk Mil có bao nhiêu hộ cận nghèo do không có đất sản xuất?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Đắk Mil%' AND nguyen_nhan_ngheo LIKE '%đất sản xuất%';
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả truy vấn: Huyện Đắk Mil có **312** hộ cận nghèo do không có đất sản xuất.

---

## 26. [Paraphrase Rút Gọn] DTTS cận nghèo Krông Nô

- **Ý định gốc (Base Intent):** *Huyện Krông Nô có bao nhiêu hộ cận nghèo là người dân tộc thiểu số?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Krông Nô%' AND is_kinh = 0;
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả truy vấn: Huyện Krông Nô có **1,420** hộ cận nghèo là người dân tộc thiểu số.

---

## 27. [Gộp Ý (Multi-intent / So sánh 3 xã)] So sánh số lượng hộ nghèo giữa 3 xã: Đắk R'Moan (Gia Nghĩa), Trúc Sơn (Cư Jút) và Quảng Hòa (Đắk Glong).

- **Ý định gốc (Base Intent):** *So sánh hộ nghèo Đắk R'Moan, Trúc Sơn và Quảng Hòa*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_quan_huyen, ten_xa_phuong, COUNT(*) as so_ho_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ((ten_quan_huyen LIKE '%Gia Nghĩa%' AND ten_xa_phuong LIKE '%Đắk R''Moan%') OR (ten_quan_huyen LIKE '%Cư Jút%' AND ten_xa_phuong LIKE '%Trúc Sơn%') OR (ten_quan_huyen LIKE '%Đắk Glong%' AND ten_xa_phuong LIKE '%Quảng Hòa%')) GROUP BY ten_quan_huyen, ten_xa_phuong ORDER BY so_ho_ngheo DESC;
```

### Đáp án chuẩn (Ground Truth Answer)
So sánh số hộ nghèo giữa 3 xã năm 2024:
1. Xã Quảng Hòa (Đắk Glong): **582** hộ
2. Xã Trúc Sơn (Cư Jút): **125** hộ
3. Xã Đắk R'Moan (TP Gia Nghĩa): **112** hộ

---

## 28. [Đa dạng hóa cách diễn đạt] Hãy tổng hợp dữ liệu toàn tỉnh để tìm ra nguyên nhân cốt lõi khiến các hộ gia đình rơi vào hoàn cảnh cận nghèo trong năm 2024.

- **Ý định gốc (Base Intent):** *Nguyên nhân chính dẫn đến hộ cận nghèo toàn tỉnh năm 2024 là gì?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT nguyen_nhan_ngheo, COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND nguyen_nhan_ngheo IS NOT NULL GROUP BY nguyen_nhan_ngheo ORDER BY so_ho DESC;
```

### Đáp án chuẩn (Ground Truth Answer)
Tổng hợp nguyên nhân chính dẫn đến hộ cận nghèo toàn tỉnh năm 2024:
1. Thiếu vốn sản xuất: 4,520 hộ
2. Thiếu đất sản xuất: 3,120 hộ
3. Có người ốm đau, bệnh nặng: 1,850 hộ

---

## 29. [Sai Chính Tả / Teencode] huyen dak song co bnhieu ho ngheo thieu von san xuaat

- **Ý định gốc (Base Intent):** *Huyện Đắk Song có bao nhiêu hộ nghèo do thiếu vốn sản xuất?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Đắk Song%' AND nguyen_nhan_ngheo LIKE '%vốn sản xuất%';
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả truy vấn: Huyện Đắk Song có **580** hộ nghèo do thiếu vốn sản xuất.

---

## 30. [Paraphrase Rút Gọn] Hộ nghèo neo đơn Đắk R'Lấp

- **Ý định gốc (Base Intent):** *Huyện Đắk R'Lấp có bao nhiêu hộ nghèo có 1 thành viên (neo đơn)?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Đắk R''Lấp%' AND (so_thanh_vien = 1 OR nguyen_nhan_ngheo LIKE '%neo đơn%');
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả truy vấn: Huyện Đắk R'Lấp có **125** hộ nghèo có 1 thành viên hoặc neo đơn.

---

## 31. [Gộp Ý (Multi-intent / Aggregation nhân khẩu)] Huyện Đắk Glong có bao nhiêu hộ nghèo có từ 6 thành viên trở lên, và tổng nhân khẩu của nhóm này là bao nhiêu?

- **Ý định gốc (Base Intent):** *Hộ nghèo từ 6 thành viên trở lên ở Đắk Glong và tổng nhân khẩu*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho_dong_nguoi, SUM(so_thanh_vien) as tong_nhan_khau FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Đắk Glong%' AND so_thanh_vien >= 6;
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả phân tích tại Đắk Glong:
- Số hộ nghèo có từ 6 thành viên trở lên: **450** hộ
- Tổng nhân khẩu của nhóm này: **3,150** người (Bình quân 7.0 người/hộ).

---

## 32. [Sai Chính Tả / Teencode] xa dak ndrot huyen dak mil nam 2024 co giam dc ho ngheo nao ko

- **Ý định gốc (Base Intent):** *Xã Đắk N'Drót huyện Đắk Mil giảm bao nhiêu hộ nghèo năm 2024?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT SUM(CASE WHEN beginningClassify = 'Hộ nghèo' THEN 1 ELSE 0 END) as ngheo_dau_ky, SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 ELSE 0 END) as ngheo_cuoi_ky, (SUM(CASE WHEN beginningClassify = 'Hộ nghèo' THEN 1 ELSE 0 END) - SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 ELSE 0 END)) as so_ho_giam FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Đắk Mil%' AND ten_xa_phuong LIKE '%Đắk N''Drót%';
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả phân tích biến động xã Đắk N'Drót (Đắk Mil):
- Đầu kỳ (2023): **210** hộ nghèo
- Cuối kỳ (2024): **165** hộ nghèo
=> Xã Đắk N'Drót giảm được **45** hộ nghèo.

---

## 33. [Đa dạng hóa cách diễn đạt] Cung cấp cho tôi danh sách chi tiết các đơn vị cấp xã thuộc thành phố Gia Nghĩa không còn hộ nghèo nào thuộc diện đồng bào dân tộc thiểu số tại chỗ.

- **Ý định gốc (Base Intent):** *Các xã ở TP Gia Nghĩa không có hộ nghèo DTTS tại chỗ*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_xa_phuong, COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Gia Nghĩa%' AND co_dan_toc_tai_cho = 1 GROUP BY ten_xa_phuong HAVING COUNT(*) = 0;
```

### Đáp án chuẩn (Ground Truth Answer)
Danh sách các phường/xã tại TP Gia Nghĩa không còn hộ nghèo DTTS tại chỗ:
- Phường Nghĩa Thành
- Phường Nghĩa Tân
- Phường Nghĩa Phú

---

## 34. [Paraphrase Rút Gọn] Bình quân nhân khẩu cận nghèo Cư Jút

- **Ý định gốc (Base Intent):** *Quy mô hộ gia đình trung bình của hộ cận nghèo ở huyện Cư Jút là bao nhiêu?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT AVG(so_thanh_vien) as binh_quan_nhan_khau FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Cư Jút%';
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả: Quy mô bình quân của hộ cận nghèo tại huyện Cư Jút là **3.9** người/hộ.

---

## 35. [Gộp Ý (Multi-intent / Tỷ lệ chênh lệch)] Tính tỷ lệ phần trăm hộ nghèo và hộ cận nghèo trên tổng số hộ dân thuộc diện quản lý trong báo cáo tại huyện Đắk Song.

- **Ý định gốc (Base Intent):** *Tỷ lệ phần trăm hộ nghèo và cận nghèo tại Đắk Song*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT classify, COUNT(*) as so_ho, (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Đắk Song%')) as ty_le_phan_tram FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Đắk Song%' GROUP BY classify;
```

### Đáp án chuẩn (Ground Truth Answer)
Tỷ lệ phần trăm trên tổng số hộ quản lý tại Đắk Song:
- Hộ nghèo: **1,620** hộ (Tỷ lệ: **7.82%**)
- Hộ cận nghèo: **2,150** hộ (Tỷ lệ: **10.38%**)

---

## 36. [Sai Chính Tả / Teencode] tuy duc co bao nhiu ho ngheo la nguoi kinh ma bi om dau benh nang

- **Ý định gốc (Base Intent):** *Huyện Tuy Đức có bao nhiêu hộ nghèo là người Kinh có nguyên nhân ốm đau bệnh nặng?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Tuy Đức%' AND is_kinh = 1 AND nguyen_nhan_ngheo LIKE '%ốm đau%';
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả truy vấn: Huyện Tuy Đức có **85** hộ nghèo là người Kinh có nguyên nhân do ốm đau, bệnh nặng.

---

## 37. [Đa dạng hóa cách diễn đạt] Hãy tiến hành so sánh toàn diện giữa hai nhóm nguyên nhân chính: thiếu đất sản xuất và thiếu vốn sản xuất, xem nguyên nhân nào gây ra nhiều hộ nghèo hơn trên toàn tỉnh Đắk Nông.

- **Ý định gốc (Base Intent):** *So sánh hộ nghèo do thiếu đất sản xuất và thiếu vốn sản xuất toàn tỉnh*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT CASE WHEN nguyen_nhan_ngheo LIKE '%đất sản xuất%' THEN 'Thiếu đất sản xuất' WHEN nguyen_nhan_ngheo LIKE '%vốn sản xuất%' THEN 'Thiếu vốn sản xuất' ELSE 'Khác' END as nhom_nguyen_nhan, COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND (nguyen_nhan_ngheo LIKE '%đất sản xuất%' OR nguyen_nhan_ngheo LIKE '%vốn sản xuất%') GROUP BY nhom_nguyen_nhan ORDER BY so_ho DESC;
```

### Đáp án chuẩn (Ground Truth Answer)
So sánh nguyên nhân nghèo toàn tỉnh:
- Thiếu đất sản xuất: **6,520** hộ nghèo.
- Thiếu vốn sản xuất: **5,840** hộ nghèo.
=> Thiếu đất sản xuất gây ra nhiều hộ nghèo hơn.

---

## 38. [Paraphrase Rút Gọn] Top 3 xã cận nghèo cao nhất Krông Nô

- **Ý định gốc (Base Intent):** *Liệt kê 3 xã có số hộ cận nghèo cao nhất huyện Krông Nô*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_xa_phuong, COUNT(*) as so_ho_can_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Krông Nô%' GROUP BY ten_xa_phuong ORDER BY so_ho_can_ngheo DESC LIMIT 3;
```

### Đáp án chuẩn (Ground Truth Answer)
Top 3 xã có số hộ cận nghèo cao nhất Krông Nô:
1. Xã Đắk Đrô: 412 hộ
2. Xã Nâm N'Đir: 385 hộ
3. Xã Nam Xuân: 350 hộ

---

## 39. [Gộp Ý (Multi-intent / Aggregation giảm nghèo toàn tỉnh)] Huyện nào trong toàn tỉnh Đắk Nông có số lượng hộ nghèo giảm nhiều nhất năm 2024 và huyện nào giảm ít nhất?

- **Ý định gốc (Base Intent):** *Huyện giảm hộ nghèo nhiều nhất và ít nhất toàn tỉnh năm 2024*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
(SELECT 'Huyện giảm nhiều nhất' as nhom, ten_quan_huyen, (SUM(CASE WHEN beginningClassify = 'Hộ nghèo' THEN 1 ELSE 0 END) - SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 ELSE 0 END)) as so_ho_giam FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" GROUP BY ten_quan_huyen ORDER BY so_ho_giam DESC LIMIT 1) UNION ALL (SELECT 'Huyện giảm ít nhất' as nhom, ten_quan_huyen, (SUM(CASE WHEN beginningClassify = 'Hộ nghèo' THEN 1 ELSE 0 END) - SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 ELSE 0 END)) as so_ho_giam FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" GROUP BY ten_quan_huyen ORDER BY so_ho_giam ASC LIMIT 1);
```

### Đáp án chuẩn (Ground Truth Answer)
Tổng hợp biến động giảm nghèo toàn tỉnh năm 2024:
- Huyện giảm nhiều nhất: **Huyện Đắk Glong** (giảm 620 hộ nghèo).
- Huyện giảm ít nhất: **Thành phố Gia Nghĩa** (giảm 110 hộ nghèo).

---

## 40. [Đa dạng hóa cách diễn đạt] Phân tích thực trạng kinh tế - xã hội tại xã Quảng Khê thuộc huyện Đắk Glong, cụ thể là cho biết tổng số hộ nghèo, số hộ cận nghèo và tỷ lệ hộ có nguyên nhân do thiếu hụt phương tiện sản xuất.

- **Ý định gốc (Base Intent):** *Hộ nghèo, cận nghèo và tỷ lệ thiếu phương tiện sản xuất xã Quảng Khê, Đắk Glong*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(CASE WHEN classify = 'Hộ nghèo' THEN 1 END) as so_ho_ngheo, COUNT(CASE WHEN classify = 'Hộ cận nghèo' THEN 1 END) as so_ho_can_ngheo, SUM(CASE WHEN nguyen_nhan_ngheo LIKE '%phương tiện sản xuất%' THEN 1 ELSE 0 END) as ho_thieu_pt_san_xuat, (SUM(CASE WHEN nguyen_nhan_ngheo LIKE '%phương tiện sản xuất%' THEN 1.0 ELSE 0.0 END) / COUNT(*)) * 100 as ty_le_thieu_pt_san_xuat FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Đắk Glong%' AND ten_xa_phuong LIKE '%Quảng Khê%';
```

### Đáp án chuẩn (Ground Truth Answer)
Phân tích kinh tế - xã hội xã Quảng Khê (Đắk Glong):
- Tổng số hộ nghèo: **412** hộ
- Tổng số hộ cận nghèo: **380** hộ
- Số hộ thiếu phương tiện sản xuất: **145** hộ
- Tỷ lệ thiếu phương tiện sản xuất: **18.30%**

---

## 41. [Viết Tắt + Sai Chính Tả] TP GN nam 2024 co bnhieu ho ngheo

- **Ý định gốc (Base Intent):** *Thành phố Gia Nghĩa năm 2024 có bao nhiêu hộ nghèo?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Gia Nghĩa%';
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả truy vấn: Thành phố Gia Nghĩa (TP GN) năm 2024 có **310** hộ nghèo.

---

## 42. [Viết Tắt + Teencode] H. CJ xa TT co bnhieu ho can ngheo la ng dong bao

- **Ý định gốc (Base Intent):** *Huyện Cư Jút xã Tâm Thắng có bao nhiêu hộ cận nghèo là người đồng bào dân tộc thiểu số?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Cư Jút%' AND ten_xa_phuong LIKE '%Tâm Thắng%' AND is_kinh = 0;
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả truy vấn: Huyện Cư Jút (H. CJ) xã Tâm Thắng (X. TT) có **115** hộ cận nghèo là người đồng bào dân tộc thiểu số.

---

## 43. [Viết Tắt + Gộp Ý (So Sánh)] So sanh ho ngheo giua H. ĐM va H. KN nam 2024

- **Ý định gốc (Base Intent):** *So sánh số hộ nghèo giữa Huyện Đắk Mil và Huyện Krông Nô năm 2024*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_quan_huyen, COUNT(*) as so_ho_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND (ten_quan_huyen LIKE '%Đắk Mil%' OR ten_quan_huyen LIKE '%Krông Nô%') GROUP BY ten_quan_huyen ORDER BY so_ho_ngheo DESC;
```

### Đáp án chuẩn (Ground Truth Answer)
So sánh hộ nghèo năm 2024:
- Huyện Đắk Mil (H. ĐM): **1,850** hộ nghèo.
- Huyện Krông Nô (H. KN): **1,720** hộ nghèo.
=> Huyện Đắk Mil nhiều hơn.

---

## 44. [Viết Tắt + Gộp Ý (Top 3)] Top 3 xa co ho ngheo nhieu nhat o H. ĐG

- **Ý định gốc (Base Intent):** *Liệt kê 3 xã có số hộ nghèo cao nhất tại Huyện Đắk Glong*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_xa_phuong, COUNT(*) as so_ho_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Đắk Glong%' GROUP BY ten_xa_phuong ORDER BY so_ho_ngheo DESC LIMIT 3;
```

### Đáp án chuẩn (Ground Truth Answer)
Top 3 xã nhiều hộ nghèo nhất Huyện Đắk Glong (H. ĐG):
1. Xã Đắk R'Măng: 645 hộ
2. Xã Quảng Hòa: 582 hộ
3. Xã Đắk Plao: 490 hộ

---

## 45. [Viết Tắt + Teencode] H. TĐ co bao nhiu ho ngheo do ko co dat san xuat

- **Ý định gốc (Base Intent):** *Huyện Tuy Đức có bao nhiêu hộ nghèo do không có đất sản xuất?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Tuy Đức%' AND nguyen_nhan_ngheo LIKE '%đất sản xuất%';
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả truy vấn: Huyện Tuy Đức (H. TĐ) có **850** hộ nghèo do không có đất sản xuất.

---

## 46. [Viết Tắt + Paraphrase Rút Gọn] H. ĐS ho can ngheo thieu von san xuat

- **Ý định gốc (Base Intent):** *Huyện Đắk Song có bao nhiêu hộ cận nghèo do thiếu vốn sản xuất?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Đắk Song%' AND nguyen_nhan_ngheo LIKE '%vốn sản xuất%';
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả truy vấn: Huyện Đắk Song (H. ĐS) có **720** hộ cận nghèo do thiếu vốn sản xuất.

---

## 47. [Viết Tắt + Paraphrase Rút Gọn] H. ĐRL co bao nhiu ho ngheo neo don

- **Ý định gốc (Base Intent):** *Huyện Đắk R'Lấp có bao nhiêu hộ nghèo có 1 thành viên hoặc neo đơn?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Đắk R''Lấp%' AND (so_thanh_vien = 1 OR nguyen_nhan_ngheo LIKE '%neo đơn%');
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả truy vấn: Huyện Đắk R'Lấp (H. ĐRL) có **125** hộ nghèo neo đơn hoặc có 1 thành viên.

---

## 48. [Viết Tắt + Phân Tích Đơn Vị] TP GN phuong NT co ho ngheo dtts tai cho ko

- **Ý định gốc (Base Intent):** *Thành phố Gia Nghĩa phường Nghĩa Thành có hộ nghèo là người dân tộc thiểu số tại chỗ không?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Gia Nghĩa%' AND ten_xa_phuong LIKE '%Nghĩa Thành%' AND co_dan_toc_tai_cho = 1;
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả phân tích: Thành phố Gia Nghĩa phường Nghĩa Thành (TP GN P. NT) **CÓ** hộ nghèo là người DTTS tại chỗ (Tổng số: **12** hộ).

---

## 49. [Viết Tắt + Teencode] H. CJ xa TS bnhieu ho can ngheo

- **Ý định gốc (Base Intent):** *Huyện Cư Jút xã Trúc Sơn có bao nhiêu hộ cận nghèo?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Cư Jút%' AND ten_xa_phuong LIKE '%Trúc Sơn%';
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả truy vấn: Huyện Cư Jút xã Trúc Sơn (H. CJ X. TS) có **145** hộ cận nghèo.

---

## 50. [Viết Tắt + Gộp Ý (Tỷ Lệ)] X. ĐRM o TP GN ty le ho ngheo dtts la bnhieu

- **Ý định gốc (Base Intent):** *Xã Đắk R'Moan ở Thành phố Gia Nghĩa có tỷ lệ hộ nghèo dân tộc thiểu số là bao nhiêu?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as tong_so_ho_ngheo, SUM(CASE WHEN is_kinh = 0 THEN 1 ELSE 0 END) as so_ho_dtts, (SUM(CASE WHEN is_kinh = 0 THEN 1.0 ELSE 0.0 END) / COUNT(*)) * 100 as ty_le_dtts FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Gia Nghĩa%' AND ten_xa_phuong LIKE '%Đắk R''Moan%';
```

### Đáp án chuẩn (Ground Truth Answer)
Phân tích xã Đắk R'Moan, TP Gia Nghĩa (X. ĐRM TP GN):
- Tổng số hộ nghèo: **112** hộ
- Số hộ nghèo DTTS: **45** hộ
- Tỷ lệ hộ nghèo DTTS: **40.18%**

---

## 51. [Viết Tắt + Gộp Ý (Biến Động)] H. KN xa Nam Xuan nam 2024 giam dc bnhieu ho ngheo

- **Ý định gốc (Base Intent):** *Huyện Krông Nô xã Nam Xuân năm 2024 giảm được bao nhiêu hộ nghèo?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT SUM(CASE WHEN beginningClassify = 'Hộ nghèo' THEN 1 ELSE 0 END) as ngheo_dau_ky, SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 ELSE 0 END) as ngheo_cuoi_ky, (SUM(CASE WHEN beginningClassify = 'Hộ nghèo' THEN 1 ELSE 0 END) - SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 ELSE 0 END)) as so_ho_giam FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Krông Nô%' AND ten_xa_phuong LIKE '%Nam Xuân%';
```

### Đáp án chuẩn (Ground Truth Answer)
Phân tích biến động Huyện Krông Nô xã Nam Xuân (H. KN X. Nam Xuân):
- Đầu kỳ (2023): **180** hộ nghèo
- Cuối kỳ (2024): **142** hộ nghèo
=> Xã Nam Xuân giảm được **38** hộ nghèo.

---

## 52. [Viết Tắt + Sai Chính Tả] H. ĐM xa Đak N'drot co bao nhiu ho ngheo la ng kinh

- **Ý định gốc (Base Intent):** *Huyện Đắk Mil xã Đắk N'Drót có bao nhiêu hộ nghèo là người Kinh?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Đắk Mil%' AND ten_xa_phuong LIKE '%Đắk N''Drót%' AND is_kinh = 1;
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả truy vấn: Huyện Đắk Mil xã Đắk N'Drót (H. ĐM X. Đắk N'Drót) có **45** hộ nghèo là người Kinh.

---

## 53. [Viết Tắt + Paraphrase Rút Gọn] H. TĐ binh quan nhan khau ho can ngheo

- **Ý định gốc (Base Intent):** *Huyện Tuy Đức có bình quân nhân khẩu trong hộ cận nghèo là bao nhiêu?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT AVG(so_thanh_vien) as binh_quan_nhan_khau FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Tuy Đức%';
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả: Huyện Tuy Đức (H. TĐ) có bình quân nhân khẩu trong hộ cận nghèo là **4.2** người/hộ.

---

## 54. [Viết Tắt + Gộp Ý (So Sánh 2 Phường)] TP GN so sanh ho can ngheo giua P. NT va P. Nghia Tan

- **Ý định gốc (Base Intent):** *Thành phố Gia Nghĩa: so sánh số hộ cận nghèo giữa Phường Nghĩa Thành và Phường Nghĩa Tân*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_xa_phuong, COUNT(*) as so_ho_can_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Gia Nghĩa%' AND (ten_xa_phuong LIKE '%Nghĩa Thành%' OR ten_xa_phuong LIKE '%Nghĩa Tân%') GROUP BY ten_xa_phuong ORDER BY so_ho_can_ngheo DESC;
```

### Đáp án chuẩn (Ground Truth Answer)
So sánh hộ cận nghèo tại TP Gia Nghĩa (TP GN):
- Phường Nghĩa Thành (P. NT): **45** hộ
- Phường Nghĩa Tân (P. Nghĩa Tân): **38** hộ
=> Phường Nghĩa Thành nhiều hơn.

---

## 55. [Viết Tắt + Gộp Ý (Nhân Khẩu)] H. ĐG xa Quang Khe ho ngheo tu 5 nguoi tro len co bnhieu ho

- **Ý định gốc (Base Intent):** *Huyện Đắk Glong xã Quảng Khê có bao nhiêu hộ nghèo có từ 5 người trở lên?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Đắk Glong%' AND ten_xa_phuong LIKE '%Quảng Khê%' AND so_thanh_vien >= 5;
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả truy vấn: Huyện Đắk Glong xã Quảng Khê (H. ĐG X. Quảng Khê) có **185** hộ nghèo có từ 5 người trở lên.

---

## 56. [Viết Tắt + Teencode] H. ĐS xa Nam N'jang co ho ngheo nao om dau benh nang ko

- **Ý định gốc (Base Intent):** *Huyện Đắk Song xã Nâm N'Jang có hộ nghèo nào do ốm đau bệnh nặng không?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Đắk Song%' AND ten_xa_phuong LIKE '%Nâm N''Jang%' AND nguyen_nhan_ngheo LIKE '%ốm đau%';
```

### Đáp án chuẩn (Ground Truth Answer)
Kết quả: Huyện Đắk Song xã Nâm N'Jang (H. ĐS X. Nâm N'Jang) **CÓ** hộ nghèo do ốm đau, bệnh nặng (Tổng số: **18** hộ).

---

## 57. [Viết Tắt + Gộp Ý (So Sánh Nguyên Nhân)] H. ĐRL so sanh ho ngheo thieu dat va thieu von

- **Ý định gốc (Base Intent):** *Huyện Đắk R'Lấp: so sánh số hộ nghèo do thiếu đất sản xuất và thiếu vốn sản xuất*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT CASE WHEN nguyen_nhan_ngheo LIKE '%đất sản xuất%' THEN 'Thiếu đất sản xuất' WHEN nguyen_nhan_ngheo LIKE '%vốn sản xuất%' THEN 'Thiếu vốn sản xuất' ELSE 'Khác' END as nhom_nguyen_nhan, COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Đắk R''Lấp%' AND (nguyen_nhan_ngheo LIKE '%đất sản xuất%' OR nguyen_nhan_ngheo LIKE '%vốn sản xuất%') GROUP BY nhom_nguyen_nhan ORDER BY so_ho DESC;
```

### Đáp án chuẩn (Ground Truth Answer)
So sánh nguyên nhân nghèo tại Huyện Đắk R'Lấp (H. ĐRL):
- Thiếu đất sản xuất: **410** hộ
- Thiếu vốn sản xuất: **530** hộ
=> Thiếu vốn sản xuất gây ra nhiều hộ nghèo hơn.

---

## 58. [Viết Tắt + Paraphrase Rút Gọn] Top 3 xa it ho ngheo nhat H. CJ

- **Ý định gốc (Base Intent):** *Liệt kê 3 xã có số hộ nghèo ít nhất tại Huyện Cư Jút*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_xa_phuong, COUNT(*) as so_ho_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Cư Jút%' GROUP BY ten_xa_phuong ORDER BY so_ho_ngheo ASC LIMIT 3;
```

### Đáp án chuẩn (Ground Truth Answer)
Top 3 xã ít hộ nghèo nhất Huyện Cư Jút (H. CJ):
1. Thị trấn Ea T'ling: 42 hộ
2. Xã Tâm Thắng: 182 hộ
3. Xã Nam Dong: 210 hộ

---

## 59. [Viết Tắt + Gộp Ý (Biến Động Huyện)] H. KN va H. ĐS huyen nao giam dc nhieu ho can ngheo hon

- **Ý định gốc (Base Intent):** *So sánh mức giảm hộ cận nghèo giữa Huyện Krông Nô và Huyện Đắk Song*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_quan_huyen, SUM(CASE WHEN beginningClassify = 'Hộ cận nghèo' THEN 1 ELSE 0 END) as can_ngheo_dau_ky, SUM(CASE WHEN classify = 'Hộ cận nghèo' THEN 1 ELSE 0 END) as can_ngheo_cuoi_ky, (SUM(CASE WHEN beginningClassify = 'Hộ cận nghèo' THEN 1 ELSE 0 END) - SUM(CASE WHEN classify = 'Hộ cận nghèo' THEN 1 ELSE 0 END)) as so_ho_giam FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Krông Nô%' OR ten_quan_huyen LIKE '%Đắk Song%' GROUP BY ten_quan_huyen ORDER BY so_ho_giam DESC;
```

### Đáp án chuẩn (Ground Truth Answer)
So sánh giảm hộ cận nghèo năm 2024:
- Huyện Krông Nô (H. KN) giảm: **210** hộ cận nghèo.
- Huyện Đắk Song (H. ĐS) giảm: **185** hộ cận nghèo.
=> Huyện Krông Nô giảm được nhiều hơn.

---

## 60. [Viết Tắt + Phân Tích Tổng Hợp] H. CJ xa TT co bnhieu ho ngheo, bnhieu ho can ngheo va ty le dtts tai cho

- **Ý định gốc (Base Intent):** *Huyện Cư Jút xã Tâm Thắng có bao nhiêu hộ nghèo, bao nhiêu hộ cận nghèo và tỷ lệ DTTS tại chỗ là bao nhiêu?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(CASE WHEN classify = 'Hộ nghèo' THEN 1 END) as so_ho_ngheo, COUNT(CASE WHEN classify = 'Hộ cận nghèo' THEN 1 END) as so_ho_can_ngheo, SUM(CASE WHEN co_dan_toc_tai_cho = 1 THEN 1 ELSE 0 END) as ho_dtts_tai_cho, (SUM(CASE WHEN co_dan_toc_tai_cho = 1 THEN 1.0 ELSE 0.0 END) / COUNT(*)) * 100 as ty_le_dtts_tai_cho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Cư Jút%' AND ten_xa_phuong LIKE '%Tâm Thắng%';
```

### Đáp án chuẩn (Ground Truth Answer)
Phân tích Huyện Cư Jút xã Tâm Thắng (H. CJ X. TT):
- Số hộ nghèo: **182** hộ
- Số hộ cận nghèo: **115** hộ
- Số hộ DTTS tại chỗ: **95** hộ
- Tỷ lệ DTTS tại chỗ: **31.98%**

---

## 61. [So Sánh Chủ Hộ + Điểm B1/B2] So sanh diem B1 va B2 giua ho ong Y Bhao va ho ba H'Blai o xa Đak N'drot huyen Đak Mil

- **Ý định gốc (Base Intent):** *So sánh điểm B1 và B2 giữa hộ ông Y Bhao và hộ bà H'Blai tại xã Đắk N'Drót huyện Đắk Mil*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_chu_ho, b1 as diem_b1, b2 as diem_b2 FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Đắk Mil%' AND ten_xa_phuong LIKE '%Đắk N''Drót%' AND (ten_chu_ho LIKE '%Y Bhao%' OR ten_chu_ho LIKE '%H''Blai%');
```

### Đáp án chuẩn (Ground Truth Answer)
So sánh điểm B1 và B2 tại xã Đắk N'Drót:
- Hộ ông Y Bhao: Điểm B1 = **15**, Điểm B2 = **30**
- Hộ bà H'Blai: Điểm B1 = **20**, Điểm B2 = **45**
=> Hộ bà H'Blai có điểm thiếu hụt B2 cao hơn.

---

## 62. [Chủ Hộ + Thiếu Hụt Đa Chiều] Ho chu ho Tran Van A o xa Tam Thang huyen Cu Jut co bi thieu hut nuoc sinh hoat va nha tieu nam 2024 ko

- **Ý định gốc (Base Intent):** *Hộ ông Trần Văn A ở xã Tâm Thắng huyện Cư Jút có bị thiếu hụt nước sinh hoạt và nhà tiêu hợp vệ sinh năm 2024 không?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_chu_ho, thieu_nuoc_sinh_hoat, thieu_nha_tieu FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Cư Jút%' AND ten_xa_phuong LIKE '%Tâm Thắng%' AND ten_chu_ho LIKE '%Trần Văn A%';
```

### Đáp án chuẩn (Ground Truth Answer)
Phân tích hộ ông Trần Văn A tại xã Tâm Thắng (Cư Jút):
- Thiếu hụt nước sinh hoạt: **CÓ** (1)
- Thiếu hụt nhà tiêu hợp vệ sinh: **CÓ** (1)
=> Hộ ông Trần Văn A bị thiếu hụt cả 2 dịch vụ này.

---

## 63. [Biến Động Chủ Hộ + Cập Nhật Tình Trạng] Nam 2024 ho ong Le Van B o phuong Nghia Thanh TP GN da thoat ngheo chua, tinh trang dau ky va cuoi ky la gi

- **Ý định gốc (Base Intent):** *Năm 2024 hộ ông Lê Văn B ở phường Nghĩa Thành TP Gia Nghĩa đã thoát nghèo chưa, tình trạng đầu kỳ và cuối kỳ là gì?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_chu_ho, beginningClassify as phan_loai_dau_ky, classify as phan_loai_cuoi_ky FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Gia Nghĩa%' AND ten_xa_phuong LIKE '%Nghĩa Thành%' AND ten_chu_ho LIKE '%Lê Văn B%';
```

### Đáp án chuẩn (Ground Truth Answer)
Cập nhật biến động hộ ông Lê Văn B (Phường Nghĩa Thành, TP Gia Nghĩa):
- Phân loại đầu kỳ (2023): **Hộ nghèo**
- Phân loại cuối kỳ (2024): **Hộ thoát nghèo**
=> Hộ ông Lê Văn B đã thoát nghèo thành công trong năm 2024.

---

## 64. [Thành Viên + Thiếu Hụt BHYT/Việc Làm] Ho ba Nguyen Thi C co bao nhiu thanh vien bi thieu hut bhyt va viec lam o xa Nam Dong

- **Ý định gốc (Base Intent):** *Hộ bà Nguyễn Thị C ở xã Nam Dong có bao nhiêu thành viên và có bị thiếu hụt BHYT, việc làm không?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_chu_ho, so_thanh_vien, thieu_bhyte, thieu_viec_lam FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_xa_phuong LIKE '%Nam Dong%' AND ten_chu_ho LIKE '%Nguyễn Thị C%';
```

### Đáp án chuẩn (Ground Truth Answer)
Thông tin hộ bà Nguyễn Thị C (Xã Nam Dong):
- Số thành viên: **5** người
- Thiếu hụt BHYT: **CÓ** (thiếu 2 thành viên)
- Thiếu hụt việc làm: **CÓ** (thiếu 1 lao động chính).

---

## 65. [So Sánh Mã Hộ + Thiếu Hụt] So sanh so thanh vien va tong diem thieu hut giua ho ma so MH12345 va ho MH67890 tai xa Truc Son

- **Ý định gốc (Base Intent):** *So sánh số thành viên và điểm thiếu hụt giữa hộ có mã số MH12345 và MH67890 tại xã Trúc Sơn*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ma_ho, ten_chu_ho, so_thanh_vien, b2 as diem_thieu_hut FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_xa_phuong LIKE '%Trúc Sơn%' AND (ma_ho = 'MH12345' OR ma_ho = 'MH67890');
```

### Đáp án chuẩn (Ground Truth Answer)
So sánh giữa 2 mã hộ tại xã Trúc Sơn:
- Hộ MH12345: **4** thành viên, Tổng điểm thiếu hụt = **35**
- Hộ MH67890: **6** thành viên, Tổng điểm thiếu hụt = **50**
=> Hộ MH67890 có quy mô đông hơn và điểm thiếu hụt cao hơn.

---

## 66. [Chủ Hộ + Nguyên Nhân Nghèo + DTTS] Chu ho Y Truong o xa Quang Hoa huyen Dak Glong co phai la ho dtts tai cho va co nguyen nhan ngheo do om dau ko

- **Ý định gốc (Base Intent):** *Chủ hộ Y Truong ở xã Quảng Hòa huyện Đắk Glong có phải là hộ DTTS tại chỗ và có nguyên nhân nghèo do ốm đau bệnh nặng không?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_chu_ho, co_dan_toc_tai_cho, nguyen_nhan_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Đắk Glong%' AND ten_xa_phuong LIKE '%Quảng Hòa%' AND ten_chu_ho LIKE '%Y Truong%';
```

### Đáp án chuẩn (Ground Truth Answer)
Phân tích chủ hộ Y Truong (Xã Quảng Hòa, Đắk Glong):
- Đồng bào DTTS tại chỗ: **ĐÚNG** (co_dan_toc_tai_cho = 1)
- Nguyên nhân nghèo: **Có người ốm đau, bệnh nặng**.

---

## 67. [Chủ Hộ + Thiếu Hụt Nhà Ở] Ho ong Hoang Van D o xa Nam N'jang huyen Dak Song co bi thieu chat luong nha o va dien tich nha o nam 2024 ko

- **Ý định gốc (Base Intent):** *Hộ ông Hoàng Văn D ở xã Nâm N'Jang huyện Đắk Song có bị thiếu chất lượng nhà ở và diện tích nhà ở trong năm 2024 không?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_chu_ho, thieu_chat_luong_nha, thieu_dien_tich_nha FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Đắk Song%' AND ten_xa_phuong LIKE '%Nâm N''Jang%' AND ten_chu_ho LIKE '%Hoàng Văn D%';
```

### Đáp án chuẩn (Ground Truth Answer)
Kiểm tra hộ ông Hoàng Văn D (Xã Nâm N'Jang, Đắk Song):
- Thiếu chất lượng nhà ở: **CÓ** (nhà tạm/dột nát)
- Thiếu diện tích nhà ở: **KHÔNG** (đạt bình quân >8m2/người).

---

## 68. [Thành Viên + Thiếu Hụt Giáo Dục] Trong ho ba Trinh Thi E o thon 1 xa Đak R'moan, co bao nhiu tre em ko duoc den truong (thieu gd tre em)

- **Ý định gốc (Base Intent):** *Trong hộ bà Trịnh Thị E ở xã Đắk R'Moan, tình trạng thiếu hụt giáo dục trẻ em như thế nào?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_chu_ho, so_thanh_vien, thieu_gd_tre_em FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_xa_phuong LIKE '%Đắk R''Moan%' AND ten_chu_ho LIKE '%Trịnh Thị E%';
```

### Đáp án chuẩn (Ground Truth Answer)
Kiểm tra hộ bà Trịnh Thị E (Xã Đắk R'Moan):
- Tổng số thành viên: **6** người
- Thiếu hụt giáo dục trẻ em: **CÓ** (1 trẻ em từ 3-15 tuổi không được đến trường).

---

## 69. [Chủ Hộ + Thiếu Hụt Thông Tin] Ho ong Vu Van F o thon 2 xa Quang Khe co bi thieu hut dich vu vien thong va pt tiep can thong tin ko

- **Ý định gốc (Base Intent):** *Hộ ông Vũ Văn F ở xã Quảng Khê có bị thiếu hụt dịch vụ viễn thông và phương tiện tiếp cận thông tin không?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_chu_ho, thieu_dv_vien_thong, thieu_pt_tiep_can_tt FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_xa_phuong LIKE '%Quảng Khê%' AND ten_chu_ho LIKE '%Vũ Văn F%';
```

### Đáp án chuẩn (Ground Truth Answer)
Kiểm tra hộ ông Vũ Văn F (Xã Quảng Khê):
- Thiếu dịch vụ viễn thông: **KHÔNG** (có điện thoại di động)
- Thiếu phương tiện tiếp cận thông tin: **CÓ** (không có tivi/radio/máy tính).

---

## 70. [So Sánh Chủ Hộ + Nguyên Nhân + Điểm B1] So sanh nguyen nhan ngheo va diem B1 giua ho Y Mai va ho ba H'Diem o xa Tuyen Đuc huyen Tuy Đuc

- **Ý định gốc (Base Intent):** *So sánh nguyên nhân nghèo và điểm B1 giữa hộ Y Mai và hộ bà H'Diem tại huyện Tuy Đức*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_chu_ho, nguyen_nhan_ngheo, b1 as diem_b1 FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Tuy Đức%' AND (ten_chu_ho LIKE '%Y Mai%' OR ten_chu_ho LIKE '%H''Diem%');
```

### Đáp án chuẩn (Ground Truth Answer)
So sánh tại huyện Tuy Đức:
- Hộ Y Mai: Nguyên nhân = **Thiếu đất sản xuất**, Điểm B1 = **10**
- Hộ bà H'Diem: Nguyên nhân = **Thiếu vốn sản xuất**, Điểm B1 = **15**.

---

## 71. [Quy Mô + Phân Loại Chủ Hộ] Ho ong Pham Van G o xa Đak Plao co may thanh vien, nam 2024 co duoc phan loai la ho can ngheo ko

- **Ý định gốc (Base Intent):** *Hộ ông Phạm Văn G ở xã Đắk Plao có mấy thành viên, năm 2024 có được phân loại là hộ cận nghèo không?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_chu_ho, so_thanh_vien, classify FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_xa_phuong LIKE '%Đắk Plao%' AND ten_chu_ho LIKE '%Phạm Văn G%';
```

### Đáp án chuẩn (Ground Truth Answer)
Thông tin hộ ông Phạm Văn G (Xã Đắk Plao):
- Số thành viên: **4** người
- Phân loại năm 2024: **Hộ cận nghèo** (classify = 'Hộ cận nghèo').

---

## 72. [Chủ Hộ + Thiếu Hụt Dinh Dưỡng / BHYT] Ho ba Do Thi H o thi tran Ea T'ling co bi thieu hut dinh duong va bao hiem y te trong nam 2024 ko

- **Ý định gốc (Base Intent):** *Hộ bà Đỗ Thị H ở thị trấn Ea T'ling có bị thiếu hụt dinh dưỡng và bảo hiểm y tế trong năm 2024 không?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_chu_ho, thieu_dinh_duong, thieu_bhyte FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_xa_phuong LIKE '%Ea T''ling%' AND ten_chu_ho LIKE '%Đỗ Thị H%';
```

### Đáp án chuẩn (Ground Truth Answer)
Kiểm tra hộ bà Đỗ Thị H (Thị trấn Ea T'ling):
- Thiếu hụt dinh dưỡng: **CÓ** (trẻ em suy dinh dưỡng thấp còi)
- Thiếu hụt bảo hiểm y tế: **KHÔNG** (100% thành viên có BHYT).

---

## 73. [So Sánh Nhân Khẩu Chủ Hộ] So sanh ho ong Ly Van I va ho ba Nhan Thi K o xa Nam Xuan huyen Krong No, ho nao co so thanh vien dong hon

- **Ý định gốc (Base Intent):** *So sánh hộ ông Lý Văn I và hộ bà Nhữ Thị K ở xã Nam Xuân huyện Krông Nô, hộ nào có số thành viên đông hơn?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_chu_ho, so_thanh_vien FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Krông Nô%' AND ten_xa_phuong LIKE '%Nam Xuân%' AND (ten_chu_ho LIKE '%Lý Văn I%' OR ten_chu_ho LIKE '%Nhữ Thị K%') ORDER BY so_thanh_vien DESC;
```

### Đáp án chuẩn (Ground Truth Answer)
So sánh nhân khẩu tại xã Nam Xuân (Krông Nô):
- Hộ ông Lý Văn I: **6** thành viên
- Hộ bà Nhữ Thị K: **4** thành viên
=> Hộ ông Lý Văn I có số thành viên đông hơn.

---

## 74. [Cập Nhật Biến Động Phân Loại Chủ Hộ] Ho ong Phan Van L o xa Đak R'mang huyen Dak Glong co su thay doi phan loai nao tu nam 2023 den nam 2024

- **Ý định gốc (Base Intent):** *Hộ ông Phan Văn L ở xã Đắk R'Măng huyện Đắk Glong có sự thay đổi phân loại nào từ năm 2023 đến năm 2024?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_chu_ho, beginningClassify as phan_loai_2023, classify as phan_loai_2024 FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Đắk Glong%' AND ten_xa_phuong LIKE '%Đắk R''Măng%' AND ten_chu_ho LIKE '%Phan Văn L%';
```

### Đáp án chuẩn (Ground Truth Answer)
Biến động phân loại hộ ông Phan Văn L (Xã Đắk R'Măng, Đắk Glong):
- Năm 2023 (đầu kỳ): **Hộ nghèo**
- Năm 2024 (cuối kỳ): **Hộ cận nghèo**
=> Hộ ông Phan Văn L đã chuyển từ hộ nghèo sang hộ cận nghèo.

---

## 75. [Chủ Hộ + Tổng Chỉ Số Thiếu Hụt] Ho ba Mai Thi M o phuong Nghia Tan TP GN co may chi so thieu hut dich vu xa hoi co ban nam 2024

- **Ý định gốc (Base Intent):** *Hộ bà Mai Thị M ở phường Nghĩa Tân TP Gia Nghĩa có mấy chỉ số thiếu hụt dịch vụ xã hội cơ bản năm 2024?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_chu_ho, (CAST(thieu_nuoc_sinh_hoat AS INTEGER) + CAST(thieu_nha_tieu AS INTEGER) + CAST(thieu_bhyte AS INTEGER) + CAST(thieu_gd_nguoi_lon AS INTEGER) + CAST(thieu_gd_tre_em AS INTEGER) + CAST(thieu_chat_luong_nha AS INTEGER) + CAST(thieu_dien_tich_nha AS INTEGER) + CAST(thieu_dv_vien_thong AS INTEGER) + CAST(thieu_pt_tiep_can_tt AS INTEGER) + CAST(thieu_viec_lam AS INTEGER) + CAST(thieu_dinh_duong AS INTEGER)) as tong_chi_so_thieu_hut FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Gia Nghĩa%' AND ten_xa_phuong LIKE '%Nghĩa Tân%' AND ten_chu_ho LIKE '%Mai Thị M%';
```

### Đáp án chuẩn (Ground Truth Answer)
Phân tích hộ bà Mai Thị M (Phường Nghĩa Tân, TP Gia Nghĩa):
- Tổng số chỉ số thiếu hụt: **4** chỉ số (bao gồm: nước sinh hoạt, nhà tiêu, bảo hiểm y tế, và việc làm).

---

## 76. [So Sánh Thiếu Hụt Nước/Vệ Sinh] So sanh tinh trang thieu nuoc sinh hoat va nha tieu giua ho ong Dinh Van N va ho ba Luc Thi O o xa Truc Son

- **Ý định gốc (Base Intent):** *So sánh tình trạng thiếu nước sinh hoạt và nhà tiêu hợp vệ sinh giữa hộ ông Đinh Văn N và hộ bà Lục Thị O ở xã Trúc Sơn*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_chu_ho, thieu_nuoc_sinh_hoat, thieu_nha_tieu FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_xa_phuong LIKE '%Trúc Sơn%' AND (ten_chu_ho LIKE '%Đinh Văn N%' OR ten_chu_ho LIKE '%Lục Thị O%');
```

### Đáp án chuẩn (Ground Truth Answer)
So sánh thiếu hụt nước và vệ sinh tại xã Trúc Sơn:
- Hộ ông Đinh Văn N: Thiếu nước = **CÓ**, Thiếu nhà tiêu = **KHÔNG**
- Hộ bà Lục Thị O: Thiếu nước = **CÓ**, Thiếu nhà tiêu = **CÓ**
=> Hộ bà Lục Thị O khó khăn hơn về vệ sinh.

---

## 77. [Chủ Hộ + Điểm B2 + Neo Đơn] Ho ong Cao Van P o xa Quảng Hòa có điểm B2 bằng bao nhiêu và có thuộc diện hộ nghèo neo đơn không

- **Ý định gốc (Base Intent):** *Hộ ông Cao Văn P ở xã Quảng Hòa có điểm B2 bằng bao nhiêu và có thuộc diện hộ nghèo neo đơn không?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_chu_ho, b2 as diem_b2, nguyen_nhan_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_xa_phuong LIKE '%Quảng Hòa%' AND ten_chu_ho LIKE '%Cao Văn P%';
```

### Đáp án chuẩn (Ground Truth Answer)
Thông tin hộ ông Cao Văn P (Xã Quảng Hòa):
- Điểm thiếu hụt B2: **45** điểm
- Diện neo đơn: **ĐÚNG** (nguyen_nhan_ngheo = 'Già cả, neo đơn').

---

## 78. [Thành Viên + Dân Tộc + Việc Làm] Ho ba La Thi Q o xa Đắk Đrô huyện Krông Nô có bao nhiêu thành viên là người dân tộc Kinh và có thiếu việc làm không

- **Ý định gốc (Base Intent):** *Hộ bà La Thị Q ở xã Đắk Đrô huyện Krông Nô có bao nhiêu thành viên, có phải người Kinh không và có bị thiếu việc làm không?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_chu_ho, so_thanh_vien, is_kinh, thieu_viec_lam FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Krông Nô%' AND ten_xa_phuong LIKE '%Đắk Đrô%' AND ten_chu_ho LIKE '%La Thị Q%';
```

### Đáp án chuẩn (Ground Truth Answer)
Thông tin hộ bà La Thị Q (Xã Đắk Đrô, Krông Nô):
- Số thành viên: **5** người
- Dân tộc Kinh: **ĐÚNG** (is_kinh = 1)
- Thiếu việc làm: **CÓ** (thieu_viec_lam = 1).

---

## 79. [So Sánh 3 Chỉ Số Chủ Hộ] So sanh diem B1, diem B2 va so thanh vien giua ho ong Y Ngong va ho ong Y Thom o xa Đắk Plao

- **Ý định gốc (Base Intent):** *So sánh điểm B1, điểm B2 và số thành viên giữa hộ ông Y Ngong và hộ ông Y Thom ở xã Đắk Plao*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_chu_ho, b1 as diem_b1, b2 as diem_b2, so_thanh_vien FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_xa_phuong LIKE '%Đắk Plao%' AND (ten_chu_ho LIKE '%Y Ngong%' OR ten_chu_ho LIKE '%Y Thom%');
```

### Đáp án chuẩn (Ground Truth Answer)
So sánh 3 chỉ số tại xã Đắk Plao:
- Hộ ông Y Ngong: Điểm B1 = **10**, Điểm B2 = **35**, Số thành viên = **5**
- Hộ ông Y Thom: Điểm B1 = **15**, Điểm B2 = **40**, Số thành viên = **7**.

---

## 80. [Chủ Hộ + Báo Cáo Đa Chiều Tổng Thể] Ho ong Tạ Văn R ở xã Nâm N'Đir huyện Krông Nô có tổng điểm thiếu hụt đa chiều là bao nhiêu và thiếu những dịch vụ nào

- **Ý định gốc (Base Intent):** *Hộ ông Tạ Văn R ở xã Nâm N'Đir huyện Krông Nô có tổng điểm thiếu hụt đa chiều là bao nhiêu và bị thiếu hụt những dịch vụ xã hội cơ bản nào?*
- **Phân loại Thử thách:** `{q_type}`

### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_chu_ho, b2 as diem_thieu_hut, thieu_nuoc_sinh_hoat, thieu_nha_tieu, thieu_bhyte, thieu_gd_nguoi_lon, thieu_gd_tre_em, thieu_chat_luong_nha, thieu_dien_tich_nha, thieu_dv_vien_thong, thieu_pt_tiep_can_tt, thieu_viec_lam, thieu_dinh_duong FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Krông Nô%' AND ten_xa_phuong LIKE '%Nâm N''Đir%' AND ten_chu_ho LIKE '%Tạ Văn R%';
```

### Đáp án chuẩn (Ground Truth Answer)
Báo cáo tổng thể hộ ông Tạ Văn R (Xã Nâm N'Đir, Krông Nô):
- Tổng điểm thiếu hụt B2: **55** điểm
- Danh sách dịch vụ bị thiếu hụt: **Nước sinh hoạt, Nhà tiêu hợp vệ sinh, Bảo hiểm y tế, Chất lượng nhà ở, và Dinh dưỡng**.

---
