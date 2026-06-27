# -*- coding: utf-8 -*-
"""
Module xây dựng Chỉ mục tìm kiếm ngữ nghĩa Qdrant (Qdrant Semantic Index).
Trích xuất định nghĩa các chỉ số (metrics), chiều dữ liệu (dimensions), thuật ngữ nghiệp vụ (business terms)
và các câu hỏi mẫu để sinh embedding, lưu trữ vào Qdrant Vector DB.
"""

from __future__ import annotations
import os
import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import json
import uuid
import argparse
from pathlib import Path
import datetime as dt
import requests
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from qdrant_client.http.exceptions import UnexpectedResponse

PROJECT_ROOT = Path(__file__).resolve().parents[2]
# Load file .env trước khi chạy từ thư mục gốc của project
dotenv_path = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=dotenv_path)

PROCESSED_DIR = PROJECT_ROOT / "data" / "Processed"
METADATA_DIR = PROCESSED_DIR / "metadata"
QUERY_CONTROL_METADATA_DIR = METADATA_DIR / "query_control"
SEMANTIC_LAYER_PATH = QUERY_CONTROL_METADATA_DIR / "semantic_layer.json"
QDRANT_CONFIG_PATH = QUERY_CONTROL_METADATA_DIR / "qdrant_index_config.json"
REPORT_PATH = QUERY_CONTROL_METADATA_DIR / "metadata_build_report.md"

