import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
from src.query_control.agentic.semantic_cache import cache_manager

with open('test/debug/100_qa_benchmark_results.json', 'r', encoding='utf-8') as f:
    results_data = json.load(f)

failed_questions = set()
for item in results_data.get('detailed_results', []):
    if not item.get('passed'):
        failed_questions.add(item.get('prompt', '').strip())

print(f"Found {len(failed_questions)} failed questions in benchmark results.")

# Delete from local cache
removed_count = 0
keys_to_remove = []
for key, val in cache_manager.local_cache.items():
    q = val.get('question', '').strip()
    if q in failed_questions:
        keys_to_remove.append(key)

for k in keys_to_remove:
    del cache_manager.local_cache[k]
    removed_count += 1

cache_manager._save_local_cache()
print(f"Removed {removed_count} failed entries from local cache.")

# Delete Qdrant collection so it rebuilds cleanly
cache_manager._init_qdrant()
if cache_manager.qclient:
    try:
        cache_manager.qclient.delete_collection(cache_manager.collection_name)
        print("Deleted Qdrant collection.")
    except Exception as e:
        print(f"Qdrant delete note: {e}")
