# -*- coding: utf-8 -*-
"""
Module run_mvp_chatbot cung cấp giao diện dòng lệnh (CLI) tương tác trực tiếp
với Chatbot Q&A rà soát hộ nghèo tỉnh Đắk Nông.
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

def print_welcome_message() -> None:
    print("=" * 70)
    print("      CHATBOT Q&A RÀ SOÁT HỘ NGHÈO TỈNH ĐẮK NÔNG (MVP)")
    print("=" * 70)
    print(" Hướng dẫn sử dụng:")
    print(" - Nhập câu hỏi nghiệp vụ hoặc truy vấn thống kê dữ liệu.")
    print(" - Gõ '/exit' hoặc '/quit' để thoát chương trình.")
    print(" - Gõ '/clear' để xóa lịch sử bộ nhớ hội thoại hiện tại.")
    print(" - Gõ '/debug' để bật/tắt chế độ hiển thị SQL và thông tin Cache.")
    print("=" * 70)

def main() -> None:
    processed_dir = PROJECT_ROOT / "data" / "Processed"
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
    
    # Khởi tạo Qdrant Config
    qdrant_config_path = metadata_dir / "qdrant_index_config.json"
    with open(qdrant_config_path, "r", encoding="utf-8") as f:
        qdrant_config = json.load(f)
        
    qdrant_url = qdrant_config.get("qdrant_url", "http://localhost:6333")
    collection_name = qdrant_config.get("collection_name", "query_control_semantic")
    embedding_model = os.environ.get("EMBEDDING_MODEL")
    if not embedding_model:
        embedding_model = os.environ.get("FPT_EMBEDDING_MODEL_NAME", qdrant_config.get("embedding_model"))
        
    # 1. Khởi tạo toàn bộ các thành phần
    print("[*] Đang khởi động hệ thống Chatbot Q&A...")
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
        
        data_engine = DuckDBEngine(config_path=str(duckdb_config_path))
        query_cache = QueryCache(config_path=str(cache_config_path))
        observability_logger = ObservabilityLogger(config_path=str(observability_config_path))
        clarification_engine = ClarificationEngine(config_path=str(clarification_config_path), semantic_layer_path=str(semantic_layer_path))
        
        session_id = "cli_session_default"
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
    except Exception as e:
        print(f"[!] Lỗi khởi động Chatbot: {e}")
        sys.exit(1)
        
    print("[+] Khởi động thành công! Chatbot sẵn sàng phục vụ.")
    print_welcome_message()
    
    debug_mode = False
    pending_options = []
    
    while True:
        try:
            # Nhập câu hỏi người dùng
            user_input = input("\nUser > ").strip()
            
            if not user_input:
                continue
                
            # Xử lý các câu lệnh CLI đặc biệt
            if user_input.lower() in ["/exit", "/quit"]:
                print("Tạm biệt!")
                break
                
            if user_input.lower() == "/clear":
                conversation_memory.clear()
                pending_options = []
                print("[Chatbot] Đã xóa lịch sử bộ nhớ hội thoại.")
                continue
                
            if user_input.lower() == "/debug":
                debug_mode = not debug_mode
                print(f"[Chatbot] Chế độ gỡ lỗi (debug): {'BẬT' if debug_mode else 'TẮT'}")
                continue
                
            # Xử lý chọn lựa chọn làm rõ nếu đang có danh sách chờ
            if pending_options:
                try:
                    choice_idx = int(user_input) - 1
                    if 0 <= choice_idx < len(pending_options):
                        selected_option = pending_options[choice_idx]
                        opt_label = selected_option["label"]
                        opt_value = selected_option["value"]
                        
                        print(f"[Hệ thống] Bạn đã chọn: '{opt_label}'")
                        pending_options = []
                        
                        # Giả định câu hỏi tiếp theo dựa trên giá trị lựa chọn làm rõ
                        if isinstance(opt_value, dict) and "route_override" in opt_value:
                            # Hỏi lại câu hỏi cuối cùng nhưng định tuyến trực tiếp
                            # Để đơn giản trong CLI: kích hoạt lại câu cuối cùng với route_override
                            last_turn = conversation_memory.load()
                            if last_turn and len(last_turn) > 0:
                                last_q = last_turn[-1].get("question", "")
                                print(f"[Hệ thống] Thực thi lại truy vấn gốc: '{last_q}'")
                                # Thực hiện câu hỏi với override
                                user_input = f"{last_q} ({opt_label})"
                            else:
                                print("[Chatbot] Không tìm thấy câu hỏi trước đó để làm rõ.")
                                continue
                        else:
                            # Giá trị trực tiếp, ví dụ năm: "năm 2024" hoặc "ở Huyện Tuy Đức"
                            # Gửi giá trị này như một follow-up
                            user_input = str(opt_value)
                    else:
                        print(f"[Cảnh báo] Vui lòng nhập số trong khoảng từ 1 đến {len(pending_options)}.")
                        continue
                except ValueError:
                    # Nếu người dùng nhập chữ thay vì chọn số, hủy lựa chọn làm rõ và coi đây là câu hỏi mới
                    pending_options = []
                    
            # Gửi câu hỏi vào engine xử lý chính
            response = engine.answer(user_input)
            
            # Kiểm tra xem có yêu cầu làm rõ không
            if response.get("needs_clarification"):
                print(f"\nBot > {response.get('message')}")
                pending_options = response.get("options", [])
                for i, opt in enumerate(pending_options, 1):
                    print(f"  [{i}] {opt['label']}")
                    
                if debug_mode:
                    print("\n" + "-" * 40)
                    print("[DEBUG INFO - CLARIFICATION]")
                    print(f"- Error codes: {response.get('error_codes')}")
                    print(f"- Reason: {response.get('reason')}")
                    print("-" * 40)
                continue
                
            # Hiển thị kết quả bình thường
            print(f"\nBot > {response.get('answer')}")
            
            # Hiển thị thông tin debug nếu bật chế độ debug
            if debug_mode:
                print("\n" + "-" * 40)
                print("[DEBUG INFO]")
                print(f"- Phân loại định tuyến: {response.get('route')}")
                print(f"- Cache hit: {response.get('cache', {}).get('hit')} (Key: {response.get('cache', {}).get('key')})")
                print(f"- Số dòng kết quả: {response.get('row_count')}")
                if response.get("sql"):
                    print(f"- SQL generated:\n{response.get('sql')}")
                if response.get("warnings"):
                    print(f"- Cảnh báo: {response.get('warnings')}")
                if response.get("errors"):
                    print(f"- Lỗi: {response.get('errors')}")
                print("-" * 40)
                
        except KeyboardInterrupt:
            print("\nTạm biệt!")
            break
        except Exception as e:
            print(f"\n[!] Có lỗi xảy ra trong quá trình xử lý: {e}")

if __name__ == "__main__":
    main()
