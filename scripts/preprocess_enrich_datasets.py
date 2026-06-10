# -*- coding: utf-8 -*-
"""
Module chứa các hàm tiền xử lý và làm sạch dữ liệu thô,
xử lý trùng lặp, chuẩn hóa ngày tháng, giới tính, địa lý cấp xã/thôn.
"""

from __future__ import annotations
import datetime as dt
import hashlib
import math
import random
import re
import unicodedata
from typing import Any
import numpy as np
import pandas as pd

# Các cột lõi để định danh duy nhất một hộ khảo sát ban đầu
CORE_COLUMNS = [
    "family.code",
    "family.hostName",
    "family.hostGender",
    "classify",
    "b1Point",
    "b2Point",
]

# Từ điển danh sách xã/phường mặc định cho từng huyện ở Đắk Nông
DISTRICT_COMMUNE_FALLBACK = {
    "Huyện Cư Jút": [
        "Thị trấn Ea T'ling", "Xã Chư K'nia", "Xã Đắk D'rông", "Xã Đắk Wil",
        "Xã Ea Po", "Xã Nam Dong", "Xã Tâm Thắng", "Xã Trúc Sơn"
    ],
    "Huyện Krông Nô": [
        "Thị trấn Đắk Mâm", "Xã Buôn Choáh", "Xã Đắk Drô", "Xã Đắk Nang",
        "Xã Đắk Sôr", "Xã Đức Xuyên", "Xã Nâm N'Đir", "Xã Nâm Nung",
        "Xã Quảng Phú", "Xã Tân Thành", "Xã Nam Xuân"
    ],
    "Huyện Tuy Đức": [
        "Xã Đắk Buk So", "Xã Đắk Ngo", "Xã Đắk R'Tih",
        "Xã Quảng Tâm", "Xã Quảng Trực", "Xã Đắk Huyền"
    ],
    "Huyện Đăk Glong": [
        "Xã Quảng Khê", "Xã Đắk Ha", "Xã Đắk Plao", "Xã Đắk R'Măng",
        "Xã Đắk Som", "Xã Quảng Sơn", "Xã Quảng Hòa"
    ],
    "Huyện Đắk Mil": [
        "Thị trấn Đắk Mil", "Xã Đắk Sắk", "Xã Đức Mạnh", "Xã Đắk Lao",
        "Xã Đức Minh", "Xã Đắk R'La", "Xã Đắk N'Drót", "Xã Long Sơn",
        "Xã Thuận An", "Xã Bản Kè"
    ],
    "Huyện Đắk RLấp": [
        "Thị trấn Kiến Đức", "Xã Đắk Ru", "Xã Đắk Wer", "Xã Đạo Nghĩa",
        "Xã Hưng Bình", "Xã Kiến Thành", "Xã Nghĩa Thắng", "Xã Nhân Cơ",
        "Xã Nhân Đạo", "Xã Quảng Tín"
    ],
    "Huyện Đắk Song": [
        "Thị trấn Đức An", "Xã Đắk Hòa", "Xã Đắk Mô", "Xã Đắk N'Drung",
        "Xã Nâm N'Jang", "Xã Thuận Hạnh", "Xã Thuận Hà", "Xã Trường Xuân",
        "Xã Quảng Hòa"
    ],
    "Thành phố Gia Nghĩa": [
        "Phường Nghĩa Đức", "Phường Nghĩa Thành", "Phường Nghĩa Phú",
        "Phường Nghĩa Trung", "Phường Nghĩa Tân", "Xã Đắk R'Moan",
        "Xã Đắk Nia", "Xã Quảng Thành"
    ],
}


