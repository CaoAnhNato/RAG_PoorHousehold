from typing import Dict, Any, Tuple
import pandas as pd
import logging
from src.query_control.agentic.schema_linker import SchemaLinker
from src.query_control.agentic.sql_generator import SQLGenerator
from src.query_control.agentic.sql_refiner import SQLRefiner
from src.query_control.agentic.answer_generator import AnswerGenerator
from src.query_control.semantic_retriever import SemanticRetriever

logger = logging.getLogger(__name__)

class AgenticOrchestrator:
    """
    Core Orchestrator cho luồng Multi-Agent NL2SQL.
    Wire 4 agents: SchemaLinker -> SQLGenerator -> SQLRefiner -> AnswerGenerator.
    """
    def __init__(self, db_path: str = 'data/Processed/intern_chatbot.duckdb', model: str = None):
        self.schema_linker = SchemaLinker(db_path=db_path)
        self.sql_generator = SQLGenerator(model=model)
        self.sql_refiner = SQLRefiner(db_path=db_path, model=model)
        self.answer_generator = AnswerGenerator(model=model)
        
        # Có thể dùng SemanticRetriever để lấy few-shot examples
        try:
            self.semantic_retriever = SemanticRetriever()
        except Exception as e:
            logger.warning(f"Could not init SemanticRetriever: {e}")
            self.semantic_retriever = None

    def process_query(self, query: str) -> Dict[str, Any]:
        logger.info(f"Processing query via Agentic NL2SQL: {query}")
        
        # 1. Schema Linking
        schema_context = self.schema_linker.get_database_schema()
        semantic_context = self.schema_linker.get_semantic_context(self.semantic_retriever, query)
        
        # 2. SQL Generation
        initial_sql = self.sql_generator.generate_sql(query, schema_context, semantic_context)
        logger.info(f"Initial generated SQL: {initial_sql}")
        
        # 3. SQL Refinement & Execution
        df, final_sql, error = self.sql_refiner.execute_with_self_correction(
            initial_sql=initial_sql,
            query=query,
            schema_context=schema_context,
            max_retries=3
        )
        
        if error:
            logger.error(f"SQL execution failed after retries: {error}")
            
        # 4. Answer Generation
        answer = self.answer_generator.generate_answer(query, final_sql, df, error)
        
        # Format response compatible with existing UI/tests
        response = {
            "query": query,
            "final_sql": final_sql,
            "answer": answer,
            "data": df.to_dict(orient='records') if (df is not None and not df.empty) else [],
            "error": error
        }
        
        return response
