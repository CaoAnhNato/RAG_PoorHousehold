# Golden Questions 30 (Bộ câu hỏi vàng kiểm thử Q&A)

Tài liệu này dùng để phục vụ quá trình rà soát và kiểm thử thủ công chất lượng câu trả lời của chatbot.

## GQ001 — easy — total_count

**Câu hỏi:** Tổng số hộ rà soát theo từng năm là bao nhiêu?

**SQL chuẩn (Gold SQL):**

```sql
SELECT "administrative.year" AS year, COUNT(*) AS household_count FROM households GROUP BY year ORDER BY year;
```

**Kết quả kỳ vọng dạng bảng (Preview):**

| year | household_count |
| --- | --- |
| 2023 | 13446 |
| 2024 | 7472 |

**Đáp án văn bản mẫu:** Theo kết quả truy vấn, tổng số hộ khảo sát năm 2023 được ghi nhận là 13.446 hộ.

**Ghi chú:** Đếm tổng số hộ rà soát nhóm theo năm.

---

## GQ002 — easy — filtered_count

**Câu hỏi:** Năm 2024 có bao nhiêu hộ nghèo?

**SQL chuẩn (Gold SQL):**

```sql
SELECT COUNT(*) AS poor_household_count FROM households WHERE "administrative.year" = 2024 AND "classify" = 'Hộ nghèo';
```

**Kết quả kỳ vọng dạng bảng (Preview):**

| poor_household_count |
| --- |
| 2446 |

**Đáp án văn bản mẫu:** Theo dữ liệu truy vấn, năm 2024 có 2.446 hộ nghèo.

**Ghi chú:** Đếm số hộ nghèo năm 2024 có lọc điều kiện.

---

## GQ003 — easy — filtered_count

**Câu hỏi:** Có bao nhiêu hộ cận nghèo trong năm 2024?

**SQL chuẩn (Gold SQL):**

```sql
SELECT COUNT(*) AS near_poor_household_count FROM households WHERE "administrative.year" = 2024 AND "classify" = 'Hộ cận nghèo';
```

**Kết quả kỳ vọng dạng bảng (Preview):**

| near_poor_household_count |
| --- |
| 3683 |

**Đáp án văn bản mẫu:** Theo dữ liệu truy vấn, năm 2024 có 3.683 hộ cận nghèo.

**Ghi chú:** Đếm số hộ cận nghèo năm 2024 có lọc điều kiện.

---

## GQ004 — easy — aggregate_by_dimension

**Câu hỏi:** Số hộ nghèo theo từng huyện trong năm 2024 là bao nhiêu?

**SQL chuẩn (Gold SQL):**

```sql
SELECT "administrative.district" AS district, COUNT(*) AS poor_household_count FROM households WHERE "administrative.year" = 2024 AND "classify" = 'Hộ nghèo' GROUP BY district ORDER BY poor_household_count DESC;
```

**Kết quả kỳ vọng dạng bảng (Preview):**

| district | poor_household_count |
| --- | --- |
| Huyện Tuy Đức | 829 |
| Huyện Đăk Glong | 538 |
| Huyện Đắk Song | 279 |
| Huyện Đắk Mil | 221 |
| Huyện Cư Jút | 204 |
| Huyện Krông Nô | 189 |
| Huyện Đắk RLấp | 135 |
| Thành phố Gia Nghĩa | 51 |

**Đáp án văn bản mẫu:** Theo kết quả truy vấn, số hộ nghèo theo từng huyện trong năm 2024 là bao nhiêu? được liệt kê chi tiết. Địa phương/nhóm có giá trị cao nhất là Huyện Tuy Đức với 829 hộ.

**Ghi chú:** Số hộ nghèo năm 2024 phân tổ theo huyện.

---

## GQ005 — easy — aggregate_by_dimension

**Câu hỏi:** Thống kê số lượng hộ cận nghèo theo huyện năm 2024.

**SQL chuẩn (Gold SQL):**

```sql
SELECT "administrative.district" AS district, COUNT(*) AS near_poor_household_count FROM households WHERE "administrative.year" = 2024 AND "classify" = 'Hộ cận nghèo' GROUP BY district ORDER BY near_poor_household_count DESC;
```

**Kết quả kỳ vọng dạng bảng (Preview):**

| district | near_poor_household_count |
| --- | --- |
| Huyện Tuy Đức | 917 |
| Huyện Krông Nô | 588 |
| Huyện Đắk Song | 510 |
| Huyện Đăk Glong | 485 |
| Huyện Đắk Mil | 466 |
| Huyện Cư Jút | 304 |
| Huyện Đắk RLấp | 271 |
| Thành phố Gia Nghĩa | 142 |

