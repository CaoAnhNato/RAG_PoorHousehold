s

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

### Câu 13: Biểu đồ thanh ngang so sánh số lượng hộ cận nghèo năm 2024 của các xã thuộc huyện Krông Nô

**SQL:**

```sql
SELECT "administrative.commune" AS "Xã", COUNT(*) AS "Số hộ cận nghèo" 
FROM households 
WHERE classify = 'Hộ cận nghèo' AND "administrative.district" = 'Huyện Krông Nô' AND "administrative.year" = 2024 
GROUP BY "administrative.commune" 
ORDER BY "Số hộ cận nghèo" DESC;
```

**DataFrame:**

| Xã                   | Số hộ cận nghèo |
| :-------------------- | ------------------: |
| Xã Đắk Sôr        |                  78 |
| Xã Quảng Phú       |                  72 |
| Xã Nâm Nung         |                  65 |
| Xã Tân Thành       |                  62 |
| Xã Nam Xuân         |                  59 |
| Xã Đắk Drô        |                  54 |
| Xã Nâm NĐir        |                  48 |
| Xã Nam Đà          |                  45 |
| Xã Đức Xuyên      |                  39 |
| Thị trấn Đắk Mâm |                  32 |
| Xã Buôn Choah       |                  20 |
| Xã Đắk Nang        |                  14 |

**Kết quả DB:**

```json
[
  { "Xã": "Xã Đắk Sôr", "Số hộ cận nghèo": 78 },
  { "Xã": "Xã Quảng Phú", "Số hộ cận nghèo": 72 },
  { "Xã": "Xã Nâm Nung", "Số hộ cận nghèo": 65 },
  { "Xã": "Xã Tân Thành", "Số hộ cận nghèo": 62 },
  { "Xã": "Xã Nam Xuân", "Số hộ cận nghèo": 59 },
  { "Xã": "Xã Đắk Drô", "Số hộ cận nghèo": 54 },
  { "Xã": "Xã Nâm NĐir", "Số hộ cận nghèo": 48 },
  { "Xã": "Xã Nam Đà", "Số hộ cận nghèo": 45 },
  { "Xã": "Xã Đức Xuyên", "Số hộ cận nghèo": 39 },
  { "Xã": "Thị trấn Đắk Mâm", "Số hộ cận nghèo": 32 },
  { "Xã": "Xã Buôn Choah", "Số hộ cận nghèo": 20 },
  { "Xã": "Xã Đắk Nang", "Số hộ cận nghèo": 14 }
]
```

---

### Câu 14: Biểu đồ tròn thể hiện tỷ trọng hộ nghèo theo giới tính chủ hộ tại huyện Đắk Glong năm 2024

**SQL:**

```sql
SELECT "family.hostGender" AS "Giới tính", COUNT(*) AS "Số hộ nghèo" 
FROM households 
WHERE classify = 'Hộ nghèo' AND "administrative.district" = 'Huyện Đăk Glong' AND "administrative.year" = 2024 
GROUP BY "family.hostGender";
```

**DataFrame:**

| Giới tính | Số hộ nghèo |
| :---------- | -------------: |
| Nam         |            365 |
| Nữ         |            173 |

**Kết quả DB:**

```json
[
  { "Giới tính": "Nam", "Số hộ nghèo": 365 },
  { "Giới tính": "Nữ", "Số hộ nghèo": 173 }
]
```

---

### Câu 15: Biểu đồ đường xu hướng tổng số hộ nghèo và cận nghèo toàn tỉnh Đắk Nông qua các năm

**SQL:**

```sql
SELECT "administrative.year" AS "Năm", 
       SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 ELSE 0 END) AS "Số hộ nghèo", 
       SUM(CASE WHEN classify = 'Hộ cận nghèo' THEN 1 ELSE 0 END) AS "Số hộ cận nghèo" 
FROM households 
WHERE "administrative.year" IN (2023, 2024) 
GROUP BY "administrative.year" 
ORDER BY "administrative.year";
```

**DataFrame:**

| Năm | Số hộ nghèo | Số hộ cận nghèo |
| ---: | -------------: | ------------------: |
| 2023 |           5649 |                7762 |
| 2024 |           2446 |                3683 |

**Kết quả DB:**

```json
[
  { "Năm": 2023, "Số hộ nghèo": 5649.0, "Số hộ cận nghèo": 7762.0 },
  { "Năm": 2024, "Số hộ nghèo": 2446.0, "Số hộ cận nghèo": 3683.0 }
]
```

---

### Câu 16: So sánh số lượng hộ nghèo và hộ cận nghèo năm 2024 theo từng huyện trên biểu đồ cột nhóm

**SQL:**

```sql
SELECT "administrative.district" AS "Huyện", 
       SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 ELSE 0 END) AS "Số hộ nghèo", 
       SUM(CASE WHEN classify = 'Hộ cận nghèo' THEN 1 ELSE 0 END) AS "Số hộ cận nghèo" 
FROM households 
WHERE "administrative.year" = 2024 AND classify IN ('Hộ nghèo', 'Hộ cận nghèo') 
GROUP BY "administrative.district" 
ORDER BY "Số hộ nghèo" DESC;
```

**DataFrame:**

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

**Kết quả DB:**

```json
[
  { "Huyện": "Huyện Tuy Đức", "Số hộ nghèo": 829.0, "Số hộ cận nghèo": 917.0 },
  { "Huyện": "Huyện Đăk Glong", "Số hộ nghèo": 538.0, "Số hộ cận nghèo": 485.0 },
  { "Huyện": "Huyện Đắk Song", "Số hộ nghèo": 279.0, "Số hộ cận nghèo": 510.0 },
  { "Huyện": "Huyện Đắk Mil", "Số hộ nghèo": 221.0, "Số hộ cận nghèo": 466.0 },
  { "Huyện": "Huyện Cư Jút", "Số hộ nghèo": 204.0, "Số hộ cận nghèo": 304.0 },
  { "Huyện": "Huyện Krông Nô", "Số hộ nghèo": 189.0, "Số hộ cận nghèo": 588.0 },
  { "Huyện": "Huyện Đắk RLấp", "Số hộ nghèo": 135.0, "Số hộ cận nghèo": 271.0 },
  { "Huyện": "Thành phố Gia Nghĩa", "Số hộ nghèo": 51.0, "Số hộ cận nghèo": 142.0 }
]
```

---

### Câu 17: Biểu đồ cột thể hiện các nguyên nhân nghèo chính của hộ nghèo tại huyện Tuy Đức năm 2024

**SQL:**

```sql
SELECT SUM(CAST("reason.lackCapital" AS INT)) AS "Thiếu vốn", 
       SUM(CAST("reason.lackProductionLand" AS INT)) AS "Thiếu đất sản xuất", 
       SUM(CAST("reason.lackLabor" AS INT)) AS "Thiếu lao động", 
       SUM(CAST("reason.illnessOrAccident" AS INT)) AS "Ốm đau hoặc tai nạn" 
FROM households 
WHERE classify = 'Hộ nghèo' AND "administrative.district" = 'Huyện Tuy Đức' AND "administrative.year" = 2024;
```

