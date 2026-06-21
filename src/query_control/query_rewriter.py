# -*- coding: utf-8 -*-
"""
Module Query Rewriter thực hiện viết lại và chuẩn hóa câu hỏi người dùng bằng LLM (Gemma).
Giải quyết từ viết tắt, địa danh hành chính, từ đồng nghĩa và tham chiếu lịch sử (follow-up).
"""

from __future__ import annotations
import json
from typing import Any, List, Dict
from src.query_control.llm_helper import call_llm, clean_json_response

class QueryRewriter:
    def __init__(self):
        """
        Khởi tạo Query Rewriter.
        """
        pass

    def rewrite(self, user_question: str, conversation_history: List[Dict[str, Any]] = None) -> str:
        """
        Viết lại câu hỏi thô của người dùng thành một câu hỏi chuẩn hóa duy nhất (canonical question).
        Loại bỏ sự khác biệt về cách diễn đạt của các câu hỏi cùng ý nghĩa (paraphrase).

        Args:
            user_question (str): Câu hỏi thô từ người dùng.
            conversation_history (List[Dict[str, Any]], optional): Lịch sử các lượt chat trước. Defaults to None.

        Returns:
            str: Câu hỏi đã được chuẩn hóa bằng Tiếng Việt.

        Lưu ý nghiệp vụ:
            Hàm này sử dụng Gemma để giải quyết:
            - Viết tắt (BHYT -> thiếu bảo hiểm y tế).
            - Địa danh hành chính ở Đắk Nông (Krông Nô -> Huyện Krông Nô).
            - Đồng bộ cấu trúc câu hỏi so sánh, cực trị, thay đổi theo thời gian.
            - Giải quyết tham chiếu ngược (coreference) từ lịch sử trò chuyện.
        """
        # Nếu câu hỏi quá ngắn (ví dụ <= 2 từ), giữ nguyên để tránh LLM hallucinate (ảo tưởng) ra câu dài từ ví dụ trong prompt
        words = user_question.strip().split()
        if len(words) <= 2:
            return user_question.strip()

        # Bước 0: Pre-check xem có tên người trong câu hỏi không (Theo yêu cầu User)
        check_name_prompt = f"\"{user_question}\"\nTrong câu trên có tồn tại tên của một người không? Chỉ trả lời 'Tên của người đó' hoặc 'Không'. Không giải thích gì thêm."
        try:
            raw_name = call_llm(
                system_prompt="Bạn là trợ lý AI chuyên trích xuất tên người. Chỉ trả lời ngắn gọn theo yêu cầu.",
                user_prompt=check_name_prompt,
                temperature=0.0,
                max_tokens=20,
                response_json=False
            ).strip()
            
            # Nếu có tên người, cấu trúc lại câu hỏi để đưa tên chủ hộ vào, từ đó Semantic Search và Planner dễ dàng bắt được
            if raw_name.lower() != "không" and len(raw_name.split()) >= 2:
                extracted_name = raw_name.strip(".'\"")
                user_question = f"Tra cứu thông tin chi tiết ({user_question}) của hộ gia đình có tên chủ hộ chứa {extracted_name}"
        except Exception:
            pass # Bỏ qua nếu lỗi
            
        # 1. Định dạng lịch sử trò chuyện để gửi kèm vào prompt
        history_str = ""
        if conversation_history:
            history_str = "\nLịch sử các lượt trò chuyện trước đó:\n"
            for i, turn in enumerate(conversation_history[-3:]): # Chỉ lấy tối đa 3 lượt gần nhất
                user_q = turn.get("user_question", "")
                history_str += f"- Lượt {i+1} (User): {user_q}\n"

        # 2. Xây dựng prompt chi tiết để định hướng mô hình Gemma viết lại chính xác
        system_prompt = (
            "Bạn là một trợ lý AI chuyên nghiệp có nhiệm vụ chuẩn hóa câu hỏi Tiếng Việt của người dùng về dữ liệu rà soát hộ nghèo, hộ cận nghèo tỉnh Đắk Nông (2023-2024).\n"
            "Mục tiêu của bạn là viết lại câu hỏi thô thành một câu hỏi chuẩn hóa duy nhất (canonical question). Bất kỳ câu hỏi nào có cùng ý nghĩa (paraphrase) phải được viết lại thành phiên bản giống hệt nhau về mặt chữ để hệ thống có thể tối ưu hóa và nhận dạng chính xác.\n\n"
            "Quy tắc chuẩn hóa bắt buộc:\n"
            "1. Địa danh hành chính Đắk Nông:\n"
            "- Luôn sử dụng tiền tố 'Huyện' hoặc 'Thành phố' và viết chuẩn tên huyện: 'Huyện Cư Jút', 'Huyện Krông Nô', 'Huyện Tuy Đức', 'Huyện Đăk Glong', 'Huyện Đắk Mil', 'Huyện Đắk RLấp', 'Huyện Đắk Song', 'Thành phố Gia Nghĩa'.\n"
            "- Ví dụ: 'Tuy Đức' -> 'Huyện Tuy Đức', 'Đắk RLấp' hoặc 'Đắk R'Lấp' -> 'Huyện Đắk RLấp', 'Gia Nghĩa' -> 'Thành phố Gia Nghĩa'.\n\n"
            "2. Thuật ngữ viết tắt & đồng nghĩa:\n"
            "- 'BHYT' -> 'thiếu bảo hiểm y tế'.\n"
            "- 'không có BHYT' -> 'thiếu bảo hiểm y tế'.\n"
            "- 'nước sạch' -> 'thiếu nước sạch' (trong các câu hỏi liên quan đến chỉ số thiếu hụt).\n"
            "- 'nhà tiêu hợp vệ sinh' -> 'thiếu nhà tiêu hợp vệ sinh'.\n\n"
            "3. Đồng nhất cấu trúc câu hỏi (Cực kỳ quan trọng để đảm bảo 2 câu paraphrase ra kết quả giống hệt nhau):\n"
            "- Câu hỏi so sánh 2 huyện: 'So sánh số hộ nghèo năm [năm] giữa [huyện A] và [huyện B].'\n"
            "  * Ví dụ: 'Năm 2024, huyện Krông Nô hay Đắk Song có số hộ nghèo nhiều hơn?' và 'So sánh số hộ nghèo giữa Krông Nô và Đắk Song năm 2024.' đều viết lại thành: 'So sánh số hộ nghèo năm 2024 giữa Huyện Krông Nô và Huyện Đắk Song.'\n"
            "- Câu hỏi đếm hộ thiếu chỉ số: 'Năm [năm], [địa danh] có bao nhiêu hộ nghèo [chỉ số thiếu hụt]?'\n"
            "  * Ví dụ: 'Trong nhóm hộ nghèo ở Đắk RLấp năm 2024, số hộ không có BHYT là bao nhiêu?' -> 'Năm 2024, Huyện Đắk RLấp có bao nhiêu hộ nghèo thiếu bảo hiểm y tế.'\n"
            "- Câu hỏi tìm cực trị: 'Huyện nào có [chỉ số] nhiều nhất năm [năm]?' hoặc 'Huyện nào có [chỉ số] cao nhất năm [năm]?'\n"
            "  * Ví dụ: 'Trong năm 2023, địa phương nào đứng đầu về số lượng hộ nghèo?' -> 'Huyện nào có số hộ nghèo nhiều nhất năm 2023?'\n"
            "  * Ví dụ: 'Huyện nào có nhiều hộ nghèo thiếu nước sạch nhất năm 2024?' và 'Năm 2024, địa phương nào có số hộ nghèo bị thiếu nước sạch cao nhất?' đều viết lại thành: 'Huyện nào có nhiều hộ nghèo thiếu nước sạch nhất năm 2024?'\n"
            "- Câu hỏi về sự thay đổi/xu hướng qua các năm: 'So sánh số hộ nghèo ở [địa danh] giữa năm [năm 1] và năm [năm 2].'\n"
            "  * Ví dụ: 'Số hộ nghèo ở Đắk Song thay đổi như thế nào từ 2023 đến 2024?' và 'Huyện Đắk Song năm 2024 có số hộ nghèo tăng hay giảm so với năm 2023?' đều viết lại thành: 'So sánh số hộ nghèo ở Huyện Đắk Song giữa năm 2023 và năm 2024.'\n"
            "- Câu hỏi về tổng số trẻ em nghèo/cận nghèo: 'Năm [năm], có bao nhiêu trẻ em thuộc hộ nghèo hoặc cận nghèo?'\n"
            "  * Ví dụ: 'Năm 2024, tổng số trẻ em trong các hộ nghèo và cận nghèo là bao nhiêu?' -> 'Năm 2024, có bao nhiêu trẻ em thuộc hộ nghèo hoặc cận nghèo?'\n"
            "- Câu hỏi thống kê theo dân tộc: 'Thống kê số hộ nghèo theo dân tộc năm [năm].'\n"
            "  * Ví dụ: 'Trong năm 2024, nhóm dân tộc nào chiếm tỷ lệ hộ nghèo cao nhất?' -> 'Thống kê số hộ nghèo theo dân tộc năm 2024.'\n\n"
            "4. Giải quyết tham chiếu ngược (Coreference Resolution) từ lịch sử trò chuyện:\n"
            "- Dựa vào các câu hỏi trước đó để điền thông tin địa danh hoặc năm bị khuyết trong câu hỏi hiện tại.\n"
            "- Ví dụ:\n"
            "  * Lịch sử: - Lượt 1 (User): Năm 2023, Huyện Tuy Đức có bao nhiêu hộ nghèo?\n"
            "  * Câu hỏi hiện tại: 'Còn năm 2024 thì sao?' -> Viết lại thành: 'Năm 2024, Huyện Tuy Đức có bao nhiêu hộ nghèo?'\n\n"
            "Hãy luôn trả về cấu trúc JSON hợp lệ sau, tuyệt đối không thêm bớt từ hay lời giải thích ngoài JSON:\n"
            "{\n"
            "  \"rewritten_question\": \"Câu hỏi sau khi đã chuẩn hóa và viết lại hoàn chỉnh\",\n"
            "  \"reasoning\": \"Lý do ngắn gọn viết lại\"\n"
            "}"
        )

        user_prompt = f"{history_str}Câu hỏi hiện tại cần chuẩn hóa: {user_question}"

        # 3. Gọi LLM
        try:
            raw_res = call_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.1,
                max_tokens=250,
                response_json=True
            )
            res_dict = clean_json_response(raw_res)
            rewritten = res_dict.get("rewritten_question", user_question).strip()
            # Xử lý dấu chấm ở cuối câu hỏi để chuẩn hóa hơn nữa
            if rewritten.endswith(".") or rewritten.endswith("?"):
                rewritten = rewritten[:-1].strip()
            return rewritten
        except Exception:
            # Fallback an toàn nếu LLM lỗi
            return user_question
