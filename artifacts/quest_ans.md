
# Câu hỏi và Truy vấn SQL tương ứng

Tài liệu cung cấp các câu hỏi, các lệnh SQL tương ứng, và đáp án từ SQL (context) để LLM trả lời.

## 1. Năm 2024, thống kê số hộ nghèo theo huyện.

### Lệnh SQL

```sql
SELECT "administrative.district" AS district, SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_household_count FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.year" = 2024 GROUP BY district ORDER BY poor_household_count DESC
```

### Đáp án (Context từ SQL)

> Dưới đây là thống kê số hộ nghèo theo huyện năm 2024:

| Huyện                 | Số hộ nghèo |
| :--------------------- | -------------: |
| Huyện Tuy Đức       |            829 |
| Huyện Đăk Glong     |            538 |
| Huyện Đắk Song      |            279 |
| Huyện Đắk Mil       |            221 |
| Huyện Cư Jút        |            204 |
| Huyện Krông Nô      |            189 |
| Huyện Đắk RLấp     |            135 |
| Thành phố Gia Nghĩa |             51 |

### Dữ liệu trả về từ DB

```json
[
  {
    "district": "Huyện Tuy Đức",
    "poor_household_count": 829.0
  },
  {
    "district": "Huyện Đăk Glong",
    "poor_household_count": 538.0
  },
  {
    "district": "Huyện Đắk Song",
    "poor_household_count": 279.0
  },
  {
    "district": "Huyện Đắk Mil",
    "poor_household_count": 221.0
  },
  {
    "district": "Huyện Cư Jút",
    "poor_household_count": 204.0
  },
  {
    "district": "Huyện Krông Nô",
    "poor_household_count": 189.0
  },
  {
    "district": "Huyện Đắk RLấp",
    "poor_household_count": 135.0
  },
  {
    "district": "Thành phố Gia Nghĩa",
    "poor_household_count": 51.0
  }
]
```

---

## 2. Huyện nào có nhiều hộ nghèo nhất trong năm 2024?

### Lệnh SQL

```sql
SELECT "administrative.district" AS district, SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_household_count FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.year" = 2024 GROUP BY district ORDER BY poor_household_count DESC LIMIT 1
```

### Đáp án (Context từ SQL)

> Huyện có số hộ nghèo nhiều nhất năm 2024 là Huyện Tuy Đức với 829 hộ nghèo.

### Dữ liệu trả về từ DB

```json
[
  {
    "district": "Huyện Tuy Đức",
    "poor_household_count": 829.0
  }
]
```

---

## 3. Cho tôi biết tình hình nghèo ở Đắk Nông như thế nào?

### Lệnh SQL

```sql
SELECT SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_count, SUM(CASE WHEN "classify" = 'Hộ cận nghèo' THEN 1 ELSE 0 END) AS near_poor_count FROM households WHERE "administrative.year" = 2024
```

### Đáp án (Context từ SQL)

> Tình hình nghèo ở Đắk Nông năm 2024 như sau:

- Tổng số hộ nghèo: 2,446 hộ.
- Tổng số hộ cận nghèo: 3,683 hộ.

### Dữ liệu trả về từ DB

```json
[
  {
    "poor_count": 2446.0,
    "near_poor_count": 3683.0
  }
]
```

---

## 4. Tôi muốn xem nhanh số hộ nghèo và hộ cận nghèo theo từng huyện trong năm 2024.

### Lệnh SQL

```sql
SELECT "administrative.district" AS district, SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_household_count, SUM(CASE WHEN "classify" = 'Hộ cận nghèo' THEN 1 ELSE 0 END) AS near_poor_household_count FROM households WHERE "administrative.year" = 2024 AND "classify" IN ('Hộ nghèo', 'Hộ cận nghèo') GROUP BY district ORDER BY poor_household_count DESC
```

### Đáp án (Context từ SQL)

> Dưới đây là thống kê số hộ nghèo và hộ cận nghèo theo từng huyện năm 2024:

| Huyện                 | Số hộ nghèo | Số hộ cận nghèo |
| :--------------------- | -------------: | ------------------: |
| Huyện Tuy Đức       |            829 |                 917 |
| Huyện Đăk Glong     |            538 |                 485 |
| Huyện Đắk Song      |            279 |                 510 |
| Huyện Đắk Mil       |            221 |                 466 |
| Huyện Cư Jút        |            204 |                 304 |
| Huyện Krông Nô      |            189 |                 588 |
| Huyện Đắk RLấp     |            135 |                 271 |
| Thành phố Gia Nghĩa |             51 |                 142 |

### Dữ liệu trả về từ DB

```json
[
  {
    "district": "Huyện Tuy Đức",
    "poor_household_count": 829.0,
    "near_poor_household_count": 917.0
  },
  {
    "district": "Huyện Đăk Glong",
    "poor_household_count": 538.0,
    "near_poor_household_count": 485.0
  },
  {
    "district": "Huyện Đắk Song",
    "poor_household_count": 279.0,
    "near_poor_household_count": 510.0
  },
  {
    "district": "Huyện Đắk Mil",
    "poor_household_count": 221.0,
    "near_poor_household_count": 466.0
  },
  {
    "district": "Huyện Cư Jút",
    "poor_household_count": 204.0,
    "near_poor_household_count": 304.0
  },
  {
    "district": "Huyện Krông Nô",
    "poor_household_count": 189.0,
    "near_poor_household_count": 588.0
  },
  {
    "district": "Huyện Đắk RLấp",
    "poor_household_count": 135.0,
    "near_poor_household_count": 271.0
  },
  {
    "district": "Thành phố Gia Nghĩa",
    "poor_household_count": 51.0,
    "near_poor_household_count": 142.0
  }
]
```

