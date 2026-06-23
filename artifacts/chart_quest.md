# Báo Cáo Kiểm Thử 12 Câu Hỏi Sinh Biểu Đồ

Báo cáo này chứa kết quả chạy chatbot ở chế độ **Biểu Đồ**.

## Câu 1: Cho biết cơ cấu số lượng hộ nghèo theo từng huyện năm 2023
- **Thời gian thực thi:** `5.94 giây`
- **SQL Query:**
```sql
SELECT "administrative.district" AS "Huyện", 
       SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 END) AS "Số hộ nghèo" 
FROM households 
WHERE "administrative.year" = 2023 
GROUP BY "administrative.district";
```
- **Giải thích (Text):**
> Biểu đồ này thể hiện số lượng hộ nghèo phân theo từng huyện trong năm 2023, cho thấy sự chênh lệch rõ rệt giữa các huyện về tình trạng hộ nghèo.

[System] Đã lưu biểu đồ tại: C:\Users\Admin\HUIT - Học Tập\Năm 3\Intern\artifacts\charts\chart_1782228170.html

- **Biểu đồ (Chart):** `[Đã sinh Plotly Figure thành công]`
- **Dữ liệu (DataFrame):**
| Huyện               |   Số hộ nghèo |
|:--------------------|--------------:|
| Huyện Đắk Mil       |           470 |
| Huyện Cư Jút        |           809 |
| Thành phố Gia Nghĩa |            88 |
| Huyện Đắk RLấp      |           466 |
| Huyện Tuy Đức       |          1674 |
| Huyện Đắk Song      |           458 |
| Huyện Đăk Glong     |          1344 |
| Huyện Krông Nô      |           370 |

## Câu 2: Cho biết cơ cấu giới tính là hộ nghèo của thành phố Gia Nghĩa năm 2024
- **Thời gian thực thi:** `7.41 giây`
- **SQL Query:**
```sql
SELECT "family.hostGender" AS "Giới tính", 
       SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 END) AS "Số hộ nghèo" 
FROM households 
WHERE "administrative.district" ILIKE '%Gia Nghĩa%' AND "administrative.year" = 2024 
GROUP BY "family.hostGender";
```
- **Giải thích (Text):**
> Biểu đồ cho thấy sự phân bố số hộ nghèo theo giới tính tại thành phố Gia Nghĩa năm 2024, với số hộ nghèo của nữ cao hơn so với nam.

[System] Đã lưu biểu đồ tại: C:\Users\Admin\HUIT - Học Tập\Năm 3\Intern\artifacts\charts\chart_1782228178.html

- **Biểu đồ (Chart):** `[Đã sinh Plotly Figure thành công]`
- **Dữ liệu (DataFrame):**
| Giới tính   |   Số hộ nghèo |
|:------------|--------------:|
| Nữ          |            31 |
| Nam         |            20 |

## Câu 3: Top 5 huyện có số lượng hộ nghèo thấp nhất năm 2024
- **Thời gian thực thi:** `7.64 giây`
- **SQL Query:**
```sql
SELECT "administrative.district" AS "Huyện", COUNT(*) AS "Số hộ nghèo" 
FROM households 
WHERE classify = 'Hộ nghèo' AND "administrative.year" = 2024 
GROUP BY "administrative.district" 
ORDER BY "Số hộ nghèo" ASC 
LIMIT 5;
```
- **Giải thích (Text):**
> Biểu đồ này hiển thị 5 huyện có số lượng hộ nghèo thấp nhất trong năm 2024, cho thấy sự phân bố hộ nghèo giữa các huyện và giúp nhận diện các khu vực có điều kiện sống tốt hơn.

[System] Đã lưu biểu đồ tại: C:\Users\Admin\HUIT - Học Tập\Năm 3\Intern\artifacts\charts\chart_1782228185.html

- **Biểu đồ (Chart):** `[Đã sinh Plotly Figure thành công]`
- **Dữ liệu (DataFrame):**
| Huyện               |   Số hộ nghèo |
|:--------------------|--------------:|
| Thành phố Gia Nghĩa |            51 |
| Huyện Đắk RLấp      |           135 |
| Huyện Krông Nô      |           189 |
| Huyện Cư Jút        |           204 |
| Huyện Đắk Mil       |           221 |

