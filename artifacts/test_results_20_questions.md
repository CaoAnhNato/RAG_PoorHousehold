# Kết Quả Test 20 Câu Hỏi Bằng Agentic Pipeline

## 1. Năm 2024, thống kê số hộ nghèo theo huyện.
### SQL
```sql
SELECT "administrative.district", COUNT(*) AS "numberOfPoorHouseholds" FROM households WHERE classify = 'Hộ nghèo' AND "administrative.year" = 2024 GROUP BY "administrative.district";
```

### Answer (Hiển thị UI)
| administrative.district   |   numberOfPoorHouseholds |
|:--------------------------|-------------------------:|
| Huyện Đắk RLấp            |                      135 |
| Huyện Krông Nô            |                      189 |
| Huyện Cư Jút              |                      204 |
| Huyện Đăk Glong           |                      538 |
| Huyện Tuy Đức             |                      829 |
| Huyện Đắk Song            |                      279 |
| Huyện Đắk Mil             |                      221 |
| Thành phố Gia Nghĩa       |                       51 |

### Data
| administrative.district   |   numberOfPoorHouseholds |
|:--------------------------|-------------------------:|
| Huyện Đắk RLấp            |                      135 |
| Huyện Krông Nô            |                      189 |
| Huyện Cư Jút              |                      204 |
| Huyện Đăk Glong           |                      538 |
| Huyện Tuy Đức             |                      829 |
| Huyện Đắk Song            |                      279 |
| Huyện Đắk Mil             |                      221 |
| Thành phố Gia Nghĩa       |                       51 |

**Thời gian:** 1.97 giây

---

## 2. Huyện nào có nhiều hộ nghèo nhất trong năm 2024?
### SQL
```sql
SELECT "administrative.district", COUNT(*) AS "number_of_poor_households" FROM households WHERE classify = 'Hộ nghèo' AND "administrative.year" = 2024 GROUP BY "administrative.district" ORDER BY "number_of_poor_households" DESC LIMIT 1;
```

### Answer (Hiển thị UI)
Huyện Tuy Đức là huyện có nhiều hộ nghèo nhất trong năm 2024, với 829 hộ nghèo.

### Data
| administrative.district   |   number_of_poor_households |
|:--------------------------|----------------------------:|
| Huyện Tuy Đức             |                         829 |

**Thời gian:** 3.75 giây

---

## 3. Cho tôi biết tình hình nghèo ở Đắk Nông như thế nào?
### SQL
```sql
SELECT "classify", COUNT(*) FROM households WHERE "administrative.year" IN (2023, 2024) GROUP BY "classify";
```

### Answer (Hiển thị UI)
Tình hình nghèo ở Đắk Nông như sau:

- Hộ nghèo: 8,125 hộ
- Hộ cận nghèo: 11,445 hộ
- Hộ không nghèo: 1,348 hộ

Có thể thấy, số lượng hộ nghèo và hộ cận nghèo chiếm tỷ lệ lớn, cho thấy tình trạng nghèo đói vẫn còn khá phổ biến trong khu vực này.

### Data
| classify       |   count_star() |
|:---------------|---------------:|
| Hộ không nghèo |           1348 |
| Hộ nghèo       |           8125 |
| Hộ cận nghèo   |          11445 |

**Thời gian:** 3.71 giây

---

## 4. Tôi muốn xem nhanh số hộ nghèo và hộ cận nghèo theo từng huyện trong năm 2024.
### SQL
```sql
SELECT "administrative.district", classify, COUNT(*) AS total_households FROM households WHERE "administrative.year" = 2024 GROUP BY "administrative.district", classify;
```

### Answer (Hiển thị UI)
| administrative.district   | classify       |   total_households |
|:--------------------------|:---------------|-------------------:|
| Huyện Tuy Đức             | Hộ cận nghèo   |                917 |
| Huyện Tuy Đức             | Hộ nghèo       |                829 |
| Huyện Đắk RLấp            | Hộ cận nghèo   |                271 |
| Huyện Đắk RLấp            | Hộ nghèo       |                135 |
| Huyện Cư Jút              | Hộ nghèo       |                204 |
| Huyện Cư Jút              | Hộ cận nghèo   |                304 |
| Huyện Krông Nô            | Hộ không nghèo |                243 |
| Huyện Đắk Song            | Hộ cận nghèo   |                510 |
| Huyện Đắk Song            | Hộ nghèo       |                279 |
| Huyện Tuy Đức             | Hộ không nghèo |                171 |
| Huyện Đăk Glong           | Hộ không nghèo |                523 |
| Huyện Đắk Mil             | Hộ cận nghèo   |                466 |
| Huyện Đắk Mil             | Hộ nghèo       |                221 |
| Huyện Đắk RLấp            | Hộ không nghèo |                 83 |
| Thành phố Gia Nghĩa       | Hộ cận nghèo   |                142 |
| Thành phố Gia Nghĩa       | Hộ nghèo       |                 51 |
| Huyện Đăk Glong           | Hộ nghèo       |                538 |
| Huyện Đăk Glong           | Hộ cận nghèo   |                485 |
| Huyện Đắk Mil             | Hộ không nghèo |                 74 |
| Huyện Cư Jút              | Hộ không nghèo |                 90 |
| Huyện Krông Nô            | Hộ cận nghèo   |                588 |
| Huyện Krông Nô            | Hộ nghèo       |                189 |
| Thành phố Gia Nghĩa       | Hộ không nghèo |                 18 |
| Huyện Đắk Song            | Hộ không nghèo |                141 |

### Data
| administrative.district   | classify       |   total_households |
|:--------------------------|:---------------|-------------------:|
| Huyện Tuy Đức             | Hộ cận nghèo   |                917 |
| Huyện Tuy Đức             | Hộ nghèo       |                829 |
| Huyện Đắk RLấp            | Hộ cận nghèo   |                271 |
| Huyện Đắk RLấp            | Hộ nghèo       |                135 |
| Huyện Cư Jút              | Hộ nghèo       |                204 |
| Huyện Cư Jút              | Hộ cận nghèo   |                304 |
| Huyện Krông Nô            | Hộ không nghèo |                243 |
| Huyện Đắk Song            | Hộ cận nghèo   |                510 |
| Huyện Đắk Song            | Hộ nghèo       |                279 |
| Huyện Tuy Đức             | Hộ không nghèo |                171 |

*(Còn 14 dòng nữa)*

**Thời gian:** 1.59 giây

---

