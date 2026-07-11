# -*- coding: utf-8 -*-
import os
import sys
import time
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.query_control.agentic.agent_pipeline import AgenticPipeline

def run_test():
    print("Initializing AgenticPipeline...")
    pipeline = AgenticPipeline()
    
    queries = [
        # Nhóm Chủ hộ
        "Năm 2024, thống kê số lượng hộ nghèo theo giới tính chủ hộ trên toàn tỉnh.",
        "Thống kê số lượng hộ nghèo năm 2024 theo độ tuổi của chủ hộ tại huyện Đắk Glong.",
        # Nhóm Thành viên hộ
        "Tổng số thành viên trong các hộ nghèo và cận nghèo tại huyện Tuy Đức năm 2024 là bao nhiêu?",
        "Thống kê số lượng thành viên dưới 16 tuổi trong các hộ nghèo trên toàn tỉnh năm 2024.",
        "Trong các hộ nghèo năm 2024, có bao nhiêu thành viên chưa có Bảo hiểm y tế?",
        # Nhóm Xã / Phường
        "Top 5 xã có số lượng hộ nghèo nhiều nhất tại huyện Đắk Song năm 2024.",
        "Thống kê số hộ cận nghèo theo từng xã tại huyện Cư Jút năm 2024.",
        "Xã Tâm Thắng (huyện Cư Jút) năm 2024 có bao nhiêu hộ nghèo là người đồng bào dân tộc thiểu số?",
        # Nhóm Huyện
        "Thống kê tổng số hộ nghèo và cận nghèo theo từng huyện trên toàn tỉnh năm 2024.",
        "Huyện nào trong tỉnh có số hộ nghèo thiếu hụt về nước sinh hoạt cao nhất năm 2024?"
    ]
    
    results = []
    print(f"\nStarting benchmark for {len(queries)} queries in 'Hỏi - Đáp' mode...\n")
    print("="*100)
    
    for idx, q in enumerate(queries, 1):
        print(f"\n[Query {idx}/{len(queries)}] {q}", flush=True)
        t0 = time.time()
        try:
            res = pipeline.process(user_question=q, mode="Hỏi - Đáp")
            latency = time.time() - t0
            
            ans_text = res.get("answer", "")
            df = res.get("data")
            error = res.get("error")
            
            has_df = df is not None and isinstance(df, pd.DataFrame) and not df.empty
            df_rows = df.shape[0] if has_df else 0
            df_cols = df.shape[1] if has_df else 0
            
            # Kiểm tra xem text có phải là chuỗi Markdown thô không hay là văn bản tự nhiên
            is_raw_md_table = "Dữ liệu chi tiết:\n\n|" in ans_text or (ans_text.startswith("|") and "---" in ans_text)
            has_text = bool(ans_text and len(ans_text.strip()) > 10)
            
            # Đánh giá đạt yêu cầu: có text nhận xét tự nhiên (không phải bảng MD thô) + có dataframe
            passed = has_df and has_text and not is_raw_md_table and not error
            
            results.append({
                "idx": idx,
                "query": q,
                "latency": latency,
                "df_shape": f"{df_rows}x{df_cols}" if has_df else "None",
                "has_text": has_text,
                "is_raw_md": is_raw_md_table,
                "passed": passed,
                "error": error,
                "ans_preview": ans_text[:200] + "..." if len(ans_text) > 200 else ans_text
            })
            
            print(f"  -> Latency: {latency:.2f}s | DF: {df_rows}x{df_cols} | Passed: {passed}")
            if not passed:
                print(f"  -> Error/Issue: Error={error} | Raw MD={is_raw_md_table} | Ans={ans_text[:100]}")
            else:
                print(f"  -> Text Preview: {ans_text[:120].replace('chr(10)', ' ')}...")
                
        except Exception as e:
            latency = time.time() - t0
            results.append({
                "idx": idx,
                "query": q,
                "latency": latency,
                "df_shape": "Error",
                "has_text": False,
                "is_raw_md": False,
                "passed": False,
                "error": str(e),
                "ans_preview": f"Exception: {e}"
            })
            print(f"  -> EXCEPTION after {latency:.2f}s: {e}")
            
    print("\n" + "="*100)
    print("BENCHMARK SUMMARY REPORT")
    print("="*100)
    
    passed_count = sum(1 for r in results if r['passed'])
    avg_latency = sum(r['latency'] for r in results) / len(results)
    
    print(f"Total Queries: {len(results)}")
    print(f"Passed Requirement (1 Text comment + 1 DataFrame): {passed_count}/{len(results)} ({passed_count/len(results)*100:.1f}%)")
    print(f"Average Latency: {avg_latency:.2f}s\n")
    
    for r in results:
        status = "PASSED ✅" if r['passed'] else "FAILED ❌"
        print(f"Q{r['idx']}: {status} ({r['latency']:.2f}s) | DF: {r['df_shape']} | Query: {r['query']}")
        print(f"    Text output: {r['ans_preview']}\n")

if __name__ == "__main__":
    run_test()