## Câu 4: Hiển thị biểu đồ xu hướng hộ nghèo và cận nghèo của thành phố gia nghĩa và huyện tuy đức qua các năm
- **Thời gian thực thi:** `7.00 giây`
- **SQL Query:**
```sql
SELECT "administrative.year" AS "Năm", 
       SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 END) AS "Số hộ nghèo", 
       SUM(CASE WHEN classify = 'Hộ cận nghèo' THEN 1 END) AS "Số hộ cận nghèo"
FROM households 
WHERE "administrative.district" IN ('Thành phố Gia Nghĩa', 'Huyện Tuy Đức') 
GROUP BY "administrative.year" 
ORDER BY "administrative.year";
```
- **Giải thích (Text):**
> Biểu đồ thể hiện xu hướng số hộ nghèo và cận nghèo qua các năm, cho thấy sự thay đổi trong tình hình kinh tế xã hội của thành phố Gia Nghĩa và huyện Tuy Đức.

[System] Đã lưu biểu đồ tại: C:\Users\Admin\HUIT - Học Tập\Năm 3\Intern\artifacts\charts\chart_1782228192.html

- **Biểu đồ (Chart):** `[Đã sinh Plotly Figure thành công]`
- **Dữ liệu (DataFrame):**
|   Năm |   Số hộ nghèo |   Số hộ cận nghèo |
|------:|--------------:|------------------:|
|  2023 |          1762 |              1832 |
|  2024 |           880 |              1059 |

## Câu 5: Biểu đồ tỷ lệ hộ cận nghèo từ năm 2023 đến 2024 của thành phố gia nghĩa.
- **Thời gian thực thi:** `6.94 giây`
- **SQL Query:**
```sql
SELECT "administrative.year" AS "Năm", COUNT(CASE WHEN classify = 'Hộ cận nghèo' THEN 1 END) * 100.0 / COUNT(*) AS "Tỷ lệ hộ cận nghèo" 
FROM households 
WHERE "administrative.district" ILIKE '%Gia Nghĩa%' AND "administrative.year" IN (2023, 2024) 
GROUP BY "administrative.year";
```
- **Giải thích (Text):**
> Biểu đồ cho thấy sự gia tăng tỷ lệ hộ cận nghèo từ năm 2023 đến 2024, phản ánh tình hình kinh tế xã hội của thành phố Gia Nghĩa trong giai đoạn này.

[System] Đã lưu biểu đồ tại: C:\Users\Admin\HUIT - Học Tập\Năm 3\Intern\artifacts\charts\chart_1782228199.html

- **Biểu đồ (Chart):** `[Đã sinh Plotly Figure thành công]`
- **Dữ liệu (DataFrame):**
|   Năm |   Tỷ lệ hộ cận nghèo |
|------:|---------------------:|
|  2023 |              65.4902 |
|  2024 |              67.2986 |

## Câu 6: Tôi muốn nhìn nhanh thông qua biểu đồ xem số hộ nghèo ở từng huyện thay đổi như thế nào từ 2023 sang 2024.
- **Thời gian thực thi:** `8.07 giây`
- **SQL Query:**
```sql
SELECT "administrative.district" AS "Huyện", 
       SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 END) AS "Số hộ nghèo" 
FROM households 
WHERE "administrative.year" IN (2023, 2024) 
GROUP BY "administrative.district", "administrative.year" 
ORDER BY "administrative.district", "administrative.year";
```
- **Giải thích (Text):**
> Biểu đồ cho thấy sự thay đổi số hộ nghèo ở từng huyện từ năm 2023 sang 2024, giúp người xem dễ dàng nhận diện các huyện có số hộ nghèo cao và thấp.

[System] Đã lưu biểu đồ tại: C:\Users\Admin\HUIT - Học Tập\Năm 3\Intern\artifacts\charts\chart_1782228206.html

- **Biểu đồ (Chart):** `[Đã sinh Plotly Figure thành công]`
- **Dữ liệu (DataFrame):**
| Huyện               |   Số hộ nghèo |
|:--------------------|--------------:|
| Huyện Cư Jút        |           809 |
| Huyện Cư Jút        |           204 |
| Huyện Krông Nô      |           370 |
| Huyện Krông Nô      |           189 |
| Huyện Tuy Đức       |          1674 |
| Huyện Tuy Đức       |           829 |
| Huyện Đăk Glong     |          1344 |
| Huyện Đăk Glong     |           538 |
| Huyện Đắk Mil       |           470 |
| Huyện Đắk Mil       |           221 |
| Huyện Đắk RLấp      |           466 |
| Huyện Đắk RLấp      |           135 |
| Huyện Đắk Song      |           458 |
| Huyện Đắk Song      |           279 |
| Thành phố Gia Nghĩa |            88 |
| Thành phố Gia Nghĩa |            51 |