def ensure_dir(path: Any) -> Any:
    """Đảm bảo thư mục tồn tại, nếu chưa có thì tạo mới."""
    from pathlib import Path
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def strip_accents(text: str) -> str:
    """Loại bỏ dấu tiếng Việt khỏi chuỗi văn bản."""
    if text is None:
        return ""
    text = unicodedata.normalize("NFKD", str(text))
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def normalize_key(text: str) -> str:
    """Chuẩn hóa khóa chuỗi (không dấu, viết thường, không ký tự đặc biệt)."""
    text = strip_accents(text).lower()
    text = re.sub(r"[^a-z0-9]+", "", text)
    return text


def normalize_no_space(text: str) -> str:
    """Loại bỏ mọi khoảng trắng và chuẩn hóa chuỗi không dấu."""
    return re.sub(r"\s+", "", strip_accents(str(text)).lower())


def clean_text(value: Any) -> str | None:
    """Làm sạch khoảng trắng thừa và chuẩn hóa NaN/None về None."""
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return None
    return text


def clean_code(value: Any) -> str | None:
    """Làm sạch mã hộ gia đình, bỏ phần đuôi .0 của số thực nếu có."""
    text = clean_text(value)
    if text is None:
        return None
    text = text.replace("\u00a0", " ")
    text = text.strip()
    if text.endswith(".0"):
        try:
            num = int(float(text))
            return str(num)
        except Exception:
            text = text[:-2]
    if text.endswith(".") and re.fullmatch(r"\d+\.", text):
        return text[:-1]
    if re.fullmatch(r"\d+\.0", text):
        return str(int(float(text)))
    return text


def parse_int(value: Any, default: int = 1) -> int:
    """Chuyển đổi giá trị bất kỳ sang số nguyên hợp lệ, có giá trị mặc định."""
    if value is None:
        return default
    if isinstance(value, (int, np.integer)):
        return max(default, int(value))
    if isinstance(value, float) and not math.isnan(value):
        return max(default, int(value))
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return default
    text = text.replace(",", ".")
    try:
        return max(default, int(float(text)))
    except Exception:
        digits = re.findall(r"\d+", text)
        if digits:
            return max(default, int(digits[0]))
        return default


def parse_float(value: Any, default: float = 0.0) -> float:
    """Chuyển đổi giá trị bất kỳ sang số thực hợp lệ."""
    if value is None:
        return default
    if isinstance(value, (int, float, np.number)):
        return float(value)
    text = str(value).strip().replace(",", ".")
    try:
        return float(text)
    except Exception:
        return default


