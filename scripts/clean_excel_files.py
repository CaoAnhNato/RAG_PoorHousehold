import os
import pandas as pd
from pathlib import Path

def clean_excel_files():
    base_dir = Path("data/Processed")
    excel_files = list(base_dir.rglob("*.xlsx"))
    
    count = 0
    for file_path in excel_files:
        if file_path.name.startswith("~$"):
            continue
            
        print(f"Processing {file_path}...")
        try:
            df = pd.read_excel(file_path)
            
            cols_to_drop = [
                c for c in df.columns 
                if c.startswith("processing.") or c.startswith("family.members") or c in ["administrative.areaTypeSource", "administrative.areaTypeConfidence"]
            ]
            
            if cols_to_drop:
                df.drop(columns=cols_to_drop, inplace=True, errors="ignore")
                df.to_excel(file_path, index=False)
                print(f" -> Dropped {len(cols_to_drop)} columns.")
                count += 1
            else:
                print(" -> No columns to drop.")
        except Exception as e:
            print(f" -> Error reading {file_path}: {e}")
            
    print(f"Finished cleaning. Updated {count} files.")

if __name__ == "__main__":
    clean_excel_files()
