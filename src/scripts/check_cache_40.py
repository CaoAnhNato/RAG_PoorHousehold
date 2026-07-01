import hashlib, re, json

q_list = [
    'Tôi tò mò không biết ở Đắk Mil năm 2024, nguyên nhân các hộ bị rơi vào diện nghèo chủ yếu là do thiếu vốn hay thiếu đất sản xuất? Cho tôi xem biểu đồ so sánh hai nguyên nhân này.',
    'Hãy gom nhóm và so sánh chi tiết số lượng hộ nghèo và cận nghèo của từng phường/xã thuộc Thành phố Gia Nghĩa trong năm 2024 trên một biểu đồ nhé.',
    'Đưa lên biểu đồ giúp tôi top 5 huyện có tổng số hộ nghèo và cận nghèo cao nhất toàn tỉnh Đắk Nông năm 2024 để tôi ưu tiên phân bổ ngân sách hỗ trợ.',
    'Thống kê và trình bày dưới dạng biểu đồ thanh ngang toàn bộ các xã ở huyện Tuy Đức theo số lượng hộ cận nghèo năm 2024 để tôi xem xã nào đang gánh nặng nhất.',
    'Cho tôi xem tỷ trọng cơ cấu các hộ nghèo bị thiếu hụt nguồn nước sinh hoạt hợp vệ sinh so với tổng số hộ nghèo trên địa bàn huyện Đắk Song năm 2024.'
]

data = json.load(open('data/Processed/cache/semantic_sql_cache.json', encoding='utf-8'))
out = {}
for idx, q in enumerate(q_list, 36):
    h = hashlib.md5(re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', '', q.lower().strip())).strip().encode('utf-8')).hexdigest()
    out[f"q{idx}_hash"] = h
    out[f"q{idx}_in_cache"] = h in data
    if h in data:
        out[f"q{idx}_sql"] = data[h].get("sql")

with open('src/scripts/out_check.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
