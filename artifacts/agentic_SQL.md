# Cơ Chế Hoạt Động Của Kiến Trúc Agentic NL2SQL

Kiến trúc Agentic NL2SQL (Natural Language to SQL) trong dự án chuyển đổi quy trình truy vấn tĩnh thành một hệ thống đa tác tử (multi-agent) linh hoạt. Thay vì dựa vào các quy tắc regex cứng nhắc, hệ thống sử dụng hai Agent chính phối hợp với nhau để tạo ra và sửa lỗi câu lệnh SQL một cách tự động và chính xác.

Dưới đây là giải thích chi tiết về cơ chế hoạt động của 2 agent nòng cốt: **SQL Generator** và **SQL Refiner (Self-Corrector)**.

---

## 1. SQL Generator Agent (Tác tử Sinh SQL)

**Vai trò:** Đây là Agent chịu trách nhiệm nhận yêu cầu bằng ngôn ngữ tự nhiên từ người dùng và dịch nó thành câu lệnh SQL ban đầu.

**Cơ chế hoạt động:**
- **Tiếp nhận Context (Ngữ cảnh):** SQL Generator nhận đầu vào bao gồm câu hỏi của người dùng (NL query) cùng với siêu dữ liệu (metadata) của cơ sở dữ liệu đã được **Schema Linker** trích xuất (gồm tên bảng, tên cột, kiểu dữ liệu, các giá trị mẫu, và các logic nghiệp vụ như phân biệt `beginningClassify` và `classify`).
- **Phân tích Intent (Ý định):** Agent sử dụng LLM để hiểu ý định phân tích của người dùng (ví dụ: thống kê xu hướng qua các năm, so sánh đầu kỳ/cuối kỳ, đếm số lượng).
- **Sinh Code (Generation):** Dựa vào schema và prompt được thiết kế chặt chẽ (zero-shot hoặc few-shot prompting), Agent trực tiếp tạo ra câu lệnh SQL nhằm trả lời câu hỏi. 
- **Bàn giao:** Câu lệnh SQL thô này sau đó được chuyển đến bước thực thi và kiểm định.

---

## 2. SQL Refiner / Self-Corrector Agent (Tác tử Tự Đánh giá và Sửa lỗi)

**Vai trò:** Đóng vai trò như một "người gác cổng" (Guardrail) và trình gỡ lỗi (Debugger). Nó đảm bảo câu lệnh SQL do Generator tạo ra không chỉ đúng cú pháp mà còn đúng logic nghiệp vụ.

**Cơ chế hoạt động:**
- **Thực thi và Bắt lỗi (Execution & Exception Handling):** SQL Refiner lấy câu lệnh SQL từ Generator và chạy thử trên Database (hoặc trình giả lập). Nếu có lỗi cú pháp (Syntax Error) hoặc lỗi thực thi, nó sẽ bắt (catch) log lỗi này.
- **Bẫy Logic (Logic Trap):** Không chỉ lỗi hệ thống, Refiner còn tự động kiểm tra các lỗi logic phổ biến thường bị bỏ sót bởi LLM. Ví dụ:
  - Bắt lỗi khi các trường (columns) nằm trong mệnh đề `SELECT` bị thiếu so với những trường được khai báo trong mệnh đề `GROUP BY`.
  - Kiểm tra xem câu lệnh SQL có trả về tập dữ liệu rỗng (empty results) do sai lệch điều kiện `WHERE` hay không.
- **Vòng lặp Phản hồi (Feedback Loop):** Nếu phát hiện lỗi (ví dụ thông qua `ValueError`), SQL Refiner sẽ tổng hợp chi tiết lỗi (Error Message + Rule bị vi phạm) thành một đoạn phản hồi (Feedback) và gửi ngược lại cho SQL Generator.
- **Tái tạo (Re-iteration):** SQL Generator nhận feedback này, nhận thức được mình đã làm sai ở đâu, và tự động viết lại câu lệnh SQL mới. Vòng lặp này tiếp tục cho đến khi câu SQL chạy thành công và vượt qua các bài kiểm tra logic, hoặc đạt đến giới hạn số lần thử tối đa.

---

## Tóm lược Luồng Xử Lý (Workflow)

1. **User** -> Đặt câu hỏi NL.
2. **SQL Generator** -> Sinh SQL (Dựa trên Schema).
3. **SQL Refiner** -> Chạy thử và phân tích SQL.
    - *Nếu Lỗi:* Gửi thông báo lỗi về lại bước 2 (Tạo thành vòng lặp tự sửa chữa).
    - *Nếu Đúng:* SQL được chấp nhận và trả kết quả về để **Answer Generator** (hoặc trình Report/Chart) trình bày cho User.

**Lợi ích của cơ chế này:**
- Chịu lỗi tốt (Fault-tolerant): Không bị gián đoạn (crash) hệ thống khi LLM sinh sai cú pháp.
- Giảm thiểu Hallucination: Các ràng buộc và kiểm tra logic nghiêm ngặt ép LLM phải tuân thủ đúng cấu trúc CSDL thực tế.
- Tự động hóa cao: Tiết kiệm thời gian rà soát thủ công, thích ứng được với nhiều loại câu hỏi phức tạp.
