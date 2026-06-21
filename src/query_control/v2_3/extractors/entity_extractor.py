import json
from flashtext import KeywordProcessor
from src.query_control.v2_3.extractors.base import BaseExtractor
from src.query_control.v2_3.models import ExtractionReport

class EntityExtractor(BaseExtractor):
    def __init__(self, entities_path: str = "data/Processed/metadata/entities.json", synonyms_path: str = "data/Processed/metadata/synonyms.json"):
        self.keyword_processor = KeywordProcessor()
        self.entity_map = {}
        
        # Load entities
        with open(entities_path, 'r', encoding='utf-8') as f:
            entities = json.load(f)
            for entity_key, data in entities.items():
                physical_col = data.get("physical_column")
                aliases = data.get("aliases", [])
                
                # We map the physical column back to the query intent
                for alias in aliases:
                    # FlashText maps keyword -> clean_name
                    self.keyword_processor.add_keyword(alias, physical_col)
                    self.entity_map[physical_col] = {
                        "entity_key": entity_key,
                        "source_table": data.get("source_table")
                    }
                    
        # Load synonyms (if they add extra aliases)
        try:
            with open(synonyms_path, 'r', encoding='utf-8') as f:
                synonyms = json.load(f)
                for syn, canonical in synonyms.items():
                    # If canonical is a known physical column or entity key
                    # For simplicity, we just add it to KeywordProcessor if canonical matches something we know
                    # But if canonical is not a physical col, we'd need to resolve it.
                    # As a basic step, let's just add it mapping to canonical
                    self.keyword_processor.add_keyword(syn, canonical)
        except FileNotFoundError:
            pass
            
    def extract(self, text: str, report: ExtractionReport):
        # FlashText extract keywords
        keywords_found = self.keyword_processor.extract_keywords(text)
        
        # Deduplicate
        keywords_found = list(set(keywords_found))
        
        if keywords_found:
            # Ghi nhận các physical_columns đã map được
            report.add_resolved("entities", keywords_found)
