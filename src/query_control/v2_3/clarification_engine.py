from typing import Optional
from src.query_control.v2_3.models import ExtractionReport

class ClarificationEngine:
    def generate_question(self, report: ExtractionReport) -> Optional[str]:
        """
        Dựa vào các issues trong ExtractionReport để sinh ra câu hỏi làm rõ cho người dùng.
        Gộp tất cả các vấn đề thành một câu hỏi duy nhất (nếu có).
        """
        if not report.has_issues:
            return None
            
        messages = []
        
        # 1. Xử lý các issue thiếu dữ liệu (missing)
        missing_issues = report.get_issues_by_type("missing")
        for issue in missing_issues:
            if issue.entity_type == "time":
                # Chúng ta đã thiết lập default là 2024, chỉ thêm vào như một lưu ý nhẹ 
                # (tuy nhiên nếu nghiêm ngặt thì sẽ bắt người dùng chọn)
                # messages.append("Bạn muốn xem dữ liệu của năm nào? (Ví dụ: 2023, 2024).")
                pass # Bỏ qua time missing vì đã có fallback 2024
            else:
                messages.append(issue.message)
                
        # 2. Xử lý các issue mơ hồ (ambiguous)
        ambiguous_issues = report.get_issues_by_type("ambiguous")
        for issue in ambiguous_issues:
            messages.append(issue.message)
            
        # 3. Xử lý các issue không thể giải quyết (unresolved)
        unresolved_issues = report.get_issues_by_type("unresolved")
        for issue in unresolved_issues:
            messages.append(issue.message)
            
        if not messages:
            return None
            
        # Nối các thông điệp lại
        final_question = "Tôi cần làm rõ một số thông tin trước khi trả lời:\n"
        for i, msg in enumerate(messages):
            final_question += f"{i+1}. {msg}\n"
            
        final_question += "Vui lòng cung cấp thêm thông tin để tôi có thể hỗ trợ tốt nhất."
        
        return final_question
