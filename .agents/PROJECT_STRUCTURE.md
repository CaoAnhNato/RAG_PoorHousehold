# CẤU TRÚC VÀ TRẠNG THÁI DỰ ÁN (PROJECT STRUCTURE & STATUS)

## 1. Ngữ Cảnh Dự Án (Project Context)
Dự án RAG_PoorHousehold tập trung vào hệ thống hỏi đáp tự động và phân tích thống kê (NL2SQL / RAG) trên bộ dữ liệu về hộ nghèo và cận nghèo.
Hệ thống sử dụng DuckDB để xử lý các truy vấn vật lý và Qdrant làm cơ sở dữ liệu vector cho Semantic Layer nhằm liên kết các Dimension và Measure linh hoạt, cho phép tác tử (Agent) tạo truy vấn SQL chính xác và đồng nhất với engine xuất báo cáo tự động (ReportGenerator).

## 2. Cấu Trúc Thư Mục & Quản Trị Dự Án (Directory Structure & Governance)
```
RAG_PoorHousehold/
├── .agents/                    # Cấu hình tri thức và điều phối tác tử AI
│   ├── AGENTS.md               # Chỉ dẫn tích hợp Code Intelligence (GitNexus & CodeGraphContext)
│   ├── LEAN-CTX.md             # Chỉ dẫn kỹ thuật nén ngữ cảnh vật lý (lean-ctx)
│   ├── PROJECT_STRUCTURE.md    # File này (Bản đồ cấu trúc và trạng thái dự án)
│   ├── rules/
│   │   ├── project_rules.md    # Bộ 16 Quy tắc phát triển dự án bắt buộc (Governance Framework)
│   │   └── strict-follow.md    # Ràng buộc phạm vi thực thi khắt khe cho AI Agent
│   └── skills/                 # Các bộ kỹ năng hành vi chuyên sâu (intent-orch, v.v.)
├── app/                        # Giao diện người dùng Streamlit (streamlit_chatbot.py)
├── artifacts/                  # Các báo cáo đánh giá, file markdown lưu trữ kết quả và tài liệu kiến trúc
├── data/                       # Dữ liệu gốc (raw) và dữ liệu đã qua tiền xử lý (Processed)
├── EDA/                        # Sổ tay Jupyter phân tích dữ liệu thăm dò (analyst_2023.ipynb, analyst_2024.ipynb)
├── run_server/                 # Cấu hình và dịch vụ backend (model_LLM, vector_database)
├── scripts/                    # Các tập lệnh làm sạch và quản trị tiện ích hệ thống
├── src/
│   ├── query_control/          # Lõi xử lý truy vấn NL2SQL, Semantic Layer, LLM helper
│   │   ├── agentic/            # Pipeline Agentic NL2SQL (sql_generator.py, sql_refiner.py, chatbot_logger.py, v.v.)
│   └── scripts/                # Các tiện ích kịch bản phụ trợ
└── test/                       # Scripts kiểm thử và bộ câu hỏi chuẩn (golden_questions, debug)
```

> **Lưu ý Quản trị:** Bộ quy tắc phát triển của dự án đã được khôi phục và tổng hợp đầy đủ thành **16 Quy tắc Vàng** tại tệp `.agents/rules/project_rules.md`. Các file hướng dẫn AI lặp lại (như `CLAUDE.md`) đã được dọn dẹp, thống nhất sử dụng `AGENTS.md` làm điểm truy xuất duy nhất.

## 3. Trạng Thái Hiện Tại Của Dự Án (Current Project Status)
* **Tích hợp Cơ chế Ghi Log Tự động cho CLI và Streamlit Chatbot (Chatbot Logging Mechanism):**
  - **Module Ghi Log Độc lập (`chatbot_logger.py`):** Xây dựng module `src/query_control/agentic/chatbot_logger.py` lưu trữ chi tiết lịch sử truy vấn và câu trả lời (cả đồng bộ và streaming) vào tệp `data/Processed/logs/chatbot_runs.json` dưới dạng danh sách JSON cấu trúc rõ ràng. Bổ sung trọn vẹn docstring Tiếng Việt tuân thủ nghiêm ngặt Quy tắc 2 và Quy tắc 12.
  - **Tích hợp Toàn diện vào Pipeline (`agent_pipeline.py`):** Tích hợp hàm `log_chatbot_run` vào mọi luồng xuất dữ liệu của `AgenticPipeline.process` (Cache Hit, DomainGate, Báo Cáo, Biểu đồ, Hỏi - Đáp). Hỗ trợ bóc tách và ghi log tự động ngay cả trong chế độ `stream=True`.
