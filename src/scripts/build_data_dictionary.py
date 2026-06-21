import os
import glob
import pandas as pd
import json

def get_dtype_str(dtype):
    if pd.api.types.is_bool_dtype(dtype) or pd.api.types.is_object_dtype(dtype):
        # We can check the first non-null value if it's object, but let's map standard ones
        if dtype.name == 'object':
            return 'string'
        elif dtype.name == 'bool':
            return 'boolean'
    if pd.api.types.is_integer_dtype(dtype):
        return 'integer'
    if pd.api.types.is_float_dtype(dtype):
        return 'float'
    return str(dtype)

def build_data_dictionary():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Processed'))
    metadata_dir = os.path.join(base_dir, 'metadata')
    
    # Load existing descriptions if possible
    existing_dict_path = os.path.join(metadata_dir, 'data_dictionary.json')
    descriptions = {}
    if os.path.exists(existing_dict_path):
        with open(existing_dict_path, 'r', encoding='utf-8') as f:
            old_dict = json.load(f)
            for k, v in old_dict.items():
                if 'description' in v:
                    descriptions[k] = v['description']
                    
    data_dictionary = {}
    
    # 1. Household columns
    household_files = glob.glob(os.path.join(base_dir, '*', '*.xlsx'))
    if household_files:
        df_hh = pd.read_excel(household_files[0], nrows=100)
        for col in df_hh.columns:
            data_dictionary[col] = {
                "table": "fact_household",
                "dtype": get_dtype_str(df_hh[col].dtype),
                "description": descriptions.get(col, col)
            }
            
    # 2. Member columns
    member_files = glob.glob(os.path.join(base_dir, '*', '_members', '*.xlsx'))
    if member_files:
        df_mem = pd.read_excel(member_files[0], nrows=100)
        for col in df_mem.columns:
            # If member column is also in household (like year, district, family.code), we might want to keep it or mark it.
            # Usually we just map it to fact_member if it's specifically a member column.
            if col not in data_dictionary:
                data_dictionary[col] = {
                    "table": "fact_member",
                    "dtype": get_dtype_str(df_mem[col].dtype),
                    "description": descriptions.get(col, col)
                }
            else:
                # it exists in household as well (e.g. keys)
                pass

    os.makedirs(metadata_dir, exist_ok=True)
    with open(existing_dict_path, 'w', encoding='utf-8') as f:
        json.dump(data_dictionary, f, ensure_ascii=False, indent=2)
        
    print(f"Data dictionary built with {len(data_dictionary)} columns and saved to {existing_dict_path}")

if __name__ == '__main__':
    build_data_dictionary()