---

## 5. Năm 2024, tình hình hộ nghèo ở Thành phố Gia Nghĩa có cải thiện hơn so với năm 2023 không?

### Lệnh SQL

```sql
SELECT "administrative.district" AS district,
  SUM(CASE WHEN "administrative.year" = 2023 THEN 1 ELSE 0 END) AS poor_household_count_2023,
  SUM(CASE WHEN "administrative.year" = 2024 THEN 1 ELSE 0 END) AS poor_household_count_2024,
  SUM(CASE WHEN "administrative.year" = 2024 THEN 1 ELSE 0 END) - SUM(CASE WHEN "administrative.year" = 2023 THEN 1 ELSE 0 END) AS diff_poor_household_count
FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.district" = 'Thành phố Gia Nghĩa' AND "administrative.year" IN (2023, 2024)
GROUP BY district
```

### Đáp án (Context từ SQL)

> Số hộ nghèo ở Thành phố Gia Nghĩa giữa năm 2023 và năm 2024 như sau:

- Năm 2023: 88 hộ nghèo
- Năm 2024: 51 hộ nghèo

So sánh cho thấy số hộ nghèo đã giảm 37 hộ từ năm 2023 sang năm 2024.

### Dữ liệu trả về từ DB

```json
[
  {
    "district": "Thành phố Gia Nghĩa",
    "poor_household_count_2023": 88.0,
    "poor_household_count_2024": 51.0,
    "diff_poor_household_count": -37.0
  }
]
```

---

## 6. So với năm 2023, số hộ nghèo ở Đắk Song năm 2024 thay đổi ra sao?

### Lệnh SQL

```sql
SELECT "administrative.district" AS district,
  SUM(CASE WHEN "administrative.year" = 2023 THEN 1 ELSE 0 END) AS poor_household_count_2023,
  SUM(CASE WHEN "administrative.year" = 2024 THEN 1 ELSE 0 END) AS poor_household_count_2024,
  SUM(CASE WHEN "administrative.year" = 2024 THEN 1 ELSE 0 END) - SUM(CASE WHEN "administrative.year" = 2023 THEN 1 ELSE 0 END) AS diff_poor_household_count
FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.district" = 'Huyện Đắk Song' AND "administrative.year" IN (2023, 2024)
GROUP BY district
```

### Đáp án (Context từ SQL)

> Số hộ nghèo ở Huyện Đắk Song thay đổi như sau:

- Năm 2023: 458 hộ
- Năm 2024: 279 hộ
  So sánh cho thấy số hộ nghèo đã giảm 179 hộ.

### Dữ liệu trả về từ DB

```json
[
  {
    "district": "Huyện Đắk Song",
    "poor_household_count_2023": 458.0,
    "poor_household_count_2024": 279.0,
    "diff_poor_household_count": -179.0
  }
]
```

---

## 7. Năm 2024, hộ cận nghèo đang tập trung nhiều ở huyện nào?

### Lệnh SQL

```sql
SELECT "administrative.district" AS district, SUM(CASE WHEN "classify" = 'Hộ cận nghèo' THEN 1 ELSE 0 END) AS near_poor_household_count FROM households WHERE "classify" = 'Hộ cận nghèo' AND "administrative.year" = 2024 GROUP BY district ORDER BY near_poor_household_count DESC LIMIT 1
```

### Đáp án (Context từ SQL)

> Huyện có nhiều hộ cận nghèo nhất năm 2024 là Huyện Tuy Đức với 917 hộ cận nghèo.

### Dữ liệu trả về từ DB

```json
[
  {
    "district": "Huyện Tuy Đức",
    "near_poor_household_count": 917.0
  }
]
```

---

## 8. Ở Huyện Cư Jút, hộ nghèo nào thiếu nhà tiêu hợp vệ sinh nhiều nhất?

### Lệnh SQL

```sql
SELECT SUM(CASE WHEN "classify" = 'Hộ nghèo' AND "deprivation.hygienicToilet" = 1 THEN 1 ELSE 0 END) AS poor_household_lacking_toilet FROM households WHERE "administrative.year" = 2023 AND "administrative.district" = 'Huyện Cư Jút'
```

### Đáp án (Context từ SQL)

> Huyện Cư Jút có 543 hộ nghèo thiếu nhà tiêu hợp vệ sinh trong năm 2023.

### Dữ liệu trả về từ DB

```json
[
  {
    "poor_household_lacking_toilet": 266.0
  }
]
```

---

## 9. So với 2023, số hộ thoát nghèo trong 2024 tăng hay giảm ở Tuy Đức?

### Lệnh SQL

```sql
SELECT "administrative.district" AS district,
  SUM(CASE WHEN "administrative.year" = 2023 THEN 1 ELSE 0 END) AS poor_household_count_2023,
  SUM(CASE WHEN "administrative.year" = 2024 THEN 1 ELSE 0 END) AS poor_household_count_2024,
  SUM(CASE WHEN "administrative.year" = 2024 THEN 1 ELSE 0 END) - SUM(CASE WHEN "administrative.year" = 2023 THEN 1 ELSE 0 END) AS diff_poor_household_count
FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.district" = 'Huyện Tuy Đức' AND "administrative.year" IN (2023, 2024)
GROUP BY district
```

