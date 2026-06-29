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
from src.query_control.agentic.utils import normalize_columns

class AgentChartGenerator:
    """Agent sinh mã Python (Plotly) vẽ biểu đồ và overview từ dữ liệu."""
    
    def generate(self, user_question: str, df: pd.DataFrame, save_path: Path | None = None) -> tuple[Any | None, str, str]:
        if df is None or df.empty:
            return None, "Không có dữ liệu để vẽ biểu đồ.", ""
            
        # Chuẩn hoá tên cột sang tiếng Việt trước
        df = normalize_columns(df.copy())
        
        # Làm sạch DataFrame: thay thế NaN/Null để tránh hiển thị chữ 'NaN' trên biểu đồ
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(0)
            else:
                df[col] = df[col].fillna("")
                
        # Loại bỏ cột 'Năm' (hoặc các cột thời gian duy nhất) nếu chỉ có 1 giá trị duy nhất và không yêu cầu vẽ xu hướng qua nhiều năm
        year_cols = [c for c in df.columns if c.lower() in ["năm", "year", "administrative.year"]]
        for y_col in year_cols:
            if df[y_col].nunique() <= 1 and not any(w in user_question.lower() for w in ["xu hướng", "thay đổi", "qua các năm", "từ năm", "đến năm"]):
                df = df.drop(columns=[y_col])
            
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
- Đầu vào là biến `df` (pandas DataFrame). Không tự định nghĩa `df` hay đọc file. Bắt buộc kiểm tra và chỉ dùng đúng các cột có sẵn trong mô tả Dữ liệu.
- `fig = px.bar(...)` hoặc `fig = go.Figure(...)`. Không được dùng `fig.show()`. Biến cuối cùng phải là `fig`.
- ĐẶC BIỆT QUAN TRỌNG: BẮT BUỘC phải đọc năm từ dữ liệu và đưa vào tham số `title` của biểu đồ để người dùng biết biểu đồ này dành cho năm nào (Ví dụ: `title='Tỷ lệ hộ nghèo theo từng Huyện năm 2024'`).
- ĐỐI VỚI YÊU CẦU SO SÁNH NHẤT, TOP, SO SÁNH QUY MÔ: BẮT BUỘC dùng biểu đồ cột (Bar chart). BẮT BUỘC gán tham số `color` (vd `color='Xã'` hoặc `color='Năm'`) để các cột có màu sắc khác nhau, TUYỆT ĐỐI không để biểu đồ chỉ có 1 màu duy nhất! QUY TẮC CHỌN TRỤC X: Trục x (hoặc trục y nếu biểu đồ ngang) BẮT BUỘC phải là cột danh mục phân loại chính (ví dụ: 'Huyện', 'Xã', 'Giới tính', 'Nhóm dân tộc', 'Chỉ số', 'Nguyên nhân'...). NẾU dữ liệu chỉ có số liệu của MỘT NĂM DUY NHẤT (ví dụ cột 'Năm' chỉ toàn giá trị 2024), TUYỆT ĐỐI KHÔNG ĐƯỢC gán `x='Năm'` hoặc `color='Năm'` vì sẽ làm biểu đồ bị gộp sai! CHỈ gán `x='Năm'` khi câu hỏi yêu cầu xem XU HƯỚNG qua nhiều năm. NẾU dữ liệu có chứa NHIỀU NĂM, BẮT BUỘC thêm `barmode='group'` và `color='Năm'` để hiển thị các năm đứng cạnh nhau. LƯU Ý ĐẢO CHIỀU TRỤC: NẾU danh sách tên danh mục (như Xã, Huyện) có HƠN 5 ĐỐI TƯỢNG và tên dài, bạn BẮT BUỘC dùng biểu đồ thanh ngang (`orientation='h'`, `y='Danh Mục'`, `x='CộtSốLiệu'`) để không bị đè chữ; ngược lại dùng thanh đứng (`x='Danh Mục'`, `y='CộtSốLiệu'`). ĐỊNH DẠNG SỐ: Bắt buộc định dạng nhãn có dấu phẩy phân cách hàng nghìn bằng `text_auto='.2s'` hoặc `texttemplate='%{y:,.0f}'` (hoặc `%{x:,.0f}` nếu thanh ngang).
- ĐỐI VỚI YÊU CẦU SO SÁNH QUA CÁC NĂM (nhưng không nhắc đến "xu hướng"): BẮT BUỘC dùng biểu đồ cột đứng (`px.bar`) với trục `x` là cột Danh Mục, `y` là cột Số Liệu, thuộc tính `barmode='group'` và BẮT BUỘC sử dụng tham số `color='Năm'` để phân tách các năm thành các cột đứng cạnh nhau. TUYỆT ĐỐI KHÔNG gán `color` bằng cột Danh Mục (như `Xã` hay `Huyện`) vì nó sẽ làm gộp dữ liệu các năm lại với nhau thành 1 cột.
- ĐỐI VỚI YÊU CẦU "CƠ CẤU", "TỶ LỆ", "TỶ TRỌNG": LƯU Ý QUAN TRỌNG: NẾU DataFrame có từ 2 cột số liệu trở lên (ví dụ có cả cột 'Số hộ nghèo' và 'Số hộ cận nghèo' phân theo 'Huyện'), TUYỆT ĐỐI KHÔNG DÙNG BIỂU ĐỒ TRÒN (`px.pie`) vì biểu đồ tròn không thể hiện được 2 cột số liệu cùng lúc. Trong trường hợp này, BẮT BUỘC phải dùng biểu đồ cột ghép (`px.bar` với `y=['Số hộ nghèo', 'Số hộ cận nghèo']`, `barmode='group'`) hoặc làm phẳng dữ liệu rồi vẽ biểu đồ cột. CHỈ DÙNG BIỂU ĐỒ TRÒN (`px.pie`) khi chỉ có ĐÚNG 1 cột số liệu cần chia tỷ lệ theo 1 cột phân loại (ví dụ: tỷ lệ Nam/Nữ). Khi dùng `px.pie`, bắt buộc gán `values='CộtSốLiệu'` và `names='CộtPhânLoại'`, đồng thời thêm `fig.update_traces(textposition='auto', textinfo='percent+label')`. KHÔNG gán tham số `color` trừ khi dùng color map.
- ĐỐI VỚI DATAFRAME CÓ NHIỀU CỘT SỐ LIỆU ĐỂ SO SÁNH (ví dụ: đếm 12 chỉ số thiếu hụt khác nhau, hoặc có 2 cột Số hộ nghèo và Số hộ cận nghèo): TUYỆT ĐỐI KHÔNG truyền trực tiếp DataFrame vào `px.bar` để tránh lỗi xếp chồng (stacked) sai lệch. Bạn BẮT BUỘC phải làm phẳng dữ liệu (Melt) trước khi vẽ bằng lệnh: `df_melt = df.melt(id_vars=['Tên_Cột_Danh_Mục_Như_Huyện_Hoặc_Xã'], var_name='Chỉ số', value_name='Giá trị')`. LƯU Ý: Không đưa cột 'Năm' vào `id_vars` nếu chỉ có 1 năm duy nhất. Sau đó, dùng `df_melt` để vẽ biểu đồ cột (`px.bar` với `x='Tên_Cột_Danh_Mục', y='Giá trị', color='Chỉ số', barmode='group'`).
- ĐỐI VỚI YÊU CẦU "XU HƯỚNG" (TREND): BẮT BUỘC dùng biểu đồ đường (Line chart) bằng hàm `px.line`. QUY TẮC SẮP XẾP THỜI GIAN (CRITICAL): Trước khi gọi `px.line`, bạn BẮT BUỘC phải sắp xếp dữ liệu theo thời gian bằng lệnh `df = df.sort_values('Năm')` để đường không bị vẽ nhảy zig-zag! Trục X BẮT BUỘC phải là thời gian (`x='Năm'`). LỖI LOGIC ĐẶC BIỆT CHÚ Ý: Nếu dữ liệu có nhiều cột số liệu cần so sánh, BẮT BUỘC phải truyền MẢNG danh sách các cột đó vào trục Y (ví dụ `y=['Số hộ nghèo', 'Số hộ cận nghèo']`) để vẽ đủ tất cả các đường, KHÔNG ĐƯỢC bỏ sót! Sử dụng tham số `color` để phân biệt đối tượng (ví dụ `color='Huyện'`). Bắt buộc thêm `markers=True`, `symbol='Huyện'` (hoặc `symbol='variable'`), và `line_dash='variable'` (hoặc `line_dash='Huyện'`) vào hàm `px.line` để tạo đa dạng nét đứt, nét liền, và các điểm vuông/tròn/tam giác khác nhau. Bắt buộc gọi `fig.update_traces(mode='lines+markers+text', texttemplate='%{y:,.0f}', textposition='top center')`. Cuối cùng format trục X (`fig.update_xaxes(tickformat='d', dtick=1)`). TUYỆT ĐỐI KHÔNG dùng biểu đồ cột cho yêu cầu "xu hướng".
- MÀU SẮC & BỐ CỤC UI PREMIUM: BẮT BUỘC sử dụng palette màu 'Paired'. Nếu cột bạn gán vào tham số `color` đang là số nguyên (ví dụ: `color='Năm'`), bạn BẮT BUỘC phải ép kiểu cột đó sang chuỗi trước khi vẽ bằng cách thêm `df['Năm'] = df['Năm'].astype(str)`. Bắt buộc thêm tham số `color_discrete_sequence=px.colors.colorbrewer.Paired` vào MỌI hàm vẽ. ĐỂ TỐI ƯU HÓA KHÔNG GIAN VÀ TRỰC QUAN (PREMIUM UI): BẮT BUỘC thêm dòng lệnh `fig.update_layout(margin=dict(l=20, r=20, t=60, b=20), legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))` vào TẤT CẢ các biểu đồ để bảng chú thích nằm ngang ở phía trên cùng, tránh bị xén chữ và mở rộng tối đa không gian biểu đồ.
- TIÊU ĐỀ (TITLE) VÀ NHÃN TRỤC: Title, nhãn trục X, Y và Legend phải rõ ràng, ưu tiên tiếng Việt. ĐẶC BIỆT QUAN TRỌNG: Nếu câu hỏi có nhắc đến TÊN RIÊNG của các địa phương (ví dụ: "Thành phố Gia Nghĩa", "Huyện Tuy Đức"), BẮT BUỘC phải nhúng các tên riêng này vào Tiêu đề của biểu đồ để minh bạch thông tin.
- BẮT BUỘC phải dùng template JSON: Bạn trả về chính xác chuỗi JSON có format sau:
```json
{
  "code": "import plotly.express as px\\nif 'Năm' in df.columns: df['Năm'] = df['Năm'].astype(str)\\nfig = px.bar(df, x='...', y='...', color='...', color_discrete_sequence=px.colors.colorbrewer.Paired, ...)\\nfig.update_layout(margin=dict(l=20, r=20, t=60, b=20), legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))",
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
                        return None, "Lỗi phân tích cú pháp JSON từ LLM.", ""
                else:
                    response_json = response
                    
                code_str = response_json.get("code", "")
                overview = response_json.get("overview", "")
                
                # --- VALIDATE CODE VẼ BIỂU ĐỒ (POST-PROCESSING CORRECTION) ---
                import re
                
                # Kiểm tra lỗi logic map trục X là 'Năm' khi dữ liệu chỉ có 1 năm duy nhất
                if "Năm" in columns and df["Năm"].nunique() <= 1 and "xu hướng" not in user_question.lower():
                    if "x='Năm'" in code_str or 'x="Năm"' in code_str:
                        if attempt < max_retries - 1:
                            current_prompt += "\n\nLỖI LOGIC LẦN TRƯỚC: Dữ liệu chỉ có 1 năm duy nhất, TUYỆT ĐỐI KHÔNG gán x='Năm' hoặc x=\"Năm\". Hãy chọn cột phân loại chính (như Huyện, Xã, Nhóm dân tộc, Giới tính, Chỉ số...) làm trục x!"
                            continue
                
                # 1. Kiểm tra biểu đồ xu hướng và tự động sort theo năm nếu LLM bỏ sót
                if "xu hướng" in user_question.lower() and "px.line" not in code_str:
                    if attempt < max_retries - 1:
                        current_prompt += "\n\nLỖI LẦN TRƯỚC: Yêu cầu xem 'xu hướng' nhưng bạn không sinh biểu đồ đường (px.line). Vui lòng dùng px.line."
                        continue
                    return None, "Lỗi logic: Người dùng yêu cầu xem 'xu hướng' nhưng LLM không sinh biểu đồ đường (px.line).", ""
                
                if "px.line" in code_str and "Năm" in columns and "sort_values" not in code_str:
                    # Chèn sort_values ngay trước px.line
                    code_str = code_str.replace("fig = px.line(", "df = df.sort_values('Năm')\nfig = px.line(")

                # Sửa lỗi: Nếu LLM nhét text_auto=True vào update_traces (gây lỗi Plotly), ta tự động bóc ra và sửa
                if "update_traces" in code_str and "text_auto=True" in code_str:
                    code_str = code_str.replace("text_auto=True", "")
                    if "px.bar(" in code_str and "text_auto" not in code_str:
                        code_str = re.sub(r"(px\.bar\([^,]+,)", r"\1 text_auto='.2s',", code_str)
                
                # 2. Đảm bảo luôn sử dụng bảng màu 'Paired' thay vì mặc định (Tránh lỗi positional argument)
                if "color_discrete_sequence" not in code_str and "px." in code_str:
                    code_str = re.sub(r"(px\.(?:bar|pie|line|scatter)\([^,]+,)", r"\1 color_discrete_sequence=px.colors.colorbrewer.Paired,", code_str)
                elif "px.colors.colorbrewer.Paired" not in code_str:
                    code_str = re.sub(r"color_discrete_sequence=[^,)]+", "color_discrete_sequence=px.colors.colorbrewer.Paired", code_str)
                
                # 3. Đảm bảo trục X của biểu đồ đường được format chuẩn và nhãn dữ liệu, và cột cho biểu đồ bar
                if "px.line" in code_str:
                    if "dtick=1" not in code_str:
                        code_str += "\nfig.update_xaxes(tickformat='d', dtick=1)"
                    if "markers=" not in code_str:
                        code_str = re.sub(r"(px\.line\([^,]+,)", r"\1 markers=True,", code_str)
                    if "texttemplate" not in code_str:
                        code_str += "\nfig.update_traces(mode='lines+markers+text', texttemplate='%{y:,.0f}', textposition='top center')"
                
                if "px.bar" in code_str:
                    # Tự động gán text_auto để hiển thị nhãn chuẩn xác cho cả bar đơn và bar ghép (tránh lỗi NaN do melt)
                    if "texttemplate" not in code_str and "text_auto" not in code_str:
                        code_str = re.sub(r"(px\.bar\([^,]+,)", r"\1 text_auto='.2s',", code_str)
                            
                if "px.pie" in code_str:
                    if "textinfo" not in code_str:
                        code_str += "\nfig.update_traces(textposition='auto', textinfo='percent+label')"
                        
                # 4. Tự động thêm update_layout chuẩn Premium UI (Legend ngang trên cùng, Margin) nếu chưa có
                if "orientation='h'" not in code_str and 'orientation="h"' not in code_str and "update_layout" not in code_str:
                    code_str += "\nfig.update_layout(margin=dict(l=20, r=20, t=60, b=20), legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))"
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
                        
                    return fig, overview, code_str
                except Exception as e:
                    import traceback
                    error_msg = f"Lỗi khi thực thi mã sinh biểu đồ: {e}"
                    print(f"[AgentChartGenerator] {error_msg}")
                    if attempt < max_retries - 1:
                        # Feed the error back to the LLM to self-correct
                        current_prompt += f"\n\nLỖI TRONG LẦN CHẠY CODE TRƯỚC: {e}. Vui lòng sửa lại mã Python để không bị lỗi này. CHÚ Ý: KHÔNG ĐƯỢC để `text_auto=True` bên trong hàm `fig.update_traces()`, tham số đó chỉ dành cho hàm `px.bar()`. Nhớ sắp xếp dữ liệu df = df.sort_values('Năm') nếu dùng px.line."
                        continue
                    else:
                        return None, f"Tôi đã gặp lỗi khi cố gắng vẽ biểu đồ: {e}", ""
                    
        except Exception as e:
            return None, f"Lỗi gọi LLM khi sinh biểu đồ: {e}", ""