**Đáp án văn bản mẫu:** Theo kết quả truy vấn, thống kê số lượng hộ cận nghèo theo huyện năm 2024. được liệt kê chi tiết. Địa phương/nhóm có giá trị cao nhất là Huyện Tuy Đức với 917 hộ.

**Ghi chú:** Số hộ cận nghèo năm 2024 phân tổ theo huyện.

---

## GQ006 — easy — aggregate_by_dimension

**Câu hỏi:** Số lượng hộ nghèo và cận nghèo của từng xã thuộc Huyện Tuy Đức năm 2024 là bao nhiêu?

**SQL chuẩn (Gold SQL):**

```sql
SELECT "administrative.commune" AS commune, COUNT(*) AS household_count FROM households WHERE "administrative.year" = 2024 AND "administrative.district" = 'Huyện Tuy Đức' GROUP BY commune ORDER BY household_count DESC;
```

**Kết quả kỳ vọng dạng bảng (Preview):**

| commune | household_count |
| --- | --- |
| Xã Quảng Tâm | 320 |
| Xã Quảng Tân | 320 |
| Xã Đắk RTíh | 320 |
| Xã Đắk Ngo | 319 |
| Xã Quảng Trực | 319 |
| Xã Đắk Búk So | 319 |

**Đáp án văn bản mẫu:** Theo kết quả truy vấn, số lượng hộ nghèo và cận nghèo của từng xã thuộc huyện tuy đức năm 2024 là bao nhiêu? được liệt kê chi tiết. Địa phương/nhóm có giá trị cao nhất là Xã Quảng Tâm với 320 hộ.

**Ghi chú:** Tổng số hộ khảo sát của Huyện Tuy Đức năm 2024 theo từng xã.

---

## GQ007 — easy — average_measure

**Câu hỏi:** Điểm B1 trung bình của các hộ khảo sát năm 2024 là bao nhiêu?

**SQL chuẩn (Gold SQL):**

```sql
SELECT ROUND(AVG(b1Point), 2) AS avg_b1 FROM households WHERE "administrative.year" = 2024;
```

**Kết quả kỳ vọng dạng bảng (Preview):**

| avg_b1 |
| --- |
| 125.34 |

**Đáp án văn bản mẫu:** Theo kết quả truy vấn, điểm trung bình chung được ghi nhận là 125.34 điểm.

**Ghi chú:** Trung bình điểm B1 năm 2024 toàn tỉnh.

---

## GQ008 — easy — average_measure

**Câu hỏi:** Điểm B2 trung bình của các hộ khảo sát năm 2024 là bao nhiêu?

**SQL chuẩn (Gold SQL):**

```sql
SELECT ROUND(AVG(b2Point), 2) AS avg_b2 FROM households WHERE "administrative.year" = 2024;
```

**Kết quả kỳ vọng dạng bảng (Preview):**

| avg_b2 |
| --- |
| 23.67 |

**Đáp án văn bản mẫu:** Theo kết quả truy vấn, điểm trung bình chung được ghi nhận là 23.67 điểm.

**Ghi chú:** Trung bình điểm B2 năm 2024 toàn tỉnh.

---

## GQ009 — easy — aggregate_by_dimension

**Câu hỏi:** Thống kê số hộ nghèo theo từng xã trong năm 2023.

**SQL chuẩn (Gold SQL):**

```sql
SELECT "administrative.commune" AS commune, COUNT(*) AS poor_household_count FROM households WHERE "administrative.year" = 2023 AND "classify" = 'Hộ nghèo' GROUP BY commune ORDER BY poor_household_count DESC;
```

**Kết quả kỳ vọng dạng bảng (Preview):**

| commune | poor_household_count |
| --- | --- |
| Xã Đắk Búk So | 283 |
| Xã Đắk Ngo | 280 |
| Xã Đắk RTíh | 279 |
| Xã Quảng Tâm | 278 |
| Xã Quảng Trực | 278 |
| Xã Quảng Tân | 276 |
| Xã Quảng Sơn | 194 |
| Xã Đắk RMăng | 194 |
| Xã Đắk Som | 193 |
| Xã Quảng Khê | 192 |
| ... | *Đã ẩn bớt 40 dòng* | ... |

