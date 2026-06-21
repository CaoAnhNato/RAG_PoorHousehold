# -*- coding: utf-8 -*-
"""
Module chứa các quy tắc pháp lý và hằng số liên quan đến việc xác định,
phân loại hộ nghèo, hộ cận nghèo theo chuẩn nghèo đa chiều giai đoạn 2021-2025.
"""

from __future__ import annotations
import random
import re
from typing import Any
import pandas as pd
from scripts.preprocess_enrich_datasets import clean_text, parse_int, normalize_yes_no

# Giai đoạn pháp lý áp dụng
LEGAL_PERIOD = "2021_2025"

# Tùy chọn ngày khảo sát theo năm
DATE_OPTIONS_BY_YEAR = {
    2023: ["2023-09-15", "2023-10-15", "2023-11-15", "2023-12-01"],
    2024: ["2024-09-15", "2024-10-15", "2024-11-15", "2024-12-01"],
}
DATE_OPTIONS_2023 = ["29/10/2023", "05/11/2023", "12/11/2023", "19/11/2023"]
DATE_OPTIONS_2024 = ["29/10/2024", "05/11/2024", "12/11/2024", "19/11/2024"]

# Danh sách dân tộc
ETHNICITY_POOL = [
    "Kinh", "Ê đê", "Mạ", "Mường", "Thái", "M'Nông", "Tày", "Nùng", "Mông", "Dao", "DT Khác"
]

NON_LOCAL_ETHNICITIES = ["Kinh", "Tày", "Nùng", "Mường", "Thái", "Mông", "Dao", "DT Khác"]

# Cấu hình dân tộc tại chỗ (DTTC)
LOCAL_ETHNICITY_MAPPING = {
    "province": "Đắk Nông",
    "source_note": "Cấu hình dự án cần được địa phương kiểm tra lại trước khi dùng cho phân tích chính sách chính thức.",
    "default_local_ethnicities": ["M'Nông", "Mạ", "Ê Đê"],
    "district_overrides": {
        "Huyện Cư Jút": ["M'Nông", "Ê đê"],
        "Huyện Đắk Mil": ["M'Nông", "Ê đê", "Mạ"],
        "Huyện Đắk Song": ["M'Nông", "Mạ"],
        "Huyện Đắk RLấp": ["M'Nông", "Mạ"],
        "Huyện Đăk Glong": ["M'Nông", "Mạ"],
        "Huyện Tuy Đức": ["M'Nông", "Mạ"],
        "Huyện Krông Nô": ["M'Nông", "Ê đê"],
        "Thành phố Gia Nghĩa": ["M'Nông", "Mạ", "Ê đê"],
    },
    "confidence": "controlled_project_assumption_needs_local_review",
}

# Đặc tính tỷ lệ dân tộc thiểu số theo huyện
DISTRICT_MINORITY_PROFILE = {
    "Huyện Cư Jút": "high",
    "Huyện Krông Nô": "high",
    "Huyện Tuy Đức": "high",
    "Huyện Đăk Glong": "high",
    "Huyện Đắk Mil": "medium",
    "Huyện Đắk RLấp": "medium",
    "Huyện Đắk Song": "medium",
    "Thành phố Gia Nghĩa": "urban",
}


def resolve_area_type_info(commune: Any) -> tuple[str, str, str]:
    """
    Xác định phân loại khu vực nông thôn hay thành thị dựa trên tên xã/phường/thị trấn.
    
    Args:
        commune (Any): Tên xã/phường/thị trấn.
        
    Returns:
        tuple[str, str, str]: (area_type, source, confidence)
            - area_type: 'rural' hoặc 'urban'
            - source: nguồn sinh dữ liệu
            - confidence: mức độ tin cậy ('high' hoặc 'low')
    """
    from scripts.preprocess_enrich_datasets import strip_accents
    commune_text = clean_text(commune) or ""
    normalized = strip_accents(commune_text).lower().strip()
    if normalized.startswith("xa"):
        return "rural", "generated_by_legal_rule", "high"
    if normalized.startswith("phuong") or normalized.startswith("thi tran"):
        return "urban", "generated_by_legal_rule", "high"
    return "rural", "template_required_default", "low"