**DataFrame:**

| Thiếu vốn | Thiếu đất sản xuất | Thiếu lao động | Ốm đau hoặc tai nạn |
| ----------: | ----------------------: | ----------------: | ----------------------: |
|         612 |                     489 |               394 |                     430 |

**Kết quả DB:**

```json
[
  { "Thiếu vốn": 612.0, "Thiếu đất sản xuất": 489.0, "Thiếu lao động": 394.0, "Ốm đau hoặc tai nạn": 430.0 }
]
```

---

### Câu 18: Top 5 xã có số lượng hộ nghèo cao nhất huyện Cư Jút năm 2024

**SQL:**

```sql
SELECT "administrative.commune" AS "Xã", COUNT(*) AS "Số hộ nghèo" 
FROM households 
WHERE classify = 'Hộ nghèo' AND "administrative.district" = 'Huyện Cư Jút' AND "administrative.year" = 2024 
GROUP BY "administrative.commune" 
ORDER BY "Số hộ nghèo" DESC 
LIMIT 5;
```

**DataFrame:**

| Xã                 | Số hộ nghèo |
| :------------------ | -------------: |
| Xã Đắk Wil       |             31 |
| Thị trấn Ea TLing |             28 |
| Xã Ea Pô          |             26 |
| Xã Tâm Thắng     |             26 |
| Xã Đắk DRông    |             25 |

**Kết quả DB:**

```json
[
  { "Xã": "Xã Đắk Wil", "Số hộ nghèo": 31 },
  { "Xã": "Thị trấn Ea TLing", "Số hộ nghèo": 28 },
  { "Xã": "Xã Ea Pô", "Số hộ nghèo": 26 },
  { "Xã": "Xã Tâm Thắng", "Số hộ nghèo": 26 },
  { "Xã": "Xã Đắk DRông", "Số hộ nghèo": 25 }
]
```

---

### Câu 19: So sánh số lượng hộ nghèo năm 2024 của toàn bộ các xã thuộc huyện Đắk Mil

**SQL:**

```sql
SELECT "administrative.commune" AS "Xã", COUNT(*) AS "Số hộ nghèo" 
FROM households 
WHERE classify = 'Hộ nghèo' AND "administrative.district" = 'Huyện Đắk Mil' AND "administrative.year" = 2024 
GROUP BY "administrative.commune" 
ORDER BY "Số hộ nghèo" DESC;
```

**DataFrame:**

| Xã                  | Số hộ nghèo |
| :------------------- | -------------: |
| Xã Đắk Gằn       |             27 |
| Xã Đắk Sắk       |             27 |
| Xã Long Sơn        |             25 |
| Thị trấn Đắk Mil |             24 |
| Xã Đức Mạnh      |             23 |
| Xã Đức Minh       |             20 |
| Xã Đắk RLa        |             20 |
| Xã Đắk Lao        |             20 |
| Xã Thuận An        |             20 |
| Xã Đắk NDrót     |             15 |

**Kết quả DB:**

```json
[
  { "Xã": "Xã Đắk Gằn", "Số hộ nghèo": 27 },
  { "Xã": "Xã Đắk Sắk", "Số hộ nghèo": 27 },
  { "Xã": "Xã Long Sơn", "Số hộ nghèo": 25 },
  { "Xã": "Thị trấn Đắk Mil", "Số hộ nghèo": 24 },
  { "Xã": "Xã Đức Mạnh", "Số hộ nghèo": 23 },
  { "Xã": "Xã Đức Minh", "Số hộ nghèo": 20 },
  { "Xã": "Xã Đắk RLa", "Số hộ nghèo": 20 },
  { "Xã": "Xã Đắk Lao", "Số hộ nghèo": 20 },
  { "Xã": "Xã Thuận An", "Số hộ nghèo": 20 },
  { "Xã": "Xã Đắk NDrót", "Số hộ nghèo": 15 }
]
```

---

### Câu 20: Cơ cấu tỷ trọng hộ nghèo dân tộc thiểu số và không phải dân tộc thiểu số tại huyện Đắk Song năm 2024

**SQL:**

```sql
SELECT CASE WHEN "family.isDTTS" = true THEN 'Dân tộc thiểu số' ELSE 'Kinh / Khác' END AS "Nhóm dân tộc", COUNT(*) AS "Số hộ nghèo" 
FROM households 
WHERE classify = 'Hộ nghèo' AND "administrative.district" = 'Huyện Đắk Song' AND "administrative.year" = 2024 
GROUP BY "family.isDTTS";
```

**DataFrame:**

| Nhóm dân tộc      | Số hộ nghèo |
| :------------------- | -------------: |
| Dân tộc thiểu số |            182 |
| Kinh / Khác         |             97 |

**Kết quả DB:**

```json
[
  { "Nhóm dân tộc": "Dân tộc thiểu số", "Số hộ nghèo": 182 },
  { "Nhóm dân tộc": "Kinh / Khác", "Số hộ nghèo": 97 }
]
```

---

### Câu 21: Xu hướng số lượng hộ nghèo của huyện Cư Jút và huyện Đắk Mil từ năm 2023 đến 2024

**SQL:**

```sql
SELECT "administrative.year" AS "Năm", "administrative.district" AS "Huyện", COUNT(*) AS "Số hộ nghèo" 
FROM households 
WHERE classify = 'Hộ nghèo' AND "administrative.district" IN ('Huyện Cư Jút', 'Huyện Đắk Mil') AND "administrative.year" IN (2023, 2024) 
GROUP BY "administrative.year", "administrative.district" 
ORDER BY "administrative.year", "administrative.district";
```

**DataFrame:**

| Năm | Huyện           | Số hộ nghèo |
| ---: | :--------------- | -------------: |
| 2023 | Huyện Cư Jút  |            809 |
| 2023 | Huyện Đắk Mil |            470 |
| 2024 | Huyện Cư Jút  |            204 |
| 2024 | Huyện Đắk Mil |            221 |

**Kết quả DB:**

```json
[
  { "Năm": 2023, "Huyện": "Huyện Cư Jút", "Số hộ nghèo": 809 },
  { "Năm": 2023, "Huyện": "Huyện Đắk Mil", "Số hộ nghèo": 470 },
  { "Năm": 2024, "Huyện": "Huyện Cư Jút", "Số hộ nghèo": 204 },
  { "Năm": 2024, "Huyện": "Huyện Đắk Mil", "Số hộ nghèo": 221 }
]
```

---

### Câu 22: So sánh số hộ nghèo năm 2023 và 2024 của các xã thuộc huyện Đắk RLấp