**Đáp án văn bản mẫu:** Theo kết quả truy vấn, thống kê số hộ nghèo theo từng xã trong năm 2023. được liệt kê chi tiết. Địa phương/nhóm có giá trị cao nhất là Xã Đắk Búk So với 283 hộ.

**Ghi chú:** Đếm số hộ nghèo năm 2023 phân tổ theo xã.

---

## GQ010 — easy — empty_result_test

**Câu hỏi:** Danh sách các hộ nghèo tại Huyện Cư Jút năm 2025 là bao nhiêu?

**SQL chuẩn (Gold SQL):**

```sql
SELECT "family.code" AS household_id, "family.hostName" AS host_name FROM households WHERE "administrative.year" = 2025 AND "administrative.district" = 'Huyện Cư Jút' AND "classify" = 'Hộ nghèo' LIMIT 5;
```

**Kết quả kỳ vọng dạng bảng (Preview):**

*[Kết quả rỗng]*

**Đáp án văn bản mẫu:** Theo kết quả truy vấn thử nghiệm, không có bản ghi dữ liệu nào thỏa mãn các điều kiện lọc được yêu cầu.

**Ghi chú:** Lọc điều kiện theo năm 2025 không có dữ liệu để kiểm tra trả về rỗng.

---

## GQ011 — medium — topk_query

**Câu hỏi:** Huyện nào có nhiều hộ nghèo nhất trong năm 2024?

**SQL chuẩn (Gold SQL):**

```sql
SELECT "administrative.district" AS district, COUNT(*) AS poor_household_count FROM households WHERE "administrative.year" = 2024 AND "classify" = 'Hộ nghèo' GROUP BY district ORDER BY poor_household_count DESC LIMIT 1;
```

**Kết quả kỳ vọng dạng bảng (Preview):**

| district | poor_household_count |
| --- | --- |
| Huyện Tuy Đức | 829 |

**Đáp án văn bản mẫu:** Theo kết quả truy vấn, địa phương/phân loại hàng đầu là Huyện Tuy Đức với giá trị 829.

**Ghi chú:** Top-1 huyện có nhiều hộ nghèo nhất.

---

## GQ012 — medium — topk_query

**Câu hỏi:** Huyện nào có ít hộ nghèo nhất trong năm 2024?

**SQL chuẩn (Gold SQL):**

```sql
SELECT "administrative.district" AS district, COUNT(*) AS poor_household_count FROM households WHERE "administrative.year" = 2024 AND "classify" = 'Hộ nghèo' GROUP BY district ORDER BY poor_household_count ASC LIMIT 1;
```

**Kết quả kỳ vọng dạng bảng (Preview):**

| district | poor_household_count |
| --- | --- |
| Thành phố Gia Nghĩa | 51 |

**Đáp án văn bản mẫu:** Theo kết quả truy vấn, địa phương/phân loại hàng đầu là Thành phố Gia Nghĩa với giá trị 51.

**Ghi chú:** Top-1 huyện có ít hộ nghèo nhất.

---

## GQ013 — medium — topk_query

**Câu hỏi:** Xã nào thuộc Huyện Krông Nô có nhiều hộ cận nghèo nhất năm 2024?

**SQL chuẩn (Gold SQL):**

```sql
SELECT "administrative.commune" AS commune, COUNT(*) AS near_poor_household_count FROM households WHERE "administrative.year" = 2024 AND "administrative.district" = 'Huyện Krông Nô' AND "classify" = 'Hộ cận nghèo' GROUP BY commune ORDER BY near_poor_household_count DESC LIMIT 1;
```

**Kết quả kỳ vọng dạng bảng (Preview):**

| commune | near_poor_household_count |
| --- | --- |
| Xã Đắk Nang | 55 |

**Đáp án văn bản mẫu:** Theo kết quả truy vấn, địa phương/phân loại hàng đầu là Xã Đắk Nang với giá trị 55.

**Ghi chú:** Top-1 xã thuộc huyện có nhiều hộ cận nghèo nhất.

---

## GQ014 — medium — comparison_by_year

**Câu hỏi:** So sánh số lượng hộ nghèo giữa năm 2023 và năm 2024 theo từng huyện.

**SQL chuẩn (Gold SQL):**

```sql
WITH poor_by_year AS (SELECT "administrative.district" AS district, "administrative.year" AS year, COUNT(*) AS poor_count FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.year" IN (2023, 2024) GROUP BY district, year) SELECT district, SUM(CASE WHEN year = 2023 THEN poor_count ELSE 0 END) AS poor_2023, SUM(CASE WHEN year = 2024 THEN poor_count ELSE 0 END) AS poor_2024, SUM(CASE WHEN year = 2024 THEN poor_count ELSE 0 END) - SUM(CASE WHEN year = 2023 THEN poor_count ELSE 0 END) AS diff_poor FROM poor_by_year GROUP BY district ORDER BY diff_poor DESC;
```

