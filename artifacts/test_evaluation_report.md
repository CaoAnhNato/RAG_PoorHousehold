# BÁO CÁO ĐÁNH GIÁ CÁC CẶP CÂU HỎI PARAPHRASE

Báo cáo này đánh giá hiệu quả của cấu phần **Query Rewriter** trong việc xử lý các câu hỏi cùng nghĩa nhưng viết khác dạng.

## Thống kê Tổng Hợp
- **Tổng số cặp câu hỏi kiểm thử:** 10
- **Số cặp khớp hoàn toàn SQL sinh ra:** 9 / 10
- **Tỷ lệ khớp SQL (SQL Match Rate):** 90.0%

## Chi Tiết Đánh Giá Từng Cặp Câu Hỏi

### Cặp #1
- **Câu hỏi 1 (Gốc):** `Năm 2023, Huyện Tuy Đức có bao nhiêu hộ nghèo?`
- **Câu hỏi 2 (Paraphrase):** `Số hộ thuộc diện nghèo ở Tuy Đức trong năm 2023 là bao nhiêu?`

- **Câu viết lại 1 (LLM):** *"Năm 2023, Huyện Tuy Đức có bao nhiêu hộ nghèo"*
- **Câu viết lại 2 (LLM):** *"Năm 2023, Huyện Tuy Đức có bao nhiêu hộ nghèo"*

- **Trạng thái Khớp SQL:** ✅ KHỚP

#### SQL generated cho Câu hỏi 1:
```sql
SELECT SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_household_count FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.year" = 2023 AND LOWER("administrative.district") = 'huyện tuy đức' ORDER BY poor_household_count DESC
```

#### SQL generated cho Câu hỏi 2:
```sql
SELECT SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_household_count FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.year" = 2023 AND LOWER("administrative.district") = 'huyện tuy đức' ORDER BY poor_household_count DESC
```

#### Câu trả lời của Câu hỏi 1:
> Năm 2023, huyện Tuy Đức có 1.674 hộ nghèo.

#### Câu trả lời của Câu hỏi 2:
> Năm 2023, huyện Tuy Đức có 1674 hộ nghèo.

---

### Cặp #2
- **Câu hỏi 1 (Gốc):** `Đắk Mil năm 2024 có bao nhiêu hộ cận nghèo?`
- **Câu hỏi 2 (Paraphrase):** `Trong năm 2024, số lượng hộ cận nghèo tại huyện Đắk Mil là bao nhiêu?`

- **Câu viết lại 1 (LLM):** *"Năm 2024, Huyện Đắk Mil có bao nhiêu hộ cận nghèo"*
- **Câu viết lại 2 (LLM):** *"Năm 2024, Huyện Đắk Mil có bao nhiêu hộ cận nghèo"*

- **Trạng thái Khớp SQL:** ✅ KHỚP

#### SQL generated cho Câu hỏi 1:
```sql
SELECT SUM(CASE WHEN "classify" = 'Hộ cận nghèo' THEN 1 ELSE 0 END) AS near_poor_household_count FROM households WHERE "administrative.year" = 2024 AND LOWER("administrative.district") = 'huyện đắk mil' AND LOWER("classify") = 'hộ cận nghèo' ORDER BY near_poor_household_count DESC
```

#### SQL generated cho Câu hỏi 2:
```sql
SELECT SUM(CASE WHEN "classify" = 'Hộ cận nghèo' THEN 1 ELSE 0 END) AS near_poor_household_count FROM households WHERE "administrative.year" = 2024 AND LOWER("administrative.district") = 'huyện đắk mil' AND LOWER("classify") = 'hộ cận nghèo' ORDER BY near_poor_household_count DESC
```

#### Câu trả lời của Câu hỏi 1:
> Năm 2024, huyện Đắk Mil có 466 hộ cận nghèo.

#### Câu trả lời của Câu hỏi 2:
> Năm 2024, huyện Đắk Mil có 466 hộ cận nghèo.

