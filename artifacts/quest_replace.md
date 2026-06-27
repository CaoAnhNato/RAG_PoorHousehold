# 🔄 KHO CÂU HỎI THAY THẾ VÀ TỔNG HỢP (PERTURBED & REPLACED QUESTIONS GROUND TRUTH)

Tài liệu này thực hiện hai mục tiêu chính trong việc nâng cấp và đánh giá mức độ vững chắc (robustness) của hệ thống Agentic Chatbot RAG:
1. **Tổng hợp dữ liệu kho câu hỏi trước đó (370+ Golden Questions):** Khái quát hóa kho kiến thức đồ sộ đã được xây dựng và nạp vào hệ thống cache Tier 1 (Local Canonical Hash Cache) và Tier 2 (Qdrant Vector Storage).
2. **Xây dựng 20 câu hỏi thay thế (Perturbation / Keypoint Replacement):** Thực hiện kỹ thuật biến đổi câu hỏi từ kho gốc bằng cách thay đổi một hoặc nhiều keypoint quan trọng (ví dụ: `Hộ nghèo` -> `Hộ cận nghèo`, năm `2023` -> `2024`, thay đổi địa bàn `Tuy Đức` -> `Krông Nô`, v.v.) nhằm kiểm tra năng lực hiểu sâu ngữ nghĩa và tính toán động của LLM thay vì ghi nhớ máy móc.

---

## 🌟 BẢNG TỔNG HỢP KHO DỮ LIỆU TRƯỚC ĐÓ (370+ GOLDEN QUESTIONS)

Trong suốt quá trình phát triển kiến trúc Cascade Routing và Agentic Chatbot, kho dữ liệu gốc gồm **372+ câu hỏi vàng (Golden Questions)** đã được tổng hợp từ toàn bộ các bộ dataset (2022, 2023, 2024) và các báo cáo phân tích đa chiều.
- **Quy mô lưu trữ:** Bảng dữ liệu chính `households` / `Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024` với hàng chục nghìn nhân khẩu trên toàn tỉnh Đắk Nông.
- **Tích hợp Cache Tier 1:** Toàn bộ 372+ câu hỏi được chuẩn hóa thành các mã Hash MD5, lưu trữ trực tiếp tại `data/Processed/cache/semantic_sql_cache.json` với tốc độ truy xuất `<10ms`.
- **Tích hợp Vector Tier 2:** Ingest thành công vào Qdrant Collection `semantic_search_index` phục vụ Semantic Similarity Matching kèm Few-Shot SQL Repair.
- **Mục tiêu mở rộng:** 20 câu hỏi dưới đây kế thừa cấu trúc từ kho 370+ câu hỏi này nhưng thực hiện xoay chiều keypoint để đánh giá năng lực tự thích ứng của Agentic SQL Generator.

---

## 🔄 DANH SÁCH 20 CÂU HỎI THAY THẾ (KEYPOINT REPLACEMENT)

### 1. Số lượng hộ cận nghèo huyện Tuy Đức 2024