class EmbeddingClient:
    """Client sinh Vector Embedding, hỗ trợ cả API (như ShopAPI) và SentenceTransformers cục bộ."""
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.shopapi_api_key = os.environ.get("SHOPAPI_LLM_API_KEY", "").strip()
        self.shopapi_base_url = os.environ.get("SHOPAPI_BASE_URL", "").strip()
        
        self.use_shopapi = False
        # Nếu cấu hình ShopAPI đầy đủ và model không phải local, sử dụng API
        if self.shopapi_api_key and self.shopapi_base_url:
            if "text-embedding" in model_name or ("intfloat" not in model_name and "BAAI" not in model_name):
                self.use_shopapi = True
                
        self.local_model = None
        if not self.use_shopapi:
            print(f"Khởi tạo mô hình local SentenceTransformer: {model_name}...")
            try:
                from sentence_transformers import SentenceTransformer
                self.local_model = SentenceTransformer(model_name)
            except ImportError:
                print("Lỗi: Không tìm thấy thư viện sentence-transformers. Vui lòng cài đặt qua requirements.txt.")
                sys.exit(1)
                
    def get_dimension(self) -> int:
        """Lấy kích thước vector embedding động từ mô hình."""
        if self.use_shopapi:
            try:
                # Gửi thử một từ để lấy kích thước vector trả về
                test_emb = self.embed_text("test")
                return len(test_emb)
            except Exception as e:
                print(f"Lỗi: Không thể gọi API Embedding để lấy kích thước vector. Chi tiết: {e}")
                print("Vui lòng kiểm tra lại SHOPAPI_LLM_API_KEY và SHOPAPI_BASE_URL trong tệp .env.")
                sys.exit(1)
        else:
            return self.local_model.get_sentence_embedding_dimension()
            
    def embed_text(self, text: str) -> list[float]:
        return self.embed_batch([text])[0]
        
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        if self.use_shopapi:
            base = self.shopapi_base_url.rstrip("/")
            url = f"{base}/embeddings" if base.endswith("/v1") else f"{base}/v1/embeddings"
            headers = {
                "Authorization": f"Bearer {self.shopapi_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model_name,
                "input": texts,
                "encoding_format": "float"
            }
            try:
                resp = requests.post(url, json=payload, headers=headers, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                # Định dạng chuẩn OpenAI: data['data'] = [{'embedding': [...]}, ...]
                return [item["embedding"] for item in data["data"]]
            except Exception as e:
                print(f"Lỗi khi gọi API Embedding: {e}")
                sys.exit(1)
        else:
            embeddings = self.local_model.encode(texts, show_progress_bar=False)
            return embeddings.tolist()

def load_qdrant_config() -> dict[str, Any]:
    if not QDRANT_CONFIG_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy file cấu hình Qdrant tại {QDRANT_CONFIG_PATH}")
    with open(QDRANT_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_semantic_layer() -> dict[str, Any]:
    if not SEMANTIC_LAYER_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy Semantic Layer tại {SEMANTIC_LAYER_PATH}. Vui lòng chạy build_semantic_layer.py trước.")
    with open(SEMANTIC_LAYER_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def build_documents(semantic_layer: dict[str, Any]) -> list[dict[str, Any]]:
    """Xây dựng nội dung văn bản (text) giàu ngữ nghĩa và payload tương ứng cho từng đối tượng."""
    documents = []
    
    # 1. Metric definitions
    for m_id, m in semantic_layer.get("metrics", {}).items():
        examples_str = "; ".join(m.get("query_examples", []))
        filters_str = json.dumps(m.get("filters", []), ensure_ascii=False)
        text = (
            f"Metric: {m_id}\n"
            f"Tên tiếng Việt: {m.get('name_vi', '')}\n"
            f"Định nghĩa: {m.get('definition', '')}\n"
            f"Công thức: {m.get('expression', '')}\n"
            f"Filter nghiệp vụ: {filters_str}\n"
            f"Có thể hỏi: {examples_str}"
        )
        payload = {
            "doc_type": "metric_definition",
            "semantic_id": m_id,
            "name_vi": m.get("name_vi"),
            "definition": m.get("definition"),
            "status": m.get("status"),
            "base_table": m.get("base_table"),
            "target_metric": m_id,
            "maps_to": {
                "metric": m_id
            },
            "source": "semantic_layer.json"
        }
        documents.append({
            "semantic_id": m_id,
            "doc_type": "metric_definition",
            "text": text,
            "payload": payload
        })
        
    # 2. Dimension definitions
    for d_id, d in semantic_layer.get("dimensions", {}).items():
        examples_str = "; ".join(d.get("query_examples", []))
        text = (
            f"Dimension: {d_id}\n"
            f"Tên tiếng Việt: {d.get('name_vi', '')}\n"
            f"Định nghĩa: {d.get('definition', '')}\n"
            f"Có thể hỏi: {examples_str}"
        )
        payload = {
            "doc_type": "dimension_definition",
            "semantic_id": d_id,
            "name_vi": d.get("name_vi"),
            "definition": d.get("definition"),
            "status": d.get("status"),
            "base_table": d.get("base_table"),
            "target_dimension": d_id,
            "maps_to": {
                "dimension": d_id
            },
            "source": "semantic_layer.json"
        }
        documents.append({
            "semantic_id": d_id,
            "doc_type": "dimension_definition",
            "text": text,
            "payload": payload
        })
        
    # 3. Business terms
    for term, b in semantic_layer.get("business_terms", {}).items():
        text = (
            f"Business term: {term}\n"
            f"Định nghĩa: {b.get('definition', '')}\n"
            f"Map tới metric: {b.get('maps_to', {}).get('metric', 'none')}\n"
            f"Map tới dimension: {b.get('maps_to', {}).get('dimension', 'none')}\n"
            f"Filter value: {b.get('maps_to', {}).get('filter_value', 'none')}"
        )
        payload = {
            "doc_type": "business_term",
            "semantic_id": term,
            "name_vi": term,
            "definition": b.get("definition"),
            "status": "ready",
            "maps_to": b.get("maps_to"),
            "source": "semantic_layer.json"
        }
        documents.append({
            "semantic_id": term,
            "doc_type": "business_term",
            "text": text,
            "payload": payload
        })
        
    # 4. Query examples
    for qe in semantic_layer.get("query_examples", []):
        maps = qe.get("maps_to", {})
        text = (
            f"Query example: {qe.get('text')}\n"
            f"Map tới task_type: {maps.get('task_type')}\n"
            f"Metric: {', '.join(maps.get('metrics', []))}\n"
            f"Dimension: {', '.join(maps.get('dimensions', []))}"
        )
        payload = {
            "doc_type": "query_example",
            "semantic_id": qe.get("example_id"),
            "name_vi": qe.get("text"),
            "definition": f"Ví dụ truy vấn: {qe.get('text')}",
            "status": "ready",
            "maps_to": maps,
            "source": "semantic_layer.json"
        }
        documents.append({
            "semantic_id": qe.get("example_id"),
            "doc_type": "query_example",
            "text": text,
            "payload": payload
        })
        
    return documents

def main() -> None:
    parser = argparse.ArgumentParser(description="Xây dựng chỉ mục tìm kiếm ngữ nghĩa Qdrant.")
    parser.add_argument("--recreate", action="store_true", help="Xoá và tạo lại collection Qdrant.")
    args = parser.parse_args()
    
    # 1. Tải cấu hình Qdrant
    qdrant_config = load_qdrant_config()
    
    # Đọc model cấu hình từ biến môi trường nếu có, nếu không lấy từ file config hoặc .env
    embedding_model = os.environ.get("EMBEDDING_MODEL")
    if not embedding_model:
        embedding_model = os.environ.get("SHOPAPI_EMBEDDING", qdrant_config.get("embedding_model"))
        
    qdrant_url = qdrant_config.get("qdrant_url", "http://localhost:6333")
    collection_name = qdrant_config.get("collection_name", "query_control_semantic")
    
    print(f"Kết nối Qdrant tại: {qdrant_url}")
    try:
        qclient = QdrantClient(url=qdrant_url, timeout=5.0)
        # Kiểm tra kết nối nhanh bằng cách lấy danh sách collections
        qclient.get_collections()
    except Exception as e:
        print(f"Lỗi: Không thể kết nối tới Qdrant Vector Database tại {qdrant_url}.")
        print("Sự cố có thể do container Qdrant chưa được khởi động. Vui lòng chạy lệnh:")
        print("  docker compose up -d qdrant")
        print("Chi tiết lỗi kết nối:")
        print(f"  {e}")
        # Dừng và yêu cầu người dùng xử lý (Quy tắc 6)
        sys.exit(1)
        
    # 2. Khởi tạo client embedding
    print(f"Khởi tạo Embedding model: {embedding_model}")
    emb_client = EmbeddingClient(embedding_model)
    vector_size = emb_client.get_dimension()
    print(f"Kích thước vector của mô hình: {vector_size}")
    
    # 3. Kiểm tra collection hiện tại
    collection_exists = False
    try:
        col_info = qclient.get_collection(collection_name)
        collection_exists = True
        existing_size = col_info.config.params.vectors.size
        print(f"Tìm thấy collection '{collection_name}' hiện tại với vector size: {existing_size}")
        
        # Nếu vector size khác biệt và không có flag recreate -> báo lỗi và dừng (Rule 6)
        if existing_size != vector_size:
            if not args.recreate:
                print(f"Lỗi: Kích thước vector của collection hiện tại ({existing_size}) khác với kích thước của mô hình embedding hiện tại ({vector_size}).")
                print("Vui lòng thực thi lại script với tham số --recreate để tạo lại collection phù hợp:")
                print(f"  python Intern/src/query_control/build_qdrant_semantic_index.py --recreate")
                sys.exit(1)
    except UnexpectedResponse:
        # Collection chưa tồn tại
        pass
        
    # 4. Xử lý xoá/tạo mới collection
    if args.recreate or not collection_exists:
        if collection_exists:
            print(f"Đang xoá collection '{collection_name}'...")
            qclient.delete_collection(collection_name)
            
        print(f"Đang tạo collection '{collection_name}' với vector size {vector_size}...")
        qclient.create_collection(
            collection_name=collection_name,
            vectors_config=qmodels.VectorParams(
                size=vector_size,
                distance=qmodels.Distance.COSINE
            )
        )
        
        # Tạo index payload cho các cột lọc thường dùng để tăng hiệu suất
        for field in qdrant_config.get("payload_indexes", []):
            print(f"Tạo chỉ mục payload cho: {field}")
            qclient.create_payload_index(
                collection_name=collection_name,
                field_name=field,
                field_schema=qmodels.PayloadSchemaType.KEYWORD
            )
            
    # 5. Đọc Semantic Layer và chuẩn bị documents
    print("Đang đọc Semantic Layer...")
    semantic_layer = load_semantic_layer()
    documents = build_documents(semantic_layer)
    
    print(f"Đã chuẩn bị {len(documents)} đối tượng để đưa vào chỉ mục.")
    
    # 6. Tạo vectors và upsert vào Qdrant
    texts = [doc["text"] for doc in documents]
    print("Đang tạo embedding vectors...")
    vectors = emb_client.embed_batch(texts)
    
    points = []
    for index, doc in enumerate(documents):
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc['doc_type']}_{doc['semantic_id']}"))
        points.append(qmodels.PointStruct(
            id=point_id,
            vector=vectors[index],
            payload=doc["payload"]
        ))
        
    print("Đang upsert points vào Qdrant...")
    qclient.upsert(
        collection_name=collection_name,
        points=points
    )
    print("Hoàn tất việc nạp dữ liệu vào Qdrant.")
    
    # 7. Ghi báo cáo kết quả
    counts = {
        "metric_definition": 0,
        "dimension_definition": 0,
        "business_term": 0,
        "query_example": 0
    }
    for doc in documents:
        counts[doc["doc_type"]] = counts.get(doc["doc_type"], 0) + 1
        
    report_additions = []
    report_additions.append("\n## 4. Kết quả nạp chỉ mục ngữ nghĩa Qdrant")
    report_additions.append(f"- **Địa chỉ Qdrant:** `{qdrant_url}`")
    report_additions.append(f"- **Tên Collection:** `{collection_name}`")
    report_additions.append(f"- **Mô hình Embedding:** `{embedding_model}`")
    report_additions.append(f"- **Kích thước vector:** {vector_size}")
    report_additions.append(f"- **Tổng số điểm đã index:** {len(documents)}")
    report_additions.append(f"  - Số chỉ số (metrics): {counts['metric_definition']}")
    report_additions.append(f"  - Số chiều dữ liệu (dimensions): {counts['dimension_definition']}")
    report_additions.append(f"  - Số thuật ngữ nghiệp vụ (business terms): {counts['business_term']}")
    report_additions.append(f"  - Số câu hỏi mẫu (query examples): {counts['query_example']}")
    report_additions.append(f"- **Collection được tạo lại (recreated):** {args.recreate or not collection_exists}\n")
    
    with open(REPORT_PATH, "a", encoding="utf-8") as f:
        f.write("\n" + "\n".join(report_additions))
    print(f"Đã cập nhật báo cáo metadata tại: {REPORT_PATH}")

if __name__ == "__main__":
    main()