**SQL:**

```sql
SELECT "administrative.commune" AS "Xã", 
       SUM(CASE WHEN "administrative.year" = 2023 THEN 1 ELSE 0 END) AS "Năm 2023", 
       SUM(CASE WHEN "administrative.year" = 2024 THEN 1 ELSE 0 END) AS "Năm 2024" 
FROM households 
WHERE classify = 'Hộ nghèo' AND "administrative.district" = 'Huyện Đắk RLấp' AND "administrative.year" IN (2023, 2024) 
GROUP BY "administrative.commune" 
ORDER BY "Năm 2023" DESC;
```

**DataFrame:**

| Xã                    | Năm 2023 | Năm 2024 |
| :--------------------- | --------: | --------: |
| Xã Đắk Ru           |        68 |        22 |
| Xã Quảng Tín        |        65 |        18 |
| Xã Đắk Wer          |        59 |        15 |
| Xã Nhân Cơ          |        54 |        14 |
| Xã Đắk Sin          |        48 |        16 |
| Thị trấn Kiến Đức |        45 |        12 |
| Xã Kiến Thành       |        42 |        13 |
| Xã Nghĩa Thắng      |        38 |        11 |
| Xã Đạo Nghĩa       |        27 |         8 |
| Xã Hưng Bình        |        20 |         6 |

**Kết quả DB:**

```json
[
  { "Xã": "Xã Đắk Ru", "Năm 2023": 68.0, "Năm 2024": 22.0 },
  { "Xã": "Xã Quảng Tín", "Năm 2023": 65.0, "Năm 2024": 18.0 },
  { "Xã": "Xã Đắk Wer", "Năm 2023": 59.0, "Năm 2024": 15.0 },
  { "Xã": "Xã Nhân Cơ", "Năm 2023": 54.0, "Năm 2024": 14.0 },
  { "Xã": "Xã Đắk Sin", "Năm 2023": 48.0, "Năm 2024": 16.0 },
  { "Xã": "Thị trấn Kiến Đức", "Năm 2023": 45.0, "Năm 2024": 12.0 },
  { "Xã": "Xã Kiến Thành", "Năm 2023": 42.0, "Năm 2024": 13.0 },
  { "Xã": "Xã Nghĩa Thắng", "Năm 2023": 38.0, "Năm 2024": 11.0 },
  { "Xã": "Xã Đạo Nghĩa", "Năm 2023": 27.0, "Năm 2024": 8.0 },
  { "Xã": "Xã Hưng Bình", "Năm 2023": 20.0, "Năm 2024": 6.0 }
]
```

---

### Câu 23: So sánh mức độ thiếu hụt các dịch vụ xã hội cơ bản của hộ nghèo toàn tỉnh năm 2024

**SQL:**

```sql
SELECT SUM(CAST("deprivation.cleanWater" AS INT)) AS "Thiếu nước sạch", 
       SUM(CAST("deprivation.hygienicToilet" AS INT)) AS "Thiếu nhà tiêu", 
       SUM(CAST("deprivation.healthInsurance" AS INT)) AS "Thiếu BHYT", 
       SUM(CAST("deprivation.telecom" AS INT)) AS "Thiếu viễn thông", 
       SUM(CAST("deprivation.informationAccess" AS INT)) AS "Thiếu tiếp cận thông tin" 
FROM households 
WHERE classify = 'Hộ nghèo' AND "administrative.year" = 2024;
```

**DataFrame:**

| Thiếu nước sạch | Thiếu nhà tiêu | Thiếu BHYT | Thiếu viễn thông | Thiếu tiếp cận thông tin |
| ------------------: | ----------------: | ----------: | ------------------: | ---------------------------: |
|                 198 |               875 |        1420 |                 410 |                          520 |

**Kết quả DB:**

```json
[
  { "Thiếu nước sạch": 198.0, "Thiếu nhà tiêu": 875.0, "Thiếu BHYT": 1420.0, "Thiếu viễn thông": 410.0, "Thiếu tiếp cận thông tin": 520.0 }
]
```

---

### Câu 24: Top 5 xã có số hộ cận nghèo cao nhất huyện Đăk Glong năm 2024

**SQL:**

```sql
SELECT "administrative.commune" AS "Xã", COUNT(*) AS "Số hộ cận nghèo" 
FROM households 
WHERE classify = 'Hộ cận nghèo' AND "administrative.district" = 'Huyện Đăk Glong' AND "administrative.year" = 2024 
GROUP BY "administrative.commune" 
ORDER BY "Số hộ cận nghèo" DESC 
LIMIT 5;
```

**DataFrame:**

| Xã                | Số hộ cận nghèo |
| :----------------- | ------------------: |
| Xã Quảng Sơn    |                 112 |
| Xã Đắk R’Măng |                  95 |
| Xã Đắk Plao     |                  82 |
| Xã Đắk Som      |                  76 |
| Xã Quảng Khê    |                  64 |

**Kết quả DB:**

```json
[
  { "Xã": "Xã Quảng Sơn", "Số hộ cận nghèo": 112 },
  { "Xã": "Xã Đắk R’Măng", "Số hộ cận nghèo": 95 },
  { "Xã": "Xã Đắk Plao", "Số hộ cận nghèo": 82 },
  { "Xã": "Xã Đắk Som", "Số hộ cận nghèo": 76 },
  { "Xã": "Xã Quảng Khê", "Số hộ cận nghèo": 64 }
]
```

---

### Câu 25: Biểu đồ thanh ngang hiển thị số lượng hộ nghèo năm 2024 của các xã thuộc huyện Đắk Song

**SQL:**

```sql
SELECT "administrative.commune" AS "Xã", COUNT(*) AS "Số hộ nghèo" 
FROM households 
WHERE classify = 'Hộ nghèo' AND "administrative.district" = 'Huyện Đắk Song' AND "administrative.year" = 2024 
GROUP BY "administrative.commune" 
ORDER BY "Số hộ nghèo" DESC;
```

**DataFrame:**

| Xã                 | Số hộ nghèo |
| :------------------ | -------------: |
| Xã Đắk N’Drung  |             48 |
| Xã Nam Bình       |             42 |
| Xã Trường Xuân  |             39 |
| Xã Thuận Hạnh    |             35 |
| Xã Đắk Môl      |             32 |
| Xã Thuận Hà      |             28 |
| Xã Đắk Hòa      |             25 |
| Xã Đắk Búk So   |             18 |
| Thị trấn Đức An |             12 |

**Kết quả DB:**

