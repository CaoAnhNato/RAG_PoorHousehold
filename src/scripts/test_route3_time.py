# -*- coding: utf-8 -*-
import sys
import time
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.query_control.agentic.agent_pipeline import AgenticPipeline

def run_test():
    print("="*80)
    print("BAT DAU CHAY TUAN TU 10 CAU HOI QUA AGENTIC PIPELINE")
    print("="*80)

    pipeline = AgenticPipeline()

    test_queries = [
        "thống kê sl hộ nghèo vs cận nghèo dtts năm 2024 ở các huyện xem thế nào",
        "huyện krông nô 2024 có bao nhiêu hn bị thiếu vốn sx với thiếu đất sx?",
        "năm 2024 khu vực thành thị hay nông thôn có số hộ thoát nghèo nhiều hơn?",
        "top 3 xã có trẻ em ko đi học nhiều nhất 2024 là xã nào?",
        "ở tp gia nghĩa bn hộ nghèo bị thiếu hụt chất lượng nhà ở với diện tích nhà ở năm 2024",
        "tính tỷ lệ chủ hộ nam vs nữ trong các hcn năm 2024 toàn tỉnh",
        "so sánh sl hộ nghèo ko có khả năng lao động ở đắk mil giữa 2 năm 2023 vs 2024",
        "đăk glong 2024 có bn hộ nghèo cần hỗ trợ về y tế và giáo dục?",
        "huyện nào có nhiều hộ nghèo bị ốm đau tai nạn nhất năm 2024?",
        "check xem cư jút 2024 có bn hộ nghèo thiếu nước sạch vs nhà vệ sinh"
    ]

    for idx, q in enumerate(test_queries, 1):
        print(f"\n--- [Câu {idx}/10] ---")
        print(f"Q: {q}")
        t0 = time.time()
        try:
            res = pipeline.process(q, mode="Auto")
            elapsed = time.time() - t0
            print(f"=> Hoàn thành trong {elapsed:.2f}s | SQL: {res.get('sql', '')[:60]}...")
        except Exception as e:
            elapsed = time.time() - t0
            print(f"=> LỖI: {e}")

    log_file = PROJECT_ROOT / "data" / "Processed" / "logs" / "chatbot_runs.json"
    print("\n" + "="*80)
    print("THONG KE TU LOG CHATBOT_RUNS.JSON (10 lan thuc thi gan nhat):")
    print("="*80)
    if log_file.exists():
        with open(log_file, "r", encoding="utf-8") as f:
            logs = json.load(f)
        
        recent_logs = logs[-10:]
        print(f"{'ID':<4} | {'Mode logged':<35} | {'Time (s)':<10} | {'Question':<35}")
        print("-" * 90)
        for i, l in enumerate(recent_logs, 1):
            q_short = l.get("user_question", "")[:32] + ".." if len(l.get("user_question", "")) > 32 else l.get("user_question", "")
            print(f"{i:<4} | {l.get('mode', ''):<35} | {l.get('execution_time_sec', 0):<10.4f} | {q_short:<35}")
    
    print("="*80)

if __name__ == "__main__":
    run_test()
