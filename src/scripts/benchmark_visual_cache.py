# -*- coding: utf-8 -*-
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.query_control.agentic.agent_pipeline import AgenticPipeline

def run_benchmark():
    queries = [
        "So sánh số hộ nghèo và hộ cận nghèo theo từng huyện bằng biểu đồ.",
        "So sánh số hộ nghèo và hộ cận nghèo theo nguyên nhân nghèo bằng biểu đồ.",
        "Biểu đồ thể hiện mức sống trung bình theo huyện năm 2024.",
        "Vẽ biểu đồ so sánh số hộ nghèo năm 2023 và 2024 theo từng huyện.",
        "Biểu đồ so sánh số hộ cận nghèo năm 2023 và 2024 theo từng huyện.",
        "Thống kê số lượng hộ nghèo đa chiều thiếu hụt theo các chỉ số đo lường bằng biểu đồ.",
        "Thống kê số lượng hộ cận nghèo đa chiều thiếu hụt theo các chỉ số đo lường bằng biểu đồ.",
        "Vẽ biểu đồ Top 5 xã có số hộ nghèo nhiều nhất năm 2024.",
        "Vẽ biểu đồ Top 5 xã có số hộ cận nghèo nhiều nhất năm 2024.",
        "Vẽ biểu đồ so sánh số trẻ em thuộc hộ nghèo theo từng huyện năm 2024."
    ]
    
    pipeline = AgenticPipeline()
    
    print("="*80)
    print("BAT DAU BENCHMARK VISUAL CODE CACHE (10 CAU HOI BIEU DO)")
    print("="*80)
    
    # Round 1: Populate / Check Cache
    print("\n--- ROUND 1: Populate / Execution ---")
    r1_times = []
    for i, q in enumerate(queries, 31):
        t0 = time.time()
        res = pipeline.process(q, mode="Biểu đồ", stream=False)
        elapsed = time.time() - t0
        r1_times.append(elapsed)
        print(f"Cau {i} | Time: {elapsed:.2f}s | SQL: {res.get('sql', '')[:40]}...")
        
    # Round 2: Instant Code Execution Hit
    print("\n--- ROUND 2: Visual Code Cache Hit Verification ---")
    r2_times = []
    for i, q in enumerate(queries, 31):
        t0 = time.time()
        res = pipeline.process(q, mode="Biểu đồ", stream=False)
        elapsed = time.time() - t0
        r2_times.append(elapsed)
        print(f"Cau {i} | Time: {elapsed:.4f}s | Chart Generated: {res.get('chart_fig') is not None}")
        
    print("\n" + "="*80)
    print("TONG KET BENCHMARK:")
    print(f"Trung binh thoi gian Round 1: {sum(r1_times)/len(r1_times):.2f}s")
    print(f"Trung binh thoi gian Round 2 (Visual Code Cache Hit): {sum(r2_times)/len(r2_times):.4f}s")
    savings = (1 - sum(r2_times)/sum(r1_times)) * 100 if sum(r1_times) > 0 else 0
    print(f"MUC DO TIET KIEM THOI GIAN: {savings:.1f}%")
    print("="*80)

if __name__ == "__main__":
    run_benchmark()
