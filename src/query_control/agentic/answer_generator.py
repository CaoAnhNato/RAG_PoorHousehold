# -*- coding: utf-8 -*-
from __future__ import annotations
import sys
import pandas as pd
from pathlib import Path
from typing import Generator, Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from src.query_control.llm_helper import call_llm, stream_llm

class AnswerGenerator:
    """Agent tổng hợp kết quả thành câu trả lời tự nhiên, hỗ trợ streaming chunk thô."""
    
    def generate(self, user_question: str, df: pd.DataFrame | None, stream: bool = False) -> str | Generator[str, None, None]:
        if df is None or df.empty:
            msg = "Tôi không tìm thấy dữ liệu phù hợp hoặc hệ thống gặp lỗi khi truy xuất dữ liệu."
            if stream:
                return (chunk for chunk in [msg])
            return msg
            
        # Xử lý nhanh bằng Heuristic cho DataFrame 1 dòng (tiết kiệm ~3.5s LLM latency)
        if not stream and df.shape[0] == 1 and df.shape[1] <= 4:
            row = df.iloc[0]
            cols_desc = []
            year_str = "năm 2024"
            for col in df.columns:
                col_lower = str(col).lower()
                if "năm" in col_lower or "year" in col_lower:
                    year_str = f"năm {row[col]}"
                else:
                    val = row[col]
                    if isinstance(val, float):
                        val_str = f"{val:,.2f}".rstrip('0').rstrip('.')
                    elif isinstance(val, int):
                        val_str = f"{val:,}"
                    else:
                        val_str = str(val)
                    cols_desc.append(f"{col.lower()} đạt {val_str}")
            
            summary_part = ", ".join(cols_desc) if cols_desc else "dữ liệu đã được trích xuất"
            return f"Trong {year_str}, theo kết quả rà soát từ cơ sở dữ liệu hộ nghèo và cận nghèo tỉnh Đắk Nông, {summary_part}. Đây là số liệu thống kê chính xác theo tiêu chí truy vấn của bạn."
            
        # Limit rows to avoid token overflow
        data_str = df.head(50).to_csv(index=False)
        
        # Phân nhánh chỉ dẫn trong System Prompt theo độ dài bảng dữ liệu
        if df.shape[0] <= 10:
            listing_instruction = "- TÍNH TOÀN DIỆN [RẤT QUAN TRỌNG]: BẠN BẮT BUỘC PHẢI liệt kê ĐẦY ĐỦ tên và số liệu của TẤT CẢ các dòng trong bảng dữ liệu cung cấp (tuyệt đối không được bỏ sót dòng nào, không dùng dấu `...` hoặc `v.v.`). Nếu dữ liệu có 8 huyện, phải nhắc đủ tên và số liệu của 8 huyện đó."
        else:
            listing_instruction = "- NHẬN XÉT TỔNG QUAN VÀ ĐIỂM NỔI BẬT: Bảng dữ liệu chi tiết đã được hiển thị đầy đủ bên dưới cho người dùng. Do đó, bạn KHÔNG CẦN VÀ KHÔNG ĐƯỢC chép lại từng dòng chi tiết của toàn bộ bảng. Thay vào đó, hãy tập trung phân tích tổng quan, chỉ ra Top cao nhất/thấp nhất, mức độ chênh lệch giữa các nhóm, phân bố xu hướng chung hoặc những điểm bất thường đáng chú ý."

        system_prompt = f"""Bạn là trợ lý ảo phân tích dữ liệu chuyên nghiệp.
Nhiệm vụ của bạn là dựa vào kết quả dữ liệu được cung cấp để trả lời câu hỏi của người dùng một cách chính xác, tự nhiên và CÓ TÍNH PHÂN TÍCH. Yêu cầu bắt buộc:
- BẮT BUỘC đề cập đến MỐC THỜI GIAN (ví dụ: "Trong năm 2024...", "Tính đến năm 2023...") ngay ở đầu câu trả lời dựa trên cột Năm (nếu có).
- KHÔNG CHỈ BÁO CÁO SỐ LIỆU ĐƠN THUẦN: Hãy mở rộng câu trả lời bằng cách so sánh sự chênh lệch (gap) giữa đối tượng đứng nhất và phần còn lại, nhận xét về khoảng cách, tỷ trọng, hoặc xu hướng (nếu có dữ liệu qua các năm).
{listing_instruction}
- KHÔNG SUY ĐOÁN (NO ESTIMATION): Chỉ sử dụng dữ liệu được cung cấp, tuyệt đối không tự bịa ra số liệu.
- Không cần đề cập đến việc bạn lấy dữ liệu từ đâu hay bảng biểu nào, hãy trả lời thẳng vào câu hỏi một cách mượt mà và chuyên nghiệp.
- Nếu dữ liệu cần liệt kê các điểm chính, hãy trình bày dạng gạch đầu dòng rõ ràng.
"""
        user_prompt = f"Câu hỏi: {user_question}\n\nKết quả dữ liệu (CSV format, max 50 rows):\n{data_str}\n\nHãy sinh câu trả lời tự nhiên dựa trên dữ liệu trên."
        
        if stream:
            return stream_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.1,
                max_tokens=180
            )
        else:
            answer = call_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.1,
                max_tokens=180,
                model="gpt-4o-mini",
                response_json=False
            )
            return answer.strip()