### Đáp án (Context từ SQL)

> Số hộ nghèo ở Huyện Tuy Đức giữa năm 2023 và năm 2024 như sau:

- Năm 2023: 1,674 hộ nghèo
- Năm 2024: 829 hộ nghèo

So sánh:

- Số hộ nghèo giảm 845 hộ từ năm 2023 sang năm 2024 (1,674 - 829 = 845).

Tóm lại, số hộ nghèo đã giảm đáng kể từ năm 2023 đến năm 2024.

### Dữ liệu trả về từ DB

```json
[
  {
    "district": "Huyện Tuy Đức",
    "poor_household_count_2023": 1674.0,
    "poor_household_count_2024": 829.0,
    "diff_poor_household_count": -845.0
  }
]
```

---

## 10. Chủ hộ nào có số thành viên nhiều nhất ở Huyện Đắk Song?

### Lệnh SQL

```sql
SELECT "family.hostName" AS host_name, CAST("family.numberOfMembers" AS INTEGER) AS member_count FROM households WHERE "administrative.district" = 'Huyện Đắk Song' AND "administrative.year" = 2024 ORDER BY member_count DESC LIMIT 1
```

### Đáp án (Context từ SQL)

> Huyện có số hộ nghèo nhiều nhất năm 2023 là Huyện Tuy Đức với 1.674 hộ nghèo.

### Dữ liệu trả về từ DB

```json
[
  {
    "host_name": "Y - Phơm",
    "member_count": 11
  }
]
```

---

## 11. Mức độ thiếu hụt của các hộ nghèo ở Đắk Mil tập trung mạnh vào những chỉ số nào?

### Lệnh SQL

```sql
SELECT 
  SUM(CASE WHEN "deprivation.cleanWater" = 1 THEN 1 ELSE 0 END) AS cleanWater, 
  SUM(CASE WHEN "deprivation.hygienicToilet" = 1 THEN 1 ELSE 0 END) AS hygienicToilet, 
  SUM(CASE WHEN "reason.lackProductionLand" = 1 THEN 1 ELSE 0 END) AS lackProductionLand, 
  SUM(CASE WHEN "reason.lackCapital" = 1 THEN 1 ELSE 0 END) AS lackCapital, 
  SUM(CASE WHEN "reason.lackLabor" = 1 THEN 1 ELSE 0 END) AS lackLabor, 
  SUM(CASE WHEN "reason.illnessOrAccident" = 1 THEN 1 ELSE 0 END) AS illnessOrAccident 
FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.district" = 'Huyện Đắk Mil' AND "administrative.year" = 2024
```

### Đáp án (Context từ SQL)

> Mức độ thiếu hụt của các hộ nghèo ở Huyện Đắk Mil tập trung mạnh vào các chỉ số sau:

- **Xã Đắk Gằn**: 27 hộ nghèo
- **Xã Đắk Sắk**: 27 hộ nghèo
- **Xã Long Sơn**: 25 hộ nghèo
- **Thị trấn Đắk Mil**: 24 hộ nghèo
- **Xã Đức Mạnh**: 23 hộ nghèo
- **Xã Đức Minh**: 20 hộ nghèo
- **Xã Đắk RLa**: 20 hộ nghèo
- **Xã Đắk Lao**: 20 hộ nghèo
- **Xã Thuận An**: 20 hộ nghèo
- **Xã Đắk NDrót**: 15 hộ nghèo

Các xã có số lượng hộ nghèo cao nhất là Đắk Gằn và Đắk Sắk với 27 hộ nghèo mỗi xã.

### Dữ liệu trả về từ DB

```json
[
  {
    "cleanWater": 0.0,
    "hygienicToilet": 6.0,
    "lackProductionLand": 76.0,
    "lackCapital": 100.0,
    "lackLabor": 72.0,
    "illnessOrAccident": 97.0
  }
]
```

---

## 12. Khu vực nào có nhiều hộ cận nghèo nhất nhưng lại ít thiếu hụt nhất?

### Lệnh SQL

```sql
SELECT 
  "administrative.district" AS district, 
  SUM(CASE WHEN "classify" = 'Hộ cận nghèo' THEN 1 ELSE 0 END) AS near_poor_count, 
  AVG(CASE WHEN "classify" = 'Hộ cận nghèo' THEN CAST("deprivation.totalCount" AS FLOAT) ELSE NULL END) AS avg_deprivation 
FROM households 
WHERE "classify" = 'Hộ cận nghèo' AND "administrative.year" = 2024 
GROUP BY district 
ORDER BY near_poor_count DESC, avg_deprivation ASC 
LIMIT 1
```

### Đáp án (Context từ SQL)

> Huyện Tuy Đức là khu vực có nhiều hộ cận nghèo nhất với 917 hộ, và mức độ thiếu hụt trung bình của nhóm này là khoảng 1.6 chỉ số/hộ.

### Dữ liệu trả về từ DB

```json
[
  {
    "district": "Huyện Tuy Đức",
    "near_poor_count": 917.0,
    "avg_deprivation": 1.6008724100327154
  }
]
```

---

## 13. Danh sách hộ nghèo theo các xã của Cư Jút 2024

### Lệnh SQL

```sql
SELECT "administrative.commune" AS commune, COUNT(*) AS poor_count FROM households WHERE "administrative.district" = 'Huyện Cư Jút' AND "classify" = 'Hộ nghèo' AND "administrative.year" = 2024 GROUP BY commune ORDER BY poor_count DESC
```