**Kết quả kỳ vọng dạng bảng (Preview):**

| district | poor_2023 | poor_2024 | diff_poor |
| --- | --- | --- | --- |
| Thành phố Gia Nghĩa | 88 | 51 | -37 |
| Huyện Đắk Song | 458 | 279 | -179 |
| Huyện Krông Nô | 370 | 189 | -181 |
| Huyện Đắk Mil | 470 | 221 | -249 |
| Huyện Đắk RLấp | 466 | 135 | -331 |
| Huyện Cư Jút | 809 | 204 | -605 |
| Huyện Đăk Glong | 1344 | 538 | -806 |
| Huyện Tuy Đức | 1674 | 829 | -845 |

**Đáp án văn bản mẫu:** Theo kết quả truy vấn, Huyện Tuy Đức là địa phương có mức thay đổi nổi bật nhất, với chênh lệch -845 đơn vị giữa năm 2023 và 2024.

**Ghi chú:** So sánh chênh lệch tuyệt đối số hộ nghèo giữa 2 năm.

---

## GQ015 — medium — comparison_by_year

**Câu hỏi:** Huyện nào giảm được nhiều hộ nghèo nhất từ năm 2023 sang năm 2024?

**SQL chuẩn (Gold SQL):**

```sql
WITH poor_by_year AS (SELECT "administrative.district" AS district, "administrative.year" AS year, COUNT(*) AS poor_count FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.year" IN (2023, 2024) GROUP BY district, year) SELECT district, SUM(CASE WHEN year = 2023 THEN poor_count ELSE 0 END) AS poor_2023, SUM(CASE WHEN year = 2024 THEN poor_count ELSE 0 END) AS poor_2024, SUM(CASE WHEN year = 2024 THEN poor_count ELSE 0 END) - SUM(CASE WHEN year = 2023 THEN poor_count ELSE 0 END) AS diff_poor FROM poor_by_year GROUP BY district ORDER BY diff_poor ASC LIMIT 1;
```

**Kết quả kỳ vọng dạng bảng (Preview):**

| district | poor_2023 | poor_2024 | diff_poor |
| --- | --- | --- | --- |
| Huyện Tuy Đức | 1674 | 829 | -845 |

**Đáp án văn bản mẫu:** Theo kết quả truy vấn, Huyện Tuy Đức là địa phương có mức thay đổi nổi bật nhất, với chênh lệch -845 đơn vị giữa năm 2023 và 2024.

**Ghi chú:** Tìm huyện có lượng giảm hộ nghèo (hiệu số 2024 - 2023 âm nhất) nhiều nhất.

---

## GQ016 — medium — comparison_by_year

**Câu hỏi:** Huyện nào có số hộ cận nghèo tăng nhiều nhất từ năm 2023 sang năm 2024?

**SQL chuẩn (Gold SQL):**

```sql
WITH near_poor_by_year AS (SELECT "administrative.district" AS district, "administrative.year" AS year, COUNT(*) AS near_poor_count FROM households WHERE "classify" = 'Hộ cận nghèo' AND "administrative.year" IN (2023, 2024) GROUP BY district, year) SELECT district, SUM(CASE WHEN year = 2023 THEN near_poor_count ELSE 0 END) AS near_poor_2023, SUM(CASE WHEN year = 2024 THEN near_poor_count ELSE 0 END) AS near_poor_2024, SUM(CASE WHEN year = 2024 THEN near_poor_count ELSE 0 END) - SUM(CASE WHEN year = 2023 THEN near_poor_count ELSE 0 END) AS diff_near_poor FROM near_poor_by_year GROUP BY district ORDER BY diff_near_poor DESC LIMIT 1;
```

**Kết quả kỳ vọng dạng bảng (Preview):**

| district | near_poor_2023 | near_poor_2024 | diff_near_poor |
| --- | --- | --- | --- |
| Huyện Cư Jút | 305 | 304 | -1 |

**Đáp án văn bản mẫu:** Theo kết quả truy vấn, Huyện Cư Jút là địa phương có mức thay đổi nổi bật nhất, với chênh lệch -1 đơn vị giữa năm 2023 và 2024.

