import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()
from src.query_control.query_planner import QueryPlanner
from src.query_control.sql_compiler import SQLCompiler
from src.query_control.data_engine import DuckDBEngine
from src.query_control.semantic_retriever import SemanticRetriever

PROJECT_ROOT = Path(".").resolve()
PROCESSED_DIR = PROJECT_ROOT / "data" / "Processed"
METADATA_DIR = PROCESSED_DIR / "metadata"
QUERY_CONTROL_METADATA_DIR = METADATA_DIR / "query_control"

retriever = SemanticRetriever(
    qdrant_url="http://localhost:6333",
    collection_name="query_control_semantic",
    embedding_model="text-embedding-3-small"
)
planner = QueryPlanner(
    schema_graph_path=QUERY_CONTROL_METADATA_DIR / "schema_graph.json",
    semantic_layer_path=QUERY_CONTROL_METADATA_DIR / "semantic_layer.json",
    query_plan_schema_path=QUERY_CONTROL_METADATA_DIR / "query_plan_schema.json",
    semantic_retriever=retriever
)
compiler = SQLCompiler(
    schema_graph_path=QUERY_CONTROL_METADATA_DIR / "schema_graph.json",
    semantic_layer_path=QUERY_CONTROL_METADATA_DIR / "semantic_layer.json"
)
engine = DuckDBEngine("data/Processed/metadata/query_control/duckdb_config.json")

q3 = "Cho tôi biết tình hình nghèo ở Đắk Nông như thế nào?"
plan = planner.plan(q3)
print("Plan:", json.dumps(plan, ensure_ascii=False, indent=2))

try:
    sql = compiler.compile(plan)
    print("SQL:", sql)
    res = engine.execute_sql(sql)
    print("Result rows:", res["row_count"])
    print("Result data:", res["data"][:5])
except Exception as e:
    print("Error:", e)
