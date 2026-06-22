# -*- coding: utf-8 -*-
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Force UTF-8 stdout
sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parents[1]
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
    
    qdrant_config_path = metadata_dir / "qdrant_index_config.json"
    with open(qdrant_config_path, "r", encoding="utf-8") as f:
        qdrant_config = json.load(f)
        
    qdrant_url = qdrant_config.get("qdrant_url", "http://localhost:6333")
    collection_name = qdrant_config.get("collection_name", "query_control_semantic")
    embedding_model = os.environ.get("EMBEDDING_MODEL")
    if not embedding_model:
        embedding_model = os.environ.get("SHOPAPI_EMBEDDING", qdrant_config.get("embedding_model"))
        
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
    
    questions = [
        "Năm 2024, thống kê số hộ nghèo theo huyện.",
        "Huyện nào có nhiều hộ nghèo nhất trong năm 2024?",
        "Cho tôi biết tình hình nghèo ở Đắk Nông như thế nào?",
        "Tôi muốn xem nhanh số hộ nghèo và hộ cận nghèo theo từng huyện trong năm 2024.",
        "Năm 2024, tình hình hộ nghèo ở Thành phố Gia Nghĩa có cải thiện hơn so với năm 2023 không?",
        "So với năm 2023, số hộ nghèo ở Đắk Song năm 2024 thay đổi ra sao?",
        "Năm 2024, hộ cận nghèo đang tập trung nhiều ở huyện nào?",
        "Ở Huyện Cư Jút, hộ nghèo nào thiếu nhà tiêu hợp vệ sinh nhiều nhất?",
        "So với 2023, số hộ thoát nghèo trong 2024 tăng hay giảm ở Tuy Đức?",
        "Chủ hộ nào có số thành viên nhiều nhất ở Huyện Đắk Song?",
        "Mức độ thiếu hụt của các hộ nghèo ở Đắk Mil tập trung mạnh vào những chỉ số nào?",
        "Khu vực nào có nhiều hộ cận nghèo nhất nhưng lại ít thiếu hụt nhất?"
    ]
    
    output_path = PROJECT_ROOT / "artifacts" / "quest_ans.md"
    
    with open(output_path, "w", encoding="utf-8") as out:
        out.write("# Câu hỏi và Truy vấn SQL tương ứng\n\n")
        out.write("Tài liệu cung cấp các câu hỏi, các lệnh SQL tương ứng, và đáp án từ SQL (context) để LLM trả lời.\n\n")
        out.flush()
        
        for idx, q in enumerate(questions, 1):
            print(f"Processing question {idx}: {q}")
            out.write(f"## {idx}. {q}\n")
            out.flush()
            conversation_memory.clear() # Clear memory for independent questions
            
            try:
                response = engine.answer(q)
                
                sql = response.get("sql", "Không sinh được SQL")
                answer = response.get("answer", "Không có câu trả lời")
                data_result = response.get("data", [])
                
                print(f"-> SQL: {sql}")
                out.write("### Lệnh SQL\n")
                out.write("```sql\n")
                out.write(f"{sql}\n")
                out.write("```\n\n")
                
                out.write("### Đáp án (Context từ SQL)\n")
                out.write(f"> {answer}\n\n")
                
                out.write("### Dữ liệu trả về từ DB\n")
                out.write("```json\n")
                out.write(f"{json.dumps(data_result, ensure_ascii=False, indent=2)}\n")
                out.write("```\n\n")
                out.write("---\n\n")
                out.flush()
            except Exception as e:
                print(f"-> ERROR: {e}")
                out.write(f"**Lỗi xử lý:** {e}\n\n")
                out.flush()

if __name__ == "__main__":
    main()