---

### Cặp #3
- **Câu hỏi 1 (Gốc):** `Gia Nghĩa năm 2024 có tổng bao nhiêu hộ nghèo và cận nghèo?`
- **Câu hỏi 2 (Paraphrase):** `Tổng số hộ thuộc nhóm nghèo và cận nghèo ở thành phố Gia Nghĩa năm 2024 là bao nhiêu?`

- **Câu viết lại 1 (LLM):** *"Năm 2024, Thành phố Gia Nghĩa có bao nhiêu hộ nghèo và cận nghèo"*
- **Câu viết lại 2 (LLM):** *"Năm 2024, Thành phố Gia Nghĩa có bao nhiêu hộ nghèo hoặc cận nghèo"*

- **Trạng thái Khớp SQL:** ❌ KHÔNG KHỚP

#### SQL generated cho Câu hỏi 1:
```sql
SELECT SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_household_count, SUM(CASE WHEN "classify" = 'Hộ cận nghèo' THEN 1 ELSE 0 END) AS near_poor_household_count FROM households WHERE "administrative.year" = 2024 AND LOWER("administrative.district") = 'thành phố gia nghĩa' AND LOWER("classify") IN ('hộ nghèo', 'hộ cận nghèo') ORDER BY poor_household_count DESC
```

#### SQL generated cho Câu hỏi 2:
```sql
SELECT SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_household_count, SUM(CASE WHEN "classify" = 'Hộ cận nghèo' THEN 1 ELSE 0 END) AS near_poor_household_count FROM households WHERE "administrative.year" = 2024 AND LOWER("administrative.district") = 'thành phố gia nghĩa' ORDER BY poor_household_count DESC
```

#### Câu trả lời của Câu hỏi 1:
> Năm 2024, Thành phố Gia Nghĩa có số lượng hộ nghèo và cận nghèo cụ thể như sau:

* **Số hộ nghèo:** 51 hộ
* **Số hộ cận nghèo:** 142 hộ

#### Câu trả lời của Câu hỏi 2:
> Năm 2024, Thành phố Gia Nghĩa có:
* Số hộ nghèo: 51 hộ
* Số hộ cận nghèo: 142 hộ

---

### Cặp #4
- **Câu hỏi 1 (Gốc):** `So sánh số hộ nghèo giữa Krông Nô và Đắk Song năm 2024.`
- **Câu hỏi 2 (Paraphrase):** `Năm 2024, huyện Krông Nô hay Đắk Song có số hộ nghèo nhiều hơn?`

- **Câu viết lại 1 (LLM):** *"So sánh số hộ nghèo năm 2024 giữa Huyện Krông Nô và Huyện Đắk Song"*
- **Câu viết lại 2 (LLM):** *"So sánh số hộ nghèo năm 2024 giữa Huyện Krông Nô và Huyện Đắk Song"*

- **Trạng thái Khớp SQL:** ✅ KHỚP

#### SQL generated cho Câu hỏi 1:
```sql
SELECT "administrative.district" AS district, SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_household_count FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.year" = 2024 AND LOWER("administrative.district") IN ('huyện krông nô', 'huyện đắk song') GROUP BY district ORDER BY poor_household_count DESC
```

#### SQL generated cho Câu hỏi 2:
```sql
SELECT "administrative.district" AS district, SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_household_count FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.year" = 2024 AND LOWER("administrative.district") IN ('huyện krông nô', 'huyện đắk song') GROUP BY district ORDER BY poor_household_count DESC
```

#### Câu trả lời của Câu hỏi 1:
> Số lượng hộ nghèo năm 2024 giữa hai huyện như sau:

* **Huyện Đắk Song:** 279 hộ.
* **Huyện Krông Nô:** 189 hộ.

Như vậy, số hộ nghèo của huyện Đắk Song cao hơn huyện Krông Nô là 90 hộ.