## 5. Năm 2024, tình hình hộ nghèo ở Thành phố Gia Nghĩa có cải thiện hơn so với năm 2023 không?
### SQL
```sql
SELECT "administrative.year", COUNT(*) AS total_poverty FROM households WHERE classify = 'Hộ nghèo' AND "administrative.district" ILIKE '%Thành phố Gia Nghĩa%' AND "administrative.year" IN (2023, 2024) GROUP BY "administrative.year";
```

### Answer (Hiển thị UI)
Có, tình hình hộ nghèo ở Thành phố Gia Nghĩa đã cải thiện hơn so với năm 2023. Số hộ nghèo giảm từ 88 hộ trong năm 2023 xuống còn 51 hộ trong năm 2024.

### Data
|   administrative.year |   total_poverty |
|----------------------:|----------------:|
|                  2023 |              88 |
|                  2024 |              51 |

**Thời gian:** 4.31 giây

---

## 6. So với năm 2023, số hộ nghèo ở Đắk Song năm 2024 thay đổi ra sao?
### SQL
```sql
SELECT "administrative.year", COUNT(*) AS "so_ho_ngheo" 
FROM households 
WHERE classify = 'Hộ nghèo' AND "administrative.district" ILIKE '%Đắk Song%' AND "administrative.year" IN (2023, 2024) 
GROUP BY "administrative.year";
```

### Answer (Hiển thị UI)
So với năm 2023, số hộ nghèo ở Đắk Song năm 2024 đã giảm đáng kể, từ 458 hộ xuống còn 279 hộ.

### Data
|   administrative.year |   so_ho_ngheo |
|----------------------:|--------------:|
|                  2023 |           458 |
|                  2024 |           279 |

**Thời gian:** 3.68 giây

---

## 7. Năm 2024, hộ cận nghèo đang tập trung nhiều ở huyện nào?
### SQL
```sql
SELECT "administrative.district", COUNT(*) AS "count" 
FROM households 
WHERE classify = 'Hộ cận nghèo' AND "administrative.year" = 2024 
GROUP BY "administrative.district" 
ORDER BY "count" DESC 
LIMIT 1;
```

### Answer (Hiển thị UI)
Năm 2024, hộ cận nghèo đang tập trung nhiều ở huyện Tuy Đức với 917 hộ.

### Data
| administrative.district   |   count |
|:--------------------------|--------:|
| Huyện Tuy Đức             |     917 |

**Thời gian:** 3.22 giây

---

## 8. Ở Huyện Cư Jút, hộ nghèo nào thiếu nhà tiêu hợp vệ sinh nhiều nhất?
### SQL
```sql
SELECT "family.hostName", COUNT(*) AS "numberOfPoorHouseholdsWithoutToilet"
FROM households
WHERE classify = 'Hộ nghèo' AND "deprivation.hygienicToilet" = true AND "administrative.district" ILIKE '%Cư Jút%'
GROUP BY "family.hostName"
ORDER BY "numberOfPoorHouseholdsWithoutToilet" DESC
LIMIT 1;
```

### Answer (Hiển thị UI)
Ở Huyện Cư Jút, hộ nghèo thiếu nhà tiêu hợp vệ sinh nhiều nhất là hộ của bà Nguyễn Thị Hường, với 2 hộ.

### Data
| family.hostName   |   numberOfPoorHouseholdsWithoutToilet |
|:------------------|--------------------------------------:|
| NGUYỄN THỊ HƯỜNG  |                                     2 |

**Thời gian:** 3.48 giây

---

## 9. So với 2023, số hộ thoát nghèo trong 2024 tăng hay giảm ở Tuy Đức?
### SQL
```sql
SELECT COUNT(*) AS "số_hộ_thoát_nghèo", "administrative.year" FROM households WHERE classify = 'Hộ không nghèo' AND "administrative.district" ILIKE '%Tuy Đức%' AND "administrative.year" IN (2023, 2024) GROUP BY "administrative.year";
```

### Answer (Hiển thị UI)
So với năm 2023, số hộ thoát nghèo ở Tuy Đức trong năm 2024 đã tăng lên, từ 1 hộ lên 171 hộ.

### Data
|   số_hộ_thoát_nghèo |   administrative.year |
|--------------------:|----------------------:|
|                   1 |                  2023 |
|                 171 |                  2024 |

**Thời gian:** 3.30 giây

---

## 10. Chủ hộ nào có số thành viên nhiều nhất ở Huyện Đắk Song?
### SQL
```sql
SELECT "family.hostName", MAX("family.numberOfMembers") AS max_members FROM households WHERE "administrative.district" ILIKE '%Đắk Song%' GROUP BY "family.hostName" ORDER BY max_members DESC LIMIT 1;
```

### Answer (Hiển thị UI)
Chủ hộ có số thành viên nhiều nhất ở Huyện Đắk Song là Trần Văn Hải với 11 thành viên.

### Data
| family.hostName   |   max_members |
|:------------------|--------------:|
| Trần Văn Hải      |            11 |

**Thời gian:** 3.44 giây

---

## 11. Mức độ thiếu hụt của các hộ nghèo ở Đắk Mil tập trung mạnh vào những chỉ số nào?
### SQL
```sql
SELECT "deprivation.cleanWater", "deprivation.hygienicToilet", "deprivation.totalCount"
FROM households
WHERE classify = 'Hộ nghèo' AND "administrative.district" ILIKE '%Đắk Mil%'
```

