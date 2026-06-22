import duckdb
import json
import re

file_path = 'artifacts/quest_ans.md'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content_blocks = content.split('---')

q_num = 1
for i, block in enumerate(content_blocks):
    if re.search(rf"^## {q_num}\. ", block.strip(), flags=re.MULTILINE):
        print("Found block for Q1!")
        old_block = block
        block = re.sub(r"(### Dữ liệu trả về từ DB)\n```json\n.*?\n```", r"\1\n```json\nTEST_JSON\n```", block, flags=re.DOTALL)
        if block != old_block:
            print("Successfully replaced JSON!")
        else:
            print("Failed to replace JSON. Let's see the match:")
            m = re.search(r"(### Dữ liệu trả về từ DB)\n```json\n.*?\n```", old_block, flags=re.DOTALL)
            print("Match found:", bool(m))
            if m:
                print("Matched text:", repr(m.group(0)))
            else:
                print("No match found for pattern in block.")
