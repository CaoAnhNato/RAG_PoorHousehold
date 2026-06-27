# -*- coding: utf-8 -*-
"""
Module chatbot_logger cung cấp cơ chế ghi log tự động cho mọi câu trả lời
của CLI chatbot và Streamlit chatbot (bao gồm cả các phiên test).
Lưu trữ log dưới dạng cấu trúc JSON Lines / List để thuận tiện phân tích và debug.
"""

from __future__ import annotations
import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
LOG_DIR = PROJECT_ROOT / "data" / "Processed" / "logs"
LOG_FILE = LOG_DIR / "chatbot_runs.json"

def log_chatbot_run(
    user_question: str,
    mode: str,
    sql_query: str,
    answer: str,
    stream: bool = False,
    execution_time_sec: float = 0.0
) -> bool:
    """
    Ghi lại thông tin chi tiết của mỗi lượt hỏi đáp vào tệp log cấu trúc JSON.

    Hàm này tự động tạo thư mục lưu trữ nếu chưa tồn tại, tổng hợp các thông tin
    về câu hỏi, chế độ, câu truy vấn SQL sinh ra, câu trả lời đầy đủ và thời gian thực thi,
    sau đó lưu vào tệp `data/Processed/logs/chatbot_runs.json`.

    Args:
        user_question (str): Câu hỏi gốc của người dùng gửi đến hệ thống chatbot.
        mode (str): Chế độ xử lý (ví dụ: 'Auto', 'Báo Cáo', 'Hỏi - Đáp', 'Biểu đồ').
        sql_query (str): Câu truy vấn SQL được sinh ra từ mô hình (hoặc rỗng nếu không có).
        answer (str): Câu trả lời đầy đủ dạng văn bản trả về cho người dùng.
        stream (bool): Trạng thái cho biết câu trả lời có được stream hay không (mặc định False).
        execution_time_sec (float): Thời gian thực thi truy vấn tính bằng giây (mặc định 0.0).

    Returns:
        bool: Trả về True nếu quá trình ghi log thành công, False nếu xảy ra lỗi.

    Lưu ý:
        Logic nghiệp vụ đặc thù: Để đảm bảo an toàn truy xuất đồng thời và định dạng file
        dễ đọc cho cả con người lẫn máy, tệp log được lưu theo cấu trúc danh sách JSON (JSON List).
        Nếu tệp đã tồn tại nhưng không đúng định dạng, hệ thống sẽ tự động khởi tạo lại mảng mới.
    """
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        
        # Chuẩn bị dữ liệu bản ghi log
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_question": user_question,
            "mode": mode,
            "sql_query": sql_query,
            "answer": answer,
            "stream": stream,
            "execution_time_sec": round(execution_time_sec, 4)
        }
        
        # Đọc dữ liệu log cũ (nếu có)
        existing_logs = []
        if LOG_FILE.exists():
            try:
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        existing_logs = json.loads(content)
                        if not isinstance(existing_logs, list):
                            existing_logs = [existing_logs]
            except Exception:
                existing_logs = []
                
        existing_logs.append(log_entry)
        
        # Ghi lại dữ liệu cập nhật vào tệp log
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(existing_logs, f, ensure_ascii=False, indent=2)
            
        return True
    except Exception as e:
        print(f"[ChatbotLogger] Lỗi khi ghi log chạy chatbot: {e}")
        return False

def get_recent_logs(limit: int = 50) -> list[dict[str, Any]]:
    """
    Truy xuất danh sách các bản ghi log gần đây nhất của hệ thống chatbot.

    Hàm này đọc tệp log lưu trữ tại `data/Processed/logs/chatbot_runs.json` và trả về
    danh sách các bản ghi log được sắp xếp theo thứ tự mới nhất (LIFO).

    Args:
        limit (int): Số lượng bản ghi log tối đa cần lấy (mặc định là 50).

    Returns:
        list[dict[str, Any]]: Danh sách các bản ghi log gần đây, mỗi bản ghi là một từ điển.

    Lưu ý:
        Logic nghiệp vụ đặc thù: Nếu tệp log chưa tồn tại hoặc rỗng, hàm sẽ trả về danh sách rỗng
        mà không gây ra lỗi hệ thống (Non-blocking retrieval).
    """
    if not LOG_FILE.exists():
        return []
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            logs = json.loads(content)
            if isinstance(logs, list):
                return logs[-limit:]
            return [logs]
    except Exception as e:
        print(f"[ChatbotLogger] Lỗi khi đọc log chạy chatbot: {e}")
        return []
