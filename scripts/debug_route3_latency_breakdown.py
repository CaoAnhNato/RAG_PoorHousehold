# -*- coding: utf-8 -*-
"""
Debug và đo lường latency từng phần của Route 3 trong chế độ 'Hỏi - Đáp' cho 10 câu hỏi phức tạp đa chiều (chưa có trong cache).
Phân tích thời gian:
- Re-write / Preflight (InputGuardrail)
- Schema Linking (SchemaLinker)
- Sinh SQL (SQLGenerator)
- Thực thi & Sửa SQL (SQLRefiner)
- Sinh Text trả lời (AnswerGenerator)
- Kiểm chứng Output Guardrail (OutputGuardrail)
"""

import time
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.query_control.agentic.agent_pipeline import AgenticPipeline
from src.query_control.agentic.guardrails import InputGuardrail, OutputGuardrail
from src.query_control.agentic.schema_linker import SchemaLinker
from src.query_control.agentic.sql_generator import SQLGenerator
from src.query_control.agentic.sql_refiner import SQLRefiner
from src.query_control.agentic.answer_generator import AnswerGenerator

# Dictionary to hold timing data for current run
current_timings = {}

def create_wrapper(orig_method, step_key):
    def wrapper(*args, **kwargs):
        t0 = time.time()
        try:
            return orig_method(*args, **kwargs)
        finally:
            dt = time.time() - t0
            current_timings[step_key] = current_timings.get(step_key, 0.0) + dt
    return wrapper

# Wrap class methods to record execution time dynamically
InputGuardrail.validate_and_rewrite = create_wrapper(InputGuardrail.validate_and_rewrite, "Re-write")
SchemaLinker.link = create_wrapper(SchemaLinker.link, "Schema Linking")
SQLGenerator.generate = create_wrapper(SQLGenerator.generate, "Sinh SQL")
SQLRefiner.execute_and_refine = create_wrapper(SQLRefiner.execute_and_refine, "Thực thi & Sửa SQL")
AnswerGenerator.generate = create_wrapper(AnswerGenerator.generate, "Sinh Text")
OutputGuardrail.validate_fact_checking = create_wrapper(OutputGuardrail.validate_fact_checking, "Output Guardrail")

