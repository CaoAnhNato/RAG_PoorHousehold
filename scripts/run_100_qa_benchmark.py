# -*- coding: utf-8 -*-
"""
Script chạy kiểm định 100 Golden Benchmark Queries trên CLI Chatbot ở mode 'Hỏi - Đáp'.
Kiểm tra output parity (Text + DataFrame), đo đạc thời gian thực thi trung bình (latency),
và ghi nhận chi tiết kết quả để debug nếu có lỗi.
"""
import os
import sys
import time
import json
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.query_control.agentic.agent_pipeline import AgenticPipeline

def run_benchmark():
    benchmark_path = PROJECT_ROOT / "test/comprehensive_100_qa_benchmark.json"
    if not benchmark_path.exists():
        print(f"[ERROR] Không tìm thấy file benchmark: {benchmark_path}")
        return

    with open(benchmark_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    test_cases = data.get("test_cases", [])

    print(f"=== BẮT ĐẦU CHẠY KIỂM ĐỊNH 100 GOLDEN BENCHMARK QUERIES (MODE: 'HỎI - ĐÁP') ===")
    print(f"Tổng số test cases: {len(test_cases)}\n")

    print("Đang khởi tạo AgenticPipeline...")
    pipeline = AgenticPipeline()
    print("Khởi tạo thành công!\n" + "="*100)

    results = []
    t_start_all = time.time()

    for idx, tc in enumerate(test_cases, 1):
        tc_id = tc.get("test_id", f"TC_{idx:03d}")
        cat = tc.get("category", "Unknown")
        prompt = tc.get("prompt", "")

        print(f"\n[{idx}/{len(test_cases)}] [{tc_id}] [{cat}] {prompt}", flush=True)
        t0 = time.time()
        try:
            res = pipeline.process(user_question=prompt, mode="Hỏi - Đáp")
            latency = time.time() - t0

            ans_text = res.get("answer", "")
            df = res.get("data")
            error = res.get("error")
            sql_gen = res.get("sql", "")

            if isinstance(df, pd.DataFrame):
                has_df = not df.empty
                df_shape_str = f"{df.shape[0]}x{df.shape[1]}"
            elif isinstance(df, dict):
                has_df = any(isinstance(v, pd.DataFrame) and not v.empty for v in df.values())
                df_shape_str = "Dict of DFs"
            else:
                has_df = False
                df_shape_str = "None"

            is_raw_md_table = "Dữ liệu chi tiết:\n\n|" in str(ans_text) or (str(ans_text).startswith("|") and "---" in str(ans_text))
            has_text = bool(ans_text and len(str(ans_text).strip()) > 10)

            passed = has_df and has_text and not is_raw_md_table and not error

            results.append({
                "idx": idx,
                "test_id": tc_id,
                "category": cat,
                "prompt": prompt,
                "latency": latency,
                "df_shape": df_shape_str,
                "has_df": has_df,
                "has_text": has_text,
                "is_raw_md": is_raw_md_table,
                "passed": passed,
                "error": error,
                "sql": sql_gen,
                "ans_preview": str(ans_text)[:200] + "..." if len(str(ans_text)) > 200 else str(ans_text)
            })

            status_icon = "✅ PASSED" if passed else "❌ FAILED"
            print(f"  -> Status: {status_icon} | Latency: {latency:.2f}s | DF: {df_shape_str}")
            if not passed:
                print(f"  -> Reason: Error={error} | has_df={has_df} | has_text={has_text} | RawMD={is_raw_md_table}")
                print(f"  -> Ans Preview: {str(ans_text)[:120]}")

        except Exception as e:
            latency = time.time() - t0
            results.append({
                "idx": idx,
                "test_id": tc_id,
                "category": cat,
                "prompt": prompt,
                "latency": latency,
                "df_shape": "Exception",
                "has_df": False,
                "has_text": False,
                "is_raw_md": False,
                "passed": False,
                "error": str(e),
                "sql": "",
                "ans_preview": f"Exception: {e}"
            })
            print(f"  -> ❌ EXCEPTION after {latency:.2f}s: {e}")

    total_time = time.time() - t_start_all
    passed_count = sum(1 for r in results if r["passed"])
    avg_latency = sum(r["latency"] for r in results) / len(results) if results else 0.0

    print("\n" + "="*100)
    print("=== TỔNG HỢP KẾT QUẢ KIỂM ĐỊNH 100 GOLDEN BENCHMARK (HỎI - ĐÁP) ===")
    print("="*100)
    print(f"Tổng số câu hỏi: {len(results)}")
    print(f"Số câu đạt chuẩn (Passed): {passed_count}/{len(results)} ({passed_count/len(results)*100:.2f}%)")
    print(f"Thời gian thực thi trung bình: {avg_latency:.3f} giây/câu")
    print(f"Tổng thời gian kiểm định: {total_time:.2f} giây")
    print("\nThống kê theo từng Category:")
    
    cats = {}
    for r in results:
        c = r["category"]
        if c not in cats:
            cats[c] = {"total": 0, "passed": 0, "latency_sum": 0.0}
        cats[c]["total"] += 1
        if r["passed"]:
            cats[c]["passed"] += 1
        cats[c]["latency_sum"] += r["latency"]

    for c, stat in sorted(cats.items()):
        c_avg = stat["latency_sum"] / stat["total"]
        print(f"  - {c}: {stat['passed']}/{stat['total']} passed ({stat['passed']/stat['total']*100:.1f}%) | Avg Latency: {c_avg:.3f}s")

    out_file = PROJECT_ROOT / "test/debug/100_qa_benchmark_results.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total_queries": len(results),
                "passed_queries": passed_count,
                "pass_rate_pct": round(passed_count / len(results) * 100, 2),
                "average_latency_sec": round(avg_latency, 3),
                "total_execution_time_sec": round(total_time, 2),
                "category_breakdown": {
                    c: {
                        "total": stat["total"],
                        "passed": stat["passed"],
                        "pass_rate_pct": round(stat["passed"]/stat["total"]*100, 2),
                        "avg_latency_sec": round(stat["latency_sum"]/stat["total"], 3)
                    }
                    for c, stat in cats.items()
                }
            },
            "detailed_results": results
        }, f, ensure_ascii=False, indent=2)

    print(f"\nĐã lưu báo cáo chi tiết tại: {out_file}")
    print("="*100)

if __name__ == "__main__":
    run_benchmark()