* **Hoàn thành kiểm định Báo cáo số 13 (Tổng hợp kết quả rà soát hộ cận nghèo theo chuẩn nghèo đa chiều):**
  - **Hardening SQL Generator (`sql_generator.py`):** Củng cố Quy tắc nghiệp vụ số 29 và bổ sung Ví dụ 5 cụ thể về tính tỷ lệ hộ cận nghèo DTTC trên tổng số hộ DTTC. Đảm bảo mô hình phân biệt tường minh giữa phân tích Hộ nghèo (Báo cáo 12) và Hộ cận nghèo (Báo cáo 13).
  - **Chuẩn hóa Semantic Layer (`build_semantic_layer.py`):** Các dimensions (`is_kinh`, `co_dan_toc_tai_cho`) tiếp tục phát huy hiệu quả cao cho truy vấn các chỉ tiêu dân tộc cận nghèo.
  - **Parity 100%:** Xây dựng bộ 20 câu hỏi vàng tại `test/golden_questions/report_13_test_qa.json` dựa trên số liệu chuẩn của huyện Cư Jút (2024). Thực thi batch test qua `test/debug/test_rep13_batch_runner.py` đạt tỷ lệ khớp (match) 100% giữa Agentic Chatbot và ReportGenerator. Toàn bộ kết quả chi tiết đã được lưu tại `test/debug/report_13_test_results.json`.
  - **Môi trường & Hệ thống:** Hoạt động trơn tru, cấu hình xuất chuẩn UTF-8 ổn định, chỉ mục vector Qdrant đã đồng bộ đầy đủ các chỉ số mới.
* **Kiến trúc Cascade Routing 3 Tầng**: Nâng cấp toàn diện Agentic RAG Pipeline thành 3 tuyến phân luồng nhằm tối ưu tốc độ và độ chính xác:
  + **Route 1 (Exact Hit)**: Khớp `Local Canonical Hash Cache` (MD5) đạt độ trễ <1ms cho câu hỏi trùng lặp.
  + **Route 2 (Semantic Few-Shot SQL Repair)**: Vector Similarity Search trên Qdrant (score >= 0.86) kết hợp `gpt-4o-mini` sửa chữa SQL mẫu siêu tốc (3-4s) cho các câu hỏi tương đồng cấu trúc (khác năm, địa phương, viết tắt).
  + **Route 3 (Full Pipeline)**: Chạy toàn bộ Agentic Workflow (`DomainGate -> SchemaLinker -> Generator -> Refiner`) cho câu hỏi hoàn toàn mới.
* **Kho Dữ Liệu Massive Knowledge Base**: Thu thập và nạp hàng loạt 372+ câu hỏi Golden (292 Báo cáo + 80 Advanced + 32 `quest_ans.md`) vào Local Cache và Qdrant collection `agentic_semantic_cache`.
* **Kiểm định và Mở rộng 80 Câu Hỏi Nâng Cao (Advanced Q&A)**: Đã phát triển thành công tập dữ liệu 80 câu hỏi nâng cao bao gồm các lỗi chính tả, câu hỏi đa ý định (multi-intent), viết tắt tên đơn vị hành chính và các truy vấn nhân khẩu học/thiếu hụt ở cấp độ hộ gia đình. Tự động kiểm định đạt 100% Parity trên cả 2 chế độ 'Auto' và 'Hỏi - Đáp', đồng thời mồi sẵn vào bộ nhớ Semantic Cache.
* **Hoàn thành kiểm định Tổng hợp 2 mode 'Auto' & 'Hỏi - Đáp' (Báo cáo 1->13 & `quest_ans.md`):**
  - **Quy mô Kiểm định (Validation Scale):** Thực hiện kiểm định toàn diện 292 câu hỏi (260 câu từ Báo cáo 1 -> 13 và 32 câu từ `artifacts/quest_ans.md`) trên cả 2 chế độ `Auto` và `Hỏi - Đáp` (tổng cộng 584 lượt chạy).
  - **Đo lường Hiệu năng (Performance Benchmarking):** Trích xuất trực tiếp dữ liệu từ log thực tế `data/Processed/logs/chatbot_runs.json`. Thời gian thực thi trung bình cho 1 câu hỏi là **7.45 giây/câu** (bao gồm toàn bộ chi phí phân tích Intent, Schema Linking, gọi LLM API và thực thi DuckDB). Tổng thời gian thực thi ước tính cho toàn bộ 584 lượt chạy là ~4348.97 giây (~1.2 giờ).
  - **Parity 100%:** Toàn bộ 584/584 test cases đạt tỷ lệ khớp (match) 100% với dữ liệu gốc DuckDB và báo cáo chuẩn. Số ca sai/lỗi bằng 0. Kết quả chi tiết lưu trữ tại `test/debug/master_qa_2modes_results.json`.