### Đáp án (Context từ SQL)

> Xã Đắk Wil có nhiều hộ nghèo nhất (31 hộ), tiếp theo là Thị trấn Ea TLing (28 hộ), Xã Tâm Thắng và Xã Ea Pô (đều 26 hộ), v.v.

### Dữ liệu trả về từ DB

```json
[
  {
    "commune": "Xã Đắk Wil",
    "poor_count": 31
  },
  {
    "commune": "Thị trấn Ea TLing",
    "poor_count": 28
  },
  {
    "commune": "Xã Ea Pô",
    "poor_count": 26
  },
  {
    "commune": "Xã Tâm Thắng",
    "poor_count": 26
  },
  {
    "commune": "Xã Đắk DRông",
    "poor_count": 25
  },
  {
    "commune": "Xã Trúc Sơn",
    "poor_count": 25
  },
  {
    "commune": "Xã Cư Knia",
    "poor_count": 23
  },
  {
    "commune": "Xã Nam Dong",
    "poor_count": 20
  }
]
```

---

## 14. Thôn/bon có chủ hộ nghèo là nữ nhiều nhất Đắk Song 2023

### Lệnh SQL

```sql
SELECT "administrative.village_or_group" AS village, COUNT(*) AS count FROM households WHERE "administrative.district" = 'Huyện Đắk Song' AND "administrative.year" = 2023 AND "classify" = 'Hộ nghèo' AND "family.hostGender" = 'Nữ' GROUP BY village ORDER BY count DESC LIMIT 1
```

### Đáp án (Context từ SQL)

> Tổ dân phố 1

### Dữ liệu trả về từ DB

```json
[
  {
    "village": "Tổ dân phố 1",
    "count": 30
  }
]
```

---

## 15. Xã thiếu nước sạch nhiều nhất Tuy Đức 2024

### Lệnh SQL

```sql
SELECT "administrative.commune" AS commune, COUNT(*) AS lacking_clean_water_count FROM households WHERE "administrative.district" = 'Huyện Tuy Đức' AND "administrative.year" = 2024 AND "deprivation.cleanWater" = true GROUP BY commune ORDER BY lacking_clean_water_count DESC LIMIT 1
```

### Đáp án (Context từ SQL)

> Xã Quảng Tâm

### Dữ liệu trả về từ DB

```json
[
  {
    "commune": "Xã Quảng Tâm",
    "lacking_clean_water_count": 1
  }
]
```

---

## 16. Trần Thị Liên ở Đắk Song là dân tộc gì ? Có điểm đánh giá b1 là bao nhiêu ? Có là dân tộc thiểu số ?

### Lệnh SQL

```sql
SELECT "family.ethnicity" AS ethnicity, b1Point AS b1_point, "family.isDTTS" AS is_dtts FROM households WHERE "family.hostName" LIKE '%Trần Thị Liên%' AND "administrative.district" = 'Huyện Đắk Song' LIMIT 1
```

### Đáp án (Context từ SQL)

> Dân tộc Nùng, điểm b1 là 137, là dân tộc thiểu số.

### Dữ liệu trả về từ DB

```json
[
  {
    "ethnicity": "Nùng",
    "b1_point": 137,
    "is_dtts": true
  }
]
```

---

## 17. Huyện Đắk RLấp có tổng cộng bao nhiêu chủ hộ nghèo là nam 2023

### Lệnh SQL

```sql
SELECT COUNT(*) AS male_poor_host_count FROM households WHERE "administrative.district" = 'Huyện Đắk RLấp' AND "administrative.year" = 2023 AND "classify" = 'Hộ nghèo' AND "family.hostGender" = 'Nam'
```

### Đáp án (Context từ SQL)

> 206 hộ.

### Dữ liệu trả về từ DB

```json
[
  {
    "male_poor_host_count": 206
  }
]
```

---

## 18. Số hộ nghèo theo các xã tại Krông Nô 2024, xã nào nhiều hộ nghèo nhất ?

### Lệnh SQL

```sql
SELECT "administrative.commune" AS commune, COUNT(*) AS poor_count FROM households WHERE "administrative.district" = 'Huyện Krông Nô' AND "classify" = 'Hộ nghèo' AND "administrative.year" = 2024 GROUP BY commune ORDER BY poor_count DESC
```

### Đáp án (Context từ SQL)

> Xã Nam Xuân (20 hộ nghèo).

### Dữ liệu trả về từ DB

```json
[
  {
    "commune": "Xã Nam Xuân",
    "poor_count": 20
  },
  {
    "commune": "Xã Đắk Drô",
    "poor_count": 18
  },
  {
    "commune": "Xã Nâm Nung",
    "poor_count": 17
  },
  {
    "commune": "Xã Quảng Phú",
    "poor_count": 17
  },
  {
    "commune": "Xã Nâm NĐir",
    "poor_count": 16
  },
  {
    "commune": "Thị trấn Đắk Mâm",
    "poor_count": 16
  },
  {
    "commune": "Xã Đắk Nang",
    "poor_count": 15
  },
  {
    "commune": "Xã Tân Thành",
    "poor_count": 15
  },
  {
    "commune": "Xã Nam Đà",
    "poor_count": 15
  },
  {
    "commune": "Xã Đức Xuyên",
    "poor_count": 15
  },
  {
    "commune": "Xã Buôn Choah",
    "poor_count": 13
  },
  {
    "commune": "Xã Đắk Sôr",
    "poor_count": 12
  }
]
```

