import json

file_path = 'data/Processed/metadata/query_control/semantic_layer.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

missing_dims = {
    "employment": {
      "name_vi": "Thiếu hụt việc làm",
      "definition": "Xác định hộ có bị thiếu hụt việc làm không",
      "semantic_type": "boolean",
      "base_table": "households",
      "physical_columns": ["deprivation.employment"],
      "allowed_for_group_by": True,
      "allowed_for_filter": True,
      "query_examples": ["thiếu việc làm", "không có việc làm"],
      "status": "ready"
    },
    "dependent_person": {
      "name_vi": "Thiếu hụt người phụ thuộc",
      "definition": "Xác định hộ có bị thiếu hụt người phụ thuộc không",
      "semantic_type": "boolean",
      "base_table": "households",
      "physical_columns": ["deprivation.dependentPerson"],
      "allowed_for_group_by": True,
      "allowed_for_filter": True,
      "query_examples": ["thiếu hụt người phụ thuộc"],
      "status": "ready"
    },
    "nutrition": {
      "name_vi": "Thiếu hụt dinh dưỡng",
      "definition": "Xác định hộ có bị thiếu hụt dinh dưỡng không",
      "semantic_type": "boolean",
      "base_table": "households",
      "physical_columns": ["deprivation.nutrition"],
      "allowed_for_group_by": True,
      "allowed_for_filter": True,
      "query_examples": ["thiếu dinh dưỡng"],
      "status": "ready"
    },
    "health_insurance": {
      "name_vi": "Thiếu hụt bảo hiểm y tế",
      "definition": "Xác định hộ có bị thiếu hụt bảo hiểm y tế không",
      "semantic_type": "boolean",
      "base_table": "households",
      "physical_columns": ["deprivation.healthInsurance"],
      "allowed_for_group_by": True,
      "allowed_for_filter": True,
      "query_examples": ["thiếu bảo hiểm y tế", "thiếu bhyt"],
      "status": "ready"
    },
    "adult_education": {
      "name_vi": "Thiếu hụt trình độ giáo dục người lớn",
      "definition": "Xác định hộ có bị thiếu hụt trình độ giáo dục của người lớn không",
      "semantic_type": "boolean",
      "base_table": "households",
      "physical_columns": ["deprivation.adultEducation"],
      "allowed_for_group_by": True,
      "allowed_for_filter": True,
      "query_examples": ["thiếu học vấn", "thiếu giáo dục"],
      "status": "ready"
    },
    "child_school_attendance": {
      "name_vi": "Thiếu hụt tình trạng đi học của trẻ em",
      "definition": "Xác định hộ có bị thiếu hụt tình trạng đi học của trẻ em không",
      "semantic_type": "boolean",
      "base_table": "households",
      "physical_columns": ["deprivation.childSchoolAttendance"],
      "allowed_for_group_by": True,
      "allowed_for_filter": True,
      "query_examples": ["trẻ em không đi học", "thiếu đi học"],
      "status": "ready"
    },
    "housing_quality": {
      "name_vi": "Thiếu hụt chất lượng nhà ở",
      "definition": "Xác định hộ có bị thiếu hụt chất lượng nhà ở không",
      "semantic_type": "boolean",
      "base_table": "households",
      "physical_columns": ["deprivation.housingQuality"],
      "allowed_for_group_by": True,
      "allowed_for_filter": True,
      "query_examples": ["chất lượng nhà ở thấp", "nhà tạm"],
      "status": "ready"
    },
    "housing_area": {
      "name_vi": "Thiếu hụt diện tích nhà ở",
      "definition": "Xác định hộ có bị thiếu hụt diện tích nhà ở không",
      "semantic_type": "boolean",
      "base_table": "households",
      "physical_columns": ["deprivation.housingArea"],
      "allowed_for_group_by": True,
      "allowed_for_filter": True,
      "query_examples": ["thiếu diện tích nhà ở", "nhà chật"],
      "status": "ready"
    },
    "telecommunication": {
      "name_vi": "Thiếu hụt dịch vụ viễn thông",
      "definition": "Xác định hộ có bị thiếu hụt dịch vụ viễn thông không",
      "semantic_type": "boolean",
      "base_table": "households",
      "physical_columns": ["deprivation.telecommunication"],
      "allowed_for_group_by": True,
      "allowed_for_filter": True,
      "query_examples": ["thiếu viễn thông", "không có điện thoại"],
      "status": "ready"
    },
    "information_access_assets": {
      "name_vi": "Thiếu hụt tài sản tiếp cận thông tin",
      "definition": "Xác định hộ có bị thiếu hụt tài sản tiếp cận thông tin không",
      "semantic_type": "boolean",
      "base_table": "households",
      "physical_columns": ["deprivation.informationAccessAssets"],
      "allowed_for_group_by": True,
      "allowed_for_filter": True,
      "query_examples": ["thiếu tài sản thông tin", "không có tv"],
      "status": "ready"
    }
}

data['dimensions'].update(missing_dims)

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Added missing dimensions successfully!")
