import json
import os
from rapidfuzz import process, fuzz
from src.query_control.v2_3.extractors.base import BaseExtractor
from src.query_control.v2_3.models import ExtractionReport

class LocationExtractor(BaseExtractor):
    def __init__(self, mapping_path: str = "data/Processed/metadata/district_commune_mapping.json"):
        with open(mapping_path, 'r', encoding='utf-8') as f:
            self.mapping = json.load(f)
            
        self.districts = {}
        self.communes = {}
        self.commune_to_district = {}
        
        prefixes_to_remove = ["huyện ", "thành phố ", "thị xã ", "xã ", "phường ", "thị trấn "]
        
        def get_alias(name: str) -> str:
            lower_name = name.lower()
            for prefix in prefixes_to_remove:
                if lower_name.startswith(prefix):
                    return lower_name[len(prefix):].strip()
            return lower_name

        for d, comms in self.mapping.items():
            d_alias = get_alias(d)
            self.districts[d_alias] = d
            # Vẫn giữ key gốc lowercase đề phòng người dùng gõ đủ "huyện đắk song"
            self.districts[d.lower()] = d
            
            for c in comms:
                c_alias = get_alias(c)
                self.communes[c_alias] = c
                self.communes[c.lower()] = c
                self.commune_to_district[c] = d
                
    def extract(self, text: str, report: ExtractionReport):
        # 1. Tìm Huyện (District)
        # Sử dụng partial_ratio để tìm chuỗi con khớp trong câu hỏi
        district_matches = process.extract(
            text, 
            self.districts.keys(), 
            scorer=fuzz.partial_ratio, 
            limit=None, 
            score_cutoff=90
        )
        
        found_districts = set()
        for match in district_matches:
            # match is a tuple: (choice, score, index)
            district_key = match[0]
            district_name = self.districts[district_key]
            found_districts.add(district_name)
            
        found_districts = list(found_districts)
        if found_districts:
            report.add_resolved("administrative.district", found_districts)
            
        # 2. Tìm Xã (Commune)
        commune_matches = process.extract(
            text, 
            self.communes.keys(), 
            scorer=fuzz.partial_ratio, 
            limit=None, 
            score_cutoff=90
        )
        
        found_communes = set()
        for match in commune_matches:
            commune_key = match[0]
            commune_name = self.communes[commune_key]
            found_communes.add(commune_name)
            
        found_communes = list(found_communes)
        if found_communes:
            report.add_resolved("administrative.commune", found_communes)
            
            # Kiểm tra logic: Nếu có xã, thì xã đó phải thuộc huyện đã tìm thấy (hoặc thêm huyện vào nếu thiếu)
            for c in found_communes:
                parent_district = self.commune_to_district[c]
                if not found_districts:
                    report.add_resolved("administrative.district", [parent_district])
                    found_districts.append(parent_district)
                elif parent_district not in found_districts:
                    report.add_issue(
                        entity_type="location",
                        issue_type="ambiguous",
                        message=f"Xã '{c}' thuộc '{parent_district}' nhưng câu hỏi lại nhắc đến huyện khác {found_districts}."
                    )