**Ghi chú:** Tìm huyện có lượng tăng hộ cận nghèo nhiều nhất.

---

## GQ017 — medium — average_measure

**Câu hỏi:** Điểm B1 trung bình theo từng huyện trong năm 2024 là bao nhiêu?

**SQL chuẩn (Gold SQL):**

```sql
SELECT "administrative.district" AS district, ROUND(AVG(b1Point), 2) AS avg_b1 FROM households WHERE "administrative.year" = 2024 GROUP BY district ORDER BY avg_b1 DESC;
```

**Kết quả kỳ vọng dạng bảng (Preview):**

| district | avg_b1 |
| --- | --- |
| Thành phố Gia Nghĩa | 135.28 |
| Huyện Krông Nô | 133.4 |
| Huyện Đắk RLấp | 128.7 |
| Huyện Đắk Song | 127.66 |
| Huyện Cư Jút | 124.9 |
| Huyện Đăk Glong | 123.37 |
| Huyện Tuy Đức | 121.45 |
| Huyện Đắk Mil | 120.88 |

**Đáp án văn bản mẫu:** Theo kết quả truy vấn, điểm trung bình cao nhất ghi nhận tại Thành phố Gia Nghĩa với 135.28 điểm.

**Ghi chú:** Điểm B1 trung bình năm 2024 nhóm theo huyện.

---

## GQ018 — medium — average_measure

**Câu hỏi:** Thống kê điểm B2 trung bình theo từng huyện năm 2024.

**SQL chuẩn (Gold SQL):**

```sql
SELECT "administrative.district" AS district, ROUND(AVG(b2Point), 2) AS avg_b2 FROM households WHERE "administrative.year" = 2024 GROUP BY district ORDER BY avg_b2 DESC;
```

**Kết quả kỳ vọng dạng bảng (Preview):**

| district | avg_b2 |
| --- | --- |
| Huyện Đăk Glong | 26.07 |
| Huyện Tuy Đức | 24.87 |
| Thành phố Gia Nghĩa | 23.84 |
| Huyện Cư Jút | 23.14 |
| Huyện Đắk Mil | 23.1 |
| Huyện Đắk Song | 22.61 |
| Huyện Đắk RLấp | 22.15 |
| Huyện Krông Nô | 20.16 |

**Đáp án văn bản mẫu:** Theo kết quả truy vấn, điểm trung bình cao nhất ghi nhận tại Huyện Đăk Glong với 26.07 điểm.

**Ghi chú:** Điểm B2 trung bình năm 2024 nhóm theo huyện.

---

## GQ019 — medium — topk_query

**Câu hỏi:** Tìm 5 xã có số hộ nghèo cao nhất trong năm 2024.

**SQL chuẩn (Gold SQL):**

```sql
SELECT "administrative.commune" AS commune, "administrative.district" AS district, COUNT(*) AS poor_count FROM households WHERE "administrative.year" = 2024 AND "classify" = 'Hộ nghèo' GROUP BY commune, district ORDER BY poor_count DESC LIMIT 5;
```

**Kết quả kỳ vọng dạng bảng (Preview):**

| commune | district | poor_count |
| --- | --- | --- |
| Xã Đắk Búk So | Huyện Tuy Đức | 153 |
| Xã Quảng Tân | Huyện Tuy Đức | 139 |
| Xã Đắk RTíh | Huyện Tuy Đức | 137 |
| Xã Quảng Tâm | Huyện Tuy Đức | 135 |
| Xã Quảng Trực | Huyện Tuy Đức | 134 |

**Đáp án văn bản mẫu:** Theo kết quả truy vấn, địa phương/phân loại hàng đầu là Xã Đắk Búk So với giá trị 153.

**Ghi chú:** Top 5 xã nghèo nhất.

---

## GQ020 — medium — ratio_query

**Câu hỏi:** Tỷ lệ hộ nghèo trên tổng số hộ của từng huyện trong năm 2024 là bao nhiêu?

**SQL chuẩn (Gold SQL):**

```sql
WITH base AS (SELECT "administrative.district" AS district, COUNT(*) AS total_hhs, SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_hhs FROM households WHERE "administrative.year" = 2024 GROUP BY district) SELECT district, total_hhs, poor_hhs, ROUND(100.0 * poor_hhs / NULLIF(total_hhs, 0), 2) AS poor_rate FROM base ORDER BY poor_rate DESC;
```

**Kết quả kỳ vọng dạng bảng (Preview):**

