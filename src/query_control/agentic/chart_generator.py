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
3. Sinh ra một đoạn văn bản ngắn (1-3 câu) 'overview' NHẬN XÉT TRỰC TIẾP VÀO SỐ LIỆU của biểu đồ. Yêu cầu bắt buộc cho đoạn văn nhận xét:
   - BẮT BUỘC đọc cột 'Năm' (nếu có) và gọi tên chính xác MỐC THỜI GIAN (ví dụ: "Trong năm 2024...", "Xuyên suốt năm 2023 và 2024...") ngay ở đầu câu để tránh nhầm lẫn.
   - BẮT BUỘC gọi tên (chỉ ra) đối tượng cao nhất/thấp nhất nếu có so sánh.
   - PHẢI CÓ TÍNH PHÂN TÍCH: Hãy nhận xét thêm về xu hướng (nếu có dữ liệu của nhiều năm) hoặc sự chênh lệch (gap) giữa đối tượng cao nhất và phần còn lại, tránh chỉ báo cáo số liệu một cách khô khan.
   - Tuyệt đối KHÔNG viết câu giới thiệu sáo rỗng (ví dụ: "Biểu đồ này thể hiện...").

YÊU CẦU CHO MÃ PYTHON:
- Đầu vào là biến `df` (pandas DataFrame). Không tự định nghĩa `df` hay đọc file.
- `fig = px.bar(...)` hoặc `fig = go.Figure(...)`.
- ĐẶC BIỆT QUAN TRỌNG: BẮT BUỘC phải đọc năm từ dữ liệu và đưa vào tham số `title` của biểu đồ để người dùng biết biểu đồ này dành cho năm nào (Ví dụ: `title='Tỷ lệ hộ nghèo theo từng Huyện năm 2024'`).
- Không được dùng `fig.show()`. Biến cuối cùng phải là `fig`.
- ĐỐI VỚI YÊU CẦU SO SÁNH NHẤT, TOP: BẮT BUỘC dùng biểu đồ cột (Bar chart) với trục `x` là cột Danh Mục (ví dụ: `x='Xã'`) và trục `y` là cột Số Liệu. BẮT BUỘC gán tham số `color` (vd `color='Xã'` hoặc `color='Năm'`) để các cột có màu sắc khác nhau, TUYỆT ĐỐI không để biểu đồ chỉ có 1 màu duy nhất! NẾU dữ liệu có chứa NHIỀU NĂM, BẮT BUỘC thêm `barmode='group'` và `color='Năm'` để hiển thị các năm đứng cạnh nhau. Đừng dùng `orientation='h'` trừ khi danh sách tên trục quá dài.
- ĐỐI VỚI YÊU CẦU SO SÁNH QUA CÁC NĂM (nhưng không nhắc đến "xu hướng"): BẮT BUỘC dùng biểu đồ cột đứng (`px.bar`) với trục `x` là cột Danh Mục, `y` là cột Số Liệu, thuộc tính `barmode='group'` và BẮT BUỘC sử dụng tham số `color='Năm'` để phân tách các năm thành các cột đứng cạnh nhau. TUYỆT ĐỐI KHÔNG gán `color` bằng cột Danh Mục (như `Xã` hay `Huyện`) vì nó sẽ làm gộp dữ liệu các năm lại với nhau thành 1 cột.
- ĐỐI VỚI YÊU CẦU "CƠ CẤU", "TỶ LỆ", "TỶ TRỌNG": BẮT BUỘC dùng biểu đồ tròn (Pie chart) bằng hàm `px.pie`. Khi dùng `px.pie`, bắt buộc gán `values='CộtSốLiệu'` và `names='CộtPhânLoại'`. ĐỂ NGƯỜI DÙNG DỄ ĐỌC: Bạn BẮT BUỘC phải thêm dòng lệnh `fig.update_traces(textposition='auto', textinfo='percent+label')` để hiển thị nhãn và phần trăm bên trong biểu đồ, hoặc tự động đưa ra ngoài kèm đường dẫn (leader lines) nếu không đủ chỗ. KHÔNG gán tham số `color` trừ khi dùng color map.
- ĐỐI VỚI DATAFRAME CÓ NHIỀU CỘT SỐ LIỆU ĐỂ SO SÁNH (ví dụ: đếm 12 chỉ số thiếu hụt khác nhau): TUYỆT ĐỐI KHÔNG truyền trực tiếp DataFrame vào `px.bar` để tránh lỗi xếp chồng (stacked) tất cả các chỉ số thành một thanh duy nhất. Bạn BẮT BUỘC phải làm phẳng dữ liệu (Melt) trước khi vẽ bằng lệnh: `df_melt = df.melt(id_vars=['Tên_Cột_Danh_Mục_Như_Năm_Hoặc_Huyện'], var_name='Chỉ số', value_name='Giá trị')`. Sau đó, dùng `df_melt` để vẽ biểu đồ cột (`px.bar` với `x='Chỉ số', y='Giá trị', color='Tên_Cột_Danh_Mục', barmode='group'`) hoặc biểu đồ tròn (`px.pie` với `names='Chỉ số', values='Giá trị'`).
- ĐỐI VỚI YÊU CẦU "XU HƯỚNG" (TREND): BẮT BUỘC dùng biểu đồ đường (Line chart) bằng hàm `px.line`. Trục X BẮT BUỘC phải là thời gian (`x='Năm'`). LỖI LOGIC ĐẶC BIỆT CHÚ Ý: Nếu dữ liệu có nhiều cột số liệu cần so sánh (ví dụ `Số hộ nghèo` và `Số hộ cận nghèo`), BẮT BUỘC phải truyền MẢNG danh sách các cột đó vào trục Y (ví dụ `y=['Số hộ nghèo', 'Số hộ cận nghèo']`) để vẽ đủ tất cả các đường, KHÔNG ĐƯỢC bỏ sót! Sử dụng tham số `color` để phân biệt đối tượng (ví dụ `color='Huyện'`). ĐỂ DỄ NHÌN HƠN: Bắt buộc thêm `markers=True`, `symbol='Huyện'` (hoặc `symbol='variable'`), và `line_dash='variable'` (hoặc `line_dash='Huyện'`) vào hàm `px.line` để tạo đa dạng nét đứt, nét liền, và các điểm vuông/tròn/tam giác khác nhau. ĐỂ HIỂN THỊ SỐ LIỆU: Bắt buộc phải gọi `fig.update_traces(mode='lines+markers+text', texttemplate='%{y}', textposition='top center')`. Cuối cùng format trục X (`fig.update_xaxes(tickformat='d', dtick=1)`). TUYỆT ĐỐI KHÔNG dùng biểu đồ cột cho yêu cầu "xu hướng".
- MÀU SẮC: BẮT BUỘC sử dụng palette màu 'Paired'. LƯU Ý TỐI QUAN TRỌNG: Để Plotly áp dụng được bảng màu Palette rời rạc, nếu cột bạn gán vào tham số `color` đang là số nguyên (ví dụ: `color='Năm'`), bạn BẮT BUỘC phải ép kiểu cột đó sang chuỗi trước khi vẽ bằng cách thêm `df['Năm'] = df['Năm'].astype(str)` hoặc truyền `color=df['Năm'].astype(str)`. Nếu không, Plotly sẽ áp dụng dải màu liên tục (continuous) và bảng màu Paired của bạn sẽ VÔ TÁC DỤNG! Hãy luôn thêm tham số `color_discrete_sequence=px.colors.colorbrewer.Paired` vào MỌI hàm vẽ. Đối với biểu đồ cột/đường, bạn bắt buộc PHẢI GÁN tham số `color` bằng một TRONG CÁC CỘT CÓ SẴN (hoặc sau khi Melt) thì mới lên màu.
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
            max_retries = 3
            current_prompt = system_prompt
            
            for attempt in range(max_retries):
                response = call_llm(
                    system_prompt=current_prompt,
                    user_prompt=data_info,
                    temperature=0.2,
                    max_tokens=1000,
                    response_json=True
                )
                
                if isinstance(response, str):
                    try:
                        response_json = json.loads(response)
                    except json.JSONDecodeError:
                        if attempt < max_retries - 1:
                            current_prompt += "\n\nLỖI LẦN TRƯỚC: Output không phải là JSON hợp lệ. Vui lòng trả về JSON chuẩn xác."
                            continue
                        return None, "Lỗi phân tích cú pháp JSON từ LLM."
                else:
                    response_json = response
                    
                code_str = response_json.get("code", "")
                overview = response_json.get("overview", "")
                
                # --- VALIDATE CODE VẼ BIỂU ĐỒ ---
                import re
                
                # 1. Kiểm tra biểu đồ xu hướng
                if "xu hướng" in user_question.lower() and "px.line" not in code_str:
                    if attempt < max_retries - 1:
                        current_prompt += "\n\nLỖI LẦN TRƯỚC: Yêu cầu xem 'xu hướng' nhưng bạn không sinh biểu đồ đường (px.line). Vui lòng dùng px.line."
                        continue
                    return None, "Lỗi logic: Người dùng yêu cầu xem 'xu hướng' nhưng LLM không sinh biểu đồ đường (px.line)."
                
                # Sửa lỗi: Nếu LLM nhét text_auto=True vào update_traces (gây lỗi Plotly), ta tự động bóc ra và sửa
                if "update_traces" in code_str and "text_auto=True" in code_str:
                    code_str = code_str.replace("text_auto=True", "")
                    if "px.bar(" in code_str and "text_auto" not in code_str:
                        code_str = code_str.replace("px.bar(", "px.bar(text_auto=True, ")
                
                # 2. Đảm bảo luôn sử dụng bảng màu 'Paired' thay vì mặc định
                if "color_discrete_sequence" not in code_str and "px." in code_str:
                    code_str = code_str.replace("px.bar(", "px.bar(color_discrete_sequence=px.colors.colorbrewer.Paired, ")
                    code_str = code_str.replace("px.pie(", "px.pie(color_discrete_sequence=px.colors.colorbrewer.Paired, ")
                    code_str = code_str.replace("px.line(", "px.line(color_discrete_sequence=px.colors.colorbrewer.Paired, ")
                elif "px.colors.colorbrewer.Paired" not in code_str:
                    code_str = re.sub(r"color_discrete_sequence=[^,)]+", "color_discrete_sequence=px.colors.colorbrewer.Paired", code_str)
                
                # 3. Đảm bảo trục X của biểu đồ đường được format chuẩn và nhãn dữ liệu, và cột cho biểu đồ bar
                if "px.line" in code_str:
                    if "dtick=1" not in code_str:
                        code_str += "\nfig.update_xaxes(tickformat='d', dtick=1)"
                    if "markers=" not in code_str:
                        code_str = code_str.replace("px.line(", "px.line(markers=True, ")
                    if "texttemplate" not in code_str:
                        code_str += "\nfig.update_traces(mode='lines+markers+text', texttemplate='%{y}', textposition='top center')"
                if "px.bar" in code_str:
                    # Tự động xoá orientation='h' nếu LLM thiết lập sai trục x là text và y là số
                    if "orientation='h'" in code_str or 'orientation="h"' in code_str:
                        if ("x='Xã'" in code_str or 'x="Xã"' in code_str or "x='Huyện'" in code_str or 'x="Huyện"' in code_str or "x='Năm'" in code_str or 'x="Năm"' in code_str):
                            code_str = code_str.replace("orientation='h',", "").replace('orientation="h",', "").replace("orientation='h'", "").replace('orientation="h"', "")

                    if "texttemplate" not in code_str and "text_auto" not in code_str:
                        if "orientation='h'" in code_str or 'orientation="h"' in code_str:
                            code_str += "\nfig.update_traces(texttemplate='%{x}', textposition='outside')"
                        else:
                            code_str += "\nfig.update_traces(texttemplate='%{y}', textposition='outside')"
                if "px.pie" in code_str:
                    if "textinfo" not in code_str:
                        code_str += "\nfig.update_traces(textposition='auto', textinfo='percent+label')"
                # ---------------------------------
                
                # Execute Python code to get `fig`
                local_vars = {"df": df.copy()}
                try:
                    exec(code_str, globals(), local_vars)
                    fig = local_vars.get("fig", None)
                    
                    # Save the image if requested
                    if fig is not None and save_path is not None:
                        save_path.parent.mkdir(parents=True, exist_ok=True)
                        html_path = save_path.with_suffix(".html")
                        fig.write_html(str(html_path))
                        
                    return fig, overview
                except Exception as e:
                    import traceback
                    error_msg = f"Lỗi khi thực thi mã sinh biểu đồ: {e}"
                    print(f"[AgentChartGenerator] {error_msg}")
                    if attempt < max_retries - 1:
                        # Feed the error back to the LLM to self-correct
                        current_prompt += f"\n\nLỖI TRONG LẦN CHẠY CODE TRƯỚC: {e}. Vui lòng sửa lại mã Python để không bị lỗi này. CHÚ Ý: KHÔNG ĐƯỢC để `text_auto=True` bên trong hàm `fig.update_traces()`, tham số đó chỉ dành cho hàm `px.bar()`."
                        continue
                    else:
                        return None, f"Tôi đã gặp lỗi khi cố gắng vẽ biểu đồ: {e}"
                    
        except Exception as e:
            return None, f"Lỗi gọi LLM khi sinh biểu đồ: {e}"
