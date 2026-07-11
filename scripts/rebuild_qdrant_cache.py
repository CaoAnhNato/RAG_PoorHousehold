import json
import sys
import uuid
sys.stdout.reconfigure(encoding='utf-8')

from src.query_control.agentic.semantic_cache import cache_manager

print("Initializing Qdrant...", flush=True)
cache_manager._init_qdrant()

if cache_manager.qclient is not None:
    print(f"Deleting existing Qdrant collection: {cache_manager.collection_name}", flush=True)
    try:
        cache_manager.qclient.delete_collection(cache_manager.collection_name)
    except Exception as e:
        print(f"Delete collection note: {e}", flush=True)
    
    # Re-init will create collection
    cache_manager.initialized_qdrant = False
    cache_manager._init_qdrant()
    
    print("Loading clean entries from local cache...", flush=True)
    with open('data/Processed/cache/semantic_sql_cache.json', 'r', encoding='utf-8') as f:
        clean_cache = json.load(f)
        
    print(f"Re-populating Qdrant with {len(clean_cache)} clean entries...", flush=True)
    count = 0
    for key, cache_data in clean_cache.items():
        q = cache_data.get("question", "")
        if not q:
            continue
        ans_str = str(cache_data.get("answer", ""))
        sql_str = str(cache_data.get("sql", "")).strip()
        bad_phrases = [
            "Tôi không tìm thấy dữ liệu", "Lỗi khi", "Hệ thống gặp lỗi", 
            "không có khả năng lao động đạt 100", "chưa có thông tin", "không thể xác định"
        ]
        if not sql_str or "SELECT" not in sql_str.upper() or any(p in ans_str for p in bad_phrases):
            continue
            
        vector = cache_manager.emb_client.embed_text(q)
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"cache_{key}"))
        cache_manager.qclient.upsert(
            collection_name=cache_manager.collection_name,
            points=[{
                "id": point_id,
                "vector": vector,
                "payload": cache_data
            }]
        )
        count += 1
        if count % 10 == 0:
            print(f"Upserted {count}/{len(clean_cache)} points...", flush=True)
            
    print(f"Successfully rebuilt Qdrant cache with {count} clean entries!", flush=True)
else:
    print("Qdrant client not available.", flush=True)
