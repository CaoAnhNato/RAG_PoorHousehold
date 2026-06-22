import sys
import json
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()
from src.query_control.semantic_retriever import SemanticRetriever

retriever = SemanticRetriever(
    qdrant_url="http://localhost:6333",
    collection_name="query_control_semantic",
    embedding_model="text-embedding-3-small"
)

q3 = "Cho tôi biết tình hình nghèo ở Đắk Nông như thế nào?"
rule_output = {
    "task_type": "aggregate_query",
    "years": [2024]
}

from src.query_control.query_planner import QueryPlanner
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
planner = QueryPlanner(
    schema_graph_path=PROJECT_ROOT / "data" / "Processed" / "metadata" / "schema_graph.json",
    semantic_layer_path=PROJECT_ROOT / "data" / "Processed" / "metadata" / "query_control" / "semantic_layer.json",
    query_plan_schema_path=PROJECT_ROOT / "data" / "Processed" / "metadata" / "query_control" / "query_plan_schema.json",
    semantic_retriever=retriever
)
ctx = planner.build_planner_context(q3, rule_output)
print(json.dumps(ctx, ensure_ascii=False, indent=2))
