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

QUEST_CHART_CASES = [
    {"id": "QC_01", "mode": "Biểu đồ", "prompt": "Cho biết cơ cấu số lượng hộ nghèo theo từng huyện năm 2023", "new_session": True},
    {"id": "QC_02", "mode": "Biểu đồ", "prompt": "Cho biết cơ cấu giới tính là hộ nghèo của thành phố Gia Nghĩa năm 2024", "new_session": True},
    {"id": "QC_03", "mode": "Biểu đồ", "prompt": "Top 5 huyện có số lượng hộ nghèo thấp nhất năm 2024", "new_session": True},
    {"id": "QC_04", "mode": "Biểu đồ", "prompt": "Hiển thị biểu đồ xu hướng hộ nghèo và cận nghèo của thành phố gia nghĩa và huyện tuy đức qua các năm", "new_session": True},
    {"id": "QC_05", "mode": "Biểu đồ", "prompt": "Biểu đồ tỷ lệ hộ cận nghèo từ năm 2023 đến 2024 của thành phố gia nghĩa.", "new_session": True},
    {"id": "QC_06", "mode": "Biểu đồ", "prompt": "Tôi muốn nhìn nhanh thông qua biểu đồ xem số hộ nghèo ở từng huyện thay đổi như thế nào từ 2023 sang 2024.", "new_session": True},
    {"id": "QC_07", "mode": "Biểu đồ", "prompt": "Hiện nay hộ nghèo và hộ cận nghèo đang chiếm tỷ trọng ra sao trên toàn tỉnh năm 2024?", "new_session": True},
    {"id": "QC_08", "mode": "Biểu đồ", "prompt": "Lập biểu đồ các huyện có số hộ nghèo cao nhất năm 2023, chỉ cần lấy vài huyện nổi bật thôi.", "new_session": True},
    {"id": "QC_09", "mode": "Biểu đồ", "prompt": "Tôi muốn xem phân bố hộ nghèo và hộ cận nghèo qua các năm theo từng huyện để dễ so sánh.", "new_session": True},
    {"id": "QC_10", "mode": "Biểu đồ", "prompt": "Trong huyện Tuy Đức, xã nào đang có nhiều hộ nghèo nhất?", "new_session": True},
]