| district | total_hhs | poor_hhs | poor_rate |
| --- | --- | --- | --- |
| Huyện Tuy Đức | 1917 | 829 | 43.24 |
| Huyện Đăk Glong | 1546 | 538 | 34.8 |
| Huyện Cư Jút | 598 | 204 | 34.11 |
| Huyện Đắk Song | 930 | 279 | 30.0 |
| Huyện Đắk Mil | 761 | 221 | 29.04 |
| Huyện Đắk RLấp | 489 | 135 | 27.61 |
| Thành phố Gia Nghĩa | 211 | 51 | 24.17 |
| Huyện Krông Nô | 1020 | 189 | 18.53 |

**Đáp án văn bản mẫu:** Theo kết quả truy vấn, tỷ lệ cao nhất thuộc về Huyện Tuy Đức, đạt 43.24%.

**Ghi chú:** Tính toán tỷ lệ phần trăm hộ nghèo năm 2024 theo huyện.

---

## GQ021 — medium — ratio_query

**Câu hỏi:** Thống kê tỷ lệ hộ cận nghèo trên tổng số hộ của từng huyện năm 2024.

**SQL chuẩn (Gold SQL):**

```sql
WITH base AS (SELECT "administrative.district" AS district, COUNT(*) AS total_hhs, SUM(CASE WHEN "classify" = 'Hộ cận nghèo' THEN 1 ELSE 0 END) AS near_poor_hhs FROM households WHERE "administrative.year" = 2024 GROUP BY district) SELECT district, total_hhs, near_poor_hhs, ROUND(100.0 * near_poor_hhs / NULLIF(total_hhs, 0), 2) AS near_poor_rate FROM base ORDER BY near_poor_rate DESC;
```

**Kết quả kỳ vọng dạng bảng (Preview):**

| district | total_hhs | near_poor_hhs | near_poor_rate |
| --- | --- | --- | --- |
| Thành phố Gia Nghĩa | 211 | 142 | 67.3 |
| Huyện Đắk Mil | 761 | 466 | 61.24 |
| Huyện Krông Nô | 1020 | 588 | 57.65 |
| Huyện Đắk RLấp | 489 | 271 | 55.42 |
| Huyện Đắk Song | 930 | 510 | 54.84 |
| Huyện Cư Jút | 598 | 304 | 50.84 |
| Huyện Tuy Đức | 1917 | 917 | 47.84 |
| Huyện Đăk Glong | 1546 | 485 | 31.37 |

**Đáp án văn bản mẫu:** Theo kết quả truy vấn, tỷ lệ cao nhất thuộc về Thành phố Gia Nghĩa, đạt 67.30%.

**Ghi chú:** Tính toán tỷ lệ phần trăm hộ cận nghèo năm 2024 theo huyện.

---

## GQ022 — medium — aggregate_by_dimension

**Câu hỏi:** Phân bố số lượng hộ gia đình theo từng trạng thái classify trong năm 2024.

**SQL chuẩn (Gold SQL):**

```sql
SELECT "classify" AS poverty_status, COUNT(*) AS household_count FROM households WHERE "administrative.year" = 2024 GROUP BY poverty_status ORDER BY household_count DESC;
```

**Kết quả kỳ vọng dạng bảng (Preview):**

| poverty_status | household_count |
| --- | --- |
| Hộ cận nghèo | 3683 |
| Hộ nghèo | 2446 |
| Hộ không nghèo | 1343 |

**Đáp án văn bản mẫu:** Theo kết quả truy vấn, phân bố số lượng hộ gia đình theo từng trạng thái classify trong năm 2024. được liệt kê chi tiết. Địa phương/nhóm có giá trị cao nhất là Hộ cận nghèo với 3.683 hộ.

**Ghi chú:** Thống kê phân phối của tất cả các nhãn phân loại hộ năm 2024.

---

## GQ023 — hard — ratio_query

**Câu hỏi:** Huyện nào có tỷ lệ hộ nghèo cao nhất trong năm 2024?

**SQL chuẩn (Gold SQL):**

```sql
WITH base AS (SELECT "administrative.district" AS district, COUNT(*) AS total_hhs, SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_hhs FROM households WHERE "administrative.year" = 2024 GROUP BY district) SELECT district, ROUND(100.0 * poor_hhs / NULLIF(total_hhs, 0), 2) AS poor_rate FROM base ORDER BY poor_rate DESC LIMIT 1;
```

**Kết quả kỳ vọng dạng bảng (Preview):**

| district | poor_rate |
| --- | --- |
| Huyện Tuy Đức | 43.24 |