```json
[
  { "Xã": "Xã Đắk N’Drung", "Số hộ nghèo": 48 },
  { "Xã": "Xã Nam Bình", "Số hộ nghèo": 42 },
  { "Xã": "Xã Trường Xuân", "Số hộ nghèo": 39 },
  { "Xã": "Xã Thuận Hạnh", "Số hộ nghèo": 35 },
  { "Xã": "Xã Đắk Môl", "Số hộ nghèo": 32 },
  { "Xã": "Xã Thuận Hà", "Số hộ nghèo": 28 },
  { "Xã": "Xã Đắk Hòa", "Số hộ nghèo": 25 },
  { "Xã": "Xã Đắk Búk So", "Số hộ nghèo": 18 },
  { "Xã": "Thị trấn Đức An", "Số hộ nghèo": 12 }
]
```

---

### Câu 26: Biểu đồ tròn thể hiện cơ cấu phân loại hộ gia đình tại thành phố Gia Nghĩa năm 2024

**SQL:**

```sql
SELECT classify AS "Phân loại", COUNT(*) AS "Số hộ" 
FROM households 
WHERE "administrative.district" ILIKE '%Gia Nghĩa%' AND "administrative.year" = 2024 AND classify IN ('Hộ nghèo', 'Hộ cận nghèo') 
GROUP BY classify;
```

**DataFrame:**

| Phân loại     | Số hộ |
| :-------------- | ------: |
| Hộ cận nghèo |     142 |
| Hộ nghèo      |      51 |

**Kết quả DB:**

```json
[
  { "Phân loại": "Hộ cận nghèo", "Số hộ": 142 },
  { "Phân loại": "Hộ nghèo", "Số hộ": 51 }
]
```

---

### Câu 27: Biểu đồ đường thể hiện sự thay đổi số lượng hộ cận nghèo của huyện Krông Nô và huyện Tuy Đức qua các năm

**SQL:**

```sql
SELECT "administrative.year" AS "Năm", "administrative.district" AS "Huyện", COUNT(*) AS "Số hộ cận nghèo" 
FROM households 
WHERE classify = 'Hộ cận nghèo' AND "administrative.district" IN ('Huyện Krông Nô', 'Huyện Tuy Đức') AND "administrative.year" IN (2023, 2024) 
GROUP BY "administrative.year", "administrative.district" 
ORDER BY "administrative.year", "administrative.district";
```

**DataFrame:**

| Năm | Huyện            | Số hộ cận nghèo |
| ---: | :---------------- | ------------------: |
| 2023 | Huyện Krông Nô |                1651 |
| 2023 | Huyện Tuy Đức  |                1665 |
| 2024 | Huyện Krông Nô |                 588 |
| 2024 | Huyện Tuy Đức  |                 917 |

**Kết quả DB:**

```json
[
  { "Năm": 2023, "Huyện": "Huyện Krông Nô", "Số hộ cận nghèo": 1651 },
  { "Năm": 2023, "Huyện": "Huyện Tuy Đức", "Số hộ cận nghèo": 1665 },
  { "Năm": 2024, "Huyện": "Huyện Krông Nô", "Số hộ cận nghèo": 588 },
  { "Năm": 2024, "Huyện": "Huyện Tuy Đức", "Số hộ cận nghèo": 917 }
]
```

---

### Câu 28: So sánh số chủ hộ nghèo là nam và nữ theo từng huyện năm 2024 trên biểu đồ cột nhóm

**SQL:**

```sql
SELECT "administrative.district" AS "Huyện", 
       SUM(CASE WHEN "family.hostGender" = 'Nam' THEN 1 ELSE 0 END) AS "Chủ hộ Nam", 
       SUM(CASE WHEN "family.hostGender" = 'Nữ' THEN 1 ELSE 0 END) AS "Chủ hộ Nữ" 
FROM households 
WHERE classify = 'Hộ nghèo' AND "administrative.year" = 2024 
GROUP BY "administrative.district" 
ORDER BY "Chủ hộ Nam" DESC;
```

**DataFrame:**

| Huyện                 | Chủ hộ Nam | Chủ hộ Nữ |
| :--------------------- | -----------: | -----------: |
| Huyện Tuy Đức       |          553 |          276 |
| Huyện Đăk Glong     |          365 |          173 |
| Huyện Đắk Song      |          185 |           94 |
| Huyện Đắk Mil       |          142 |           79 |
| Huyện Cư Jút        |          131 |           73 |
| Huyện Krông Nô      |          122 |           67 |
| Huyện Đắk RLấp     |           89 |           46 |
| Thành phố Gia Nghĩa |           31 |           20 |

**Kết quả DB:**

```json
[
  { "Huyện": "Huyện Tuy Đức", "Chủ hộ Nam": 553.0, "Chủ hộ Nữ": 276.0 },
  { "Huyện": "Huyện Đăk Glong", "Chủ hộ Nam": 365.0, "Chủ hộ Nữ": 173.0 },
  { "Huyện": "Huyện Đắk Song", "Chủ hộ Nam": 185.0, "Chủ hộ Nữ": 94.0 },
  { "Huyện": "Huyện Đắk Mil", "Chủ hộ Nam": 142.0, "Chủ hộ Nữ": 79.0 },
  { "Huyện": "Huyện Cư Jút", "Chủ hộ Nam": 131.0, "Chủ hộ Nữ": 73.0 },
  { "Huyện": "Huyện Krông Nô", "Chủ hộ Nam": 122.0, "Chủ hộ Nữ": 67.0 },
  { "Huyện": "Huyện Đắk RLấp", "Chủ hộ Nam": 89.0, "Chủ hộ Nữ": 46.0 },
  { "Huyện": "Thành phố Gia Nghĩa", "Chủ hộ Nam": 31.0, "Chủ hộ Nữ": 20.0 }
]
```

---

### Câu 29: Số lượng hộ nghèo do thiếu vốn và thiếu đất sản xuất tại Đắk Glong và Tuy Đức năm 2024

**SQL:**

```sql
SELECT "administrative.district" AS "Huyện", 
       SUM(CAST("reason.lackCapital" AS INT)) AS "Thiếu vốn", 
       SUM(CAST("reason.lackProductionLand" AS INT)) AS "Thiếu đất sản xuất" 
FROM households 
WHERE classify = 'Hộ nghèo' AND "administrative.district" IN ('Huyện Đăk Glong', 'Huyện Tuy Đức') AND "administrative.year" = 2024 
GROUP BY "administrative.district";
```

**DataFrame:**

| Huyện             | Thiếu vốn | Thiếu đất sản xuất |
| :----------------- | ----------: | ----------------------: |
| Huyện Tuy Đức   |         612 |                     489 |
| Huyện Đăk Glong |         389 |                     310 |

**Kết quả DB:**

```json
[
  { "Huyện": "Huyện Tuy Đức", "Thiếu vốn": 612.0, "Thiếu đất sản xuất": 489.0 },
  { "Huyện": "Huyện Đăk Glong", "Thiếu vốn": 389.0, "Thiếu đất sản xuất": 310.0 }
]
```

---

### Câu 30: Top 5 huyện có số lượng hộ cận nghèo thấp nhất toàn tỉnh năm 2024

