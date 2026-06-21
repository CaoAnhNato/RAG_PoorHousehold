import re
from src.query_control.v2_3.extractors.base import BaseExtractor
from src.query_control.v2_3.models import ExtractionReport

class TimeExtractor(BaseExtractor):
    def __init__(self, default_year=2024, valid_years=None):
        self.default_year = default_year
        self.valid_years = valid_years or [2023, 2024]
        
    def extract(self, text: str, report: ExtractionReport):
        """
        Trích xuất thông tin năm (năm 2023, năm 2024, v.v.)
        """
        # Tìm tất cả các số có 4 chữ số bắt đầu bằng 20
        years_found = [int(y) for y in re.findall(r'\b(20\d{2})\b', text)]
        
        if not years_found:
            # Nếu không tìm thấy, ghi nhận missing
            report.add_issue(
                entity_type="time",
                issue_type="missing",
                message=f"Không tìm thấy thông tin năm trong câu hỏi. Hệ thống sẽ mặc định dùng dữ liệu năm mới nhất ({self.default_year}) nếu không được làm rõ."
            )
            # Mặc định sử dụng năm mới nhất để fallback, nhưng vẫn coi là một issue để làm rõ
            report.add_resolved("administrative.year", [self.default_year])
            return

        resolved_years = []
        out_of_scope_years = []
        
        for year in set(years_found):
            if year in self.valid_years:
                resolved_years.append(year)
            else:
                out_of_scope_years.append(year)
                
        if out_of_scope_years:
            report.add_issue(
                entity_type="time",
                issue_type="unresolved",
                value=str(out_of_scope_years),
                message=f"Hệ thống chỉ có dữ liệu của các năm {self.valid_years}, không có dữ liệu năm {out_of_scope_years}."
            )
            
        if resolved_years:
            report.add_resolved("administrative.year", resolved_years)