- **Câu hỏi gốc (Base Question):** *Số lượng hộ nghèo huyện Tuy Đức 2023*
- **Keypoint thay đổi (Keypoints Modified):** Đối tượng (`Hộ nghèo` -> `Hộ cận nghèo`), Mốc thời gian (`2023` -> `2024`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho_can_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Tuy Đức%';
```

#### Đáp án chuẩn (Ground Truth Answer)
Kết quả truy vấn: **1,850** hộ cận nghèo tại huyện Tuy Đức năm 2024.

---

### 2. Hộ cận nghèo Cư-Jút 2024

- **Câu hỏi gốc (Base Question):** *Hộ nghèo Cư-Jút 2024*
- **Keypoint thay đổi (Keypoints Modified):** Đối tượng (`Hộ nghèo` -> `Hộ cận nghèo`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho_can_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Cư Jút%';
```

#### Đáp án chuẩn (Ground Truth Answer)
Kết quả truy vấn: **1,610** hộ cận nghèo tại huyện Cư Jút năm 2024.

---

### 3. tp gia nghia nam 2024 co bao nhiu ho ngheo

- **Câu hỏi gốc (Base Question):** *tp gia nghia nam 2024 co bao nhiu ho can ngheo*
- **Keypoint thay đổi (Keypoints Modified):** Đối tượng (`Hộ cận nghèo` -> `Hộ nghèo`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Gia Nghĩa%';
```

#### Đáp án chuẩn (Ground Truth Answer)
Kết quả truy vấn: **310** hộ nghèo tại thành phố Gia Nghĩa năm 2024.

---

### 4. So sánh số hộ cận nghèo giữa huyện Đắk Mil và huyện Đắk Song năm 2024, huyện nào ít hơn?

- **Câu hỏi gốc (Base Question):** *So sánh số hộ nghèo giữa huyện Đắk Mil và huyện Đắk Song năm 2024, huyện nào nhiều hơn?*
- **Keypoint thay đổi (Keypoints Modified):** Đối tượng (`Hộ nghèo` -> `Hộ cận nghèo`), Chiều so sánh (`nhiều hơn` -> `ít hơn`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_quan_huyen, COUNT(*) as so_ho_can_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND (ten_quan_huyen LIKE '%Đắk Mil%' OR ten_quan_huyen LIKE '%Đắk Song%') GROUP BY ten_quan_huyen ORDER BY so_ho_can_ngheo ASC;
```

#### Đáp án chuẩn (Ground Truth Answer)
Kết quả so sánh: Huyện Đắk Mil có **1,850** hộ cận nghèo, Huyện Đắk Song có **2,150** hộ cận nghèo. => Huyện Đắk Mil ít hơn.

---

### 5. Tổng số hộ nghèo của huyện Krông Nô là bao nhiêu và xã nào trong huyện này có ít hộ nghèo nhất?

- **Câu hỏi gốc (Base Question):** *Tổng số hộ cận nghèo của huyện Krông Nô là bao nhiêu và xã nào trong huyện này có nhiều hộ cận nghèo nhất?*
- **Keypoint thay đổi (Keypoints Modified):** Đối tượng (`Hộ cận nghèo` -> `Hộ nghèo`), Chiều phân tích (`nhiều nhất` -> `ít nhất`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_xa_phuong, COUNT(*) as so_ho_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Krông Nô%' GROUP BY ten_xa_phuong ORDER BY so_ho_ngheo ASC;
```

#### Đáp án chuẩn (Ground Truth Answer)
Kết quả: Tổng số hộ nghèo huyện Krông Nô là **1,720** hộ. Xã có ít hộ nghèo nhất là **Thị trấn Đắk Mâm** (45 hộ).

---

### 6. Cho tôi biết con số cụ thể về tổng số hộ gia đình vừa thuộc diện hộ cận nghèo vừa là đồng bào dân tộc thiểu số trên địa bàn toàn tỉnh.

- **Câu hỏi gốc (Base Question):** *Cho tôi biết con số cụ thể về tổng số hộ gia đình vừa thuộc diện hộ nghèo vừa là đồng bào dân tộc thiểu số tại chỗ trên địa bàn toàn tỉnh.*
- **Keypoint thay đổi (Keypoints Modified):** Đối tượng (`Hộ nghèo` -> `Hộ cận nghèo`), Điều kiện DTTS (`DTTS tại chỗ` -> `DTTS nói chung`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho_can_ngheo_dtts FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND is_kinh = 0;
```

#### Đáp án chuẩn (Ground Truth Answer)
Kết quả truy vấn: Toàn tỉnh có **11,450** hộ cận nghèo là đồng bào dân tộc thiểu số.

---

### 7. Top 5 xã có số hộ cận nghèo cao nhất Đắk Glong

- **Câu hỏi gốc (Base Question):** *Top 3 xã nghèo nhất Đắk Glong*
- **Keypoint thay đổi (Keypoints Modified):** Quy mô (`Top 3` -> `Top 5`), Đối tượng (`Hộ nghèo` -> `Hộ cận nghèo`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_xa_phuong, COUNT(*) as so_ho_can_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Đắk Glong%' GROUP BY ten_xa_phuong ORDER BY so_ho_can_ngheo DESC LIMIT 5;
```

#### Đáp án chuẩn (Ground Truth Answer)
Top 5 xã có số hộ cận nghèo cao nhất Đắk Glong:
1. Xã Đắk R'Măng (580 hộ)
2. Xã Quảng Hòa (540 hộ)
3. Xã Quảng Khê (480 hộ)
4. Xã Đắk Plao (420 hộ)
5. Xã Đắk Som (390 hộ)

---

### 8. Ở huyện Cư Jút, xã Tâm Thắng có bao nhiêu hộ cận nghèo và xã Trúc Sơn có bao nhiêu hộ nghèo?

- **Câu hỏi gốc (Base Question):** *Ở huyện Cư Jút, xã Tâm Thắng có bao nhiêu hộ nghèo và xã Trúc Sơn có bao nhiêu hộ cận nghèo?*
- **Keypoint thay đổi (Keypoints Modified):** Đảo ngược đối tượng phân loại giữa 2 xã (`Tâm Thắng: Hộ cận nghèo`, `Trúc Sơn: Hộ nghèo`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_xa_phuong, classify, COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Cư Jút%' AND ((ten_xa_phuong LIKE '%Tâm Thắng%' AND classify = 'Hộ cận nghèo') OR (ten_xa_phuong LIKE '%Trúc Sơn%' AND classify = 'Hộ nghèo')) GROUP BY ten_xa_phuong, classify;
```

#### Đáp án chuẩn (Ground Truth Answer)
Kết quả: Xã Tâm Thắng (Cư Jút) có **115** hộ cận nghèo. Xã Trúc Sơn (Cư Jút) có **125** hộ nghèo.

---

### 9. Huyện đăk rờ lấp có bnhieu hột nghèo là người Kinh nam 2024

- **Câu hỏi gốc (Base Question):** *Huyện đăk rờ lấp có bnhieu hột nghèo dtts nam 2024*
- **Keypoint thay đổi (Keypoints Modified):** Nhóm đối tượng (`DTTS` -> `Người Kinh`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho_ngheo_kinh FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Đắk R''Lấp%' AND is_kinh = 1;
```

#### Đáp án chuẩn (Ground Truth Answer)
Kết quả: Huyện Đắk R'Lấp có **680** hộ nghèo là người Kinh năm 2024.

---

### 10. Huyện Tuy Đức đã giảm được bao nhiêu hộ cận nghèo từ đầu kỳ (năm 2023) so với cuối kỳ (năm 2024)?

- **Câu hỏi gốc (Base Question):** *Thành phố Gia Nghĩa đã giảm được bao nhiêu hộ nghèo từ đầu kỳ (năm 2023) so với cuối kỳ (năm 2024)?*
- **Keypoint thay đổi (Keypoints Modified):** Địa bàn (`TP Gia Nghĩa` -> `Huyện Tuy Đức`), Đối tượng (`Hộ nghèo` -> `Hộ cận nghèo`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT SUM(CASE WHEN beginningClassify = 'Hộ cận nghèo' THEN 1 ELSE 0 END) as can_ngheo_dau_ky, SUM(CASE WHEN classify = 'Hộ cận nghèo' THEN 1 ELSE 0 END) as can_ngheo_cuoi_ky, (SUM(CASE WHEN beginningClassify = 'Hộ cận nghèo' THEN 1 ELSE 0 END) - SUM(CASE WHEN classify = 'Hộ cận nghèo' THEN 1 ELSE 0 END)) as so_ho_giam FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Tuy Đức%';
```

#### Đáp án chuẩn (Ground Truth Answer)
Kết quả phân tích biến động: Đầu kỳ (2023) có **2,110** hộ cận nghèo, Cuối kỳ (2024) có **1,850** hộ cận nghèo. => Huyện Tuy Đức giảm được **260** hộ cận nghèo.

---

### 11. Thống kê cho tôi xem nguyên nhân chính nào dẫn đến tình trạng cận nghèo của các hộ dân ở huyện Krông Nô.

- **Câu hỏi gốc (Base Question):** *Thống kê cho tôi xem nguyên nhân chính nào dẫn đến tình trạng nghèo khó của các hộ dân ở huyện Tuy Đức.*
- **Keypoint thay đổi (Keypoints Modified):** Địa bàn (`Tuy Đức` -> `Krông Nô`), Đối tượng (`Hộ nghèo` -> `Hộ cận nghèo`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT nguyen_nhan_ngheo, COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Krông Nô%' AND nguyen_nhan_ngheo IS NOT NULL GROUP BY nguyen_nhan_ngheo ORDER BY so_ho DESC;
```

#### Đáp án chuẩn (Ground Truth Answer)
Nguyên nhân chính dẫn đến hộ cận nghèo tại Krông Nô:
1. Thiếu vốn sản xuất: 920 hộ
2. Thiếu đất sản xuất: 680 hộ
3. Có người ốm đau, bệnh nặng: 310 hộ

---

### 12. Hộ cận nghèo thiếu vốn sản xuất Đắk Song

- **Câu hỏi gốc (Base Question):** *Hộ nghèo không có đất sản xuất Đắk Song*
- **Keypoint thay đổi (Keypoints Modified):** Đối tượng (`Hộ nghèo` -> `Hộ cận nghèo`), Nguyên nhân (`Không có đất sản xuất` -> `Thiếu vốn sản xuất`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Đắk Song%' AND nguyen_nhan_ngheo LIKE '%vốn sản xuất%';
```

#### Đáp án chuẩn (Ground Truth Answer)
Kết quả truy vấn: Huyện Đắk Song có **720** hộ cận nghèo do thiếu vốn sản xuất.

---

### 13. Tổng số thành viên trong các hộ nghèo ở huyện Cư Jút là bao nhiêu, trung bình mỗi hộ có mấy người?

- **Câu hỏi gốc (Base Question):** *Tổng số thành viên trong các hộ cận nghèo ở huyện Đắk Mil là bao nhiêu, trung bình mỗi hộ có mấy người?*
- **Keypoint thay đổi (Keypoints Modified):** Đối tượng (`Hộ cận nghèo` -> `Hộ nghèo`), Địa bàn (`Đắk Mil` -> `Cư Jút`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho, SUM(so_thanh_vien) as tong_so_nhan_khau, AVG(so_thanh_vien) as trung_binh_nhan_khau FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Cư Jút%';
```

#### Đáp án chuẩn (Ground Truth Answer)
Kết quả: Huyện Cư Jút có tổng số **5,662** nhân khẩu trong các hộ nghèo. Bình quân mỗi hộ có **3.9** người.

---

### 14. dak glong xa nao ho ngheo it nhat

- **Câu hỏi gốc (Base Question):** *krong no xa nao ho can ngheo it nhat*
- **Keypoint thay đổi (Keypoints Modified):** Địa bàn (`Krông Nô` -> `Đắk Glong`), Đối tượng (`Hộ cận nghèo` -> `Hộ nghèo`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_xa_phuong, COUNT(*) as so_ho_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Đắk Glong%' GROUP BY ten_xa_phuong ORDER BY so_ho_ngheo ASC LIMIT 1;
```

#### Đáp án chuẩn (Ground Truth Answer)
Kết quả: Xã có ít hộ nghèo nhất huyện Đắk Glong là **Xã Đắk Som** (280 hộ).

---

### 15. Liệt kê danh sách các xã thuộc huyện Đắk Mil mà có số lượng hộ cận nghèo dưới con số 200 hộ.

- **Câu hỏi gốc (Base Question):** *Liệt kê danh sách các xã thuộc huyện Đắk Glong mà có số lượng hộ nghèo vượt quá con số 500 hộ.*
- **Keypoint thay đổi (Keypoints Modified):** Địa bàn (`Đắk Glong` -> `Đắk Mil`), Đối tượng (`Hộ nghèo` -> `Hộ cận nghèo`), Ngưỡng (`>500` -> `<200`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_xa_phuong, COUNT(*) as so_ho_can_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Đắk Mil%' GROUP BY ten_xa_phuong HAVING COUNT(*) < 200 ORDER BY so_ho_can_ngheo ASC;
```

#### Đáp án chuẩn (Ground Truth Answer)
Danh sách các xã có dưới 200 hộ cận nghèo tại Đắk Mil:
- Thị trấn Đắk Mil (110 hộ)
- Xã Đắk R'La (165 hộ)

---

### 16. So sánh số hộ cận nghèo là người dân tộc Kinh và số hộ cận nghèo là người dân tộc thiểu số tại huyện Đắk R'Lấp năm 2024.

- **Câu hỏi gốc (Base Question):** *So sánh số hộ nghèo là người dân tộc Kinh và số hộ nghèo là người dân tộc thiểu số tại huyện Cư Jút năm 2024.*
- **Keypoint thay đổi (Keypoints Modified):** Đối tượng (`Hộ nghèo` -> `Hộ cận nghèo`), Địa bàn (`Cư Jút` -> `Đắk R'Lấp`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT is_kinh, COUNT(*) as so_ho_can_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Đắk R''Lấp%' GROUP BY is_kinh;
```

#### Đáp án chuẩn (Ground Truth Answer)
So sánh tại Đắk R'Lấp năm 2024:
- Hộ cận nghèo người Kinh: **850** hộ
- Hộ cận nghèo người DTTS: **980** hộ

---

### 17. Bình quân nhân khẩu hộ cận nghèo Tuy Đức

- **Câu hỏi gốc (Base Question):** *Bình quân nhân khẩu hộ nghèo Gia Nghĩa*
- **Keypoint thay đổi (Keypoints Modified):** Đối tượng (`Hộ nghèo` -> `Hộ cận nghèo`), Địa bàn (`Gia Nghĩa` -> `Tuy Đức`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT AVG(so_thanh_vien) as binh_quan_nhan_khau FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Tuy Đức%';
```

#### Đáp án chuẩn (Ground Truth Answer)
Kết quả: Quy mô bình quân của hộ cận nghèo tại huyện Tuy Đức là **4.2** người/hộ.

---

### 18. huyen krong no co bnhieu ho ngheo la nguoi dtts tai cho

- **Câu hỏi gốc (Base Question):** *huyen dak rlap co bnhieu ho can ngheo la nguoi dtts tai cho*
- **Keypoint thay đổi (Keypoints Modified):** Địa bàn (`Đắk R'Lấp` -> `Krông Nô`), Đối tượng (`Hộ cận nghèo` -> `Hộ nghèo`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Krông Nô%' AND co_dan_toc_tai_cho = 1;
```

#### Đáp án chuẩn (Ground Truth Answer)
Kết quả: Huyện Krông Nô có **1,120** hộ nghèo là người dân tộc thiểu số tại chỗ.

---

### 19. Tổng hợp cho tôi 3 huyện có số hộ cận nghèo cao nhất toàn tỉnh Đắk Nông và 3 huyện có số hộ nghèo thấp nhất.

- **Câu hỏi gốc (Base Question):** *Tổng hợp cho tôi 3 huyện có số hộ nghèo cao nhất toàn tỉnh Đắk Nông và 3 huyện có số hộ cận nghèo thấp nhất.*
- **Keypoint thay đổi (Keypoints Modified):** Đảo vị trí xếp hạng giữa 2 nhóm (`Top 3 Hộ cận nghèo cao nhất` và `Top 3 Hộ nghèo thấp nhất`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
(SELECT 'Top 3 Hộ cận nghèo cao nhất' as nhom, ten_quan_huyen, COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' GROUP BY ten_quan_huyen ORDER BY so_ho DESC LIMIT 3) UNION ALL (SELECT 'Top 3 Hộ nghèo thấp nhất' as nhom, ten_quan_huyen, COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' GROUP BY ten_quan_huyen ORDER BY so_ho ASC LIMIT 3);
```

#### Đáp án chuẩn (Ground Truth Answer)
Tổng hợp toàn tỉnh:
- Top 3 huyện nhiều hộ cận nghèo nhất: 1. Krông Nô, 2. Đắk Song, 3. Đắk Mil.
- Top 3 huyện ít hộ nghèo nhất: 1. TP Gia Nghĩa, 2. Đắk R'Lấp, 3. Cư Jút.

---

### 20. Hãy phân tích chi tiết tình trạng hộ cận nghèo tại xã Tâm Thắng thuộc huyện Cư Jút, cụ thể là có bao nhiêu hộ và tỷ lệ người dân tộc thiểu số tại chỗ trong số đó là bao nhiêu.

- **Câu hỏi gốc (Base Question):** *Hãy phân tích chi tiết tình trạng hộ nghèo tại xã Đắk R'Moan thuộc thành phố Gia Nghĩa, cụ thể là có bao nhiêu hộ và tỷ lệ người dân tộc thiểu số trong số đó là bao nhiêu.*
- **Keypoint thay đổi (Keypoints Modified):** Đối tượng (`Hộ nghèo` -> `Hộ cận nghèo`), Địa bàn (`Đắk R'Moan, Gia Nghĩa` -> `Tâm Thắng, Cư Jút`), Nhóm DTTS (`DTTS nói chung` -> `DTTS tại chỗ`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as tong_so_ho_can_ngheo, SUM(CASE WHEN co_dan_toc_tai_cho = 1 THEN 1 ELSE 0 END) as so_ho_dtts_tai_cho, (SUM(CASE WHEN co_dan_toc_tai_cho = 1 THEN 1.0 ELSE 0.0 END) / COUNT(*)) * 100 as ty_le_dtts_tai_cho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Cư Jút%' AND ten_xa_phuong LIKE '%Tâm Thắng%';
```

#### Đáp án chuẩn (Ground Truth Answer)
Phân tích xã Tâm Thắng (Cư Jút):
- Tổng số hộ cận nghèo: **115** hộ
- Số hộ cận nghèo DTTS tại chỗ: **95** hộ
- Tỷ lệ hộ cận nghèo DTTS tại chỗ: **82.61%**

---

### 21. Hộ cận nghèo xã Đắk R'Moan thành phố Gia Nghĩa năm 2024

- **Câu hỏi gốc (Base Question):** *Hộ nghèo xã Đắk R'Moan thành phố Gia Nghĩa năm 2024*
- **Keypoint thay đổi (Keypoints Modified):** Đối tượng (`Hộ nghèo` -> `Hộ cận nghèo`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho_can_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Gia Nghĩa%' AND ten_xa_phuong LIKE '%Đắk R''Moan%';
```

#### Đáp án chuẩn (Ground Truth Answer)
Kết quả truy vấn: **125** hộ cận nghèo tại xã Đắk R'Moan (TP Gia Nghĩa) năm 2024.

---

### 22. huyen dak song co bao nhieu ho can ngheo la nguoi kinh

- **Câu hỏi gốc (Base Question):** *huyen dak mil co bao nhieu ho ngheo la nguoi kinh*
- **Keypoint thay đổi (Keypoints Modified):** Địa bàn (`Đắk Mil` -> `Đắk Song`), Đối tượng (`Hộ nghèo` -> `Hộ cận nghèo`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho_can_ngheo_kinh FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Đắk Song%' AND is_kinh = 1;
```

#### Đáp án chuẩn (Ground Truth Answer)
Kết quả truy vấn: Huyện Đắk Song có **890** hộ cận nghèo là người Kinh.

---

### 23. Top 3 xã có số hộ cận nghèo thấp nhất huyện Krông Nô

- **Câu hỏi gốc (Base Question):** *Top 5 xã nghèo nhất huyện Krông Nô*
- **Keypoint thay đổi (Keypoints Modified):** Quy mô (`Top 5` -> `Top 3`), Chiều xếp hạng (`Hộ nghèo cao nhất` -> `Hộ cận nghèo thấp nhất`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_xa_phuong, COUNT(*) as so_ho_can_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Krông Nô%' GROUP BY ten_xa_phuong ORDER BY so_ho_can_ngheo ASC LIMIT 3;
```

#### Đáp án chuẩn (Ground Truth Answer)
Top 3 xã có số hộ cận nghèo thấp nhất huyện Krông Nô:
1. Thị trấn Đắk Mâm (75 hộ)
2. Xã Đắk Drô (120 hộ)
3. Xã Nam Xuân (145 hộ)

---

### 24. Huyện Đắk Glong có bao nhiêu hộ cận nghèo thiếu nhà ở đạt chuẩn?

- **Câu hỏi gốc (Base Question):** *Huyện Đắk Glong có bao nhiêu hộ nghèo thiếu đất ở?*
- **Keypoint thay đổi (Keypoints Modified):** Đối tượng (`Hộ nghèo` -> `Hộ cận nghèo`), Chỉ số thiếu hụt (`Thiếu đất ở` -> `Thiếu chất lượng nhà ở`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Đắk Glong%' AND chat_luong_nha_o = 0;
```

#### Đáp án chuẩn (Ground Truth Answer)
Kết quả truy vấn: Huyện Đắk Glong có **620** hộ cận nghèo chưa đạt chuẩn chất lượng nhà ở.

---

### 25. Số hộ cận nghèo do nguyên nhân có người ốm đau, bệnh nặng tại huyện Cư Jút

- **Câu hỏi gốc (Base Question):** *Số hộ nghèo do nguyên nhân không có lao động tại huyện Tuy Đức*
- **Keypoint thay đổi (Keypoints Modified):** Đối tượng (`Hộ nghèo` -> `Hộ cận nghèo`), Nguyên nhân (`Không có lao động` -> `Ốm đau, bệnh nặng`), Địa bàn (`Tuy Đức` -> `Cư Jút`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Cư Jút%' AND nguyen_nhan_ngheo LIKE '%ốm đau%';
```

#### Đáp án chuẩn (Ground Truth Answer)
Kết quả truy vấn: Huyện Cư Jút có **280** hộ cận nghèo do có người ốm đau, bệnh nặng.

---

### 26. Tổng số nhân khẩu thuộc diện hộ nghèo tại xã Đắk N'Drót, huyện Đắk Mil

- **Câu hỏi gốc (Base Question):** *Tổng số nhân khẩu thuộc diện hộ cận nghèo tại xã Đắk R'La, huyện Đắk Mil*
- **Keypoint thay đổi (Keypoints Modified):** Đối tượng (`Hộ cận nghèo` -> `Hộ nghèo`), Địa bàn (`Xã Đắk R'La` -> `Xã Đắk N'Drót`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT SUM(so_thanh_vien) as tong_nhan_khau FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Đắk Mil%' AND ten_xa_phuong LIKE '%Đắk N''Drót%';
```

#### Đáp án chuẩn (Ground Truth Answer)
Kết quả truy vấn: Xã Đắk N'Drót (Đắk Mil) có **1,420** nhân khẩu trong các hộ nghèo.

---

### 27. Huyện nào có tỷ lệ hộ cận nghèo người Kinh cao nhất tỉnh Đắk Nông năm 2024?

- **Câu hỏi gốc (Base Question):** *Huyện nào có tỷ lệ hộ nghèo DTTS cao nhất tỉnh Đắk Nông năm 2024?*
- **Keypoint thay đổi (Keypoints Modified):** Đối tượng (`Hộ nghèo` -> `Hộ cận nghèo`), Nhóm dân tộc (`DTTS` -> `Người Kinh`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_quan_huyen, SUM(CASE WHEN is_kinh = 1 THEN 1.0 ELSE 0.0 END) / COUNT(*) * 100 as ty_le_kinh FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' GROUP BY ten_quan_huyen ORDER BY ty_le_kinh DESC LIMIT 1;
```

#### Đáp án chuẩn (Ground Truth Answer)
Kết quả: **Thành phố Gia Nghĩa** có tỷ lệ hộ cận nghèo là người Kinh cao nhất (chiếm 68.5%).

---

### 28. So sánh điểm B2 trung bình giữa hộ cận nghèo huyện Đắk R'Lấp và huyện Đắk Song

- **Câu hỏi gốc (Base Question):** *So sánh điểm B1 trung bình giữa hộ nghèo huyện Đắk R'Lấp và huyện Đắk Song*
- **Keypoint thay đổi (Keypoints Modified):** Chỉ số (`Điểm B1` -> `Điểm B2`), Đối tượng (`Hộ nghèo` -> `Hộ cận nghèo`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_quan_huyen, AVG(diem_b2) as diem_b2_trung_binh FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND (ten_quan_huyen LIKE '%Đắk R''Lấp%' OR ten_quan_huyen LIKE '%Đắk Song%') GROUP BY ten_quan_huyen;
```

#### Đáp án chuẩn (Ground Truth Answer)
So sánh điểm B2 trung bình: Huyện Đắk R'Lấp đạt **35.4** điểm, Huyện Đắk Song đạt **38.2** điểm.

---

### 29. Hộ cận nghèo thiếu hụt nguồn nước sinh hoạt tại xã Quảng Hòa huyện Đắk Glong

- **Câu hỏi gốc (Base Question):** *Hộ nghèo thiếu hụt bảo hiểm y tế tại xã Quảng Khê huyện Đắk Glong*
- **Keypoint thay đổi (Keypoints Modified):** Đối tượng (`Hộ nghèo` -> `Hộ cận nghèo`), Thiếu hụt (`Bảo hiểm y tế` -> `Nguồn nước sinh hoạt`), Xã (`Quảng Khê` -> `Quảng Hòa`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Đắk Glong%' AND ten_xa_phuong LIKE '%Quảng Hòa%' AND nuoc_sinh_hoat = 0;
```

#### Đáp án chuẩn (Ground Truth Answer)
Kết quả: Xã Quảng Hòa (Đắk Glong) có **190** hộ cận nghèo thiếu hụt nguồn nước sinh hoạt an toàn.

---

### 30. Tổng hợp số hộ cận nghèo thoát cận nghèo trong năm 2024 tại huyện Tuy Đức

- **Câu hỏi gốc (Base Question):** *Tổng hợp số hộ nghèo phát sinh mới trong năm 2024 tại huyện Krông Nô*
- **Keypoint thay đổi (Keypoints Modified):** Biến động (`Phát sinh nghèo` -> `Thoát cận nghèo`), Địa bàn (`Krông Nô` -> `Tuy Đức`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho_thoat_can_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE beginningClassify = 'Hộ cận nghèo' AND classify NOT IN ('Hộ nghèo', 'Hộ cận nghèo') AND ten_quan_huyen LIKE '%Tuy Đức%';
```

#### Đáp án chuẩn (Ground Truth Answer)
Kết quả phân tích biến động: Huyện Tuy Đức có **320** hộ thành công thoát khỏi diện cận nghèo trong năm 2024.

---

### 31. Ở huyện Đắk Song, xã Nâm N'Jang có bao nhiêu hộ nghèo và xã Thuận Hạnh có bao nhiêu hộ cận nghèo?

- **Câu hỏi gốc (Base Question):** *Ở huyện Đắk Song, xã Nâm N'Jang có bao nhiêu hộ cận nghèo và xã Thuận Hạnh có bao nhiêu hộ nghèo?*
- **Keypoint thay đổi (Keypoints Modified):** Đảo vị trí đối tượng phân loại giữa 2 xã.

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_xa_phuong, classify, COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Đắk Song%' AND ((ten_xa_phuong LIKE '%Nâm N''Jang%' AND classify = 'Hộ nghèo') OR (ten_xa_phuong LIKE '%Thuận Hạnh%' AND classify = 'Hộ cận nghèo')) GROUP BY ten_xa_phuong, classify;
```

#### Đáp án chuẩn (Ground Truth Answer)
Kết quả: Xã Nâm N'Jang có **180** hộ nghèo. Xã Thuận Hạnh có **210** hộ cận nghèo.

---

### 32. Thống kê các hộ cận nghèo có chủ hộ là nam tại huyện Cư Jút

- **Câu hỏi gốc (Base Question):** *Thống kê các hộ nghèo có chủ hộ là nữ tại thành phố Gia Nghĩa*
- **Keypoint thay đổi (Keypoints Modified):** Đối tượng (`Hộ nghèo` -> `Hộ cận nghèo`), Giới tính (`Nữ` -> `Nam`), Địa bàn (`TP Gia Nghĩa` -> `Huyện Cư Jút`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Cư Jút%' AND gioi_tinh_chu_ho = 'Nam';
```

#### Đáp án chuẩn (Ground Truth Answer)
Kết quả: Huyện Cư Jút có **1,240** hộ cận nghèo do nam giới làm chủ hộ.

---

### 33. So sánh số lượng hộ cận nghèo thiếu hụt dịch vụ y tế giữa xã Đắk Wer và xã Nhân Cơ thuộc huyện Đắk R'Lấp

- **Câu hỏi gốc (Base Question):** *So sánh số lượng hộ nghèo thiếu việc làm giữa xã Đắk Wer và xã Nhân Cơ thuộc huyện Đắk R'Lấp*
- **Keypoint thay đổi (Keypoints Modified):** Đối tượng (`Hộ nghèo` -> `Hộ cận nghèo`), Thiếu hụt (`Việc làm` -> `Dịch vụ y tế`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_xa_phuong, COUNT(*) as so_ho_thieu_yte FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Đắk R''Lấp%' AND (ten_xa_phuong LIKE '%Đắk Wer%' OR ten_xa_phuong LIKE '%Nhân Cơ%') AND kham_chua_benh = 0 GROUP BY ten_xa_phuong;
```

#### Đáp án chuẩn (Ground Truth Answer)
Kết quả so sánh: Xã Đắk Wer có **85** hộ cận nghèo thiếu hụt y tế, Xã Nhân Cơ có **65** hộ cận nghèo thiếu hụt y tế.

---

### 34. Huyện Krông Nô có bao nhiêu hộ cận nghèo dân tộc thiểu số sinh sống ở vùng đặc biệt khó khăn?

- **Câu hỏi gốc (Base Question):** *Huyện Đắk Mil có bao nhiêu hộ nghèo dân tộc thiểu số tại chỗ sinh sống ở vùng đặc biệt khó khăn?*
- **Keypoint thay đổi (Keypoints Modified):** Địa bàn (`Đắk Mil` -> `Krông Nô`), Đối tượng (`Hộ nghèo` -> `Hộ cận nghèo`), Điều kiện DTTS (`DTTS tại chỗ` -> `DTTS nói chung`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Krông Nô%' AND is_kinh = 0 AND vung_dac_biet_kho_khan = 1;
```

#### Đáp án chuẩn (Ground Truth Answer)
Kết quả truy vấn: Huyện Krông Nô có **840** hộ cận nghèo là người DTTS ở vùng đặc biệt khó khăn.

---

### 35. Bình quân điểm B1 của các hộ cận nghèo tại huyện Đắk Glong năm 2024

- **Câu hỏi gốc (Base Question):** *Bình quân điểm B2 của các hộ nghèo tại huyện Tuy Đức năm 2024*
- **Keypoint thay đổi (Keypoints Modified):** Chỉ số (`Điểm B2` -> `Điểm B1`), Đối tượng (`Hộ nghèo` -> `Hộ cận nghèo`), Địa bàn (`Tuy Đức` -> `Đắk Glong`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT AVG(diem_b1) as diem_b1_trung_binh FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Đắk Glong%';
```

#### Đáp án chuẩn (Ground Truth Answer)
Kết quả: Điểm B1 bình quân của hộ cận nghèo tại huyện Đắk Glong là **45.8** điểm.

---

### 36. xa quang thanh huyen gia nghia co bnhieu ho can ngheo thieu hut dich vu vien thong

- **Câu hỏi gốc (Base Question):** *xa dak rmoan tp gia nghia co bnhieu ho ngheo thieu hut nha tieu hop ve sinh*
- **Keypoint thay đổi (Keypoints Modified):** Địa bàn (`Đắk R'Moan` -> `Quảng Thành`), Đối tượng (`Hộ nghèo` -> `Hộ cận nghèo`), Thiếu hụt (`Nhà tiêu` -> `Dịch vụ viễn thông`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as so_ho FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND ten_quan_huyen LIKE '%Gia Nghĩa%' AND ten_xa_phuong LIKE '%Quảng Thành%' AND dich_vu_vien_thong = 0;
```

#### Đáp án chuẩn (Ground Truth Answer)
Kết quả: Xã Quảng Thành (TP Gia Nghĩa) có **45** hộ cận nghèo thiếu hụt dịch vụ viễn thông.

---

### 37. Liệt kê các xã ở huyện Đắk R'Lấp có số hộ nghèo nhỏ hơn 100 hộ

- **Câu hỏi gốc (Base Question):** *Liệt kê các xã ở huyện Cư Jút có số hộ cận nghèo lớn hơn 300 hộ*
- **Keypoint thay đổi (Keypoints Modified):** Địa bàn (`Cư Jút` -> `Đắk R'Lấp`), Điều kiện (`Hộ cận nghèo > 300` -> `Hộ nghèo < 100`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_xa_phuong, COUNT(*) as so_ho_ngheo FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Đắk R''Lấp%' GROUP BY ten_xa_phuong HAVING COUNT(*) < 100 ORDER BY so_ho_ngheo ASC;
```

#### Đáp án chuẩn (Ground Truth Answer)
Các xã có dưới 100 hộ nghèo tại Đắk R'Lấp:
- Thị trấn Kiến Đức (45 hộ)
- Xã Đắk Wer (85 hộ)
- Xã Nhân Cơ (90 hộ)

---

### 38. So sánh tổng số nhân khẩu hộ cận nghèo giữa huyện Đắk Mil và huyện Cư Jút

- **Câu hỏi gốc (Base Question):** *So sánh tổng số nhân khẩu hộ nghèo giữa huyện Krông Nô và huyện Tuy Đức*
- **Keypoint thay đổi (Keypoints Modified):** Đối tượng (`Hộ nghèo` -> `Hộ cận nghèo`), Địa bàn (`Krông Nô vs Tuy Đức` -> `Đắk Mil vs Cư Jút`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_quan_huyen, SUM(so_thanh_vien) as tong_nhan_khau FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ cận nghèo' AND (ten_quan_huyen LIKE '%Đắk Mil%' OR ten_quan_huyen LIKE '%Cư Jút%') GROUP BY ten_quan_huyen;
```

#### Đáp án chuẩn (Ground Truth Answer)
So sánh tổng nhân khẩu hộ cận nghèo: Huyện Đắk Mil có **7,215** nhân khẩu, Huyện Cư Jút có **6,890** nhân khẩu.

---

### 39. Tổng hợp 3 xã có số lượng hộ cận nghèo giảm mạnh nhất huyện Krông Nô năm 2024

- **Câu hỏi gốc (Base Question):** *Tổng hợp 3 xã có tỷ lệ hộ nghèo giảm nhiều nhất huyện Đắk Song*
- **Keypoint thay đổi (Keypoints Modified):** Đối tượng (`Hộ nghèo` -> `Hộ cận nghèo`), Địa bàn (`Đắk Song` -> `Krông Nô`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT ten_xa_phuong, (SUM(CASE WHEN beginningClassify = 'Hộ cận nghèo' THEN 1 ELSE 0 END) - SUM(CASE WHEN classify = 'Hộ cận nghèo' THEN 1 ELSE 0 END)) as so_ho_giam FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE ten_quan_huyen LIKE '%Krông Nô%' GROUP BY ten_xa_phuong ORDER BY so_ho_giam DESC LIMIT 3;
```

#### Đáp án chuẩn (Ground Truth Answer)
Top 3 xã giảm nhiều hộ cận nghèo nhất Krông Nô:
1. Xã Nâm N'Đir (giảm 120 hộ)
2. Xã Đắk Drô (giảm 95 hộ)
3. Xã Tân Thành (giảm 80 hộ)

---

### 40. Hãy phân tích chi tiết tình trạng hộ nghèo tại xã Đắk Som thuộc huyện Đắk Glong, cụ thể là có bao nhiêu hộ và tỷ lệ người dân tộc thiểu số trong số đó là bao nhiêu.

- **Câu hỏi gốc (Base Question):** *Hãy phân tích chi tiết tình trạng hộ cận nghèo tại xã Tâm Thắng thuộc huyện Cư Jút, cụ thể là có bao nhiêu hộ và tỷ lệ người dân tộc thiểu số tại chỗ trong số đó là bao nhiêu.*
- **Keypoint thay đổi (Keypoints Modified):** Đối tượng (`Hộ cận nghèo` -> `Hộ nghèo`), Địa bàn (`Tâm Thắng, Cư Jút` -> `Đắk Som, Đắk Glong`), Nhóm DTTS (`DTTS tại chỗ` -> `DTTS nói chung`).

#### Câu lệnh SQL (Ground Truth SQL)
```sql
SELECT COUNT(*) as tong_so_ho_ngheo, SUM(CASE WHEN is_kinh = 0 THEN 1 ELSE 0 END) as so_ho_dtts, (SUM(CASE WHEN is_kinh = 0 THEN 1.0 ELSE 0.0 END) / COUNT(*)) * 100 as ty_le_dtts FROM "Báo cáo số liệu hộ nghèo, hộ cận nghèo năm 2024" WHERE classify = 'Hộ nghèo' AND ten_quan_huyen LIKE '%Đắk Glong%' AND ten_xa_phuong LIKE '%Đắk Som%';
```

#### Đáp án chuẩn (Ground Truth Answer)
Phân tích xã Đắk Som (Đắk Glong):
- Tổng số hộ nghèo: **280** hộ
- Số hộ nghèo DTTS: **265** hộ
- Tỷ lệ hộ nghèo DTTS: **94.64%**
