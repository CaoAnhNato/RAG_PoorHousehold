# -*- coding: utf-8 -*-
"""
Module chứa các hàm logic ở cấp độ hộ gia đình và thành viên, sinh các trường đặc trưng,
nguyên nhân nghèo, chính sách hỗ trợ, phân loại tình trạng nghèo, và sinh dữ liệu thành viên.
"""

from __future__ import annotations
import datetime as dt
import json
import random
import re
from typing import Any
import numpy as np
import pandas as pd

from scripts.preprocess_enrich_datasets import (
    clean_text,
    clean_code,
    parse_int,
    parse_float,
    rng_for,
    normalize_yes_no,
    normalize_gender,
    parse_date_value,
    format_date,
    choose_from_weights,
)
from scripts.legal_rules import (
    LOCAL_ETHNICITY_MAPPING,
    NON_LOCAL_ETHNICITIES,
    DISTRICT_MINORITY_PROFILE,
    DATE_OPTIONS_BY_YEAR,
)

def is_missingish(value: Any) -> bool:
    """
    Kiểm tra xem một giá trị có phải là thiếu hoặc trống hay không.
    
    Args:
        value (Any): Giá trị cần kiểm tra.
        
    Returns:
        bool: True nếu thiếu/trống, ngược lại False.
    """
    text = clean_text(value)
    return text is None or text in {"", "None", "NaN", "nan"}

def audit_suffix(column_name: str) -> str:
    """
    Chuẩn hóa tên cột để làm hậu tố audit log.
    
    Args:
        column_name (str): Tên cột ban đầu.
        
    Returns:
        str: Tên cột đã chuẩn hóa dạng snake_case/hợp lệ.
    """
    return re.sub(r"[^A-Za-z0-9]+", "_", column_name).strip("_")

def candidate_dates_for_year(year: int) -> list[str]:
    """
    Lấy danh sách các ngày khảo sát ứng viên cho một năm nhất định.
    
    Args:
        year (int): Năm khảo sát.
        
    Returns:
        list[str]: Danh sách chuỗi ngày YYYY-MM-DD.
    """
    return DATE_OPTIONS_BY_YEAR.get(year, DATE_OPTIONS_BY_YEAR[2024])

def resolve_area_type_info(commune: Any) -> tuple[str, str, str]:
    """
    Xác định phân loại khu vực thành thị/nông thôn dựa trên tên xã.
    
    Args:
        commune (Any): Tên xã/phường/thị trấn.
        
    Returns:
        tuple[str, str, str]: (area_type, source, confidence)
    """
    commune_text = clean_text(commune) or ""
    normalized = re.sub(r"\s+", " ", commune_text).strip()
    # Loại bỏ dấu tiếng Việt để so sánh
    from scripts.preprocess_enrich_datasets import strip_accents
    normalized_no_accent = strip_accents(normalized).lower()
    if normalized_no_accent.startswith("xa"):
        return "rural", "generated_by_legal_rule", "high"
    if normalized_no_accent.startswith("phuong") or normalized_no_accent.startswith("thi tran"):
        return "urban", "generated_by_legal_rule", "high"
    return "rural", "template_required_default", "low"

def review_period_for_year(year: int) -> str:
    """
    Trả về định danh kỳ rà soát của năm.
    
    Args:
        year (int): Năm rà soát.
        
    Returns:
        str: Định danh kỳ rà soát (ví dụ: '2023_annual_review').
    """
    return f"{year}_annual_review"

def resolve_review_type(date_value: Any) -> str:
    """
    Xác định loại hình rà soát dựa trên ngày khảo sát theo quy định pháp lý.
    
    Args:
        date_value (Any): Ngày khảo sát.
        
    Returns:
        str: Loại hình rà soát (Rà soát định kỳ hằng năm, Rà soát trong năm, Rà soát đột xuất/cuối năm).
    """
    parsed = parse_date_value(date_value)
    if parsed is None:
        return "Rà soát định kỳ hằng năm"
    if dt.date(parsed.year, 9, 1) <= parsed <= dt.date(parsed.year, 12, 14):
        return "Rà soát định kỳ hằng năm"
    if dt.date(parsed.year, 1, 1) <= parsed <= dt.date(parsed.year, 8, 31):
        return "Rà soát trong năm"
    return "Rà soát đột xuất/cuối năm"

def resolve_quick_review_result(value: Any) -> tuple[str, str, bool]:
    """
    Xử lý và chuẩn hóa kết quả rà soát nhanh.
    
    Args:
        value (Any): Giá trị gốc.
        
    Returns:
        tuple[str, str, bool]: (kết quả đã chuẩn hóa, nguồn, cờ điền thiếu)
    """
    text = clean_text(value)
    if text is None or text == "--":
        return "Đủ điều kiện rà soát B1/B2", "template_required_default", True
    return re.sub(r"\s+", " ", text).strip(), "cleaned_original", False

def resolve_reviewer_value(value: Any) -> tuple[str, str, bool]:
    """
    Xử lý danh tính người thực hiện rà soát.
    
    Args:
        value (Any): Giá trị gốc.
        
    Returns:
        tuple[str, str, bool]: (tên người rà soát, nguồn, cờ điền thiếu)
    """
    text = clean_text(value)
    if text is None:
        return "Rà soát viên cấp xã", "template_required_default", True
    return re.sub(r"\s+", " ", text).strip(), "cleaned_original", False