### Answer (Hiển thị UI)
| deprivation.cleanWater   | deprivation.hygienicToilet   |   deprivation.totalCount |
|:-------------------------|:-----------------------------|-------------------------:|
| False                    | False                        |                        4 |
| False                    | False                        |                        5 |
| False                    | True                         |                        7 |
| False                    | True                         |                        7 |
| False                    | False                        |                        3 |
| False                    | True                         |                        7 |
| True                     | True                         |                        8 |
| False                    | False                        |                        4 |
| False                    | False                        |                        5 |
| False                    | True                         |                        7 |
| False                    | False                        |                        5 |
| False                    | False                        |                        5 |
| True                     | True                         |                        8 |
| False                    | False                        |                        4 |
| False                    | True                         |                        7 |
| False                    | False                        |                        6 |
| False                    | False                        |                        6 |
| False                    | False                        |                        4 |
| False                    | False                        |                        6 |
| False                    | False                        |                        3 |
| False                    | False                        |                        5 |
| False                    | True                         |                        8 |
| False                    | False                        |                        4 |
| False                    | True                         |                        8 |
| False                    | False                        |                        6 |
| False                    | False                        |                        5 |
| False                    | True                         |                        7 |
| False                    | False                        |                        6 |
| False                    | True                         |                        7 |
| False                    | False                        |                        6 |
| False                    | False                        |                        6 |
| False                    | False                        |                        6 |
| True                     | True                         |                        8 |
| False                    | False                        |                        3 |
| False                    | False                        |                        5 |
| False                    | False                        |                        4 |
| False                    | False                        |                        5 |
| False                    | False                        |                        3 |
| False                    | True                         |                        8 |
| False                    | False                        |                        5 |
| False                    | False                        |                        5 |
| False                    | True                         |                        7 |
| False                    | False                        |                        6 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        6 |
| False                    | False                        |                        6 |
| False                    | False                        |                        6 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | False                        |                        6 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | True                         |                        8 |
| False                    | False                        |                        6 |
| False                    | True                         |                        7 |
| False                    | True                         |                        7 |
| False                    | False                        |                        5 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | True                         |                        8 |
| False                    | False                        |                        5 |
| False                    | False                        |                        5 |
| False                    | True                         |                        8 |
| False                    | True                         |                        8 |
| False                    | True                         |                        8 |
| False                    | False                        |                        6 |
| False                    | False                        |                        6 |
| False                    | False                        |                        4 |
| False                    | False                        |                        5 |
| False                    | False                        |                        4 |
| False                    | False                        |                        5 |
| False                    | False                        |                        6 |
| False                    | True                         |                        7 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | True                         |                        7 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        5 |
| False                    | False                        |                        3 |
| False                    | False                        |                        6 |
| False                    | False                        |                        6 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        5 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        5 |
| False                    | False                        |                        3 |
| False                    | True                         |                        7 |
| False                    | True                         |                        7 |
| False                    | True                         |                        8 |
| False                    | True                         |                        8 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | True                         |                        8 |
| False                    | False                        |                        5 |
| True                     | True                         |                        8 |
| True                     | True                         |                        8 |
| False                    | False                        |                        4 |
| False                    | False                        |                        6 |
| False                    | True                         |                        7 |
| False                    | False                        |                        5 |
| True                     | True                         |                        8 |
| False                    | False                        |                        5 |
| False                    | False                        |                        3 |
| False                    | False                        |                        6 |
| False                    | True                         |                        7 |
| False                    | False                        |                        5 |
| False                    | False                        |                        6 |
| True                     | True                         |                        8 |
| True                     | True                         |                        8 |
| False                    | True                         |                        7 |
| False                    | True                         |                        8 |
| False                    | False                        |                        4 |
| True                     | True                         |                        8 |
| True                     | True                         |                        8 |
| True                     | True                         |                        8 |
| False                    | False                        |                        5 |
| False                    | True                         |                        7 |
| False                    | False                        |                        4 |
| False                    | True                         |                        8 |
| False                    | False                        |                        4 |
| False                    | False                        |                        5 |
| False                    | False                        |                        5 |
| False                    | True                         |                        7 |
| False                    | False                        |                        5 |
| False                    | True                         |                        7 |
| True                     | True                         |                        8 |
| False                    | False                        |                        5 |
| False                    | False                        |                        4 |
| False                    | True                         |                        7 |
| False                    | False                        |                        5 |
| False                    | True                         |                        7 |
| False                    | True                         |                        7 |
| False                    | False                        |                        3 |
| False                    | True                         |                        7 |
| False                    | False                        |                        6 |
| False                    | False                        |                        3 |
| False                    | False                        |                        6 |
| False                    | False                        |                        5 |
| False                    | False                        |                        5 |
| True                     | True                         |                        8 |
| False                    | False                        |                        6 |
| False                    | False                        |                        6 |
| False                    | False                        |                        5 |
| False                    | False                        |                        5 |
| False                    | True                         |                        7 |
| False                    | False                        |                        6 |
| False                    | True                         |                        7 |
| False                    | True                         |                        8 |
| False                    | False                        |                        5 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        6 |
| False                    | False                        |                        5 |
| False                    | False                        |                        3 |
| False                    | False                        |                        6 |
| False                    | False                        |                        5 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | False                        |                        5 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | True                         |                        7 |
| False                    | False                        |                        6 |
| False                    | False                        |                        6 |
| False                    | True                         |                        8 |
| False                    | False                        |                        6 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | False                        |                        5 |
| False                    | False                        |                        5 |
| False                    | True                         |                        7 |
| False                    | True                         |                        7 |
| False                    | True                         |                        7 |
| False                    | True                         |                        7 |
| False                    | False                        |                        5 |
| False                    | False                        |                        6 |
| False                    | False                        |                        6 |
| False                    | False                        |                        5 |
| False                    | False                        |                        6 |
| False                    | False                        |                        3 |
| False                    | True                         |                        7 |
| False                    | False                        |                        5 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        6 |
| False                    | True                         |                        8 |
| False                    | False                        |                        5 |
| False                    | False                        |                        4 |
| False                    | False                        |                        6 |
| False                    | True                         |                        7 |
| False                    | False                        |                        3 |
| True                     | True                         |                        8 |
| False                    | False                        |                        5 |
| False                    | True                         |                        7 |
| False                    | True                         |                        8 |
| False                    | False                        |                        4 |
| False                    | False                        |                        6 |
| True                     | True                         |                        8 |
| False                    | True                         |                        8 |
| True                     | True                         |                        8 |
| False                    | False                        |                        6 |
| False                    | True                         |                        7 |
| False                    | False                        |                        6 |
| False                    | False                        |                        5 |
| False                    | True                         |                        7 |
| False                    | False                        |                        4 |
| True                     | True                         |                        8 |
| False                    | True                         |                        7 |
| False                    | False                        |                        6 |
| False                    | False                        |                        5 |
| False                    | True                         |                        7 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | True                         |                        7 |
| False                    | True                         |                        7 |
| False                    | False                        |                        6 |
| False                    | False                        |                        3 |
| False                    | True                         |                        8 |
| False                    | False                        |                        3 |
| False                    | False                        |                        5 |
| False                    | False                        |                        5 |
| False                    | False                        |                        6 |
| True                     | True                         |                        8 |
| False                    | False                        |                        5 |
| True                     | True                         |                        8 |
| False                    | True                         |                        7 |
| False                    | False                        |                        6 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        5 |
| False                    | False                        |                        5 |
| False                    | True                         |                        8 |
| False                    | False                        |                        5 |
| False                    | False                        |                        4 |
| False                    | True                         |                        7 |
| False                    | False                        |                        3 |
| False                    | True                         |                        7 |
| False                    | True                         |                        7 |
| False                    | False                        |                        6 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        6 |
| True                     | True                         |                        8 |
| False                    | True                         |                        7 |
| False                    | False                        |                        3 |
| False                    | False                        |                        5 |
| False                    | False                        |                        3 |
| False                    | False                        |                        6 |
| False                    | True                         |                        7 |
| False                    | False                        |                        4 |
| False                    | False                        |                        5 |
| False                    | False                        |                        5 |
| False                    | False                        |                        4 |
| False                    | True                         |                        7 |
| False                    | False                        |                        6 |
| False                    | True                         |                        7 |
| False                    | False                        |                        4 |
| False                    | False                        |                        6 |
| True                     | True                         |                        8 |
| False                    | True                         |                        7 |
| False                    | False                        |                        5 |
| False                    | False                        |                        5 |
| False                    | False                        |                        5 |
| False                    | True                         |                        7 |
| False                    | False                        |                        6 |
| False                    | True                         |                        8 |
| False                    | True                         |                        8 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | False                        |                        6 |
| False                    | False                        |                        5 |
| False                    | False                        |                        6 |
| True                     | True                         |                        8 |
| False                    | False                        |                        5 |
| False                    | False                        |                        5 |
| False                    | False                        |                        5 |
| False                    | True                         |                        8 |
| False                    | False                        |                        6 |
| False                    | False                        |                        5 |
| False                    | True                         |                        7 |
| False                    | True                         |                        7 |
| True                     | True                         |                        8 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | True                         |                        7 |
| False                    | False                        |                        3 |
| True                     | True                         |                        8 |
| True                     | True                         |                        8 |
| False                    | False                        |                        5 |
| False                    | False                        |                        6 |
| False                    | False                        |                        4 |
| False                    | True                         |                        7 |
| False                    | False                        |                        4 |
| False                    | True                         |                        8 |
| False                    | False                        |                        5 |
| False                    | False                        |                        5 |
| False                    | True                         |                        7 |
| True                     | True                         |                        8 |
| False                    | False                        |                        5 |
| False                    | False                        |                        4 |
| False                    | True                         |                        7 |
| False                    | True                         |                        7 |
| False                    | False                        |                        6 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | False                        |                        6 |
| False                    | True                         |                        7 |
| False                    | False                        |                        5 |
| False                    | False                        |                        5 |
| False                    | True                         |                        7 |
| False                    | False                        |                        3 |
| True                     | True                         |                        8 |
| False                    | False                        |                        5 |
| False                    | False                        |                        5 |
| False                    | True                         |                        7 |
| True                     | True                         |                        8 |
| False                    | True                         |                        7 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        6 |
| False                    | False                        |                        5 |
| False                    | False                        |                        4 |
| False                    | False                        |                        6 |
| False                    | False                        |                        6 |
| False                    | False                        |                        6 |
| False                    | True                         |                        7 |
| False                    | False                        |                        5 |
| False                    | True                         |                        7 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| True                     | True                         |                        8 |
| False                    | True                         |                        7 |
| False                    | True                         |                        7 |
| False                    | False                        |                        3 |
| False                    | False                        |                        6 |
| False                    | True                         |                        7 |
| False                    | False                        |                        3 |
| True                     | True                         |                        8 |
| False                    | False                        |                        6 |
| False                    | False                        |                        4 |
| False                    | False                        |                        6 |
| True                     | True                         |                        8 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | False                        |                        5 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | False                        |                        5 |
| False                    | False                        |                        6 |
| False                    | True                         |                        8 |
| False                    | False                        |                        6 |
| False                    | True                         |                        7 |
| False                    | False                        |                        5 |
| False                    | False                        |                        4 |
| True                     | True                         |                        8 |
| False                    | False                        |                        6 |
| False                    | False                        |                        6 |
| False                    | False                        |                        4 |
| False                    | False                        |                        6 |
| False                    | False                        |                        5 |
| False                    | False                        |                        5 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        5 |
| False                    | True                         |                        7 |
| False                    | False                        |                        6 |
| False                    | False                        |                        6 |
| False                    | False                        |                        4 |
| False                    | False                        |                        6 |
| True                     | True                         |                        8 |
| False                    | False                        |                        4 |
| False                    | True                         |                        7 |
| False                    | False                        |                        4 |
| False                    | False                        |                        6 |
| False                    | False                        |                        3 |
| False                    | True                         |                        7 |
| False                    | True                         |                        8 |
| False                    | True                         |                        7 |
| False                    | False                        |                        4 |
| False                    | False                        |                        6 |
| False                    | False                        |                        3 |
| False                    | False                        |                        6 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        6 |
| False                    | False                        |                        5 |
| False                    | False                        |                        4 |
| False                    | True                         |                        8 |
| False                    | True                         |                        7 |
| False                    | False                        |                        6 |
| False                    | True                         |                        8 |
| False                    | False                        |                        6 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | True                         |                        7 |
| False                    | False                        |                        3 |
| False                    | True                         |                        7 |
| False                    | False                        |                        5 |
| False                    | True                         |                        7 |
| False                    | False                        |                        3 |
| False                    | False                        |                        5 |
| False                    | False                        |                        3 |
| False                    | False                        |                        6 |
| False                    | True                         |                        7 |
| False                    | False                        |                        4 |
| False                    | True                         |                        8 |
| False                    | False                        |                        4 |
| False                    | True                         |                        7 |
| False                    | False                        |                        5 |
| True                     | True                         |                        8 |
| True                     | True                         |                        8 |
| False                    | False                        |                        3 |
| False                    | False                        |                        6 |
| False                    | False                        |                        5 |
| False                    | True                         |                        7 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| True                     | True                         |                        8 |
| False                    | False                        |                        3 |
| False                    | True                         |                        7 |
| False                    | False                        |                        6 |
| False                    | False                        |                        5 |
| False                    | False                        |                        5 |
| False                    | False                        |                        6 |
| False                    | False                        |                        4 |
| False                    | False                        |                        6 |
| False                    | False                        |                        3 |
| True                     | True                         |                        8 |
| False                    | False                        |                        6 |
| False                    | False                        |                        5 |
| False                    | True                         |                        7 |
| False                    | False                        |                        3 |
| False                    | False                        |                        6 |
| False                    | False                        |                        4 |
| False                    | True                         |                        8 |
| False                    | False                        |                        4 |
| False                    | False                        |                        6 |
| False                    | False                        |                        5 |
| False                    | True                         |                        7 |
| False                    | True                         |                        8 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        5 |
| False                    | False                        |                        6 |
| False                    | False                        |                        6 |
| False                    | False                        |                        5 |
| False                    | False                        |                        5 |
| False                    | False                        |                        6 |
| False                    | False                        |                        4 |
| False                    | False                        |                        5 |
| False                    | False                        |                        5 |
| False                    | False                        |                        4 |
| False                    | False                        |                        5 |
| False                    | False                        |                        4 |
| False                    | False                        |                        5 |
| False                    | False                        |                        3 |
| False                    | False                        |                        5 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        5 |
| False                    | False                        |                        4 |
| False                    | False                        |                        5 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        5 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        5 |
| False                    | False                        |                        5 |
| False                    | False                        |                        5 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        6 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        5 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        5 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        6 |
| False                    | True                         |                        7 |
| False                    | False                        |                        6 |
| False                    | False                        |                        6 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        5 |
| False                    | False                        |                        6 |
| False                    | False                        |                        4 |
| False                    | False                        |                        6 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | False                        |                        5 |
| False                    | True                         |                        7 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | True                         |                        7 |
| False                    | False                        |                        5 |
| False                    | False                        |                        4 |
| False                    | False                        |                        5 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | False                        |                        5 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        6 |
| False                    | False                        |                        6 |
| False                    | False                        |                        5 |
| False                    | False                        |                        5 |
| False                    | False                        |                        3 |
| False                    | True                         |                        7 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        6 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        5 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | False                        |                        5 |
| False                    | True                         |                        7 |
| False                    | False                        |                        4 |
| False                    | False                        |                        5 |
| False                    | False                        |                        6 |
| False                    | False                        |                        4 |
| False                    | True                         |                        7 |
| False                    | False                        |                        5 |
| False                    | False                        |                        5 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        5 |
| False                    | False                        |                        6 |
| False                    | False                        |                        3 |
| False                    | False                        |                        5 |
| False                    | False                        |                        5 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        5 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | False                        |                        4 |
| False                    | False                        |                        5 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        5 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        5 |
| False                    | False                        |                        4 |
| False                    | False                        |                        5 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        5 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        4 |
| False                    | False                        |                        3 |
| False                    | False                        |                        5 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |
| False                    | False                        |                        3 |