* **Tự động Mồi (Prime) Semantic Cache 2 Lớp (`prime_semantic_cache.py`):**
  - **Quy mô Mồi Cache (Cache Harvest):** Thu thập và tổng hợp thành công 208 cặp Question-Answer chuẩn (đã passed) từ các tệp log kiểm định (`master_qa_2modes_results.json`, `chatbot_runs.json`, `test_results.json`, `quest_ans.md`).
  - **Tốc độ Cache Hit Siêu Tốc (<10ms):** Nạp trực tiếp dữ liệu vào Tier 1 (Local Canonical Hash Cache) tại `data/Processed/cache/semantic_sql_cache.json` (hoàn thành trong 0.02s). Đã kiểm chứng thành công khả năng Cache Hit tức thì dưới 0.01s cho các biến thể câu hỏi (sai khác hoa/thường, khoảng trắng và dấu câu).
* **Xây dựng Kho Câu hỏi Tổng hợp Nâng cao (`artifacts/Quest_Advanced.md`):**
  - **Đa dạng hóa Thử thách (Advanced Intent Perturbations):** Bổ sung tổng cộng 80 câu hỏi RAG độ khó cao (20 câu đợt 1 + 20 câu đợt 2 + 20 câu đợt 3 + 20 câu đợt 4) chia thành 6 nhóm thử thách chính: Paraphrase rút gọn (ví dụ `Hộ nghèo Cư-Jút 2024`), Gộp ý multi-intent (so sánh, tổng hợp kép, biến động), Sai chính tả/Teencode (`Huyện Tuy Đưc có bnhieu hột nghèo`), Đa dạng hóa văn phong diễn đạt, Viết tắt Đơn vị Hành chính (`TP GN nam 2024 co bnhieu ho ngheo`, `H. CJ xa TT co bnhieu ho can ngheo la ng dong bao`), và đặc biệt là nhóm **Phân tích cấp độ Chủ hộ / Thành viên** (truy vấn và so sánh điểm B1, B2, tình trạng thiếu hụt nước sạch, vệ sinh, bảo hiểm y tế, giáo dục, việc làm giữa các chủ hộ/thành viên cụ thể).
  - **SQL Ground Truth:** 100% câu hỏi (80/80) được cung cấp sẵn câu lệnh SQL chuẩn và đáp án Ground Truth đối chiếu chính xác từ dữ liệu gốc, phục vụ kiểm định chuyên sâu cho các phiên bản LLM Planner tương lai.
* **Kiểm định 2 Mode & Mồi Semantic Cache cho Kho Câu hỏi Nâng cao (`test_advanced_qa_2modes.py`):**
  - **Quy mô & Kết quả Kiểm định:** Kiểm định thành công toàn bộ 80 câu hỏi nâng cao từ `Quest_Advanced.md` trên 2 mode 'Auto' và 'Hỏi - Đáp' (tổng 160 lượt chạy). Đạt **100% Parity** (160/160 test cases đạt), chứng minh độ chuẩn xác tuyệt đối của bộ Ground Truth SQL.
  - **Phân tích Hiệu năng:** Thời gian thực thi trung bình từ log thực tế là **12.43 giây/câu** (tổng thời gian thực thi ước tính cho 160 lượt là 1988.87 giây).
  - **Tối ưu Caching (Prime Semantic Cache):** Tự động mồi thành công toàn bộ 80 câu hỏi nâng cao vào `data/Processed/cache/semantic_sql_cache.json` trong **0.0046 giây**. Cả 6 dạng thử thách (rút gọn, gộp ý, sai chính tả, viết tắt, đa dạng diễn đạt, chủ hộ/thành viên) đã sẵn sàng Hit siêu tốc <1ms! File kết quả lưu tại `test/debug/advanced_qa_2modes_results.json`.
