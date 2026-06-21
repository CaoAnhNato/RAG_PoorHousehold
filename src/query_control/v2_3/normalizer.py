import re

class TextNormalizer:
    def normalize(self, text: str) -> str:
        """
        Chuẩn hóa chuỗi văn bản đầu vào:
        - Chuyển thành chữ thường
        - Loại bỏ khoảng trắng thừa
        - Chuẩn hóa các dấu câu cơ bản
        
        Args:
            text (str): Chuỗi gốc
            
        Returns:
            str: Chuỗi đã được chuẩn hóa
        """
        if not text:
            return ""
        
        # Chuyển chữ thường
        text = str(text).lower()
        
        # Loại bỏ dấu câu không cần thiết (giữ lại chữ, số, và khoảng trắng)
        # Tạm thời giữ nguyên dấu tiếng Việt
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Loại bỏ khoảng trắng thừa
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
