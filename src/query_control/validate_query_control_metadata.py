# -*- coding: utf-8 -*-
"""
Module validate_query_control_metadata thực thi kiểm tra tính toàn vẹn
và tuân thủ quy tắc của toàn bộ các file metadata được sinh ra.
"""

import json
import os
import sys
from pathlib import Path
import datetime as dt

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "Processed"
METADATA_DIR = PROCESSED_DIR / "metadata"
QUERY_CONTROL_METADATA_DIR = METADATA_DIR / "query_control"
REPORT_PATH = QUERY_CONTROL_METADATA_DIR / "metadata_build_report.md"

def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    errors = []
    successes = []
    
    # 1. Kiểm tra validation_rules.json
    rules_file = QUERY_CONTROL_METADATA_DIR / "validation_rules.json"
    if not rules_file.exists():
        errors.append("Thiếu file validation_rules.json!")
    else:
        try:
            with open(rules_file, "r", encoding="utf-8") as f:
                rules = json.load(f)
            successes.append("validation_rules.json hợp lệ.")
        except Exception as e:
            errors.append(f"Lỗi cú pháp validation_rules.json: {e}")
            
    # 2. Kiểm tra schema_graph.json
    schema_file = QUERY_CONTROL_METADATA_DIR / "schema_graph.json"
    if not schema_file.exists():
        errors.append("Thiếu file schema_graph.json!")
    else:
        try:
            with open(schema_file, "r", encoding="utf-8") as f:
                graph = json.load(f)
            nodes = graph.get("nodes", {})
            if "households" not in nodes:
                errors.append("schema_graph.json thiếu node 'households'!")
            if "members" not in nodes:
                errors.append("schema_graph.json thiếu node 'members'!")
            successes.append("schema_graph.json hợp lệ và đầy đủ nodes.")
        except Exception as e:
            errors.append(f"Lỗi cú pháp schema_graph.json: {e}")
            
    # 3. Kiểm tra semantic_layer.json
    semantic_file = QUERY_CONTROL_METADATA_DIR / "semantic_layer.json"
    if not semantic_file.exists():
        errors.append("Thiếu file semantic_layer.json!")
    else:
        try:
            with open(semantic_file, "r", encoding="utf-8") as f:
                sem = json.load(f)
            if "dimensions" not in sem or "metrics" not in sem:
                errors.append("semantic_layer.json thiếu trường 'dimensions' hoặc 'metrics'!")
            successes.append("semantic_layer.json hợp lệ.")
        except Exception as e:
            errors.append(f"Lỗi cú pháp semantic_layer.json: {e}")
            
    # 4. Kiểm tra domain_gate_config.json
    gate_file = QUERY_CONTROL_METADATA_DIR / "domain_gate_config.json"
    if not gate_file.exists():
        errors.append("Thiếu file domain_gate_config.json!")
    else:
        try:
            with open(gate_file, "r", encoding="utf-8") as f:
                gate = json.load(f)
            if "routing_labels" not in gate:
                errors.append("domain_gate_config.json thiếu 'routing_labels'!")
            successes.append("domain_gate_config.json hợp lệ.")
        except Exception as e:
            errors.append(f"Lỗi cú pháp domain_gate_config.json: {e}")
            
    # 5. Kiểm tra planner_prompt.md và general_answer_prompt.md
    for prompt_name in ["planner_prompt.md", "general_answer_prompt.md"]:
        prompt_file = QUERY_CONTROL_METADATA_DIR / prompt_name
        if not prompt_file.exists():
            errors.append(f"Thiếu file prompt: {prompt_name}!")
        elif prompt_file.stat().st_size == 0:
            errors.append(f"File prompt '{prompt_name}' trống!")
        else:
            successes.append(f"Prompt '{prompt_name}' hợp lệ.")
            
    # 6. Ghi kết quả vào báo cáo (Tránh ghi lặp phần 5)
    report_additions = []
    report_additions.append("## 5. Kết quả kiểm định tự động Metadata (Self-Validation)")
    report_additions.append(f"**Thời gian kiểm định:** {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if errors:
        report_additions.append("### ❌ Lỗi kiểm định phát hiện:")
        for err in errors:
            report_additions.append(f"- [FAIL] {err}")
    else:
        report_additions.append("###  Toàn bộ file metadata đã vượt qua bài kiểm định thành công!")
        for succ in successes:
            report_additions.append(f"- [PASS] {succ}")
            
    # Đọc nội dung báo cáo cũ và cắt bỏ phần 5 cũ nếu có
    report_text = ""
    if REPORT_PATH.exists():
        with open(REPORT_PATH, "r", encoding="utf-8") as f:
            report_text = f.read()
            
    section_marker = "## 5. Kết quả kiểm định tự động Metadata"
    if section_marker in report_text:
        report_text = report_text.split(section_marker)[0].rstrip()
        
    new_report_text = report_text + "\n\n" + "\n".join(report_additions)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(new_report_text.strip() + "\n")
        
    print(f"Đã chạy kiểm định metadata. Phát hiện {len(errors)} lỗi và {len(successes)} thành công.")
    if errors:
        print("Chi tiết lỗi kiểm định đã ghi vào báo cáo metadata_build_report.md.")
        sys.exit(1)
    else:
        print("Tất cả kiểm định thành công!")
        sys.exit(0)

if __name__ == "__main__":
    main()
