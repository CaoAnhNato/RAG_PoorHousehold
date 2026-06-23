# -*- coding: utf-8 -*-
from __future__ import annotations
import sys
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))
from src.query_control.llm_helper import call_llm

class AnswerGenerator:
    """Agent tổng hợp kết quả thành câu trả lời tự nhiên."""
    def generate(self, user_question: str, df: pd.DataFrame | None) -> str:
        if df is None or df.empty:
            return "Tôi không tìm thấy dữ liệu phù hợp hoặc hệ thống gặp lỗi khi truy xuất dữ liệu."
            
        # Bypass LLM if the result is a large table (> 5 rows)
        if df.shape[0] > 5:
            from src.query_control.agentic.utils import normalize_columns
            return normalize_columns(df)
            
        # Limit rows to avoid token overflow
        data_str = df.head(50).to_csv(index=False)
        
        system_prompt = """Bạn là trợ lý ảo phân tích dữ liệu chuyên nghiệp.
Nhiệm vụ của bạn là dựa vào kết quả dữ liệu được cung cấp để trả lời câu hỏi của người dùng một cách chính xác, ngắn gọn và tự nhiên nhất.
Không cần đề cập đến việc bạn lấy dữ liệu từ đâu hay bảng biểu nào, hãy trả lời thẳng vào câu hỏi.
Nếu dữ liệu là danh sách (liệt kê), hãy trình bày dạng gạch đầu dòng rõ ràng.
"""
        user_prompt = f"Câu hỏi: {user_question}\n\nKết quả dữ liệu (CSV format, max 50 rows):\n{data_str}\n\nHãy sinh câu trả lời tự nhiên dựa trên dữ liệu trên."
        
        answer = call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3,
            max_tokens=800,
            response_json=False
        )
        return answer.strip()
