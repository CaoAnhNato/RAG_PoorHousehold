import os
import glob
import json
import pandas as pd

def build_dimensions():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Processed'))
    metadata_dir = os.path.join(base_dir, 'metadata')
    
    # Read one sample file to get cardinality
    household_files = glob.glob(os.path.join(base_dir, '*', '*.xlsx'))
    member_files = glob.glob(os.path.join(base_dir, '*', '_members', '*.xlsx'))
    
    dimensions = {}
    
    if household_files:
        df_hh = pd.read_excel(household_files[0])
        for col in df_hh.columns:
            cardinality = df_hh[col].nunique(dropna=False)
            col_type = "dimension" if cardinality <= 100 else "identifier"
            dimensions[col] = {
                "cardinality": int(cardinality),
                "type": col_type,
                "table": "fact_household"
            }
            
    if member_files:
        df_mem = pd.read_excel(member_files[0])
        for col in df_mem.columns:
            if col not in dimensions:
                cardinality = df_mem[col].nunique(dropna=False)
                col_type = "dimension" if cardinality <= 100 else "identifier"
                dimensions[col] = {
                    "cardinality": int(cardinality),
                    "type": col_type,
                    "table": "fact_member"
                }

    out_path = os.path.join(metadata_dir, 'dimensions.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(dimensions, f, ensure_ascii=False, indent=2)
        
    try:
        print(f"Dimensions generated: {len(dimensions)} attributes categorized.")
    except:
        pass

if __name__ == '__main__':
    build_dimensions()