def stable_seed(*parts: Any) -> int:
    """Tạo seed số nguyên ổn định từ các chuỗi/giá trị đầu vào."""
    joined = "|".join("" if p is None else str(p) for p in parts)
    digest = hashlib.sha256(joined.encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def rng_for(*parts: Any) -> random.Random:
    """Trả về bộ sinh số ngẫu nhiên Random độc lập dựa trên stable_seed."""
    return random.Random(stable_seed(*parts))


def normalize_yes_no(value: Any) -> str:
    """Chuẩn hóa giá trị Có/Không về dạng chuẩn 'Có' hoặc 'Không'."""
    text = clean_text(value)
    if text is None:
        return "Không"
    lowered = strip_accents(text).lower().strip()
    true_values = {"co", "có", "1", "true", "yes", "y", "t"}
    false_values = {"khong", "không", "0", "false", "no", "n", "f"}
    if lowered in true_values:
        return "Có"
    if lowered in false_values:
        return "Không"
    if "co" == lowered or lowered.startswith("co "):
        return "Có"
    if "khong" == lowered or lowered.startswith("khong "):
        return "Không"
    return "Không"


def normalize_gender(value: Any, name: str | None = None, rng: random.Random | None = None) -> str:
    """
    Chuẩn hóa giới tính dựa trên giá trị gốc hoặc tên của chủ hộ.
    
    Args:
        value (Any): Giới tính gốc.
        name (str | None): Tên chủ hộ để đoán giới tính nếu thiếu.
        rng (random.Random | None): Bộ sinh số ngẫu nhiên.
        
    Returns:
        str: 'Nam' hoặc 'Nữ'.
    """
    text = clean_text(value)
    if text is not None:
        lowered = strip_accents(text).lower()
        if lowered.startswith("nam") or lowered in {"m", "male"}:
            return "Nam"
        if lowered.startswith("nu") or lowered.startswith("nữ") or lowered in {"f", "female"}:
            return "Nữ"
    if name:
        female_tokens = ["thi", "thị", "ngoc", "ngọc", "hương", "huong", "anh", "lan", "mai", "ly", "le", "lệ", "nga", "hoa", "hồng", "hong"]
        male_tokens = ["van", "văn", "duc", "đức", "quang", "tuan", "tùng", "tung", "hieu", "hiếu", "minh", "dung", "hoang", "hùng", "hung"]
        normalized_name = strip_accents(name).lower()
        female_score = sum(1 for tok in female_tokens if tok in normalized_name)
        male_score = sum(1 for tok in male_tokens if tok in normalized_name)
        if female_score > male_score:
            return "Nữ"
        if male_score > female_score:
            return "Nam"
    if rng is None:
        rng = random.Random()
    return "Nam" if rng.random() < 0.5 else "Nữ"


def parse_date_value(value: Any) -> dt.date | None:
    """Phân tích linh hoạt các kiểu chuỗi ngày tháng sang dt.date."""
    text = clean_text(value)
    if text is None:
        return None
    candidates = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"]
    for fmt in candidates:
        try:
            return dt.datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    parsed = pd.to_datetime(text, dayfirst=True, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.date()


def format_date(date_value: dt.date | None) -> str | None:
    """Định dạng ngày dt.date sang dạng chuẩn chuỗi YYYY-MM-DD."""
    if date_value is None:
        return None
    return date_value.strftime("%Y-%m-%d")


def set_year(date_value: dt.date | None, year: int) -> dt.date | None:
    """Thiết lập lại năm của ngày tháng, giữ nguyên ngày/tháng."""
    if date_value is None:
        return None
    try:
        return dt.date(year, date_value.month, date_value.day)
    except ValueError:
        return None


def maybe_random_date(year: int, rng: random.Random) -> str:
    """Tạo ngẫu nhiên ngày khảo sát cho năm tương ứng."""
    from scripts.legal_rules import DATE_OPTIONS_2023, DATE_OPTIONS_2024
    if year == 2023:
        return rng.choice(DATE_OPTIONS_2023)
    return rng.choice(DATE_OPTIONS_2024)


def is_header_row(row: pd.Series) -> bool:
    """Kiểm tra xem dòng dữ liệu có phải là dòng tiêu đề lặp lại trong file Excel không."""
    classify = clean_text(row.get("classify"))
    host = clean_text(row.get("family.hostName"))
    date_val = clean_text(row.get("date"))
    return classify == "Kết quả rà soát" or host == "Chủ hộ" or date_val == "Thời gian rà soát"


def resolve_district_communes(district_name: str, commune_mapping: dict[str, list[str]] | None = None) -> list[str]:
    """Trả về danh sách xã của huyện."""
    source = commune_mapping or DISTRICT_COMMUNE_FALLBACK
    if district_name in source:
        return source[district_name]
    normalized = normalize_key(district_name)
    for key, communes in source.items():
        if normalize_key(key) == normalized:
            return communes
    return []


def weighted_choice(rng: random.Random, weighted_items: list[tuple[Any, float]]) -> Any:
    """Chọn ngẫu nhiên một phần tử theo phân bổ trọng số."""
    total = sum(max(0.0, w) for _, w in weighted_items)
    if total <= 0:
        return weighted_items[0][0]
    pick = rng.random() * total
    cumulative = 0.0
    for item, weight in weighted_items:
        cumulative += max(0.0, weight)
        if pick <= cumulative:
            return item
    return weighted_items[-1][0]


def choose_from_weights(rng: random.Random, values: list[Any], weights: list[float]) -> Any:
    """Chọn ngẫu nhiên một phần tử từ danh sách các giá trị và danh sách trọng số tương ứng."""
    return weighted_choice(rng, list(zip(values, weights)))


def assign_communes(communes: list[str], n: int, rng: random.Random) -> list[str]:
    """Phân bổ ngẫu nhiên xã/phường cho danh sách n phần tử."""
    if not communes:
        return [None] * n
    if n <= len(communes):
        ordered = communes[:]
        rng.shuffle(ordered)
        return ordered[:n]
    base = communes[:]
    rng.shuffle(base)
    repeated: list[str] = []
    while len(repeated) < n:
        chunk = base[:]
        rng.shuffle(chunk)
        repeated.extend(chunk)
    return repeated[:n]


def assign_village_or_group(rng: random.Random) -> str:
    """Chọn ngẫu nhiên một thôn/bon/tổ dân phố."""
    return rng.choice([
        "Thôn 1", "Thôn 2", "Thôn 3", "Bon 1", "Bon 2",
        "Tổ dân phố 1", "Tổ dân phố 2"
    ])


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Làm sạch khoảng trắng cột và chuỗi văn bản của tất cả các ô trong dataframe."""
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    for col in df.columns:
        df[col] = df[col].map(clean_text)
    return df


def remove_header_rows(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Loại bỏ các dòng tiêu đề trùng lặp lẫn trong dữ liệu."""
    if df.empty:
        return df, 0
    mask = df.apply(is_header_row, axis=1)
    removed = int(mask.sum())
    return df.loc[~mask].reset_index(drop=True), removed


def normalize_raw_core_values(df: pd.DataFrame) -> pd.DataFrame:
    """Chuẩn hóa sơ bộ các cột dữ liệu chính."""
    df = df.copy()
    for col in ["family.hostName", "family.coDanTocTaiCho", "family.hostGender", "quickReview.result", "classify", "reviewer"]:
        if col in df.columns:
            df[col] = df[col].map(clean_text)
    if "family.code" in df.columns:
        df["family.code"] = df["family.code"].map(clean_code)
    if "family.numberOfMembers" in df.columns:
        df["family.numberOfMembers"] = df["family.numberOfMembers"].map(lambda x: parse_int(x, default=1))
    if "b1Point" in df.columns:
        df["b1Point"] = df["b1Point"].map(lambda x: clean_text(x))
    if "b2Point" in df.columns:
        df["b2Point"] = df["b2Point"].map(lambda x: clean_text(x))
    return df


def deduplicate_core_rows(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Loại bỏ trùng lặp tuyệt đối của các dòng dữ liệu dựa trên các cột lõi."""
    dup_mask = df.duplicated(subset=CORE_COLUMNS, keep="first")
    removed = int(dup_mask.sum())
    return df.loc[~dup_mask].reset_index(drop=True), removed


def fix_duplicate_family_codes(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """
    Sửa các mã hộ bị trùng lặp bằng cách thêm hậu tố _DUP001, _DUP002,...
    
    Args:
        df (pd.DataFrame): Dataframe đầu vào.
        
    Returns:
        tuple[pd.DataFrame, int]: (df_đã_sửa, số_lượng_thay_đổi)
    """
    df = df.copy()
    df["processing.original_family_code"] = df["family.code"]
    df["processing.family_code_was_changed"] = False
    df["processing.duplicate_code_group_size"] = 1
    df["processing.note"] = ""
    changed = 0
    grouped = df.groupby("processing.original_family_code", dropna=False, sort=False)
    for code, idxs in grouped.indices.items():
        idx_list = list(idxs)
        if len(idx_list) <= 1:
            continue
        group_size = len(idx_list)
        df.loc[idx_list, "processing.duplicate_code_group_size"] = group_size
        for suffix_idx, pos in enumerate(idx_list[1:], start=1):
            new_code = f"{code}_DUP{suffix_idx:03d}"
            df.at[pos, "family.code"] = new_code
            df.at[pos, "processing.family_code_was_changed"] = True
            df.at[pos, "processing.note"] = "duplicate_family_code_suffix_applied"
            changed += 1
        df.at[idx_list[0], "processing.note"] = "duplicate_family_code_group_kept"
    return df, changed


def normalize_dates_for_year(
    df: pd.DataFrame,
    year: int,
    district: str,
    seed: int,
) -> pd.DataFrame:
    """
    Chuẩn hóa cột ngày tháng của dataframe theo năm rà soát tương ứng.
    
    Args:
        df (pd.DataFrame): Dataframe.
        year (int): Năm rà soát (2023 hoặc 2024).
        district (str): Tên huyện.
        seed (int): Hạt giống ngẫu nhiên.
        
    Returns:
        pd.DataFrame: Dataframe đã chuẩn hóa ngày.
    """
    from scripts.legal_rules import DATE_OPTIONS_BY_YEAR
    df = df.copy()
    original = df["date"].copy()
    normalized: list[str] = []
    changed_flags: list[bool] = []
    filled_flags: list[bool] = []
    sources: list[str] = []
    for value in original.tolist():
        parsed = parse_date_value(value)
        row_idx = len(normalized)
        row_rng = rng_for(seed, "date", year, district, row_idx, df.iloc[row_idx].get("family.code"))
        candidate_dates = DATE_OPTIONS_BY_YEAR.get(year, ["2023-10-15"])
        if parsed is not None and parsed.year == year:
            new_date = format_date(parsed)
            changed = format_date(parsed) != clean_text(value)
            filled = False
            source = "cleaned_original"
        else:
            new_date = row_rng.choice(candidate_dates)
            changed = True
            filled = True
            source = "filled_from_legal_period_rule"
        normalized.append(new_date)
        changed_flags.append(changed)
        filled_flags.append(filled)
        sources.append(source)
    df["processing.original_date"] = original.map(clean_text)
    df["processing.source.date"] = sources
    df["processing.date_was_filled"] = filled_flags
    df["date"] = normalized
    df["processing.date_was_normalized"] = changed_flags
    df["administrative.year"] = year
    return df


def normalize_co_dan_toc(df: pd.DataFrame) -> pd.DataFrame:
    """Chuẩn hóa cột gia đình có dân tộc tại chỗ."""
    df = df.copy()
    df["family.coDanTocTaiCho"] = df["family.coDanTocTaiCho"].map(normalize_yes_no)
    df["family.isDTTC"] = df["family.coDanTocTaiCho"].eq("Có")
    return df


def normalize_host_gender(df: pd.DataFrame, district: str, year: int, seed: int) -> pd.DataFrame:
    """Chuẩn hóa giới tính của chủ hộ dựa trên giới tính gốc và tên chủ hộ."""
    df = df.copy()
    genders = []
    for idx, row in df.iterrows():
        rng = rng_for(seed, "gender", year, district, idx, row.get("family.code"), row.get("family.hostName"))
        genders.append(normalize_gender(row.get("family.hostGender"), row.get("family.hostName"), rng))
    df["family.hostGender"] = genders
    return df


def assign_hierarchy(df: pd.DataFrame, year: int, district: str, seed: int, commune_mapping: dict[str, list[str]] | None = None) -> pd.DataFrame:
    """Phân bổ ngẫu nhiên thông tin hành chính xã và thôn/bon cho từng hộ gia đình."""
    df = df.copy()
    communes = resolve_district_communes(district, commune_mapping)
    rng = rng_for(seed, "communes", year, district, len(df))
    df["administrative.province"] = "Đắk Nông"
    df["administrative.district"] = district
    df["administrative.commune"] = assign_communes(communes, len(df), rng)
    df["administrative.village_or_group"] = [assign_village_or_group(rng_for(seed, "village", year, district, i, code)) for i, code in enumerate(df["family.code"].tolist(), start=1)]
    return df