def main():
    semantic_layer_path = PROJECT_ROOT / "data" / "Processed" / "metadata" / "query_control" / "semantic_layer.json"
    output_data_path = PROJECT_ROOT / "artifacts" / "test_results" / "chart_10_context_retrieval_report.json"
    output_data_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("[Context Retrieval Audit] Khởi tạo SchemaLinker & SQLGenerator...")
    t_init_0 = time.perf_counter()
    linker = SchemaLinker(semantic_layer_path)
    generator = SQLGenerator()
    t_init = (time.perf_counter() - t_init_0) * 1000
    print(f"[Context Retrieval Audit] Khởi tạo xong trong {t_init:.2f} ms.")
    
    # Đếm tổng số lượng columns/dimensions/measures trong semantic_layer
    total_dims = len(linker.semantic_layer.get("dimensions", {}))
    total_meas = len(linker.semantic_layer.get("measures", {}))
    total_semantic_items = total_dims + total_meas
    
    all_physical_cols = set()
    for item in list(linker.semantic_layer.get("dimensions", {}).values()) + list(linker.semantic_layer.get("measures", {}).values()):
        for col in item.get("physical_columns", []):
            all_physical_cols.add(col)
    total_physical_columns = len(all_physical_cols)
    total_rule_groups = len(generator.RULE_INDEX)
    
    print(f"[Context Retrieval Audit] Tổng số semantic items trong csdl: {total_semantic_items} (Dimensions: {total_dims}, Measures: {total_meas})")
    print(f"[Context Retrieval Audit] Tổng số physical columns thực tế: {total_physical_columns} (trên 2 bảng households, members)")
    print(f"[Context Retrieval Audit] Tổng số nhóm rule tối đa (RULE_INDEX): {total_rule_groups}")
    
    # Lấy 10 câu đầu tiên (QC_01 -> QC_10)
    test_cases = QUEST_CHART_CASES[0:10]
    
    rule_map = {val: key for key, val in generator.RULE_INDEX.items()}
    
    results = []
    total_schema_latency = 0.0
    total_prompt_latency = 0.0
    total_columns_count = 0
    total_prompt_chars = 0
    total_rules_count = 0
    total_tables_count = 0
    
    for tc in test_cases:
        qid = tc["id"]
        prompt = tc["prompt"]
        
        # 1. Schema Linking
        t0 = time.perf_counter()
        schema_info = linker.link(prompt)
        t_link = (time.perf_counter() - t0) * 1000
        total_schema_latency += t_link
        
        relevant_tables = schema_info.get("relevant_tables", [])
        relevant_columns = schema_info.get("relevant_columns", [])
        schema_context = schema_info.get("schema_context", "")
        
        # 2. Rule Pruning & Prompt Building
        t1 = time.perf_counter()
        active_rule_texts = generator._prune_rules(prompt, schema_info)
        active_rule_names = [rule_map.get(rt, "unknown") for rt in active_rule_texts]
        
        tables_str = ", ".join(relevant_tables)
        rules_str = "\n\n".join(active_rule_texts)
        examples_str = """Ví dụ:\nCâu hỏi: "Có bao nhiêu hộ nghèo ở huyện Đắk Song năm 2024?"\nSQL: SELECT "administrative.year" AS "Năm", COUNT(*) AS "Số hộ nghèo" FROM households WHERE classify = 'Hộ nghèo' AND "administrative.district" ILIKE '%Đắk Song%' AND "administrative.year" = 2024 GROUP BY "administrative.year";"""
        
        system_prompt = f"""Bạn là chuyên gia DuckDB SQL. Viết DUY NHẤT 1 câu lệnh SQL trả lời người dùng.\nBảng: {tables_str}\n{schema_context}\n\nQUY TẮC BẮT BUỘC:\n{rules_str}\n\n{examples_str}"""
        
        t_prompt = (time.perf_counter() - t1) * 1000
        total_prompt_latency += t_prompt
        
        col_count = len(relevant_columns)
        rule_count = len(active_rule_names)
        table_count = len(relevant_tables)
        prompt_chars = len(system_prompt)
        est_tokens = prompt_chars // 3.5
        
        total_columns_count += col_count
        total_prompt_chars += prompt_chars
        total_rules_count += rule_count
        total_tables_count += table_count
        
        # Đánh giá độ tối ưu (Context Optimization Check)
        # Kiểm tra xem có đưa vào bảng members hay các rule không liên quan không
        unrelated_rules_injected = []
        if "join" in active_rule_names and not any(w in prompt.lower() for w in ["thành viên", "nhân khẩu", "từng người", "vợ/chồng", "con của"]):
            unrelated_rules_injected.append("join")
        if "deprivation" in active_rule_names and not any(w in prompt.lower() for w in ["thiếu hụt", "dịch vụ", "nước", "nhà tiêu", "việc làm", "bảo hiểm", "dinh dưỡng", "giáo dục", "nhà ở", "viễn thông"]):
            unrelated_rules_injected.append("deprivation")
        if "children" in active_rule_names and not any(w in prompt.lower() for w in ["trẻ em", "bhyt", "giáo dục", "y tế", "dinh dưỡng"]):
            unrelated_rules_injected.append("children")
        if "reason" in active_rule_names and not any(w in prompt.lower() for w in ["nguyên nhân", "lý do", "thiếu đất", "thiếu vốn", "thiếu lao động", "ốm đau"]):
            unrelated_rules_injected.append("reason")
            
        is_optimized = len(unrelated_rules_injected) == 0 and table_count == (2 if any(w in prompt.lower() for w in ["thành viên", "nhân khẩu"]) else 1)
        
        case_result = {
            "id": qid,
            "prompt": prompt,
            "schema_link_latency_ms": round(t_link, 2),
            "prompt_build_latency_ms": round(t_prompt, 2),
            "total_context_latency_ms": round(t_link + t_prompt, 2),
            "table_count": table_count,
            "relevant_tables": relevant_tables,
            "col_count": col_count,
            "relevant_columns": relevant_columns,
            "schema_context_lines": len(schema_context.splitlines()),
            "rule_count": rule_count,
            "active_rule_names": active_rule_names,
            "system_prompt_chars": prompt_chars,
            "est_tokens": int(est_tokens),
            "is_optimized": is_optimized,
            "unrelated_rules_injected": unrelated_rules_injected
        }
        results.append(case_result)
        
    avg_col = total_columns_count / len(test_cases)
    avg_chars = total_prompt_chars / len(test_cases)
    avg_tokens = (total_prompt_chars / 3.5) / len(test_cases)
    avg_rules = total_rules_count / len(test_cases)
    avg_tables = total_tables_count / len(test_cases)
    avg_schema_ms = total_schema_latency / len(test_cases)
    avg_prompt_ms = total_prompt_latency / len(test_cases)
    
    summary = {
        "metadata": {
            "total_physical_columns_in_db": total_physical_columns,
            "total_semantic_items_in_db": total_semantic_items,
            "total_rule_groups_in_db": total_rule_groups,
            "total_tables_in_db": 2
        },
        "averages_top_10_chart": {
            "avg_schema_link_latency_ms": round(avg_schema_ms, 2),
            "avg_prompt_build_latency_ms": round(avg_prompt_ms, 2),
            "avg_total_context_latency_ms": round(avg_schema_ms + avg_prompt_ms, 2),
            "avg_tables_injected": round(avg_tables, 2),
            "avg_columns_retrieved": round(avg_col, 2),
            "avg_rules_injected": round(avg_rules, 2),
            "avg_system_prompt_chars": round(avg_chars, 2),
            "avg_system_prompt_est_tokens": round(avg_tokens, 2),
            "optimized_rate": f"{sum(1 for c in results if c['is_optimized'])}/{len(test_cases)}"
        },
        "cases": results
    }
    
    with open(output_data_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
        
    print("\n=== BẢNG TỔNG HỢP CHI TIẾT CONTEXT RETRIEVAL (CÂU 1 -> 10 QUERY CHART) ===")
    print(f"{'ID':<6} | {'Số Bảng':<8} | {'Số Cột':<8} | {'Số Rule':<8} | {'Chars/Tokens':<13} | {'Tối ưu?':<8} | {'Rules được tiêm (Injected Rules)'}")
    print("-" * 105)
    for c in results:
        rules_str = ", ".join(c["active_rule_names"])
        opt_str = "✅ Chuẩn" if c["is_optimized"] else f"⚠️ Nhiễu ({c['unrelated_rules_injected']})"
        print(f"{c['id']:<6} | {c['table_count']:<8} | {c['col_count']:<8} | {c['rule_count']:<8} | {c['system_prompt_chars']}/{c['est_tokens']:<6} | {opt_str:<8} | {rules_str}")
        
    print("-" * 105)
    print(f"Khái quát TRUNG BÌNH: {avg_tables:.1f} bảng/2 bảng | {avg_col:.1f} cột/{total_physical_columns} cột | {avg_rules:.1f} rule/{total_rule_groups} rule | ~{avg_tokens:.0f} tokens | Latency: {avg_schema_ms + avg_prompt_ms:.2f} ms")

if __name__ == "__main__":
    main()