def district_ethnicity_weights(district: str, is_dttc: bool) -> list[tuple[str, float]]:
    """
    Trả về trọng số phân bổ dân tộc cho huyện.
    
    Args:
        district (str): Tên huyện.
        is_dttc (bool): Có phải dân tộc tại chỗ không.
        
    Returns:
        list[tuple[str, float]]: Danh sách cặp (Dân tộc, Trọng số)
    """
    profile = DISTRICT_MINORITY_PROFILE.get(district, "medium")
    if is_dttc:
        return [
            ("M'Nông", 0.35),
            ("Mạ", 0.20),
            ("Ê đê", 0.15),
            ("Mường", 0.06),
            ("Thái", 0.05),
            ("Tày", 0.05),
            ("Nùng", 0.05),
            ("Mông", 0.04),
            ("Dao", 0.03),
            ("DT Khác", 0.02),
            ("Kinh", 0.0),
        ]
    if profile == "high":
        return [
            ("Kinh", 0.35),
            ("M'Nông", 0.20),
            ("Ê đê", 0.10),
            ("Mạ", 0.08),
            ("Mường", 0.08),
            ("Thái", 0.05),
            ("Tày", 0.05),
            ("Nùng", 0.04),
            ("Mông", 0.03),
            ("Dao", 0.03),
            ("DT Khác", 0.09),
        ]
    if profile == "urban":
        return [
            ("Kinh", 0.70),
            ("M'Nông", 0.08),
            ("Ê đê", 0.06),
            ("Mạ", 0.04),
            ("Mường", 0.03),
            ("Thái", 0.03),
            ("Tày", 0.03),
            ("Nùng", 0.01),
            ("Mông", 0.01),
            ("Dao", 0.01),
            ("DT Khác", 0.00),
        ]
    return [
        ("Kinh", 0.55),
        ("M'Nông", 0.12),
        ("Ê đê", 0.08),
        ("Mạ", 0.06),
        ("Mường", 0.05),
        ("Thái", 0.04),
        ("Tày", 0.04),
        ("Nùng", 0.03),
        ("Mông", 0.02),
        ("Dao", 0.01),
        ("DT Khác", 0.00),
    ]


def choose_ethnicity(district: str, is_dttc: bool, rng: random.Random) -> str:
    """
    Chọn ngẫu nhiên một dân tộc dựa trên trọng số phân bổ của huyện.
    
    Args:
        district (str): Tên huyện.
        is_dttc (bool): Có phải dân tộc tại chỗ không.
        rng (random.Random): Bộ sinh số ngẫu nhiên.
        
    Returns:
        str: Tên dân tộc đã chọn.
    """
    from scripts.preprocess_enrich_datasets import choose_from_weights
    choices = district_ethnicity_weights(district, is_dttc)
    values = [item for item, _ in choices]
    weights = [weight for _, weight in choices]
    return choose_from_weights(rng, values, weights)


def resolve_ethnicity_and_dttc(
    district: str,
    classify: str,
    original_co_dan_toc: Any,
    rng: random.Random,
) -> tuple[str, str, bool]:
    """
    Xác định dân tộc và trạng thái dân tộc tại chỗ (DTTC).
    
    Args:
        district (str): Tên huyện.
        classify (str): Phân loại hộ nghèo/cận nghèo.
        original_co_dan_toc (Any): Giá trị dân tộc tại chỗ gốc.
        rng (random.Random): Bộ sinh số ngẫu nhiên.
        
    Returns:
        tuple[str, str, bool]: (ethnicity, co_dan_toc, is_dttc)
    """
    text = clean_text(original_co_dan_toc)
    local_ethnicities = LOCAL_ETHNICITY_MAPPING["district_overrides"].get(district, LOCAL_ETHNICITY_MAPPING["default_local_ethnicities"])
    if text is None:
        if classify == "Hộ nghèo":
            co_dan_toc = "Có" if rng.random() < 0.72 else "Không"
        elif classify == "Hộ cận nghèo":
            co_dan_toc = "Có" if rng.random() < 0.48 else "Không"
        else:
            co_dan_toc = "Có" if rng.random() < 0.18 else "Không"
    else:
        co_dan_toc = normalize_yes_no(text)

    if co_dan_toc == "Có":
        ethnicity = rng.choice(local_ethnicities)
        if ethnicity == "Kinh":
            ethnicity = rng.choice([e for e in local_ethnicities if e != "Kinh"] or local_ethnicities)
        return ethnicity, "Có", True

    ethnicity = rng.choice([e for e in NON_LOCAL_ETHNICITIES if e != "Kinh"])
    return ethnicity, "Không", False


