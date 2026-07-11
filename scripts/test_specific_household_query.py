import sys
sys.stdout.reconfigure(encoding='utf-8')
from src.query_control.agentic.agent_pipeline import AgenticPipeline
import time

prompts = [
    "hộ phùng thị ánh huyện cư jut có điểm b1 bao nhiêu ?",
    "ai là chủ hộ có mã hộ là 1001 và phân loại nghèo là gì ?",
    "liệt kê danh sách 5 hộ nghèo ở xã Quảng Hòa thuộc huyện Đắk Glong kèm tên chủ hộ và điểm b1"
]

pipeline = AgenticPipeline()
for p in prompts:
    print(f"\n--- Testing: {p} ---")
    t0 = time.time()
    res = pipeline.process(p, mode="Hỏi - Đáp", stream=False)
    t1 = time.time()
    print(f"Time: {t1-t0:.2f}s")
    print("SQL:\n", res.get('sql'))
    print("Error:", res.get('error'))
    df = res.get('data')
    if df is not None:
        print("Result DF:\n", df.head(5))
    else:
        print("Result DF: None")
