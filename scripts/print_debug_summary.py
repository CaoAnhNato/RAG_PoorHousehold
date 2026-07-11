# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parents[1]
data_path = PROJECT_ROOT / "artifacts" / "test_results" / "debug_50_context_retrieval_data.json"

with open(data_path, "r", encoding="utf-8") as f:
    data = json.load(f)

print("=== 1. THỐNG KÊ TRUNG BÌNH TOÀN BỘ 50 CÂU HỎI ===")
for k, v in data["averages"].items():
    print(f"  {k}: {v}")

print("\n=== 2. CHI TIẾT CÁC CÂU HỎI ĐIỂN HÌNH (QA_05, QA_07, QA_08) ===")
target_ids = ["QA_05", "QA_07", "QA_08"]
for c in data["cases"]:
    if c["id"] in target_ids:
        print(f"\n--- [{c['id']}] {c['prompt']} ---")
        print(f"  Exec Time (thực tế test): {c['exec_time_sec']}s | Status: {c['status']}")
        cr = c["context_retrieval"]
        print(f"  Context Latency: {cr['total_context_latency_ms']} ms (SchemaLink: {cr['schema_link_latency_ms']}ms, PromptBuild: {cr['prompt_build_latency_ms']}ms)")
        print(f"  Tables: {cr['relevant_tables']}")
        print(f"  Columns Count: {cr['columns_count']} | Active Rules: {cr['active_rule_names']}")
        print(f"  Prompt Size: {cr['system_prompt_chars']} chars (~{cr['est_tokens']} tokens)")
        print(f"  Analysis Flags: {cr['analysis_flags']}")
        print(f"  Retrieved Columns: {cr['relevant_columns']}")

print("\n=== 3. TOP 5 CÂU HỎI CÓ NHIỀU CỘT NHẤT (NOISIEST CONTEXT) ===")
sorted_cases = sorted(data["cases"], key=lambda x: x["context_retrieval"]["columns_count"], reverse=True)
for c in sorted_cases[:5]:
    cr = c["context_retrieval"]
    print(f"  [{c['id']}] '{c['prompt']}' -> {cr['columns_count']} cột, {cr['est_tokens']} tokens, {cr['active_rule_names']}")

print("\n=== 4. PHÂN TÍCH QUY TẮC & BẢNG ===")
multi_table_count = sum(1 for c in data["cases"] if c["context_retrieval"]["analysis_flags"]["is_multi_table"])
print(f"  Số câu hỏi bị kéo thêm bảng members (multi-table): {multi_table_count}/{len(data['cases'])}")