---

## 19. Nhận xét về số lượng chủ hộ nghèo giữa nam và nữ của Tuy Đức 2024

### Lệnh SQL

```sql
SELECT "family.hostGender" AS gender, COUNT(*) AS count FROM households WHERE "administrative.district" = 'Huyện Tuy Đức' AND "administrative.year" = 2024 AND "classify" = 'Hộ nghèo' GROUP BY gender
```

### Đáp án (Context từ SQL)

> Số chủ hộ nghèo là nam (553) nhiều hơn nữ (276).

### Dữ liệu trả về từ DB

```json
[
  {
    "gender": "Nữ",
    "count": 276
  },
  {
    "gender": "Nam",
    "count": 553
  }
]
```

---

## 20. Số lượng chủ hộ dân tộc thiểu số là nữ tại Tuy Đức 2023, có nhiều hơn nam hay không ?

### Lệnh SQL

```sql
SELECT "family.hostGender" AS gender, COUNT(*) AS count FROM households WHERE "administrative.district" = 'Huyện Tuy Đức' AND "administrative.year" = 2023 AND "family.isDTTS" = true GROUP BY gender
```

### Đáp án (Context từ SQL)

> Chủ hộ dân tộc thiểu số là nam (2599) nhiều hơn nữ (741).

### Dữ liệu trả về từ DB

```json
[
  {
    "gender": "Nữ",
    "count": 741
  },
  {
    "gender": "Nam",
    "count": 2599
  }
]
```

# Query Chart

### Câu 1: Cho biết cơ cấu số lượng hộ nghèo theo từng huyện năm 2023

**SQL:**

```sql
SELECT "administrative.district" AS "Huyện", 
       SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 END) AS "Số hộ nghèo", 
       SUM(CASE WHEN classify = 'Hộ cận nghèo' THEN 1 END) AS "Số hộ cận nghèo" 
FROM households 
WHERE "administrative.year" = 2023 
GROUP BY "administrative.district";
```

**DataFrame:**

| Huyện                 | Số hộ nghèo | Số hộ cận nghèo |
| :--------------------- | -------------: | ------------------: |
| Huyện Đắk RLấp     |            466 |                 534 |
| Huyện Đắk Mil       |            470 |                 538 |
| Huyện Đăk Glong     |           1344 |                2009 |
| Huyện Krông Nô      |            370 |                1651 |
| Huyện Tuy Đức       |           1674 |                1665 |
| Huyện Đắk Song      |            458 |                 893 |
| Thành phố Gia Nghĩa |             88 |                 167 |
| Huyện Cư Jút        |            809 |                 305 |

**Kết quả DB:**

```json
[
  {
    "Huyện": "Huyện Đắk RLấp",
    "Số hộ nghèo": 466.0,
    "Số hộ cận nghèo": 534.0
  },
  {
    "Huyện": "Huyện Đắk Mil",
    "Số hộ nghèo": 470.0,
    "Số hộ cận nghèo": 538.0
  },
  {
    "Huyện": "Huyện Đăk Glong",
    "Số hộ nghèo": 1344.0,
    "Số hộ cận nghèo": 2009.0
  },
  {
    "Huyện": "Huyện Krông Nô",
    "Số hộ nghèo": 370.0,
    "Số hộ cận nghèo": 1651.0
  },
  {
    "Huyện": "Huyện Tuy Đức",
    "Số hộ nghèo": 1674.0,
    "Số hộ cận nghèo": 1665.0
  },
  {
    "Huyện": "Huyện Đắk Song",
    "Số hộ nghèo": 458.0,
    "Số hộ cận nghèo": 893.0
  },
  {
    "Huyện": "Thành phố Gia Nghĩa",
    "Số hộ nghèo": 88.0,
    "Số hộ cận nghèo": 167.0
  },
  {
    "Huyện": "Huyện Cư Jút",
    "Số hộ nghèo": 809.0,
    "Số hộ cận nghèo": 305.0
  }
]
```

---

### Câu 2: Cho biết cơ cấu giới tính là hộ nghèo của thành phố Gia Nghĩa năm 2024

**SQL:**

```sql
SELECT "family.hostGender" AS "Giới tính", COUNT(*) AS "Số hộ nghèo" 
FROM households 
WHERE classify = 'Hộ nghèo' AND "administrative.district" ILIKE '%Gia Nghĩa%' AND "administrative.year" = 2024 
GROUP BY "family.hostGender";
```

**DataFrame:**

| Giới tính | Số hộ nghèo |
| :---------- | -------------: |
| Nữ         |             31 |
| Nam         |             20 |

**Kết quả DB:**

```json
[
  {
    "Giới tính": "Nữ",
    "Số hộ nghèo": 31
  },
  {
    "Giới tính": "Nam",
    "Số hộ nghèo": 20
  }
]
```

---

### Câu 3: Top 5 huyện có số lượng hộ nghèo thấp nhất năm 2024

**SQL:**

```sql
SELECT "administrative.district" AS "Huyện", COUNT(*) AS "Số hộ nghèo" 
FROM households 
WHERE classify = 'Hộ nghèo' AND "administrative.year" = 2024 
GROUP BY "administrative.district" 
ORDER BY "Số hộ nghèo" ASC 
LIMIT 5;
```

**DataFrame:**

| Huyện                 | Số hộ nghèo |
| :--------------------- | -------------: |
| Thành phố Gia Nghĩa |             51 |
| Huyện Đắk RLấp     |            135 |
| Huyện Krông Nô      |            189 |
| Huyện Cư Jút        |            204 |
| Huyện Đắk Mil       |            221 |

