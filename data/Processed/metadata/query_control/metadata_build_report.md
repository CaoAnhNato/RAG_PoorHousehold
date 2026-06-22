# BÁO CÁO XÂY DỰNG METADATA TRUY VẤN (METADATA BUILD REPORT)

**Thời gian sinh:** 2026-06-21 13:56:45

## 1. Kết quả quét Schema Graph
- **Số file hộ gia đình quét thành công:** 17
- **Số file thành viên quét thành công:** 16
- **Số cột phát hiện trong households:** 75
- **Số cột phát hiện trong members:** 20

## 2. Cảnh báo & Lỗi (Warnings)
- [WARNING] Không thể đọc file data/Processed/2024/~$Huyện Cư Jút.xlsx: Excel file format cannot be determined, you must specify an engine manually.

## 3. Kết quả ánh xạ Semantic Layer
- **Tổng số Dimensions đã tạo:** 22
- **Tổng số Measures đã tạo:** 4
- **Tổng số Metrics đã định nghĩa:** 10
- **Tổng số Business Terms định nghĩa:** 8
- **Tổng số Query Examples để test/embed:** 4

### Trạng thái các Metrics:
- **household_count**: ready (Lý do: Đầy đủ cột vật lý)
- **poor_household_count**: ready (Lý do: Đầy đủ cột vật lý)
- **near_poor_household_count**: ready (Lý do: Đầy đủ cột vật lý)
- **avg_b1_score**: ready (Lý do: Đầy đủ cột vật lý)
- **avg_b2_score**: ready (Lý do: Đầy đủ cột vật lý)
- **member_count**: ready (Lý do: Đầy đủ cột vật lý)
- **household_member_count**: ready (Lý do: Đầy đủ cột vật lý)
- **avg_age**: ready (Lý do: Đầy đủ cột vật lý)
- **poor_rate**: ready (Lý do: Đầy đủ cột vật lý)
- **near_poor_rate**: ready (Lý do: Đầy đủ cột vật lý)

### Trạng thái các Dimensions:
- **year**: ready (Lý do: Đầy đủ cột vật lý)
- **district**: ready (Lý do: Đầy đủ cột vật lý)
- **commune**: ready (Lý do: Đầy đủ cột vật lý)
- **poverty_status**: ready (Lý do: Đầy đủ cột vật lý)
- **household_id**: ready (Lý do: Đầy đủ cột vật lý)
- **gender**: ready (Lý do: Đầy đủ cột vật lý)
- **ethnicity**: ready (Lý do: Đầy đủ cột vật lý)
- **local_ethnicity**: ready (Lý do: Đầy đủ cột vật lý)
- **age_group**: ready (Lý do: Đầy đủ cột vật lý)
- **host_name**: ready (Lý do: Đầy đủ cột vật lý)
- **is_dtts**: ready (Lý do: Đầy đủ cột vật lý)
- **poverty_detail**: ready (Lý do: Đầy đủ cột vật lý)
- **near_poverty_detail**: ready (Lý do: Đầy đủ cột vật lý)
- **medium_living_standard**: ready (Lý do: Đầy đủ cột vật lý)
- **has_no_labor**: ready (Lý do: Đầy đủ cột vật lý)
- **has_revolution_merit**: ready (Lý do: Đầy đủ cột vật lý)
- **clean_water**: ready (Lý do: Đầy đủ cột vật lý)
- **hygienic_toilet**: ready (Lý do: Đầy đủ cột vật lý)
- **lack_production_land**: ready (Lý do: Đầy đủ cột vật lý)
- **lack_capital**: ready (Lý do: Đầy đủ cột vật lý)
- **lack_labor**: ready (Lý do: Đầy đủ cột vật lý)
- **illness_accident**: ready (Lý do: Đầy đủ cột vật lý)

## 4. Kết quả nạp chỉ mục ngữ nghĩa Qdrant
- **Địa chỉ Qdrant:** `http://localhost:6333`
- **Tên Collection:** `query_control_semantic`
- **Mô hình Embedding:** `text-embedding-3-small`
- **Kích thước vector:** 1536
- **Tổng số điểm đã index:** 44
  - Số chỉ số (metrics): 10
  - Số chiều dữ liệu (dimensions): 22
  - Số thuật ngữ nghiệp vụ (business terms): 8
  - Số câu hỏi mẫu (query examples): 4
- **Collection được tạo lại (recreated):** True


## 4. Kết quả nạp chỉ mục ngữ nghĩa Qdrant
- **Địa chỉ Qdrant:** `http://localhost:6333`
- **Tên Collection:** `query_control_semantic`
- **Mô hình Embedding:** `intfloat/multilingual-e5-small`
- **Kích thước vector:** 384
- **Tổng số điểm đã index:** 44
  - Số chỉ số (metrics): 10
  - Số chiều dữ liệu (dimensions): 22
  - Số thuật ngữ nghiệp vụ (business terms): 8
  - Số câu hỏi mẫu (query examples): 4
- **Collection được tạo lại (recreated):** True


## 4. Kết quả nạp chỉ mục ngữ nghĩa Qdrant
- **Địa chỉ Qdrant:** `http://localhost:6333`
- **Tên Collection:** `query_control_semantic`
- **Mô hình Embedding:** `text-embedding-3-small`
- **Kích thước vector:** 1536
- **Tổng số điểm đã index:** 44
  - Số chỉ số (metrics): 10
  - Số chiều dữ liệu (dimensions): 22
  - Số thuật ngữ nghiệp vụ (business terms): 8
  - Số câu hỏi mẫu (query examples): 4
- **Collection được tạo lại (recreated):** True
