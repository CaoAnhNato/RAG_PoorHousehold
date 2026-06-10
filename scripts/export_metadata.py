# -*- coding: utf-8 -*-
"""
Module chứa cấu hình 15 báo cáo Excel (REPORT_SPECS), cấu trúc bộ từ điển dữ liệu
(Data Dictionary) và các hàm xuất metadata JSON.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any

# Cấu hình 15 báo cáo Excel (REPORT_SPECS)
REPORT_SPECS = [
    {
        "report_id": 1,
        "report_name": "Tổng hợp kết quả rà soát HC,CN,NL,NN có mức sống trung bình",
        "sheet_name": None,
        "used_range": None,
        "header_rows": None,
        "main_groups": ["Tổng hợp theo huyện", "Địa bàn xã/phường/thị trấn"],
        "required_columns": [
            "administrative.province",
            "administrative.district",
            "administrative.commune",
            "family.isAgricultureForestryFisherySaltMediumLivingStandard",
            "classify",
        ],
        "notes": {
            "family.isAgricultureForestryFisherySaltMediumLivingStandard": "aggregate count / flag",
            "classify": "grouping label",
        },
    },
    {
        "report_id": 2,
        "report_name": "Tổng hợp diễn biến hộ nghèo",
        "sheet_name": None,
        "used_range": None,
        "header_rows": None,
        "main_groups": ["Biến động hộ nghèo", "Đầu kỳ / cuối kỳ"],
        "required_columns": [
            "transition.beginningClassify",
            "transition.endingClassify",
            "transition.poorChangeType",
            "classify",
            "administrative.district",
            "administrative.commune",
        ],
        "notes": {
            "transition.beginningClassify": "detail list / aggregate count",
            "transition.endingClassify": "detail list / aggregate count",
            "transition.poorChangeType": "aggregate count",
        },
    },
    {
        "report_id": 3,
        "report_name": "Tổng hợp diễn biến hộ cận nghèo",
        "sheet_name": None,
        "used_range": None,
        "header_rows": None,
        "main_groups": ["Biến động hộ cận nghèo", "Đầu kỳ / cuối kỳ"],
        "required_columns": [
            "transition.beginningClassify",
            "transition.endingClassify",
            "transition.nearPoorChangeType",
            "classify",
            "administrative.district",
            "administrative.commune",
        ],
        "notes": {
            "transition.beginningClassify": "detail list / aggregate count",
            "transition.endingClassify": "detail list / aggregate count",
            "transition.nearPoorChangeType": "aggregate count",
        },
    },
    {
        "report_id": 4,
        "report_name": "Phân tích chỉ số thiếu hụt dịch vụ xã hội cơ bản hộ nghèo",
        "sheet_name": None,
        "used_range": None,
        "header_rows": None,
        "main_groups": ["12 chỉ số thiếu hụt", "Tổng số thiếu hụt"],
        "required_columns": [
            "classify",
            "deprivation.totalCount",
            "deprivation.employment",
            "deprivation.dependentPerson",
            "deprivation.nutrition",
            "deprivation.healthInsurance",
            "deprivation.adultEducation",
            "deprivation.childSchoolAttendance",
            "deprivation.housingQuality",
            "deprivation.housingArea",
            "deprivation.cleanWater",
            "deprivation.hygienicToilet",
            "deprivation.telecommunication",
            "deprivation.informationAccessAssets",
        ],
        "notes": {f"deprivation.{name}": "aggregate count" for name in [
            "employment", "dependentPerson", "nutrition", "healthInsurance",
            "adultEducation", "childSchoolAttendance", "housingQuality", "housingArea",
            "cleanWater", "hygienicToilet", "telecommunication", "informationAccessAssets"
        ]} | {"deprivation.totalCount": "sum / aggregate count"},
    },
    {
        "report_id": 5,
        "report_name": "Phân tích tỷ lệ các chỉ số thiếu hụt dịch vụ xã hội cơ bản hộ nghèo",
        "sheet_name": None,
        "used_range": None,
        "header_rows": None,
        "main_groups": ["12 chỉ số thiếu hụt", "Tỷ lệ phần trăm"],
        "required_columns": [
            "classify",
            "deprivation.totalCount",
            "deprivation.employment",
            "deprivation.dependentPerson",
            "deprivation.nutrition",
            "deprivation.healthInsurance",
            "deprivation.adultEducation",
            "deprivation.childSchoolAttendance",
            "deprivation.housingQuality",
            "deprivation.housingArea",
            "deprivation.cleanWater",
            "deprivation.hygienicToilet",
            "deprivation.telecommunication",
            "deprivation.informationAccessAssets",
        ],
        "notes": {f"deprivation.{name}": "percentage" for name in [
            "employment", "dependentPerson", "nutrition", "healthInsurance",
            "adultEducation", "childSchoolAttendance", "housingQuality", "housingArea",
            "cleanWater", "hygienicToilet", "telecommunication", "informationAccessAssets"
        ]},
    },
    {
        "report_id": 6,
        "report_name": "Phân tích chỉ số thiếu hụt dịch vụ xã hội cơ bản hộ cận nghèo",
        "sheet_name": None,
        "used_range": None,
        "header_rows": None,
        "main_groups": ["12 chỉ số thiếu hụt", "Tổng số thiếu hụt"],
        "required_columns": [
            "classify",
            "deprivation.totalCount",
            "deprivation.employment",
            "deprivation.dependentPerson",
            "deprivation.nutrition",
            "deprivation.healthInsurance",
            "deprivation.adultEducation",
            "deprivation.childSchoolAttendance",
            "deprivation.housingQuality",
            "deprivation.housingArea",
            "deprivation.cleanWater",
            "deprivation.hygienicToilet",
            "deprivation.telecommunication",
            "deprivation.informationAccessAssets",
        ],
        "notes": {f"deprivation.{name}": "aggregate count" for name in [
            "employment", "dependentPerson", "nutrition", "healthInsurance",
            "adultEducation", "childSchoolAttendance", "housingQuality", "housingArea",
            "cleanWater", "hygienicToilet", "telecommunication", "informationAccessAssets"
        ]} | {"deprivation.totalCount": "sum / aggregate count"},
    },
    {
        "report_id": 7,
        "report_name": "Phân tích tỷ lệ các chỉ số thiếu hụt dịch vụ xã hội cơ bản hộ cận nghèo",
        "sheet_name": None,
        "used_range": None,
        "header_rows": None,
        "main_groups": ["12 chỉ số thiếu hụt", "Tỷ lệ phần trăm"],
        "required_columns": [
            "classify",
            "deprivation.totalCount",
            "deprivation.employment",
            "deprivation.dependentPerson",
            "deprivation.nutrition",
            "deprivation.healthInsurance",
            "deprivation.adultEducation",
            "deprivation.childSchoolAttendance",
            "deprivation.housingQuality",
            "deprivation.housingArea",
            "deprivation.cleanWater",
            "deprivation.hygienicToilet",
            "deprivation.telecommunication",
            "deprivation.informationAccessAssets",
        ],
        "notes": {f"deprivation.{name}": "percentage" for name in [
            "employment", "dependentPerson", "nutrition", "healthInsurance",
            "adultEducation", "childSchoolAttendance", "housingQuality", "housingArea",
            "cleanWater", "hygienicToilet", "telecommunication", "informationAccessAssets"
        ]},
    },
    {
        "report_id": 8,
        "report_name": "Phân tích hộ nghèo, hộ cận nghèo theo các nhóm đối tượng",
        "sheet_name": None,
        "used_range": None,
        "header_rows": None,
        "main_groups": ["Nhóm đối tượng", "Hộ nghèo / cận nghèo"],
        "required_columns": [
            "classify",
            "family.hasNoLaborCapacity",
            "family.hasRevolutionMeritPolicy",
            "family.isDTTC",
            "support.health",
            "support.education",
            "support.production",
            "support.credit",
            "support.housing",
            "support.other",
        ],
        "notes": {
            "family.hasNoLaborCapacity": "aggregate count",
            "family.hasRevolutionMeritPolicy": "aggregate count",
            "family.isDTTC": "aggregate count",
            "support.health": "aggregate count",
            "support.education": "aggregate count",
            "support.production": "aggregate count",
            "support.credit": "aggregate count",
            "support.housing": "aggregate count",
            "support.other": "aggregate count",
        },
    },
    {
        "report_id": 9,
        "report_name": "Phân tích hộ nghèo, hộ cận nghèo theo dân tộc",
        "sheet_name": None,
        "used_range": None,
        "header_rows": None,
        "main_groups": ["Dân tộc", "Hộ nghèo / cận nghèo"],
        "required_columns": [
            "family.ethnicity",
            "family.isDTTS",
            "family.isKinh",
            "classify",
        ],
        "notes": {
            "family.ethnicity": "detail list / aggregate count",
            "family.isDTTS": "aggregate count",
            "family.isKinh": "aggregate count",
        },
    },
    {
        "report_id": 10,
        "report_name": "Phân tích hộ nghèo, hộ cận nghèo theo nguyên nhân nghèo",
        "sheet_name": None,
        "used_range": None,
        "header_rows": None,
        "main_groups": ["Nguyên nhân nghèo/cận nghèo", "Hộ nghèo / cận nghèo"],
        "required_columns": [
            "reason.lackProductionLand",
            "reason.lackCapital",
            "reason.lackLabor",
            "reason.lackProductionTools",
            "reason.lackProductionKnowledge",
            "reason.lackLaborSkill",
            "reason.illnessOrAccident",
            "reason.other",
            "classify",
        ],
        "notes": {f"reason.{name}": "aggregate count" for name in [
            "lackProductionLand", "lackCapital", "lackLabor", "lackProductionTools",
            "lackProductionKnowledge", "lackLaborSkill", "illnessOrAccident", "other"
        ]},
    },
    {
        "report_id": 11,
        "report_name": "Tổng hợp chỉ tiêu thiếu hụt của trẻ em thuộc hộ nghèo, hộ cận nghèo",
        "sheet_name": None,
        "used_range": None,
        "header_rows": None,
        "main_groups": ["Trẻ em", "Thiếu hụt của trẻ em"],
        "required_columns": [
            "children.totalCount",
            "children.lackHealthInsuranceCount",
            "children.nutritionDeprivedCount",
            "children.schoolAttendanceDeprivedCount",
            "classify",
        ],
        "notes": {
            "children.totalCount": "sum",
            "children.lackHealthInsuranceCount": "sum",
            "children.nutritionDeprivedCount": "sum",
            "children.schoolAttendanceDeprivedCount": "sum",
        },
    },
    {
        "report_id": 12,
        "report_name": "Tổng hợp kết quả rà soát hộ nghèo theo chuẩn đa chiều",
        "sheet_name": None,
        "used_range": None,
        "header_rows": None,
        "main_groups": ["Chuẩn đa chiều", "Hộ nghèo"],
        "required_columns": [
            "classify",
            "family.povertyStatusDetail",
            "family.hasNoLaborCapacity",
            "family.hasRevolutionMeritPolicy",
            "family.ethnicity",
            "family.isDTTC",
            "support.health",
            "support.education",
            "support.production",
            "support.credit",
            "support.housing",
            "support.other",
            "deprivation.totalCount",
            "children.totalCount",
        ],
        "notes": {
            "family.povertyStatusDetail": "detail list / aggregate count",
            "deprivation.totalCount": "sum",
            "children.totalCount": "sum",
        },
    },
    {
        "report_id": 13,
        "report_name": "Tổng hợp kết quả rà soát hộ cận nghèo theo chuẩn đa chiều",
        "sheet_name": None,
        "used_range": None,
        "header_rows": None,
        "main_groups": ["Chuẩn đa chiều", "Hộ cận nghèo"],
        "required_columns": [
            "classify",
            "family.nearPovertyStatusDetail",
            "family.hasNoLaborCapacity",
            "family.hasRevolutionMeritPolicy",
            "family.ethnicity",
            "family.isDTTC",
            "support.health",
            "support.education",
            "support.production",
            "support.credit",
            "support.housing",
            "support.other",
            "deprivation.totalCount",
            "children.totalCount",
        ],
        "notes": {
            "family.nearPovertyStatusDetail": "detail list / aggregate count",
            "deprivation.totalCount": "sum",
            "children.totalCount": "sum",
        },
    },
    {
        "report_id": 14,
        "report_name": "Danh sách chi tiết hộ cận nghèo",
        "sheet_name": None,
        "used_range": None,
        "header_rows": None,
        "main_groups": ["Danh sách hộ cận nghèo", "Danh sách thành viên hộ"],
        "required_columns": [
            "family.membersGenerated",
            "family.membersFile",
            "family.membersJson",
            "family.nearPovertyStatusDetail",
            "family.hasRevolutionMeritPolicy",
            "family.isDTTC",
            "family.hasNoLaborCapacity",
            "support.health",
            "support.education",
            "support.production",
            "support.credit",
            "support.housing",
            "support.other",
        ],
        "notes": {
            "family.membersGenerated": "detail list",
            "family.membersFile": "detail list",
            "family.membersJson": "detail list",
        },
    },
    {
        "report_id": 15,
        "report_name": "Danh sách chi tiết hộ nghèo",
        "sheet_name": None,
        "used_range": None,
        "header_rows": None,
        "main_groups": ["Danh sách hộ nghèo", "Danh sách thành viên hộ"],
        "required_columns": [
            "family.membersGenerated",
            "family.membersFile",
            "family.membersJson",
            "family.povertyStatusDetail",
            "family.hasRevolutionMeritPolicy",
            "family.isDTTC",
            "family.hasNoLaborCapacity",
            "support.health",
            "support.education",
            "support.production",
            "support.credit",
            "support.housing",
            "support.other",
        ],
        "notes": {
            "family.membersGenerated": "detail list",
            "family.membersFile": "detail list",
            "family.membersJson": "detail list",
        },
    },
]


def build_report_schema_summary(template_status: str = "missing_in_workspace") -> list[dict[str, Any]]:
    """
    Tạo tóm tắt schema của 15 báo cáo Excel.
    
    Args:
        template_status (str): Trạng thái thư mục template.
        
    Returns:
        list[dict[str, Any]]: Danh sách cấu trúc báo cáo.
    """
    summary = []
    for spec in REPORT_SPECS:
        summary.append(
            {
                "report_id": spec["report_id"],
                "report_name": spec["report_name"],
                "sheet_name": spec["sheet_name"],
                "used_range": spec["used_range"],
                "header_rows": spec["header_rows"],
                "main_groups": spec["main_groups"],
                "required_columns": spec["required_columns"],
                "column_notes": spec["notes"],
                "template_status": template_status,
            }
        )
    return summary


def build_data_dictionary() -> dict[str, Any]:
    """
    Xây dựng bộ từ điển dữ liệu (Data Dictionary) mô tả chi tiết các cột.
    
    Returns:
        dict[str, Any]: Từ điển dữ liệu.
    """
    dictionary = {
        "date": {"type": "string", "scope": "original", "description": "Ngày rà soát theo định dạng dd/mm/yyyy"},
        "family.hostName": {"type": "string", "scope": "original", "description": "Chủ hộ"},
        "family.code": {"type": "string", "scope": "original", "description": "Mã hộ sau khi xử lý duplicate"},
        "family.coDanTocTaiCho": {"type": "string", "scope": "original", "description": "Có/Không về dân tộc tại chỗ"},
        "family.hostGender": {"type": "string", "scope": "original", "description": "Giới tính chủ hộ"},
        "family.numberOfMembers": {"type": "integer", "scope": "original", "description": "Số nhân khẩu"},
        "quickReview.result": {"type": "string", "scope": "original", "description": "Kết quả phiếu rà soát nhanh"},
        "b1Point": {"type": "string", "scope": "original", "description": "Điểm phiếu B1"},
        "b2Point": {"type": "string", "scope": "original", "description": "Điểm phiếu B2"},
        "classify": {"type": "string", "scope": "original", "description": "Phân loại hộ"},
        "reviewer": {"type": "string", "scope": "original", "description": "Người rà soát"},
        "processing.original_family_code": {"type": "string", "scope": "generated", "description": "Mã hộ gốc trước khi thêm hậu tố"},
        "processing.family_code_was_changed": {"type": "boolean", "scope": "generated", "description": "Mã hộ có được đổi hậu tố hay không"},
        "processing.duplicate_core_removed": {"type": "boolean", "scope": "derived", "description": "Dòng thuộc nhóm có duplicate lõi đã bị loại bớt"},
        "processing.duplicate_code_group_size": {"type": "integer", "scope": "derived", "description": "Kích thước nhóm mã hộ trùng"},
        "processing.note": {"type": "string", "scope": "generated", "description": "Ghi chú xử lý"},
        "processing.original_date": {"type": "string", "scope": "generated", "description": "Giá trị date gốc"},
        "processing.date_was_normalized": {"type": "boolean", "scope": "generated", "description": "Đã chuẩn hóa ngày hay chưa"},
        "administrative.year": {"type": "integer", "scope": "derived", "description": "Năm dữ liệu"},
        "administrative.province": {"type": "string", "scope": "generated", "description": "Tỉnh"},
        "administrative.district": {"type": "string", "scope": "generated", "description": "Huyện/thành phố"},
        "administrative.commune": {"type": "string", "scope": "generated", "description": "Xã/phường/thị trấn"},
        "administrative.village_or_group": {"type": "string", "scope": "generated", "description": "Thôn/bon/tổ dân phố"},
        "family.isDTTC": {"type": "boolean", "scope": "derived", "description": "Có dân tộc tại chỗ"},
        "family.hostBirthDate": {"type": "string", "scope": "generated", "description": "Ngày sinh chủ hộ"},
        "family.hostBirthYear": {"type": "integer", "scope": "generated", "description": "Năm sinh chủ hộ"},
        "family.ethnicity": {"type": "string", "scope": "generated", "description": "Dân tộc chủ hộ"},
        "family.isDTTS": {"type": "boolean", "scope": "derived", "description": "Hộ DTTS"},
        "family.isKinh": {"type": "boolean", "scope": "derived", "description": "Hộ Kinh"},
        "family.hasNoLaborCapacity": {"type": "boolean", "scope": "generated", "description": "Hộ không có khả năng lao động"},
        "family.hasRevolutionMeritPolicy": {"type": "boolean", "scope": "generated", "description": "Hộ có chính sách người có công"},
        "family.povertyStatusDetail": {"type": "string", "scope": "generated", "description": "Trạng thái nghèo chi tiết"},
        "family.nearPovertyStatusDetail": {"type": "string", "scope": "generated", "description": "Trạng thái cận nghèo chi tiết"},
        "family.isAgricultureForestryFisherySaltMediumLivingStandard": {"type": "boolean", "scope": "generated", "description": "Hộ có mức sống trung bình"},
        "deprivation.totalCount": {"type": "integer", "scope": "derived", "description": "Tổng số chỉ số thiếu hụt"},
        "children.totalCount": {"type": "integer", "scope": "derived", "description": "Tổng số trẻ em"},
        "children.lackHealthInsuranceCount": {"type": "integer", "scope": "derived", "description": "Số trẻ thiếu BHYT"},
        "children.nutritionDeprivedCount": {"type": "integer", "scope": "derived", "description": "Số trẻ thiếu dinh dưỡng"},
        "children.schoolAttendanceDeprivedCount": {"type": "integer", "scope": "derived", "description": "Số trẻ thiếu đi học"},
        "transition.beginningClassify": {"type": "string", "scope": "generated", "description": "Phân loại đầu kỳ"},
        "transition.endingClassify": {"type": "string", "scope": "generated", "description": "Phân loại cuối kỳ"},
        "transition.poorChangeType": {"type": "string", "scope": "generated", "description": "Kiểu biến động hộ nghèo"},
        "transition.nearPoorChangeType": {"type": "string", "scope": "generated", "description": "Kiểu biến động hộ cận nghèo"},
        "family.membersGenerated": {"type": "boolean", "scope": "generated", "description": "Đã sinh member file"},
        "family.membersFile": {"type": "string", "scope": "generated", "description": "Đường dẫn file member"},
        "family.membersJson": {"type": "string", "scope": "generated", "description": "JSON danh sách thành viên"},
        "support.health": {"type": "boolean", "scope": "generated", "description": "Hỗ trợ y tế"},
        "support.education": {"type": "boolean", "scope": "generated", "description": "Hỗ trợ giáo dục"},
        "support.production": {"type": "boolean", "scope": "generated", "description": "Hỗ trợ sản xuất"},
        "support.credit": {"type": "boolean", "scope": "generated", "description": "Hỗ trợ tín dụng"},
        "support.housing": {"type": "boolean", "scope": "generated", "description": "Hỗ trợ nhà ở"},
        "support.other": {"type": "boolean", "scope": "generated", "description": "Hỗ trợ khác"},
    }
    for name in [
        "employment", "dependentPerson", "nutrition", "healthInsurance",
        "adultEducation", "childSchoolAttendance", "housingQuality", "housingArea",
        "cleanWater", "hygienicToilet", "telecommunication", "informationAccessAssets"
    ]:
        dictionary[f"deprivation.{name}"] = {"type": "boolean", "scope": "generated", "description": "Chỉ số thiếu hụt"}
    for name in [
        "lackProductionLand", "lackCapital", "lackLabor", "lackProductionTools",
        "lackProductionKnowledge", "lackLaborSkill", "illnessOrAccident", "other"
    ]:
        dictionary[f"reason.{name}"] = {"type": "boolean", "scope": "generated", "description": "Nguyên nhân nghèo/cận nghèo"}
    return dictionary


def export_metadata_files(output_dir: Path, template_status: str = "missing_in_workspace") -> None:
    """
    Xuất các tệp tin metadata ra thư mục chỉ định.
    
    Args:
        output_dir (Path): Thư mục đầu ra.
        template_status (str): Trạng thái quét template.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Xuất báo cáo schema summary
    summary = build_report_schema_summary(template_status)
    with open(output_dir / "report_specs.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
        
    # Xuất bộ từ điển dữ liệu
    dictionary = build_data_dictionary()
    with open(output_dir / "data_dictionary.json", "w", encoding="utf-8") as f:
        json.dump(dictionary, f, ensure_ascii=False, indent=2)


def build_required_columns_by_report() -> dict[str, Any]:
    """
    Xây dựng cấu trúc các cột yêu cầu cho từng báo cáo.
    
    Returns:
        dict[str, Any]: Bản đồ id báo cáo -> thông tin cột yêu cầu.
    """
    result = {}
    for spec in REPORT_SPECS:
        result[str(spec["report_id"])] = {
            "report_id": spec["report_id"],
            "report_name": spec["report_name"],
            "required_columns": spec["required_columns"],
            "notes": spec["notes"],
        }
    return result