### Data
| deprivation.cleanWater   | deprivation.hygienicToilet   |   deprivation.totalCount |
|:-------------------------|:-----------------------------|-------------------------:|
| False                    | False                        |                        4 |
| False                    | False                        |                        5 |
| False                    | True                         |                        7 |
| False                    | True                         |                        7 |
| False                    | False                        |                        3 |
| False                    | True                         |                        7 |
| True                     | True                         |                        8 |
| False                    | False                        |                        4 |
| False                    | False                        |                        5 |
| False                    | True                         |                        7 |

*(Còn 681 dòng nữa)*

**Thời gian:** 1.77 giây

---

## 12. Khu vực nào có nhiều hộ cận nghèo nhất nhưng lại ít thiếu hụt nhất?
### SQL
```sql
SELECT "administrative.district", COUNT(*) AS "number_of_near_poverty", SUM("deprivation.totalCount") AS "total_deprivation"
FROM households
WHERE classify = 'Hộ cận nghèo' AND "administrative.year" IN (2023, 2024)
GROUP BY "administrative.district"
ORDER BY "number_of_near_poverty" DESC, "total_deprivation" ASC
LIMIT 1;
```

### Answer (Hiển thị UI)
Khu vực có nhiều hộ cận nghèo nhất nhưng lại ít thiếu hụt nhất là Huyện Tuy Đức, với 2,582 hộ cận nghèo và tổng thiếu hụt là 3,175.0.