#### Câu trả lời của Câu hỏi 2:
> Số hộ nghèo năm 2024 giữa hai huyện như sau:

* **Huyện Đắk Song:** 279 hộ.
* **Huyện Krông Nô:** 189 hộ.

Như vậy, số hộ nghèo của huyện Đắk Song cao hơn huyện Krông Nô là 90 hộ.

---

### Cặp #5
- **Câu hỏi 1 (Gốc):** `Huyện nào có số hộ nghèo cao nhất năm 2023?`
- **Câu hỏi 2 (Paraphrase):** `Trong năm 2023, địa phương nào đứng đầu về số lượng hộ nghèo?`

- **Câu viết lại 1 (LLM):** *"Huyện nào có số hộ nghèo nhiều nhất năm 2023"*
- **Câu viết lại 2 (LLM):** *"Huyện nào có số hộ nghèo nhiều nhất năm 2023"*

- **Trạng thái Khớp SQL:** ✅ KHỚP

#### SQL generated cho Câu hỏi 1:
```sql
SELECT "administrative.district" AS district, SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_household_count FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.year" = 2023 GROUP BY district ORDER BY poor_household_count DESC LIMIT 1
```

#### SQL generated cho Câu hỏi 2:
```sql
SELECT "administrative.district" AS district, SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_household_count FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.year" = 2023 GROUP BY district ORDER BY poor_household_count DESC LIMIT 1
```

#### Câu trả lời của Câu hỏi 1:
> Trong năm 2023, huyện có số hộ nghèo nhiều nhất là **Huyện Tuy Đức** với **1674** hộ.

#### Câu trả lời của Câu hỏi 2:
> Trong năm 2023, huyện có số hộ nghèo nhiều nhất là **Huyện Tuy Đức** với **1674** hộ.

---

### Cặp #6
- **Câu hỏi 1 (Gốc):** `Huyện Đắk RLấp năm 2024 có bao nhiêu hộ nghèo thiếu bảo hiểm y tế?`
- **Câu hỏi 2 (Paraphrase):** `Trong nhóm hộ nghèo ở Đắk RLấp năm 2024, số hộ không có BHYT là bao nhiêu?`

- **Câu viết lại 1 (LLM):** *"Huyện Đắk RLấp năm 2024 có bao nhiêu hộ nghèo thiếu bảo hiểm y tế?"*
- **Câu viết lại 2 (LLM):** *"Trong nhóm hộ nghèo ở Đắk RLấp năm 2024, số hộ không có BHYT là bao nhiêu?"*

- **Trạng thái Khớp SQL:** ✅ KHỚP

#### SQL generated cho Câu hỏi 1:
```sql
-- Không sinh SQL --
```

#### SQL generated cho Câu hỏi 2:
```sql
-- Không sinh SQL --
```

#### Câu trả lời của Câu hỏi 1:
> None

#### Câu trả lời của Câu hỏi 2:
> None

---

### Cặp #7
- **Câu hỏi 1 (Gốc):** `Huyện nào có nhiều hộ nghèo thiếu nước sạch nhất năm 2024?`
- **Câu hỏi 2 (Paraphrase):** `Năm 2024, địa phương nào có số hộ nghèo bị thiếu nước sạch cao nhất?`

- **Câu viết lại 1 (LLM):** *"Huyện nào có nhiều hộ nghèo thiếu nước sạch nhất năm 2024"*
- **Câu viết lại 2 (LLM):** *"Huyện nào có nhiều hộ nghèo thiếu nước sạch nhất năm 2024"*

- **Trạng thái Khớp SQL:** ✅ KHỚP

#### SQL generated cho Câu hỏi 1:
```sql
SELECT "administrative.district" AS district, SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_household_count FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.year" = 2024 AND "deprivation.cleanWater" = True GROUP BY district ORDER BY poor_household_count DESC LIMIT 1
```

