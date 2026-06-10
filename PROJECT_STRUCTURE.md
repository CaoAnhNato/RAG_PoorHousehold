# CẤU TRÚC VÀ QUY TẮC DỰ ÁN (PROJECT STRUCTURE & RULES)

Dự án này tập trung vào việc xây dựng Chatbot thông minh và hệ thống tự động hóa báo cáo phân tích diễn biến hộ nghèo, hộ cận nghèo (2023-2024) dựa trên dữ liệu khảo sát tại tỉnh Đắk Nông, hỗ trợ xuất báo cáo theo 15 biểu mẫu chuẩn của Chính phủ.

---

## 1. Cấu Trúc Thư Mục & Vai Trò (Directory Tree & Roles)

Dưới đây là sơ đồ cấu trúc chi tiết của project để xác định nhanh các tệp tin liên quan:

```text
📁 Intern/ (Thư mục gốc của project)
├── 📄 PROJECT_STRUCTURE.md              <-- File này (Quản lý ngữ cảnh & Quy tắc dự án)
├── 📄 requirements.txt                 <-- Khai báo thư viện Python cần thiết (LangChain, DuckDB, Qdrant-Client, v.v.)
├── 📄 .env                             <-- Lưu trữ API Keys (FPT API, Qdrant, HuggingFace)
├── 📄 .gitignore                       <-- Bỏ qua các tệp không cần đẩy lên Git (file log, cache, v.v.)
├── 📄 codebook.docx                    <-- Tài liệu giải thích mã hóa và định dạng biến
├── 📄 bao_cao_tuan_1_chatbot_ho_ngheo.docx <-- Báo cáo tiến độ tuần 1
├── 📁 2023/                            <-- Dữ liệu khảo sát thô đầu vào năm 2023 (8 huyện/thành phố)
├── 📁 2024/                            <-- Dữ liệu khảo sát thô đầu vào năm 2024 (8 huyện/thành phố)
├── 📁 EDA/                             <-- Phân tích khám phá dữ liệu chuyên sâu
│   ├── 📓 analyst_2023.ipynb           <-- Notebook phân tích dữ liệu 2023
│   └── 📓 analyst_2024.ipynb           <-- Notebook phân tích dữ liệu 2024
├── 📁 Format_Report/                   <-- 15 biểu mẫu Excel template chuẩn để đổ dữ liệu vào
├── 📁 Processed/                       <-- Dữ liệu đã qua làm sạch, chuẩn hóa và làm giàu bởi pipeline
│   ├── 📁 2023/                        <-- Dữ liệu hộ gia đình đã xử lý năm 2023 (Có thêm _members/)
│   ├── 📁 2024/                        <-- Dữ liệu hộ gia đình đã xử lý năm 2024 (Có thêm _members/)
│   ├── 📁 metadata/                    <-- Metadata do hệ thống tự sinh từ Format_Report và dữ liệu
│   │   ├── 📄 data_dictionary.json     <-- Từ điển định nghĩa các cột dữ liệu hộ & thành viên
│   │   ├── 📄 district_commune_mapping.json <-- Mapping danh sách xã phường của từng huyện
│   │   ├── 📄 report_schema_summary.json <-- Tóm tắt cấu trúc và thông tin của 15 biểu mẫu
│   │   ├── 📄 required_columns_by_report.json <-- Danh sách cột dữ liệu bắt buộc cho từng báo cáo
│   │   └── 📁 query_control/           <-- Metadata phục vụ chatbot Q&A (Mới tạo ở Phase 2)
│   │       ├── 📄 schema_graph.json     <-- Biểu đồ quan hệ dữ liệu
│   │       ├── 📄 semantic_layer.json   <-- Định nghĩa Dimension, Measure, Metric, Business Term
│   │       ├── 📄 query_plan_schema.json <-- Schema kiểm định cấu trúc JSON Query Plan
│   │       ├── 📄 query_templates.json  <-- Mẫu câu truy vấn SQL DuckDB
│   │       ├── 📄 validation_rules.json <-- Bộ quy tắc kiểm định toàn hệ thống
│   │       ├── 📄 domain_gate_config.json <-- Cấu hình định tuyến Domain Gate
│   │       ├── 📄 qdrant_index_config.json <-- Cấu hình chỉ mục Qdrant
│   │       ├── 📄 planner_prompt.md     <-- Prompt định hướng LLM Planner
│   │       ├── 📄 general_answer_prompt.md <-- Prompt định hướng LLM giải thích lý thuyết
│   │       └── 📄 metadata_build_report.md <-- Báo cáo tiến trình xây dựng và kiểm định metadata
│   └── 📁 logs/
│       ├── 📄 processing_log.json      <-- Log chi tiết cấu hình và thống kê số dòng xử lý
│       └── 📊 validation_summary.xlsx  <-- Kết quả kiểm định logic dữ liệu sau khi chạy pipeline
├── 📁 scripts/                         <-- Mã nguồn tiền xử lý dữ liệu cốt lõi (Phase 1)
│   ├── 📄 pipeline.py                  <-- Logic lõi (Làm sạch, chuẩn hóa, phân tích template, kiểm định)
│   ├── 📄 process_all.py               <-- Orchestrator chạy toàn bộ quy trình tiền xử lý
│   └── 📄 validate_processed_data.py   <-- Công cụ kiểm định dữ liệu đầu ra
├── 📁 src/                             <-- Mã nguồn triển khai Chatbot Q&A (Phase 2)
│   └── 📁 query_control/
│       ├── 📄 build_schema_graph.py     <-- Quét file Excel sinh schema_graph.json
│       ├── 📄 build_semantic_layer.py   <-- Sinh semantic_layer.json dựa trên schema thực tế
│       ├── 📄 build_qdrant_semantic_index.py <-- Nạp định nghĩa nghiệp vụ vào Qdrant Vector DB
│       ├── 📄 semantic_retriever.py     <-- Tìm kiếm ứng viên từ Qdrant & rerank kết hợp
│       ├── 📄 validate_query_control_metadata.py <-- Tự động kiểm định các file metadata
│       ├── 📄 domain_gate.py            <-- Phân loại định tuyến câu hỏi người dùng
│       ├── 📄 query_planner.py          <-- Regex RuleExtractor + LLM Planner sinh Query Plan
│       ├── 📄 sql_compiler.py           <-- Biên dịch Query Plan sang SQL DuckDB
│       ├── 📄 duckdb_loader.py          <-- Nạp dữ liệu Excel gộp sang Parquet & DuckDB
│       ├── 📄 data_engine.py            <-- Lớp điều phối truy vấn DuckDB (an toàn, giới hạn dòng)
│       ├── 📄 query_cache.py            <-- Bộ đệm cache kết quả theo cấu trúc Canonical Plan
│       ├── 📄 observability.py          <-- Ghi nhật ký trace log, đo đạc latency của từng stage
│       ├── 📄 clarification_engine.py   <-- Phát hiện lỗi plan/định tuyến và sinh câu hỏi làm rõ
│       ├── 📄 conversation_memory.py    <-- Lưu trữ lượt hội thoại và phân tích câu kế thừa (follow-up)
│       ├── 📄 answer_engine.py          <-- Trực tiếp điều phối luồng Q&A chatbot MVP
│       ├── 📄 run_mvp_chatbot.py        <-- Giao diện CLI tương tác trực tiếp với Chatbot Q&A
│       ├── 📄 demo_mvp_runtime.py       <-- Script chạy kiểm thử tự động 7 trường hợp nghiệp vụ
│       └── 📄 demo_query_control.py     <-- Giao diện CLI chạy thử nghiệm Chatbot Q&A (cũ)
└── 📁 eval/                            <-- Hệ thống đánh giá mô hình LLM Planner cho Chatbot
    ├── 📄 run_llm_eval.py              <-- Script chạy đánh giá chất lượng LLM Planner
    ├── 📄 eval_llm_planning_cases.jsonl <-- File chứa các test cases câu hỏi người dùng & nhãn chuẩn
```