def run_debug():
    print("=======================================================================================", flush=True)
    print("🚀 INTENTORCH: DEBUG THỜI GIAN GỌI LLM TẠI ROUTE 3 (MODE 'HỎI - ĐÁP' - CÂU HỎI KHÓ)", flush=True)
    print("=======================================================================================", flush=True)
    
    pipeline = AgenticPipeline()
    
    # 10 câu hỏi phức tạp đa chiều mới (chưa có trong cache)
    test_queries = [
        "So sánh tỷ lệ trẻ em không được đến trường giữa các xã thuộc huyện Đắk Glong năm 2024",
        "Có bao nhiêu hộ nghèo do nguyên nhân thiếu đất sản xuất tại huyện Cư Jút năm 2023?",
        "Liệt kê các xã thuộc huyện Krông Nô có trên 50 hộ cận nghèo là đồng bào dân tộc thiểu số năm 2024",
        "Tỷ trọng nhân khẩu của hộ nghèo có chủ hộ là nữ tại thành phố Gia Nghĩa năm 2024 là bao nhiêu phần trăm?",
        "Xã nào ở huyện Đắk RLấp có số lượng trẻ em thiếu hụt cả về y tế và dinh dưỡng cao nhất năm 2024?",
        "Thống kê số lượng hộ nghèo phát sinh mới trong năm 2024 tại huyện Tuy Đức theo từng nguyên nhân nghèo",
        "So sánh tổng số hộ cận nghèo có thành viên thuộc chính sách người có công tại huyện Đắk Mil giữa năm 2023 và 2024",
        "Trong các hộ nghèo tại xã Đắk Som huyện Đắk Glong năm 2024 có bao nhiêu hộ thiếu hụt về chất lượng nhà ở?",
        "Tỷ lệ hộ cận nghèo có chủ hộ không có khả năng lao động tại huyện Đắk Song năm 2024 là bao nhiêu?",
        "Huyện nào trong tỉnh Đắk Nông có tỷ lệ hộ nghèo vượt chuẩn cận nghèo cao nhất trong năm 2024?"
    ]
    
    summary_data = []
    
    for idx, q in enumerate(test_queries, 1):
        print(f"\n[{idx}/10] Câu hỏi: {q}", flush=True)
        current_timings.clear()
        
        t_start = time.time()
        # Chạy Route 3 (bỏ qua semantic cache bằng use_semantic_cache=False)
        res = pipeline.process(q, mode="Hỏi - Đáp", stream=False, use_semantic_cache=False)
        t_total = time.time() - t_start
        
        t_rewrite = current_timings.get("Re-write", 0.0)
        t_linker = current_timings.get("Schema Linking", 0.0)
        t_sql_gen = current_timings.get("Sinh SQL", 0.0)
        t_sql_refine = current_timings.get("Thực thi & Sửa SQL", 0.0)
        t_text = current_timings.get("Sinh Text", 0.0)
        t_out_guard = current_timings.get("Output Guardrail", 0.0)
        t_other = max(0.0, t_total - (t_rewrite + t_linker + t_sql_gen + t_sql_refine + t_text + t_out_guard))
        
        print(f"  ⏱️ Tổng thời gian: {t_total:.3f}s")
        print(f"    - Re-write (Preflight):     {t_rewrite:.3f}s")
        print(f"    - Schema Linking (BM25):    {t_linker:.3f}s")
        print(f"    - Sinh SQL (LLM):           {t_sql_gen:.3f}s")
        print(f"    - Thực thi & Sửa SQL:       {t_sql_refine:.3f}s")
        print(f"    - Sinh Text trả lời (LLM):  {t_text:.3f}s")
        print(f"    - Output Guardrail:         {t_out_guard:.3f}s")
        print(f"    - Khác (overhead):          {t_other:.3f}s")
        
        summary_data.append({
            "query": q[:40] + "...",
            "rewrite": t_rewrite,
            "linker": t_linker,
            "sql_gen": t_sql_gen,
            "sql_refine": t_sql_refine,
            "text": t_text,
            "out_guard": t_out_guard,
            "total": t_total
        })
        
    print("\n=======================================================================================", flush=True)
    print("📊 TỔNG HỢP THỜI GIAN THỰC THI ROUTE 3 CHO 10 CÂU HỎI KHÓ (ĐƠN VỊ: GIÂY)", flush=True)
    print("=======================================================================================", flush=True)
    header = f"{'STT':<4} | {'Re-write':<9} | {'Linker':<7} | {'Sinh SQL':<9} | {'Sửa SQL':<9} | {'Sinh Text':<10} | {'OutGuard':<9} | {'TỔNG':<7}"
    print(header)
    print("-" * len(header))
    
    sum_rewrite = sum(d["rewrite"] for d in summary_data)
    sum_linker = sum(d["linker"] for d in summary_data)
    sum_sql_gen = sum(d["sql_gen"] for d in summary_data)
    sum_sql_refine = sum(d["sql_refine"] for d in summary_data)
    sum_text = sum(d["text"] for d in summary_data)
    sum_out_guard = sum(d["out_guard"] for d in summary_data)
    sum_total = sum(d["total"] for d in summary_data)
    
    for idx, d in enumerate(summary_data, 1):
        print(f"{idx:<4} | {d['rewrite']:<9.3f} | {d['linker']:<7.3f} | {d['sql_gen']:<9.3f} | {d['sql_refine']:<9.3f} | {d['text']:<10.3f} | {d['out_guard']:<9.3f} | {d['total']:<7.3f}")
        
    print("-" * len(header))
    n = len(summary_data)
    print(f"{'TB':<4} | {sum_rewrite/n:<9.3f} | {sum_linker/n:<7.3f} | {sum_sql_gen/n:<9.3f} | {sum_sql_refine/n:<9.3f} | {sum_text/n:<10.3f} | {sum_out_guard/n:<9.3f} | {sum_total/n:<7.3f}")
    print("=======================================================================================", flush=True)
    
    # Phân tích tỷ trọng
    print("\n🔥 PHÂN TÍCH TỶ TRỌNG THỜI GIAN:", flush=True)
    print(f"1. Sinh SQL (SQLGenerator): {sum_sql_gen/sum_total*100:.1f}%")
    print(f"2. Sinh Text (AnswerGenerator): {sum_text/sum_total*100:.1f}%")
    print(f"3. Re-write / Preflight: {sum_rewrite/sum_total*100:.1f}%")
    print(f"4. Thực thi & Sửa SQL (SQLRefiner): {sum_sql_refine/sum_total*100:.1f}%")
    print(f"5. Output Guardrail: {sum_out_guard/sum_total*100:.1f}%")
    print(f"6. Schema Linking: {sum_linker/sum_total*100:.1f}%")

if __name__ == "__main__":
    run_debug()
