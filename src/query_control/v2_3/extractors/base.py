from abc import ABC, abstractmethod
from src.query_control.v2_3.models import ExtractionReport

class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, text: str, report: ExtractionReport):
        """
        Trích xuất thông tin từ text và cập nhật vào report.
        
        Args:
            text (str): Câu hỏi đã được chuẩn hóa.
            report (ExtractionReport): Báo cáo trích xuất để ghi nhận kết quả hoặc issue.
        """
        pass