**Đáp án văn bản mẫu:** Theo kết quả truy vấn, tỷ lệ cao nhất thuộc về Huyện Tuy Đức, đạt 43.24%.

**Ghi chú:** Tính tỷ lệ nghèo năm 2024 và lấy huyện cao nhất (Top-1).

---

## GQ024 — hard — comparison_by_year

**Câu hỏi:** Huyện nào có tỷ lệ hộ nghèo giảm nhiều nhất từ năm 2023 sang năm 2024?

**SQL chuẩn (Gold SQL):**

```sql
WITH by_year AS (SELECT "administrative.district" AS district, "administrative.year" AS year, COUNT(*) AS total_hhs, SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_hhs FROM households WHERE "administrative.year" IN (2023, 2024) GROUP BY district, year), rates AS (SELECT district, SUM(CASE WHEN year = 2023 THEN 100.0 * poor_hhs / NULLIF(total_hhs, 0) ELSE 0 END) AS rate_2023, SUM(CASE WHEN year = 2024 THEN 100.0 * poor_hhs / NULLIF(total_hhs, 0) ELSE 0 END) AS rate_2024 FROM by_year GROUP BY district) SELECT district, ROUND(rate_2023, 2) AS poor_rate_2023, ROUND(rate_2024, 2) AS poor_rate_2024, ROUND(rate_2024 - rate_2023, 2) AS rate_diff FROM rates ORDER BY rate_diff ASC LIMIT 1;
```

**Kết quả kỳ vọng dạng bảng (Preview):**

| district | poor_rate_2023 | poor_rate_2024 | rate_diff |
| --- | --- | --- | --- |
| Huyện Cư Jút | 72.62 | 34.11 | -38.51 |

**Đáp án văn bản mẫu:** Theo kết quả truy vấn, Huyện Cư Jút là địa phương có mức thay đổi nổi bật nhất, với chênh lệch -38.51 đơn vị giữa năm 2023 và 2024.

**Ghi chú:** So sánh hiệu số phần trăm tỷ lệ hộ nghèo giữa 2 năm để tìm huyện giảm mạnh nhất.

---

## GQ025 — hard — topk_query

**Câu hỏi:** Xã nào có điểm B1 trung bình cao nhất trong năm 2024?

**SQL chuẩn (Gold SQL):**

```sql
SELECT "administrative.commune" AS commune, "administrative.district" AS district, ROUND(AVG(b1Point), 2) AS avg_b1 FROM households WHERE "administrative.year" = 2024 GROUP BY commune, district ORDER BY avg_b1 DESC LIMIT 1;
```

**Kết quả kỳ vọng dạng bảng (Preview):**

| commune | district | avg_b1 |
| --- | --- | --- |
| Thị trấn Đắk Mâm | Huyện Krông Nô | 149.42 |

**Đáp án văn bản mẫu:** Theo kết quả truy vấn, địa phương/phân loại hàng đầu là Thị trấn Đắk Mâm với giá trị 149.42.

**Ghi chú:** Tính điểm B1 trung bình cấp xã năm 2024 và sắp xếp lấy cao nhất.

---

## GQ026 — hard — topk_query

**Câu hỏi:** Xã nào có điểm B2 trung bình cao nhất trong năm 2024?

**SQL chuẩn (Gold SQL):**

```sql
SELECT "administrative.commune" AS commune, "administrative.district" AS district, ROUND(AVG(b2Point), 2) AS avg_b2 FROM households WHERE "administrative.year" = 2024 GROUP BY commune, district ORDER BY avg_b2 DESC LIMIT 1;
```

**Kết quả kỳ vọng dạng bảng (Preview):**

| commune | district | avg_b2 |
| --- | --- | --- |
| Xã Quảng Khê | Huyện Đăk Glong | 26.74 |

**Đáp án văn bản mẫu:** Theo kết quả truy vấn, địa phương/phân loại hàng đầu là Xã Quảng Khê với giá trị 26.74.

**Ghi chú:** Tính điểm B2 trung bình cấp xã năm 2024 và sắp xếp lấy cao nhất.

---

## GQ027 — hard — average_measure

**Câu hỏi:** Trong số các hộ nghèo năm 2024, huyện nào có điểm B1 trung bình cao nhất?

**SQL chuẩn (Gold SQL):**

```sql
SELECT "administrative.district" AS district, ROUND(AVG(b1Point), 2) AS avg_b1 FROM households WHERE "administrative.year" = 2024 AND "classify" = 'Hộ nghèo' GROUP BY district ORDER BY avg_b1 DESC LIMIT 1;
```