def resolve_b1_point(classify: str, area_type: str, original_value: Any, rng: random.Random) -> tuple[int, str, bool]:
    """
    Xác định điểm B1 hợp lệ dựa trên phân loại hộ nghèo/cận nghèo/không nghèo và khu vực.
    
    Args:
        classify (str): Nhãn phân loại của hộ.
        area_type (str): 'rural' (nông thôn) hoặc 'urban' (thành thị).
        original_value (Any): Điểm B1 gốc.
        rng (random.Random): Bộ sinh số ngẫu nhiên.
        
    Returns:
        tuple[int, str, bool]: (b1_point, source, was_filled)
    """
    original_int = parse_int(original_value, default=0)
    if area_type == "urban":
        ranges = {
            "Hộ nghèo": (90, 175),
            "Hộ cận nghèo": (110, 175),
            "Hộ không nghèo": (176, 260),
        }
    else:
        ranges = {
            "Hộ nghèo": (60, 140),
            "Hộ cận nghèo": (80, 140),
            "Hộ không nghèo": (141, 210),
        }
    low, high = ranges.get(classify, ranges["Hộ không nghèo"])
    generated = rng.randint(low, high)
    if original_int > 0 and low <= original_int <= high:
        return original_int, "cleaned_original", False
    return generated, "generated_by_legal_rule", True


def resolve_deprivation_total_count(
    classify: str,
    original_b2_value: Any,
    original_total_value: Any,
    rng: random.Random,
) -> tuple[int, int, str, bool]:
    """
    Xác định tổng số chỉ số thiếu hụt và điểm B2 tương ứng, đảm bảo tính nhất quán B2 = deprivation.totalCount * 10.
    
    Args:
        classify (str): Nhãn phân loại của hộ.
        original_b2_value (Any): Điểm B2 gốc.
        original_total_value (Any): Tổng chỉ số thiếu hụt gốc.
        rng (random.Random): Bộ sinh số ngẫu nhiên.
        
    Returns:
        tuple[int, int, str, bool]: (deprivation_total, b2_point, source, was_filled)
    """
    original_b2 = parse_int(original_b2_value, default=-1)
    original_total = parse_int(original_total_value, default=-1)
    if classify == "Hộ nghèo":
        total = rng.randint(3, 8)
    else:
        total = rng.randint(0, 2)

    if original_total >= 0 and 0 <= original_total <= 12:
        total = original_total
    elif original_b2 in list(range(0, 121, 10)):
        total = int(original_b2 / 10)
    elif 0 <= original_b2 <= 12:
        total = original_b2

    if classify == "Hộ nghèo":
        total = max(3, min(8, total))
    else:
        total = max(0, min(2, total))

    return total, total * 10, "generated_by_legal_rule", True


def resolve_classification_from_scores(b1_point: int, deprivation_total: int, area_type: str) -> str:
    """
    Xác định nhãn phân loại hộ nghèo dựa trên điểm B1, tổng chỉ số thiếu hụt và khu vực.
    
    Args:
        b1_point (int): Điểm B1.
        deprivation_total (int): Tổng chỉ số thiếu hụt đa chiều.
        area_type (str): 'rural' hoặc 'urban'.
        
    Returns:
        str: Nhãn phân loại ('Hộ nghèo', 'Hộ cận nghèo', 'Hộ không nghèo').
    """
    threshold = 175 if area_type == "urban" else 140
    if b1_point <= threshold and deprivation_total >= 3:
        return "Hộ nghèo"
    if b1_point <= threshold and deprivation_total < 3:
        return "Hộ cận nghèo"
    return "Hộ không nghèo"