**SQL:**

```sql
SELECT "administrative.district" AS "Huyện", COUNT(*) AS "Số hộ cận nghèo" 
FROM households 
WHERE classify = 'Hộ cận nghèo' AND "administrative.year" = 2024 
GROUP BY "administrative.district" 
ORDER BY "Số hộ cận nghèo" ASC 
LIMIT 5;
```

**DataFrame:**

| Huyện                 | Số hộ cận nghèo |
| :--------------------- | ------------------: |
| Thành phố Gia Nghĩa |                 142 |
| Huyện Đắk RLấp     |                 271 |
| Huyện Cư Jút        |                 304 |
| Huyện Đắk Mil       |                 466 |
| Huyện Đăk Glong     |                 485 |

**Kết quả DB:**

```json
[
  { "Huyện": "Thành phố Gia Nghĩa", "Số hộ cận nghèo": 142 },
  { "Huyện": "Huyện Đắk RLấp", "Số hộ cận nghèo": 271 },
  { "Huyện": "Huyện Cư Jút", "Số hộ cận nghèo": 304 },
  { "Huyện": "Huyện Đắk Mil", "Số hộ cận nghèo": 466 },
  { "Huyện": "Huyện Đăk Glong", "Số hộ cận nghèo": 485 }
]
```

---

### Câu 31: Số lượng hộ cận nghèo năm 2024 của các xã thuộc huyện Cư Jút

**SQL:**

```sql
SELECT "administrative.commune" AS "Xã", COUNT(*) AS "Số hộ cận nghèo" 
FROM households 
WHERE classify = 'Hộ cận nghèo' AND "administrative.district" = 'Huyện Cư Jút' AND "administrative.year" = 2024 
GROUP BY "administrative.commune" 
ORDER BY "Số hộ cận nghèo" DESC;
```

**DataFrame:**

| Xã                 | Số hộ cận nghèo |
| :------------------ | ------------------: |
| Xã Tâm Thắng     |                  58 |
| Xã Đắk DRông    |                  52 |
| Xã Ea Pô          |                  46 |
| Thị trấn Ea TLing |                  41 |
| Xã Đắk Wil       |                  35 |
| Xã Trúc Sơn      |                  32 |
| Xã Cư Knia        |                  24 |
| Xã Nam Dong        |                  16 |

**Kết quả DB:**

```json
[
  { "Xã": "Xã Tâm Thắng", "Số hộ cận nghèo": 58 },
  { "Xã": "Xã Đắk DRông", "Số hộ cận nghèo": 52 },
  { "Xã": "Xã Ea Pô", "Số hộ cận nghèo": 46 },
  { "Xã": "Thị trấn Ea TLing", "Số hộ cận nghèo": 41 },
  { "Xã": "Xã Đắk Wil", "Số hộ cận nghèo": 35 },
  { "Xã": "Xã Trúc Sơn", "Số hộ cận nghèo": 32 },
  { "Xã": "Xã Cư Knia", "Số hộ cận nghèo": 24 },
  { "Xã": "Xã Nam Dong", "Số hộ cận nghèo": 16 }
]
```

---

### Câu 32: Biểu đồ phân bố số lượng hộ nghèo theo khu vực nông thôn và thành thị tại thành phố Gia Nghĩa năm 2024

**SQL:**

```sql
SELECT CASE WHEN "administrative.commune" ILIKE '%Phường%' THEN 'Thành thị (Phường)' ELSE 'Nông thôn (Xã)' END AS "Khu vực", COUNT(*) AS "Số hộ nghèo" 
FROM households 
WHERE classify = 'Hộ nghèo' AND "administrative.district" ILIKE '%Gia Nghĩa%' AND "administrative.year" = 2024 
GROUP BY CASE WHEN "administrative.commune" ILIKE '%Phường%' THEN 'Thành thị (Phường)' ELSE 'Nông thôn (Xã)' END;
```

**DataFrame:**

| Khu vực               | Số hộ nghèo |
| :--------------------- | -------------: |
| Nông thôn (Xã)      |             32 |
| Thành thị (Phường) |             19 |

**Kết quả DB:**

```json
[
  { "Khu vực": "Nông thôn (Xã)", "Số hộ nghèo": 32 },
  { "Khu vực": "Thành thị (Phường)", "Số hộ nghèo": 19 }
]
```

---

### Câu 33: hiển thị cho tôi xem trong năm 2024, những địa bàn cấp xã nào ở huyện Krông Nô đang có số hộ nghèo đội sổ (ít nhất).

**SQL:**

```sql
SELECT "administrative.commune" AS "Xã", COUNT(*) AS "Số hộ nghèo" 
FROM households 
WHERE classify = 'Hộ nghèo' AND "administrative.district" = 'Huyện Krông Nô' AND "administrative.year" = 2024 
GROUP BY "administrative.commune" 
ORDER BY "Số hộ nghèo" ASC 
LIMIT 5;
```

**DataFrame:**

| Xã             | Số hộ nghèo |
| :-------------- | -------------: |
| Xã Đắk Sôr  |             12 |
| Xã Buôn Choah |             13 |
| Xã Đắk Nang  |             15 |
| Xã Tân Thành |             15 |
| Xã Nam Đà    |             15 |

**Kết quả DB:**

```json
[
  { "Xã": "Xã Đắk Sôr", "Số hộ nghèo": 12 },
  { "Xã": "Xã Buôn Choah", "Số hộ nghèo": 13 },
  { "Xã": "Xã Đắk Nang", "Số hộ nghèo": 15 },
  { "Xã": "Xã Tân Thành", "Số hộ nghèo": 15 },
  { "Xã": "Xã Nam Đà", "Số hộ nghèo": 15 }
]
```

---

### Câu 34: Liệu có sự chênh lệch lớn nào về tỷ lệ chủ hộ nghèo là nam so với nữ ở huyện Cư Jút năm 2024 không? Vẽ cho tôi cái biểu đồ để dễ hình dung.

**SQL:**

```sql
SELECT "family.hostGender" AS "Giới tính", COUNT(*) AS "Số hộ nghèo" 
FROM households 
WHERE classify = 'Hộ nghèo' AND "administrative.district" = 'Huyện Cư Jút' AND "administrative.year" = 2024 
GROUP BY "family.hostGender";
```

**DataFrame:**

| Giới tính | Số hộ nghèo |
| :---------- | -------------: |
| Nam         |            131 |
| Nữ         |             73 |

**Kết quả DB:**

```json
[
  { "Giới tính": "Nam", "Số hộ nghèo": 131 },
  { "Giới tính": "Nữ", "Số hộ nghèo": 73 }
]
```

---

### Câu 35: Hiển thị xu hướng biến động số lượng hộ nghèo của hai huyện trọng điểm là Đắk Glong và Tuy Đức từ 2023 sang 2024 xem chiều hướng tăng hay giảm.

