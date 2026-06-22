# Câu hỏi và Truy vấn SQL tương ứng

Tài liệu cung cấp các câu hỏi, các lệnh SQL tương ứng, và đáp án từ SQL (context) để LLM trả lời.

## 1. Năm 2024, thống kê số hộ nghèo theo huyện.
### Lệnh SQL
```sql
SELECT "administrative.district" AS district, SUM(CASE WHEN "classify" = 'Hộ nghèo' THEN 1 ELSE 0 END) AS poor_household_count FROM households WHERE "classify" = 'Hộ nghèo' AND "administrative.year" = 2024 GROUP BY district ORDER BY poor_household_count DESC
```

### Đáp án (Context từ SQL)
> Dưới đây là thống kê số hộ nghèo theo huyện năm 2024:

| Huyện                   | Số hộ nghèo |
|:------------------------|-------------:|
| Huyện Tuy Đức           |          829 |
| Huyện Đăk Glong         |          538 |
| Huyện Đắk Song          |          279 |
| Huyện Đắk Mil           |          221 |
| Huyện Cư Jút            |          204 |
| Huyện Krông Nô          |          189 |
| Huyện Đắk RLấp          |          135 |
| Thành phố Gia Nghĩa     |           51 |

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

| Huyện                  | Số hộ nghèo | Số hộ cận nghèo |
|:-----------------------|-------------:|-----------------:|
| Huyện Tuy Đức          |          829 |              917 |
| Huyện Đăk Glong        |          538 |              485 |
| Huyện Đắk Song         |          279 |              510 |
| Huyện Đắk Mil          |          221 |              466 |
| Huyện Cư Jút           |          204 |              304 |
| Huyện Krông Nô         |          189 |              588 |
| Huyện Đắk RLấp         |          135 |              271 |
| Thành phố Gia Nghĩa    |           51 |              142 |

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