### Data
| administrative.district   |   number_of_near_poverty |   total_deprivation |
|:--------------------------|-------------------------:|--------------------:|
| Huyện Tuy Đức             |                     2582 |                3175 |

**Thời gian:** 4.43 giây

---

## 13. Danh sách hộ nghèo theo các xã của Cư Jút 2024
### SQL
```sql
SELECT "family.hostName", "administrative.commune" FROM households WHERE classify = 'Hộ nghèo' AND "administrative.district" ILIKE '%Cư Jút%' AND "administrative.year" = 2024;
```

### Answer (Hiển thị UI)
| family.hostName        | administrative.commune   |
|:-----------------------|:-------------------------|
| NGUYỄN VĂN HÂN         | Xã Ea Pô                 |
| NGUYỄN VĂN DŨNG        | Xã Đắk Wil               |
| TRẦN VĂN TOÀN          | Xã Trúc Sơn              |
| LÊ THỊ MƠ              | Xã Ea Pô                 |
| NGUYỄN THỊ LÝ          | Xã Tâm Thắng             |
| NGUYỄN THỊ QUỲ         | Xã Nam Dong              |
| NGUYỄN THANH THỦY      | Xã Đắk DRông             |
| H MIĂT KNUL            | Xã Trúc Sơn              |
| PHẠM VĂN TUẤN          | Thị trấn Ea TLing        |
| NGUYỄN THỊ HÒA         | Xã Đắk DRông             |
| HOÀNG THỊ TRÀN         | Xã Tâm Thắng             |
| H WANH BKRÔNG          | Thị trấn Ea TLing        |
| Y DUYÊN BYĂ            | Xã Đắk DRông             |
| NGUYỄN THỊ CHÉN        | Xã Trúc Sơn              |
| LÊ THỊ TRINH           | Xã Nam Dong              |
| NÔNG THẾ HỮU           | Xã Ea Pô                 |
| LƯƠNG ĐỨC TUÂN         | Xã Cư Knia               |
| LIÊU THỊ HẰNG          | Xã Đắk DRông             |
| Y SEP ÊBAN             | Xã Đắk Wil               |
| NGUYỄN THỊ NGỌC HƯƠNG  | Xã Tâm Thắng             |
| HOÀNG THỊ THÚY         | Xã Ea Pô                 |
| Y MÚT HRA              | Xã Nam Dong              |
| H DUAR ÊBAN            | Xã Trúc Sơn              |
| BÙI THỊ MẰN            | Xã Đắk Wil               |
| HOÀNG VĂN SẠCH         | Thị trấn Ea TLing        |
| H MÔC NIÊ              | Xã Ea Pô                 |
| Y LIA KPƠR             | Xã Đắk Wil               |
| HOÀNG MINH TUẤN        | Xã Ea Pô                 |
| PHẠM VĂN HÒA           | Xã Trúc Sơn              |
| LỮ THỊ THỂ             | Thị trấn Ea TLing        |
| HẦU VĂN TU             | Xã Ea Pô                 |
| VÕ DUY TÙNG            | Xã Đắk Wil               |
| NGÔ BÁ BAN             | Thị trấn Ea TLing        |
| Đàm Ngọc Nhương        | Xã Nam Dong              |
| NÔNG THỊ PHẨY          | Xã Tâm Thắng             |
| DƯƠNG VĂN BÀN          | Xã Trúc Sơn              |
| HOÀNG VĂN CÔNG         | Xã Đắk Wil               |
| HOÀNG VĂN QUÂN         | Xã Cư Knia               |
| NGUYỄN VĂN TIẾN        | Xã Ea Pô                 |
| VI THỊ THỦY            | Xã Ea Pô                 |
| LANG VĂN KÉO           | Xã Cư Knia               |
| DƯƠNG VĂN VÀ           | Xã Ea Pô                 |
| HOÀNG THỊ AN           | Xã Đắk DRông             |
| CHU THỊ TỐT            | Xã Nam Dong              |
| HOÀNG VĂN CAI          | Xã Đắk Wil               |
| Hoàng Thị Xuân         | Xã Trúc Sơn              |
| VƯƠNG THỊ NGUYỆT       | Xã Nam Dong              |
| NÔNG HUYỀN DIỆU        | Xã Tâm Thắng             |
| Nguyễn Thị Điều        | Xã Đắk Wil               |
| NÔNG VĂN DƯ            | Xã Nam Dong              |
| VI THỊ GIANG           | Xã Đắk Wil               |
| Lương Thị Nga          | Xã Cư Knia               |
| YKAM BKRÔNG            | Xã Đắk DRông             |
| PHAN VĂN LONG          | Thị trấn Ea TLing        |
| Đoàn Thị Thu Huyền     | Xã Đắk Wil               |
| ĐINH THỊ HOI           | Xã Trúc Sơn              |
| HỨA THỊ COI            | Xã Ea Pô                 |
| ỬNG THỊ HÀ             | Xã Nam Dong              |
| NGUYỄN VĂN THÚY        | Xã Ea Pô                 |
| HOÀNG VĂN PHÙNG        | Xã Đắk Wil               |
| NGUYỄN THỊ MINH PHƯƠNG | Xã Tâm Thắng             |
| NÔNG THỊ YẾN           | Thị trấn Ea TLing        |
| LƯU VĂN THAO           | Xã Tâm Thắng             |
| LỤC VĂN KHÁNH          | Xã Ea Pô                 |
| VI VĂN HOM             | Xã Đắk Wil               |
| HOÀNG THỊ MẮN          | Thị trấn Ea TLing        |
| LƯƠNG VĂN XUÂN         | Xã Tâm Thắng             |
| ĐINH VĂN THỰC          | Xã Trúc Sơn              |
| HẦU A TÚ               | Xã Ea Pô                 |
| HOÀNG THỊ PHƯƠNG       | Xã Nam Dong              |
| NÔNG VĂN BÁO           | Xã Ea Pô                 |
| LƯƠNG VĂN HỌC          | Xã Tâm Thắng             |
| LƯƠNG ĐỨC THÀNH        | Thị trấn Ea TLing        |
| VY VĂN TÔN             | Xã Cư Knia               |
| ĐÀM VĂN GIÁP           | Xã Đắk Wil               |
| LÒ VĂN MỢI             | Xã Đắk DRông             |
| HOÀNG VĂN VIÊN         | Xã Tâm Thắng             |
| NGUYỄN VĂN CHƯỞNG      | Xã Đắk DRông             |
| ĐẶNG THỊ LƯU           | Thị trấn Ea TLing        |
| VI VĂN ĐIỀU            | Xã Cư Knia               |
| HOÀNG XUÂN MÂY         | Xã Nam Dong              |
| NÔNG VĂN ĐẠI           | Xã Tâm Thắng             |
| LỮ VĂN TỰ              | Xã Đắk Wil               |
| HOÀNG VĂN ANH          | Xã Trúc Sơn              |
| VŨ QUỐC TRÌNH          | Xã Trúc Sơn              |
| CAO VĂN CHUNG          | Xã Ea Pô                 |
| ĐINH THỊ TOÀN          | Xã Tâm Thắng             |
| ĐÀM VĂN HƯƠNG          | Thị trấn Ea TLing        |
| VI THỊ THỦY            | Xã Đắk Wil               |
| PHẠM THÙY GIANG        | Xã Cư Knia               |
| CHU VĂN VẤN            | Xã Tâm Thắng             |
| LƯƠNG THỊ NHUNG        | Xã Nam Dong              |
| H ÐIU KÊÑ              | Xã Cư Knia               |
| PHẠM ĐỨC NAM           | Xã Trúc Sơn              |
| HOÀNG VĂN ĐÌNH         | Xã Đắk Wil               |
| Y TUẤN K' BUÔR         | Thị trấn Ea TLing        |
| NGUYỄN THỊ TÂM         | Xã Tâm Thắng             |
| Y LIÊP ÊYA             | Xã Đắk DRông             |
| HOÀNG VĂN VÀNG (B)     | Xã Cư Knia               |
| HOÀNG VĂN PÁ (D)       | Thị trấn Ea TLing        |
| Cao Văn Kính           | Xã Cư Knia               |
| LÝ VĂN KHAO            | Xã Tâm Thắng             |
| Phạm Thị Lộc           | Xã Trúc Sơn              |
| Đồng Thị Nõn           | Xã Cư Knia               |
| Phạm Văn Phàm          | Xã Ea Pô                 |
| HOÀNG VĂN PHÍNH        | Xã Đắk DRông             |
| Hoang Thị Hưu          | Xã Trúc Sơn              |
| Trần Văn Huy           | Thị trấn Ea TLing        |
| HÀ THỊ VẰN             | Xã Cư Knia               |
| TRẦN HUY THÔNG         | Xã Đắk DRông             |
| HOÀNG VĂN HÓA          | Xã Đắk Wil               |
| HỨA THỊ CẢNH           | Thị trấn Ea TLing        |
| LÝ VĂN SƠN             | Xã Nam Dong              |
| Nông Văn Dự            | Xã Đắk DRông             |
| HOÀNG VĂN CHINH        | Xã Trúc Sơn              |
| H LEM ÊBAN             | Xã Tâm Thắng             |
| HOÀNG THỊ XANH         | Xã Ea Pô                 |
| HOÀNG VĂN VẤN          | Xã Ea Pô                 |
| MÔNG THỊ SIM           | Xã Đắk DRông             |
| CHU VĂN HẠ             | Thị trấn Ea TLing        |
| HOÀNG THỊ VIỀN         | Xã Đắk Wil               |
| NÔNG HOÀNG VĂN         | Xã Nam Dong              |
| H NHANH KBUÔR          | Thị trấn Ea TLing        |
| Giàng Văn Tu           | Xã Trúc Sơn              |
| Y BLUÔN HRA            | Xã Đắk DRông             |
| H DLUÊ HRA             | Xã Tâm Thắng             |
| Y THÔNG NIÊ            | Xã Đắk Wil               |
| HÀ VĂN NGHĨA           | Xã Cư Knia               |
| H DJUIH KBUÔR          | Xã Cư Knia               |
| Y NGƯI KTUL            | Thị trấn Ea TLing        |
| H' BUEN HRA            | Xã Đắk DRông             |
| H LĨ HRA               | Xã Nam Dong              |
| HẦU THỊ SẦU            | Xã Trúc Sơn              |
| VÀNG A TU              | Thị trấn Ea TLing        |
| DƯƠNG THỊ PÁ           | Xã Tâm Thắng             |
| NÔNG VĂN THÀ           | Xã Đắk Wil               |
| H LIN HRA              | Thị trấn Ea TLing        |
| Y KÚT KỄN              | Xã Trúc Sơn              |
| H MIÊN HRA             | Xã Nam Dong              |
| HOÀNG DINH PÁ          | Xã Đắk Wil               |
| HOÀNG VĂN TU (A)       | Xã Cư Knia               |
| HOÀNG VĂN VIỆT         | Xã Đắk Wil               |
| DƯƠNG VĂN PỀNH         | Xã Cư Knia               |
| HOÀNG VĂN NGÃI         | Xã Nam Dong              |
| NÔNG VĂN TIẾN          | Xã Trúc Sơn              |
| NÔNG VĂN THÀNH         | Thị trấn Ea TLing        |
| DƯƠNG VĂN TU           | Xã Tâm Thắng             |
| HOÀNG VĂN LỪ           | Xã Đắk DRông             |
| DƯƠNG VĂN TU (B)       | Xã Ea Pô                 |
| DƯƠNG VĂN THẮNG        | Xã Nam Dong              |
| MÃ VĂN LU              | Xã Tâm Thắng             |
| HOÀNG VĂN HÀNH         | Xã Đắk Wil               |
| H NEN KBUÔR            | Xã Đắk DRông             |
| H GUAN KTUL            | Xã Cư Knia               |
| Y SĨN AYUN             | Thị trấn Ea TLing        |
| LÝ A TU                | Xã Đắk Wil               |
| DƯƠNG VĂN THÀNH        | Thị trấn Ea TLing        |
| DƯƠNG VĂN MỤA          | Xã Cư Knia               |
| Mai Văn Kiên           | Xã Đắk Wil               |
| NGUYỄN THỊ TIẾN        | Xã Tâm Thắng             |
| H JUN KBUÔR            | Xã Cư Knia               |
| H GUH PRIÊNG           | Xã Trúc Sơn              |
| H UN NIÊ               | Thị trấn Ea TLing        |
| HOÀNG VĂN THÀNH (B)    | Xã Đắk Wil               |
| Y NƯN KBUÔR            | Xã Đắk Wil               |
| Trần Thị Vui           | Xã Đắk DRông             |
| Y SINH KNUL            | Thị trấn Ea TLing        |
| LƯƠNG HỮU TRUNG        | Xã Đắk DRông             |
| NGUYỄN VĂN SỸ          | Xã Cư Knia               |
| Trương Viết Cường      | Xã Đắk Wil               |
| H ĐINH ÊBAN            | Xã Tâm Thắng             |
| Nông Văn Nghĩa         | Thị trấn Ea TLing        |
| Hoàng Thị Huệ          | Xã Trúc Sơn              |
| Trần Thanh Thảo        | Xã Cư Knia               |
| TRẦN THỊ THE           | Xã Ea Pô                 |
| H DREČ KTUL            | Xã Đắk DRông             |
| Hoàng Văn Thuận        | Xã Nam Dong              |
| NGUYỄN CÔNG CHÍNH      | Xã Ea Pô                 |
| TRƯƠNG TẤN DANH        | Xã Đắk DRông             |
| VI VĂN NÁO             | Xã Nam Dong              |
| Nguyễn Thị Hoa         | Xã Đắk DRông             |
| Y BÍCH KBUÔR           | Xã Ea Pô                 |
| Vũ Thị Cúc             | Xã Tâm Thắng             |
| TRẦN THIỆN BẢO         | Xã Cư Knia               |
| NGUYỄN THỊ MY          | Xã Đắk Wil               |
| NGUYỄN VĂN QUANG       | Thị trấn Ea TLing        |
| VŨ VĂN VỊ              | Xã Trúc Sơn              |
| LƯƠNG VĂN HIẾU         | Xã Trúc Sơn              |
| HOÀNG NGỌC SƠN         | Xã Ea Pô                 |
| ĐỖ THỊ HIỀN            | Xã Tâm Thắng             |
| Phùng Thị Hảo          | Thị trấn Ea TLing        |
| DƯƠNG THỊ CHÁM         | Xã Ea Pô                 |
| NGUYỄN THỊ HƯỜNG       | Xã Đắk DRông             |
| MAI VĂN LỰC            | Xã Đắk Wil               |
| HOÀNG PHI HỔ           | Xã Cư Knia               |
| TRỊNH THỊ LIÊN         | Xã Đắk DRông             |
| HOÀNG THỊ THIẾT        | Xã Trúc Sơn              |
| LÊ THỊ VÂN             | Xã Đắk Wil               |
| VŨ ĐÌNH QUYẾT          | Xã Tâm Thắng             |
| HOÀNG VĂN LUYỆN        | Xã Nam Dong              |
| NGUYỄN THỊ MÃO         | Xã Đắk DRông             |
| LANG PHÚC HOAN         | Xã Ea Pô                 |
| TRẦN THỊ MÃO           | Xã Tâm Thắng             |
| TÔ VĂN VỰC             | Xã Trúc Sơn              |

