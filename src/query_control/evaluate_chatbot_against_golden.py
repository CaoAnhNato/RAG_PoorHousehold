# -*- coding: utf-8 -*-
"""
Module evaluate_chatbot_against_golden thực hiện đánh giá hiệu năng và độ chính xác của
Chatbot Q&A MVP đối chiếu với bộ câu hỏi chuẩn (Golden Dataset) gồm 30 câu hỏi.
Đo lường các chỉ số: route_accuracy, query_plan_metric_accuracy, sql_execution_success, result_exact_match.
"""

from __future__ import annotations
import os
import sys
import json
import time
import argparse
from pathlib import Path
from typing import Any
import pandas as pd
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

sys.path.append(str(PROJECT_ROOT))
from src.query_control.semantic_retriever import SemanticRetriever
from src.query_control.domain_gate import DomainGate
from src.query_control.query_planner import QueryPlanner
from src.query_control.sql_compiler import SQLCompiler
from src.query_control.data_engine import DuckDBEngine
from src.query_control.query_cache import QueryCache
from src.query_control.observability import ObservabilityLogger
from src.query_control.clarification_engine import ClarificationEngine
from src.query_control.conversation_memory import ConversationMemory
from src.query_control.answer_engine import ChatbotAnswerEngine

GOLDEN_DIR = PROJECT_ROOT / "Evaluation" / "golden_questions"
GOLDEN_JSONL_PATH = GOLDEN_DIR / "golden_questions_30.jsonl"
EVAL_RESULTS_JSONL_PATH = GOLDEN_DIR / "evaluation_results.jsonl"
EVAL_REPORT_MD_PATH = GOLDEN_DIR / "evaluation_report.md"

