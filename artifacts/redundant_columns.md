# Báo cáo: Danh sách các cột dữ liệu dư thừa trong Dataset (data/Processed/)

Dựa trên quá trình đọc và phân tích cấu trúc các file `.xlsx` trong thư mục `data/Processed/`, dưới đây là danh sách các cột dữ liệu dư thừa. Những cột này chủ yếu chứa siêu dữ liệu (metadata) nội bộ của quá trình xử lý (ETL, Data Cleaning), độ tin cậy của thuật toán, hoặc đường dẫn file tạm. 

Chúng không mang lại giá trị thực tế cho mô hình LLM/RAG trong việc trả lời các câu hỏi thống kê/nghiệp vụ của người dùng và nên được loại bỏ (drop) khỏi Schema của Database dùng để truy vấn (DuckDB) để tối ưu không gian, tiết kiệm token cũng như giảm thiểu khả năng LLM bị "nhiễu" (hallucination).

## 1. Nhóm cột siêu dữ liệu quá trình xử lý (Processing Metadata & Tracking)
Nhóm này lưu vết quá trình điền khuyết dữ liệu (imputation), chuẩn hóa (normalization) và các logic sửa lỗi tự động. Không cần thiết cho việc phân tích nghiệp vụ nghèo/cận nghèo.
- `processing.duplicate_core_removed`
- `processing.original_family_code`
- `processing.family_code_was_changed`
- `processing.duplicate_code_group_size`
- `processing.note`
- `processing.original_date`
- `processing.source.date`
- `processing.date_was_filled`
- `processing.date_was_normalized`
- `processing.original_family_hostName`
- `processing.source.family.hostName`
- `processing.family_hostName_was_filled`
- `processing.family_hostName_rule`
- `processing.original_family_hostGender`
- `processing.source.family.hostGender`
- `processing.family_hostGender_was_filled`
- `processing.family_hostGender_rule`
- `processing.original_family_coDanTocTaiCho`
- `processing.source.family.coDanTocTaiCho`
- `processing.family_coDanTocTaiCho_was_filled`
- `processing.family_coDanTocTaiCho_rule`
- `processing.original_family_numberOfMembers`
- `processing.source.family.numberOfMembers`
- `processing.family_numberOfMembers_was_filled`
- `processing.family_numberOfMembers_rule`
- `processing.original_b1Point`
- `processing.source.b1Point`
- `processing.b1Point_was_filled`
- `processing.b1Point_rule`
- `processing.original_b2Point`
- `processing.source.b2Point`
- `processing.source.deprivation.totalCount`
- `processing.b2Point_was_filled`
- `processing.b2Point_rule`
- `processing.source.family.code`
- `processing.family_code_rule`

## 2. Nhóm cột Geocoding Confidence & Nguồn (Administrative Confidence)
Nhóm này thể hiện kết quả trung gian của quá trình tra cứu phân loại hành chính (vd: đây là vùng khó khăn, khu vực 1/2/3...), nguồn tra cứu và độ tin cậy. Chỉ hữu ích cho Data Engineer khi debug, không hữu ích cho RAG query.
- `administrative.areaTypeSource`
- `administrative.areaTypeConfidence`

## 3. Nhóm cột liên kết file và sinh dữ liệu trung gian (Internal File Pointers)
Chứa thông tin cờ hiệu đánh dấu xem một hộ gia đình đã được sinh danh sách thành viên hay chưa, hoặc tên file JSON/Excel trung gian.
- `family.membersGenerated`
- `family.membersFile`
- `family.membersJson`

## Đề xuất Giải Pháp Xử Lý
- **Tại Pipeline Tiền xử lý (Preprocessing):** Tiếp tục giữ nguyên các cột này trên file `.xlsx` / `.csv` lưu trong `data/Processed/` để phục vụ cho mục đích audit, logging, và đối soát chất lượng dữ liệu (Data Validation).
- **Tại Pipeline Load vào DuckDB (Query DB):** Cần cấu hình một bước `drop_columns` (hoặc cấu hình blacklist trong Schema Graph) đối với các chuỗi ký tự bắt đầu bằng `processing.*`, `family.members*` trước khi ingest vào DB và trước khi serialize Schema Map cung cấp cho AI Planner.
