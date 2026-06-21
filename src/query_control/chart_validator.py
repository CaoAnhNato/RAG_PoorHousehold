import json
import os
from typing import Dict, Any, Tuple

class ChartValidator:
    def __init__(self, metadata_dir: str = "data/Processed/metadata"):
        self.metadata_dir = metadata_dir
        self.constraints = self._load_json("chart_constraints.json")

    def _load_json(self, filename: str) -> Dict:
        filepath = os.path.join(self.metadata_dir, filename)
        if not os.path.exists(filepath):
            return {}
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def validate(self, spec: Dict[str, Any], data_preview: list = None) -> Tuple[bool, str]:
        chart_type = spec.get("chart_type")
        if not chart_type or chart_type == "table":
            return True, ""
            
        constraint = self.constraints.get(chart_type, {})
        
        # Check required dimensions
        req_dim = constraint.get("require_dimension")
        if req_dim:
            if spec.get("x") != req_dim and spec.get("y") != req_dim and spec.get("color") != req_dim:
                return False, f"Biểu đồ {chart_type} yêu cầu chiều dữ liệu phải là {req_dim}."
                
        # Check max categories if data preview is available
        max_cat = constraint.get("max_categories")
        if max_cat and data_preview:
            # simple check: if result length > max_cat
            if len(data_preview) > max_cat:
                return False, f"Biểu đồ {chart_type} không hỗ trợ hiển thị quá {max_cat} hạng mục (dữ liệu có {len(data_preview)})."
                
        return True, ""
