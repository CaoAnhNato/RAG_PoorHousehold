from src.query_control.v2_3.normalizer import TextNormalizer
from src.query_control.v2_3.extractors.time_extractor import TimeExtractor
from src.query_control.v2_3.extractors.location_extractor import LocationExtractor
from src.query_control.v2_3.extractors.entity_extractor import EntityExtractor
from src.query_control.v2_3.models import ExtractionReport
from src.query_control.v2_3.clarification_engine import ClarificationEngine
from src.query_control.v2_3.semantic_resolver import SemanticResolver
from src.query_control.v2_3.query_rewriter import QueryRewriter

class QueryOrchestratorV2_3:
    def __init__(self):
        self.rewriter = QueryRewriter()
        self.normalizer = TextNormalizer()
        self.extractors = [
            TimeExtractor(),
            LocationExtractor(),
            EntityExtractor()
        ]
        self.clarification_engine = ClarificationEngine()
        self.semantic_resolver = SemanticResolver()
        
    def process_query(self, query: str) -> dict:
        """
        Xử lý câu hỏi qua pipeline v2.3
        """
        # 0. Rewrite & Extract Raw Entities
        rewritten_info = self.rewriter.rewrite(query)
        rewritten_query = rewritten_info.get("rewritten_query", query)
        raw_entities = rewritten_info.get("extracted_entities", {})

        # 1. Normalize
        normalized_query = self.normalizer.normalize(rewritten_query)
        
        # 2. Extract
        report = ExtractionReport()
        # Lưu trữ raw_entities từ Query Rewriter vào report để sử dụng sau này
        if raw_entities:
            report.add_resolved("raw_entities", raw_entities)
            
        for extractor in self.extractors:
            extractor.extract(normalized_query, report)
            
        # 3. Clarification
        clarification_question = self.clarification_engine.generate_question(report)
        if clarification_question:
            return {
                "status": "needs_clarification",
                "message": clarification_question,
                "report": report.dict()
            }
            
        # 4. Resolve to Canonical Slots
        canonical_slots = self.semantic_resolver.resolve(report)
        
        return {
            "status": "success",
            "slots": canonical_slots.dict(),
            "report": report.dict()
        }
