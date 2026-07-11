# -*- coding: utf-8 -*-
from __future__ import annotations
import sys
import os
import time
import pandas as pd
import json
from pathlib import Path
from typing import Any

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
        
        # Làm sạch và chuẩn bị DataFrame (thay thế NaN/Null, loại bỏ cột 'Năm' nếu cần)
        from src.query_control.agentic.utils import prepare_chart_data
        df = prepare_chart_data(df, user_question)
            
        # Extract data summary for LLM
        columns = list(df.columns)
        dtypes = df.dtypes.astype(str).to_dict()
        sample_data = df.head(5).to_dict(orient="records")
        
        system_prompt = """Bạn là trợ lý ảo phân tích dữ liệu chuyên sâu và trực quan hoá dữ liệu bằng biểu đồ.
Nhiệm vụ của bạn là:
1. Đọc mô tả cấu trúc DataFrame (columns, dtypes) và dữ liệu mẫu.
2. Dựa vào câu hỏi của người dùng, sinh ra MỘT đoạn mã Python sử dụng `plotly.express` (as `px`) hoặc `plotly.graph_objects` (as `go`) để vẽ biểu đồ phù hợp nhất.
3. Sinh ra một đoạn văn bản 'overview' NHẬN XÉT TRỰC TIẾP VÀO SỐ LIỆU của biểu đồ. Yêu cầu bắt buộc cho đoạn văn nhận xét:
   - BẮT BUỘC đọc cột 'Năm' (nếu có) và gọi tên chính xác MỐC THỜI GIAN (ví dụ: "Trong năm 2024...", "Xuyên suốt năm 2023 và 2024...") ngay ở đầu câu để tránh nhầm lẫn.
   - BẮT BUỘC gọi tên (chỉ ra) đối tượng cao nhất/thấp nhất nếu có so sánh.
   - PHẢI CÓ TÍNH PHÂN TÍCH: Hãy nhận xét thêm về xu hướng (nếu có dữ liệu của nhiều năm) hoặc sự chênh lệch (gap) giữa đối tượng cao nhất và phần còn lại.
   - TÍNH TOÀN DIỆN [RẤT QUAN TRỌNG]: BẠN BẮT BUỘC PHẢI liệt kê ĐẦY ĐỦ tên và số liệu của TẤT CẢ các dòng trong bảng dữ liệu cung cấp (tuyệt đối không được bỏ sót dòng nào, không dùng dấu `...` hoặc `v.v.`). Bạn CÓ THỂ dùng gạch đầu dòng (bullet points) để liệt kê cho rõ ràng nếu có nhiều dòng dữ liệu. Khối lượng chữ không giới hạn, miễn là liệt kê ĐỦ 100% dữ liệu.
   - KHÔNG SUY ĐOÁN (NO ESTIMATION): Chỉ sử dụng dữ liệu được cung cấp, tuyệt đối không tự bịa ra số liệu.
   - Tuyệt đối KHÔNG viết câu giới thiệu sáo rỗng (ví dụ: "Biểu đồ này thể hiện...").

YÊU CẦU CHO MÃ PYTHON:
- Đầu vào là biến `df` (pandas DataFrame). Không tự định nghĩa `df` hay đọc file. Bắt buộc kiểm tra và chỉ dùng đúng các cột có sẵn trong mô tả Dữ liệu.
- `fig = px.bar(...)` hoặc `fig = go.Figure(...)`. Không được dùng `fig.show()`. Biến cuối cùng phải là `fig`.
- QUY TẮC CÚ PHÁP PLOTLY [CRITICAL - CHỐNG LỖI POSITIONAL ARGUMENT]: Khi gọi các hàm Plotly (như px.bar, px.line, px.pie...), sau tham số đầu tiên là df, BẮT BUỘC bạn phải gọi bằng Keyword Arguments rõ ràng (ví dụ: px.bar(df, x='Huyện', y='Số hộ nghèo', color='Huyện')). TUYỆT ĐỐI KHÔNG được truyền tham số theo vị trí không có tên (ví dụ sai: px.bar(df, 'Huyện', 'Số hộ nghèo')).
- ĐẶC BIỆT QUAN TRỌNG: BẮT BUỘC phải đọc năm từ dữ liệu và đưa vào tham số `title` của biểu đồ để người dùng biết biểu đồ này dành cho năm nào (Ví dụ: `title='Tỷ lệ hộ nghèo theo từng Huyện năm 2024'`).
- ĐỐI VỚI YÊU CẦU SO SÁNH NHẤT, TOP, SO SÁNH QUY MÔ: BẮT BUỘC dùng biểu đồ cột (Bar chart). BẮT BUỘC gán tham số `color` (vd `color='Xã'` hoặc `color='Huyện'` hoặc `color='Chỉ số'`) để các cột có màu sắc khác nhau, TUYỆT ĐỐI không để biểu đồ chỉ có 1 màu duy nhất! QUY TẮC CHỌN TRỤC X/Y: Trục x (hoặc trục y nếu biểu đồ ngang) BẮT BUỘC phải là cột danh mục phân loại chính (ví dụ: 'Huyện', 'Xã', 'Giới tính', 'Nhóm dân tộc', 'Chỉ số', 'Nguyên nhân'...). NẾU dữ liệu chỉ có số liệu của MỘT NĂM DUY NHẤT (ví dụ cột 'Năm' chỉ toàn giá trị 2024), TUYỆT ĐỐI KHÔNG ĐƯỢC gán `x='Năm'` hoặc `color='Năm'` vì sẽ làm biểu đồ bị gộp sai! CHỈ gán `x='Năm'` khi câu hỏi yêu cầu xem XU HƯỚNG qua nhiều năm. NẾU dữ liệu có chứa NHIỀU NĂM, BẮT BUỘC thêm `barmode='group'` và `color='Năm'` để hiển thị các năm đứng cạnh nhau. LƯU Ý QUAN TRỌNG VỀ ĐẢO CHIỀU TRỤC VÀ SẮP XẾP (INSIGHT RÕ RÀNG): NẾU danh sách tên danh mục (như Xã, Huyện, Nguyên nhân) có từ 5 ĐỐI TƯỢNG TRỞ LÊN hoặc có nhiều cột số liệu so sánh, bạn BẮT BUỘC dùng biểu đồ thanh ngang (`orientation='h'`, `y='Danh Mục'`, `x='CộtSốLiệu'`) để tên địa phương/chỉ số không bị đè chữ hay cắt xén; ngược lại nếu dưới 5 đối tượng dùng thanh đứng (`x='Danh Mục'`, `y='CộtSốLiệu'`). ĐỊNH DẠNG SỐ: Bắt buộc định dạng nhãn có dấu phẩy phân cách hàng nghìn bằng `text_auto='.2s'` hoặc `texttemplate='%{y:,.0f}'` (hoặc `%{x:,.0f}` nếu thanh ngang).
- ĐỐI VỚI YÊU CẦU SO SÁNH QUA CÁC NĂM (nhưng không nhắc đến "xu hướng"): BẮT BUỘC dùng biểu đồ cột đứng (`px.bar`) với trục `x` là cột Danh Mục, `y` là cột Số Liệu, thuộc tính `barmode='group'` và BẮT BUỘC sử dụng tham số `color='Năm'` để phân tách các năm thành các cột đứng cạnh nhau. TUYỆT ĐỐI KHÔNG gán `color` bằng cột Danh Mục (như `Xã` hay `Huyện`) vì nó sẽ làm gộp dữ liệu các năm lại với nhau thành 1 cột.
- QUY TẮC TÁCH BIỂU ĐỒ KHI CÓ NHIỀU NĂM (CRITICAL): NẾU DataFrame có cột 'Năm' chứa từ 2 năm trở lên (ví dụ có cả năm 2023 và 2024) và câu hỏi KHÔNG yêu cầu vẽ biểu đồ đường xu hướng (line chart): Bạn BẮT BUỘC phải dùng tham số `facet_col='Năm'` (hoặc `facet_row='Năm'` nếu là biểu đồ ngang `orientation='h'`) trong hàm `px.bar` / `px.pie` để tách rõ ràng số liệu của từng năm thành các biểu đồ con độc lập đặt cạnh nhau (Ví dụ: `px.bar(df, x='Huyện', y=['Số hộ nghèo', 'Số hộ cận nghèo'], facet_col='Năm', barmode='group')`). TUYỆT ĐỐI KHÔNG vẽ gộp chung các năm vào 1 biểu đồ đơn mà không có facet hoặc color phân biệt năm vì sẽ gây nhầm lẫn số liệu!
- ĐỐI VỚI YÊU CẦU "CƠ CẤU", "TỶ LỆ", "TỶ TRỌNG": LƯU Ý QUAN TRỌNG: NẾU DataFrame có từ 2 cột số liệu trở lên (ví dụ có cả cột 'Số hộ nghèo' và 'Số hộ cận nghèo' phân theo 'Huyện'), TUYỆT ĐỐI KHÔNG DÙNG BIỂU ĐỒ TRÒN (`px.pie`) vì biểu đồ tròn không thể hiện được 2 cột số liệu cùng lúc. Trong trường hợp này, BẮT BUỘC phải dùng biểu đồ cột ghép (`px.bar` với `y=['Số hộ nghèo', 'Số hộ cận nghèo']`, `barmode='group'`) hoặc làm phẳng dữ liệu rồi vẽ biểu đồ cột. CHỈ DÙNG BIỂU ĐỒ TRÒN (`px.pie`) khi chỉ có ĐÚNG 1 cột số liệu cần chia tỷ lệ theo 1 cột phân loại (ví dụ: tỷ lệ Nam/Nữ). Khi dùng `px.pie`, bắt buộc gán `values='CộtSốLiệu'` và `names='CộtPhânLoại'`, đồng thời thêm `fig.update_traces(textposition='auto', textinfo='percent+label')`. KHÔNG gán tham số `color` trừ khi dùng color map.
- ĐỐI VỚI DATAFRAME CÓ NHIỀU CỘT SỐ LIỆU ĐỂ SO SÁNH (ví dụ: đếm 12 chỉ số thiếu hụt khác nhau, hoặc có 2 cột Số hộ nghèo và Số hộ cận nghèo): TUYỆT ĐỐI KHÔNG truyền trực tiếp DataFrame vào `px.bar` để tránh lỗi xếp chồng (stacked) sai lệch. Bạn BẮT BUỘC phải làm phẳng dữ liệu (Melt) trước khi vẽ bằng lệnh: `df_melt = df.melt(id_vars=['Tên_Cột_Danh_Mục_Như_Huyện_Hoặc_Xã'], var_name='Chỉ số', value_name='Giá trị')`. LƯU Ý QUAN TRỌNG VỀ CỘT NĂM: Nếu DataFrame có từ 2 năm trở lên (ví dụ có cả 2023 và 2024), bạn BẮT BUỘC PHẢI đưa cột 'Năm' vào `id_vars` khi melt (ví dụ: `id_vars=['Huyện', 'Năm']`), NẾU KHÔNG CỘT 'Năm' SẼ BỊ MẤT KHI VẼ! Nếu chỉ có 1 năm duy nhất thì không đưa 'Năm' vào `id_vars`. Sau đó, dùng `df_melt` để vẽ biểu đồ cột (`px.bar` với `x='Tên_Cột_Danh_Mục', y='Giá trị', color='Chỉ số', facet_col='Năm', barmode='group')`).
- ĐỐI VỚI YÊU CẦU "XU HƯỚNG" (TREND): BẮT BUỘC dùng biểu đồ đường (Line chart) bằng hàm `px.line`. QUY TẮC SẮP XẾP THỜI GIAN (CRITICAL): Trước khi gọi `px.line`, bạn BẮT BUỘC phải sắp xếp dữ liệu theo thời gian bằng lệnh `df = df.sort_values('Năm')` để đường không bị vẽ nhảy zig-zag! Trục X BẮT BUỘC phải là thời gian (`x='Năm'`). LỖI LOGIC ĐẶC BIỆT CHÚ Ý: Nếu dữ liệu có nhiều cột số liệu cần so sánh, BẮT BUỘC phải truyền MẢNG danh sách các cột đó vào trục Y (ví dụ `y=['Số hộ nghèo', 'Số hộ cận nghèo']`) để vẽ đủ tất cả các đường, KHÔNG ĐƯỢC bỏ sót! Sử dụng tham số `color` để phân biệt đối tượng (ví dụ `color='Huyện'`). Bắt buộc thêm `markers=True`, `symbol='Huyện'` (hoặc `symbol='variable'`), và `line_dash='variable'` (hoặc `line_dash='Huyện'`) vào hàm `px.line` để tạo đa dạng nét đứt, nét liền, và các điểm vuông/tròn/tam giác khác nhau. Bắt buộc gọi `fig.update_traces(mode='lines+markers+text', texttemplate='%{y:,.0f}', textposition='top center')`. Cuối cùng format trục X (`fig.update_xaxes(tickformat='d', dtick=1)`). TUYỆT ĐỐI KHÔNG dùng biểu đồ cột cho yêu cầu "xu hướng".
- MÀU SẮC & BỐ CỤC UI PREMIUM: BẮT BUỘC sử dụng palette màu 'Paired'. Nếu cột bạn gán vào tham số `color` đang là số nguyên (ví dụ: `color='Năm'`), bạn BẮT BUỘC phải ép kiểu cột đó sang chuỗi trước khi vẽ bằng cách thêm `df['Năm'] = df['Năm'].astype(str)`. Bắt buộc thêm tham số `color_discrete_sequence=px.colors.colorbrewer.Paired` vào MỌI hàm vẽ. ĐỂ TỐI ƯU HÓA KHÔNG GIAN VÀ TRỰC QUAN (PREMIUM UI): BẮT BUỘC thêm dòng lệnh `fig.update_layout(margin=dict(l=20, r=20, t=60, b=20), legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))` vào TẤT CẢ các biểu đồ để bảng chú thích nằm ngang ở phía trên cùng, tránh bị xén chữ và mở rộng tối đa không gian biểu đồ.
- TIÊU ĐỀ (TITLE) VÀ NHÃN TRỤC: Title, nhãn trục X, Y và Legend phải rõ ràng, ưu tiên tiếng Việt. ĐẶC BIỆT QUAN TRỌNG: Nếu câu hỏi có nhắc đến TÊN RIÊNG của các địa phương (ví dụ: "Thành phố Gia Nghĩa", "Huyện Tuy Đức"), BẮT BUỘC phải nhúng các tên riêng này vào Tiêu đề của biểu đồ để minh bạch thông tin.
- BẮT BUỘC phải dùng template JSON: Bạn trả về chính xác chuỗi JSON có format sau:
```json
{
  "code": "import plotly.express as px\nif 'Năm' in df.columns: df['Năm'] = df['Năm'].astype(str)\nfig = px.bar(df, x='...', y='...', color='...', color_discrete_sequence=px.colors.colorbrewer.Paired, ...)\nfig.update_layout(margin=dict(l=20, r=20, t=60, b=20), legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))",
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
                    max_tokens=3000,
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
                
                def safe_inject_kwarg(code_text: str, func_prefix: str, kwarg_text: str) -> str:
                    """Tiêm từ khóa keyword argument an toàn vào trước dấu ngoặc đóng của lời gọi hàm Plotly (chống lỗi positional vs keyword argument)."""
                    idx = code_text.find(func_prefix + "(")
                    if idx == -1:
                        return code_text
                    start_paren = idx + len(func_prefix)
                    depth = 0
                    in_sq = False
                    in_dq = False
                    esc = False
                    for i in range(start_paren, len(code_text)):
                        ch = code_text[i]
                        if esc:
                            esc = False
                            continue
                        if ch == '\\':
                            esc = True
                            continue
                        if ch == "'" and not in_dq:
                            in_sq = not in_sq
                            continue
                        if ch == '"' and not in_sq:
                            in_dq = not in_dq
                            continue
                        if not in_sq and not in_dq:
                            if ch in ('(', '[', '{'):
                                depth += 1
                            elif ch in (')', ']', '}'):
                                depth -= 1
                                if depth == 0 and ch == ')':
                                    kw_name = kwarg_text.split("=")[0].strip()
                                    func_body = code_text[start_paren+1:i]
                                    if f"{kw_name}=" not in func_body and f"{kw_name} =" not in func_body:
                                        return code_text[:i] + ", " + kwarg_text + code_text[i:]
                                    return code_text
                    return code_text
                
                # Kiểm tra lỗi logic map trục X là 'Năm' khi dữ liệu chỉ có 1 năm duy nhất
                if "Năm" in columns and df["Năm"].nunique() <= 1 and "xu hướng" not in user_question.lower():
                    if "x='Năm'" in code_str or 'x="Năm"' in code_str:
                        if attempt < max_retries - 1:
                            current_prompt += "\n\nLỖI LOGIC LẦN TRƯỚC: Dữ liệu chỉ có 1 năm duy nhất, TUYỆT ĐỐI KHÔNG gán x='Năm' hoặc x=\"Năm\". Hãy chọn cột phân loại chính (như Huyện, Xã, Nhóm dân tộc, Giới tính, Chỉ số...) làm trục x!"
                            continue
                    # Tự động gỡ bỏ facet_col/facet_row hoặc chuyển đổi color='Năm' nếu LLM sinh sai khi chỉ có 1 năm
                    if "facet_col='Năm'" in code_str or 'facet_col="Năm"' in code_str or "facet_row='Năm'" in code_str or 'facet_row="Năm"' in code_str:
                        code_str = re.sub(r",?\s*facet_(col|row)=['\"]Năm['\"]", "", code_str)
                    if "color='Năm'" in code_str or 'color="Năm"' in code_str:
                        cat_cols = [c for c in columns if c != "Năm" and not pd.api.types.is_numeric_dtype(df[c])]
                        rep_col = cat_cols[0] if cat_cols else columns[0]
                        code_str = re.sub(r"color=['\"]Năm['\"]", f"color='{rep_col}'", code_str)
                
                # 1. Kiểm tra biểu đồ xu hướng và tự động sort theo năm nếu LLM bỏ sót
                if "xu hướng" in user_question.lower() and "px.line" not in code_str:
                    if attempt < max_retries - 1:
                        current_prompt += "\n\nLỖI LẦN TRƯỚC: Yêu cầu xem 'xu hướng' nhưng bạn không sinh biểu đồ đường (px.line). Vui lòng dùng px.line."
                        continue
                    return None, "Lỗi logic: Người dùng yêu cầu xem 'xu hướng' nhưng LLM không sinh biểu đồ đường (px.line).", ""
                
                if "px.line" in code_str and "Năm" in columns and "sort_values" not in code_str:
                    code_str = code_str.replace("fig = px.line(", "df = df.sort_values('Năm')\nfig = px.line(")

                # Sửa lỗi: Nếu LLM nhét text_auto=True vào update_traces (gây lỗi Plotly), ta tự động bóc ra và sửa
                if "update_traces" in code_str and "text_auto=True" in code_str:
                    code_str = code_str.replace("text_auto=True", "")
                    if "px.bar(" in code_str and "text_auto" not in code_str:
                        code_str = safe_inject_kwarg(code_str, "px.bar", "text_auto='.2s'")
                
                # Safeguard: Nếu có .melt và DataFrame có nhiều năm, đảm bảo 'Năm' có trong id_vars
                if "Năm" in columns and df["Năm"].nunique() > 1 and ".melt(" in code_str:
                    def add_nam_to_id_vars(match):
                        content = match.group(1)
                        if "'Năm'" not in content and '"Năm"' not in content:
                            return f"id_vars=[{content}, 'Năm']"
                        return match.group(0)
                    code_str = re.sub(r"id_vars=\[([^\]]+)\]", add_nam_to_id_vars, code_str)

                # 2. Đảm bảo sử dụng palette 'Paired'
                if "color_discrete_sequence" not in code_str and "px." in code_str:
                    for prefix in ["px.bar", "px.line", "px.pie", "px.scatter", "px.histogram", "px.box", "px.treemap"]:
                        if prefix in code_str:
                            code_str = safe_inject_kwarg(code_str, prefix, "color_discrete_sequence=px.colors.colorbrewer.Paired")
                            break
                
                # 3. Tự động thêm markers và format trục X cho biểu đồ đường (Line chart)
                if "px.line" in code_str:
                    if "dtick=1" not in code_str:
                        code_str += "\nfig.update_xaxes(tickformat='d', dtick=1)"
                    if "markers=" not in code_str:
                        code_str = safe_inject_kwarg(code_str, "px.line", "markers=True")
                    if "texttemplate" not in code_str:
                        code_str += "\nfig.update_traces(mode='lines+markers+text', texttemplate='%{y:,.0f}', textposition='top center')"
                
                if "px.bar" in code_str:
                    # Tự động gán text_auto để hiển thị nhãn chuẩn xác cho cả bar đơn và bar ghép (tránh lỗi NaN do melt)
                    if "texttemplate" not in code_str and "text_auto" not in code_str:
                        code_str = safe_inject_kwarg(code_str, "px.bar", "text_auto='.2s'")
                    # Tự động thêm facet_col='Năm' hoặc facet_row='Năm' nếu có nhiều năm mà LLM quên chia tách (tránh vẽ chồng lấn/cộng gộp năm)
                    if "Năm" in columns and df["Năm"].nunique() > 1 and "facet_col" not in code_str and "facet_row" not in code_str and "color='Năm'" not in code_str and 'color="Năm"' not in code_str and "xu hướng" not in user_question.lower():
                        if "orientation='h'" in code_str or 'orientation="h"' in code_str:
                            code_str = safe_inject_kwarg(code_str, "px.bar", "facet_row='Năm'")
                        else:
                            code_str = safe_inject_kwarg(code_str, "px.bar", "facet_col='Năm'")
                            
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
                    
                    # --- POST-PROCESSING: Tự động sắp xếp và tối ưu UI/Insight cho biểu đồ Plotly ---
                    if fig is not None:
                        try:
                            import plotly.graph_objects as go
                            fig.update_layout(
                                margin=dict(l=20, r=30, t=70, b=30),
                                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                                font=dict(family="Arial, sans-serif", size=13)
                            )
                            for trace in fig.data:
                                if isinstance(trace, go.Bar):
                                    if not getattr(trace, 'textposition', None):
                                        trace.textposition = 'outside'
                            
                            is_horizontal = any(getattr(trace, 'orientation', 'v') == 'h' for trace in fig.data if isinstance(trace, go.Bar))
                            if is_horizontal:
                                fig.update_layout(yaxis=dict(categoryorder='total ascending'))
                            else:
                                fig.update_layout(xaxis=dict(categoryorder='total descending', tickangle=-30 if len(df) > 5 else 0))
                        except Exception as opt_err:
                            print(f"[AgentChartGenerator Layout Optimization Warning] {opt_err}")
                    
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
                        return None, f"Hệ thống không thể vẽ biểu đồ do lỗi kỹ thuật (thường do yêu cầu chưa rõ ràng hoặc thiếu tiêu chí so sánh cụ thể). Bạn có thể cung cấp thêm thông tin (như phân tích theo huyện, năm, hoặc nguyên nhân) để hệ thống vẽ chính xác hơn nhé! Lỗi nội bộ: {e}", ""
                    
        except Exception as e:
            return None, f"Lỗi gọi LLM khi sinh biểu đồ: {e}", ""