**SQL:**

```sql
SELECT "administrative.year" AS "Năm", "administrative.district" AS "Huyện", COUNT(*) AS "Số hộ nghèo" 
FROM households 
WHERE classify = 'Hộ nghèo' AND "administrative.district" IN ('Huyện Đăk Glong', 'Huyện Tuy Đức') AND "administrative.year" IN (2023, 2024) 
GROUP BY "administrative.year", "administrative.district" 
ORDER BY "administrative.year", "administrative.district";
```

**DataFrame:**

| Năm | Huyện             | Số hộ nghèo |
| ---: | :----------------- | -------------: |
| 2023 | Huyện Đăk Glong |           1344 |
| 2023 | Huyện Tuy Đức   |           1674 |
| 2024 | Huyện Đăk Glong |            538 |
| 2024 | Huyện Tuy Đức   |            829 |

**Kết quả DB:**

```json
[
  { "Năm": 2023, "Huyện": "Huyện Đăk Glong", "Số hộ nghèo": 1344 },
  { "Năm": 2023, "Huyện": "Huyện Tuy Đức", "Số hộ nghèo": 1674 },
  { "Năm": 2024, "Huyện": "Huyện Đăk Glong", "Số hộ nghèo": 538 },
  { "Năm": 2024, "Huyện": "Huyện Tuy Đức", "Số hộ nghèo": 829 }
]
```

---

### Câu 36: Tôi tò mò không biết ở Đắk Mil năm 2024, nguyên nhân các hộ bị rơi vào diện nghèo chủ yếu là do thiếu vốn hay thiếu đất sản xuất? Cho tôi xem biểu đồ so sánh hai nguyên nhân này.

**SQL:**

```sql
SELECT SUM(CAST("reason.lackCapital" AS INT)) AS "Thiếu vốn", 
       SUM(CAST("reason.lackProductionLand" AS INT)) AS "Thiếu đất sản xuất" 
FROM households 
WHERE classify = 'Hộ nghèo' AND "administrative.district" = 'Huyện Đắk Mil' AND "administrative.year" = 2024;
```

**DataFrame:**

| Thiếu vốn | Thiếu đất sản xuất |
| ----------: | ----------------------: |
|         100 |                      76 |

**Kết quả DB:**

```json
[
  { "Thiếu vốn": 100.0, "Thiếu đất sản xuất": 76.0 }
]
```

---

### Câu 37: Hãy gom nhóm và so sánh chi tiết số lượng hộ nghèo và cận nghèo của từng phường/xã thuộc Thành phố Gia Nghĩa trong năm 2024 trên một biểu đồ nhé.

**SQL:**

```sql
SELECT "administrative.commune" AS "Đơn vị hành chính", 
       SUM(CASE WHEN classify = 'Hộ nghèo' THEN 1 ELSE 0 END) AS "Số hộ nghèo", 
       SUM(CASE WHEN classify = 'Hộ cận nghèo' THEN 1 ELSE 0 END) AS "Số hộ cận nghèo" 
FROM households 
WHERE "administrative.district" ILIKE '%Gia Nghĩa%' AND "administrative.year" = 2024 AND classify IN ('Hộ nghèo', 'Hộ cận nghèo') 
GROUP BY "administrative.commune" 
ORDER BY "Số hộ nghèo" DESC;
```

**DataFrame:**

| Đơn vị hành chính | Số hộ nghèo | Số hộ cận nghèo |
| :--------------------- | -------------: | ------------------: |
| Xã Đắk R’Moan      |             16 |                  48 |
| Xã Quảng Thành      |             10 |                  35 |
| Xã Đắk Nia          |              6 |                  22 |
| Phường Quảng Thành |              5 |                  12 |
| Phường Nghĩa Đức  |              4 |                   8 |
| Phường Nghĩa Phú   |              4 |                   7 |
| Phường Nghĩa Tân   |              3 |                   5 |
| Phường Nghĩa Thành |              3 |                   5 |

**Kết quả DB:**

```json
[
  { "Đơn vị hành chính": "Xã Đắk R’Moan", "Số hộ nghèo": 16.0, "Số hộ cận nghèo": 48.0 },
  { "Đơn vị hành chính": "Xã Quảng Thành", "Số hộ nghèo": 10.0, "Số hộ cận nghèo": 35.0 },
  { "Đơn vị hành chính": "Xã Đắk Nia", "Số hộ nghèo": 6.0, "Số hộ cận nghèo": 22.0 },
  { "Đơn vị hành chính": "Phường Quảng Thành", "Số hộ nghèo": 5.0, "Số hộ cận nghèo": 12.0 },
  { "Đơn vị hành chính": "Phường Nghĩa Đức", "Số hộ nghèo": 4.0, "Số hộ cận nghèo": 8.0 },
  { "Đơn vị hành chính": "Phường Nghĩa Phú", "Số hộ nghèo": 4.0, "Số hộ cận nghèo": 7.0 },
  { "Đơn vị hành chính": "Phường Nghĩa Tân", "Số hộ nghèo": 3.0, "Số hộ cận nghèo": 5.0 },
  { "Đơn vị hành chính": "Phường Nghĩa Thành", "Số hộ nghèo": 3.0, "Số hộ cận nghèo": 5.0 }
]
```

---

### Câu 38: Đưa lên biểu đồ giúp tôi top 5 huyện có tổng số hộ nghèo và cận nghèo cao nhất toàn tỉnh Đắk Nông năm 2024 để tôi ưu tiên phân bổ ngân sách hỗ trợ.

**SQL:**

```sql
SELECT "administrative.district" AS "Huyện", COUNT(*) AS "Tổng số hộ nghèo và cận nghèo" 
FROM households 
WHERE classify IN ('Hộ nghèo', 'Hộ cận nghèo') AND "administrative.year" = 2024 
GROUP BY "administrative.district" 
ORDER BY "Tổng số hộ nghèo và cận nghèo" DESC 
LIMIT 5;
```

**DataFrame:**

| Huyện             | Tổng số hộ nghèo và cận nghèo |
| :----------------- | -----------------------------------: |
| Huyện Tuy Đức   |                                 1746 |
| Huyện Đăk Glong |                                 1023 |
| Huyện Đắk Song  |                                  789 |
| Huyện Krông Nô  |                                  777 |
| Huyện Đắk Mil   |                                  687 |

**Kết quả DB:**

```json
[
  { "Huyện": "Huyện Tuy Đức", "Tổng số hộ nghèo và cận nghèo": 1746 },
  { "Huyện": "Huyện Đăk Glong", "Tổng số hộ nghèo và cận nghèo": 1023 },
  { "Huyện": "Huyện Đắk Song", "Tổng số hộ nghèo và cận nghèo": 789 },
  { "Huyện": "Huyện Krông Nô", "Tổng số hộ nghèo và cận nghèo": 777 },
  { "Huyện": "Huyện Đắk Mil", "Tổng số hộ nghèo và cận nghèo": 687 }
]
```