def resolve_host_name_value(value: Any, gender: str, ethnicity: str, rng: random.Random) -> tuple[str, str, bool]:
    """
    Xử lý tên chủ hộ, tự động sinh tên ngẫu nhiên hợp lệ nếu bị thiếu.
    
    Args:
        value (Any): Tên chủ hộ gốc.
        gender (str): Giới tính chủ hộ.
        ethnicity (str): Dân tộc chủ hộ.
        rng (random.Random): Bộ sinh số ngẫu nhiên.
        
    Returns:
        tuple[str, str, bool]: (tên chủ hộ, nguồn, cờ điền thiếu)
    """
    text = clean_text(value)
    if text:
        return re.sub(r"\s+", " ", text).strip(), "cleaned_original", False
    name = generate_member_name(rng, gender, ethnicity)
    return name, "generated_by_controlled_synthetic_rule", True

def resolve_family_members_count(value: Any, classify: str, rng: random.Random) -> tuple[int, str, bool]:
    """
    Xác định số lượng thành viên trong hộ, tự động điền giá trị hợp lệ nếu thiếu/sai.
    
    Args:
        value (Any): Số lượng thành viên gốc.
        classify (str): Phân loại hộ nghèo/cận nghèo/không nghèo.
        rng (random.Random): Bộ sinh số ngẫu nhiên.
        
    Returns:
        tuple[int, str, bool]: (số thành viên, nguồn, cờ điền thiếu)
    """
    size = parse_int(value, default=0)
    if size > 0:
        return size, "cleaned_original", False
    if classify == "Hộ nghèo":
        return rng.randint(2, 7), "generated_by_controlled_synthetic_rule", True
    if classify == "Hộ cận nghèo":
        return rng.randint(2, 6), "generated_by_controlled_synthetic_rule", True
    return rng.randint(1, 6), "generated_by_controlled_synthetic_rule", True

def resolve_ethnicity_and_dttc(
    district: str,
    classify: str,
    original_co_dan_toc: Any,
    rng: random.Random,
) -> tuple[str, str, bool]:
    """
    Xác định dân tộc của hộ gia đình và trạng thái có phải Dân Tộc Tại Chỗ (DTTC) hay không.
    
    Args:
        district (str): Tên huyện.
        classify (str): Phân loại hộ.
        original_co_dan_toc (Any): Trạng thái gốc về DTTC.
        rng (random.Random): Bộ sinh số ngẫu nhiên.
        
    Returns:
        tuple[str, str, bool]: (tên dân tộc, trạng thái DTTC 'Có'/'Không', is_dttc boolean)
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
    Xác định điểm B1 hợp lệ theo chuẩn pháp lý của hộ nghèo/cận nghèo/không nghèo.
    
    Args:
        classify (str): Phân loại hộ.
        area_type (str): Loại khu vực ('urban' hoặc 'rural').
        original_value (Any): Điểm B1 gốc.
        rng (random.Random): Bộ sinh số ngẫu nhiên.
        
    Returns:
        tuple[int, str, bool]: (điểm B1, nguồn, cờ điền thiếu)
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
    Xác định số chỉ số thiếu hụt (B2) và tổng điểm B2 tương ứng tuân thủ phân loại hộ.
    
    Args:
        classify (str): Phân loại hộ.
        original_b2_value (Any): Điểm B2 gốc.
        original_total_value (Any): Số chỉ số thiếu hụt gốc.
        rng (random.Random): Bộ sinh số ngẫu nhiên.
        
    Returns:
        tuple[int, int, str, bool]: (số lượng thiếu hụt, điểm B2, nguồn, cờ điền thiếu)
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
    Tính toán phân loại hộ nghèo/cận nghèo/không nghèo theo quy định pháp lý dựa trên điểm số.
    
    Args:
        b1_point (int): Điểm khảo sát B1.
        deprivation_total (int): Tổng số chiều thiếu hụt.
        area_type (str): Phân loại khu vực ('urban' hoặc 'rural').
        
    Returns:
        str: Phân loại hộ pháp lý ('Hộ nghèo', 'Hộ cận nghèo', 'Hộ không nghèo').
    """
    threshold = 175 if area_type == "urban" else 140
    if b1_point <= threshold and deprivation_total >= 3:
        return "Hộ nghèo"
    if b1_point <= threshold and deprivation_total < 3:
        return "Hộ cận nghèo"
    return "Hộ không nghèo"

