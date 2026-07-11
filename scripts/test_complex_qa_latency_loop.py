# -*- coding: utf-8 -*-
"""
Script kiểm thử 10 câu hỏi phức tạp mới (ngoài cache) trong chế độ 'Hỏi - Đáp'
Yêu cầu: Latency < 8.5s, 1 Text + 1 DataFrame hợp lệ, Text dựa trên DataFrame.
"""

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.query_control.agentic.agent_pipeline import AgenticPipeline

def run_complex_benchmark(test_queries):
    print("==================================================================================", flush=True)
    print("🚀 BẮT ĐẦU KIỂM THỬ LATENCY ROUTE 2 & 3 (COMPLEX QUERIES)", flush=True)
    print("==================================================================================", flush=True)
    
    pipeline = AgenticPipeline()
    
    results = []
    total_latency = 0.0
    passed_latency_count = 0
    passed_structure_count = 0
    
    for idx, q in enumerate(test_queries, 1):
        print(f"\n[{idx}/{len(test_queries)}] Câu hỏi: {q}", flush=True)
        t_start = time.time()
        try:
            res = pipeline.process(q, mode="Hỏi - Đáp", stream=False)
            latency = time.time() - t_start
            total_latency += latency
            
            ans_text = res.get("answer", "")
            df_res = res.get("data", None)
            
            has_text = bool(ans_text and len(ans_text.strip()) > 5)
            has_df = df_res is not None and not df_res.empty
            
            latency_pass = latency < 8.5
            structure_pass = has_text and has_df
            
            if latency_pass:
                passed_latency_count += 1
            if structure_pass:
                passed_structure_count += 1
                
            status_lat = "✅ <8.5s" if latency_pass else f"❌ {latency:.2f}s (>=8.5s)"
            status_str = "✅ 1 Text + 1 DF" if structure_pass else "❌ Sai cấu trúc (Thiếu Text/DF rỗng)"
            
            print(f"   ⏱️ Latency: {latency:.2f}s -> {status_lat}", flush=True)
            print(f"   📊 Structure: {status_str} (DF shape: {df_res.shape if has_df else 'None'})", flush=True)
            print(f"   💬 Text snippet: {ans_text[:150]}...", flush=True)
            
            results.append({
                "query": q,
                "latency": latency,
                "latency_pass": latency_pass,
                "structure_pass": structure_pass,
                "df_shape": df_res.shape if has_df else None,
                "text": ans_text
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
    print("📈 TỔNG KẾT BENCHMARK COMPLEX QUERIES", flush=True)
    print("==================================================================================", flush=True)
    avg_lat = total_latency / len(test_queries)
    print(f"⏱️ Thời gian trung bình / truy vấn: {avg_lat:.2f}s", flush=True)
    print(f"✅ Số câu đạt yêu cầu Latency (< 8.5s): {passed_latency_count}/{len(test_queries)} ({passed_latency_count*100//len(test_queries)}%)", flush=True)
    print(f"✅ Số câu đạt yêu cầu Cấu trúc (1 Text + 1 DF): {passed_structure_count}/{len(test_queries)} ({passed_structure_count*100//len(test_queries)}%)", flush=True)
    print("==================================================================================", flush=True)
    
    if passed_latency_count == len(test_queries) and passed_structure_count == len(test_queries):
        print("🎉 SUCCESS: TẤT CẢ CÁC TIÊU CHÍ ĐỀU ĐẠT!")
    else:
        print("⚠️ FAILED: CHƯA ĐẠT TIÊU CHÍ. CẦN FIX CODE VÀ RE-RUN LẠI!")

if __name__ == "__main__":
    queries_loop_1 = [
        "So sánh số hộ nghèo ở các xã của tuy đức 2024",
        "Xã nào đang có nhiều chủ hộ nghèo là nữ nhất gia nghĩa ?",
        "số hộ nghèo 2024 ở dak nong có giảm so với năm 2023 không",
        "tình trạng thiếu hụt bhyt tại dak mil 2024",
        "Hộ gia đình nào đang có điểm b1 nhất dak mil ?",
        "dân tộc nào có tỉ lệ nghèo cao nhất dak song 2023",
        "Xã nào có nhiều dttc nhất dak rlap",
        "gia nghĩa có đứng đầu về số hộ nghèo 2024 không ?",
        "xã dak lao của dak mil đang có các hộ nào",
        "tỷ lệ thoát nghèo ở các xã của dak glong 2024"
    ]
    run_complex_benchmark(queries_loop_1)
