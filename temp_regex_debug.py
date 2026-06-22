import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

file_path = 'artifacts/quest_ans.md'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content_blocks = content.split('---')

for q_num in [1, 4, 10]:
    for i, block in enumerate(content_blocks):
        if re.search(rf"^## {q_num}\. ", block.strip(), flags=re.MULTILINE):
            # Check if json replacement works
            res_json = f"TEST_JSON_{q_num}"
            new_block = re.sub(r"(### Dữ liệu trả về từ DB\s*```json).*?(```)", rf"\g<1>\n{res_json}\n\g<2>", block, flags=re.DOTALL)
            if new_block != block:
                print(f"Q{q_num}: Regex substitution succeeded.")
            else:
                print(f"Q{q_num}: Regex substitution FAILED.")
                print("Block ending repr:", repr(block[-100:]))
                
                # Let's try to find out what's really there
                m = re.search(r"### Dữ liệu trả về từ DB", block)
                if m:
                    print("Found heading at:", m.start())
                    print("Rest of block:", repr(block[m.start():]))