def resolve_transition_change_types(beginning: str, ending: str) -> tuple[str, str, bool]:
    """
    Xác định loại chuyển dịch nghèo trong kỳ (đầu kỳ so với cuối kỳ).
    
    Args:
        beginning (str): Phân loại hộ đầu kỳ.
        ending (str): Phân loại hộ cuối kỳ.
        
    Returns:
        tuple[str, str, bool]: (poorChangeType, nearPoorChangeType, isEscapedPoverty)
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

def classify_bucket(classify: str | None) -> str:
    """
    Nhóm phân loại hộ vào 3 nhóm rút gọn phục vụ tính xác suất thiếu hụt.
    
    Args:
        classify (str | None): Phân loại hộ.
        
    Returns:
        str: Nhóm phân loại ('poor', 'near_poor', 'other').
    """
    if classify == "Hộ nghèo":
        return "poor"
    if classify == "Hộ cận nghèo":
        return "near_poor"
    return "other"

def district_ethnicity_weights(district: str, is_dttc: bool) -> list[tuple[str, float]]:
    """
    Trả về phân bổ xác suất các dân tộc của huyện dựa trên trạng thái dân tộc tại chỗ.
    
    Args:
        district (str): Tên huyện.
        is_dttc (bool): Có phải dân tộc tại chỗ không.
        
    Returns:
        list[tuple[str, float]]: Danh sách cặp (tên dân tộc, trọng số xác suất).
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
    Chọn ngẫu nhiên một dân tộc dựa trên huyện và trạng thái dân tộc tại chỗ.
    
    Args:
        district (str): Tên huyện.
        is_dttc (bool): Có phải dân tộc tại chỗ không.
        rng (random.Random): Bộ sinh số ngẫu nhiên.
        
    Returns:
        str: Tên dân tộc được chọn.
    """
    choices = district_ethnicity_weights(district, is_dttc)
    values = [item for item, _ in choices]
    weights = [weight for _, weight in choices]
    return choose_from_weights(rng, values, weights)

def age_to_birthdate(age: int, rng: random.Random, year_anchor: int) -> dt.date:
    """
    Ước lượng ngày sinh dựa trên tuổi hiện tại và năm neo mốc.
    
    Args:
        age (int): Tuổi.
        rng (random.Random): Bộ sinh số ngẫu nhiên.
        year_anchor (int): Năm mốc khảo sát.
        
    Returns:
        dt.date: Ngày sinh tương đối.
    """
    age = max(0, age)
    birth_year = year_anchor - age
    month = rng.randint(1, 12)
    day = rng.randint(1, 28)
    return dt.date(birth_year, month, day)

def host_age_for_row(row: pd.Series, rng: random.Random) -> int:
    """
    Sinh tuổi chủ hộ hợp lý dựa trên quy mô gia đình và tình trạng nghèo.
    
    Args:
        row (pd.Series): Dòng thông tin hộ gia đình.
        rng (random.Random): Bộ sinh số ngẫu nhiên.
        
    Returns:
        int: Tuổi của chủ hộ.
    """
    classify = row.get("classify")
    size = parse_int(row.get("family.numberOfMembers"), default=1)
    if classify == "Hộ nghèo":
        return rng.randint(30, 78 if size > 1 else 85)
    if classify == "Hộ cận nghèo":
        return rng.randint(28, 80)
    if classify == "Hộ không nghèo":
        return rng.randint(25, 75)
    return rng.randint(25, 80)

def allocate_member_ages(size: int, classify: str | None, host_age: int, rng: random.Random) -> list[int]:
    """
    Phân bổ tuổi của các thành viên trong gia đình hợp lý theo cơ cấu tuổi và tình trạng nghèo.
    
    Args:
        size (int): Số lượng thành viên.
        classify (str | None): Phân loại hộ.
        host_age (int): Tuổi chủ hộ.
        rng (random.Random): Bộ sinh số ngẫu nhiên.
        
    Returns:
        list[int]: Danh sách tuổi của từng thành viên (thành viên đầu tiên là chủ hộ).
    """
    if size <= 1:
        return [host_age]
    bucket = classify_bucket(classify)
    child_prob = {"poor": 0.42, "near_poor": 0.34, "other": 0.22}[bucket]
    elder_prob = {"poor": 0.10, "near_poor": 0.08, "other": 0.12}[bucket]
    ages = [host_age]
    for _ in range(size - 1):
        roll = rng.random()
        if roll < child_prob:
            ages.append(rng.randint(0, 15))
        elif roll < child_prob + elder_prob:
            ages.append(rng.randint(60, 90))
        else:
            low = max(16, min(45, host_age - 20))
            high = max(low + 5, min(59, host_age + 15))
            ages.append(rng.randint(low, high))
    return ages

def member_name_pool(gender: str, ethnicity: str) -> tuple[list[str], list[str]]:
    """
    Trả về tập hợp tên mẫu dựa trên giới tính và dân tộc.
    
    Args:
        gender (str): Giới tính ('Nam' hoặc 'Nữ').
        ethnicity (str): Dân tộc.
        
    Returns:
        tuple[list[str], list[str]]: (danh sách tên nam, danh sách tên nữ).
    """
    male = [
        "Nguyễn Văn An", "Trần Văn Bình", "Lê Văn Cường", "Phạm Văn Đức",
        "Hoàng Văn Dũng", "Phan Văn Hải", "Võ Văn Hùng", "Đặng Văn Khoa",
        "Bùi Văn Lâm", "Đỗ Văn Minh", "Ngô Văn Nam", "Dương Văn Phúc",
    ]
    female = [
        "Nguyễn Thị Mai", "Trần Thị Lan", "Lê Thị Hạnh", "Phạm Thị Hoa",
        "Hoàng Thị Ngọc", "Phan Thị Hương", "Võ Thị Loan", "Đặng Thị Nhung",
        "Bùi Thị Phượng", "Đỗ Thị Thanh", "Ngô Thị Thúy", "Dương Thị Vân",
    ]
    if ethnicity != "Kinh":
        male = [
            "Y Phúc", "Y Lộc", "Y Sang", "H'Rin", "H'My",
            "A Mí", "A Kha", "Rơ Mah Đức", "K'Tiêng", "Siu Khoa",
        ] + male
        female = [
            "H'Lan", "H'Nhung", "Y Lanh", "Y Nhi", "H'Mây",
            "A Dung", "Rơ Chăm Mai", "K'Ly", "Siu Hồng", "A Nhiên",
        ] + female
    return male, female

def generate_member_name(rng: random.Random, gender: str, ethnicity: str) -> str:
    """
    Sinh tên ngẫu nhiên cho thành viên theo giới tính và dân tộc.
    
    Args:
        rng (random.Random): Bộ sinh số ngẫu nhiên.
        gender (str): Giới tính.
        ethnicity (str): Dân tộc.
        
    Returns:
        str: Tên thành viên được sinh.
    """
    male_pool, female_pool = member_name_pool(gender, ethnicity)
    if gender == "Nữ":
        return rng.choice(female_pool)
    return rng.choice(male_pool)

def relationship_for_member(age: int, member_index: int, host_age: int, rng: random.Random) -> str:
    """
    Xác định mối quan hệ của thành viên với chủ hộ dựa trên chênh lệch tuổi tác.
    
    Args:
        age (int): Tuổi thành viên.
        member_index (int): Thứ tự thành viên trong hộ (1-indexed).
        host_age (int): Tuổi chủ hộ.
        rng (random.Random): Bộ sinh số ngẫu nhiên.
        
    Returns:
        str: Mối quan hệ với chủ hộ.
    """
    if member_index == 1:
        return "Chủ hộ"
    if age >= host_age - 5 and age <= host_age + 5 and member_index == 2:
        return rng.choice(["Vợ/chồng", "Vợ/chồng chủ hộ"])
    if age < 18:
        return rng.choice(["Con", "Cháu"])
    if age >= host_age + 18:
        return rng.choice(["Bố/mẹ", "Khác"])
    return rng.choice(["Con", "Anh/chị/em", "Khác"])

def choose_child_health_insurance(is_poor: bool, is_near_poor: bool, rng: random.Random) -> bool:
    """
    Quyết định ngẫu nhiên xem trẻ em dưới 6 tuổi/dưới 16 tuổi có bảo hiểm y tế không.
    
    Args:
        is_poor (bool): Có thuộc hộ nghèo không.
        is_near_poor (bool): Có thuộc hộ cận nghèo không.
        rng (random.Random): Bộ sinh số ngẫu nhiên.
        
    Returns:
        bool: True nếu có bảo hiểm y tế, ngược lại False.
    """
    if is_poor:
        return rng.random() < 0.70
    if is_near_poor:
        return rng.random() < 0.78
    return rng.random() < 0.88

def choose_child_deprivation_flag(base_prob: float, rng: random.Random) -> bool:
    """
    Quyết định ngẫu nhiên một chiều thiếu hụt cụ thể của trẻ em.
    
    Args:
        base_prob (float): Xác suất thiếu hụt cơ sở.
        rng (random.Random): Bộ sinh số ngẫu nhiên.
        
    Returns:
        bool: True nếu bị thiếu hụt, ngược lại False.
    """
    return rng.random() < base_prob

def household_deprivation_flags(classify: str | None, rng: random.Random, target_total: int | None = None) -> dict[str, bool]:
    """
    Sinh các thuộc tính thiếu hụt (deprivation.xxx) của hộ gia đình khớp với tổng số lượng thiếu hụt.
    
    Args:
        classify (str | None): Phân loại hộ.
        rng (random.Random): Bộ sinh số ngẫu nhiên.
        target_total (int | None): Số chiều thiếu hụt mục tiêu.
        
    Returns:
        dict[str, bool]: Từ điển các chiều thiếu hụt.
    """
    poor = classify == "Hộ nghèo"
    near_poor = classify == "Hộ cận nghèo"
    severity_map = {
        "poor": (3, 8, [0.05, 0.08, 0.10, 0.14, 0.16, 0.17, 0.16, 0.14]),
        "near_poor": (0, 2, [0.35, 0.45, 0.20]),
        "other": (0, 2, [0.55, 0.30, 0.15]),
    }
    bucket = classify_bucket(classify)
    low, high, weights = severity_map[bucket]
    if target_total is None:
        target_total = choose_from_weights(rng, list(range(low, high + 1)), weights)
    target_total = int(max(low, min(high, target_total)))
    all_flags = [
        "employment", "dependentPerson", "nutrition", "healthInsurance",
        "adultEducation", "childSchoolAttendance", "housingQuality",
        "housingArea", "cleanWater", "hygienicToilet",
        "telecommunication", "informationAccessAssets"
    ]
    weights_map = {
        "employment": 1.0, "dependentPerson": 0.8, "nutrition": 1.1,
        "healthInsurance": 1.2, "adultEducation": 0.7, "childSchoolAttendance": 1.0,
        "housingQuality": 1.0, "housingArea": 0.9, "cleanWater": 0.8,
        "hygienicToilet": 0.85, "telecommunication": 0.6, "informationAccessAssets": 0.75
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

def reason_flags(classify: str | None, deprivation_flags: dict[str, bool], children_total: int, rng: random.Random) -> dict[str, bool]:
    """
    Xác định các nguyên nhân nghèo/cận nghèo của hộ gia đình (dưới dạng các cột boolean).
    
    Args:
        classify (str | None): Phân loại hộ.
        deprivation_flags (dict[str, bool]): Từ điển chỉ số thiếu hụt.
        children_total (int): Số trẻ em dưới 16 tuổi trong hộ.
        rng (random.Random): Bộ sinh số ngẫu nhiên.
        
    Returns:
        dict[str, bool]: Từ điển các lý do nghèo dạng 'reason.<tên_lý_do>': boolean.
    """
    poor = classify == "Hộ nghèo"
    near_poor = classify == "Hộ cận nghèo"
    if not (poor or near_poor):
        return {
            "reason.lackProductionLand": False,
            "reason.lackCapital": False,
            "reason.lackLabor": False,
            "reason.lackProductionTools": False,
            "reason.lackProductionKnowledge": False,
            "reason.lackLaborSkill": False,
            "reason.illnessOrAccident": False,
            "reason.other": False,
        }
    base = 0.25 if poor else 0.18
    choices = {
        "reason.lackProductionLand": 0.10 + base,
        "reason.lackCapital": 0.18 + base,
        "reason.lackLabor": 0.12 + base,
        "reason.lackProductionTools": 0.10 + base,
        "reason.lackProductionKnowledge": 0.10 + base,
        "reason.lackLaborSkill": 0.10 + base,
        "reason.illnessOrAccident": 0.14 + base,
        "reason.other": 0.03,
    }
    if deprivation_flags.get("deprivation.healthInsurance"):
        choices["reason.illnessOrAccident"] += 0.08
    if deprivation_flags.get("deprivation.housingQuality") or deprivation_flags.get("deprivation.housingArea"):
        choices["reason.lackCapital"] += 0.04
    if children_total > 0:
        choices["reason.lackCapital"] += 0.02
    flags = {k: rng.random() < p for k, p in choices.items()}
    if not any(flags.values()):
        flags["reason.other"] = True
    return flags

def support_flags(
    classify: str | None,
    deprivation_flags: dict[str, bool],
    reason_flags_map: dict[str, bool],
    children_total: int,
    children_lack_health: int,
    rng: random.Random,
) -> dict[str, bool]:
    """
    Xác định các chính sách hỗ trợ nhận được dựa trên tình trạng thiếu hụt và lý do nghèo.
    
    Args:
        classify (str | None): Phân loại hộ.
        deprivation_flags (dict[str, bool]): Từ điển chỉ số thiếu hụt.
        reason_flags_map (dict[str, bool]): Từ điển lý do nghèo.
        children_total (int): Số trẻ em dưới 16 tuổi.
        children_lack_health (int): Số trẻ em thiếu bảo hiểm y tế.
        rng (random.Random): Bộ sinh số ngẫu nhiên.
        
    Returns:
        dict[str, bool]: Từ điển các chính sách hỗ trợ dạng 'support.<tên_chính_sách>': boolean.
    """
    poor = classify == "Hộ nghèo"
    near_poor = classify == "Hộ cận nghèo"
    if not (poor or near_poor):
        return {
            "support.health": False,
            "support.education": False,
            "support.production": False,
            "support.credit": False,
            "support.housing": False,
            "support.other": False,
        }
    flags = {
        "support.health": bool(deprivation_flags.get("deprivation.healthInsurance") or children_lack_health > 0),
        "support.education": bool(children_total > 0 and (deprivation_flags.get("deprivation.childSchoolAttendance") or children_total > 0)),
        "support.production": bool(
            reason_flags_map.get("reason.lackProductionLand")
            or reason_flags_map.get("reason.lackProductionTools")
            or reason_flags_map.get("reason.lackProductionKnowledge")
        ),
        "support.credit": bool(reason_flags_map.get("reason.lackCapital")),
        "support.housing": bool(deprivation_flags.get("deprivation.housingQuality") or deprivation_flags.get("deprivation.housingArea")),
        "support.other": False,
    }
    if not any(v for k, v in flags.items() if k != "support.other"):
        flags["support.other"] = True
    return flags

def poverty_detail(classify: str | None, rng: random.Random) -> tuple[str | None, str | None]:
    """
    Chi tiết nhãn tình trạng nghèo (Nghèo mới, Tái nghèo, Nghèo cũ) hoặc cận nghèo.
    
    Args:
        classify (str | None): Phân loại hộ.
        rng (random.Random): Bộ sinh số ngẫu nhiên.
        
    Returns:
        tuple[str | None, str | None]: (povertyStatusDetail, nearPovertyStatusDetail)
    """
    if classify == "Hộ nghèo":
        return choose_from_weights(rng, ["Nghèo mới", "Tái nghèo", "Nghèo cũ"], [0.55, 0.25, 0.20]), "Không áp dụng"
    if classify == "Hộ cận nghèo":
        return "Không áp dụng", choose_from_weights(rng, ["Cận nghèo mới", "Tái cận nghèo", "Cận nghèo cũ"], [0.55, 0.20, 0.25])
    return "Không áp dụng", "Không áp dụng"

def generate_household_features(
    df: pd.DataFrame,
    year: int,
    district: str,
    seed: int,
) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    """
    Sinh các trường đặc trưng ở cấp độ hộ gia đình và thành viên từ dữ liệu thô.
    
    Args:
        df (pd.DataFrame): Dataframe chứa thông tin hộ sơ bộ.
        year (int): Năm rà soát.
        district (str): Huyện.
        seed (int): Hạt giống ngẫu nhiên.
        
    Returns:
        tuple[pd.DataFrame, list[dict[str, Any]]]: (df_hộ_gia_đình, danh_sách_thành_viên).
    """
    df = df.copy()
    rows: list[dict[str, Any]] = []
    members_rows: list[dict[str, Any]] = []

    for idx, row in df.iterrows():
        row_rng = rng_for(seed, "household", year, district, idx, row.get("family.code"), row.get("family.hostName"))
        out: dict[str, Any] = {col: row.get(col) for col in df.columns}

        out["processing.note"] = clean_text(row.get("processing.note")) or "Không áp dụng"
        out["processing.duplicate_core_removed"] = bool(row.get("processing.duplicate_core_removed"))
        out["processing.duplicate_code_group_size"] = parse_int(row.get("processing.duplicate_code_group_size"), default=1)

        original_classify = clean_text(row.get("classify")) or "Hộ không nghèo"
        if original_classify not in {"Hộ nghèo", "Hộ cận nghèo", "Hộ không nghèo"}:
            original_classify = "Hộ không nghèo"
        out["classify.original"] = original_classify

        area_type, area_source, area_confidence = resolve_area_type_info(row.get("administrative.commune"))
        out["administrative.areaType"] = area_type
        out["administrative.areaTypeSource"] = area_source
        out["administrative.areaTypeConfidence"] = area_confidence

        review_result, review_source, review_filled = resolve_quick_review_result(row.get("quickReview.result"))
        reviewer_value, reviewer_source, reviewer_filled = resolve_reviewer_value(row.get("reviewer"))
        out["quickReview.result"] = review_result
        out["reviewer"] = reviewer_value
        out["reviewer.role"] = "Người thực hiện rà soát"
        out["reviewer.source"] = reviewer_source

        date_value = row.get("date")
        out["review.reviewType"] = resolve_review_type(date_value)
        out["review.reviewPeriod"] = review_period_for_year(year)

        ethnicity, co_dan_toc, is_dttc = resolve_ethnicity_and_dttc(district, original_classify, row.get("family.coDanTocTaiCho"), row_rng)
        host_gender = normalize_gender(row.get("family.hostGender"), row.get("family.hostName"), row_rng)
        host_name, host_name_source, host_name_filled = resolve_host_name_value(row.get("family.hostName"), host_gender, ethnicity, row_rng)

        out["family.hostName"] = host_name
        out["family.hostGender"] = host_gender
        out["family.coDanTocTaiCho"] = co_dan_toc
        out["family.ethnicity"] = ethnicity
        out["family.isDTTC"] = bool(is_dttc)
        out["family.isKinh"] = ethnicity == "Kinh"
        out["family.isDTTS"] = not out["family.isKinh"]

        out["processing.original_family_hostName"] = clean_text(row.get("family.hostName")) or "Không xác định"
        out["processing.source.family.hostName"] = host_name_source
        out["processing.family_hostName_was_filled"] = host_name_filled
        out["processing.family_hostName_rule"] = "generated_by_controlled_synthetic_rule"
        out["processing.original_family_hostGender"] = clean_text(row.get("family.hostGender")) or "Không xác định"
        out["processing.source.family.hostGender"] = "cleaned_original" if not is_missingish(row.get("family.hostGender")) else "generated_by_controlled_synthetic_rule"
        out["processing.family_hostGender_was_filled"] = is_missingish(row.get("family.hostGender"))
        out["processing.family_hostGender_rule"] = "normalized_gender_rule"
        out["processing.original_family_coDanTocTaiCho"] = clean_text(row.get("family.coDanTocTaiCho")) or "Không xác định"
        out["processing.source.family.coDanTocTaiCho"] = "cleaned_original" if not is_missingish(row.get("family.coDanTocTaiCho")) else "generated_by_controlled_synthetic_rule"
        out["processing.family_coDanTocTaiCho_was_filled"] = is_missingish(row.get("family.coDanTocTaiCho"))
        out["processing.family_coDanTocTaiCho_rule"] = "ethnicity_consistency_rule"
        out["family.isPoorNearPoorDTTS"] = bool(original_classify in {"Hộ nghèo", "Hộ cận nghèo"} and out["family.isDTTS"])

        family_size, family_size_source, family_size_filled = resolve_family_members_count(row.get("family.numberOfMembers"), original_classify, row_rng)
        out["family.numberOfMembers"] = int(family_size)
        out["processing.original_family_numberOfMembers"] = parse_int(row.get("family.numberOfMembers"), default=0) if not is_missingish(row.get("family.numberOfMembers")) else "Không xác định"
        out["processing.source.family.numberOfMembers"] = family_size_source
        out["processing.family_numberOfMembers_was_filled"] = family_size_filled
        out["processing.family_numberOfMembers_rule"] = "generated_from_classify_final_when_invalid"

        b1_point, b1_source, b1_filled = resolve_b1_point(original_classify, area_type, row.get("b1Point"), row_rng)
        deprivation_total, b2_point, b2_source, b2_filled = resolve_deprivation_total_count(original_classify, row.get("b2Point"), row.get("deprivation.totalCount"), row_rng)
        legal_classify = resolve_classification_from_scores(b1_point, deprivation_total, area_type)
        if original_classify == legal_classify:
            final_classify = original_classify
            consistency_status = "matched_legal_rule"
            consistency_reason = "original_consistent_with_legal_rule"
        else:
            final_classify = legal_classify
            consistency_status = "overridden_by_legal_rule" if original_classify in {"Hộ nghèo", "Hộ cận nghèo", "Hộ không nghèo"} else "filled_from_legal_rule"
            consistency_reason = "original_missing" if original_classify not in {"Hộ nghèo", "Hộ cận nghèo", "Hộ không nghèo"} else "original_conflicted_with_legal_rule"

        out["classify"] = original_classify
        out["classify.legalRecomputed"] = legal_classify
        out["classify.final"] = final_classify
        out["classify.consistencyStatus"] = consistency_status
        out["classify.consistencyReason"] = consistency_reason
        out["b1Point"] = int(b1_point)
        out["b2Point"] = int(b2_point)
        out["deprivation.totalCount"] = int(deprivation_total)
        out["processing.original_b1Point"] = clean_text(row.get("b1Point")) or "Không xác định"
        out["processing.source.b1Point"] = b1_source
        out["processing.b1Point_was_filled"] = b1_filled
        out["processing.b1Point_rule"] = f"{area_type}_threshold_rule"
        out["processing.original_b2Point"] = clean_text(row.get("b2Point")) or "Không xác định"
        out["processing.source.b2Point"] = b2_source
        out["processing.source.deprivation.totalCount"] = "derived_from_generated_values"
        out["processing.b2Point_was_filled"] = b2_filled
        out["processing.b2Point_rule"] = "deprivation.totalCount * 10"

        host_age = host_age_for_row(pd.Series({"classify": final_classify, "family.numberOfMembers": family_size}), row_rng)
        host_birth_date = age_to_birthdate(host_age, row_rng, year)
        out["family.hostBirthDate"] = format_date(host_birth_date)
        out["family.hostBirthYear"] = host_birth_date.year
        out["processing.original_date"] = clean_text(row.get("processing.original_date")) or clean_text(row.get("date")) or "Không xác định"
        out["processing.source.date"] = clean_text(row.get("processing.source.date")) or "cleaned_original"
        out["processing.date_was_filled"] = bool(row.get("processing.date_was_filled")) if row.get("processing.date_was_filled") is not None else False
        out["processing.date_was_normalized"] = bool(row.get("processing.date_was_normalized")) if row.get("processing.date_was_normalized") is not None else False

        if final_classify == "Hộ nghèo":
            out["family.povertyStatusDetail"], out["family.nearPovertyStatusDetail"] = poverty_detail(final_classify, row_rng)
        elif final_classify == "Hộ cận nghèo":
            out["family.povertyStatusDetail"], out["family.nearPovertyStatusDetail"] = poverty_detail(final_classify, row_rng)
        else:
            out["family.povertyStatusDetail"], out["family.nearPovertyStatusDetail"] = "Không áp dụng", "Không áp dụng"
        out["family.isAgricultureForestryFisherySaltMediumLivingStandard"] = bool(final_classify == "Hộ không nghèo" and row_rng.random() < 0.28)
        out["family.hasNoLaborCapacity"] = bool(
            (final_classify == "Hộ nghèo" and row_rng.random() < 0.18)
            or (final_classify == "Hộ cận nghèo" and row_rng.random() < 0.12)
            or (final_classify == "Hộ không nghèo" and row_rng.random() < 0.04)
            or host_age >= 70
        )
        out["family.hasRevolutionMeritPolicy"] = bool(row_rng.random() < 0.03)

        size = int(family_size)
        ages = allocate_member_ages(size, final_classify, host_age, row_rng)
        child_indices = [i for i, age in enumerate(ages) if age < 16]
        child_total = len(child_indices)
        child_lack_health = 0
        child_nutrition = 0
        child_school = 0
        member_records: list[dict[str, Any]] = []
        for member_pos, age in enumerate(ages, start=1):
            member_rng = rng_for(seed, "member", year, district, idx, member_pos, row.get("family.code"), host_name)
            if member_pos == 1:
                member_name = host_name
                relation = "Chủ hộ"
                member_gender = out["family.hostGender"]
                member_ethnicity = ethnicity
                birth_date = host_birth_date
                birth_year = host_birth_date.year
                is_host = True
            else:
                member_gender = "Nam" if member_rng.random() < 0.5 else "Nữ"
                member_name = generate_member_name(member_rng, member_gender, ethnicity)
                relation = relationship_for_member(age, member_pos, host_age, member_rng)
                member_ethnicity = ethnicity if member_rng.random() < 0.92 else choose_ethnicity(district, False, member_rng)
                birth_date = age_to_birthdate(age, member_rng, year)
                birth_year = birth_date.year
                is_host = False
            is_child = age < 16
            if is_child:
                lack_health = not choose_child_health_insurance(final_classify == "Hộ nghèo", final_classify == "Hộ cận nghèo", member_rng)
                nutrition_deprived = choose_child_deprivation_flag(0.28 if final_classify == "Hộ nghèo" else 0.18 if final_classify == "Hộ cận nghèo" else 0.08, member_rng)
                school_deprived = choose_child_deprivation_flag(0.24 if final_classify == "Hộ nghèo" else 0.14 if final_classify == "Hộ cận nghèo" else 0.05, member_rng)
            else:
                lack_health = False
                nutrition_deprived = False
                school_deprived = False
            child_lack_health += int(is_child and lack_health)
            child_nutrition += int(is_child and nutrition_deprived)
            child_school += int(is_child and school_deprived)
            member_records.append(
                {
                    "administrative.year": year,
                    "administrative.province": "Đắk Nông",
                    "administrative.district": district,
                    "administrative.commune": row.get("administrative.commune"),
                    "administrative.village_or_group": row.get("administrative.village_or_group"),
                    "family.code": out["family.code"],
                    "family.hostName": host_name,
                    "member.householdOrder": idx + 1,
                    "member.orderInHousehold": member_pos,
                    "member.fullName": member_name,
                    "member.gender": member_gender,
                    "member.birthDate": format_date(birth_date),
                    "member.birthYear": birth_year,
                    "member.ethnicity": member_ethnicity,
                    "member.relationshipToHost": relation,
                    "member.isHost": is_host,
                    "member.isChild": is_child,
                    "member.hasHealthInsurance": bool(not lack_health),
                    "member.nutritionDeprived": bool(nutrition_deprived),
                    "member.schoolAttendanceDeprived": bool(school_deprived),
                }
            )

        out["children.totalCount"] = child_total
        out["children.lackHealthInsuranceCount"] = min(child_total, child_lack_health)
        out["children.nutritionDeprivedCount"] = min(child_total, child_nutrition)
        out["children.schoolAttendanceDeprivedCount"] = min(child_total, child_school)

        dep_flags = household_deprivation_flags(final_classify, row_rng, target_total=deprivation_total)
        for col, val in dep_flags.items():
            out[col] = bool(val)

        reason_map = reason_flags(final_classify, dep_flags, child_total, row_rng)
        for col, val in reason_map.items():
            out[col] = bool(val)

        support_map = support_flags(final_classify, dep_flags, reason_map, child_total, child_lack_health, row_rng)
        for col, val in support_map.items():
            out[col] = bool(val)

        if final_classify == "Hộ nghèo":
            beginning_pool = ["Hộ nghèo", "Hộ cận nghèo", "Hộ không nghèo"]
        elif final_classify == "Hộ cận nghèo":
            beginning_pool = ["Hộ cận nghèo", "Hộ nghèo", "Hộ không nghèo"]
        else:
            beginning_pool = ["Hộ không nghèo", "Hộ cận nghèo", "Hộ nghèo"]
        beginning = row_rng.choice(beginning_pool)
        poor_change, near_change, escaped = resolve_transition_change_types(beginning, final_classify)
        out["transition.beginningClassify"] = beginning
        out["transition.endingClassify"] = final_classify
        out["transition.poorChangeType"] = poor_change
        out["transition.nearPoorChangeType"] = near_change
        out["transition.isEscapedPoverty"] = escaped

        out["family.membersGenerated"] = True
        out["family.membersFile"] = "Không áp dụng"
        out["family.membersJson"] = json.dumps(member_records, ensure_ascii=False)

        out["member.householdOrder"] = idx + 1

        out["processing.source.family.code"] = "derived_from_original" if out.get("processing.family_code_was_changed") else "original"
        out["processing.family_code_rule"] = "duplicate suffix preserved from first occurrence"

        rows.append(out)
        members_rows.extend(member_records)

    df = pd.DataFrame(rows)
    for col in [
        "family.coDanTocTaiCho", "family.hostGender", "family.hostName", "family.numberOfMembers",
        "quickReview.result", "b1Point", "b2Point", "classify", "reviewer",
        "reviewer.role", "reviewer.source", "review.reviewType", "review.reviewPeriod",
        "administrative.areaType", "administrative.areaTypeSource", "administrative.areaTypeConfidence",
        "classify.original", "classify.legalRecomputed", "classify.final", "classify.consistencyStatus",
        "classify.consistencyReason", "transition.isEscapedPoverty", "family.isPoorNearPoorDTTS",
        "processing.source.date", "processing.date_was_filled", "processing.date_was_normalized",
        "processing.original_b1Point", "processing.source.b1Point", "processing.b1Point_was_filled",
        "processing.b1Point_rule", "processing.original_b2Point", "processing.source.b2Point",
        "processing.source.deprivation.totalCount", "processing.b2Point_was_filled", "processing.b2Point_rule",
        "processing.original_family_hostName", "processing.source.family.hostName", "processing.family_hostName_was_filled",
        "processing.family_hostName_rule", "processing.original_family_hostGender", "processing.source.family.hostGender",
        "processing.family_hostGender_was_filled", "processing.family_hostGender_rule", "processing.original_family_coDanTocTaiCho",
        "processing.source.family.coDanTocTaiCho", "processing.family_coDanTocTaiCho_was_filled", "processing.family_coDanTocTaiCho_rule",
        "processing.original_family_numberOfMembers", "processing.source.family.numberOfMembers",
        "processing.family_numberOfMembers_was_filled", "processing.family_numberOfMembers_rule",
        "processing.source.family.code", "processing.family_code_rule"
    ]:
        if col not in df.columns:
            if col in {
                "family.isDTTC", "family.isDTTS", "family.isKinh", "family.hasNoLaborCapacity",
                "family.hasRevolutionMeritPolicy", "family.isAgricultureForestryFisherySaltMediumLivingStandard",
                "family.membersGenerated", "transition.isEscapedPoverty", "family.isPoorNearPoorDTTS",
                "processing.date_was_filled", "processing.date_was_normalized", "processing.b1Point_was_filled",
                "processing.b2Point_was_filled", "processing.family_hostName_was_filled",
                "processing.family_hostGender_was_filled", "processing.family_coDanTocTaiCho_was_filled",
                "processing.family_numberOfMembers_was_filled"
            }:
                df[col] = False
            elif col in {
                "family.numberOfMembers", "b1Point", "b2Point", "deprivation.totalCount",
                "children.totalCount", "children.lackHealthInsuranceCount", "children.nutritionDeprivedCount",
                "children.schoolAttendanceDeprivedCount", "family.hostBirthYear", "member.householdOrder"
            }:
                df[col] = 0
            elif col == "family.membersJson":
                df[col] = "[]"
            else:
                df[col] = "Không xác định"

    df["family.membersGenerated"] = df["family.membersGenerated"].fillna(True)
    df["family.membersFile"] = df["family.membersFile"].fillna("Không áp dụng")
    df["family.membersJson"] = df["family.membersJson"].fillna("[]")
    df["transition.isEscapedPoverty"] = df["transition.isEscapedPoverty"].fillna(False)
    df["family.isPoorNearPoorDTTS"] = df["family.isPoorNearPoorDTTS"].fillna(False)

    return df, members_rows