## Câu 7: Hiện nay hộ nghèo và hộ cận nghèo đang chiếm tỷ trọng ra sao trên toàn tỉnh năm 2024?
- **Thời gian thực thi:** `8.97 giây`
- **SQL Query:**
```sql
SELECT 
    SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 END) AS "Số hộ nghèo", 
    SUM(CASE WHEN classify = 'Hộ cận nghèo' THEN 1 END) AS "Số hộ cận nghèo", 
    COUNT(CASE WHEN classify = 'Hộ nghèo' THEN 1 END) * 100.0 / COUNT(*) AS "Tỷ lệ hộ nghèo", 
    COUNT(CASE WHEN classify = 'Hộ cận nghèo' THEN 1 END) * 100.0 / COUNT(*) AS "Tỷ lệ hộ cận nghèo" 
FROM households 
WHERE "administrative.year" = 2024;
```
- **Giải thích (Text):**
> Tôi đã gặp lỗi khi cố gắng vẽ biểu đồ: Cannot accept list of column references or list of columns for both `x` and `y`.

- **Biểu đồ (Chart):** `[Lỗi / Không sinh được biểu đồ]`
- **Dữ liệu (DataFrame):**
|   Số hộ nghèo |   Số hộ cận nghèo |   Tỷ lệ hộ nghèo |   Tỷ lệ hộ cận nghèo |
|--------------:|------------------:|-----------------:|---------------------:|
|          2446 |              3683 |          32.7355 |              49.2907 |

## Câu 8: Lập biểu đồ các huyện có số hộ nghèo cao nhất năm 2023, chỉ cần lấy vài huyện nổi bật thôi.
- **Thời gian thực thi:** `6.49 giây`
- **SQL Query:**
```sql
SELECT "administrative.district" AS "Huyện", COUNT(*) AS "Số hộ nghèo"
FROM households
WHERE classify = 'Hộ nghèo' AND "administrative.year" = 2023
GROUP BY "administrative.district"
ORDER BY "Số hộ nghèo" DESC
LIMIT 5;
```
- **Giải thích (Text):**
> Biểu đồ này hiển thị các huyện có số hộ nghèo cao nhất trong năm 2023, giúp nhận diện những khu vực cần được hỗ trợ nhiều nhất.

[System] Đã lưu biểu đồ tại: C:\Users\Admin\HUIT - Học Tập\Năm 3\Intern\artifacts\charts\chart_1782228223.html

- **Biểu đồ (Chart):** `[Đã sinh Plotly Figure thành công]`
- **Dữ liệu (DataFrame):**
| Huyện           |   Số hộ nghèo |
|:----------------|--------------:|
| Huyện Tuy Đức   |          1674 |
| Huyện Đăk Glong |          1344 |
| Huyện Cư Jút    |           809 |
| Huyện Đắk Mil   |           470 |
| Huyện Đắk RLấp  |           466 |

## Câu 9: Tôi muốn xem phân bố hộ nghèo và hộ cận nghèo qua các năm theo từng huyện để dễ so sánh.
- **Thời gian thực thi:** `6.55 giây`
- **SQL Query:**
```sql
SELECT "administrative.year" AS "Năm", "administrative.district" AS "Huyện", 
       SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 END) AS "Số hộ nghèo", 
       SUM(CASE WHEN classify = 'Hộ cận nghèo' THEN 1 END) AS "Số hộ cận nghèo" 
FROM households 
WHERE "administrative.year" IN (2023, 2024) 
GROUP BY "administrative.year", "administrative.district";
```
- **Giải thích (Text):**
> Biểu đồ này cho thấy sự phân bố số hộ nghèo qua các năm theo từng huyện, giúp dễ dàng so sánh tình hình nghèo đói giữa các khu vực.

[System] Đã lưu biểu đồ tại: C:\Users\Admin\HUIT - Học Tập\Năm 3\Intern\artifacts\charts\chart_1782228229.html

- **Biểu đồ (Chart):** `[Đã sinh Plotly Figure thành công]`
- **Dữ liệu (DataFrame):**
|   Năm | Huyện               |   Số hộ nghèo |   Số hộ cận nghèo |
|------:|:--------------------|--------------:|------------------:|
|  2023 | Huyện Đắk RLấp      |           466 |               534 |
|  2024 | Thành phố Gia Nghĩa |            51 |               142 |
|  2023 | Huyện Cư Jút        |           809 |               305 |
|  2024 | Huyện Krông Nô      |           189 |               588 |
|  2023 | Huyện Krông Nô      |           370 |              1651 |
|  2024 | Huyện Cư Jút        |           204 |               304 |
|  2024 | Huyện Đắk RLấp      |           135 |               271 |
|  2024 | Huyện Tuy Đức       |           829 |               917 |
|  2024 | Huyện Đắk Song      |           279 |               510 |
|  2024 | Huyện Đăk Glong     |           538 |               485 |
|  2023 | Huyện Đăk Glong     |          1344 |              2009 |
|  2023 | Thành phố Gia Nghĩa |            88 |               167 |
|  2023 | Huyện Tuy Đức       |          1674 |              1665 |
|  2023 | Huyện Đắk Song      |           458 |               893 |
|  2023 | Huyện Đắk Mil       |           470 |               538 |
|  2024 | Huyện Đắk Mil       |           221 |               466 |