def resolve_transition_change_types(beginning: str, ending: str) -> tuple[str, str, bool]:
    """
    Xác định diễn biến chuyển đổi hộ nghèo/cận nghèo giữa đầu kỳ và cuối kỳ.
    
    Args:
        beginning (str): Nhãn phân loại đầu kỳ.
        ending (str): Nhãn phân loại cuối kỳ.
        
    Returns:
        tuple[str, str, bool]: (poor_change_type, near_poor_change_type, is_escaped_poverty)
    """
    if beginning == "Hộ nghèo" and ending == "Hộ nghèo":
        return "poor_beginning", "none", False
    if beginning == "Hộ nghèo" and ending == "Hộ cận nghèo":
        return "poor_to_near_poor", "poor_to_near_poor", False
    if beginning == "Hộ nghèo" and ending == "Hộ không nghèo":
        return "poor_escape_above_near_poor", "none", True
    if beginning == "Hộ cận nghèo" and ending == "Hộ nghèo":
        return "near_poor_to_poor", "near_poor_to_poor", False
    if beginning == "Hộ cận nghèo" and ending == "Hộ cận nghèo":
        return "none", "near_poor_beginning", False
    if beginning == "Hộ cận nghèo" and ending == "Hộ không nghèo":
        return "none", "near_poor_escape", True
    if beginning == "Hộ không nghèo" and ending == "Hộ nghèo":
        return "new_poor", "none", False
    if beginning == "Hộ không nghèo" and ending == "Hộ cận nghèo":
        return "none", "new_near_poor", False
    return "none", "none", False


def class_transition_label(
    beginning: str | None,
    ending: str | None,
    kind: str,
    rng: random.Random,
) -> tuple[str, str]:
    """
    Trả về nhãn chuyển biến cụ thể của hộ.
    
    Args:
        beginning (str | None): Đầu kỳ.
        ending (str | None): Cuối kỳ.
        kind (str): Loại nhãn ('poor', 'near', 'other').
        rng (random.Random): Bộ sinh số ngẫu nhiên.
        
    Returns:
        tuple[str, str]: (poor_label, near_label)
    """
    poor_label, near_label, _ = resolve_transition_change_types(beginning or "Hộ không nghèo", ending or "Hộ không nghèo")
    return poor_label, near_label


def household_deprivation_flags(classify: str | None, rng: random.Random, target_total: int | None = None) -> dict[str, bool]:
    """
    Sinh 12 chỉ số thiếu hụt đa chiều dưới dạng boolean sao cho tổng số chỉ số đúng bằng target_total.
    
    Args:
        classify (str | None): Phân loại hộ.
        rng (random.Random): Bộ sinh số ngẫu nhiên.
        target_total (int | None): Tổng số chỉ số thiếu hụt mong muốn.
        
    Returns:
        dict[str, bool]: Từ điển 12 chỉ số thiếu hụt dạng 'deprivation.<tên_chỉ_số>': boolean.
    """
    from scripts.preprocess_enrich_datasets import choose_from_weights
    poor = classify == "Hộ nghèo"
    near_poor = classify == "Hộ cận nghèo"
    severity_map = {
        "poor": (3, 8, [0.05, 0.08, 0.10, 0.14, 0.16, 0.17, 0.16, 0.14]),
        "near_poor": (0, 2, [0.35, 0.45, 0.20]),
        "other": (0, 2, [0.55, 0.30, 0.15]),
    }
    
    def classify_bucket(c: str | None) -> str:
        if c == "Hộ nghèo": return "poor"
        if c == "Hộ cận nghèo": return "near_poor"
        return "other"

    bucket = classify_bucket(classify)
    low, high, weights = severity_map[bucket]
    if target_total is None:
        target_total = choose_from_weights(rng, list(range(low, high + 1)), weights)
    target_total = int(max(low, min(high, target_total)))
    
    all_flags = [
        "employment",
        "dependentPerson",
        "nutrition",
        "healthInsurance",
        "adultEducation",
        "childSchoolAttendance",
        "housingQuality",
        "housingArea",
        "cleanWater",
        "hygienicToilet",
        "telecommunication",
        "informationAccessAssets",
    ]
    weights_map = {
        "employment": 1.0,
        "dependentPerson": 0.8,
        "nutrition": 1.1,
        "healthInsurance": 1.2,
        "adultEducation": 0.7,
        "childSchoolAttendance": 1.0,
        "housingQuality": 1.0,
        "housingArea": 0.9,
        "cleanWater": 0.8,
        "hygienicToilet": 0.85,
        "telecommunication": 0.6,
        "informationAccessAssets": 0.75,
    }
    if target_total <= 0:
        chosen = set()
    else:
        ordered = sorted(all_flags, key=lambda k: (weights_map[k], rng.random()), reverse=True)
        chosen = set(ordered[:target_total])
    flags = {f"deprivation.{name}": (name in chosen) for name in all_flags}
    if poor and not any(flags.values()):
        flags["deprivation.healthInsurance"] = True
    if near_poor and not any(flags.values()) and target_total > 0:
        flags["deprivation.healthInsurance"] = True
    return flags
