import sys
sys.stdout.reconfigure(encoding='utf-8')
from src.query_control.agentic.semantic_cache import cache_manager

print("Connecting to Qdrant...", flush=True)
cache_manager._init_qdrant()
if cache_manager.qclient:
    print(f"Deleting Qdrant collection '{cache_manager.collection_name}'...", flush=True)
    try:
        cache_manager.qclient.delete_collection(cache_manager.collection_name)
        print("Collection deleted successfully! No more poisoned templates in Qdrant.", flush=True)
    except Exception as e:
        print(f"Delete note: {e}", flush=True)
else:
    print("Qdrant not available.", flush=True)