def load_golden_dataset(file_path: Path) -> list[dict[str, Any]]:
    """
    Đọc bộ câu hỏi vàng từ tệp JSONL.

    Args:
        file_path (Path): Đường dẫn tới tệp JSONL chứa bộ câu hỏi vàng.

    Returns:
        list[dict[str, Any]]: Danh sách các bản ghi câu hỏi vàng.

    Lưu ý:
        Tệp JSONL cần phải tồn tại và đúng định dạng được sinh ra từ generate_golden_questions.py.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Không tìm thấy tệp câu hỏi vàng tại {file_path}. Vui lòng chạy sinh trước.")
    
    dataset = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                dataset.append(json.loads(line.strip()))
    return dataset

def compare_data_results(actual: list[dict[str, Any]], expected: list[dict[str, Any]], expected_truncated: bool = False) -> dict[str, Any]:
    """
    So sánh kết quả truy vấn thực tế của chatbot với kết quả vàng làm chuẩn (Ground Truth).

    Args:
        actual (list[dict[str, Any]]): Kết quả thực tế dạng danh sách bản ghi thu được từ chatbot.
        expected (list[dict[str, Any]]): Kết quả chuẩn dạng danh sách bản ghi từ Golden Dataset.
        expected_truncated (bool): Cho biết kết quả vàng có bị rút gọn hay không.

    Returns:
        dict[str, Any]: Kết quả chi tiết cuộc so sánh bao gồm:
            - exact_match (bool): Trùng khớp hoàn hảo hay không.
            - similarity (float): Tỷ lệ số dòng trùng khớp trên tổng số dòng.
            - reason (str): Lý do chi tiết hoặc kết quả khớp.
    """
    if not actual and not expected:
        return {"exact_match": True, "similarity": 1.0, "reason": "Cả hai kết quả đều rỗng"}
    if not actual or not expected:
        return {"exact_match": False, "similarity": 0.0, "reason": "Một bên rỗng và một bên có dữ liệu"}

    # Chuẩn hóa giá trị các trường trong dòng
    def normalize_row(row):
        normalized = {}
        for k, v in row.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                normalized[k] = round(v, 2)
            elif v is None:
                normalized[k] = None
            else:
                normalized[k] = str(v).strip()
        return normalized

    actual_norm = [normalize_row(r) for r in actual]
    expected_norm = [normalize_row(r) for r in expected]

    # Phân tách phần số (metrics) và phần chữ (dimensions) của một dòng không phụ thuộc vào key
    def get_metrics_and_dims_values(row):
        metrics_vals = []
        dims_vals = []
        for k, v in row.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                metrics_vals.append(v)
            else:
                dims_vals.append(v)
        # Sắp xếp để không phụ thuộc vào thứ tự cột/key
        return tuple(sorted(metrics_vals)), tuple(sorted([str(x) for x in dims_vals]))

    # Nhóm danh sách kết quả vàng theo nhóm giá trị của metrics
    expected_groups = []
    if expected_norm:
        curr_metrics, curr_dims = get_metrics_and_dims_values(expected_norm[0])
        curr_group = [curr_dims]
        for r in expected_norm[1:]:
            m, d = get_metrics_and_dims_values(r)
            if m == curr_metrics:
                curr_group.append(d)
            else:
                expected_groups.append((curr_metrics, curr_group))
                curr_metrics = m
                curr_group = [d]
        expected_groups.append((curr_metrics, curr_group))

    # Nhóm danh sách kết quả thực tế theo nhóm giá trị của metrics
    actual_groups = {}
    for r in actual_norm:
        m, d = get_metrics_and_dims_values(r)
        if m not in actual_groups:
            actual_groups[m] = []
        actual_groups[m].append(d)

    # Đối sánh từng nhóm giữa kết quả vàng và kết quả thực tế
    match_count = 0
    total_expected = len(expected_norm)
    
    for m, exp_dims in expected_groups:
        if m not in actual_groups:
            continue
        act_dims = actual_groups[m]
        
        # Đếm số dòng trùng khớp thông qua multiset intersection
        act_dims_cp = list(act_dims)
        group_matches = 0
        for ed in exp_dims:
            if ed in act_dims_cp:
                act_dims_cp.remove(ed)
                group_matches += 1
        match_count += group_matches

    similarity = match_count / total_expected
    exact_match = (match_count == total_expected)
    
    # Nếu không phải là dạng rút gọn, số lượng dòng phải bằng nhau hoàn toàn
    if exact_match and not expected_truncated and len(actual_norm) != len(expected_norm):
        exact_match = False

    return {
        "exact_match": exact_match,
        "similarity": similarity,
        "reason": "Khớp hoàn hảo tất cả các dòng" if exact_match else f"Chỉ khớp {match_count}/{total_expected} dòng"
    }

def compare_query_plans(actual_plan: dict[str, Any], gold_plan: dict[str, Any]) -> dict[str, Any]:
    """
    So sánh kế hoạch truy vấn thực tế với kế hoạch vàng để đánh giá mức độ chính xác của LLM Planner.

    Args:
        actual_plan (dict[str, Any]): Kế hoạch truy vấn thực tế do Chatbot sinh ra.
        gold_plan (dict[str, Any]): Kế hoạch vàng làm chuẩn từ Golden Dataset.

    Returns:
        dict[str, Any]: Điểm số chi tiết bao gồm:
            - metrics_accuracy (float): Điểm chính xác của metrics.
            - dimensions_accuracy (float): Điểm chính xác của dimensions.
            - filters_accuracy (float): Điểm chính xác của bộ lọc (filters).
            - overall_accuracy (float): Điểm trung bình cộng của 3 thành phần trên.

    Lưu ý:
        Sử dụng Jaccard Similarity (Intersection over Union) để đo lường độ trùng khớp của các tập hợp từ khóa.
    """
    if not actual_plan:
        return {
            "metrics_accuracy": 0.0,
            "dimensions_accuracy": 0.0,
            "filters_accuracy": 0.0,
            "overall_accuracy": 0.0
        }
        
    # 1. Đo lường chính xác Metrics
    act_metrics = set(actual_plan.get("metrics", []))
    gold_metrics = set(gold_plan.get("metrics", []))
    if not act_metrics and not gold_metrics:
        metrics_acc = 1.0
    elif not act_metrics or not gold_metrics:
        metrics_acc = 0.0
    else:
        metrics_acc = len(act_metrics.intersection(gold_metrics)) / len(act_metrics.union(gold_metrics))
        
    # 2. Đo lường chính xác Dimensions
    act_dims = set(actual_plan.get("dimensions", []))
    gold_dims = set(gold_plan.get("dimensions", []))
    if not act_dims and not gold_dims:
        dims_acc = 1.0
    elif not act_dims or not gold_dims:
        dims_acc = 0.0
    else:
        dims_acc = len(act_dims.intersection(gold_dims)) / len(act_dims.union(gold_dims))
        
    # 3. Đo lường chính xác Filters
    act_filt_fields = set(f.get("field") for f in actual_plan.get("filters", []) if isinstance(f, dict) and f.get("field"))
    gold_filt_fields = set(f.get("field") for f in gold_plan.get("filters", []) if isinstance(f, dict) and f.get("field"))
    if not act_filt_fields and not gold_filt_fields:
        filters_acc = 1.0
    elif not act_filt_fields or not gold_filt_fields:
        filters_acc = 0.0
    else:
        filters_acc = len(act_filt_fields.intersection(gold_filt_fields)) / len(act_filt_fields.union(gold_filt_fields))
        
    overall = (metrics_acc + dims_acc + filters_acc) / 3.0
    return {
        "metrics_accuracy": metrics_acc,
        "dimensions_accuracy": dims_acc,
        "filters_accuracy": filters_acc,
        "overall_accuracy": overall
    }

def main():
    """
    Hàm thực thi chính chạy luồng đánh giá tự động trên toàn bộ tệp Golden Dataset.
    """
    parser = argparse.ArgumentParser(description="Đánh giá hiệu năng Chatbot Q&A với Golden Set.")
    parser.add_argument("--n", type=int, default=30, help="Số lượng câu hỏi cần đánh giá.")
    parser.add_argument("--use-cache", action="store_true", help="Giữ lại cache giữa các câu hỏi để kiểm thử cache hit.")
    parser.add_argument("--verbose", action="store_true", help="In thông tin log chi tiết.")
    args = parser.parse_args()

    print("=" * 60)
    print(f"BẮT ĐẦU ĐÁNH GIÁ CHATBOT MVP VỚI BỘ CÂU HỎI VÀNG (N = {args.n})")
    print("=" * 60)

    # 1. Đường dẫn các tệp cấu hình
    processed_dir = PROJECT_ROOT / "Processed"
    metadata_dir = processed_dir / "metadata" / "query_control"
    
    schema_graph_path = metadata_dir / "schema_graph.json"
    semantic_layer_path = metadata_dir / "semantic_layer.json"
    query_plan_schema_path = metadata_dir / "query_plan_schema.json"
    domain_gate_config_path = metadata_dir / "domain_gate_config.json"
    duckdb_config_path = metadata_dir / "duckdb_config.json"
    cache_config_path = metadata_dir / "cache_config.json"
    observability_config_path = metadata_dir / "observability_config.json"
    clarification_config_path = metadata_dir / "clarification_config.json"
    memory_config_path = metadata_dir / "memory_config.json"
    qdrant_config_path = metadata_dir / "qdrant_index_config.json"

    # Đọc cấu hình Qdrant
    with open(qdrant_config_path, "r", encoding="utf-8") as f:
        qdrant_config = json.load(f)
        
    qdrant_url = qdrant_config.get("qdrant_url", "http://localhost:6333")
    collection_name = qdrant_config.get("collection_name", "query_control_semantic")
    embedding_model = os.environ.get("EMBEDDING_MODEL")
    if not embedding_model:
        embedding_model = os.environ.get("FPT_EMBEDDING_MODEL_NAME", qdrant_config.get("embedding_model"))

    # 2. Khởi tạo Chatbot Answer Engine
    print("[*] Đang khởi tạo các thành phần Chatbot...")
    retriever = SemanticRetriever(
        qdrant_url=qdrant_url,
        collection_name=collection_name,
        embedding_model=embedding_model
    )
    
    domain_gate = DomainGate(
        config_path=domain_gate_config_path,
        semantic_layer_path=semantic_layer_path,
        semantic_retriever=retriever
    )
    
    planner = QueryPlanner(
        schema_graph_path=schema_graph_path,
        semantic_layer_path=semantic_layer_path,
        query_plan_schema_path=query_plan_schema_path,
        semantic_retriever=retriever
    )
    
    compiler = SQLCompiler(
        schema_graph_path=schema_graph_path,
        semantic_layer_path=semantic_layer_path
    )
    
    data_engine = DuckDBEngine(config_path=str(duckdb_config_path))
    query_cache = QueryCache(config_path=str(cache_config_path))
    observability_logger = ObservabilityLogger(config_path=str(observability_config_path))
    clarification_engine = ClarificationEngine(
        config_path=str(clarification_config_path), 
        semantic_layer_path=str(semantic_layer_path)
    )
    
    session_id = "evaluation_session_999"
    conversation_memory = ConversationMemory(config_path=str(memory_config_path), session_id=session_id)
    
    engine = ChatbotAnswerEngine(
        domain_gate=domain_gate,
        query_planner=planner,
        sql_compiler=compiler,
        data_engine=data_engine,
        query_cache=query_cache,
        observability_logger=observability_logger,
        clarification_engine=clarification_engine,
        conversation_memory=conversation_memory
    )
    print("[+] Khởi tạo thành công!")

    # 3. Tải bộ dữ liệu câu hỏi vàng
    golden_questions = load_golden_dataset(GOLDEN_JSONL_PATH)
    total_gqs = min(len(golden_questions), args.n)
    golden_questions = golden_questions[:total_gqs]

    eval_results = []
    
    # Các biến tích lũy chỉ số tổng thể
    total_route_correct = 0
    total_sql_success = 0
    total_exact_match = 0
    total_plan_accuracy = 0.0
    total_latency_ms = 0.0
    
    # Duyệt qua từng câu hỏi để đánh giá
    for idx, gq in enumerate(golden_questions):
        q_id = gq["id"]
        q_text = gq["question_vi"]
        expected_route = gq["expected_route"]
        gold_sql = gq["gold_sql"]
        gold_result = gq["gold_result"]
        gold_plan = {
            "metrics": gq.get("metrics", []),
            "dimensions": gq.get("dimensions", []),
            "filters": gq.get("filters", [])
        }
        
        print(f"\n[{idx+1}/{total_gqs}] Đang đánh giá {q_id}: '{q_text}'")
        
        # Cô lập phiên hội thoại: Xóa bộ nhớ và cache trước mỗi câu hỏi (nếu không bật --use-cache)
        conversation_memory.clear()
        if not args.use_cache:
            query_cache.clear()
            
        # Ghi nhận thời gian chạy của cả pipeline
        start_time = time.perf_counter()
        res = engine.answer(q_text)
        latency_ms = (time.perf_counter() - start_time) * 1000.0
        total_latency_ms += latency_ms
        
        # 1. Đánh giá Route
        actual_route = res.get("route", "UNKNOWN")
        route_correct = (actual_route == expected_route)
        if not route_correct:
            print(f"DEBUG: {q_id} failed route. Expected: {expected_route}, Got: {actual_route}")
            print(f"DEBUG Response: {json.dumps(res, indent=2, ensure_ascii=False)}")
        if route_correct:
            total_route_correct += 1
            
        # 2. Đánh giá Query Plan
        actual_plan = res.get("query_plan", {})
        plan_comp = compare_query_plans(actual_plan, gold_plan)
        total_plan_accuracy += plan_comp["overall_accuracy"]
        
        # 3. Đánh giá SQL Compilation & Execution Success
        sql_compiled = res.get("sql")
        has_errors = bool(res.get("errors", []))
        sql_success = (sql_compiled is not None and not has_errors)
        if sql_success:
            total_sql_success += 1
            
        # 4. Đánh giá Result Exact Match
        actual_result = res.get("result_preview", [])
        expected_truncated = gq.get("validation", {}).get("result_truncated", False)
        res_comp = compare_data_results(actual_result, gold_result, expected_truncated=expected_truncated)
        if res_comp["exact_match"]:
            total_exact_match += 1
            
        # Tạo bản ghi đánh giá chi tiết
        eval_record = {
            "id": q_id,
            "question_vi": q_text,
            "difficulty": gq["difficulty"],
            "expected_route": expected_route,
            "actual_route": actual_route,
            "route_correct": route_correct,
            "query_plan_metric_accuracy": plan_comp["overall_accuracy"],
            "query_plan_details": plan_comp,
            "gold_sql": gold_sql,
            "actual_sql": sql_compiled,
            "sql_execution_success": sql_success,
            "result_exact_match": res_comp["exact_match"],
            "result_similarity": res_comp["similarity"],
            "result_comparison_reason": res_comp["reason"],
            "latency_ms": latency_ms,
            "errors": res.get("errors", []),
            "checked_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        eval_results.append(eval_record)
        
        if args.verbose:
            print(f"  -> Route: {actual_route} (Khớp: {route_correct})")
            print(f"  -> Plan Accuracy: {plan_comp['overall_accuracy']:.2f}")
            print(f"  -> SQL Success: {sql_success}")
            print(f"  -> Result Exact Match: {res_comp['exact_match']} (Độ tương đồng: {res_comp['similarity']:.2f})")
            print(f"  -> Latency: {latency_ms:.1f} ms")
            if res.get("errors"):
                print(f"  -> Gặp lỗi: {res.get('errors')}")

    # 4. Tính toán các chỉ số tổng hợp
    avg_route_accuracy = total_route_correct / total_gqs
    avg_sql_success = total_sql_success / total_gqs
    avg_exact_match = total_exact_match / total_gqs
    avg_plan_accuracy = total_plan_accuracy / total_gqs
    avg_latency = total_latency_ms / total_gqs

    print("\n" + "=" * 60)
    print("HOÀN THÀNH ĐÁNH GIÁ CHATBOT MVP!")
    print(f"- Số câu hỏi kiểm định: {total_gqs}")
    print(f"- Độ chính xác định tuyến (Route Accuracy): {avg_route_accuracy * 100.0:.2f}%")
    print(f"- Độ tương đồng Query Plan: {avg_plan_accuracy * 100.0:.2f}%")
    print(f"- Tỷ lệ thực thi SQL thành công: {avg_sql_success * 100.0:.2f}%")
    print(f"- Tỷ lệ kết quả khớp tuyệt đối (Exact Match): {avg_exact_match * 100.0:.2f}%")
    print(f"- Thời gian phản hồi trung bình: {avg_latency:.1f} ms")
    print("=" * 60)

    # 5. Xuất kết quả chi tiết ra tệp JSONL
    print(f"[*] Đang ghi kết quả chi tiết ra {EVAL_RESULTS_JSONL_PATH}...")
    with open(EVAL_RESULTS_JSONL_PATH, "w", encoding="utf-8") as f:
        for rec in eval_results:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # 6. Xuất báo cáo đánh giá định dạng Markdown
    print(f"[*] Đang ghi báo cáo tổng hợp ra {EVAL_REPORT_MD_PATH}...")
    
    # Phân loại độ khó
    diff_stats = {}
    for diff in ["easy", "medium", "hard"]:
        diff_recs = [r for r in eval_results if r["difficulty"] == diff]
        if diff_recs:
            diff_stats[diff] = {
                "count": len(diff_recs),
                "route_acc": sum(1 for r in diff_recs if r["route_correct"]) / len(diff_recs),
                "sql_success": sum(1 for r in diff_recs if r["sql_execution_success"]) / len(diff_recs),
                "exact_match": sum(1 for r in diff_recs if r["result_exact_match"]) / len(diff_recs)
            }

    with open(EVAL_REPORT_MD_PATH, "w", encoding="utf-8") as f:
        f.write(f"# BÁO CÁO ĐÁNH GIÁ ĐỘ CHÍNH XÁC CHATBOT Q&A MVP\n\n")
        f.write(f"*Thời gian đánh giá: {time.strftime('%Y-%m-%d %H:%M:%S')}*\n")
        f.write(f"*Tổng số câu hỏi kiểm nghiệm: {total_gqs} câu hỏi*\n\n")
        
        f.write(f"## 1. Tóm Tắt Chỉ Số Hiệu Năng (Overall Metrics)\n\n")
        f.write(f"| Chỉ số đo lường | Kết quả thực tế | Mục tiêu đề ra | Trạng thái |\n")
        f.write(f"| :--- | :---: | :---: | :---: |\n")
        f.write(f"| **Độ chính xác định tuyến (Route Accuracy)** | **{avg_route_accuracy * 100.0:.2f}%** | 95.00% | {'ĐẠT' if avg_route_accuracy >= 0.95 else 'CẦN CẢI THIỆN'} |\n")
        f.write(f"| **Độ tương đồng Query Plan (Planner Accuracy)** | **{avg_plan_accuracy * 100.0:.2f}%** | 90.00% | {'ĐẠT' if avg_plan_accuracy >= 0.90 else 'CẦN CẢI THIỆN'} |\n")
        f.write(f"| **Tỷ lệ thực thi SQL thành công (SQL Exec Success)** | **{avg_sql_success * 100.0:.2f}%** | 90.00% | {'ĐẠT' if avg_sql_success >= 0.90 else 'CẦN CẢI THIỆN'} |\n")
        f.write(f"| **Tỷ lệ kết quả khớp tuyệt đối (Exact Match)** | **{avg_exact_match * 100.0:.2f}%** | 80.00% | {'ĐẠT' if avg_exact_match >= 0.80 else 'CẦN CẢI THIỆN'} |\n")
        f.write(f"| **Thời gian phản hồi trung bình (Avg Latency)** | **{avg_latency:.1f} ms** | < 2000 ms | {'TỐT' if avg_latency < 2000 else 'CẦN TỐI ƯU'} |\n\n")
        
        f.write(f"## 2. Thống Kê Theo Độ Khó (Metrics by Difficulty)\n\n")
        f.write(f"| Độ khó | Số câu hỏi | Route Accuracy | SQL Exec Success | Exact Match |\n")
        f.write(f"| :--- | :---: | :---: | :---: | :---: |\n")
        for diff, stats in diff_stats.items():
            f.write(f"| {diff.upper()} | {stats['count']} | {stats['route_acc'] * 100.0:.1f}% | {stats['sql_success'] * 100.0:.1f}% | {stats['exact_match'] * 100.0:.1f}% |\n")
        f.write("\n")
        
        f.write(f"## 3. Chi Tiết Kết Quả Kiểm Nghiệm Từng Câu Hỏi (Detailed Test Logs)\n\n")
        f.write(f"| ID | Câu hỏi tiếng Việt | Độ khó | Thực thi SQL | Kết quả khớp | Trạng thái |\n")
        f.write(f"| :--- | :--- | :---: | :---: | :---: | :---: |\n")
        for r in eval_results:
            sql_status = "✅ Thành công" if r["sql_execution_success"] else "❌ Thất bại"
            match_status = "✅ Khớp" if r["result_exact_match"] else f"❌ Khớp {r['result_similarity']*100.0:.0f}%"
            status = "🟢 ĐẠT" if r["sql_execution_success"] and r["result_exact_match"] else "🔴 LỖI"
            f.write(f"| {r['id']} | {r['question_vi']} | {r['difficulty'].upper()} | {sql_status} | {match_status} | {status} |\n")
        f.write("\n")
        
        # Liệt kê các câu hỏi bị lỗi để nhà phát triển dễ dàng sửa lỗi
        failed_questions = [r for r in eval_results if not (r["sql_execution_success"] and r["result_exact_match"])]
        if failed_questions:
            f.write(f"## 4. Danh Sách Các Câu Hỏi Lỗi Cần Khắc Phục (Failed Cases & Errors)\n\n")
            for r in failed_questions:
                f.write(f"### ❌ {r['id']}: {r['question_vi']} ({r['difficulty'].upper()})\n")
                f.write(f"- **Định tuyến thực tế:** `{r['actual_route']}` (Yêu cầu: `{r['expected_route']}`)\n")
                f.write(f"- **Độ tương đồng Query Plan:** `{r['query_plan_metric_accuracy']*100.0:.1f}%`\n")
                if r["errors"]:
                    f.write(f"- **Danh sách lỗi ghi nhận:**\n")
                    for err in r["errors"]:
                        f.write(f"  - `[{err.get('code')}]` {err.get('message')}\n")
                if r["actual_sql"]:
                    f.write(f"- **SQL Chatbot sinh ra:**\n```sql\n{r['actual_sql']}\n```\n")
                    f.write(f"- **SQL Vàng đối chiếu:**\n```sql\n{r['gold_sql']}\n```\n")
                f.write(f"- **Chi tiết so sánh kết quả:** {r['result_comparison_reason']}\n\n")
                f.write(f"---\n\n")
        else:
            f.write(f"## 4. Kết Luận\n\n")
            f.write(f"🎉 Tuyệt vời! Tất cả các câu hỏi trong bộ kiểm định đều đạt kết quả chính xác 100%.\n")
            
    print(f"[+] Đã tạo báo cáo đánh giá thành công tại {EVAL_REPORT_MD_PATH}!")

if __name__ == "__main__":
    main()