## Câu 10: Trong huyện Tuy Đức, xã nào đang có nhiều hộ nghèo nhất?
- **Thời gian thực thi:** `5.86 giây`
- **SQL Query:**
```sql
SELECT "administrative.commune" AS "Xã", COUNT(*) AS "Số hộ nghèo" FROM households WHERE classify = 'Hộ nghèo' AND "administrative.district" ILIKE '%Tuy Đức%' GROUP BY "administrative.commune" ORDER BY "Số hộ nghèo" DESC LIMIT 1;
```
- **Giải thích (Text):**
> Biểu đồ cho thấy số hộ nghèo tại các xã trong huyện Tuy Đức, giúp xác định xã có nhiều hộ nghèo nhất.

[System] Đã lưu biểu đồ tại: C:\Users\Admin\HUIT - Học Tập\Năm 3\Intern\artifacts\charts\chart_1782228235.html

- **Biểu đồ (Chart):** `[Đã sinh Plotly Figure thành công]`
- **Dữ liệu (DataFrame):**
| Xã            |   Số hộ nghèo |
|:--------------|--------------:|
| Xã Đắk Búk So |           436 |

## Câu 11: Thành phố Gia Nghĩa có cải thiện tình hình hộ nghèo sau một năm không? Hiển thị giúp tôi dễ nhìn.
- **Thời gian thực thi:** `6.32 giây`
- **SQL Query:**
```sql
SELECT 
    "administrative.year" AS "Năm",
    SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 END) AS "Số hộ nghèo"
FROM 
    households
WHERE 
    "administrative.district" ILIKE '%Gia Nghĩa%'
    AND "administrative.year" IN (2023, 2024)
GROUP BY 
    "administrative.year";
```
- **Giải thích (Text):**
> Biểu đồ cho thấy sự giảm số hộ nghèo tại Gia Nghĩa từ năm 2023 đến 2024, cho thấy tình hình đã được cải thiện rõ rệt.

[System] Đã lưu biểu đồ tại: C:\Users\Admin\HUIT - Học Tập\Năm 3\Intern\artifacts\charts\chart_1782228243.html

- **Biểu đồ (Chart):** `[Đã sinh Plotly Figure thành công]`
- **Dữ liệu (DataFrame):**
|   Năm |   Số hộ nghèo |
|------:|--------------:|
|  2023 |            88 |
|  2024 |            51 |

## Câu 12: Những thiếu hụt nào xuất hiện nhiều nhất trong nhóm hộ nghèo?
- **Thời gian thực thi:** `8.79 giây`
- **SQL Query:**
```sql
SELECT 
    SUM(CAST("deprivation.cleanWater" AS INT)) AS "Thiếu nước sinh hoạt", 
    SUM(CAST("deprivation.hygienicToilet" AS INT)) AS "Thiếu nhà tiêu hợp vệ sinh", 
    SUM(CAST("reason.lackProductionLand" AS INT)) AS "Thiếu đất sản xuất", 
    SUM(CAST("reason.lackCapital" AS INT)) AS "Thiếu vốn", 
    SUM(CAST("reason.lackLabor" AS INT)) AS "Thiếu lao động", 
    SUM(CAST("reason.illnessOrAccident" AS INT)) AS "Ốm đau hoặc tai nạn"
FROM households 
WHERE classify = 'Hộ nghèo';
```
- **Giải thích (Text):**
> Biểu đồ cho thấy số lượng các thiếu hụt phổ biến trong nhóm hộ nghèo, giúp xác định những vấn đề cần được ưu tiên giải quyết.

[System] Đã lưu biểu đồ tại: C:\Users\Admin\HUIT - Học Tập\Năm 3\Intern\artifacts\charts\chart_1782228250.html

- **Biểu đồ (Chart):** `[Đã sinh Plotly Figure thành công]`
- **Dữ liệu (DataFrame):**
|   Thiếu nước sinh hoạt |   Thiếu nhà tiêu hợp vệ sinh |   Thiếu đất sản xuất |   Thiếu vốn |   Thiếu lao động |   Ốm đau hoặc tai nạn |
|-----------------------:|-----------------------------:|---------------------:|------------:|-----------------:|----------------------:|
|                    468 |                         1997 |                 2792 |        3825 |             2968 |                  3816 |

