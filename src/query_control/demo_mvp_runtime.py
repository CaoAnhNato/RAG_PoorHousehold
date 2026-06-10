# -*- coding: utf-8 -*-
"""
Module demo_mvp_runtime thực hiện chạy kiểm thử tự động 7 trường hợp nghiệp vụ
để đánh giá sự ổn định và chính xác của Chatbot Q&A MVP.
"""

from __future__ import annotations
import os
import sys
import json
from pathlib import Path
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

def main():
    print("=" * 60)
    print("BẮT ĐẦU KIỂM THỬ RUNTIME MVP CHATBOT Q&A")
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
    
    # Đọc cấu hình Qdrant
    qdrant_config_path = metadata_dir / "qdrant_index_config.json"
    with open(qdrant_config_path, "r", encoding="utf-8") as f:
        qdrant_config = json.load(f)
        
    qdrant_url = qdrant_config.get("qdrant_url", "http://localhost:6333")
    collection_name = qdrant_config.get("collection_name", "query_control_semantic")
    embedding_model = os.environ.get("EMBEDDING_MODEL")
    if not embedding_model:
        embedding_model = os.environ.get("FPT_EMBEDDING_MODEL_NAME", qdrant_config.get("embedding_model"))
        
    # 2. Khởi tạo các thành phần bổ trợ
    print("[1/2] Khởi tạo các thành phần hệ thống...")
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
    clarification_engine = ClarificationEngine(config_path=str(clarification_config_path), semantic_layer_path=str(semantic_layer_path))
    
    # Xoá cache cũ để test cache hit chính xác
    query_cache.clear()
    
    session_id = "test_session_123"
    conversation_memory = ConversationMemory(config_path=str(memory_config_path), session_id=session_id)
    conversation_memory.clear() # Xoá bộ nhớ cũ để test
    
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
    print("-> Khởi tạo thành công!")
    print("-" * 60)
    
    # 3. Thực hiện 7 trường hợp kiểm thử
    print("[2/2] Chạy các trường hợp kiểm thử nghiệp vụ:")
    
    # CASE 1: Kiểm tra tính sẵn sàng của DuckDB (validate_runtime_ready)
    print("\n--- TEST CASE 1: Kiểm tra trạng thái sẵn sàng của DuckDB ---")
    db_status = data_engine.validate_runtime_ready()
    print(f"Trạng thái DuckDB: {'SẴN SÀNG' if db_status['ready'] else 'LỖI'}")
    print(f"File DuckDB tồn tại: {db_status['duckdb_file_exists']}")
    print(f"Bảng households tồn tại: {db_status['households_table_exists']}")
    print(f"Bảng members tồn tại: {db_status['members_table_exists']}")
    assert db_status["ready"] is True, "Lỗi: DuckDB chưa sẵn sàng!"
    
    # CASE 2: Kiểm tra Cache Hit (Hỏi 2 lần cùng một câu)
    print("\n--- TEST CASE 2: Kiểm tra lưu trữ và truy xuất Cache ---")
    question_cache = "Thống kê số lượng hộ nghèo năm 2024 theo huyện"
    
    print("Lần hỏi 1 (Cache Miss dự kiến):")
    res1 = engine.answer(question_cache)
    print(f"-> Cache Hit: {res1['cache']['hit']}")
    print(f"-> Số dòng trả về: {res1['row_count']}")
    
    print("Lần hỏi 2 (Cache Hit dự kiến):")
    res2 = engine.answer(question_cache)
    print(f"-> Cache Hit: {res2['cache']['hit']}")
    print(f"-> Số dòng trả về: {res2['row_count']}")
    assert res2["cache"]["hit"] is True, "Lỗi: Không tìm thấy kết quả trong Cache ở lần hỏi thứ hai!"
    
    # CASE 3: Kiểm tra câu hỏi kế thừa (Follow-up Memory)
    print("\n--- TEST CASE 3: Kiểm tra kế thừa câu hỏi (Conversation Memory) ---")
    print("Hỏi câu gốc: 'Thống kê số lượng hộ cận nghèo theo huyện năm 2024'")
    engine.answer("Thống kê số lượng hộ cận nghèo theo huyện năm 2024")
    
    follow_up_q = "Còn năm 2023 thì sao?"
    print(f"Hỏi câu kế thừa: '{follow_up_q}'")
    res_follow = engine.answer(follow_up_q)
    print(f"-> Kế hoạch thực tế (Filters): {res_follow['query_plan']['filters']}")
    print(f"-> Câu trả lời: {res_follow['answer'][:150]}...")
    
    # Kiểm tra xem bộ lọc năm 2023 có được cập nhật thành công không
    has_year_2023 = False
    for f in res_follow["query_plan"]["filters"]:
        if f.get("field") == "year" and f.get("value") in [2023, "2023"]:
            has_year_2023 = True
            
    assert has_year_2023 is True, "Lỗi: Câu hỏi kế thừa không cập nhật được bộ lọc năm 2023!"
    
    # CASE 4: Kiểm tra làm rõ (Clarification Engine)
    print("\n--- TEST CASE 4: Kiểm tra làm rõ yêu cầu (Clarification Engine) ---")
    conversation_memory.clear()  # Xóa lịch sử để tránh ảnh hưởng từ test case trước
    ambiguous_q = "nghèo"
    print(f"Hỏi câu mơ hồ: '{ambiguous_q}'")
    res_clarify = engine.answer(ambiguous_q)
    print(f"Full response: {res_clarify}")
    assert res_clarify.get("needs_clarification") is True, "Lỗi: Hệ thống không yêu cầu làm rõ đối với câu hỏi mơ hồ!"
    
    # CASE 5: Kiểm tra General Knowledge (Kiến thức chung)
    print("\n--- TEST CASE 5: Kiểm tra hỏi đáp kiến thức nghiệp vụ ---")
    gk_q = "Quy trình rà soát hộ nghèo gồm mấy bước?"
    print(f"Hỏi câu lý thuyết: '{gk_q}'")
    res_gk = engine.answer(gk_q)
    print(f"-> Route: {res_gk['route']}")
    print(f"-> Câu trả lời: {res_gk['answer'][:250]}...")
    assert res_gk["route"] == "GENERAL_KNOWLEDGE", "Lỗi: Định tuyến sai câu hỏi kiến thức chung!"
    
    # CASE 6: Kiểm tra Out Of Scope (Nằm ngoài phạm vi)
    print("\n--- TEST CASE 6: Kiểm tra từ chối câu hỏi ngoài phạm vi ---")
    oos_q = "Dự báo thời tiết Gia Nghĩa hôm nay thế nào?"
    print(f"Hỏi câu ngoài phạm vi: '{oos_q}'")
    res_oos = engine.answer(oos_q)
    print(f"-> Route: {res_oos['route']}")
    print(f"-> Câu trả lời: {res_oos['answer']}")
    assert res_oos["route"] == "OUT_OF_SCOPE", "Lỗi: Không từ chối câu hỏi ngoài phạm vi nghiệp vụ!"
    
    # CASE 7: Kiểm tra Observability logs
    print("\n--- TEST CASE 7: Kiểm tra nhật ký giám sát Observability ---")
    events_log_path = PROJECT_ROOT / "Runtime" / "logs" / "query_events.jsonl"
    print(f"Đường dẫn file events log: {events_log_path}")
    assert events_log_path.exists(), "Lỗi: Tệp query_events.jsonl không được tạo!"
    
    # Đọc số dòng của log
    with open(events_log_path, "r", encoding="utf-8") as f:
        log_lines = f.readlines()
    print(f"-> Số sự kiện ghi nhận thành công: {len(log_lines)}")
    assert len(log_lines) > 0, "Lỗi: Không có log sự kiện nào được ghi!"
    
    print("\n" + "=" * 60)
    print("HOÀN THÀNH KIỂM THỬ: TẤT CẢ 7 TEST CASES ĐỀU ĐẠT CHẤT LƯỢNG (PASSED)!")
    print("=" * 60)

if __name__ == "__main__":
    main()
