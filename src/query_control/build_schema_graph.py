# -*- coding: utf-8 -*-
"""
Module xây dựng Schema Graph cho dữ liệu hộ gia đình và thành viên.
Thực hiện quét toàn bộ file Excel đã tiền xử lý để xác định schema vật lý,
kiểu dữ liệu, tỷ lệ null và các mối quan hệ khoá.
"""

from __future__ import annotations
import json
import os
from pathlib import Path
import datetime as dt
from typing import Any
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "Processed"
METADATA_DIR = PROCESSED_DIR / "metadata"
QUERY_CONTROL_METADATA_DIR = METADATA_DIR / "query_control"
REPORT_PATH = QUERY_CONTROL_METADATA_DIR / "metadata_build_report.md"

def map_dtype(dtype: Any, col_name: str) -> str:
    """Ánh xạ kiểu dữ liệu pandas sang kiểu dữ liệu chuẩn JSON."""
    dtype_str = str(dtype).lower()
    if "int" in dtype_str:
        return "integer"
    elif "float" in dtype_str or "double" in dtype_str:
        return "float"
    elif "bool" in dtype_str:
        return "boolean"
    elif "datetime" in dtype_str or "date" in dtype_str:
        return "date"
    else:
        # Kiểm tra theo tên cột nếu là object
        if col_name in ["administrative.year", "year"]:
            return "integer"
        return "string"

def infer_semantic_type(col_name: str, dtype_str: str) -> str:
    """Suy luận kiểu ngữ nghĩa của cột dựa trên tên và kiểu dữ liệu vật lý."""
    name_lower = col_name.lower()
    if any(k in name_lower for k in ["code", "id", "uuid"]):
        return "id"
    if any(k in name_lower for k in ["year", "date", "time"]):
        return "time"
    if any(k in name_lower for k in ["district", "commune", "province", "village_or_group", "village"]):
        return "geography"
    if dtype_str == "boolean":
        return "boolean"
    if dtype_str in ["integer", "float"]:
        if any(k in name_lower for k in ["count", "point", "score", "size", "age"]):
            return "measure"
        return "category"
    if dtype_str == "string":
        if any(k in name_lower for k in ["classify", "gender", "ethnicity", "status"]):
            return "category"
        return "text"
    return "unknown"

def scan_excel_files(node_type: str, files: list[Path]) -> tuple[dict[str, Any], list[str]]:
    """Quét các tệp Excel và trích xuất thông tin schema chi tiết."""
    merged_columns: dict[str, Any] = {}
    warnings: list[str] = []
    
    for file_path in files:
        rel_path = file_path.relative_to(PROJECT_ROOT).as_posix()
        try:
            # Chỉ đọc schema trước để tránh tốn bộ nhớ nếu file lớn, nhưng ở đây
            # load đầy đủ để tính null_rate và lấy mẫu giá trị
            df = pd.read_excel(file_path)
            
            # Suy luận năm và huyện từ đường dẫn nếu không có cột
            year_val = None
            for part in file_path.parts:
                if part.isdigit() and len(part) == 4:
                    year_val = int(part)
                    break
            
            district_val = file_path.stem.replace("_members", "").strip()
            
            # Nếu trong dataframe thiếu các cột phân vùng, tự động thêm vào
            if "administrative.year" not in df.columns and "year" not in df.columns:
                df["administrative.year"] = year_val or 2023
            if "administrative.district" not in df.columns and "district" not in df.columns:
                df["administrative.district"] = district_val
                
            for col in df.columns:
                series = df[col]
                null_count = int(series.isna().sum())
                total_count = len(series)
                null_rate = null_count / total_count if total_count > 0 else 0.0
                
                # Trích xuất sample values
                non_nulls = series.dropna()
                sample_candidates = non_nulls.unique().tolist()
                samples = []
                for val in sample_candidates:
                    if len(samples) >= 5:
                        break
                    # Chuẩn hoá kiểu dữ liệu để serialize sang JSON
                    if isinstance(val, (dt.datetime, dt.date)):
                        samples.append(val.isoformat())
                    elif isinstance(val, (int, float, bool, str)):
                        # Kiểm tra nan
                        if isinstance(val, float) and pd.isna(val):
                            continue
                        samples.append(val)
                    else:
                        samples.append(str(val))
                        
                dtype = map_dtype(series.dtype, col)
                sem_type = infer_semantic_type(col, dtype)
                
                if col not in merged_columns:
                    roles = ["dimension"]
                    if sem_type == "id":
                        roles.append("join_key")
                    elif sem_type == "measure":
                        roles.append("measure")
                    
                    merged_columns[col] = {
                        "physical_name": col,
                        "normalized_name": col,
                        "data_type": dtype,
                        "semantic_type": sem_type,
                        "null_rates": [null_rate],
                        "sample_values": samples,
                        "source_files": [rel_path],
                        "candidate_roles": roles
                    }
                else:
                    # Cập nhật thông tin cột đã có
                    col_info = merged_columns[col]
                    col_info["null_rates"].append(null_rate)
                    col_info["source_files"].append(rel_path)
                    # Merge samples
                    for s in samples:
                        if s not in col_info["sample_values"] and len(col_info["sample_values"]) < 5:
                            col_info["sample_values"].append(s)
                            
        except Exception as e:
            warnings.append(f"Không thể đọc file {rel_path}: {e}")
            
    # Tính toán null_rate trung bình
    for col, col_info in merged_columns.items():
        col_info["null_rate"] = sum(col_info["null_rates"]) / len(col_info["null_rates"])
        del col_info["null_rates"]
        
    return merged_columns, warnings

