# -*- coding: utf-8 -*-
from __future__ import annotations
import json
import re
from typing import List
from src.query_control.llm_helper import call_llm

class QueryDecomposer:
    """
    Phân rã câu hỏi kép/đa ý thành danh sách các Sub-queries độc lập có đầy đủ ngữ cảnh.
    Ví dụ: 'Thống kê các dân tộc đang có ở Tuy Đức 2024 ? Có bao nhiêu hộ nghèo trong đây là nữ ?'
    -> ['Thống kê các dân tộc đang có ở Tuy Đức 2024', 'Có bao nhiêu hộ nghèo là nữ ở Tuy Đức năm 2024']
    """
    def __init__(self):
        self.system_prompt = """Bạn là chuyên gia phân rã câu hỏi nghiệp vụ (Sub-Query Decomposer) và giải quyết đồng tham chiếu (Coreference Resolution).
Nhiệm vụ của bạn là:
1. Nếu câu hỏi có từ 2 ý/câu hỏi nghiệp vụ độc lập rõ ràng trở lên (thường ngăn cách bởi dấu "?", dấu ";", hoặc từ nối như "Đồng thời", "Và cho biết"):
   - Hãy tách thành danh sách các câu hỏi con.
   - TUYỆT ĐỐI KHÔNG tách các câu mang tính chất yêu cầu định dạng, hiển thị, vẽ biểu đồ, HOẶC yêu cầu so sánh/gộp nhiều đối tượng/địa danh trên cùng một biểu đồ (như "Hiển thị biểu đồ... của thành phố Gia Nghĩa và huyện Tuy Đức", "so sánh giữa X và Y", "xu hướng của A và B qua các năm", "hiển thị giúp tôi dễ nhìn") thành các câu hỏi con riêng biệt! Khi người dùng yêu cầu biểu đồ hoặc so sánh nhiều địa danh (nối bởi 'và', 'hoặc', 'với', 'giữa'), BẮT BUỘC giữ nguyên thành 1 câu truy vấn duy nhất!
2. PHẢI giải quyết đồng tham chiếu (Coreference Resolution): Nếu câu hỏi hiện tại (hoặc ý con) có sử dụng các đại từ như "trong đây", "ở đó", "xã đó", "huyện này", "những hộ này", "còn lại", "trong số đó", "năm đó", bạn BẮT BUỘC phải đối chiếu với Lịch sử hội thoại trước đó để thay thế bằng tên huyện, tên xã, hoặc năm cụ thể.
   - Ví dụ: Lịch sử hỏi về "Tuy Đức 2024", câu hỏi hiện tại là "Có bao nhiêu hộ nghèo trong đây là nữ?" -> Trả về: ["Có bao nhiêu hộ nghèo ở huyện Tuy Đức năm 2024 có chủ hộ là nữ?"]
3. Nếu câu hỏi chỉ là 1 ý đơn lẻ hoặc 1 câu hỏi duy nhất (dù dài):
   - Trả về danh sách chứa đúng 1 câu hỏi ban đầu (đã thay thế đồng tham chiếu nếu cần).
4. CHỈ TRẢ VỀ một chuỗi JSON dạng mảng (List of strings), không giải thích gì thêm.
Ví dụ đầu ra chuẩn:
["câu hỏi 1", "câu hỏi 2"]"""

    def decompose(self, user_question: str, history: list[dict] | None = None) -> List[str]:
        q_strip = user_question.strip()
        has_coref = any(w in q_strip.lower() for w in ["trong đây", "ở đó", "xã đó", "huyện đó", "còn lại", "trong số đó", "những hộ", "huyện này", "xã này", "năm đó", "trên", "đó", "này"])
        
        # Fast path heuristics
        if not history and len(q_strip) < 25 and "?" not in q_strip[:-1]:
            return [q_strip]
        if history and not has_coref and len(q_strip) < 25 and "?" not in q_strip[:-1]:
            return [q_strip]

        try:
            user_prompt_str = f"Câu hỏi: {q_strip}"
            if history:
                history_lines = []
                for msg in history[-4:]:
                    role_str = "Người dùng" if msg.get("role") == "user" else "Hệ thống"
                    history_lines.append(f"{role_str}: {msg.get('content', '')[:300]}")
                history_str = "\n".join(history_lines)
                user_prompt_str = f"Lịch sử hội thoại trước đó:\n{history_str}\n\nCâu hỏi hiện tại cần phân rã/thay thế đồng tham chiếu: {q_strip}"

            res_raw = call_llm(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt_str,
                temperature=0.0,
                max_tokens=256,
                response_json=True
            )
            
            if isinstance(res_raw, str):
                res_clean = res_raw.strip()
                if res_clean.startswith("```json"):
                    res_clean = res_clean[7:]
                if res_clean.startswith("```"):
                    res_clean = res_clean[3:]
                if res_clean.endswith("```"):
                    res_clean = res_clean[:-3]
                parsed = json.loads(res_clean.strip())
            else:
                parsed = res_raw

            if isinstance(parsed, dict):
                for k in ["questions", "queries", "list", "result", "sub_queries"]:
                    if k in parsed and isinstance(parsed[k], list):
                        parsed = parsed[k]
                        break

            if isinstance(parsed, list) and len(parsed) > 0:
                valid_queries = [str(q).strip() for q in parsed if str(q).strip()]
                if valid_queries:
                    return valid_queries
        except Exception as e:
            print(f"[QueryDecomposer Warning] Lỗi phân rã câu hỏi ({e}). Trả về nguyên bản.")

        return [q_strip]
