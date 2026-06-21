from src.query_control.v2_3.models import ExtractionReport
from src.query_control.v2_3.canonical_slot import CanonicalSlotRepresentation

class SemanticResolver:
    def resolve(self, report: ExtractionReport) -> CanonicalSlotRepresentation:
        """
        Chuyển đổi ExtractionReport thành CanonicalSlotRepresentation.
        """
        slots = CanonicalSlotRepresentation()
        
        # 1. Map Time
        if "administrative.year" in report.slots:
            slots.time_context = report.slots["administrative.year"]
            
        # 2. Map Location
        if "administrative.district" in report.slots:
            slots.location_context.district = report.slots["administrative.district"]
        if "administrative.commune" in report.slots:
            slots.location_context.commune = report.slots["administrative.commune"]
            
        # 3. Map Metrics/Entities
        if "entities" in report.slots:
            slots.metrics = report.slots["entities"]
            
        # Các logic conditions (ví dụ: > 0, = true) sẽ được bổ sung sau bởi logic_extractor
        
        return slots
