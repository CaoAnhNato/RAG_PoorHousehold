# -*- coding: utf-8 -*-
"""
Module dọn dẹp thư mục gốc và chuẩn hóa vị trí các tệp tin phát triển trong dự án.
"""
import os
import sys
import shutil
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def clean_project_root() -> bool:
    """
    Dọn dẹp các tệp tin log rác và di chuyển các tệp tin script/kiểm thử từ thư mục gốc vào đúng thư mục chức năng.
    
    Args:
        Không có.
        
    Returns:
        bool: Trả về True nếu quá trình dọn dẹp hoàn tất thành công.
    """
    root_dir = Path(__file__).resolve().parent.parent
    
    # Danh sách tệp tin log rác cần xóa
    junk_logs = [
        "debug_chart.txt",
        "debug_line_chart.txt",
        "debug_sql.txt"
    ]
    
    # Danh sách tệp tin tiện ích/script cần chuyển vào thư mục scripts/
    scripts_to_move = [
        "add_missing_dims.py",
        "update_quest_ans.py"
    ]
    
    # Danh sách tệp tin kiểm thử/nháp cần chuyển vào thư mục test/debug/
    tests_to_move = [
        "dump_counts.py",
        "scratch_check_QA_logic.py",
        "scratch_sql_executor.py",
        "test_counts.py",
        "test_report_11_15.py"
    ]
    
    print("=== BẮT ĐẦU DỌN DẸP THƯ MỤC GỐC ===")
    
    # 1. Xóa tệp tin log rác
    for log_file in junk_logs:
        target = root_dir / log_file
        if target.exists():
            try:
                target.unlink()
                print(f"[Đã xóa] {log_file}")
            except Exception as e:
                print(f"[Lỗi xóa] {log_file}: {e}")
                
    # 2. Di chuyển script vào thư mục scripts/
    scripts_dir = root_dir / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    for script_file in scripts_to_move:
        src = root_dir / script_file
        dest = scripts_dir / script_file
        if src.exists():
            try:
                if dest.exists():
                    dest.unlink()
                shutil.move(str(src), str(dest))
                print(f"[Đã di chuyển] {script_file} -> scripts/")
            except Exception as e:
                print(f"[Lỗi di chuyển] {script_file}: {e}")
                
    # 3. Di chuyển tệp tin kiểm thử/nháp vào thư mục test/debug/
    debug_dir = root_dir / "test" / "debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    for test_file in tests_to_move:
        src = root_dir / test_file
        dest = debug_dir / test_file
        if src.exists():
            try:
                if dest.exists():
                    dest.unlink()
                shutil.move(str(src), str(dest))
                print(f"[Đã di chuyển] {test_file} -> test/debug/")
            except Exception as e:
                print(f"[Lỗi di chuyển] {test_file}: {e}")
                
    print("=== HOÀN TẤT DỌN DẸP ===")
    return True

if __name__ == "__main__":
    clean_project_root()