#### SQL generated cho Câu hỏi 2:
```sql
SELECT "administrative.district" AS district, SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_household_count FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.year" = 2024 AND "deprivation.cleanWater" = True GROUP BY district ORDER BY poor_household_count DESC LIMIT 1
```

#### Câu trả lời của Câu hỏi 1:
> Trong năm 2024, huyện có nhiều hộ nghèo thiếu nước sạch nhất là:

* **Huyện Đăk Glong:** 11 hộ.

#### Câu trả lời của Câu hỏi 2:
> Trong năm 2024, huyện có nhiều hộ nghèo thiếu nước sạch nhất là:

* **Huyện Đăk Glong:** 11 hộ.

---

### Cặp #8
- **Câu hỏi 1 (Gốc):** `Số hộ nghèo ở Đắk Song thay đổi như thế nào từ 2023 đến 2024?`
- **Câu hỏi 2 (Paraphrase):** `Huyện Đắk Song năm 2024 có số hộ nghèo tăng hay giảm so với năm 2023?`

- **Câu viết lại 1 (LLM):** *"So sánh số hộ nghèo ở Huyện Đắk Song giữa năm 2023 và năm 2024"*
- **Câu viết lại 2 (LLM):** *"So sánh số hộ nghèo ở Huyện Đắk Song giữa năm 2023 và năm 2024"*

- **Trạng thái Khớp SQL:** ✅ KHỚP

#### SQL generated cho Câu hỏi 1:
```sql
WITH base_by_year AS (
  SELECT "administrative.year" AS year, "administrative.year" AS year, ROUND(100.0 * SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS val FROM households WHERE LOWER("administrative.district") = 'huyện đắk song' AND "administrative.year" IN (2023, 2024) GROUP BY year, year
)
SELECT year,
  SUM(CASE WHEN year = 2023 THEN val ELSE 0 END) AS poor_rate_2023,
  SUM(CASE WHEN year = 2024 THEN val ELSE 0 END) AS poor_rate_2024,
  SUM(CASE WHEN year = 2024 THEN val ELSE 0 END) - SUM(CASE WHEN year = 2023 THEN val ELSE 0 END) AS diff_poor_rate
FROM base_by_year
GROUP BY year
ORDER BY diff_poor_rate ASC
```

#### SQL generated cho Câu hỏi 2:
```sql
WITH base_by_year AS (
  SELECT "administrative.year" AS year, "administrative.year" AS year, ROUND(100.0 * SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS val FROM households WHERE LOWER("administrative.district") = 'huyện đắk song' AND "administrative.year" IN (2023, 2024) GROUP BY year, year
)
SELECT year,
  SUM(CASE WHEN year = 2023 THEN val ELSE 0 END) AS poor_rate_2023,
  SUM(CASE WHEN year = 2024 THEN val ELSE 0 END) AS poor_rate_2024,
  SUM(CASE WHEN year = 2024 THEN val ELSE 0 END) - SUM(CASE WHEN year = 2023 THEN val ELSE 0 END) AS diff_poor_rate
FROM base_by_year
GROUP BY year
ORDER BY diff_poor_rate ASC
```

#### Câu trả lời của Câu hỏi 1:
> Dựa trên dữ liệu truy vấn, sự so sánh về tỷ lệ hộ nghèo tại huyện Đắk Song giữa năm 2023 và năm 2024 như sau:

*   **Năm 2023:** Tỷ lệ hộ nghèo là **33.9%**.
*   **Năm 2024:** Tỷ lệ hộ nghèo là **30%**.

Như vậy, tỷ lệ hộ nghèo tại huyện Đắk Song năm 2024 đã giảm so với năm 2023.

#### Câu trả lời của Câu hỏi 2:
> Dựa trên dữ liệu truy vấn, sự so sánh về tỷ lệ hộ nghèo tại huyện Đắk Song giữa năm 2023 và năm 2024 như sau:

*   **Năm 2023:** Tỷ lệ hộ nghèo là **33.9%**.
*   **Năm 2024:** Tỷ lệ hộ nghèo là **30%**.

Như vậy, tỷ lệ hộ nghèo tại huyện Đắk Song năm 2024 đã giảm so với năm 2023.

---

### Cặp #9
- **Câu hỏi 1 (Gốc):** `Có bao nhiêu trẻ em thuộc hộ nghèo hoặc cận nghèo trong năm 2024?`
- **Câu hỏi 2 (Paraphrase):** `Năm 2024, tổng số trẻ em trong các hộ nghèo và cận nghèo là bao nhiêu?`

- **Câu viết lại 1 (LLM):** *"Năm 2024, có bao nhiêu trẻ em thuộc hộ nghèo hoặc cận nghèo"*
- **Câu viết lại 2 (LLM):** *"Năm 2024, có bao nhiêu trẻ em thuộc hộ nghèo hoặc cận nghèo"*

- **Trạng thái Khớp SQL:** ✅ KHỚP

#### SQL generated cho Câu hỏi 1:
```sql
SELECT SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_household_count, SUM(CASE WHEN "classify" = 'Hộ cận nghèo' THEN 1 ELSE 0 END) AS near_poor_household_count FROM households WHERE "administrative.year" = 2024 ORDER BY poor_household_count DESC
```

#### SQL generated cho Câu hỏi 2:
```sql
SELECT SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_household_count, SUM(CASE WHEN "classify" = 'Hộ cận nghèo' THEN 1 ELSE 0 END) AS near_poor_household_count FROM households WHERE "administrative.year" = 2024 ORDER BY poor_household_count DESC
```

#### Câu trả lời của Câu hỏi 1:
> Năm 2024, số lượng hộ nghèo và hộ cận nghèo như sau:

*   **Số hộ nghèo:** 2.446 hộ
*   **Số hộ cận nghèo:** 3.683 hộ

#### Câu trả lời của Câu hỏi 2:
> Năm 2024, số lượng hộ nghèo và hộ cận nghèo như sau:

*   **Số hộ nghèo:** 2.446 hộ
*   **Số hộ cận nghèo:** 3.683 hộ

---

### Cặp #10
- **Câu hỏi 1 (Gốc):** `Dân tộc nào có số hộ nghèo nhiều nhất năm 2024?`
- **Câu hỏi 2 (Paraphrase):** `Trong năm 2024, nhóm dân tộc nào chiếm tỷ lệ hộ nghèo cao nhất?`

- **Câu viết lại 1 (LLM):** *"Thống kê số hộ nghèo theo dân tộc năm 2024"*
- **Câu viết lại 2 (LLM):** *"Thống kê số hộ nghèo theo dân tộc năm 2024"*

- **Trạng thái Khớp SQL:** ✅ KHỚP

#### SQL generated cho Câu hỏi 1:
```sql
SELECT "family.isDTTC" AS local_ethnicity, SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_household_count FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.year" = 2024 GROUP BY local_ethnicity ORDER BY poor_household_count DESC
```

#### SQL generated cho Câu hỏi 2:
```sql
SELECT "family.isDTTC" AS local_ethnicity, SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_household_count FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.year" = 2024 GROUP BY local_ethnicity ORDER BY poor_household_count DESC
```

#### Câu trả lời của Câu hỏi 1:
> Thống kê số hộ nghèo theo dân tộc năm 2024 như sau:

* **Hộ dân tộc thiểu số (True):** 791 hộ
* **Hộ không phải dân tộc thiểu số (False):** 1655 hộ

#### Câu trả lời của Câu hỏi 2:
> Thống kê số hộ nghèo theo dân tộc năm 2024 như sau:

* **Hộ không thuộc dân tộc thiểu số (False):** 1655 hộ
* **Hộ thuộc dân tộc thiểu số (True):** 791 hộ

---

