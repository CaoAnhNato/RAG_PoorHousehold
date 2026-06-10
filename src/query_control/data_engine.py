# -*- coding: utf-8 -*-
"""
Module DuckDB Engine cung cấp môi trường thực thi SQL an toàn, nhanh chóng
và cung cấp thông tin profile/metadata của các bảng dữ liệu.
"""

from __future__ import annotations
import os
import json
import time
from pathlib import Path
from typing import Any
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[2]

class DuckDBEngine:
    def __init__(self, config_path: str):
        """Khởi tạo DuckDB Engine với cấu hình tương ứng."""
        self.config_path = Path(config_path)
        if not self.config_path.is_absolute():
            self.config_path = PROJECT_ROOT / self.config_path
            
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
            
        self.duckdb_path = PROJECT_ROOT / self.config.get("duckdb_path", "Runtime/duckdb/intern_chatbot.duckdb")
        self.max_rows = self.config.get("execution", {}).get("max_result_rows", 5000)
        self.default_limit = self.config.get("execution", {}).get("default_limit", 100)
        self.read_only = self.config.get("execution", {}).get("read_only", True)
        self.conn = None

    def connect(self):
        """Kết nối tới cơ sở dữ liệu DuckDB."""
        if not self.duckdb_path.exists():
            raise FileNotFoundError(f"Cơ sở dữ liệu DuckDB không tồn tại tại: {self.duckdb_path}. Vui lòng chạy duckdb_loader.py trước.")
        # Kết nối ở chế độ read-only
        self.conn = duckdb.connect(str(self.duckdb_path), read_only=self.read_only)

    def execute_sql(self, sql: str, parameters: dict | None = None) -> dict[str, Any]:
        """
        Thực thi câu SQL DuckDB và trả về kết quả cấu trúc.
        """
        output = {
            "success": True,
            "data": [],
            "columns": [],
            "row_count": 0,
            "execution_ms": 0.0,
            "error": None,
            "warnings": []
        }
        
        start_time = time.perf_counter()
        
        try:
            if not self.conn:
                self.connect()
                
            # Thực thi truy vấn
            if parameters:
                rel = self.conn.execute(sql, parameters)
            else:
                rel = self.conn.execute(sql)
                
            # Lấy thông tin cột
            columns = [desc[0] for desc in rel.description] if rel.description else []
            output["columns"] = columns
            
            # Đọc toàn bộ dữ liệu dưới dạng danh sách dict
            raw_data = rel.fetchall()
            row_count = len(raw_data)
            
            # Cắt bớt nếu vượt quá số dòng tối đa cấu hình
            if row_count > self.max_rows:
                raw_data = raw_data[:self.max_rows]
                output["warnings"].append(
                    f"Kết quả truy vấn vượt quá giới hạn tối đa {self.max_rows} dòng. Đã cắt bớt kết quả."
                )
                
            # Map dữ liệu sang dict
            data_dicts = []
            for row in raw_data:
                data_dicts.append(dict(zip(columns, row)))
                
            output["data"] = data_dicts
            output["row_count"] = len(data_dicts)
            
        except Exception as e:
            output["success"] = False
            output["error"] = str(e)
            
        finally:
            end_time = time.perf_counter()
            output["execution_ms"] = (end_time - start_time) * 1000.0
            
        return output

    def validate_runtime_ready(self) -> dict[str, Any]:
        """
        Kiểm tra trạng thái sẵn sàng của DuckDB runtime.
        """
        status = {
            "ready": True,
            "duckdb_file_exists": False,
            "households_table_exists": False,
            "members_table_exists": False,
            "errors": [],
            "warnings": []
        }
        
        if self.duckdb_path.exists():
            status["duckdb_file_exists"] = True
        else:
            status["ready"] = False
            status["errors"].append("Tệp tin DuckDB không tồn tại.")
            return status
            
        try:
            if not self.conn:
                self.connect()
                
            # Kiểm tra sự tồn tại của bảng households
            tables_df = self.conn.execute("SHOW TABLES").df()
            existing_tables = tables_df["name"].tolist() if not tables_df.empty else []
            
            if "households" in existing_tables:
                status["households_table_exists"] = True
            else:
                status["ready"] = False
                status["errors"].append("Bảng 'households' không tồn tại trong DuckDB.")
                
            if "members" in existing_tables:
                status["members_table_exists"] = True
            else:
                status["warnings"].append("Bảng 'members' (tùy chọn) không tồn tại trong DuckDB.")
                
        except Exception as e:
            status["ready"] = False
            status["errors"].append(f"Không thể kết nối hoặc truy vấn DuckDB: {e}")
            
        return status

    def get_table_profile(self, table_name: str) -> dict[str, Any]:
        """
        Lấy hồ sơ tóm tắt cấu trúc và thông tin của bảng.
        """
        profile = {
            "table_name": table_name,
            "exists": False,
            "row_count": 0,
            "columns": [],
            "sample_rows": []
        }
        
        try:
            if not self.conn:
                self.connect()
                
            tables_df = self.conn.execute("SHOW TABLES").df()
            existing_tables = tables_df["name"].tolist() if not tables_df.empty else []
            
            if table_name not in existing_tables:
                return profile
                
            profile["exists"] = True
            
            # Lấy số dòng
            cnt_res = self.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
            profile["row_count"] = cnt_res[0] if cnt_res else 0
            
            # Lấy thông tin cột
            cols_res = self.conn.execute(f"PRAGMA table_info('{table_name}')").fetchall()
            profile["columns"] = [
                {
                    "cid": col[0],
                    "name": col[1],
                    "type": col[2],
                    "notnull": bool(col[3]),
                    "dflt_value": col[4],
                    "pk": bool(col[5])
                }
                for col in cols_res
            ]
            
            # Lấy sample 5 dòng
            sample_res = self.conn.execute(f"SELECT * FROM {table_name} LIMIT 5")
            cols = [desc[0] for desc in sample_res.description] if sample_res.description else []
            sample_data = sample_res.fetchall()
            
            for row in sample_data:
                profile["sample_rows"].append(dict(zip(cols, row)))
                
        except Exception as e:
            pass
            
        return profile