### Data
| family.hostName   | administrative.commune   |
|:------------------|:-------------------------|
| NGUYỄN VĂN HÂN    | Xã Ea Pô                 |
| NGUYỄN VĂN DŨNG   | Xã Đắk Wil               |
| TRẦN VĂN TOÀN     | Xã Trúc Sơn              |
| LÊ THỊ MƠ         | Xã Ea Pô                 |
| NGUYỄN THỊ LÝ     | Xã Tâm Thắng             |
| NGUYỄN THỊ QUỲ    | Xã Nam Dong              |
| NGUYỄN THANH THỦY | Xã Đắk DRông             |
| H MIĂT KNUL       | Xã Trúc Sơn              |
| PHẠM VĂN TUẤN     | Thị trấn Ea TLing        |
| NGUYỄN THỊ HÒA    | Xã Đắk DRông             |

*(Còn 194 dòng nữa)*

**Thời gian:** 2.30 giây

---

## 14. Thôn/bon có chủ hộ nghèo là nữ nhiều nhất Đắk Song 2023
### SQL
```sql
SELECT "administrative.commune", COUNT(*) AS "numberOfPoorHouseholds"
FROM households
WHERE classify = 'Hộ nghèo' AND "family.hostGender" = 'Nữ' AND "administrative.district" ILIKE '%Đắk Song%' AND "administrative.year" = 2023
GROUP BY "administrative.commune"
ORDER BY "numberOfPoorHouseholds" DESC
LIMIT 1;
```