**Kết quả kỳ vọng dạng bảng (Preview):**

| district | avg_b1 |
| --- | --- |
| Thành phố Gia Nghĩa | 122.12 |

**Đáp án văn bản mẫu:** Theo kết quả truy vấn, điểm trung bình cao nhất ghi nhận tại Thành phố Gia Nghĩa với 122.12 điểm.

**Ghi chú:** Tính điểm B1 trung bình cho nhóm đối tượng hộ nghèo năm 2024 phân tổ theo huyện.

---

## GQ028 — hard — average_measure

**Câu hỏi:** Trong số các hộ cận nghèo năm 2024, huyện nào có điểm B2 trung bình cao nhất?

**SQL chuẩn (Gold SQL):**

```sql
SELECT "administrative.district" AS district, ROUND(AVG(b2Point), 2) AS avg_b2 FROM households WHERE "administrative.year" = 2024 AND "classify" = 'Hộ cận nghèo' GROUP BY district ORDER BY avg_b2 DESC LIMIT 1;
```

**Kết quả kỳ vọng dạng bảng (Preview):**

| district | avg_b2 |
| --- | --- |
| Huyện Cư Jút | 18.19 |

**Đáp án văn bản mẫu:** Theo kết quả truy vấn, điểm trung bình cao nhất ghi nhận tại Huyện Cư Jút với 18.19 điểm.

**Ghi chú:** Tính điểm B2 trung bình cho nhóm đối tượng hộ cận nghèo năm 2024 phân tổ theo huyện.

---

## GQ029 — hard — members_query

**Câu hỏi:** Số lượng nhân khẩu thuộc diện hộ nghèo tại các huyện trong năm 2024 là bao nhiêu?

**SQL chuẩn (Gold SQL):**

```sql
SELECT h."administrative.district" AS district, COUNT(m."member.fullName") AS member_count FROM households h JOIN members m ON h."family.code" = m."family.code" AND h."administrative.year" = m."administrative.year" WHERE h."administrative.year" = 2024 AND h."classify" = 'Hộ nghèo' GROUP BY district ORDER BY member_count DESC;
```

**Kết quả kỳ vọng dạng bảng (Preview):**

| district | member_count |
| --- | --- |
| Huyện Tuy Đức | 10550 |
| Huyện Đăk Glong | 9762 |
| Huyện Đắk Song | 6181 |
| Huyện Cư Jút | 5251 |
| Huyện Krông Nô | 4442 |
| Huyện Đắk Mil | 4027 |
| Huyện Đắk RLấp | 3066 |
| Thành phố Gia Nghĩa | 1595 |

**Đáp án văn bản mẫu:** Theo kết quả truy vấn thành viên, huyện có giá trị nổi bật nhất là Huyện Tuy Đức với 10.550.

**Ghi chú:** Truy vấn liên kết (JOIN) households và members để đếm số nhân khẩu.

---

## GQ030 — hard — members_query

**Câu hỏi:** Độ tuổi trung bình của nhân khẩu thuộc diện hộ nghèo theo từng huyện năm 2024 là bao nhiêu?

**SQL chuẩn (Gold SQL):**

```sql
SELECT h."administrative.district" AS district, ROUND(AVG(m."administrative.year" - m."member.birthYear"), 2) AS avg_age FROM households h JOIN members m ON h."family.code" = m."family.code" AND h."administrative.year" = m."administrative.year" WHERE h."administrative.year" = 2024 AND h."classify" = 'Hộ nghèo' GROUP BY district ORDER BY avg_age DESC;
```

**Kết quả kỳ vọng dạng bảng (Preview):**

| district | avg_age |
| --- | --- |
| Thành phố Gia Nghĩa | 38.6 |
| Huyện Đắk RLấp | 38.43 |
| Huyện Đắk Song | 38.42 |
| Huyện Krông Nô | 38.3 |
| Huyện Cư Jút | 38.29 |
| Huyện Tuy Đức | 38.07 |
| Huyện Đắk Mil | 37.96 |
| Huyện Đăk Glong | 37.76 |

**Đáp án văn bản mẫu:** Theo kết quả truy vấn thành viên, huyện có giá trị nổi bật nhất là Thành phố Gia Nghĩa với 38.60.

**Ghi chú:** Truy vấn liên kết (JOIN) households và members để tính độ tuổi trung bình (năm khảo sát - năm sinh).

---