---

## 2. Bản Đồ File & Xác Định Nhanh File/Hàm Cần Chỉnh Sửa

Khi nhận được yêu cầu từ người dùng, chatbot có thể đối chiếu ngay với bảng sau để biết cần đọc và sửa đổi file/hàm nào:

| Yêu Cầu / Chức Năng Cần Thay Đổi | File Cần Sửa | Hàm / Vị Trí Cụ Thể | Ghi Chú |
| :--- | :--- | :--- | :--- |
| **Thay đổi logic làm sạch dữ liệu thô** | `scripts/pipeline.py` | `normalize_raw_core_values` | Các bước tiền xử lý thô trước khi sinh thuộc tính. |
| **Thay đổi logic sinh thuộc tính hộ nghèo** | `scripts/pipeline.py` | `generate_household_features` | Nơi tính toán các chỉ số đa chiều và chính sách hỗ trợ. |
| **Thay đổi định tuyến câu hỏi Chatbot** | `src/query_control/domain_gate.py` | `DomainGate.classify` | Phân loại giữa DATASET_QA, GENERAL_KNOWLEDGE, HYBRID, OUT_OF_SCOPE, CLARIFICATION_NEEDED. |
| **Tinh chỉnh Prompt sinh Query Plan** | `Processed/metadata/query_control/planner_prompt.md` | Toàn bộ prompt | Hướng dẫn LLM Planner cách sinh kế hoạch JSON Plan chuẩn. |
| **Sửa đổi logic sinh SQL từ Plan** | `src/query_control/sql_compiler.py` | `SQLCompiler.compile` | Xử lý ánh xạ cột vật lý, gộp filter nghiệp vụ và giải quyết JOIN. |
| **Cập nhật cách kết nối LLM FPT** | `src/query_control/llm_helper.py` | `call_llm` | Điều chỉnh cấu hình, URL API, cơ chế retry khi gọi mô hình gemma. |
| **Thay đổi cách tính điểm xếp hạng Qdrant** | `src/query_control/semantic_retriever.py` | `SemanticRetriever.retrieve` | Công thức kết hợp điểm cosine, exact anchor và rule signals. |

