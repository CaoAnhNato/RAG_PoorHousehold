# CẤU TRÚC VÀ TRẠNG THÁI DỰ ÁN (PROJECT STRUCTURE & STATUS)

## 1. Ngữ Cảnh Dự Án (Project Context)
Dự án RAG_PoorHousehold tập trung vào hệ thống hỏi đáp tự động và phân tích thống kê (NL2SQL / RAG) trên bộ dữ liệu về hộ nghèo và cận nghèo.
Hệ thống sử dụng DuckDB để xử lý các truy vấn vật lý và Qdrant làm cơ sở dữ liệu vector cho Semantic Layer nhằm liên kết các Dimension và Measure linh hoạt, cho phép tác tử (Agent) tạo truy vấn SQL chính xác và đồng nhất với engine xuất báo cáo tự động (ReportGenerator).

## 2. Cấu Trúc Thư Mục (Directory Structure)
```
RAG_PoorHousehold/
├── app/                        # Giao diện người dùng Streamlit (streamlit_chatbot.py)
├── artifacts/                  # Các báo cáo đánh giá, file markdown lưu trữ kết quả và tài liệu kiến trúc
├── data/                       # Dữ liệu gốc (raw) và dữ liệu đã qua tiền xử lý (Processed)
├── EDA/                        # Sổ tay Jupyter phân tích dữ liệu thăm dò (analyst_2023.ipynb, analyst_2024.ipynb)
├── run_server/                 # Cấu hình và dịch vụ backend (model_LLM, vector_database)
├── scripts/                    # Các tập lệnh làm sạch và quản trị tiện ích hệ thống
├── src/
│   ├── query_control/          # Lõi xử lý truy vấn NL2SQL, Semantic Layer, LLM helper
│   │   ├── agentic/            # Pipeline Agentic NL2SQL (sql_generator.py, sql_refiner.py, v.v.)
│   └── scripts/                # Các tiện ích kịch bản phụ trợ
└── test/                       # Scripts kiểm thử và bộ câu hỏi chuẩn (golden_questions, debug)
```

## 3. Trạng Thái Hiện Tại Của Dự Án (Current Project Status)
* **Hoàn thành kiểm định Báo cáo số 13 (Tổng hợp kết quả rà soát hộ cận nghèo theo chuẩn nghèo đa chiều):**
  - **Hardening SQL Generator (`sql_generator.py`):** Củng cố Quy tắc nghiệp vụ số 29 và bổ sung Ví dụ 5 cụ thể về tính tỷ lệ hộ cận nghèo DTTC trên tổng số hộ DTTC. Đảm bảo mô hình phân biệt tường minh giữa phân tích Hộ nghèo (Báo cáo 12) và Hộ cận nghèo (Báo cáo 13).
  - **Chuẩn hóa Semantic Layer (`build_semantic_layer.py`):** Các dimensions (`is_kinh`, `co_dan_toc_tai_cho`) tiếp tục phát huy hiệu quả cao cho truy vấn các chỉ tiêu dân tộc cận nghèo.
  - **Parity 100%:** Xây dựng bộ 20 câu hỏi vàng tại `test/golden_questions/report_13_test_qa.json` dựa trên số liệu chuẩn của huyện Cư Jút (2024). Thực thi batch test qua `test/debug/test_rep13_batch_runner.py` đạt tỷ lệ khớp (match) 100% giữa Agentic Chatbot và ReportGenerator. Toàn bộ kết quả chi tiết đã được lưu tại `test/debug/report_13_test_results.json`.
  - **Môi trường & Hệ thống:** Hoạt động trơn tru, cấu hình xuất chuẩn UTF-8 ổn định, chỉ mục vector Qdrant đã đồng bộ đầy đủ các chỉ số mới.