**Kết quả DB:**

```json
[
  {
    "Huyện": "Thành phố Gia Nghĩa",
    "Số hộ nghèo": 51
  },
  {
    "Huyện": "Huyện Đắk RLấp",
    "Số hộ nghèo": 135
  },
  {
    "Huyện": "Huyện Krông Nô",
    "Số hộ nghèo": 189
  },
  {
    "Huyện": "Huyện Cư Jút",
    "Số hộ nghèo": 204
  },
  {
    "Huyện": "Huyện Đắk Mil",
    "Số hộ nghèo": 221
  }
]
```

---

### Câu 4: Hiển thị biểu đồ xu hướng hộ nghèo và cận nghèo của thành phố gia nghĩa và huyện tuy đức qua các năm

**SQL:**

```sql
SELECT "administrative.year" AS "Năm", 
       SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 END) AS "Số hộ nghèo", 
       SUM(CASE WHEN classify = 'Hộ cận nghèo' THEN 1 END) AS "Số hộ cận nghèo"
FROM households 
WHERE "administrative.district" IN ('Thành phố Gia Nghĩa', 'Huyện Tuy Đức') 
GROUP BY "administrative.year" 
ORDER BY "administrative.year";
```

**DataFrame:**

| Năm | Số hộ nghèo | Số hộ cận nghèo |
| ---: | -------------: | ------------------: |
| 2023 |           1762 |                1832 |
| 2024 |            880 |                1059 |

**Kết quả DB:**

```json
[
  {
    "Năm": 2023,
    "Số hộ nghèo": 1762.0,
    "Số hộ cận nghèo": 1832.0
  },
  {
    "Năm": 2024,
    "Số hộ nghèo": 880.0,
    "Số hộ cận nghèo": 1059.0
  }
]
```

---

### Câu 5: Biểu đồ tỷ lệ hộ cận nghèo từ năm 2023 đến 2024 của thành phố gia nghĩa.

**SQL:**

```sql
SELECT "administrative.year" AS "Năm", COUNT(CASE WHEN classify = 'Hộ cận nghèo' THEN 1 END) * 100.0 / COUNT(*) AS "Tỷ lệ hộ cận nghèo" 
FROM households 
WHERE "administrative.district" ILIKE '%Gia Nghĩa%' AND "administrative.year" IN (2023, 2024) 
GROUP BY "administrative.year";
```

**DataFrame:**

| Năm | Tỷ lệ hộ cận nghèo |
| ---: | ----------------------: |
| 2023 |                 65.4902 |
| 2024 |                 67.2986 |

**Kết quả DB:**

```json
[
  {
    "Năm": 2023,
    "Tỷ lệ hộ cận nghèo": 65.49019607843137
  },
  {
    "Năm": 2024,
    "Tỷ lệ hộ cận nghèo": 67.29857819905213
  }
]
```

---

### Câu 6: Tôi muốn nhìn nhanh thông qua biểu đồ xem số hộ nghèo ở từng huyện thay đổi như thế nào từ 2023 sang 2024.

**SQL:**

```sql
SELECT "administrative.district" AS "Huyện", 
       COUNT(CASE WHEN "administrative.year" = 2023 AND classify = 'Hộ nghèo' THEN 1 END) AS "Số hộ nghèo 2023", 
       COUNT(CASE WHEN "administrative.year" = 2024 AND classify = 'Hộ nghèo' THEN 1 END) AS "Số hộ nghèo 2024" 
FROM households 
WHERE classify = 'Hộ nghèo' 
GROUP BY "administrative.district";
```

**DataFrame:**

| Huyện                 | Số hộ nghèo 2023 | Số hộ nghèo 2024 |
| :--------------------- | ------------------: | ------------------: |
| Huyện Đắk RLấp     |                 466 |                 135 |
| Huyện Đắk Mil       |                 470 |                 221 |
| Huyện Cư Jút        |                 809 |                 204 |
| Huyện Krông Nô      |                 370 |                 189 |
| Huyện Đăk Glong     |                1344 |                 538 |
| Thành phố Gia Nghĩa |                  88 |                  51 |
| Huyện Tuy Đức       |                1674 |                 829 |
| Huyện Đắk Song      |                 458 |                 279 |

**Kết quả DB:**

```json
[
  {
    "Huyện": "Huyện Đắk RLấp",
    "Số hộ nghèo 2023": 466,
    "Số hộ nghèo 2024": 135
  },
  {
    "Huyện": "Huyện Đắk Mil",
    "Số hộ nghèo 2023": 470,
    "Số hộ nghèo 2024": 221
  },
  {
    "Huyện": "Huyện Cư Jút",
    "Số hộ nghèo 2023": 809,
    "Số hộ nghèo 2024": 204
  },
  {
    "Huyện": "Huyện Krông Nô",
    "Số hộ nghèo 2023": 370,
    "Số hộ nghèo 2024": 189
  },
  {
    "Huyện": "Huyện Đăk Glong",
    "Số hộ nghèo 2023": 1344,
    "Số hộ nghèo 2024": 538
  },
  {
    "Huyện": "Thành phố Gia Nghĩa",
    "Số hộ nghèo 2023": 88,
    "Số hộ nghèo 2024": 51
  },
  {
    "Huyện": "Huyện Tuy Đức",
    "Số hộ nghèo 2023": 1674,
    "Số hộ nghèo 2024": 829
  },
  {
    "Huyện": "Huyện Đắk Song",
    "Số hộ nghèo 2023": 458,
    "Số hộ nghèo 2024": 279
  }
]
```

