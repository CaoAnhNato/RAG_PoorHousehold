# -*- coding: utf-8 -*-
import json
import time
from pathlib import Path
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.query_control.agentic.schema_linker import SchemaLinker
from src.query_control.agentic.sql_generator import SQLGenerator

def main():
    semantic_layer_path = PROJECT_ROOT / "data" / "Processed" / "metadata" / "query_control" / "semantic_layer.json"
    test_50_path = PROJECT_ROOT / "artifacts" / "test_results" / "test_50_results.json"
    output_data_path = PROJECT_ROOT / "artifacts" / "test_results" / "debug_50_context_retrieval_data.json"
    
    print("[Debug Context Retrieval] Khởi tạo SchemaLinker & SQLGenerator...")
    t_init_0 = time.perf_counter()
    linker = SchemaLinker(semantic_layer_path)
    generator = SQLGenerator()
    t_init = (time.perf_counter() - t_init_0) * 1000
    print(f"[Debug Context Retrieval] Khởi tạo xong trong {t_init:.2f} ms.")
    
    with open(test_50_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        test_cases = data.get("passed_list", []) + data.get("failed_list", []) + data.get("results", [])
    else:
        test_cases = data
        
    print(f"[Debug Context Retrieval] Đang phân tích {len(test_cases)} câu hỏi...")
    
    # Map rule text back to rule name
    rule_map = {val: key for key, val in generator.RULE_INDEX.items()}
    
    results = []
    total_schema_latency = 0.0
    total_prompt_latency = 0.0
    total_columns_count = 0
    total_prompt_chars = 0
    total_rules_count = 0
    
    for idx, tc in enumerate(test_cases):
        qid = tc.get("id", f"Q_{idx}")
        prompt = tc.get("prompt", "")
        exec_time_sec = tc.get("exec_time_sec", 0.0)
        status = tc.get("status", "")
        
        # 1. Measure Schema Linking
        t0 = time.perf_counter()
        schema_info = linker.link(prompt)
        t_link = (time.perf_counter() - t0) * 1000
        total_schema_latency += t_link
        
        relevant_tables = schema_info.get("relevant_tables", [])
        relevant_columns = schema_info.get("relevant_columns", [])
        schema_context = schema_info.get("schema_context", "")
        
        # 2. Measure Prompt Building & Rule Pruning
        t1 = time.perf_counter()
        active_rule_texts = generator._prune_rules(prompt)
        active_rule_names = [rule_map.get(rt, "unknown") for rt in active_rule_texts]
        
        # Simulate generate prompt building (without calling LLM)
        tables_str = ", ".join(relevant_tables)
        rules_str = "\n\n".join(active_rule_texts)
        examples_str = """Ví dụ:
Câu hỏi: "Có bao nhiêu hộ nghèo ở huyện Đắk Song năm 2024?"
SQL: SELECT "administrative.year" AS "Năm", COUNT(*) AS "Số hộ nghèo" FROM households WHERE classify = 'Hộ nghèo' AND "administrative.district" ILIKE '%Đắk Song%' AND "administrative.year" = 2024 GROUP BY "administrative.year";"""
        
        system_prompt = f"""Bạn là chuyên gia DuckDB SQL. Viết DUY NHẤT 1 câu lệnh SQL trả lời người dùng.
Bảng: {tables_str}
{schema_context}

QUY TẮC BẮT BUỘC:
{rules_str}

{examples_str}"""
        
        t_prompt = (time.perf_counter() - t1) * 1000
        total_prompt_latency += t_prompt
        
        col_count = len(relevant_columns)
        rule_count = len(active_rule_names)
        prompt_chars = len(system_prompt)
        est_tokens = prompt_chars // 3.5
        
        total_columns_count += col_count
        total_prompt_chars += prompt_chars
        total_rules_count += rule_count
        
        # Check specific column presence for analysis
        has_host_name = "host_name" in relevant_columns
        has_rel_host = "relationship_to_host" in relevant_columns or "member.relationshipToHost" in schema_context
        
        case_result = {
            "id": qid,
            "prompt": prompt,
            "exec_time_sec": exec_time_sec,
            "status": status,
            "context_retrieval": {
                "schema_link_latency_ms": round(t_link, 2),
                "prompt_build_latency_ms": round(t_prompt, 2),
                "total_context_latency_ms": round(t_link + t_prompt, 2),
                "relevant_tables": relevant_tables,
                "columns_count": col_count,
                "relevant_columns": relevant_columns,
                "schema_context_lines": len(schema_context.splitlines()),
                "raw_schema_context": schema_context,
                "rules_count": rule_count,
                "active_rule_names": active_rule_names,
                "system_prompt_chars": prompt_chars,
                "raw_system_prompt": system_prompt,
                "est_tokens": int(est_tokens),
                "analysis_flags": {
                    "has_host_name_col": has_host_name,
                    "has_relationship_to_host_injected": has_rel_host,
                    "is_multi_table": len(relevant_tables) > 1
                }
            }
        }
        results.append(case_result)
        
    avg_col = total_columns_count / len(test_cases)
    avg_chars = total_prompt_chars / len(test_cases)
    avg_tokens = (total_prompt_chars / 3.5) / len(test_cases)
    avg_rules = total_rules_count / len(test_cases)
    avg_schema_ms = total_schema_latency / len(test_cases)
    avg_prompt_ms = total_prompt_latency / len(test_cases)
    
    summary = {
        "total_cases": len(test_cases),
        "averages": {
            "avg_schema_link_latency_ms": round(avg_schema_ms, 2),
            "avg_prompt_build_latency_ms": round(avg_prompt_ms, 2),
            "avg_total_context_latency_ms": round(avg_schema_ms + avg_prompt_ms, 2),
            "avg_columns_retrieved": round(avg_col, 2),
            "avg_rules_injected": round(avg_rules, 2),
            "avg_system_prompt_chars": round(avg_chars, 2),
            "avg_system_prompt_est_tokens": round(avg_tokens, 2)
        },
        "cases": results
    }
    
    with open(output_data_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
        
    print(f"\n[Debug Context Retrieval] Hoàn tất! Đã lưu kết quả tại {output_data_path}")
    print(f"=== TÓM TẮT THỐNG KÊ (50 CÂU HỎI) ===")
    print(f"- Avg Schema Linking Latency: {avg_schema_ms:.2f} ms")
    print(f"- Avg Prompt Building Latency: {avg_prompt_ms:.2f} ms")
    print(f"- Avg Columns Retrieved: {avg_col:.1f} cột / câu hỏi")
    print(f"- Avg Rules Injected: {avg_rules:.1f} nhóm rule / câu hỏi")
    print(f"- Avg System Prompt Length: {avg_chars:.0f} chars (~{avg_tokens:.0f} tokens)")

if __name__ == "__main__":
    main()
