# Báo cáo Phân tích Hiệu năng Latency - Chatbot Q&A Engine

Báo cáo này phân tích chi tiết thời gian thực thi (latency) của từng giai đoạn trong pipeline của Chatbot Q&A Engine dựa trên kết quả thực tế của lượt chạy đánh giá gần nhất với bộ **30 câu hỏi vàng** (Golden Dataset) khi bộ đệm cache được làm sạch (`Cache Cleared`).

---

## 1. Thống kê Tổng quan Hiệu năng (Overall Performance)

* **Số lượng câu hỏi phân tích**: 30 câu hỏi (từ GQ001 đến GQ030).
* **Tổng thời gian tiêu thụ trong các giai đoạn**: 48.69 giây.
* **Thời gian phản hồi trung bình (Avg)**: **1623.18 ms** (1.62 giây).
* **Trung vị thời gian phản hồi (P50)**: **1549.42 ms** (1.55 giây).
* **Thời gian phản hồi phân vị 95 (P95)**: **1944.64 ms** (1.94 giây).
* **Thời gian phản hồi nhanh nhất (Min)**: **1175.84 ms** (GQ010).
* **Thời gian phản hồi lâu nhất (Max)**: **3738.33 ms** (GQ009).

---

## 2. Điểm nghẽn Hiệu năng theo Giai đoạn (Pipeline Bottlenecks)

Dưới đây là chi tiết thời gian thực thi trung bình và tỷ lệ chiếm dụng của từng bước trong pipeline của hệ thống Chatbot:

| Giai đoạn (Stage) | Số lượng cuộc gọi | Thời gian TB (ms) | Min (ms) | Max (ms) | P50 (ms) | P95 (ms) | Tỷ lệ % |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **planner** | 29 | 864.84 | 743.53 | 979.62 | 841.63 | 932.72 | **51.50%** |
| **answer_formatting** | 29 | 552.33 | 0.01 | 2753.90 | 511.36 | 799.02 | **32.89%** |
| **domain_gate** | 30 | 245.54 | 181.21 | 312.95 | 247.48 | 290.30 | **15.13%** |
| **duckdb_execution** | 29 | 3.52 | 0.65 | 8.96 | 3.38 | 7.38 | **0.21%** |
| **sql_compiler** | 29 | 1.63 | 0.61 | 4.88 | 1.49 | 2.50 | **0.10%** |

> [!IMPORTANT]
> **Nhận xét cốt lõi**: 
> * Hai giai đoạn liên quan đến việc gọi API LLM từ bên ngoài (`planner` và `answer_formatting`) chiếm tới **84.39%** tổng thời gian xử lý của chatbot (tổng cộng gần 41.1 giây trên 48.7 giây).
> * `domain_gate` chiếm **15.13%** thời gian xử lý do sử dụng cả rule-based kết hợp LLM fallback khi cần thiết.
> * Xử lý dữ liệu cục bộ bằng DuckDB (`duckdb_execution` và `sql_compiler`) cực kỳ nhanh và tối ưu, chỉ chiếm **0.31%** tổng thời gian thực thi (trung bình ~5ms cho cả hai bước).

---

## 3. Chi tiết Latency theo Từng Câu hỏi Vàng (GQ001 - GQ030)

Bảng dưới đây thống kê thời gian thực thi chi tiết của 30 câu hỏi vàng (đơn vị: ms):

