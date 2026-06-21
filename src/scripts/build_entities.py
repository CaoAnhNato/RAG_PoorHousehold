import os
import json

def build_entities():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Processed'))
    metadata_dir = os.path.join(base_dir, 'metadata')
    dict_path = os.path.join(metadata_dir, 'data_dictionary.json')
    
    with open(dict_path, 'r', encoding='utf-8') as f:
        data_dict = json.load(f)
        
    entities = {}
    
    # Define some initial manual mapping for important entities
    manual_entities = {
        "healthInsurance": {
            "physical_column": "deprivation.healthInsurance",
            "source_table": "fact_household",
            "aliases": ["bhyt", "bảo hiểm y tế", "thẻ bhyt"]
        },
        "cleanWater": {
            "physical_column": "deprivation.cleanWater",
            "source_table": "fact_household",
            "aliases": ["nước sạch", "nguồn nước sinh hoạt", "nước sinh hoạt"]
        },
        "hygienicToilet": {
            "physical_column": "deprivation.hygienicToilet",
            "source_table": "fact_household",
            "aliases": ["hố xí", "nhà tiêu hợp vệ sinh", "nhà vệ sinh"]
        },
        "nutrition": {
            "physical_column": "deprivation.nutrition",
            "source_table": "fact_household",
            "aliases": ["dinh dưỡng", "thiếu dinh dưỡng"]
        },
        "housingQuality": {
            "physical_column": "deprivation.housingQuality",
            "source_table": "fact_household",
            "aliases": ["chất lượng nhà ở", "nhà tạm", "nhà dột nát"]
        },
        "housingArea": {
            "physical_column": "deprivation.housingArea",
            "source_table": "fact_household",
            "aliases": ["diện tích nhà ở", "diện tích chật hẹp"]
        },
        "adultEducation": {
            "physical_column": "deprivation.adultEducation",
            "source_table": "fact_household",
            "aliases": ["giáo dục người lớn", "trình độ học vấn người lớn"]
        },
        "childSchoolAttendance": {
            "physical_column": "deprivation.childSchoolAttendance",
            "source_table": "fact_household",
            "aliases": ["trẻ em đi học", "tình trạng đi học của trẻ em"]
        },
        "employment": {
            "physical_column": "deprivation.employment",
            "source_table": "fact_household",
            "aliases": ["việc làm"]
        },
        "dependentPerson": {
            "physical_column": "deprivation.dependentPerson",
            "source_table": "fact_household",
            "aliases": ["người phụ thuộc"]
        },
        "telecommunication": {
            "physical_column": "deprivation.telecommunication",
            "source_table": "fact_household",
            "aliases": ["dịch vụ viễn thông", "điện thoại", "internet"]
        },
        "informationAccessAssets": {
            "physical_column": "deprivation.informationAccessAssets",
            "source_table": "fact_household",
            "aliases": ["tài sản tiếp cận thông tin", "tivi", "radio", "máy tính"]
        },
        # Lý do nghèo
        "lackProductionLand": {
            "physical_column": "reason.lackProductionLand",
            "source_table": "fact_household",
            "aliases": ["đất sản xuất", "thiếu đất"]
        },
        "lackCapital": {
            "physical_column": "reason.lackCapital",
            "source_table": "fact_household",
            "aliases": ["vốn", "thiếu vốn", "không có vốn"]
        },
        "lackLabor": {
            "physical_column": "reason.lackLabor",
            "source_table": "fact_household",
            "aliases": ["lao động", "thiếu lao động"]
        },
        "lackProductionTools": {
            "physical_column": "reason.lackProductionTools",
            "source_table": "fact_household",
            "aliases": ["công cụ sản xuất", "thiếu phương tiện sản xuất"]
        },
        "lackProductionKnowledge": {
            "physical_column": "reason.lackProductionKnowledge",
            "source_table": "fact_household",
            "aliases": ["kiến thức sản xuất", "thiếu kiến thức"]
        },
        "lackLaborSkill": {
            "physical_column": "reason.lackLaborSkill",
            "source_table": "fact_household",
            "aliases": ["kỹ năng lao động", "tay nghề"]
        },
        "illnessOrAccident": {
            "physical_column": "reason.illnessOrAccident",
            "source_table": "fact_household",
            "aliases": ["ốm đau", "tai nạn", "bệnh tật", "mắc bệnh"]
        },
        # Phân loại
        "isDTTS": {
            "physical_column": "family.isDTTS",
            "source_table": "fact_household",
            "aliases": ["dtts", "dân tộc thiểu số"]
        },
        "isDTTC": {
            "physical_column": "family.isDTTC",
            "source_table": "fact_household",
            "aliases": ["dân tộc tại chỗ", "dttc"]
        },
        "hasNoLaborCapacity": {
            "physical_column": "family.hasNoLaborCapacity",
            "source_table": "fact_household",
            "aliases": ["không có khả năng lao động", "mất sức lao động"]
        },
        "hasRevolutionMeritPolicy": {
            "physical_column": "family.hasRevolutionMeritPolicy",
            "source_table": "fact_household",
            "aliases": ["người có công", "chính sách có công"]
        },
        "classify": {
            "physical_column": "classify",
            "source_table": "fact_household",
            "aliases": ["hộ nghèo", "hộ cận nghèo", "phân loại hộ"]
        },
        "district": {
            "physical_column": "administrative.district",
            "source_table": "fact_household",
            "aliases": ["huyện", "thành phố", "địa bàn"]
        },
        "commune": {
            "physical_column": "administrative.commune",
            "source_table": "fact_household",
            "aliases": ["xã", "phường", "thị trấn"]
        },
        "year": {
            "physical_column": "administrative.year",
            "source_table": "fact_household",
            "aliases": ["năm", "thời gian"]
        }
    }
    
    # Auto-generate remaining entities from data_dictionary
    for col, info in data_dict.items():
        # Keep physical column short name
        entity_key = col.split('.')[-1]
        if entity_key not in manual_entities:
            manual_entities[entity_key] = {
                "physical_column": col,
                "source_table": info["table"],
                "aliases": [entity_key, info.get("description", "").lower()]
            }
            
    out_path = os.path.join(metadata_dir, 'entities.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(manual_entities, f, ensure_ascii=False, indent=2)
        
    print(f"Entities generated: {len(manual_entities)} entities saved to {out_path}")

if __name__ == '__main__':
    build_entities()