### Answer (Hiển thị UI)
Thôn/bon có số hộ nghèo do nữ làm chủ nhiều nhất tại Đắk Song năm 2023 là xã Đắk Môl, với 27 hộ nghèo.

### Data
| administrative.commune   |   numberOfPoorHouseholds |
|:-------------------------|-------------------------:|
| Xã Đắk Môl               |                       27 |

**Thời gian:** 4.08 giây

---

## 15. Xã thiếu nước sạch nhiều nhất Tuy Đức 2024
### SQL
```sql
SELECT "administrative.commune", COUNT(*) AS "count" FROM households WHERE "deprivation.cleanWater" = true AND "administrative.district" ILIKE '%Tuy Đức%' AND "administrative.year" = 2024 GROUP BY "administrative.commune" ORDER BY "count" DESC LIMIT 1;
```

### Answer (Hiển thị UI)
Xã Quảng Tâm là xã thiếu nước sạch nhiều nhất tại Tuy Đức trong năm 2024.

### Data
| administrative.commune   |   count |
|:-------------------------|--------:|
| Xã Quảng Tâm             |       1 |

**Thời gian:** 3.32 giây

---

## 16. Trần Thị Liên ở Đắk Song là dân tộc gì ? Có điểm đánh giá b1 là bao nhiêu ? Có là dân tộc thiểu số ?
### SQL
```sql
SELECT "family.ethnicity", "b1Point", "family.isDTTS" FROM households JOIN members ON households."administrative.district" = members."administrative.district" AND households."administrative.commune" = members."administrative.commune" AND households."family.hostName" = members."member.fullName" AND households."administrative.year" = members."administrative.year" WHERE members."member.fullName" = 'Trần Thị Liên' AND households."administrative.district" ILIKE '%Đắk Song%';
```