def main() -> None:
    QUERY_CONTROL_METADATA_DIR.mkdir(parents=True, exist_ok=True)
    
    warnings: list[str] = []
    
    # 1. Tìm các file dữ liệu hộ gia đình
    household_files: list[Path] = []
    for year in ["2023", "2024"]:
        year_dir = PROCESSED_DIR / year
        if year_dir.exists():
            for f in year_dir.glob("*.xlsx"):
                if f.name != "desktop.ini":
                    household_files.append(f)
                    
    # 2. Tìm các file thành viên
    member_files: list[Path] = []
    for year in ["2023", "2024"]:
        member_dir = PROCESSED_DIR / year / "_members"
        if member_dir.exists():
            for f in member_dir.glob("*.xlsx"):
                if f.name != "desktop.ini":
                    member_files.append(f)
                    
    if not household_files:
        warnings.append("Cảnh báo: Không tìm thấy file dữ liệu hộ gia đình trong Processed/2023 hoặc Processed/2024!")
    if not member_files:
        warnings.append("Cảnh báo: Không tìm thấy file dữ liệu thành viên trong Processed/2023/_members hoặc Processed/2024/_members!")
        
    # 3. Quét cột và kiểu dữ liệu
    print("Đang quét dữ liệu hộ gia đình...")
    household_cols, hh_warnings = scan_excel_files("households", household_files)
    warnings.extend(hh_warnings)
    
    print("Đang quét dữ liệu thành viên...")
    member_cols, mem_warnings = scan_excel_files("members", member_files)
    warnings.extend(mem_warnings)
    
    # 4. Xác định quan hệ khóa ngoại (foreign key candidate)
    member_fks = []
    if "family.code" in member_cols and "family.code" in household_cols:
        member_fks.append({
            "column": "family.code",
            "ref_table": "households",
            "ref_column": "family.code"
        })
        
    # 5. Xây dựng Schema Graph cấu trúc JSON
    schema_graph = {
        "version": "1.0",
        "root_path": "data/Processed",
        "generated_at": dt.datetime.now().isoformat(),
        "nodes": {
            "households": {
                "node_type": "fact_table",
                "description": "Dữ liệu hộ gia đình đã xử lý",
                "grain": "1 row = 1 household in one review year",
                "source_files": [f.relative_to(PROJECT_ROOT).as_posix() for f in household_files],
                "primary_key_candidates": ["family.code", "administrative.year"],
                "columns": household_cols,
                "partitions": ["year", "district"],
                "default_time_column": "administrative.year"
            },
            "members": {
                "node_type": "fact_table",
                "description": "Dữ liệu thành viên hộ nếu tồn tại",
                "grain": "1 row = 1 household member",
                "source_files": [f.relative_to(PROJECT_ROOT).as_posix() for f in member_files],
                "primary_key_candidates": ["family.code", "member.code"],  # Gia định khoá chính
                "foreign_key_candidates": member_fks,
                "columns": member_cols
            }
        },
        "edges": [
            {
                "from_node": "members",
                "to_node": "households",
                "edge_type": "many_to_one",
                "join_columns": [
                    {"from_column": "family.code", "to_column": "family.code"}
                ]
            }
        ],
        "join_paths": {
            "members_to_households": {
                "steps": [
                    {
                        "from_node": "members",
                        "to_node": "households",
                        "join_columns": [
                            {"from_column": "family.code", "to_column": "family.code"}
                        ]
                    }
                ]
            }
        }
    }
    
    # Ghi file schema_graph.json
    output_file = QUERY_CONTROL_METADATA_DIR / "schema_graph.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(schema_graph, f, ensure_ascii=False, indent=2)
    print(f"Đã lưu Schema Graph tại: {output_file}")
    
    # 6. Ghi báo cáo metadata_build_report.md
    report_content = []
    report_content.append("# BÁO CÁO XÂY DỰNG METADATA TRUY VẤN (METADATA BUILD REPORT)\n")
    report_content.append(f"**Thời gian sinh:** {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report_content.append("## 1. Kết quả quét Schema Graph")
    report_content.append(f"- **Số file hộ gia đình quét thành công:** {len(household_files)}")
    report_content.append(f"- **Số file thành viên quét thành công:** {len(member_files)}")
    report_content.append(f"- **Số cột phát hiện trong households:** {len(household_cols)}")
    report_content.append(f"- **Số cột phát hiện trong members:** {len(member_cols)}\n")
    
    if warnings:
        report_content.append("## 2. Cảnh báo & Lỗi (Warnings)")
        for w in warnings:
            report_content.append(f"- [WARNING] {w}")
    else:
        report_content.append("## 2. Cảnh báo & Lỗi (Warnings)\n- Không có cảnh báo hay lỗi nghiêm trọng nào được ghi nhận.")
        
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(report_content))
    print(f"Đã lưu báo cáo tại: {REPORT_PATH}")

if __name__ == "__main__":
    main()
