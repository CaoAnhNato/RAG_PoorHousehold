import json
import os
from typing import Dict, Any, List

class VisualizationPlanner:
    def __init__(self, metadata_dir: str = "data/Processed/metadata"):
        self.metadata_dir = metadata_dir
        self.rules = self._load_json("chart_rules.json").get("rules", [])
        self.default_chart = self._load_json("chart_rules.json").get("default_chart_type", "table")
        self.labels = self._load_json("visual_labels.json")
        self.templates = self._load_json("chart_templates.json")

    def _load_json(self, filename: str) -> Dict:
        filepath = os.path.join(self.metadata_dir, filename)
        if not os.path.exists(filepath):
            return {}
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def plan_chart(self, query_plan: Dict[str, Any], result_schema: Dict[str, str]) -> Dict[str, Any]:
        dimensions = query_plan.get("dimensions", [])
        metrics = query_plan.get("metrics", [])
        
        num_dims = len(dimensions)
        num_metrics = len(metrics)
        
        has_time = "year" in dimensions
        is_top_k = query_plan.get("limit") is not None
        
        # Simplified percentage check
        is_percentage = any("rate" in m.lower() or "percentage" in m.lower() for m in metrics)

        selected_chart = self.default_chart
        for rule in self.rules:
            cond = rule["condition"]
            match = True
            if cond.get("time_dimension") and not has_time:
                match = False
            if "max_dimensions" in cond and num_dims > cond["max_dimensions"]:
                match = False
            if "dimensions" in cond and num_dims != cond["dimensions"]:
                match = False
            if "metrics" in cond and num_metrics != cond["metrics"]:
                match = False
            if cond.get("is_top_k") and not is_top_k:
                match = False
            if cond.get("is_percentage") and not is_percentage:
                match = False
                
            if match:
                selected_chart = rule["chart_type"]
                break
                
        # Generate Spec
        spec = self.templates.get("base_template", {}).copy()
        spec["chart_type"] = selected_chart
        
        if num_dims > 0:
            spec["x"] = dimensions[0]
            if num_dims > 1:
                spec["color"] = dimensions[1]
                
        if num_metrics > 0:
            y_field = metrics[0]
            
            # Ưu tiên sử dụng metric tỷ lệ nếu câu hỏi có nhắc đến tỷ lệ
            if is_percentage:
                for m in metrics:
                    if "rate" in m.lower() or "percentage" in m.lower():
                        y_field = m
                        break

            # Đồng bộ hoá tên cột (xử lý alias từ SQLCompiler)
            if result_schema and y_field not in result_schema:
                possible_y = [col for col in result_schema.keys() if col not in dimensions and col != "year"]
                if possible_y:
                    found = False
                    for col in possible_y:
                        if is_percentage and ("rate" in col.lower() or "percentage" in col.lower()):
                            y_field = col
                            found = True
                            break
                    if not found:
                        y_field = possible_y[0]

            spec["y"] = y_field
            if selected_chart == "horizontal_bar":
                # Swap X and Y for horizontal
                spec["x"], spec["y"] = spec.get("y"), spec.get("x")
                spec["orientation"] = "h"

        title_parts = []
        if num_metrics > 0:
            title_parts.append(self.labels.get(metrics[0], metrics[0]))
        if num_dims > 0:
            title_parts.append("theo " + " và ".join([self.labels.get(d, d) for d in dimensions]))
            
        spec["title"] = " ".join(title_parts).capitalize()
        if is_percentage:
            spec["unit"] = "%"
            
        return spec
