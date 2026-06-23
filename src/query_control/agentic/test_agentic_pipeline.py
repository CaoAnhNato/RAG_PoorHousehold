# -*- coding: utf-8 -*-
import sys
import re
from pathlib import Path

# Force UTF-8 for Windows console
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))

from src.query_control.agentic.agent_pipeline import AgenticPipeline

def extract_qa_pairs():
    file_path = PROJECT_ROOT / "artifacts" / "quest_ans.md"
    qa_pairs = []
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Tách theo block ## \d+\.
    blocks = re.split(r"## \d+\. ", content)
    for block in blocks[1:]:
        lines = block.split('\n')
        question = lines[0].strip()
        
        # Trích xuất expected answer
        expected_ans = ""
        in_answer_block = False
        for line in lines:
            if line.startswith("### Đáp án"):
                in_answer_block = True
            elif line.startswith("### Dữ liệu trả về"):
                in_answer_block = False
            elif in_answer_block:
                if line.startswith(">"):
                    expected_ans += line[1:].strip() + " "
                else:
                    expected_ans += line.strip() + " "
                    
        qa_pairs.append({
            "question": question,
            "expected_ans": expected_ans.strip()
        })
        
    return qa_pairs

def run_tests():
    pipeline = AgenticPipeline()
    qa_pairs = extract_qa_pairs()
    
    import time
    total_time = 0
    times = []
    
    with open("test_results.log", "w", encoding="utf-8") as f:
        for i, qa in enumerate(qa_pairs):
            f.write(f"==============================\n")
            f.write(f"Q{i+1}: {qa['question']}\n")
            
            start_time = time.time()
            res = pipeline.process(qa['question'])
            end_time = time.time()
            
            exec_time = end_time - start_time
            times.append(exec_time)
            total_time += exec_time
            
            f.write(f"Time taken: {exec_time:.2f}s\n")
            f.write(f"Final SQL: {res['sql']}\n")
            if res['data'] is not None:
                f.write(f"Rows returned: {len(res['data'])}\n")
            f.write(f"-> Generated Answer:\n{res['answer']}\n\n")
            f.write(f"-> Expected Answer:\n{qa['expected_ans']}\n\n")
            
        # Thống kê tổng hợp
        f.write("\n" + "=" * 50 + "\n")
        f.write("THỐNG KÊ THỜI GIAN THỰC THI\n")
        f.write("=" * 50 + "\n")
        f.write(f"Tổng số câu hỏi: {len(qa_pairs)}\n")
        f.write(f"Tổng thời gian chạy: {total_time:.2f}s\n")
        f.write(f"Thời gian trung bình: {total_time / len(qa_pairs):.2f}s/câu\n")
        f.write(f"Thời gian chậm nhất: {max(times):.2f}s (Câu {times.index(max(times)) + 1})\n")
        f.write(f"Thời gian nhanh nhất: {min(times):.2f}s (Câu {times.index(min(times)) + 1})\n")
        f.write("=" * 50 + "\n")

if __name__ == "__main__":
    # Disable stdout print inside tests and rely on file
    import builtins
    original_print = builtins.print
    def mock_print(*args, **kwargs):
        pass
    builtins.print = mock_print
    
    run_tests()
    builtins.print = original_print
