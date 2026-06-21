# -*- coding: utf-8 -*-
"""
Module demo_query_control thực thi chạy thử nghiệm hệ thống Chatbot Q&A
với các câu hỏi mẫu nhằm kiểm tra đầy đủ các thành phần trong pipeline.
"""

from __future__ import annotations
import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
# Nạp cấu hình từ .env
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.query_control.semantic_retriever import SemanticRetriever
from src.query_control.domain_gate import DomainGate
from src.query_control.query_planner import QueryPlanner
from src.query_control.sql_compiler import SQLCompiler
from src.query_control.answer_engine import ChatbotAnswerEngine

def main() -> None:
    parser = argparse.ArgumentParser(description="Demo chatbot Q&A rà soát hộ nghèo Đắk Nông.")
    parser.add_argument("--query", type=str, default="", help="Câu hỏi đơn lẻ cần chạy thử.")
    args = parser.parse_args()
    
    # 1. Định nghĩa các đường dẫn metadata
    processed_dir = PROJECT_ROOT / "data" / "Processed"
    metadata_dir = processed_dir / "metadata" / "query_control"
    
    schema_graph_path = metadata_dir / "schema_graph.json"
    semantic_layer_path = metadata_dir / "semantic_layer.json"
    query_plan_schema_path = metadata_dir / "query_plan_schema.json"
    domain_gate_config_path = metadata_dir / "domain_gate_config.json"
    
    # Đọc cấu hình Qdrant và mô hình Embedding
    qdrant_config_path = metadata_dir / "qdrant_index_config.json"
    with open(qdrant_config_path, "r", encoding="utf-8") as f:
        qdrant_config = json.load(f)
        
    qdrant_url = qdrant_config.get("qdrant_url", "http://localhost:6333")
    collection_name = qdrant_config.get("collection_name", "query_control_semantic")
    embedding_model = os.environ.get("EMBEDDING_MODEL")
    if not embedding_model:
        embedding_model = os.environ.get("FPT_EMBEDDING_MODEL_NAME", qdrant_config.get("embedding_model"))
        
    print("=" * 60)
    print("KHỞI TẠO HỆ THỐNG CHATBOT Q&A")
    print("=" * 60)
    print(f"- Qdrant Server: {qdrant_url}")
    print(f"- Collection: {collection_name}")
    print(f"- Embedding Model: {embedding_model}")
    print("-" * 60)
    
    # 2. Khởi tạo các thành phần pipeline
    try:
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
        
        engine = ChatbotAnswerEngine(
            domain_gate=domain_gate,
            query_planner=planner,
            sql_compiler=compiler
        )
        
    except Exception as e:
        print(f"Lỗi khởi tạo hệ thống: {e}")
        sys.exit(1)
        
    print("Hệ thống đã sẵn sàng!")
    print("=" * 60)
    
    # 3. Chạy câu hỏi đơn lẻ nếu có tham số truyền vào
    if args.query:
        run_query_flow(engine, args.query)
        return
        
    # Danh sách câu hỏi mẫu chạy thử nghiệm
    test_queries = [
        "Thống kê số lượng hộ nghèo theo huyện năm 2024",
        "Huyện nào có nhiều hộ cận nghèo nhất năm 2023?",
        "Thế nào là hộ nghèo đa chiều?",
        "So sánh số lượng hộ nghèo giữa năm 2023 và 2024",
        "Cho tôi xem thông tin",
        "PhoBERT hoạt động như thế nào?"
    ]
    
    print("Bắt đầu chạy thử nghiệm 6 câu hỏi mẫu:")
    for idx, q in enumerate(test_queries, 1):
        print(f"\n[{idx}] CÂU HỎI: \"{q}\"")
        run_query_flow(engine, q)
        print("-" * 60)
        
    # Chế độ tương tác nhập trực tiếp
    print("\nBắt đầu chế độ tương tác (Gõ 'exit' hoặc 'quit' để thoát):")
    while True:
        try:
            user_input = input("\nĐặt câu hỏi của bạn: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print("Tạm biệt!")
                break
            run_query_flow(engine, user_input)
        except KeyboardInterrupt:
            print("\nThoát chương trình.")
            break
        except Exception as e:
            print(f"Lỗi trong quá trình xử lý câu hỏi: {e}")

def run_query_flow(engine: ChatbotAnswerEngine, query: str) -> None:
    """Chạy toàn bộ pipeline cho một câu hỏi và in kết quả chi tiết."""
    print("  1. Phân loại định tuyến (Domain Gate)...")
    gate_res = engine.domain_gate.classify(query)
    route = gate_res.get("route")
    confidence = gate_res.get("confidence")
    print(f"     => Route: {route} (Độ tin cậy: {confidence})")
    print(f"     => Lý do: {gate_res.get('reason')}")
    
    # Thực hiện trả lời
    res = engine.answer(query)
    
    if res.get("query_plan"):
        print("  2. Kế hoạch truy vấn (Query Plan):")
        print(f"     {json.dumps(res['query_plan'], ensure_ascii=False)}")
        
    if res.get("sql"):
        print("  3. Câu SQL DuckDB:")
        print(f"     {res['sql']}")
        
    if res.get("result_preview"):
        print(f"  4. Số dòng kết quả DB: {len(res['result_preview'])}")
        print("     Xem trước 3 dòng đầu:")
        for r in res["result_preview"][:3]:
            print(f"     - {r}")
            
    print("\n  5. CÂU TRẢ LỜI CỦA CHATBOT:")
    print(res["answer"])
    
    # In cảnh báo/lỗi nếu có
    if res.get("warnings"):
        print("  ⚠️ Cảnh báo:")
        for w in res["warnings"]:
            print(f"     - [{w.get('code')}] {w.get('message')}")
            
    if res.get("errors"):
        print("  ❌ Lỗi:")
        for err in res["errors"]:
            print(f"     - [{err.get('code')}] {err.get('message')}")

import json  # Import cục bộ để phục vụ đọc config
if __name__ == "__main__":
    main()
