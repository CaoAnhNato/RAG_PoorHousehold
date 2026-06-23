# -*- coding: utf-8 -*-
from __future__ import annotations
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))

from src.query_control.agentic.schema_linker import SchemaLinker
from src.query_control.agentic.sql_generator import SQLGenerator
from src.query_control.agentic.sql_refiner import SQLRefiner
from src.query_control.agentic.answer_generator import AnswerGenerator

class AgenticPipeline:
    def __init__(self):
        semantic_layer_path = PROJECT_ROOT / "data" / "Processed" / "metadata" / "query_control" / "semantic_layer.json"
        db_path = PROJECT_ROOT / "data" / "Processed" / "intern_chatbot.duckdb"
        
        self.schema_linker = SchemaLinker(semantic_layer_path)
        self.sql_generator = SQLGenerator()
        self.sql_refiner = SQLRefiner(db_path)
        self.answer_generator = AnswerGenerator()
        
    def process(self, user_question: str, mode: str = "Auto") -> dict:
        print(f"\n--- [AgenticPipeline] Processing: {user_question} | Mode: {mode} ---")
        
        if mode == "Báo Cáo":
            return {
                "question": user_question,
                "sql": "",
                "answer": "Tính năng Báo Cáo đang phát triển.",
                "data": None
            }
            
        # 1. Schema Linking
        schema_info = self.schema_linker.link(user_question)
        
        # 2. SQL Generation
        sql_query = self.sql_generator.generate(user_question, schema_info)
        
        # 3. SQL Execution & Refinement
        df, final_sql = self.sql_refiner.execute_and_refine(sql_query, user_question, schema_info)
        
        # 4. Mode routing based on 'Auto' logic or explicit selection
        actual_mode = mode
        if mode == "Auto":
            if df is not None and not df.empty and len(df) > 1:
                actual_mode = "Biểu đồ"
            else:
                actual_mode = "Hỏi - Đáp"
                
        # 5. Output Generation
        fig = None
        if actual_mode == "Biểu đồ":
            from src.query_control.agentic.utils import normalize_columns
            from src.query_control.agentic.chart_generator import AgentChartGenerator
            
            df_vi = normalize_columns(df)
            chart_gen = AgentChartGenerator()
            # Generate chart and save HTML in artifacts for CLI debugging
            chart_dir = PROJECT_ROOT / "artifacts" / "charts"
            save_path = chart_dir / f"chart_{int(time.time())}.html"
            
            fig, answer = chart_gen.generate(user_question, df_vi, save_path=save_path)
            data_out = df_vi
        else: # Hỏi - Đáp
            answer = self.answer_generator.generate(user_question, df)
            data_out = df
            
        return {
            "question": user_question,
            "sql": final_sql,
            "answer": answer,
            "data": data_out,
            "chart_fig": fig
        }
