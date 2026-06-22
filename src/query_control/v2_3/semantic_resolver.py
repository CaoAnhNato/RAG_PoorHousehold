from src.query_control.v2_3.models import ExtractionReport
from src.query_control.v2_3.canonical_slot import CanonicalSlotRepresentation

class SemanticResolver:
    def resolve(self, report: ExtractionReport) -> CanonicalSlotRepresentation:
        """
        Chuyển đổi ExtractionReport thành CanonicalSlotRepresentation.
        """
        slots = CanonicalSlotRepresentation()
        
        raw_entities = report.slots.get("raw_entities", {})
        
        # 1. Map Time
        # Extract time from raw_entities and convert to int if possible
        raw_time = raw_entities.get("time", [])
        for t in raw_time:
            if isinstance(t, str) and t.isdigit():
                slots.time_context.append(int(t))
                
        # Also include rule-based time
        if "administrative.year" in report.slots:
            for y in report.slots["administrative.year"]:
                if y not in slots.time_context:
                    slots.time_context.append(y)
            
        # 2. Map Location
        # Rule-based location extraction is generally very accurate due to fuzzy matching
        if "administrative.district" in report.slots:
            slots.location_context.district = report.slots["administrative.district"]
        if "administrative.commune" in report.slots:
            slots.location_context.commune = report.slots["administrative.commune"]
            
        # 3. Map Metrics/Entities
        combined_metrics = []
        if "entities" in report.slots:
            combined_metrics.extend(report.slots["entities"])
            
        if "metrics" in raw_entities:
            combined_metrics.extend([m for m in raw_entities["metrics"] if m not in combined_metrics])
        if "filters" in raw_entities:
            combined_metrics.extend([f for f in raw_entities["filters"] if f not in combined_metrics])
            
        slots.metrics = combined_metrics
        
        # Các logic conditions (ví dụ: > 0, = true) sẽ được bổ sung sau bởi logic_extractor
        
        return slots
