# TỔNG QUAN NÂNG CẤP HỆ THỐNG AGENTIC & REPORT GENERATION

Tài liệu này tổng hợp các bước đột phá trong kiến trúc hệ thống và tính năng ứng dụng, hỗ trợ việc xây dựng tài liệu thuyết trình (Slide/Presentation) về dự án Chatbot Rà soát Hộ nghèo.

---

## 1. Tái Cấu Trúc Kiến Trúc (Agentic Framework Migration)
Hệ thống đã chuyển mình từ mô hình xử lý NL2SQL nguyên thủy (dựa trên Heuristic/Regex) sang kiến trúc đa tác tử (Multi-Agent) chuyên biệt và bền bỉ hơn, lấy `AgenticPipeline` làm trung tâm.

- **4 Module Tác Tử Độc Lập:**
  1. `SchemaLinker`: Phân tích ngữ nghĩa câu hỏi, ánh xạ chuẩn xác với cấu trúc cơ sở dữ liệu (Domain Gate & Schema Context).
  2. `SQLGenerator`: Trực tiếp dịch ngôn ngữ tự nhiên sang DuckDB SQL mà không cần qua tầng JSON trung gian, tối ưu hóa token và độ trễ (latency).
  3. `SQLRefiner`: Điểm nhấn mạnh mẽ nhất của hệ thống. Tích hợp cơ chế **"Logic Self-Correction"**, tự động bắt lỗi thực thi DuckDB (VD: thiếu cột trong GROUP BY) và yêu cầu LLM sửa lại truy vấn ngay lập tức thay vì trả lỗi về cho người dùng.
  4. `AnswerGenerator`: Chuyển hóa số liệu thô thành ngôn ngữ tự nhiên thân thiện, dễ hiểu.

## 2. Thiết Kế & Ra Mắt Chế Độ "Báo Cáo" (Report Mode)
Đây là tính năng lõi giúp giải quyết trực tiếp bài toán hành chính của Chính quyền địa phương, đưa ứng dụng từ mức "hỏi-đáp" lên mức "hỗ trợ nghiệp vụ chuyên sâu".

- **Hỗ trợ Toàn Diện 15 Biểu Mẫu Chính Phủ:** 
  Hệ thống đã được lập trình sẵn logic SQL (DuckDB) phức tạp để tính toán, tổng hợp và phân tổ cho 15 loại báo cáo khác nhau (từ báo cáo mức sống, nguyên nhân nghèo đến phân tích đa chiều trẻ em, hộ cận nghèo).
- **Trích Xuất Thông Minh bằng LLM:**
  Thay vì bắt người dùng chọn từ menu dài dòng, ở mode "Báo cáo", hệ thống sử dụng một LLM router nhỏ để **tự động hiểu yêu cầu** người dùng (VD: "Cho tôi báo cáo số 15 của Krông Nô năm 2024"). Hệ thống sẽ tự bóc tách `report_id`, `year`, và `district` để khởi chạy pipeline.

## 3. Hệ Thống Xuất Báo Cáo Tự Động (Report Generation Engine)
Được thiết kế để giải quyết bài toán "Pixel-perfect" so với định dạng Excel/Word gốc của Nhà nước.

- **Đồng bộ hóa 2 Định dạng (Word & PDF):** 
  Toàn bộ dữ liệu tự động được dàn trang và xuất đồng thời ra `.docx` (dùng `python-docx`) và `.pdf` (dùng `fpdf2`) với độ chính xác và tương đồng cấu trúc cao nhất.
- **Xử lý Bố cục Bảng Phức Tạp (Multi-tier Headers & Merge Cells):**
  - Khả năng xử lý tự động các cấu trúc phân cấp (Rollup) từ **Huyện -> Phường/Xã**.
  - Tính năng `is_commune_header` tự động nhận diện dòng tiêu đề cấp Xã, thực hiện **gộp cột (colspan)**, bôi đậm chữ, căn lề trái để tạo ra bảng số liệu dễ đọc và chuyên nghiệp.
  - Cấu hình độ rộng cột (Column Widths), font chữ (Times New Roman), và kiểu trang in (A4/A3, Landscape) được tùy biến cứng cho từng nhóm báo cáo.

## 4. Tích Hợp UI & Trải Nghiệm Người Dùng Cuối
- Hệ thống hỗ trợ đa kênh linh hoạt: giao diện dòng lệnh cho môi trường dev (`cli_agent_chatbot.py`) và ứng dụng Web UI (`streamlit_chatbot.py`).
- Chế độ hiển thị tương tác:
  - Nếu kết quả là số liệu, hiển thị thẳng dưới dạng bảng `pandas.DataFrame` đẹp mắt.
  - Bổ sung nút **Download trực tiếp** (Word/PDF) vào ngay phần phản hồi của Chatbot, tối giản số bước thao tác của người dùng.
- Quản lý phiên hội thoại (`UIHistoryStore`), đảm bảo quá trình truy vấn báo cáo và biểu đồ được lưu lại xuyên suốt.

---

### Điểm Nhấn (Key Takeaways for Presentation)
1. **Từ Reactive sang Proactive:** Không chỉ chờ hỏi và trả lời, hệ thống có khả năng tự sửa lỗi bên trong (`Self-Correction`).
2. **Khớp Hoàn Toàn Nghiệp Vụ:** Số hóa 100% 15 biểu mẫu báo cáo phức tạp, giải phóng nhân lực làm báo cáo hành chính bằng các tính năng trích xuất thông minh.
3. **Mở Rộng Linh Hoạt:** Kiến trúc 4 bước của `AgenticPipeline` giúp việc bổ sung nguồn dữ liệu mới hay thiết kế luồng mới trở nên cực kỳ dễ dàng.
