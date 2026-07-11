import re

class CanonicalNormalizer:
    def __init__(self):
        # Mappings from user variations to Exact Canonical Database Name.
        self.mappings = {
            # Huyện
            r'\bđ[ăắa]k\s*glong\b': "Huyện Đăk Glong",
            r'\bđ[ăắa]k\s*r\'?l[aăắâ]p\b': "Huyện Đắk RLấp",
            r'\bđ[ăắa]k\s*mil\b': "Huyện Đắk Mil",
            r'\bđ[ăắa]k\s*song\b': "Huyện Đắk Song",
            r'\bcư\s*j[uú]t\b': "Huyện Cư Jút",
            r'\bkr[oô]ng\s*n[oô]\b': "Huyện Krông Nô",
            r'\btuy\s*đ[uưứ]c\b': "Huyện Tuy Đức",
            r'\bgia\s*ngh[iĩ]a\b': "Thành phố Gia Nghĩa",
            
            # Phường / Thị trấn đặc biệt
            r'\bea\s*t\'?ling\b': "Thị trấn Ea TLing",
            r'\bđ[ăắa]k\s*m[aăââm]\b': "Thị trấn Đắk Mâm",
            
            # Xã đặc biệt
            r'\bđ[ăắa]k\s*r\'?m[aăắ]ng\b': "Xã Đắk RMăng",
            r'\bđ[ăắa]k\s*r\'?t[ií]h\b': "Xã Đắk RTíh",
            r'\bđ[ăắa]k\s*r\'?moan\b': "Xã Đăk RMoan",
            r'\bđ[ăắa]k\s*lao\b': "Xã  Đắk Lao",  # CSDL bị dư 1 khoảng trắng
            r'\bđ[ăắa]k\s*n\'?drung\b': "Xã Đắk N'Drung",
            r'\bđ[ăắa]k\s*n\'?dr[oó]t\b': "Xã Đắk NDrót",
            r'\bđ[ăắa]k\s*d\'?r[oôông]\b': "Xã Đắk DRông",
            r'\bđ[ăắa]k\s*r\'?la\b': "Xã Đắk RLa",
            r'\bn[aâ]m\s*n\'?đir\b': "Xã Nâm NĐir",
            r'\bn[aâ]m\s*n\'?jang\b': "Xã Nâm NJang",
            
            # Các xã/phường có chứa Đắk/Đăk phổ biến
            r'\bđ[ăắa]k\s*b[uú]k\s*so\b': "Xã Đắk Búk So",
            r'\bđ[ăắa]k\s*dr[oô]\b': "Xã Đắk Drô",
            r'\bđ[ăắa]k\s*g[aăằ]n\b': "Xã Đắk Gằn",
            r'\bđ[ăắa]k\s*ha\b': "Xã Đắk Ha",
            r'\bđ[ăắa]k\s*h[oò]a\b': "Xã Đắk Hòa",
            r'\bquảng\s*h[oò]a\b': "Xã Quảng Hoà",
            r'\bquảng\s*hoà\b': "Xã Quảng Hoà",
            r'\bđ[ăắa]k\s*m[oô]l\b': "Xã Đắk Môl",
            r'\bđ[ăắa]k\s*nang\b': "Xã Đắk Nang",
            r'\bđ[ăắa]k\s*ngo\b': "Xã Đắk Ngo",
            r'\bđ[ăắa]k\s*nia\b': "Xã Đắk Nia",
            r'\bđ[ăắa]k\s*plao\b': "Xã Đắk Plao",
            r'\bđ[ăắa]k\s*ru\b': "Xã Đắk Ru",
            r'\bđ[ăắa]k\s*sin\b': "Xã Đắk Sin",
            r'\bđ[ăắa]k\s*som\b': "Xã Đắk Som",
            r'\bđ[ăắa]k\s*s[oôôr]\b': "Xã Đắk Sôr",
            r'\bđ[ăắa]k\s*s[aăắ]k\b': "Xã Đắk Sắk",
            r'\bđ[ăắa]k\s*wer\b': "Xã Đắk Wer",
            r'\bđ[ăắa]k\s*wil\b': "Xã Đắk Wil"
        }
        
        # Compile regexes in advance for speed
        self.compiled_mappings = []
        for pat, canonical in self.mappings.items():
            # Use ignorecase for robustness against user input (e.g., "đắk R'măng")
            self.compiled_mappings.append((re.compile(pat, re.IGNORECASE), canonical))
            
    def normalize(self, question: str) -> str:
        """
        Quét qua câu hỏi và chuẩn hóa các danh từ riêng Hành chính (Xã, Huyện)
        về định dạng gốc 100% của Database.
        """
        normalized_q = question
        placeholders = {}
        for i, (pattern, canonical_name) in enumerate(self.compiled_mappings):
            placeholder = f"__CANONICAL_{i}__"
            placeholders[placeholder] = canonical_name
            
            # 1. Thay thế nếu có sẵn tiền tố hành chính (chuẩn hóa tiền tố)
            prefix_pattern = re.compile(r'\b(?:huyện|thành phố|thị xã|xã|phường|thị trấn)\s+' + pattern.pattern, re.IGNORECASE)
            normalized_q = prefix_pattern.sub(placeholder, normalized_q)
            
            # 2. Thay thế nếu không có tiền tố (tự động thêm tiền tố)
            normalized_q = pattern.sub(placeholder, normalized_q)
            
        # 3. Phục hồi placeholder về giá trị chuẩn
        for placeholder, canonical_name in placeholders.items():
            normalized_q = normalized_q.replace(placeholder, canonical_name)
            
        return normalized_q
        
    def sanitize_sql(self, sql_query: str) -> str:
        """
        [Plan A] Xử lý câu lệnh SQL trước khi thực thi để sửa các lỗi Syntax do dấu nháy đơn
        bị LLM sinh ngược lại (ảo giác), hoặc các lỗi escape nháy đơn không hợp lệ.
        Ví dụ: 
        ILIKE '%Đắk R'Măng%' -> ILIKE '%Đắk RMăng%'
        ILIKE '%Đắk N'Drung%' -> ILIKE '%Đắk N''Drung%' (Escape đúng chuẩn SQL)
        """
        sanitized = sql_query
        
        # 1. Các trường hợp Canonical DB name KHÔNG có nháy đơn, nhưng LLM thường sinh ngược lại
        # Xóa dấu nháy đơn nếu nó nằm giữa 2 chữ cái trong các từ đặc biệt
        remove_quote_patterns = [
            ("R", "Măng"), ("R", "Lấp"), ("R", "Tíh"), ("R", "Moan"),
            ("T", "Ling"), ("R", "La"), ("N", "Đir"), ("N", "Jang"),
            ("D", "Róng"), ("N", "Drót")
        ]
        
        for prefix, suffix in remove_quote_patterns:
            # Match prefix + one or more quotes + suffix (e.g., R'Măng, R''Măng)
            pattern = rf"{prefix}'+{suffix}"
            target = f"{prefix}{suffix}"
            sanitized = re.sub(pattern, target, sanitized, flags=re.IGNORECASE)
            
        # 2. Các trường hợp Canonical DB name CÓ nháy đơn, bắt buộc phải escape bằng 2 nháy đơn ('') trong SQL string
        # Đắk N'Drung -> Đắk N''Drung
        # Chuyển đổi 1 hoặc nhiều dấu nháy liên tiếp thành ĐÚNG 2 dấu nháy
        sanitized = re.sub(r"N'+Drung", "N''Drung", sanitized, flags=re.IGNORECASE)
        
        # 3. Chuẩn hóa dấu thanh Quảng Hòa -> Quảng Hoà
        sanitized = re.sub(r"Quảng\s*Hòa", "Quảng Hoà", sanitized, flags=re.IGNORECASE)
        
        # 4. Sửa lỗi ảo giác tên cột có dấu chấm (như deprivation.healthInsurance) bị LLM sinh thiếu ngoặc kép hoặc sai ngoặc
        prefixes_tuple = ("administrative", "family", "member", "deprivation", "transition", "policy", "support", "reason", "children")
        prefixes_pat = "|".join(prefixes_tuple)
        
        # Trường hợp 4a: LLM sinh "deprivation"."healthInsurance" hoặc deprivation."healthInsurance" hoặc "deprivation".healthInsurance
        def fix_broken_quotes(m):
            alias = m.group(1) or ""
            pref = m.group(2)
            col = m.group(3)
            return f'{alias}"{pref}.{col}"'
            
        sanitized = re.sub(rf'(?:([a-zA-Z0-9_]+)\.)?["\']?({prefixes_pat})["\']?\.["\']([a-zA-Z0-9_]+)["\']?', fix_broken_quotes, sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(rf'(?:([a-zA-Z0-9_]+)\.)?["\']({prefixes_pat})["\']\.["\']?([a-zA-Z0-9_]+)["\']?', fix_broken_quotes, sanitized, flags=re.IGNORECASE)
        
        # Trường hợp 4b: LLM sinh hoàn toàn không có ngoặc kép: deprivation.healthInsurance hoặc h.deprivation.healthInsurance
        pattern_unquoted = rf'(?<!["\'\w\.0-9])(?:([a-zA-Z0-9_]+)\.)?({prefixes_pat})\.([a-zA-Z0-9_]+)(?!["\'\w])'
        def fix_unquoted(m):
            alias = m.group(1)
            pref = m.group(2)
            col = m.group(3)
            if alias:
                return f'{alias}."{pref}.{col}"'
            else:
                return f'"{pref}.{col}"'
        sanitized = re.sub(pattern_unquoted, fix_unquoted, sanitized, flags=re.IGNORECASE)
        
        return sanitized

# Demo
if __name__ == "__main__":
    normalizer = CanonicalNormalizer()
    q = "Tỉ lệ nghèo tại xã Đắk R'Măng năm 2024?"
    print(normalizer.normalize(q))
    q2 = "tình trạng thiếu hụt bhyt tại huyện đăk glong và gia nghĩa 2024"
    print(normalizer.normalize(q2))
