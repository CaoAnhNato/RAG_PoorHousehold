# -*- coding: utf-8 -*-
"""
Module tải dữ liệu từ các tệp Excel đã tiền xử lý vào DuckDB dưới dạng Parquet.
Hỗ trợ kiểm tra thời gian thay đổi tệp (modified time) để tránh tải lại nếu không có thay đổi.
"""

from __future__ import annotations
import os
import json
import sys
import argparse
import logging
from pathlib import Path
import pandas as pd
import duckdb

# Thiết lập log tiếng Việt
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("duckdb_loader")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "Processed" / "metadata" / "query_control" / "duckdb_config.json"

def load_config() -> dict:
    """Tải tệp cấu hình duckdb_config.json."""
    if not CONFIG_PATH.exists():
        logger.error(f"Không tìm thấy cấu hình DuckDB tại: {CONFIG_PATH}")
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def check_needs_rebuild(config: dict) -> bool:
    """Kiểm tra xem dữ liệu có cần build lại hay không dựa trên thời gian sửa đổi file."""
    duckdb_path = PROJECT_ROOT / config.get("duckdb_path", "Runtime/duckdb/intern_chatbot.duckdb")
    parquet_dir = PROJECT_ROOT / config.get("parquet_dir", "Runtime/parquet")
    
    if not duckdb_path.exists():
        return True
    
    # Kiểm tra xem có tệp parquet nào thiếu không
    for table_name, table_cfg in config.get("tables", {}).items():
        out_pq = PROJECT_ROOT / table_cfg.get("output_parquet")
        if not out_pq.exists():
            return True
            
    # Lấy thời điểm thay đổi lớn nhất của các tệp nguồn Excel
    max_source_mtime = 0.0
    source_root = PROJECT_ROOT / config.get("source_root", "Processed")
    
    for table_name, table_cfg in config.get("tables", {}).items():
        for s_dir in table_cfg.get("source_dirs", []):
            full_s_dir = PROJECT_ROOT / s_dir
            if not full_s_dir.exists():
                continue
            for f in full_s_dir.glob("**/*.xlsx"):
                if f.name.startswith("~$"):
                    continue
                mtime = f.stat().st_mtime
                if mtime > max_source_mtime:
                    max_source_mtime = mtime
                    
    # Lấy thời điểm tạo của tệp DuckDB
    db_mtime = duckdb_path.stat().st_mtime
    
    # Nếu có bất kỳ tệp nguồn nào mới hơn tệp DB, cần build lại
    return max_source_mtime > db_mtime

def process_table_data(table_name: str, table_cfg: dict, source_root: Path) -> pd.DataFrame | None:
    """Đọc và gộp các tệp Excel thành một DataFrame duy nhất."""
    dfs = []
    
    for s_dir in table_cfg.get("source_dirs", []):
        full_s_dir = PROJECT_ROOT / s_dir
        if not full_s_dir.exists():
            logger.warning(f"Thư mục nguồn không tồn tại: {full_s_dir}")
            continue
            
        # Tìm kiếm các tệp Excel
        excel_files = list(full_s_dir.glob("*.xlsx"))
        # Hỗ trợ đệ quy cho cả _members nằm trong thư mục con
        if table_name == "members":
            excel_files = list(full_s_dir.glob("**/*.xlsx"))
            
        for f in excel_files:
            if f.name.startswith("~$"):
                continue
            try:
                logger.info(f"Đang đọc tệp: {f.name} ({s_dir})")
                # Đọc tệp excel
                df = pd.read_excel(f)
                if df.empty:
                    continue
                
                # Suy luận các trường còn thiếu từ cấu trúc thư mục/tên file
                # 1. Năm (Year): suy luận từ đường dẫn nếu thiếu cột administrative.year
                if "administrative.year" not in df.columns:
                    # Tìm xem đường dẫn có chứa 2023 hay 2024 không
                    if "2023" in str(f.resolve()):
                        df["administrative.year"] = 2023
                    elif "2024" in str(f.resolve()):
                        df["administrative.year"] = 2024
                    else:
                        df["administrative.year"] = 2024  # mặc định
                
                # 2. Huyện (District): suy luận từ tên file
                if "administrative.district" not in df.columns:
                    district_name = f.stem
                    df["administrative.district"] = district_name
                
                dfs.append(df)
            except Exception as e:
                logger.warning(f"Không thể đọc tệp {f}: {e}")
                
    if not dfs:
        return None
        
    # Gộp và loại bỏ trùng lặp
    merged_df = pd.concat(dfs, ignore_index=True)
    merged_df.drop_duplicates(inplace=True)
    return merged_df

