# -*- coding: utf-8 -*-
from __future__ import annotations
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))
from src.query_control.llm_helper import call_llm, clean_json_response

class SchemaLinker:
    """Agent trích xuất các bảng và cột liên quan từ schema dựa trên câu hỏi."""
    def __init__(self, semantic_layer_path: Path):
        with open(semantic_layer_path, "r", encoding="utf-8") as f:
            self.semantic_layer = json.load(f)
            
    def link(self, user_question: str) -> dict:
        """Trả về thông tin schema tĩnh (bỏ qua LLM để giảm latency)."""
        schema_lines = ["Danh sách các cột (physical_columns) và ý nghĩa trong CSDL:"]
        for key, dim in self.semantic_layer.get("dimensions", {}).items():
            cols = ", ".join(dim.get("physical_columns", []))
            desc = dim.get("definition", "")
            schema_lines.append(f"- Cột {cols}: {desc} (Bảng {dim.get('base_table')})")
            
        for key, msr in self.semantic_layer.get("measures", {}).items():
            cols = ", ".join(msr.get("physical_columns", []))
            desc = msr.get("definition", "")
            schema_lines.append(f"- Cột {cols}: {desc} (Bảng {msr.get('base_table')})")
            
        schema_context = "\n".join(schema_lines)
        
        return {
            "relevant_tables": ["households", "members"],
            "schema_context": schema_context,
            "relevant_columns": [] # Không cần trích xuất trước nữa, để SQL Generator tự định đoạt
        }
