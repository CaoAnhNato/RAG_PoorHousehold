# -*- coding: utf-8 -*-
from __future__ import annotations
import pandas as pd

COLUMN_MAPPING = {
    "administrative.district": "Huyện",
    "administrative.commune": "Xã",
    "administrative.village_or_group": "Thôn/Bon",
    "administrative.year": "Năm",
    "family.hostName": "Chủ hộ",
    "family.hostGender": "Giới tính",
    "family.ethnicity": "Dân tộc",
    "family.numberOfMembers": "Số thành viên",
    "family.isDTTS": "Dân tộc thiểu số",
    "classify": "Loại hộ",
    "count_star()": "Số lượng",
    "count": "Số lượng",
    "total_households": "Tổng số hộ",
    "so_hogheo": "Số hộ nghèo",
    "so_ho_ngheo": "Số hộ nghèo",
    "numberOfPoorHouseholds": "Số hộ nghèo",
    "number_of_poor_households": "Số hộ nghèo",
    "poor_household_count": "Số hộ nghèo",
    "near_poor_household_count": "Số hộ cận nghèo",
    "deprivation.cleanWater": "Thiếu nước sạch",
    "deprivation.hygienicToilet": "Thiếu vệ sinh",
    "deprivation.totalCount": "Tổng chỉ số thiếu hụt"
}

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Chuẩn hoá tên cột của DataFrame sang tiếng Việt để hiển thị."""
    if df is None or df.empty:
        return df
    # Đổi tên nếu cột nằm trong mapping
    return df.rename(columns=COLUMN_MAPPING)
