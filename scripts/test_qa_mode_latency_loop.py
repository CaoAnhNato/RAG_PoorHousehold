# -*- coding: utf-8 -*-
"""
Script kiểm thử 10 câu hỏi MỚI (ngoài cache) trong chế độ 'Hỏi - Đáp' (Vòng lặp 4 - Final Verification)
Đo lường Latency (< 7s) và kiểm chứng cấu trúc Output (1 Text + 1 DataFrame).
"""

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.query_control.agentic.agent_pipeline import AgenticPipeline

def run_latency_benchmark():
    print("==================================================================================", flush=True)
    print("🚀 BẮT ĐẦU KIỂM THỬ LATENCY ROUTE 2 & 3 (LOOP 4 - FINAL VERIFICATION)", flush=True)
    print("==================================================================================", flush=True)
    
    pipeline = AgenticPipeline()
    
    test_queries = [
        "Xin cho biết tổng số hộ nghèo năm 2024 tại huyện Cư Jút là bao nhiêu hộ?",
        "Số lượng hộ cận nghèo năm 2024 tại xã Đức Minh thuộc huyện Đắk Mil?",
        "Trong năm 2024 có bao nhiêu hộ nghèo là người dân tộc thiểu số tại huyện Đắk Song?",
        "Tỷ lệ hộ nghèo năm 2024 trên địa bàn huyện Tuy Đức là bao nhiêu phần trăm?",
        "Tại phường Nghĩa Đức thành phố Gia Nghĩa năm 2024 có bao nhiêu hộ cận nghèo?",
        "Số lượng nhân khẩu thuộc hộ nghèo tại huyện Krông Nô năm 2024?",
        "Ở huyện Đắk RLấp năm 2024 có bao nhiêu hộ nghèo thiếu hụt tiêu chí nước sinh hoạt?",
        "Có bao nhiêu hộ nghèo tại xã Nhân Cơ huyện Đắk RLấp năm 2024?",
        "Huyện Cư Jút năm 2024 có bao nhiêu hộ nghèo do nguyên nhân thiếu lao động?",
        "Xin cho biết tổng số hộ nghèo và hộ cận nghèo năm 2024 tại huyện Tuy Đức?"
    ]
    
    results = []
    total_latency = 0.0
    passed_latency_count = 0
    passed_structure_count = 0
    
    for idx, q in enumerate(test_queries, 1):
        print(f"\n[{idx}/10] Câu hỏi: {q}", flush=True)
        t_start = time.time()
        try:
            res = pipeline.process(q, mode="Hỏi - Đáp", stream=False)
            latency = time.time() - t_start
            total_latency += latency
            
            ans_text = res.get("answer", "")
            df_res = res.get("data", None)
            
            has_text = bool(ans_text and len(ans_text.strip()) > 5)
            has_df = df_res is not None and not df_res.empty
            
            latency_pass = latency < 7.0
            structure_pass = has_text and has_df
            
            if latency_pass:
                passed_latency_count += 1
            if structure_pass:
                passed_structure_count += 1
                
            status_lat = "✅ <7s" if latency_pass else f"❌ {latency:.2f}s (>=7s)"
            status_str = "✅ 1 Text + 1 DF" if structure_pass else "❌ Sai cấu trúc"
            
            print(f"   ⏱️ Latency: {latency:.2f}s -> {status_lat}", flush=True)
            print(f"   📊 Structure: {status_str} (DF shape: {df_res.shape if has_df else 'None'})", flush=True)
            print(f"   💬 Text snippet: {ans_text[:120]}...", flush=True)
            
            results.append({
                "query": q,
                "latency": latency,
                "latency_pass": latency_pass,
                "structure_pass": structure_pass
            })
        except Exception as e:
            latency = time.time() - t_start
            print(f"   ❌ LỖI RUNTIME: {e} after {latency:.2f}s", flush=True)
            results.append({
                "query": q,
                "latency": latency,
                "latency_pass": False,
                "structure_pass": False
            })
            
    print("\n==================================================================================", flush=True)
    print("📈 TỔNG KẾT BENCHMARK LATENCY ROUTE 2 & 3 (LOOP 4)", flush=True)
    print("==================================================================================", flush=True)
    avg_lat = total_latency / len(test_queries)
    print(f"⏱️ Thời gian trung bình / truy vấn: {avg_lat:.2f}s", flush=True)
    print(f"✅ Số câu đạt yêu cầu Latency (< 7s): {passed_latency_count}/10 ({passed_latency_count*10}%)", flush=True)
    print(f"✅ Số câu đạt yêu cầu Cấu trúc (1 Text + 1 DF): {passed_structure_count}/10 ({passed_structure_count*10}%)", flush=True)
    print("==================================================================================", flush=True)

if __name__ == "__main__":
    run_latency_benchmark()
