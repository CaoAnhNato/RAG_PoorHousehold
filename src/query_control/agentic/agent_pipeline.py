# -*- coding: utf-8 -*-
from __future__ import annotations
import sys
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))

from src.query_control.agentic.schema_linker import SchemaLinker
from src.query_control.agentic.sql_generator import SQLGenerator
from src.query_control.agentic.sql_refiner import SQLRefiner
from src.query_control.agentic.answer_generator import AnswerGenerator
from src.query_control.domain_gate import DomainGate

class AgenticPipeline:
    def __init__(self):
        semantic_layer_path = PROJECT_ROOT / "data" / "Processed" / "metadata" / "query_control" / "semantic_layer.json"
        db_path = PROJECT_ROOT / "data" / "Processed" / "intern_chatbot.duckdb"
        domain_gate_config_path = PROJECT_ROOT / "data" / "Processed" / "metadata" / "query_control" / "domain_gate_config.json"
        
        self.domain_gate = DomainGate(config_path=domain_gate_config_path, semantic_layer_path=semantic_layer_path)
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
            
        # 0. Domain Gate: Chặn các câu hỏi ngoài luồng, không đủ thông tin hoặc câu hỏi lý thuyết
        gate_res = self.domain_gate.classify(user_question)
        route = gate_res.get("route", "OUT_OF_SCOPE")
        confidence = gate_res.get("confidence", 0.0)
        
        print(f"[DomainGate] Route: {route} | Confidence: {confidence:.2f}")
        
        if route == "OUT_OF_SCOPE":
            return {
                "question": user_question,
                "sql": "",
                "answer": "Câu hỏi của bạn nằm ngoài phạm vi phân tích dữ liệu rà soát hộ nghèo. Xin vui lòng hỏi các vấn đề liên quan đến thống kê, quy định, hoặc thông tin hộ nghèo/cận nghèo trên địa bàn tỉnh Đắk Nông.",
                "data": None
            }
        elif route == "CLARIFICATION_NEEDED":
            return {
                "question": user_question,
                "sql": "",
                "answer": "Câu hỏi của bạn chưa đủ rõ ràng. Bạn có thể cung cấp thêm thông tin chi tiết (ví dụ: cần xem dữ liệu của huyện/xã nào, năm nào, hoặc chỉ số cụ thể nào) để tôi hỗ trợ chính xác hơn không?",
                "data": None
            }
        elif route == "GENERAL_KNOWLEDGE":
            return {
                "question": user_question,
                "sql": "",
                "answer": "Hệ thống hiện tại chỉ tập trung trả lời số liệu, chưa hỗ trợ trả lời lý thuyết.",
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