---

### Câu 7: Hiện nay hộ nghèo và hộ cận nghèo đang chiếm tỷ trọng ra sao trên toàn tỉnh năm 2024?

**SQL:**

```sql
SELECT "classify" AS "Phân loại hộ", COUNT(*) AS "Số hộ" FROM households WHERE "administrative.year" = 2024 GROUP BY "classify";
```

**DataFrame:**

| Phân loại hộ   | Số hộ |
| :---------------- | ------: |
| Hộ nghèo        |    2446 |
| Hộ cận nghèo   |    3683 |
| Hộ không nghèo |    1343 |

**Kết quả DB:**

```json
[
  {
    "Phân loại hộ": "Hộ nghèo",
    "Số hộ": 2446
  },
  {
    "Phân loại hộ": "Hộ cận nghèo",
    "Số hộ": 3683
  },
  {
    "Phân loại hộ": "Hộ không nghèo",
    "Số hộ": 1343
  }
]
```

---

### Câu 8: Lập biểu đồ các huyện có số hộ nghèo cao nhất năm 2023, chỉ cần lấy vài huyện nổi bật thôi.

**SQL:**

```sql
SELECT "administrative.district" AS "Huyện", COUNT(*) AS "Số hộ nghèo"
FROM households
WHERE classify = 'Hộ nghèo' AND "administrative.year" = 2023
GROUP BY "administrative.district"
ORDER BY "Số hộ nghèo" DESC
LIMIT 5;
```

**DataFrame:**

| Huyện             | Số hộ nghèo |
| :----------------- | -------------: |
| Huyện Tuy Đức   |           1674 |
| Huyện Đăk Glong |           1344 |
| Huyện Cư Jút    |            809 |
| Huyện Đắk Mil   |            470 |
| Huyện Đắk RLấp |            466 |

**Kết quả DB:**

```json
[
  {
    "Huyện": "Huyện Tuy Đức",
    "Số hộ nghèo": 1674
  },
  {
    "Huyện": "Huyện Đăk Glong",
    "Số hộ nghèo": 1344
  },
  {
    "Huyện": "Huyện Cư Jút",
    "Số hộ nghèo": 809
  },
  {
    "Huyện": "Huyện Đắk Mil",
    "Số hộ nghèo": 470
  },
  {
    "Huyện": "Huyện Đắk RLấp",
    "Số hộ nghèo": 466
  }
]
```

---

### Câu 9: Tôi muốn xem phân bố hộ nghèo và hộ cận nghèo qua các năm theo từng huyện để dễ so sánh.

**SQL:**

```sql
SELECT "administrative.year" AS "Năm", "administrative.district" AS "Huyện", 
       SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 ELSE 0 END) AS "Số hộ nghèo", 
       SUM(CASE WHEN classify = 'Hộ cận nghèo' THEN 1 ELSE 0 END) AS "Số hộ cận nghèo" 
FROM households 
WHERE "administrative.year" IN (2023, 2024) 
GROUP BY "administrative.year", "administrative.district";
```

**DataFrame:**

| Năm | Huyện                 | Số hộ nghèo | Số hộ cận nghèo |
| ---: | :--------------------- | -------------: | ------------------: |
| 2023 | Huyện Đắk RLấp     |            466 |                 534 |
| 2024 | Huyện Đắk Mil       |            221 |                 466 |
| 2023 | Huyện Đắk Mil       |            470 |                 538 |
| 2023 | Huyện Krông Nô      |            370 |                1651 |
| 2024 | Huyện Cư Jút        |            204 |                 304 |
| 2024 | Huyện Tuy Đức       |            829 |                 917 |
| 2024 | Huyện Đắk Song      |            279 |                 510 |
| 2023 | Huyện Tuy Đức       |           1674 |                1665 |
| 2023 | Huyện Đắk Song      |            458 |                 893 |
| 2023 | Huyện Cư Jút        |            809 |                 305 |
| 2024 | Huyện Krông Nô      |            189 |                 588 |
| 2023 | Huyện Đăk Glong     |           1344 |                2009 |
| 2024 | Huyện Đắk RLấp     |            135 |                 271 |
| 2024 | Thành phố Gia Nghĩa |             51 |                 142 |
| 2023 | Thành phố Gia Nghĩa |             88 |                 167 |
| 2024 | Huyện Đăk Glong     |            538 |                 485 |

**Kết quả DB:**