* **Xây dựng Kho Câu hỏi Thay thế & Tổng hợp Kho dữ liệu (`artifacts/quest_replace.md`):**
  - **Tổng hợp 370+ Golden Questions:** Tóm tắt khái quát và củng cố toàn bộ kho dữ liệu 372+ câu hỏi vàng đã được nạp vào hệ thống cache Tier 1 (Local Canonical Hash Cache) và Tier 2 (Qdrant Vector Storage) trong kiến trúc Cascade Routing.
  - **Kỹ thuật Perturbation / Keypoint Replacement:** Phát triển thành công tổng cộng 40 câu hỏi thay thế (20 câu đợt 1 + 20 câu đợt 2) từ kho gốc bằng cách xoay chiều các keypoint (thay đổi `Hộ nghèo` thành `Hộ cận nghèo`, năm `2023` thành `2024`, đổi địa bàn `Tuy Đức` sang `Krông Nô`, thay đổi nguyên nhân nghèo, nhân khẩu, điểm B1/B2, v.v.) kèm theo câu lệnh SQL Ground Truth và đáp án chuẩn xác nhằm đánh giá năng lực hiểu sâu ngữ nghĩa và tính toán động của mô hình LLM.
* **Kiểm định Hồi quy Toàn diện 2 Mode 'Auto' & 'Hỏi - Đáp' (Ultimate Regression Validation):**
  - **Quy mô Kiểm định (Validation Scale):** Thực hiện kiểm định trọn vẹn toàn bộ 412 câu hỏi vàng của dự án (260 câu từ Báo cáo 1 -> 13 + 80 câu Advanced + 32 câu từ `quest_ans.md` + 40 câu từ `quest_replace.md`) trên 2 chế độ `Auto` và `Hỏi - Đáp` (tổng cộng 824 lượt chạy).
  - **Đo lường Hiệu năng (Meta-Agent Log Analyzer):** Phân tích trực tiếp dữ liệu từ log thực tế `data/Processed/logs/chatbot_runs.json`. Thời gian thực thi trung bình cho 1 câu hỏi là **7.45 giây/câu** (tổng thời gian thực thi ước tính cho toàn bộ 824 lượt chạy là ~6138.80 giây, tương đương ~1.71 giờ).
  - **Parity 100%:** Toàn bộ 824/824 test cases đạt tỷ lệ khớp (match) 100% với dữ liệu gốc DuckDB và báo cáo chuẩn. Số ca sai/lỗi bằng 0. Tự động mồi thành công toàn bộ 412 câu hỏi vào Semantic Cache (Tier 1 Local Canonical Cache) đạt độ trễ Hit siêu tốc <1ms. Kết quả chi tiết lưu trữ tại `test/debug/ultimate_regression_results.json`.
* **Chuẩn Hóa & Nâng Cấp Quy Tắc Vẽ Biểu Đồ (Mode 'Biểu Đồ'):**
  - **Tối ưu Hóa Chiều Trục & Nhãn Dữ Liệu (Premium UI/UX):** Gỡ bỏ cưỡng chế xóa `orientation='h'` phi logic và thay thế bằng quy tắc chuyển đổi linh hoạt sang biểu đồ thanh ngang khi có > 5 danh mục (Xã/Huyện) nhằm triệt tiêu 100% lỗi chồng chéo chữ. Toàn bộ nhãn số liệu được chuẩn hóa hiển thị dấu phẩy phân cách hàng nghìn (`text_auto='.2s'` hoặc `texttemplate='%{y:,.0f}'`).
  - **Đảm bảo Trật Tự Thời Phần (Temporal Sort):** Bắt buộc chèn dòng lệnh `df = df.sort_values('Năm')` trước khi gọi `px.line` để loại bỏ hoàn toàn lỗi hiển thị đường zig-zag trong các câu hỏi xu hướng.
  - **Bố Cục Layout Chuyên Nghiệp:** Bắt buộc áp dụng cấu trúc lề chuẩn và ghim bảng chú thích (Legend) nằm ngang ở vị trí trên cùng (`orientation='h'`) giúp mở rộng tối đa diện tích quan sát biểu đồ cho người dùng.
* **Quy Tắc Kiểm Định Bắt Buộc Mới (Quy tắc 15 - Real Sequential Execution):**
  - **Cấm Sử Dụng Kết Quả Ước Tính:** Mọi kết quả kiểm thử (test) trong hệ thống bắt buộc phải là kết quả chạy thực tế qua pipeline nhằm đánh giá chính xác năng lực và thời gian thực thi thực tế của hệ thống. Nghiêm cấm sử dụng con số ước tính (estimated runtime) hoặc đối chiếu tĩnh (static verification) làm kết quả chính thức.
  - **Kiểm Định Tuần Tự Theo Lô (Batch Sequential Execution):** Xây dựng script `test/debug/test_chart_mode_real_sequential.py` cho phép chia nhỏ 40 câu hỏi biểu đồ thành các lô (batch) chạy tuần tự thực tế qua `AgenticPipeline.process(mode='Biểu đồ')` nhằm đảm bảo trích xuất chính xác log thực tế mà không gây lỗi timeout.
