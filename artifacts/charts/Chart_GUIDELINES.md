# Hướng Dẫn Kỹ Thuật Và Bộ Quy Tắc Chấm Điểm Biểu Đồ - Sub-agent 'Visual'

Tài liệu này định nghĩa tiêu chuẩn và quy tắc vận hành độc lập dành cho Sub-agent **'Visual'** (được AI Assistant điều phối) trong quá trình debug và kiểm định chất lượng biểu đồ sinh ra bởi hệ thống Chatbot.

---

## 1. Nguyên Tắc Hoạt Động & Ranh Giới (Core Principles & Boundaries)

- **100% Đánh Giá Qua Ảnh Render:** Nghiêm cấm mọi hình thức ước tính, chẩn đoán, hoặc chấm điểm biểu đồ dựa trên phân tích mã nguồn (code). Mọi đánh giá, nhận xét và điểm số phải được kiểm chứng bằng cách kiểm tra hình ảnh render thực tế (qua screenshot base64).
- **Cơ chế Vòng Lặp Chấm Điểm (Scoring Loop):** Quá trình phân tích, chấm điểm và đưa feedback cho Agent Coding sửa code sẽ lặp lại liên tục cho đến khi biểu đồ đạt **>= 85 điểm** trên thang điểm 100.
- **Ranh Giới Bất Khả Xâm Phạm:** Các công cụ và quy trình của Sub-agent Visual chỉ hoạt động trong quá trình debug/testing của AI Assistant, tuyệt đối không can thiệp vào mã nguồn chính của hệ thống Chatbot Poorhousehold.

---

## 2. Tiêu Chuẩn Phân Tích & Bộ Quy Tắc (Analysis Standards & Rule Sets)

### 2.1. Kiểm Tra Độ Tương Phản WCAG (Contrast Verification)
- **Kiểm tra Relative Luminance:** Mọi thành phần text (tiêu đề, nhãn trục, chú thích) và màu nền tương ứng phải được kiểm tra tỷ lệ tương phản theo chuẩn WCAG 2.x.
- **Công thức tính tỷ lệ (Contrast Ratio):** $CR = (L1 + 0.05) / (L2 + 0.05)$, trong đó $L1$ là relative luminance của màu sáng hơn, $L2$ là relative luminance của màu tối hơn.
- **Tiêu chuẩn đạt (Threshold):**
  + **Text thường (Regular Text < 18pt):** Tỷ lệ tối thiểu **4.5:1**.
  + **Text lớn (Large Text >= 18pt hoặc bold >= 14pt):** Tỷ lệ tối thiểu **3:1**.

### 2.2. Kiểm Tra Chồng Chéo Nhãn (Overlap Detection)
- **DOM Bounding Box Analysis:** Sử dụng dữ liệu Bounding Box ($x, y, width, height$) thu thập từ DOM của các nhãn trên trục X.
- **Tiêu chí phát hiện:** Hai nhãn được coi là chồng chéo (overlap) nếu khoảng cách giữa mép phải của nhãn trước và mép trái của nhãn sau nhỏ hơn 2px hoặc bị giao nhau.
- **Hướng giải quyết bắt buộc:** 
  + Nếu phát hiện chồng chéo trên trục X, AI Assistant phải chỉ đạo sửa code Plotly xoay nhãn 45 độ (`tickangle=45`) hoặc ẩn bớt nhãn chẵn/lẻ (`dtick`).

### 2.3. Kiểm Tra Logic Loại Biểu Đồ (Chart Type Logic)
- **Dữ liệu Chuỗi Thời Gian (Time-series / Biến động theo Năm, Tháng):** 
  + **NGHIÊM CẤM** sử dụng Pie Chart / Donut Chart.
  + **BẮT BUỘC** sử dụng Line Chart hoặc Bar Chart.
  + **Sắp xếp thời gian:** Phải đảm bảo chèn `df = df.sort_values('Năm')` để tránh hiện tượng đường zig-zag phi logic.
- **Dữ liệu Tỷ Lệ Phần Trăm Tổng (Cơ cấu, Thành phần tỷ trọng):**
  + **BẮT BUỘC** sử dụng Pie Chart hoặc Donut Chart.
- **Dữ liệu So Sánh Nhiều Hạng Mục (> 5 Danh mục Xã / Huyện):**
  + **BẮT BUỘC** chuyển đổi sang biểu đồ thanh ngang (Horizontal Bar Chart với `orientation='h'`) để đảm bảo không gian đọc nhãn thoải mái nhất.

---

## 3. Ma Trận Chấm Điểm Thang 100 (100-Point Scoring Matrix)

Biểu đồ sẽ được chấm theo 4 tiêu chí cốt lõi, tổng điểm tối đa là 100 điểm. **Điểm chuẩn hoàn thành vòng lặp: >= 85 điểm.**

| Tiêu Chí | Điểm Tối Đa | Chi Tiết Đánh Giá & Điểm Trừ |
| :--- | :---: | :--- |
| **1. Đúng Logic Loại Biểu Đồ** | **30** | - Chọn đúng loại biểu đồ theo quy tắc mục 2.3 (30đ).<br>- Dùng Pie chart cho chuỗi thời gian: -30đ.<br>- Không dùng Horizontal bar cho >5 danh mục: -15đ. |
| **2. Trục X/Y Rõ Ràng & Không Overlap** | **30** | - Label trục X/Y đầy đủ, đúng ngữ nghĩa (15đ).<br>- Không có hiện tượng chồng chéo (overlap) nhãn (15đ).<br>- Phát hiện overlap qua DOM/ảnh: -15đ. |
| **3. Độ Tương Phản WCAG Đạt Chuẩn** | **20** | - Màu chữ và màu nền đạt tỷ lệ >= 4.5:1 (hoặc 3:1 với text lớn) (20đ).<br>- Tương phản thấp, khó đọc: -20đ. |
| **4. Tiêu Đề & Chú Thích (Title & Legend)** | **20** | - Bố trí Legend hợp lý (ưu tiên `orientation='h'` trên cùng), Title phản ánh đúng nội dung (20đ).<br>- Mất tiêu đề hoặc chú thích che khuất biểu đồ: -10đ. |

---

## 4. Quy Trình Phối Hợp Trong Debug & Testing

1. **Sinh Biểu Đồ:** Hệ thống/Agent Coding xuất file `.html` vào thư mục `artifacts/charts/`.
2. **Kích hoạt Tool MCP (khi có yêu cầu):** AI Assistant gọi `visual_start_chart_server` để bật server port 3000, sau đó gọi `visual_playwright_screenshot`, `visual_extract_dom_boxes`, và `visual_check_wcag_contrast`.
3. **Phân tích & Chấm điểm:** Sub-agent Visual tiếp nhận hình ảnh Base64 và dữ liệu DOM, thực hiện đối chiếu theo Ma trận 100 điểm.
4. **Vòng lặp Phản hồi:** Nếu điểm < 85, xuất báo cáo lỗi chi tiết. AI Assistant dựa vào đó sửa logic code và lặp lại bước 1. Nếu điểm >= 85, chấm dứt vòng lặp và ghi nhận biểu đồ đạt chuẩn.