| Mã GQ | Câu hỏi | Tổng (ms) | Planner (ms) | Format (ms) | Gate (ms) | Exec (ms) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **GQ001** | Điểm B1 trung bình của tất cả các hộ khảo sát... | 1344.82 | 772.33 | 329.80 | 240.21 | 2.48 |
| **GQ002** | Năm 2024 có bao nhiêu hộ nghèo? | 1389.16 | 799.72 | 346.55 | 237.62 | 1.40 |
| **GQ003** | Có bao nhiêu hộ cận nghèo trong năm 2024? | 1498.03 | 923.45 | 339.65 | 231.46 | 1.36 |
| **GQ004** | Số hộ nghèo theo từng huyện trong năm 2024 là b... | 1601.70 | 816.69 | 599.68 | 181.21 | 2.14 |
| **GQ005** | Thống kê số lượng hộ cận nghèo theo huyện năm 2... | 1630.22 | 841.63 | 542.70 | 239.37 | 4.54 |
| **GQ006** | Số lượng hộ nghèo và cận nghèo của từng xã thuộ... | 2025.13 | 979.62 | 790.09 | 251.19 | 2.02 |
| **GQ007** | Điểm B1 trung bình của các hộ khảo sát năm 2024... | 1333.43 | 751.38 | 330.29 | 247.48 | 2.22 |
| **GQ008** | Điểm B2 trung bình của các hộ khảo sát năm 2024... | 1396.05 | 786.76 | 331.77 | 274.26 | 1.06 |
| **GQ009** | Thống kê số hộ nghèo theo từng xã trong năm 2023. | **3738.33** | 775.40 | **2753.90** | 203.71 | 3.37 |
| **GQ010** | Danh sách các hộ nghèo tại Huyện Cư Jút năm 202... | **1175.84** | 901.61 | **0.01** | 269.97 | 0.65 |
| **GQ011** | Huyện nào có nhiều hộ nghèo nhất trong năm 2024? | 1425.09 | 845.56 | 360.50 | 214.33 | 2.76 |
| **GQ012** | Huyện nào có ít hộ nghèo nhất trong năm 2024? | 1473.24 | 868.57 | 343.59 | 254.97 | 4.13 |
| **GQ013** | Xã nào thuộc Huyện Krông Nô có nhiều hộ cận ngh... | 1528.96 | 883.93 | 367.74 | 271.79 | 3.15 |
| **GQ014** | So sánh số lượng hộ nghèo giữa năm 2023 và năm ... | 1846.27 | 807.38 | 799.02 | 233.66 | 4.44 |
| **GQ015** | Huyện nào giảm được nhiều hộ nghèo nhất từ năm ... | 1524.03 | 853.96 | 405.79 | 255.77 | 6.50 |
| **GQ016** | Huyện nào có số hộ cận nghèo tăng nhiều nhất từ... | 1593.79 | 860.18 | 511.36 | 208.99 | 8.96 |
| **GQ017** | Điểm B1 trung bình theo từng huyện trong năm 20... | 1591.24 | 773.44 | 565.44 | 246.21 | 4.39 |
| **GQ018** | Thống kê điểm B2 trung bình theo từng huyện năm... | 1529.05 | 743.53 | 517.00 | 264.26 | 2.20 |
| **GQ019** | Tìm 5 xã có số hộ nghèo cao nhất trong năm 2024. | 1569.79 | 792.70 | 528.67 | 241.42 | 4.52 |
| **GQ020** | Tỷ lệ hộ nghèo trên tổng số hộ của từng huyện t... | 1604.24 | 803.08 | 579.50 | 216.12 | 3.41 |
| **GQ021** | Thống kê tỷ lệ hộ cận nghèo trên tổng số hộ của... | 1642.78 | 789.71 | 589.31 | 258.34 | 3.38 |
| **GQ022** | Phân bố số lượng hộ gia đình theo từng trạng th... | 1512.17 | 790.33 | 405.35 | 312.95 | 1.65 |
| **GQ023** | Huyện nào có tỷ lệ hộ nghèo cao nhất trong năm ... | 1465.23 | 852.86 | 367.15 | 238.90 | 4.46 |
| **GQ024** | Huyện nào có tỷ lệ hộ nghèo giảm nhiều nhất từ ... | 1615.05 | 929.69 | 421.56 | 254.22 | 7.38 |
| **GQ025** | Xã nào có điểm B1 trung bình cao nhất trong năm... | 1525.33 | 827.53 | 400.49 | 290.30 | 4.89 |
| **GQ026** | Xã nào có điểm B2 trung bình cao nhất trong năm... | 1457.22 | 816.90 | 402.47 | 230.67 | 5.54 |
| **GQ027** | Trong số các hộ nghèo năm 2024, huyện nào có đi... | 1441.31 | 860.20 | 365.19 | 210.63 | 2.65 |
| **GQ028** | Trong số các hộ cận nghèo năm 2024, huyện nào c... | 1591.94 | 932.72 | 411.66 | 240.40 | 4.21 |
| **GQ029** | Số lượng nhân khẩu thuộc diện hộ nghèo tại các ... | 1680.21 | 815.58 | 605.03 | 249.97 | 7.27 |
| **GQ030** | Độ tuổi trung bình của nhân khẩu thuộc diện hộ ... | 1684.81 | 829.80 | 586.35 | 258.44 | 6.25 |

