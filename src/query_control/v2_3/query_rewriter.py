# -*- coding: utf-8 -*-
import json
from src.query_control.llm_helper import call_llm, clean_json_response

class QueryRewriter:
    def __init__(self):
        self.system_prompt = """
        Bạn là một chuyên gia phân tích truy vấn dữ liệu.
        Nhiệm vụ của bạn là phân rã và cấu trúc hóa câu hỏi phức tạp của người dùng thành các thành phần dễ xử lý hơn cho hệ thống SQL.
        Đặc biệt lưu ý các câu hỏi chứa nhiều thực thể cùng loại (ví dụ: nhiều huyện, nhiều năm).
        
        Trả về kết quả DƯỚI DẠNG JSON với cấu trúc:
        {
            "rewritten_query": "Câu hỏi đã được viết lại cho rõ ràng và dễ hiểu",
            "extracted_entities": {
                "locations": ["danh sách địa danh, xã, huyện"],
                "time": ["năm hoặc khoảng thời gian"],
                "metrics": ["các chỉ số cần tính, ví dụ: số lượng, tỷ lệ"],
                "filters": ["các điều kiện lọc khác, ví dụ: hộ nghèo, chủ hộ là nữ"]
            }
        }
        """

    def rewrite(self, query: str) -> dict:
        """
        Viết lại câu hỏi và trích xuất thực thể thô ban đầu.
        """
        user_prompt = f"Câu hỏi gốc: {query}"
        
        try:
            # Sử dụng LLM (đã config gpt-4o-mini trong .env)
            response = call_llm(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                temperature=0.1,
                response_json=True
            )
            return clean_json_response(response)
        except Exception as e:
            # Fallback nếu LLM thất bại
            return {
                "rewritten_query": query,
                "extracted_entities": {
                    "locations": [],
                    "time": [],
                    "metrics": [],
                    "filters": []
                },
                "error": str(e)
            }
