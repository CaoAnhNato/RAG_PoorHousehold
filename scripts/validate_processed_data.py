# -*- coding: utf-8 -*-
"""
Module thực hiện kiểm định chất lượng dữ liệu sau khi được xử lý bởi pipeline.
Kiểm tra tính toàn vẹn của mã hộ, điểm số B1/B2, tính nhất quán của phân loại hộ đa chiều
theo chuẩn nghèo giai đoạn 2021-2025, các kiểm tra Null/NaN và độ bao phủ cột.
"""

from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from typing import Any
import pandas as pd

from scripts.preprocess_enrich_datasets import (
    clean_text,
    parse_int,
    parse_date_value,
)
from scripts.legal_rules import (
    resolve_classification_from_scores,
    DATE_OPTIONS_BY_YEAR,
)
from scripts.export_metadata import REPORT_SPECS

# Cột lõi sử dụng để kiểm tra trùng lặp
CORE_COLUMNS = [
    "date",
    "family.hostName",
    "family.code",
    "family.coDanTocTaiCho",
    "family.hostGender",
    "family.numberOfMembers",
    "quickReview.result",
    "b1Point",
    "b2Point",
    "classify",
]

# Cột đầu vào cơ sở bắt buộc
BASE_INPUT_COLUMNS = [
    "date",
    "family.hostName",
    "family.code",
    "family.coDanTocTaiCho",
    "family.hostGender",
    "family.numberOfMembers",
    "quickReview.result",
    "b1Point",
    "b2Point",
    "classify",
    "reviewer",
]