def build_runtime_database(config: dict, rebuild: bool = False):
    """Xây dựng Parquet và DuckDB database từ nguồn Excel."""
    duckdb_path = PROJECT_ROOT / config.get("duckdb_path", "Runtime/duckdb/intern_chatbot.duckdb")
    parquet_dir = PROJECT_ROOT / config.get("parquet_dir", "Runtime/parquet")
    source_root = PROJECT_ROOT / config.get("source_root", "Processed")
    
    # Tạo các thư mục Runtime cần thiết
    duckdb_path.parent.mkdir(parents=True, exist_ok=True)
    parquet_dir.mkdir(parents=True, exist_ok=True)
    
    # Kiểm tra xem có cần build không
    if not rebuild and not check_needs_rebuild(config):
        logger.info("Dữ liệu DuckDB/Parquet đã mới nhất. Bỏ qua bước xây dựng lại.")
        return
        
    logger.info("Bắt đầu xây dựng lại cơ sở dữ liệu DuckDB/Parquet...")
    
    # Khởi tạo kết nối DuckDB
    if duckdb_path.exists():
        try:
            os.remove(duckdb_path)
        except Exception as e:
            logger.warning(f"Không thể xóa file DB cũ {duckdb_path}: {e}")
            
    con = duckdb.connect(str(duckdb_path))
    
    for table_name, table_cfg in config.get("tables", {}).items():
        logger.info(f"Đang xử lý bảng: {table_name}...")
        df = process_table_data(table_name, table_cfg, source_root)
        
        if df is None or df.empty:
            if table_cfg.get("optional", False):
                logger.warning(f"Bảng tùy chọn '{table_name}' không có dữ liệu để nạp.")
                continue
            else:
                logger.error(f"Lỗi: Bảng bắt buộc '{table_name}' không tìm thấy dữ liệu!")
                sys.exit(1)
                
        # Xuất ra Parquet
        out_parquet = PROJECT_ROOT / table_cfg.get("output_parquet")
        out_parquet.parent.mkdir(parents=True, exist_ok=True)
        
        # Chuẩn hóa kiểu dữ liệu cho pandas object columns để tránh lỗi trộn kiểu (mixed types) trong PyArrow
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].apply(lambda x: str(x) if pd.notna(x) else None)
                
        logger.info(f"Đang lưu Parquet tại: {out_parquet} (Dòng: {len(df)})")
        df.to_parquet(out_parquet, index=False)
        
        # Nạp vào DuckDB dưới dạng bảng vật lý
        duckdb_table = table_cfg.get("duckdb_table", table_name)
        # Sử dụng đường dẫn tương đối hoặc tuyệt đối cho DuckDB nạp trực tiếp Parquet
        con.execute(f"CREATE TABLE {duckdb_table} AS SELECT * FROM read_parquet('{out_parquet.as_posix()}')")
        logger.info(f"Đã tạo bảng '{duckdb_table}' trong DuckDB thành công.")
        
    con.close()
    logger.info("Xây dựng cơ sở dữ liệu DuckDB/Parquet thành công!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DuckDB Loader - Nạp dữ liệu Excel sang DuckDB/Parquet")
    parser.add_argument("--rebuild", action="store_true", help="Bắt buộc xây dựng lại từ đầu")
    args = parser.parse_args()
    
    cfg = load_config()
    build_runtime_database(cfg, rebuild=args.rebuild)
