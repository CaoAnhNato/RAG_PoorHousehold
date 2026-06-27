import sys
from pathlib import Path

# Force UTF-8 encoding
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parents[0]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.query_control.agentic.agent_pipeline import AgenticPipeline

def main():
    print("Khởi tạo Agentic Pipeline...")
    pipeline = AgenticPipeline()
    print("="*50)
    print("🤖 CHATBOT RÀ SOÁT HỘ NGHÈO ĐẮK NÔNG (CLI)")
    print("Nhập 'quit' hoặc 'exit' để thoát.")
    print("="*50)
    
    while True:
        try:
            q = input("\nBạn: ")
            if q.strip().lower() in ['quit', 'exit']:
                break
            if not q.strip():
                continue
                
            res = pipeline.process(q, mode="Auto")
            print("\n🤖 Chatbot:")
            print(f"{res.get('answer', '')}")
            
            if res.get('chart_fig'):
                print(f"[Hệ thống đã tạo biểu đồ: {type(res.get('chart_fig')).__name__}]")
                
            df = res.get('data')
            if df is not None and not df.empty:
                print("\n[Dữ liệu đính kèm]:")
                print(df.to_string())
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\n[LỖI]: {e}")

if __name__ == "__main__":
    main()
