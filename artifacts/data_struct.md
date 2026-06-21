# Cấu trúc và Mô hình Dữ liệu: `data/Processed`

Tài liệu này mô tả chi tiết về cấu trúc các tệp tin và thư mục bên trong `data/Processed`, cũng như mối quan hệ giữa chúng trong hệ thống Chatbot.

## 1. Sơ đồ Cây (Directory Tree)

```text
data/Processed/
├── 2023/                           # Dữ liệu đã xử lý theo thời gian (năm 2023)
├── 2024/                           # Dữ liệu đã xử lý theo thời gian (năm 2024)
├── intern_chatbot.duckdb           # Cơ sở dữ liệu chính (DuckDB) chứa data đã qua xử lý
├── rag_question_pairs.csv          # Tập dữ liệu huấn luyện hoặc đánh giá cho RAG
├── logs/                           # Nhật ký hệ thống và truy vết (Traces)
│   ├── processing_log.json         # Log quá trình ETL / xử lý dữ liệu
│   └── traces/                     # Chứa các file .json ghi lại chi tiết luồng xử lý của từng session
└── metadata/                       # Lưu trữ toàn bộ quy tắc, cấu hình và lớp ngữ nghĩa (Semantic Layer)
    ├── chart_constraints.json      # Ràng buộc cho việc vẽ biểu đồ
    ├── chart_rules.json            # Quy tắc chọn biểu đồ
    ├── chart_templates.json        # Template biểu đồ
    ├── data_dictionary.json        # Từ điển dữ liệu mô tả các cột/bảng
    ├── dimensions.json             # Định nghĩa các chiều phân tích (dimensions)
    ├── district_commune_mapping.json # Ánh xạ cấp hành chính (huyện/xã)
    ├── entities.json               # Các thực thể dữ liệu (entities)
    ├── report_schema_summary.json  # Tóm tắt cấu trúc schema báo cáo
    ├── required_columns_by_report.json # Mapping các cột bắt buộc theo loại báo cáo
    ├── synonyms.json               # Từ đồng nghĩa phục vụ NLP
    ├── visual_labels.json          # Nhãn hiển thị cho UI/biểu đồ
    ├── visualization_examples.json # Ví dụ về cách trực quan hóa
    └── query_control/              # Cấu hình lõi điều khiển Agent/Chatbot
        ├── schema_graph.json       # Graph mô tả các liên kết schema
        ├── semantic_layer.json     # Lớp ngữ nghĩa (Semantic Layer) lõi cho chatbot
        ├── query_plan_schema.json  # Schema để LLM lập kế hoạch (Query Planner)
        ├── qdrant_index_config.json # Cấu hình index của Qdrant
        ├── duckdb_config.json      # Cấu hình kết nối DuckDB
        ├── planner_prompt.md       # Prompt kỹ thuật cho Planner
        ├── general_answer_prompt.md # Prompt kỹ thuật cho phần sinh câu trả lời
        └── ...
```

## 2. Giải thích Nội dung và Mối quan hệ

### 2.1. Dữ liệu Lõi (Core Data)
- **`2023/` và `2024/`**: Chứa các file dữ liệu trung gian dạng CSV/Parquet được chia theo năm. Đây là nguồn dữ liệu đầu vào cho bước load vào database.
- **`intern_chatbot.duckdb`**: Đây là trái tim của hệ thống lưu trữ phân tích. Nó là tệp DuckDB đóng gói toàn bộ dữ liệu từ `2023/` và `2024/` thành các bảng quan hệ tối ưu cho truy vấn SQL. Mọi thao tác truy vấn dữ liệu từ Chatbot (thông qua `DuckDBEngine`) đều đánh trực tiếp vào tệp này.

### 2.2. Lớp Ngữ nghĩa và Quy tắc (Metadata & Semantic Layer)
Thư mục **`metadata/`** làm cầu nối giữa ngôn ngữ tự nhiên của người dùng và cơ sở dữ liệu DuckDB cứng nhắc:
- Khi người dùng hỏi, Chatbot sử dụng các file trong `metadata/query_control/` (đặc biệt là `semantic_layer.json` và `schema_graph.json`) để hiểu thuật ngữ nghiệp vụ (như "hộ nghèo", "tỷ lệ").
- Các file như `district_commune_mapping.json`, `data_dictionary.json` và `synonyms.json` giúp map chính xác các từ khóa tự do sang tên cột hoặc giá trị hợp lệ trong DuckDB.
- Khi có kết quả, các file như `chart_rules.json` và `visual_labels.json` quyết định cách trình bày số liệu (vẽ biểu đồ gì, nhãn trục là gì).

### 2.3. Nhật ký và Cải thiện thuật toán (Logs & RAG)
- **`logs/traces/`**: Lưu lại Input/Output của mọi Pipeline step. Giúp phục vụ mục đích debug và cải thiện prompt.
- **`rag_question_pairs.csv`**: Chứa các cặp câu hỏi - câu trả lời được dùng để đánh giá độ chính xác (Evaluation) của RAG pipeline, hoặc có thể dùng để tinh chỉnh (fine-tune) mô hình embedding/LLM trong tương lai.

### 2.4. Mối quan hệ tổng thể (Data Flow)
1. Dữ liệu thô $\rightarrow$ Xử lý thành `2023/`, `2024/` $\rightarrow$ Nạp vào `intern_chatbot.duckdb`.
2. Chatbot nhận câu hỏi $\rightarrow$ Tra cứu `metadata/` (Semantic/Schema) $\rightarrow$ Sinh SQL $\rightarrow$ Truy vấn `intern_chatbot.duckdb` $\rightarrow$ Render biểu đồ theo `metadata/chart_*.json`.
3. Toàn bộ hành vi được log lại vào `logs/`.