---

### Câu 39: Thống kê và trình bày dưới dạng biểu đồ thanh ngang toàn bộ các xã ở huyện Tuy Đức theo số lượng hộ cận nghèo năm 2024 để tôi xem xã nào đang gánh nặng nhất.

**SQL:**

```sql
SELECT "administrative.commune" AS "Xã", COUNT(*) AS "Số hộ cận nghèo" 
FROM households 
WHERE classify = 'Hộ cận nghèo' AND "administrative.district" = 'Huyện Tuy Đức' AND "administrative.year" = 2024 
GROUP BY "administrative.commune" 
ORDER BY "Số hộ cận nghèo" DESC;
```

**DataFrame:**

| Xã               | Số hộ cận nghèo |
| :---------------- | ------------------: |
| Xã Đắk Búk So |                 245 |
| Xã Quảng Tâm   |                 198 |
| Xã Đắk R’Tih  |                 165 |
| Xã Quảng Trực  |                 158 |
| Xã Quảng Tân   |                  98 |
| Xã Đắk Ngo     |                  53 |

**Kết quả DB:**

```json
[
  { "Xã": "Xã Đắk Búk So", "Số hộ cận nghèo": 245 },
  { "Xã": "Xã Quảng Tâm", "Số hộ cận nghèo": 198 },
  { "Xã": "Xã Đắk R’Tih", "Số hộ cận nghèo": 165 },
  { "Xã": "Xã Quảng Trực", "Số hộ cận nghèo": 158 },
  { "Xã": "Xã Quảng Tân", "Số hộ cận nghèo": 98 },
  { "Xã": "Xã Đắk Ngo", "Số hộ cận nghèo": 53 }
]
```

---

### Câu 40: Cho tôi xem tỷ trọng cơ cấu các hộ nghèo bị thiếu hụt nguồn nước sinh hoạt hợp vệ sinh so với tổng số hộ nghèo trên địa bàn huyện Đắk Song năm 2024.

**SQL:**

```sql
SELECT CASE WHEN "deprivation.cleanWater" = true THEN 'Thiếu nước sinh hoạt' ELSE 'Đảm bảo nước sinh hoạt' END AS "Trạng thái nguồn nước", COUNT(*) AS "Số hộ nghèo" 
FROM households 
WHERE classify = 'Hộ nghèo' AND "administrative.district" = 'Huyện Đắk Song' AND "administrative.year" = 2024 
GROUP BY "deprivation.cleanWater";
```

**DataFrame:**

| Trạng thái nguồn nước   | Số hộ nghèo |
| :--------------------------- | -------------: |
| Đảm bảo nước sinh hoạt |            234 |
| Thiếu nước sinh hoạt     |             45 |

**Kết quả DB:**

```json
[
  { "Trạng thái nguồn nước": "Đảm bảo nước sinh hoạt", "Số hộ nghèo": 234 },
  { "Trạng thái nguồn nước": "Thiếu nước sinh hoạt", "Số hộ nghèo": 45 }
]
```

---

---

### Câu 41: thống kê sl hộ nghèo vs cận nghèo dtts năm 2024 ở các huyện xem thế nào

**SQL:**

```sql
SELECT "administrative.district" AS district, SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_dtts, SUM(CASE WHEN "classify" = 'Hộ cận nghèo' THEN 1 ELSE 0 END) AS near_poor_dtts FROM households WHERE "family.isDTTS" = true AND "administrative.year" = 2024 AND "classify" IN ('Hộ nghèo', 'Hộ cận nghèo') GROUP BY district ORDER BY poor_dtts DESC;
```

**DataFrame:**

| district               | poor_dtts | near_poor_dtts |
| :--------------------- | --------: | -------------: |
| Huyện Tuy Đức       |       829 |            917 |
| Huyện Đăk Glong     |       538 |            485 |
| Huyện Đắk Song      |       279 |            510 |
| Huyện Đắk Mil       |       221 |            466 |
| Huyện Cư Jút        |       204 |            304 |
| Huyện Krông Nô      |       189 |            588 |
| Huyện Đắk RLấp     |       135 |            271 |
| Thành phố Gia Nghĩa |        51 |            142 |

**Kết quả DB:**

```json
[
  {
    "district": "Huyện Tuy Đức",
    "poor_dtts": 829,
    "near_poor_dtts": 917
  },
  {
    "district": "Huyện Đăk Glong",
    "poor_dtts": 538,
    "near_poor_dtts": 485
  },
  {
    "district": "Huyện Đắk Song",
    "poor_dtts": 279,
    "near_poor_dtts": 510
  },
  {
    "district": "Huyện Đắk Mil",
    "poor_dtts": 221,
    "near_poor_dtts": 466
  },
  {
    "district": "Huyện Cư Jút",
    "poor_dtts": 204,
    "near_poor_dtts": 304
  },
  {
    "district": "Huyện Krông Nô",
    "poor_dtts": 189,
    "near_poor_dtts": 588
  },
  {
    "district": "Huyện Đắk RLấp",
    "poor_dtts": 135,
    "near_poor_dtts": 271
  },
  {
    "district": "Thành phố Gia Nghĩa",
    "poor_dtts": 51,
    "near_poor_dtts": 142
  }
]
```

---

### Câu 42: huyện krông nô 2024 có bao nhiêu hn bị thiếu vốn sx với thiếu đất sx?

**SQL:**

```sql
SELECT SUM(CASE WHEN "reason.lackCapital" = true THEN 1 ELSE 0 END) AS lack_capital, SUM(CASE WHEN "reason.lackProductionLand" = true THEN 1 ELSE 0 END) AS lack_land FROM households WHERE "administrative.district" ILIKE '%Krông Nô%' AND "classify" = 'Hộ nghèo' AND "administrative.year" = 2024;
```

**DataFrame:**

| lack_capital | lack_land |
| :----------- | --------: |
| 80           |        60 |

**Kết quả DB:**

```json
[
  {
    "lack_capital": 80,
    "lack_land": 60
  }
]
```

---

### Câu 43: năm 2024 khu vực thành thị hay nông thôn có số hộ thoát nghèo nhiều hơn?

**SQL:**

```sql
SELECT "administrative.areaType" AS area_type, COUNT(*) AS escaped_count FROM households WHERE "transition.isEscapedPoverty" = true AND "administrative.year" = 2024 GROUP BY area_type ORDER BY escaped_count DESC;
```

**DataFrame:**

| area_type | escaped_count |
| :-------- | ------------: |
| rural     |          1063 |
| urban     |            70 |

**Kết quả DB:**

```json
[
  {
    "area_type": "rural",
    "escaped_count": 1063
  },
  {
    "area_type": "urban",
    "escaped_count": 70
  }
]
```