---

## 4. Phân tích Các Trường hợp Đặc biệt (Case Studies)

### 1. Câu hỏi chậm nhất: **GQ009 (3738.33 ms)**
* **Nguyên nhân**: Điểm nghẽn nằm ở bước `answer_formatting` tốn tới **2753.90 ms**. Câu hỏi yêu cầu danh sách hộ nghèo theo từng xã trong năm 2023, dẫn đến số dòng kết quả SQL DuckDB trả về rất lớn (hơn 70 xã). Khi LLM nhận cấu trúc bảng thô này để định dạng thành báo cáo Markdown hoàn chỉnh, thời gian sinh (generation time) tỷ lệ thuận với số lượng token đầu ra, khiến latency tăng đột biến.

### 2. Câu hỏi nhanh nhất: **GQ010 (1175.84 ms)**
* **Định tuyến**: Điểm đặc biệt của GQ010 ("Danh sách các hộ nghèo tại Huyện Cư Jút...") là nó được phát hiện là câu hỏi trả về danh sách chi tiết quá lớn. Do đó, hệ thống chỉ xuất ra file Excel đính kèm và không thực hiện bước gọi LLM `answer_formatting` để tóm tắt chi tiết (thời gian định dạng chỉ tốn **0.01 ms**). Nhờ đó, tổng thời gian phản hồi giảm hẳn xuống chỉ còn 1.17 giây, chủ yếu là thời gian lập kế hoạch `planner` và thực thi SQL.

---

## 5. Chiến lược Tối ưu hóa Đề xuất (Actionable Optimization Strategies)

Để đưa thời gian phản hồi trung bình của chatbot xuống dưới **1.0 giây** trong khi vẫn duy trì độ chính xác 100%, chúng tôi đề xuất 4 chiến lược cụ thể sau:

### Chiến lược 1: Áp dụng cơ chế Query Cache nâng cao
* **Mô tả**: Sử dụng lại kết quả của các kế hoạch truy vấn có cấu trúc tương tự (Canonical Plan Hashing).
* **Hiệu quả dự kiến**: Giảm latency xuống **< 10 ms** (cache hit 100%) đối với các câu hỏi trùng lặp hoặc tương đương về mặt cấu trúc (chỉ khác tham số như tên xã, năm).

### Chiến lược 2: Tối ưu hóa Prompt và Giới hạn sinh của LLM (Max Tokens)
* **Mô tả**: Thiết lập `max_tokens` ngắn hơn cho bước `planner` (~150 tokens) và thiết kế hệ thống prompt cực kỳ cô đọng cho `answer_formatting`.
* **Hiệu quả dự kiến**: Giảm 30% - 40% thời gian chờ sinh token từ API LLM (ước tính giảm ~300ms - 500ms).

### Chiến lược 3: Gom nhóm (Consolidation) các bước gọi LLM
* **Mô tả**: Hiện tại luồng đi qua `domain_gate` và `planner` riêng biệt. Có thể tích hợp phân loại định tuyến trực tiếp vào bước lập kế hoạch của LLM hoặc tối ưu bộ phân loại `domain_gate` bằng rule-based 100% đối với các từ khóa cố định (năm, địa bàn) để tránh cuộc gọi LLM đầu tiên.
* **Hiệu quả dự kiến**: Tiết kiệm ~250ms (loại bỏ hoàn toàn cuộc gọi LLM ở `domain_gate`).

### Chiến lược 4: Bất đồng bộ hóa (Async Pipeline) & Stream kết quả
* **Mô tả**: Sử dụng async calls (`httpx.AsyncClient`) cho các cuộc gọi API LLM đồng thời, hoặc stream trực tiếp câu trả lời định dạng thô/báo cáo về giao diện người dùng.
* **Hiệu quả dự kiến**: Cải thiện đáng kể thời gian phản hồi cảm nhận (Perceived Latency) của người dùng xuống chỉ còn khoảng **500ms** khi chữ bắt đầu xuất hiện trên màn hình.
