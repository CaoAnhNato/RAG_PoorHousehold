# -*- coding: utf-8 -*-
from __future__ import annotations
import sys
import os
import time
import pandas as pd
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.query_control.llm_helper import call_llm

class AgentChartGenerator:
    """Agent sinh mã Python (Plotly) vẽ biểu đồ và overview từ dữ liệu."""
    
    def generate(self, user_question: str, df: pd.DataFrame, save_path: Path | None = None) -> tuple[Any | None, str]:
        if df is None or df.empty:
            return None, "Không có dữ liệu để vẽ biểu đồ."
            
        # Extract data summary for LLM
        columns = list(df.columns)
        dtypes = df.dtypes.astype(str).to_dict()
        sample_data = df.head(5).to_dict(orient="records")
        
        system_prompt = """Bạn là trợ lý ảo phân tích dữ liệu chuyên sâu và trực quan hoá dữ liệu bằng biểu đồ.
Nhiệm vụ của bạn là:
1. Đọc mô tả cấu trúc DataFrame (columns, dtypes) và dữ liệu mẫu.
2. Dựa vào câu hỏi của người dùng, sinh ra MỘT đoạn mã Python sử dụng `plotly.express` (as `px`) hoặc `plotly.graph_objects` (as `go`) để vẽ biểu đồ phù hợp nhất.
3. Sinh ra một đoạn văn bản ngắn (1-3 câu) 'overview' NHẬN XÉT TRỰC TIẾP VÀO SỐ LIỆU của biểu đồ. Tuyệt đối KHÔNG viết câu giới thiệu sáo rỗng (ví dụ: "Biểu đồ này thể hiện..."). Hãy tập trung vào Insight: Đối tượng nào cao nhất? Xu hướng là gì? Tỷ trọng phân bổ ra sao?

YÊU CẦU CHO MÃ PYTHON:
- Đầu vào là biến `df` (pandas DataFrame). Không tự định nghĩa `df` hay đọc file.
- Gán đối tượng Plotly Figure vừa tạo vào biến `fig`. Ví dụ: `fig = px.bar(...)`.
- ĐỐI VỚI YÊU CẦU SO SÁNH NHẤT, TOP: Bắt buộc dùng biểu đồ thanh ngang (Horizontal bar chart) tức là thiết lập `orientation='h'` cho `px.bar`.
- ĐỐI VỚI BIỂU ĐỒ SO SÁNH THAY ĐỔI THEO THỜI GIAN CỦA NHIỀU ĐỐI TƯỢNG (VD: nhiều Huyện/Xã qua các năm): BẮT BUỘC dùng biểu đồ cột (`px.bar`) với thuộc tính `barmode='group'` và BẮT BUỘC sử dụng tham số `color='Năm'` (hoặc tên cột biểu thị thời gian) để phân tách các năm thành các cột đứng cạnh nhau. TUYỆT ĐỐI KHÔNG dùng `color='Huyện'` vì nó sẽ làm gộp dữ liệu các năm lại với nhau. TUYỆT ĐỐI KHÔNG dùng biểu đồ đường (`px.line`) cho dữ liệu chứa các danh mục rời rạc.
- ĐỐI VỚI YÊU CẦU "CƠ CẤU", "TỶ LỆ", "TỶ TRỌNG": BẮT BUỘC dùng biểu đồ tròn (Pie chart) bằng hàm `px.pie`. Khi dùng `px.pie`, bắt buộc gán `values='CộtSốLiệu'` và `names='CộtPhânLoại'` và KHÔNG gán tham số `color` (trừ khi dùng color map).
- ĐỐI VỚI BIỂU ĐỒ ĐƯỜNG (LINE CHART): Phải format rõ trục X nếu trục X là năm (hiển thị số nguyên, ví dụ 2023 thay vì 2,023.2) bằng cách dùng `fig.update_xaxes(tickformat='d', dtick=1)`. Bắt buộc hiển thị marker trên line (ví dụ `markers=True` trong `px.line`).
- MÀU SẮC: BẮT BUỘC sử dụng palette màu 'Paired'. Hãy luôn thêm tham số `color_discrete_sequence=px.colors.colorbrewer.Paired` vào MỌI hàm vẽ. Quan trọng: Đối với biểu đồ cột (bar), bạn bắt buộc PHẢI GÁN tham số `color` bằng một TRONG CÁC CỘT CÓ SẴN CỦA DATAFRAME (như `color='Năm'` hoặc `color='Huyện'`) thì Plotly mới áp dụng bảng màu. Đối với biểu đồ tròn (`px.pie`), chỉ cần `color_discrete_sequence` là đủ.
- TIÊU ĐỀ (TITLE) VÀ NHÃN TRỤC: Title, nhãn trục X, Y và Legend phải rõ ràng, ưu tiên tiếng Việt. ĐẶC BIỆT QUAN TRỌNG: Nếu câu hỏi có nhắc đến TÊN RIÊNG của các địa phương (ví dụ: "Thành phố Gia Nghĩa", "Huyện Tuy Đức"), BẮT BUỘC phải nhúng các tên riêng này vào Tiêu đề của biểu đồ để minh bạch thông tin (Ví dụ: "Biểu đồ ... của Thành phố Gia Nghĩa và Huyện Tuy Đức").
- BẮT BUỘC phải dùng template JSON: Bạn trả về chính xác chuỗi JSON có format sau:
```json
{
  "code": "import plotly.express as px\\nfig = px.pie(df, values='...', names='...', color_discrete_sequence=px.colors.colorbrewer.Paired, ...)\\nfig.update_layout(...)",
  "overview": "Đoạn văn nhận xét phân tích trực tiếp số liệu insight..."
}
```
Không trả về markdown code block thừa thãi bên ngoài JSON. Chỉ cần format JSON hợp lệ.
"""
        
        data_info = f"""--- Dữ liệu ---
Câu hỏi: {user_question}
Cột: {columns}
Kiểu dữ liệu: {dtypes}
Dữ liệu mẫu: {sample_data}
"""

        try:
            response = call_llm(
                system_prompt=system_prompt,
                user_prompt=data_info,
                temperature=0.2,
                max_tokens=1000,
                response_json=True
            )
            
            if isinstance(response, str):
                try:
                    response_json = json.loads(response)
                except json.JSONDecodeError:
                    return None, "Lỗi phân tích cú pháp JSON từ LLM."
            else:
                response_json = response
                
            code_str = response_json.get("code", "")
            overview = response_json.get("overview", "")
            
            # Execute Python code to get `fig`
            local_vars = {"df": df.copy()}
            try:
                exec(code_str, globals(), local_vars)
                fig = local_vars.get("fig", None)
                
                # Save the image if requested (for CLI debugging)
                if fig is not None and save_path is not None:
                    # ensure folder exists
                    save_path.parent.mkdir(parents=True, exist_ok=True)
                    html_path = save_path.with_suffix(".html")
                    fig.write_html(str(html_path))
                    # Đã loại bỏ thông báo "[System] Đã lưu..." khỏi overview để tránh hiện lên UI Streamlit
                    
                return fig, overview
            except Exception as e:
                import traceback
                error_msg = f"Lỗi khi thực thi mã sinh biểu đồ: {e}\n{traceback.format_exc()}"
                print(f"[AgentChartGenerator] {error_msg}")
                return None, f"Tôi đã gặp lỗi khi cố gắng vẽ biểu đồ: {e}"
                
        except Exception as e:
            return None, f"Lỗi gọi LLM khi sinh biểu đồ: {e}"