def ensure_dir(path: Path) -> Path:
    """
    Đảm bảo thư mục cha tồn tại.
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_validation_workbook(path: Path, sheets: dict[str, pd.DataFrame]) -> None:
    """
    Ghi kết quả kiểm định dữ liệu ra các sheet của tệp Excel.
    
    Args:
        path (Path): Đường dẫn tệp Excel đầu ra.
        sheets (dict[str, pd.DataFrame]): Bản đồ tên sheet -> DataFrame dữ liệu kiểm định.
    """
    ensure_dir(path.parent)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for sheet_name, df in sheets.items():
            df.to_excel(writer, index=False, sheet_name=sheet_name)


def write_dataframe_to_excel(df: pd.DataFrame, path: Path, sheet_name: str) -> None:
    """
    Ghi một DataFrame ra file Excel với tên sheet được chỉ định.
    
    Args:
        df (pd.DataFrame): DataFrame dữ liệu.
        path (Path): Đường dẫn ghi file.
        sheet_name (str): Tên sheet trong file Excel.
    """
    ensure_dir(path.parent)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)


def build_column_coverage(processed_df: pd.DataFrame, member_df: pd.DataFrame) -> pd.DataFrame:
    """
    Xây dựng báo cáo về độ bao phủ của các cột so với 15 cấu hình biểu mẫu báo cáo Excel.
    
    Args:
        processed_df (pd.DataFrame): DataFrame của hộ gia đình sau xử lý.
        member_df (pd.DataFrame): DataFrame của thành viên hộ gia đình sau xử lý.
        
    Returns:
        pd.DataFrame: DataFrame tóm tắt độ bao phủ cột.
    """
    rows = []
    processed_columns = set(processed_df.columns)
    member_columns = set(member_df.columns)
    for spec in REPORT_SPECS:
        for column in spec["required_columns"]:
            exists = column in processed_columns or column in member_columns
            if column.startswith("member."):
                source = "member_file"
            elif (
                column.startswith("children.")
                or column.startswith("deprivation.")
                or column.startswith("reason.")
                or column.startswith("support.")
                or column.startswith("transition.")
                or (column.startswith("family.") and column not in BASE_INPUT_COLUMNS)
            ):
                source = "generated"
            else:
                source = "original"
            rows.append(
                {
                    "report_id": spec["report_id"],
                    "report_name": spec["report_name"],
                    "required_column": column,
                    "exists_in_processed_dataset": bool(exists),
                    "source_type": source,
                    "note": spec["notes"].get(column, ""),
                }
            )
    return pd.DataFrame(rows)


def validate_processed_outputs(
    output_root: Path,
    mapping: dict[str, list[str]],
) -> tuple[dict[str, Any], pd.DataFrame, pd.DataFrame, pd.DataFrame, list[dict[str, Any]]]:
    """
    Thực hiện kiểm định chi tiết toàn bộ dữ liệu đã được lưu trong thư mục Processed.
    
    Args:
        output_root (Path): Thư mục chứa dữ liệu đầu ra Processed/
        mapping (dict[str, list[str]]): Ánh xạ địa bàn hành chính quận/huyện -> danh sách xã/phường.
        
    Returns:
        tuple: (validation_frames, file_level_df, null_checks_df, aggregate_df, warnings)
    """
    file_level_rows: list[dict[str, Any]] = []
    aggregate_rows: list[dict[str, Any]] = []
    null_rows: list[dict[str, Any]] = []
    legal_rows: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    dep_cols = [
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
    ]
    reason_cols = [
        "reason.lackProductionLand",
        "reason.lackCapital",
        "reason.lackLabor",
        "reason.lackProductionTools",
        "reason.lackProductionKnowledge",
        "reason.lackLaborSkill",
        "reason.illnessOrAccident",
        "reason.other",
    ]
    support_cols = [
        "support.health",
        "support.education",
        "support.production",
        "support.credit",
        "support.housing",
        "support.other",
    ]

    for year in [2023, 2024]:
        year_dir = output_root / str(year)
        if not year_dir.exists():
            continue
        for path in sorted(year_dir.glob("*.xlsx")):
            if path.name.startswith("~$"):
                continue
            df = pd.read_excel(path, sheet_name="Data", engine="openpyxl", dtype=object)
            district = path.stem
            commune_allowed = set(mapping.get(district, []))
            member_path = output_root / str(year) / "_members" / f"{district}_members.xlsx"
            member_df = (
                pd.read_excel(member_path, sheet_name="Members", engine="openpyxl", dtype=object)
                if member_path.exists()
                else pd.DataFrame()
            )

            # Hàm con kiểm tra null
            def _null_counts(frame: pd.DataFrame, file_type: str) -> None:
                for column in frame.columns:
                    series = frame[column]
                    null_count = int(series.isna().sum())
                    blank_count = int(series.map(lambda x: isinstance(x, str) and x.strip() == "").sum())
                    if null_count or blank_count:
                        null_rows.append(
                            {
                                "year": year,
                                "district": district,
                                "file_type": file_type,
                                "column": column,
                                "null_count": null_count,
                                "blank_count": blank_count,
                                "total_issues": null_count + blank_count,
                                "severity": "high" if null_count + blank_count > 0 else "info",
                            }
                        )

            _null_counts(df, "household")
            if not member_df.empty:
                _null_counts(member_df, "member")

            # Kiểm tra trùng lặp
            core_dup = (
                int(df.duplicated(subset=[c for c in CORE_COLUMNS if c in df.columns]).sum())
                if all(c in df.columns for c in CORE_COLUMNS)
                else 0
            )
            code_dup = int(df.duplicated(subset=["family.code"]).sum()) if "family.code" in df.columns else 0

            # Kiểm tra ngày tháng
            date_parsed = df["date"].map(parse_date_value) if "date" in df.columns else pd.Series([None] * len(df))
            date_year_bad = int(date_parsed.map(lambda d: d is None or d.year != year).sum())
            candidate_dates = set(DATE_OPTIONS_BY_YEAR.get(year, ["2023-10-15"]))
            
            date_filled_bad = int(
                (
                    (df.get("processing.date_was_filled", pd.Series([False] * len(df))).fillna(False).astype(bool))
                    & (~df.get("date", pd.Series([""] * len(df))).astype(str).isin(candidate_dates))
                ).sum()
            )

            # Kiểm tra phân loại hành chính
            missing_commune = (
                int(df["administrative.commune"].isna().sum()) if "administrative.commune" in df.columns else len(df)
            )
            commune_outside = (
                int((~df["administrative.commune"].isin(commune_allowed)).sum())
                if commune_allowed and "administrative.commune" in df.columns
                else 0
            )
            area_null = (
                int(df["administrative.areaType"].isna().sum()) if "administrative.areaType" in df.columns else len(df)
            )
            
            # Kiểm tra điểm số
            b1_null = int(df["b1Point"].isna().sum()) if "b1Point" in df.columns else len(df)
            b2_null = int(df["b2Point"].isna().sum()) if "b2Point" in df.columns else len(df)
            dep_total_null = (
                int(df["deprivation.totalCount"].isna().sum()) if "deprivation.totalCount" in df.columns else len(df)
            )
            family_number_null = (
                int(df["family.numberOfMembers"].isna().sum()) if "family.numberOfMembers" in df.columns else len(df)
            )
            reviewer_null = int(df["reviewer"].isna().sum()) if "reviewer" in df.columns else len(df)
            quick_review_bad = (
                int((df["quickReview.result"] == "--").sum()) if "quickReview.result" in df.columns else len(df)
            )

            # Tính nhất quán pháp lý B2 = deprivation.totalCount * 10
            expected_dep_total = (
                df[dep_cols].fillna(False).astype(bool).sum(axis=1)
                if all(col in df.columns for col in dep_cols)
                else pd.Series([0] * len(df))
            )
            dep_total_bad = (
                int((df["deprivation.totalCount"].fillna(0).astype(int) != expected_dep_total.astype(int)).sum())
                if "deprivation.totalCount" in df.columns
                else len(df)
            )
            b2_total_bad = (
                int(
                    (
                        df["b2Point"].fillna(0).astype(int)
                        != (df["deprivation.totalCount"].fillna(0).astype(int) * 10)
                    ).sum()
                )
                if "b2Point" in df.columns and "deprivation.totalCount" in df.columns
                else len(df)
            )

            # Tính nhất quán phân loại hộ (classify) dựa trên điểm B1 và tổng thiếu hụt
            expected_classify = pd.Series(
                [
                    resolve_classification_from_scores(parse_int(b1, 0), parse_int(dep, 0), area)
                    for b1, dep, area in zip(
                        df.get("b1Point", pd.Series([0] * len(df))),
                        df.get("deprivation.totalCount", pd.Series([0] * len(df))),
                        df.get("administrative.areaType", pd.Series(["rural"] * len(df))),
                    )
                ]
            )
            final_classify = (
                df["classify.final"]
                if "classify.final" in df.columns
                else df.get("classify", pd.Series(["Hộ không nghèo"] * len(df)))
            )
            classification_bad = int((final_classify.astype(str) != expected_classify.astype(str)).sum())

            # Kiểm tra nhất quán Dân tộc
            dtts_bad = int(
                (
                    df.get("family.isDTTS", pd.Series([False] * len(df))).fillna(False).astype(bool)
                    & (df.get("family.ethnicity", pd.Series([""] * len(df))).astype(str) == "Kinh")
                ).sum()
            )
            kinh_bad = int(
                (
                    (df.get("family.ethnicity", pd.Series([""] * len(df))).astype(str) == "Kinh")
                    & df.get("family.isDTTS", pd.Series([False] * len(df))).fillna(False).astype(bool)
                ).sum()
            )
            dttc_bad = int(
                (
                    df.get("family.isDTTC", pd.Series([False] * len(df))).fillna(False).astype(bool)
                    & (~df.get("family.isDTTS", pd.Series([False] * len(df))).fillna(False).astype(bool))
                ).sum()
            )

            # Kiểm tra thông tin Trẻ em
            children_total = df.get("children.totalCount", pd.Series([0] * len(df))).fillna(0).astype(int)
            family_members = df.get("family.numberOfMembers", pd.Series([0] * len(df))).fillna(0).astype(int)
            children_bad = int((children_total > family_members).sum())
            child_dep_bad = int(
                (
                    (df.get("children.lackHealthInsuranceCount", pd.Series([0] * len(df))).fillna(0).astype(int) > children_total)
                    | (df.get("children.nutritionDeprivedCount", pd.Series([0] * len(df))).fillna(0).astype(int) > children_total)
                    | (df.get("children.schoolAttendanceDeprivedCount", pd.Series([0] * len(df))).fillna(0).astype(int) > children_total)
                ).sum()
            )

            # Kiểm tra nguyên nhân nghèo & chính sách hỗ trợ
            reason_required_bad = (
                int(
                    (
                        (final_classify.isin(["Hộ nghèo", "Hộ cận nghèo"]))
                        & (df[reason_cols].fillna(False).astype(bool).sum(axis=1) == 0)
                    ).sum()
                )
                if all(col in df.columns for col in reason_cols)
                else 0
            )
            
            support_bad = 0
            if all(col in df.columns for col in support_cols):
                expected_support = []
                for _, row in df.iterrows():
                    poor_or_near = row.get("classify.final") in {"Hộ nghèo", "Hộ cận nghèo"}
                    health = bool(row.get("deprivation.healthInsurance")) or parse_int(row.get("children.lackHealthInsuranceCount"), 0) > 0
                    education = parse_int(row.get("children.schoolAttendanceDeprivedCount"), 0) > 0
                    production = (
                        bool(row.get("reason.lackProductionLand"))
                        or bool(row.get("reason.lackProductionTools"))
                        or bool(row.get("reason.lackProductionKnowledge"))
                    )
                    credit = bool(row.get("reason.lackCapital"))
                    housing = bool(row.get("deprivation.housingQuality")) or bool(row.get("deprivation.housingArea"))
                    other = poor_or_near and not any([health, education, production, credit, housing])
                    expected_support.append(
                        [
                            health if poor_or_near else False,
                            education if poor_or_near else False,
                            production if poor_or_near else False,
                            credit if poor_or_near else False,
                            housing if poor_or_near else False,
                            other if poor_or_near else False,
                        ]
                    )
                expected_support_df = pd.DataFrame(expected_support, columns=support_cols)
                support_bad = int((df[support_cols].fillna(False).astype(bool).ne(expected_support_df)).any(axis=1).sum())

            # Kiểm tra biến động
            transition_bad = int(
                (df.get("transition.endingClassify", pd.Series([""] * len(df))).astype(str) != final_classify.astype(str)).sum()
            )

            # Kiểm tra tệp thành viên (Members)
            member_total_bad = 0
            host_bad = 0
            if not member_df.empty and "family.code" in member_df.columns:
                member_group_sizes = member_df.groupby("family.code").size().to_dict()
                for _, row in df.iterrows():
                    code = str(row.get("family.code"))
                    expected_size = parse_int(row.get("family.numberOfMembers"), 0)
                    actual_size = int(member_group_sizes.get(code, 0))
                    if expected_size != actual_size:
                        member_total_bad += 1
                if "family.hostName" in member_df.columns:
                    host_set = set(
                        member_df.loc[
                            member_df.get("member.isHost", pd.Series([False] * len(member_df))).fillna(False).astype(bool),
                            "family.hostName",
                        ].astype(str)
                    )
                    host_bad = int((~df["family.hostName"].astype(str).isin(host_set)).sum()) if "family.hostName" in df.columns else 0
            else:
                member_total_bad = len(df)

            # Ghi nhận kết quả file level
            file_level_rows.append(
                {
                    "year": year,
                    "district": district,
                    "input_rows": len(df),
                    "rows_after_core_dedup": len(df),
                    "core_duplicates_removed": 0,
                    "duplicate_family_codes_fixed": int(
                        df.get("processing.family_code_was_changed", pd.Series([False] * len(df)))
                        .fillna(False)
                        .astype(bool)
                        .sum()
                    ),
                    "output_rows": len(df),
                    "output_file": str(path),
                }
            )

            # Phân tách tổng hợp theo địa bàn xã/phường
            for commune, group in df.groupby("administrative.commune", dropna=False):
                aggregate_rows.append(
                    {
                        "year": year,
                        "district": district,
                        "commune": commune,
                        "poor_households": int((group["classify.final"] == "Hộ nghèo").sum()) if "classify.final" in group.columns else 0,
                        "near_poor_households": int((group["classify.final"] == "Hộ cận nghèo").sum()) if "classify.final" in group.columns else 0,
                        "poor_members": int(group.loc[group["classify.final"] == "Hộ nghèo", "family.numberOfMembers"].fillna(0).astype(int).sum()) if "classify.final" in group.columns else 0,
                        "near_poor_members": int(group.loc[group["classify.final"] == "Hộ cận nghèo", "family.numberOfMembers"].fillna(0).astype(int).sum()) if "classify.final" in group.columns else 0,
                        "dtts_households": int(group["family.isDTTS"].fillna(False).astype(bool).sum()) if "family.isDTTS" in group.columns else 0,
                        "dttc_households": int(group["family.isDTTC"].fillna(False).astype(bool).sum()) if "family.isDTTC" in group.columns else 0,
                        "no_labor_capacity_households": int(group["family.hasNoLaborCapacity"].fillna(False).astype(bool).sum()) if "family.hasNoLaborCapacity" in group.columns else 0,
                        "revolution_merit_policy_households": int(group["family.hasRevolutionMeritPolicy"].fillna(False).astype(bool).sum()) if "family.hasRevolutionMeritPolicy" in group.columns else 0,
                        "deprivation_total_poor": int(group.loc[group["classify.final"] == "Hộ nghèo", "deprivation.totalCount"].fillna(0).astype(int).sum()) if "classify.final" in group.columns else 0,
                        "deprivation_total_near_poor": int(group.loc[group["classify.final"] == "Hộ cận nghèo", "deprivation.totalCount"].fillna(0).astype(int).sum()) if "classify.final" in group.columns else 0,
                        "children_poor_total": int(group.loc[group["classify.final"] == "Hộ nghèo", "children.totalCount"].fillna(0).astype(int).sum()) if "classify.final" in group.columns else 0,
                        "children_near_poor_total": int(group.loc[group["classify.final"] == "Hộ cận nghèo", "children.totalCount"].fillna(0).astype(int).sum()) if "classify.final" in group.columns else 0,
                    }
                )

            # Ghi nhận kết quả kiểm định pháp lý (legal consistency)
            legal_rows.append(
                {
                    "year": year,
                    "district": district,
                    "core_duplicates": core_dup,
                    "code_duplicates": code_dup,
                    "date_year_bad": date_year_bad,
                    "date_filled_bad": date_filled_bad,
                    "missing_commune": missing_commune,
                    "commune_outside": commune_outside,
                    "area_null": area_null,
                    "b1_null": b1_null,
                    "b2_null": b2_null,
                    "deprivation_total_null": dep_total_null,
                    "b2_total_bad": b2_total_bad,
                    "deprivation_sum_bad": dep_total_bad,
                    "classification_bad": classification_bad,
                    "dtts_bad": dtts_bad,
                    "kinh_bad": kinh_bad,
                    "dttc_bad": dttc_bad,
                    "children_bad": children_bad,
                    "child_dep_bad": child_dep_bad,
                    "member_total_bad": member_total_bad,
                    "host_bad": host_bad,
                    "reason_required_bad": reason_required_bad,
                    "support_bad": support_bad,
                    "transition_bad": transition_bad,
                    "reviewer_null": reviewer_null,
                    "quick_review_bad": quick_review_bad,
                    "family_number_null": family_number_null,
                    "severity": "high" if any(
                        [
                            core_dup,
                            code_dup,
                            date_year_bad,
                            date_filled_bad,
                            missing_commune,
                            commune_outside,
                            area_null,
                            b1_null,
                            b2_null,
                            dep_total_null,
                            b2_total_bad,
                            dep_total_bad,
                            classification_bad,
                            dtts_bad,
                            kinh_bad,
                            dttc_bad,
                            children_bad,
                            child_dep_bad,
                            member_total_bad,
                            host_bad,
                            reason_required_bad,
                            support_bad,
                            transition_bad,
                        ]
                    ) else "info",
                }
            )

            warnings.append(
                {
                    "warning_type": "validation_check",
                    "year": year,
                    "district": district,
                    "message": f"core_dup={core_dup}, code_dup={code_dup}, date_year_bad={date_year_bad}, date_filled_bad={date_filled_bad}, commune_outside={commune_outside}, area_null={area_null}, b1_null={b1_null}, b2_null={b2_null}, dep_total_bad={dep_total_bad}, classification_bad={classification_bad}, member_total_bad={member_total_bad}, host_bad={host_bad}, reason_required_bad={reason_required_bad}, support_bad={support_bad}, transition_bad={transition_bad}",
                    "severity": "info" if not any([core_dup, code_dup, date_year_bad, date_filled_bad, commune_outside, area_null, b1_null, b2_null, dep_total_bad, classification_bad, member_total_bad, host_bad, reason_required_bad, support_bad, transition_bad]) else "high",
                }
            )

    file_level_df = pd.DataFrame(file_level_rows)
    aggregate_df = pd.DataFrame(aggregate_rows)
    legal_consistency_df = pd.DataFrame(legal_rows)
    null_checks_df = pd.DataFrame(null_rows)
    
    # Báo cáo Column Coverage
    column_coverage_df = pd.DataFrame()
    if not file_level_df.empty:
        # Lấy file đầu tiên để tính column coverage đại diện
        sample_path = Path(file_level_rows[0]["output_file"])
        sample_df = pd.read_excel(sample_path, sheet_name="Data", engine="openpyxl", dtype=object)
        sample_member_path = sample_path.parent / "_members" / f"{sample_path.stem}_members.xlsx"
        sample_member_df = (
            pd.read_excel(sample_member_path, sheet_name="Members", engine="openpyxl", dtype=object)
            if sample_member_path.exists()
            else pd.DataFrame()
        )
        column_coverage_df = build_column_coverage(sample_df, sample_member_df)

    validation_frames = {
        "file_level_df": file_level_df,
        "aggregate_df": aggregate_df,
        "warnings_df": pd.DataFrame(warnings),
        "column_coverage_df": column_coverage_df,
        "legal_consistency_df": legal_consistency_df,
        "null_checks_df": null_checks_df,
    }
    return validation_frames, file_level_df, null_checks_df, aggregate_df, warnings


def parse_file_level_from_processing_log(log_path: Path) -> pd.DataFrame:
    """
    Phân tích log xử lý file level từ processing_log.json.
    
    Args:
        log_path (Path): Đường dẫn tệp log.
        
    Returns:
        pd.DataFrame: DataFrame tóm tắt thông tin các tệp đã xử lý.
    """
    if not log_path.exists():
        return pd.DataFrame()
    with open(log_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    rows = []
    for warning in data.get("warnings", []):
        if warning.get("warning_type") != "file_processed":
            continue
        message = warning.get("message", "")
        parsed = dict(re.findall(r"([a-z_]+)=([0-9]+)", message))
        rows.append(
            {
                "year": warning.get("year"),
                "district": warning.get("district"),
                "input_rows": int(parsed.get("input_rows", 0)),
                "rows_after_core_dedup": int(parsed.get("output_rows", 0)),
                "core_duplicates_removed": int(parsed.get("core_duplicates_removed", 0)),
                "duplicate_family_codes_fixed": int(parsed.get("duplicate_family_codes_fixed", 0)),
                "output_rows": int(parsed.get("output_rows", 0)),
                "output_file": str(Path("Processed") / str(warning.get("year")) / f"{warning.get('district')}.xlsx"),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    """
    Hàm thực thi chính khi gọi script từ dòng lệnh (CLI).
    """
    parser = argparse.ArgumentParser(description="Validate processed household datasets.")
    parser.add_argument("--input-root", default=".", help="Project root")
    parser.add_argument("--output-root", default="Processed", help="Output root")
    args = parser.parse_args()

    output_root = Path(args.output_root).resolve()
    mapping_path = output_root / "metadata" / "district_commune_mapping.json"
    if mapping_path.exists():
        with open(mapping_path, "r", encoding="utf-8") as f:
            mapping = json.load(f)
    else:
        mapping = {}
        
    log_path = output_root / "logs" / "processing_log.json"
    file_level_records = parse_file_level_from_processing_log(log_path)
    
    validation_frames, file_level_df, null_checks_df, aggregate_df, warnings = validate_processed_outputs(output_root, mapping)
    
    warnings_df = pd.DataFrame(warnings)
    
    write_validation_workbook(
        output_root / "logs" / "validation_summary.xlsx",
        {
            "File_Level": file_level_records if not file_level_records.empty else file_level_df,
            "Column_Coverage": validation_frames.get("column_coverage_df", pd.DataFrame()),
            "Legal_Consistency": validation_frames.get("legal_consistency_df", pd.DataFrame()),
            "Null_Checks": validation_frames.get("null_checks_df", pd.DataFrame()),
            "Aggregate_Checks": aggregate_df,
            "Warnings": warnings_df,
        },
    )
    print(f"Validated {len(file_level_df)} files, warnings={len(warnings)}")


if __name__ == "__main__":
    main()