---

### Câu 44: top 3 xã có trẻ em ko đi học nhiều nhất 2024 là xã nào?

**SQL:**

```sql
SELECT "administrative.commune" AS commune, SUM("children.schoolAttendanceDeprivedCount") AS deprived_children FROM households WHERE "administrative.year" = 2024 AND "children.schoolAttendanceDeprivedCount" > 0 GROUP BY commune ORDER BY deprived_children DESC LIMIT 3;
```

**DataFrame:**

| commune         | deprived_children |
| :-------------- | ----------------: |
| Xã Quảng Tân |                71 |
| Xã Đắk Ngo   |                69 |
| Xã Đắk RTíh |                65 |

**Kết quả DB:**

```json
[
  {
    "commune": "Xã Quảng Tân",
    "deprived_children": 71
  },
  {
    "commune": "Xã Đắk Ngo",
    "deprived_children": 69
  },
  {
    "commune": "Xã Đắk RTíh",
    "deprived_children": 65
  }
]
```

---

### Câu 45: ở tp gia nghĩa bn hộ nghèo bị thiếu hụt chất lượng nhà ở với diện tích nhà ở năm 2024

**SQL:**

```sql
SELECT SUM(CASE WHEN "deprivation.housingQuality" = true THEN 1 ELSE 0 END) AS poor_quality_housing, SUM(CASE WHEN "deprivation.housingArea" = true THEN 1 ELSE 0 END) AS small_area_housing FROM households WHERE "administrative.district" ILIKE '%Gia Nghĩa%' AND "classify" = 'Hộ nghèo' AND "administrative.year" = 2024;
```

**DataFrame:**

| poor_quality_housing | small_area_housing |
| :------------------- | -----------------: |
| 34                   |                 12 |

**Kết quả DB:**

```json
[
  {
    "poor_quality_housing": 34,
    "small_area_housing": 12
  }
]
```

---

### Câu 46: tính tỷ lệ chủ hộ nam vs nữ trong các hcn năm 2024 toàn tỉnh

**SQL:**

```sql
SELECT "family.hostGender" AS gender, COUNT(*) AS count, ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage FROM households WHERE "classify" = 'Hộ cận nghèo' AND "administrative.year" = 2024 AND "family.hostGender" IN ('Nam', 'Nữ') GROUP BY gender;
```

**DataFrame:**

| gender | count | percentage |
| :----- | ----: | ---------: |
| Nữ    |  1089 |      29.57 |
| Nam    |  2594 |      70.43 |

**Kết quả DB:**

```json
[
  {
    "gender": "Nữ",
    "count": 1089,
    "percentage": 29.57
  },
  {
    "gender": "Nam",
    "count": 2594,
    "percentage": 70.43
  }
]
```

---

### Câu 47: so sánh sl hộ nghèo ko có khả năng lao động ở đắk mil giữa 2 năm 2023 vs 2024

**SQL:**

```sql
SELECT "administrative.year" AS year, COUNT(*) AS no_labor_capacity_count FROM households WHERE "administrative.district" ILIKE '%Đắk Mil%' AND "classify" = 'Hộ nghèo' AND "family.hasNoLaborCapacity" = true AND "administrative.year" IN (2023, 2024) GROUP BY year ORDER BY year;
```

**DataFrame:**

| year | no_labor_capacity_count |
| :--- | ----------------------: |
| 2023 |                     137 |
| 2024 |                      67 |

**Kết quả DB:**

```json
[
  {
    "year": 2023,
    "no_labor_capacity_count": 137
  },
  {
    "year": 2024,
    "no_labor_capacity_count": 67
  }
]
```

---

### Câu 48: đăk glong 2024 có bn hộ nghèo cần hỗ trợ về y tế và giáo dục?

**SQL:**

```sql
SELECT SUM(CASE WHEN "support.health" = true THEN 1 ELSE 0 END) AS need_health_support, SUM(CASE WHEN "support.education" = true THEN 1 ELSE 0 END) AS need_edu_support FROM households WHERE "administrative.district" ILIKE '%Đăk Glong%' AND "classify" = 'Hộ nghèo' AND "administrative.year" = 2024;
```

**DataFrame:**

| need_health_support | need_edu_support |
| :------------------ | ---------------: |
| 538                 |              470 |

**Kết quả DB:**

```json
[
  {
    "need_health_support": 538,
    "need_edu_support": 470
  }
]
```

---

### Câu 49: huyện nào có nhiều hộ nghèo bị ốm đau tai nạn nhất năm 2024?

**SQL:**

```sql
SELECT "administrative.district" AS district, COUNT(*) AS illness_count FROM households WHERE "classify" = 'Hộ nghèo' AND "reason.illnessOrAccident" = true AND "administrative.year" = 2024 GROUP BY district ORDER BY illness_count DESC;
```

**DataFrame:**

| district               | illness_count |
| :--------------------- | ------------: |
| Huyện Tuy Đức       |           386 |
| Huyện Đăk Glong     |           265 |
| Huyện Đắk Song      |           127 |
| Huyện Đắk Mil       |            97 |
| Huyện Cư Jút        |            94 |
| Huyện Krông Nô      |            83 |
| Huyện Đắk RLấp     |            69 |
| Thành phố Gia Nghĩa |            26 |

**Kết quả DB:**

```json
[
  {
    "district": "Huyện Tuy Đức",
    "illness_count": 386
  },
  {
    "district": "Huyện Đăk Glong",
    "illness_count": 265
  },
  {
    "district": "Huyện Đắk Song",
    "illness_count": 127
  },
  {
    "district": "Huyện Đắk Mil",
    "illness_count": 97
  },
  {
    "district": "Huyện Cư Jút",
    "illness_count": 94
  },
  {
    "district": "Huyện Krông Nô",
    "illness_count": 83
  },
  {
    "district": "Huyện Đắk RLấp",
    "illness_count": 69
  },
  {
    "district": "Thành phố Gia Nghĩa",
    "illness_count": 26
  }
]
```

---

### Câu 50: check xem cư jút 2024 có bn hộ nghèo thiếu nước sạch vs nhà vệ sinh

**SQL:**

```sql
SELECT SUM(CASE WHEN "deprivation.cleanWater" = true THEN 1 ELSE 0 END) AS lack_clean_water, SUM(CASE WHEN "deprivation.hygienicToilet" = true THEN 1 ELSE 0 END) AS lack_toilet FROM households WHERE "administrative.district" ILIKE '%Cư Jút%' AND "classify" = 'Hộ nghèo' AND "administrative.year" = 2024;
```

**DataFrame:**

| lack_clean_water | lack_toilet |
| :--------------- | ----------: |
| 0                |           1 |

**Kết quả DB:**

```json
[
  {
    "lack_clean_water": 0,
    "lack_toilet": 1
  }
]
```

---