### Answer (Hiển thị UI)
Trần Thị Liên ở Đắk Song thuộc dân tộc Nùng, có điểm đánh giá B1 là 137 và là dân tộc thiểu số.

### Data
| family.ethnicity   |   b1Point | family.isDTTS   |
|:-------------------|----------:|:----------------|
| Nùng               |       137 | True            |

**Thời gian:** 8.51 giây

---

## 17. Huyện Đắk RLấp có tổng cộng bao nhiêu chủ hộ nghèo là nam 2023
### SQL
```sql
SELECT COUNT(DISTINCT "family.hostName") FROM households WHERE classify = 'Hộ nghèo' AND "family.hostGender" = 'Nam' AND "administrative.district" ILIKE '%Đắk RLấp%' AND "administrative.year" = 2023;
```

### Answer (Hiển thị UI)
Huyện Đắk R'lấp có tổng cộng 203 chủ hộ nghèo là nam trong năm 2023.

### Data
|   count(DISTINCT "family.hostName") |
|------------------------------------:|
|                                 203 |

**Thời gian:** 3.42 giây

---

## 18. Số hộ nghèo theo các xã tại Krông Nô 2024, xã nào nhiều hộ nghèo nhất ?
### SQL
```sql
SELECT "administrative.commune", COUNT(*) AS "so_ho_ngheo" 
FROM households 
WHERE classify = 'Hộ nghèo' AND "administrative.district" ILIKE '%Krông Nô%' AND "administrative.year" = 2024 
GROUP BY "administrative.commune" 
ORDER BY "so_ho_ngheo" DESC 
LIMIT 1;
```

### Answer (Hiển thị UI)
Xã Nam Xuân có số hộ nghèo nhiều nhất tại Krông Nô vào năm 2024, với 20 hộ nghèo.

### Data
| administrative.commune   |   so_ho_ngheo |
|:-------------------------|--------------:|
| Xã Nam Xuân              |            20 |

**Thời gian:** 3.54 giây

---

## 19. Nhận xét về số lượng chủ hộ nghèo giữa nam và nữ của Tuy Đức 2024
### SQL
```sql
SELECT "family.hostGender", COUNT(*) AS "numberOfPoorHouseholds"
FROM households
WHERE classify = 'Hộ nghèo' AND "administrative.district" ILIKE '%Tuy Đức%' AND "administrative.year" = 2024
GROUP BY "family.hostGender";
```

### Answer (Hiển thị UI)
Số lượng chủ hộ nghèo ở Tuy Đức năm 2024 cho thấy sự chênh lệch rõ rệt giữa nam và nữ:

- Chủ hộ nghèo nam: 553
- Chủ hộ nghèo nữ: 276

Điều này cho thấy nam giới chiếm tỷ lệ cao hơn đáng kể trong số hộ nghèo so với nữ giới.

### Data
| family.hostGender   |   numberOfPoorHouseholds |
|:--------------------|-------------------------:|
| Nữ                  |                      276 |
| Nam                 |                      553 |

**Thời gian:** 5.10 giây

---

## 20. Số lượng chủ hộ dân tộc thiểu số là nữ tại Tuy Đức 2023, có nhiều hơn nam hay không ?
### SQL
```sql
SELECT "family.hostGender", COUNT(*) FROM households WHERE "family.isDTTS" = true AND "administrative.district" ILIKE '%Tuy Đức%' AND "administrative.year" = 2023 GROUP BY "family.hostGender";
```

### Answer (Hiển thị UI)
Số lượng chủ hộ dân tộc thiểu số là nữ tại Tuy Đức năm 2023 là 741, trong khi số lượng nam là 2599. Do đó, số lượng nữ ít hơn nam.

### Data
| family.hostGender   |   count_star() |
|:--------------------|---------------:|
| Nữ                  |            741 |
| Nam                 |           2599 |

**Thời gian:** 4.90 giây

---

## Tổng kết
- Thời gian trung bình: 3.69 giây / câu
