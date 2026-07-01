with open('artifacts/quest_ans.md', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.split('\n')
for i, line in enumerate(lines):
    if '40.' in line or 'tỷ trọng cơ cấu' in line.lower() or 'thiếu hụt nguồn nước' in line.lower():
        print(f"Line {i+1}:")
        for j in range(max(0, i-2), min(len(lines), i+25)):
            print(lines[j])
        break
