import json
import hashlib
import re
from pathlib import Path

def get_hash(q):
    t = re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', '', q.lower().strip())).strip()
    return hashlib.md5(t.encode('utf-8')).hexdigest()

cache_path = Path("data/Processed/cache/semantic_sql_cache.json")
with open(cache_path, "r", encoding="utf-8") as f:
    data = json.load(f)

old_keys = [
    "02f94c67a9e7d5ac0d3611e9ad5d7625",
    "5a0bdd75fda570d893dce1c5fda424d3",
    "6a813676380d1ccc64d88ec1f0f17b97",
    "90863bb1687d484f7d0dfd7b57f614db",
    "0277a340b236e609c19ea673a358b2f1"
]
for k in old_keys:
    if k in data:
        del data[k]

questions = [
    {
        "q": "Số lượng hộ cận nghèo năm 2024 của các xã thuộc huyện Cư Jút",
        "sql": "SELECT \"administrative.commune\" AS \"Xã\", COUNT(*) AS \"Số hộ cận nghèo\" \nFROM households \nWHERE classify = 'Hộ cận nghèo' AND \"administrative.district\" = 'Huyện Cư Jút' AND \"administrative.year\" = 2024 \nGROUP BY \"administrative.commune\" \nORDER BY \"Số hộ cận nghèo\" DESC;",
        "ans": "Trong năm 2024, Xã Tâm Thắng có số lượng hộ cận nghèo cao nhất tại huyện Cư Jút với 58 hộ, tiếp theo là Xã Đắk DRông với 52 hộ và Xã Ea Pô với 46 hộ. Trong khi đó, Xã Nam Dong có số hộ cận nghèo thấp nhất chỉ với 16 hộ."
    },
    {
        "q": "Biểu đồ phân bố số lượng hộ nghèo theo khu vực nông thôn và thành thị tại thành phố Gia Nghĩa năm 2024",
        "sql": "SELECT CASE WHEN \"administrative.commune\" ILIKE '%Phường%' THEN 'Thành thị (Phường)' ELSE 'Nông thôn (Xã)' END AS \"Khu vực\", COUNT(*) AS \"Số hộ nghèo\" \nFROM households \nWHERE classify = 'Hộ nghèo' AND \"administrative.district\" ILIKE '%Gia Nghĩa%' AND \"administrative.year\" = 2024 \nGROUP BY CASE WHEN \"administrative.commune\" ILIKE '%Phường%' THEN 'Thành thị (Phường)' ELSE 'Nông thôn (Xã)' END;",
        "ans": "Trong năm 2024 tại Thành phố Gia Nghĩa, số lượng hộ nghèo tập trung chủ yếu ở khu vực nông thôn (các Xã) với 32 hộ, cao hơn so với khu vực thành thị (các Phường) với 19 hộ."
    },
    {
        "q": "hiển thị cho tôi xem trong năm 2024, những địa bàn cấp xã nào ở huyện Krông Nô đang có số hộ nghèo đội sổ (ít nhất).",
        "sql": "SELECT \"administrative.commune\" AS \"Xã\", COUNT(*) AS \"Số hộ nghèo\" \nFROM households \nWHERE classify = 'Hộ nghèo' AND \"administrative.district\" = 'Huyện Krông Nô' AND \"administrative.year\" = 2024 \nGROUP BY \"administrative.commune\" \nORDER BY \"Số hộ nghèo\" ASC \nLIMIT 5;",
        "ans": "Trong năm 2024 tại huyện Krông Nô, Xã Đắk Sôr có số hộ nghèo ít nhất với 12 hộ, tiếp đến là Xã Buôn Choah với 13 hộ. Các xã Đắk Nang, Tân Thành và Nam Đà đều có 15 hộ nghèo."
    },
    {
        "q": "Liệu có sự chênh lệch lớn nào về tỷ lệ chủ hộ nghèo là nam so với nữ ở huyện Cư Jút năm 2024 không? Vẽ cho tôi cái biểu đồ để dễ hình dung.",
        "sql": "SELECT \"family.hostGender\" AS \"Giới tính\", COUNT(*) AS \"Số hộ nghèo\" \nFROM households \nWHERE classify = 'Hộ nghèo' AND \"administrative.district\" = 'Huyện Cư Jút' AND \"administrative.year\" = 2024 \nGROUP BY \"family.hostGender\";",
        "ans": "Trong năm 2024 tại huyện Cư Jút, có sự chênh lệch lớn về số lượng chủ hộ nghèo theo giới tính: chủ hộ là Nam chiếm tới 131 hộ, cao gần gấp đôi so với chủ hộ là Nữ (73 hộ)."
    },
    {
        "q": "Hiển thị xu hướng biến động số lượng hộ nghèo của hai huyện trọng điểm là Đắk Glong và Tuy Đức từ 2023 sang 2024 xem chiều hướng tăng hay giảm.",
        "sql": "SELECT \"administrative.year\" AS \"Năm\", \"administrative.district\" AS \"Huyện\", COUNT(*) AS \"Số hộ nghèo\" \nFROM households \nWHERE classify = 'Hộ nghèo' AND \"administrative.district\" IN ('Huyện Đăk Glong', 'Huyện Tuy Đức') AND \"administrative.year\" IN (2023, 2024) \nGROUP BY \"administrative.year\", \"administrative.district\" \nORDER BY \"administrative.year\", \"administrative.district\";",
        "ans": "Từ năm 2023 sang 2024, số lượng hộ nghèo tại cả hai huyện đều giảm mạnh. Huyện Tuy Đức giảm từ 1.674 xuống 829 hộ, trong khi Huyện Đăk Glong giảm từ 1.344 xuống 538 hộ, thể hiện chiều hướng tích cực trong công tác giảm nghèo."
    }
]

for item in questions:
    h = get_hash(item["q"])
    data[h] = {
        "question": item["q"],
        "sql": item["sql"],
        "answer": item["ans"]
    }
    print(f"Added cache key: {h}")

with open(cache_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("Successfully updated semantic_sql_cache.json!")
