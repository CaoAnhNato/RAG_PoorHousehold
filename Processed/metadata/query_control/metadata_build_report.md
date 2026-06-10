# BÁO CÁO XÂY DỰNG METADATA TRUY VẤN (METADATA BUILD REPORT)

**Thời gian sinh:** 2026-06-10 02:15:30

## 1. Kết quả quét Schema Graph
- **Số file hộ gia đình quét thành công:** 16
- **Số file thành viên quét thành công:** 16
- **Số cột phát hiện trong households:** 116
- **Số cột phát hiện trong members:** 20

## 2. Cảnh báo & Lỗi (Warnings)
- Không có cảnh báo hay lỗi nghiêm trọng nào được ghi nhận.

## 3. Kết quả ánh xạ Semantic Layer
- **Tổng số Dimensions đã tạo:** 9
- **Tổng số Measures đã tạo:** 4
- **Tổng số Metrics đã định nghĩa:** 6
- **Tổng số Business Terms định nghĩa:** 8
- **Tổng số Query Examples để test/embed:** 4

### Trạng thái các Metrics:
- **household_count**: ready (Lý do: Đầy đủ cột vật lý)
- **poor_household_count**: ready (Lý do: Đầy đủ cột vật lý)
- **near_poor_household_count**: ready (Lý do: Đầy đủ cột vật lý)
- **avg_b1_score**: ready (Lý do: Đầy đủ cột vật lý)
- **avg_b2_score**: ready (Lý do: Đầy đủ cột vật lý)
- **member_count**: ready (Lý do: Đầy đủ cột vật lý)

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

## 4. Kết quả nạp chỉ mục ngữ nghĩa Qdrant
- **Địa chỉ Qdrant:** `http://localhost:6333`
- **Tên Collection:** `query_control_semantic`
- **Mô hình Embedding:** `intfloat/multilingual-e5-small`
- **Kích thước vector:** 384
- **Tổng số điểm đã index:** 27
  - Số chỉ số (metrics): 6
  - Số chiều dữ liệu (dimensions): 9
  - Số thuật ngữ nghiệp vụ (business terms): 8
  - Số câu hỏi mẫu (query examples): 4
- **Collection được tạo lại (recreated):** True

## 5. Kết quả kiểm định tự động Metadata (Self-Validation)
**Thời gian kiểm định:** 2026-06-10 10:40:42
###  Toàn bộ file metadata đã vượt qua bài kiểm định thành công!
- [PASS] validation_rules.json hợp lệ.
- [PASS] schema_graph.json hợp lệ và đầy đủ nodes.
- [PASS] semantic_layer.json hợp lệ.
- [PASS] domain_gate_config.json hợp lệ.
- [PASS] Prompt 'planner_prompt.md' hợp lệ.
- [PASS] Prompt 'general_answer_prompt.md' hợp lệ.


## 4. Kết quả nạp chỉ mục ngữ nghĩa Qdrant
- **Địa chỉ Qdrant:** `http://localhost:6333`
- **Tên Collection:** `query_control_semantic`
- **Mô hình Embedding:** `Vietnamese_Embedding`
- **Kích thước vector:** 1024
- **Tổng số điểm đã index:** 31
  - Số chỉ số (metrics): 9
  - Số chiều dữ liệu (dimensions): 10
  - Số thuật ngữ nghiệp vụ (business terms): 8
  - Số câu hỏi mẫu (query examples): 4
- **Collection được tạo lại (recreated):** True
