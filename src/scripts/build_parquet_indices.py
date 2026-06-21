import os
import glob
import pandas as pd
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

def build_indices():
    processed_dir = "Processed"
    
    # Required columns
    household_cols = [
        'administrative.year', 
        'administrative.district', 
        'administrative.commune', 
        'administrative.village_or_group', 
        'family.code', 
        'family.hostName', 
        'classify.final', 
        'family.numberOfMembers'
    ]
    
    member_cols = [
        'administrative.year', 
        'administrative.district', 
        'family.code', 
        'member.fullName', 
        'member.relationshipToHost', 
        'member.isChild'
    ]
    
    # Find all excel files
    all_files = glob.glob(os.path.join(processed_dir, "**", "*.xlsx"), recursive=True)
    
    household_dfs = []
    member_dfs = []
    
    for f in all_files:
        # Ignore metadata or logs
        if "metadata" in f or "logs" in f:
            continue
            
        print(f"Reading {f}")
        try:
            df = pd.read_excel(f)
            
            # Identify if this is a member file or household file
            if "_members" in f:
                # Member file
                # Check if required columns exist
                missing = [c for c in member_cols if c not in df.columns]
                if not missing:
                    member_dfs.append(df[member_cols])
                else:
                    print(f"  -> Missing columns in member file: {missing}")
            else:
                # Household file
                missing = [c for c in household_cols if c not in df.columns]
                if not missing:
                    household_dfs.append(df[household_cols])
                else:
                    print(f"  -> Missing columns in household file: {missing}")
        except Exception as e:
            print(f"  -> Error reading {f}: {e}")
            
    # Concatenate and save to parquet
    os.makedirs(os.path.join(processed_dir, "metadata"), exist_ok=True)
    
    if household_dfs:
        household_index = pd.concat(household_dfs, ignore_index=True)
        # Drop duplicates based on primary key
        household_index = household_index.drop_duplicates(subset=['administrative.year', 'administrative.district', 'family.code'])
        out_path = os.path.join(processed_dir, "metadata", "household_index.parquet")
        household_index.to_parquet(out_path, index=False)
        print(f"Saved household_index.parquet with {len(household_index)} records")
        
    if member_dfs:
        member_index = pd.concat(member_dfs, ignore_index=True)
        # Drop duplicates based on primary key
        member_index = member_index.drop_duplicates(subset=['administrative.year', 'administrative.district', 'family.code', 'member.fullName'])
        out_path = os.path.join(processed_dir, "metadata", "member_index.parquet")
        member_index.to_parquet(out_path, index=False)
        print(f"Saved member_index.parquet with {len(member_index)} records")

if __name__ == "__main__":
    build_indices()