---

## 3. Trạng Thái Hiện Tại Của Dự Án (Project Status)
## 3. Trang Thai Hien Tai Cua Du An (Project Status)

Du an hien da hoan thanh Phase 2 - Xay dung thanh cong he thong Chatbot Q&A 2 nhanh va tich hop day du cac thanh phan MVP:
* **Da hoan thanh:**
  * **Phase 1 (Tien xu ly):** Pipeline tien xu ly va lam giau du lieu chay thanh cong, sinh day du du lieu ho gia dinh va thanh vien sach, luu tai `Processed/`.
  * **Phase 2 (Chatbot Q&A Engine & MVP Runtime Infrastructure):**
    * Tu dong quet va sinh file `schema_graph.json` va `semantic_layer.json`.
    * Xay dung chi muc tim kiem ngu nghia Qdrant (`build_qdrant_semantic_index.py`), nap 27 points.
    * Trien khai `DomainGate` ket hop bo loc tu khoa, khop chuoi chinh xac va LLM Fallback.
    * Trien khai `QueryPlanner` ket hop `RuleExtractor` de lap ke hoach truy van JSON va kiem dinh an toan.
    * Trien khai `SQLCompiler` bien dich Query Plan sang SQL DuckDB.
    * **DuckDB Engine:** Tong hop du lieu Excel nap thanh cong vao DuckDB vat ly.
    * **Query Cache (`query_cache.py`):** Exact-match MD5 hash cache (da loai bo semantic caching de tranh embedding overhead per-request).
    * **Observability, Clarification Engine, Conversation Memory:** Hoan thanh.
    * **Answer Engine MVP (`answer_engine.py`):** Chi giu luong `answer()` dong bo (da loai bo `async_answer` va `async_answer_stream`).
    * **CLI (`run_mvp_chatbot.py`) va Demo Scripts:** Hoan thanh.
    * **Golden Questions Evaluation:** Dat 100% Exact Match, 100% Route Accuracy, 100% SQL Exec Success voi Avg Latency ~1.73 giay.
  * **Khoi phuc hieu nang baseline (Session hien tai):**
    * `domain_gate.py`: Xoa pre-compute embedding routing patterns, khoi phuc rule-based + LLM fallback.
    * `query_cache.py`: Loai bo EmbeddingClient va cosine similarity, chi giu exact MD5 hash lookup.
    * `query_planner.py`: Xoa `async_plan()` method.
    * `answer_engine.py`: Xoa `async_answer()` va `async_answer_stream()`.

* **Dang trien khai / Can lam tiep theo:**
  * Chay lai danh gia golden questions (`eval/evaluate_chatbot_against_golden.py`) de xac nhan latency ve moc ~1.7s.
  * Tinh chinh hieu nang LLM Planner (~72.85% Planner Accuracy nhung 100% data accuracy).
  * Tich hop chatbot Q&A voi giao dien Web (UI) va xay dung module xuat bao cao Excel theo 15 bieu mau.

---

## 4. Quy Tắc Phát Triển Dự Án Bắt Buộc (Developer & Chatbot Rules)

### ⚠️ Quy tắc 1: Luôn đọc và cập nhật file `PROJECT_STRUCTURE.md`
* Bắt buộc đọc file này đầu tiên để nắm bắt ngữ cảnh, cấu trúc thư mục và trạng thái mới nhất của dự án.
* Cập nhật lại phần "3. Trạng Thái Hiện Tại Của Dự Án" sau khi hoàn thành mỗi yêu cầu phát triển.

### 📝 Quy tắc 2: Tiêu chuẩn hóa chú thích mã nguồn bằng Tiếng Việt
* Viết ghi chú và docstring bằng tiếng Việt rõ ràng cho tất cả các hàm và module mới được sửa đổi/tạo mới.

### 🛑 Quy tắc 3: Kiểm soát phân quyền Git/Github
* Tuyệt đối không chạy lệnh `git push` lên remote repository trừ khi có sự đồng ý hoặc hướng dẫn trực tiếp của người dùng.

### ⚙️ Quy tắc 4: Quy trình kiểm nghiệm chất lượng dữ liệu và Q&A
* Chạy lại bộ kiểm định tự động metadata `validate_query_control_metadata.py` sau khi có bất kỳ thay đổi nào liên quan đến cấu trúc metadata.

### 🐍 Quy tắc 5: Luôn Sử Dụng Môi Trường Ảo `venv`
* Mọi script kiểm thử, pipeline và chatbot bắt buộc phải chạy trong môi trường ảo `venv` cục bộ của dự án.

### 🛑 Quy tắc 6: Xử Lỗi Do Sơ Xuất Của Người Dùng (Handling User Oversight Errors)
* Dừng ngay lập tức tác vụ và báo cáo rõ ràng khi thiếu cấu hình `.env` hoặc lỗi kết nối dịch vụ ngoài (Qdrant, API Key), yêu cầu người dùng sửa cấu hình trước khi chạy tiếp.
