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
    "family.isDTTC": "Hộ DTTC (thuộc DTTS)",
    "Hộ DTTC": "Hộ DTTC (thuộc DTTS)",
    "Hộ DT Tại chỗ": "Hộ DTTC (thuộc DTTS)",
    "Hộ dân tộc tại chỗ": "Hộ DTTC (thuộc DTTS)",
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

def prepare_chart_data(df: pd.DataFrame, user_question: str) -> pd.DataFrame:
    """Làm sạch và loại bỏ các cột không cần thiết trước khi vẽ biểu đồ."""
    if df is None or df.empty:
        return df
    
    # 1. Thay thế NaN/Null
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(0)
        else:
            df[col] = df[col].fillna("")
            
    # 2. Xác định cột năm để loại bỏ khỏi danh sách cột số thô (tránh vẽ tổng số nghìn hộ cạnh năm 2023/2024)
    # Tuy nhiên VẪN GIỮ lại cột năm trong df để LLM có thể đọc năm cho chart title (title=f'... năm {df["Năm"].iloc[0]}')
    year_cols = [c for c in df.columns if c.lower() in ["năm", "year", "administrative.year"]]
    for y_col in year_cols:
        # Chỉ drop nếu cột năm hoàn toàn rỗng/null, nếu có dữ liệu thì giữ nguyên để phục vụ metadata/facet
        if df[y_col].isnull().all():
            df = df.drop(columns=[y_col])
            
    # 3. Loại bỏ xung đột giữa cột Số lượng/Count và cột Tỷ lệ % (tránh vẽ thang đo 100% cạnh số nghìn hộ)
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    pct_cols = [c for c in num_cols if any(kw in str(c).lower() for kw in ["tỷ lệ", "%", "rate", "percent", "tỷ trọng", "ty le"])]
    count_cols = [c for c in num_cols if c not in pct_cols and c not in year_cols]
    
    q_lower = user_question.lower()
    asks_for_pct = any(kw in q_lower for kw in ["tỷ lệ", "%", "phần trăm", "tỷ trọng", "ty le", "cơ cấu"])
    
    if len(pct_cols) > 0 and len(count_cols) > 0:
        if asks_for_pct and len(pct_cols) >= 1:
            # Nếu hỏi tỷ lệ/cơ cấu, ưu tiên giữ cột tỷ lệ, loại bỏ cột số lượng thô
            df = df.drop(columns=count_cols, errors='ignore')
        else:
            # Nếu không hỏi tỷ lệ, loại bỏ cột tỷ lệ % để không vẽ chồng lấn lên biểu đồ số lượng
            df = df.drop(columns=pct_cols, errors='ignore')
            
    # 4. Loại bỏ cột Tổng (Summary/Total column) nếu có từ 2 cột thành phần trở lên
    rem_num_cols = [c for c in df.select_dtypes(include=['number']).columns if c not in year_cols]
    if len(rem_num_cols) >= 2:
        total_cols = [c for c in rem_num_cols if str(c).strip().lower().startswith(("tổng", "total", "tổng số", "tổng cộng")) or str(c).strip().lower() in ["tổng hộ", "tổng số hộ"]]
        if len(rem_num_cols) - len(total_cols) >= 1:
            df = df.drop(columns=total_cols, errors='ignore')
            
    return df