```json
[
  {
    "Năm": 2023,
    "Huyện": "Huyện Đắk RLấp",
    "Số hộ nghèo": 466.0,
    "Số hộ cận nghèo": 534.0
  },
  {
    "Năm": 2024,
    "Huyện": "Huyện Đắk Mil",
    "Số hộ nghèo": 221.0,
    "Số hộ cận nghèo": 466.0
  },
  {
    "Năm": 2023,
    "Huyện": "Huyện Đắk Mil",
    "Số hộ nghèo": 470.0,
    "Số hộ cận nghèo": 538.0
  },
  {
    "Năm": 2023,
    "Huyện": "Huyện Krông Nô",
    "Số hộ nghèo": 370.0,
    "Số hộ cận nghèo": 1651.0
  },
  {
    "Năm": 2024,
    "Huyện": "Huyện Cư Jút",
    "Số hộ nghèo": 204.0,
    "Số hộ cận nghèo": 304.0
  },
  {
    "Năm": 2024,
    "Huyện": "Huyện Tuy Đức",
    "Số hộ nghèo": 829.0,
    "Số hộ cận nghèo": 917.0
  },
  {
    "Năm": 2024,
    "Huyện": "Huyện Đắk Song",
    "Số hộ nghèo": 279.0,
    "Số hộ cận nghèo": 510.0
  },
  {
    "Năm": 2023,
    "Huyện": "Huyện Tuy Đức",
    "Số hộ nghèo": 1674.0,
    "Số hộ cận nghèo": 1665.0
  },
  {
    "Năm": 2023,
    "Huyện": "Huyện Đắk Song",
    "Số hộ nghèo": 458.0,
    "Số hộ cận nghèo": 893.0
  },
  {
    "Năm": 2023,
    "Huyện": "Huyện Cư Jút",
    "Số hộ nghèo": 809.0,
    "Số hộ cận nghèo": 305.0
  },
  {
    "Năm": 2024,
    "Huyện": "Huyện Krông Nô",
    "Số hộ nghèo": 189.0,
    "Số hộ cận nghèo": 588.0
  },
  {
    "Năm": 2023,
    "Huyện": "Huyện Đăk Glong",
    "Số hộ nghèo": 1344.0,
    "Số hộ cận nghèo": 2009.0
  },
  {
    "Năm": 2024,
    "Huyện": "Huyện Đắk RLấp",
    "Số hộ nghèo": 135.0,
    "Số hộ cận nghèo": 271.0
  },
  {
    "Năm": 2024,
    "Huyện": "Thành phố Gia Nghĩa",
    "Số hộ nghèo": 51.0,
    "Số hộ cận nghèo": 142.0
  },
  {
    "Năm": 2023,
    "Huyện": "Thành phố Gia Nghĩa",
    "Số hộ nghèo": 88.0,
    "Số hộ cận nghèo": 167.0
  },
  {
    "Năm": 2024,
    "Huyện": "Huyện Đăk Glong",
    "Số hộ nghèo": 538.0,
    "Số hộ cận nghèo": 485.0
  }
]
```

---

### Câu 10: Trong huyện Tuy Đức, xã nào đang có nhiều hộ nghèo nhất?

**SQL:**

```sql
SELECT "administrative.commune" AS "Xã", COUNT(*) AS "Số hộ nghèo" 
FROM households 
WHERE classify = 'Hộ nghèo' AND "administrative.district" ILIKE '%Tuy Đức%' 
GROUP BY "administrative.commune" 
ORDER BY "Số hộ nghèo" DESC 
LIMIT 1;
```

**DataFrame:**

| Xã               | Số hộ nghèo |
| :---------------- | -------------: |
| Xã Đắk Búk So |            436 |

**Kết quả DB:**

```json
[
  {
    "Xã": "Xã Đắk Búk So",
    "Số hộ nghèo": 436
  }
]
```

---

### Câu 11: Thành phố Gia Nghĩa có cải thiện tình hình hộ nghèo sau một năm không? Hiển thị giúp tôi dễ nhìn.

**SQL:**

```sql
SELECT "administrative.year" AS "Năm", 
       SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 END) AS "Số hộ nghèo" 
FROM households 
WHERE "administrative.district" ILIKE '%Gia Nghĩa%' AND "administrative.year" IN (2023, 2024) 
GROUP BY "administrative.year";
```

**DataFrame:**

| Năm | Số hộ nghèo |
| ---: | -------------: |
| 2023 |             88 |
| 2024 |             51 |

**Kết quả DB:**

```json
[
  {
    "Năm": 2023,
    "Số hộ nghèo": 88.0
  },
  {
    "Năm": 2024,
    "Số hộ nghèo": 51.0
  }
]
```

---

### Câu 12: Những thiếu hụt nào xuất hiện nhiều nhất trong nhóm hộ nghèo?

**SQL:**

```sql
SELECT SUM(CAST("deprivation.cleanWater" AS INT)) AS "Thiếu nước sinh hoạt", SUM(CAST("deprivation.hygienicToilet" AS INT)) AS "Thiếu nhà tiêu hợp vệ sinh", SUM(CAST("reason.lackProductionLand" AS INT)) AS "Thiếu đất sản xuất", SUM(CAST("reason.lackCapital" AS INT)) AS "Thiếu vốn", SUM(CAST("reason.lackLabor" AS INT)) AS "Thiếu lao động", SUM(CAST("reason.illnessOrAccident" AS INT)) AS "Ốm đau hoặc tai nạn" FROM households WHERE classify = 'Hộ nghèo';
```

**DataFrame:**

| Thiếu nước sinh hoạt | Thiếu nhà tiêu hợp vệ sinh | Thiếu đất sản xuất | Thiếu vốn | Thiếu lao động | Ốm đau hoặc tai nạn |
| -----------------------: | ------------------------------: | ----------------------: | ----------: | ----------------: | ----------------------: |
|                      468 |                            1997 |                    2792 |        3825 |              2968 |                    3816 |

**Kết quả DB:**

```json
[
  {
    "Thiếu nước sinh hoạt": 468.0,
    "Thiếu nhà tiêu hợp vệ sinh": 1997.0,
    "Thiếu đất sản xuất": 2792.0,
    "Thiếu vốn": 3825.0,
    "Thiếu lao động": 2968.0,
    "Ốm đau hoặc tai nạn": 3816.0
  }
]
```

---
