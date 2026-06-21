# -*- coding: utf-8 -*-
"""
Module chứa các hàm sinh dữ liệu cấp thành viên của hộ gia đình,
bao gồm tuổi tác, họ tên, quan hệ với chủ hộ và thông tin trẻ em.
"""

from __future__ import annotations
import datetime as dt
import random
import pandas as pd
from typing import Any

# Import các hàm tiện ích
from scripts.preprocess_enrich_datasets import parse_int


def age_to_birthdate(age: int, rng: random.Random, year_anchor: int) -> dt.date:
    """
    Tính ngày sinh dt.date ngẫu nhiên dựa trên tuổi và năm mốc (năm khảo sát).
    
    Args:
        age (int): Tuổi.
        rng (random.Random): Bộ sinh số ngẫu nhiên.
        year_anchor (int): Năm khảo sát.
        
    Returns:
        dt.date: Ngày sinh tương ứng.
    """
    age = max(0, age)
    birth_year = year_anchor - age
    month = rng.randint(1, 12)
    day = rng.randint(1, 28)
    return dt.date(birth_year, month, day)


def host_age_for_row(row: pd.Series, rng: random.Random) -> int:
    """
    Xác định tuổi của chủ hộ dựa trên phân loại hộ nghèo và số thành viên.
    
    Args:
        row (pd.Series): Dòng thông tin hộ gia đình.
        rng (random.Random): Bộ sinh số ngẫu nhiên.
        
    Returns:
        int: Tuổi chủ hộ.
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
    Phân bổ độ tuổi cho tất cả các thành viên trong hộ dựa trên quy mô gia đình và loại hộ.
    
    Args:
        size (int): Số thành viên.
        classify (str | None): Phân loại hộ.
        host_age (int): Tuổi chủ hộ.
        rng (random.Random): Bộ sinh số ngẫu nhiên.
        
    Returns:
        list[int]: Danh sách tuổi của các thành viên.
    """
    if size <= 1:
        return [host_age]
    
    # Xác định bucket
    if classify == "Hộ nghèo":
        bucket = "poor"
    elif classify == "Hộ cận nghèo":
        bucket = "near_poor"
    else:
        bucket = "other"

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
    """Trả về kho tên nam/nữ mặc định dựa trên giới tính và dân tộc."""
    male = [
        "Nguyễn Văn An", "Trần Văn Bình", "Lê Văn Cường", "Phạm Văn Đức",
        "Hoàng Văn Dũng", "Phan Văn Hải", "Võ Văn Hùng", "Đặng Văn Khoa",
        "Bùi Văn Lâm", "Đỗ Văn Minh", "Ngô Văn Nam", "Dương Văn Phúc"
    ]
    female = [
        "Nguyễn Thị Mai", "Trần Thị Lan", "Lê Thị Hạnh", "Phạm Thị Hoa",
        "Hoàng Thị Ngọc", "Phan Thị Hương", "Võ Thị Loan", "Đặng Thị Nhung",
        "Bùi Thị Phượng", "Đỗ Thị Thanh", "Ngô Thị Thúy", "Dương Thị Vân"
    ]
    if ethnicity != "Kinh":
        male = [
            "Y Phúc", "Y Lộc", "Y Sang", "H'Rin", "H'My",
            "A Mí", "A Kha", "Rơ Mah Đức", "K'Tiêng", "Siu Khoa"
        ] + male
        female = [
            "H'Lan", "H'Nhung", "Y Lanh", "Y Nhi", "H'Mây",
            "A Dung", "Rơ Chăm Mai", "K'Ly", "Siu Hồng", "A Nhiên"
        ] + female
    return male, female


def generate_member_name(rng: random.Random, gender: str, ethnicity: str) -> str:
    """Sinh ngẫu nhiên tên thành viên dựa trên giới tính và dân tộc."""
    male_pool, female_pool = member_name_pool(gender, ethnicity)
    if gender == "Nữ":
        return rng.choice(female_pool)
    return rng.choice(male_pool)


def relationship_for_member(age: int, member_index: int, host_age: int, rng: random.Random) -> str:
    """
    Xác định mối quan hệ của thành viên với chủ hộ dựa trên tuổi tác.
    
    Args:
        age (int): Tuổi thành viên.
        member_index (int): Thứ tự thành viên trong hộ.
        host_age (int): Tuổi chủ hộ.
        rng (random.Random): Bộ sinh số ngẫu nhiên.
        
    Returns:
        str: Tên quan hệ (Con, Vợ/chồng, Cháu, Bố/mẹ, v.v.).
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
    """Xác định trẻ em có bảo hiểm y tế hay không."""
    if is_poor:
        return rng.random() < 0.70
    if is_near_poor:
        return rng.random() < 0.78
    return rng.random() < 0.88


def choose_child_deprivation_flag(base_prob: float, rng: random.Random) -> bool:
    """Xác định cờ thiếu hụt của trẻ em."""
    return rng.random() < base_prob
