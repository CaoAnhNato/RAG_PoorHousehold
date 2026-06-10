from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from scripts.inspect_report_templates import (
    BASE_INPUT_COLUMNS,
    DISTRICT_COMMUNE_FALLBACK,
    list_input_workbooks,
    read_input_workbook,
    sanitize_dataframe_columns,
    scan_report_templates,
)
from scripts.validate_processed_data import (
    build_column_coverage,
    validate_processed_outputs,
    write_validation_workbook,
    write_dataframe_to_excel,
    ensure_dir,
)
from scripts.export_metadata import (
    build_data_dictionary,
    build_report_schema_summary,
    build_required_columns_by_report,
)
from scripts.preprocess_enrich_datasets import (
    fix_duplicate_family_codes,
    normalize_co_dan_toc,
    normalize_host_gender,
    normalize_raw_core_values,
    normalize_dates_for_year,
    remove_header_rows,
    assign_hierarchy,
    deduplicate_core_rows,
    rng_for,
)
from scripts.generate_household_fields import (
    generate_household_features,
)
from scripts.legal_rules import (
    class_transition_label,
)


def process_file(
    input_path: Path,
    output_path: Path,
    year: int,
    district: str,
    commune_mapping: dict[str, list[str]],
    seed: int,
) -> tuple[pd.DataFrame, list[dict], dict]:
    raw_df = read_input_workbook(input_path)
    raw_df = sanitize_dataframe_columns(raw_df)
    raw_df = normalize_raw_core_values(raw_df)
    raw_df, removed_headers = remove_header_rows(raw_df)
    raw_df = normalize_raw_core_values(raw_df)

    dedup_df, removed_core = deduplicate_core_rows(raw_df)
    dedup_df["processing.duplicate_core_removed"] = False
    dedup_df["processing.duplicate_core_removed"] = True if removed_core else False
    dedup_df, changed_codes = fix_duplicate_family_codes(dedup_df)

    dedup_df = normalize_dates_for_year(dedup_df, year, district, seed)
    dedup_df = normalize_co_dan_toc(dedup_df)
    dedup_df = normalize_host_gender(dedup_df, district, year, seed)
    dedup_df = assign_hierarchy(dedup_df, year, district, seed, commune_mapping)
    dedup_df, members_rows = generate_household_features(dedup_df, year, district, seed)

    members_df = pd.DataFrame(members_rows)
    if not members_df.empty:
        members_file = output_path.parent / "_members" / f"{district}_members.xlsx"
        ensure_dir(members_file.parent)
        dedup_df["family.membersFile"] = str(members_file.relative_to(output_path.parents[1]))
        dedup_df["family.membersGenerated"] = True
    else:
        dedup_df["family.membersGenerated"] = False

    dedup_df = dedup_df[BASE_INPUT_COLUMNS + [c for c in dedup_df.columns if c not in BASE_INPUT_COLUMNS]]
    dedup_df = dedup_df.fillna("")

    if not members_df.empty:
        members_df = members_df.fillna("")
        write_dataframe_to_excel(members_df, output_path.parent / "_members" / f"{district}_members.xlsx", "Members")

    write_dataframe_to_excel(dedup_df, output_path, "Data")

    summary_warning = [
        {
            "warning_type": "file_processed",
            "year": year,
            "district": district,
            "message": f"input_rows={len(raw_df)+removed_headers}, removed_headers={removed_headers}, core_duplicates_removed={removed_core}, duplicate_family_codes_fixed={changed_codes}, output_rows={len(dedup_df)}",
            "severity": "info",
        }
    ]
    stats = {
        "input_rows": int(len(raw_df) + removed_headers),
        "removed_headers": int(removed_headers),
        "core_duplicates_removed": int(removed_core),
        "duplicate_family_codes_fixed": int(changed_codes),
        "output_rows": int(len(dedup_df)),
    }
    return dedup_df, summary_warning, stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Preprocess and enrich household datasets.")
    parser.add_argument("--input-root", default=".", help="Project root containing 2023/, 2024/, Format_Report/")
    parser.add_argument("--output-root", default="Processed", help="Output directory root")
    parser.add_argument("--seed", type=int, default=42, help="Base random seed")
    parser.add_argument("--legal-period", default="2021_2025", help="Legal period tag for metadata output")
    parser.add_argument("--fill-missing-values", default="true", help="Whether to fill missing values")
    parser.add_argument("--no-null-output", default="true", help="Require null-free output")
    args = parser.parse_args()

    input_root = Path(args.input_root).resolve()
    output_root = Path(args.output_root).resolve()
    ensure_dir(output_root)
    ensure_dir(output_root / "2023")
    ensure_dir(output_root / "2024")
    ensure_dir(output_root / "metadata")
    ensure_dir(output_root / "logs")
    ensure_dir(output_root / "2023" / "_members")
    ensure_dir(output_root / "2024" / "_members")

    report_schema_summary, commune_mapping, template_warnings = scan_report_templates(input_root)
    if not commune_mapping:
        commune_mapping = DISTRICT_COMMUNE_FALLBACK.copy()

    required_columns = build_required_columns_by_report()
    data_dictionary = build_data_dictionary()

    with open(output_root / "metadata" / "report_schema_summary.json", "w", encoding="utf-8") as f:
        json.dump(report_schema_summary, f, ensure_ascii=False, indent=2)
    with open(output_root / "metadata" / "district_commune_mapping.json", "w", encoding="utf-8") as f:
        json.dump(commune_mapping, f, ensure_ascii=False, indent=2)
    with open(output_root / "metadata" / "required_columns_by_report.json", "w", encoding="utf-8") as f:
        json.dump(required_columns, f, ensure_ascii=False, indent=2)
    with open(output_root / "metadata" / "data_dictionary.json", "w", encoding="utf-8") as f:
        json.dump(data_dictionary, f, ensure_ascii=False, indent=2)

    file_lists = list_input_workbooks(input_root)
    processed_frames = {2023: {}, 2024: {}}
    file_level_records = []
    warnings = template_warnings[:]

    # Process 2023 first so 2024 can look back for transition matching if needed.
    for year in [2023, 2024]:
        for input_path in file_lists.get(year, []):
            district = input_path.stem
            output_path = output_root / str(year) / input_path.name
            df, file_warnings, stats = process_file(input_path, output_path, year, district, commune_mapping, args.seed)
            processed_frames[year][district] = df
            warnings.extend(file_warnings)
            file_level_records.append(
                {
                    "year": year,
                    "district": district,
                    "input_rows": stats["input_rows"],
                    "rows_after_core_dedup": int(len(df)),
                    "core_duplicates_removed": stats["core_duplicates_removed"],
                    "duplicate_family_codes_fixed": stats["duplicate_family_codes_fixed"],
                    "output_rows": stats["output_rows"],
                    "output_file": str(output_path),
                }
            )

    # Build transition matching for 2024 against 2023 by original code + host name.
    lookup = {}
    for district, df in processed_frames[2023].items():
        for _, row in df.iterrows():
            key = (str(row.get("processing.original_family_code", "")), str(row.get("family.hostName", "")).strip())
            lookup[key] = str(row.get("classify.final", row.get("classify", "")))
    for district, df in processed_frames[2024].items():
        for idx, row in df.iterrows():
            key = (str(row.get("processing.original_family_code", "")), str(row.get("family.hostName", "")).strip())
            if key in lookup:
                beginning = lookup[key]
            else:
                ending = str(row.get("classify.final", row.get("classify", "")))
                local_rng = rng_for(args.seed, "transition", 2024, district, idx, row.get("family.code"), row.get("family.hostName"))
                if ending == "Hộ nghèo":
                    beginning = local_rng.choice(["Hộ nghèo", "Hộ cận nghèo", "Hộ không nghèo"])
                elif ending == "Hộ cận nghèo":
                    beginning = local_rng.choice(["Hộ cận nghèo", "Hộ nghèo", "Hộ không nghèo"])
                else:
                    beginning = local_rng.choice(["Hộ không nghèo", "Hộ cận nghèo", "Hộ nghèo"])
            processed_frames[2024][district].at[idx, "transition.beginningClassify"] = beginning
            ending = str(row.get("classify.final", row.get("classify", "")))
            local_rng = rng_for(args.seed, "transition-label", 2024, district, idx, row.get("family.code"), row.get("family.hostName"))
            poor_label, near_label = class_transition_label(beginning, ending, "poor" if ending == "Hộ nghèo" else "near" if ending == "Hộ cận nghèo" else "other", local_rng)
            processed_frames[2024][district].at[idx, "transition.poorChangeType"] = poor_label
            processed_frames[2024][district].at[idx, "transition.nearPoorChangeType"] = near_label
            processed_frames[2024][district].at[idx, "transition.endingClassify"] = ending
            processed_frames[2024][district].at[idx, "transition.isEscapedPoverty"] = beginning in ["Hộ nghèo", "Hộ cận nghèo"] and ending == "Hộ không nghèo"

    # Write back updated 2024 files after transition lookup.
    for district, df in processed_frames[2024].items():
        output_path = output_root / "2024" / f"{district}.xlsx"
        write_dataframe_to_excel(df, output_path, "Data")

    # Update member file references and write member files.
    for year in [2023, 2024]:
        for district, df in processed_frames[year].items():
            member_file = output_root / str(year) / "_members" / f"{district}_members.xlsx"
            if member_file.exists():
                df = df.copy()
                df["family.membersFile"] = str(member_file.relative_to(output_root))
                processed_frames[year][district] = df
                write_dataframe_to_excel(df, output_root / str(year) / f"{district}.xlsx", "Data")

    # Validate outputs and create summary workbook.
    validation_frames, file_level_df, _, aggregate_df, validation_warnings = validate_processed_outputs(output_root, commune_mapping)
    warnings.extend(validation_warnings)

    # Build coverage table from all household files and one member file sample.
    combined_household = pd.concat([df for year_map in processed_frames.values() for df in year_map.values()], ignore_index=True) if any(processed_frames.values()) else pd.DataFrame()
    member_sample = pd.DataFrame()
    member_files = list((output_root / "2023" / "_members").glob("*.xlsx")) + list((output_root / "2024" / "_members").glob("*.xlsx"))
    if member_files:
        member_sample = pd.read_excel(member_files[0], sheet_name="Members", engine="openpyxl")
    coverage_df = build_column_coverage(combined_household if not combined_household.empty else pd.DataFrame(), member_sample)
    validation_frames["column_coverage_df"] = coverage_df

    # Replace validation workbook sheets.
    warnings_df = pd.DataFrame(warnings)
    write_validation_workbook(
        output_root / "logs" / "validation_summary.xlsx",
        {
            "File_Level": pd.DataFrame(file_level_records),
            "Column_Coverage": coverage_df,
            "Legal_Consistency": validation_frames.get("legal_consistency_df", pd.DataFrame()),
            "Null_Checks": validation_frames.get("null_checks_df", pd.DataFrame()),
            "Aggregate_Checks": aggregate_df if not aggregate_df.empty else pd.DataFrame(),
            "Warnings": warnings_df,
        },
    )

    with open(output_root / "logs" / "processing_log.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "input_root": str(input_root),
                "output_root": str(output_root),
                "seed": args.seed,
                "legal_period": args.legal_period,
                "fill_missing_values": args.fill_missing_values,
                "no_null_output": args.no_null_output,
                "template_warnings": template_warnings,
                "warnings": warnings,
                "file_counts": {str(year): len(file_lists.get(year, [])) for year in [2023, 2024]},
                "processed_files": [
                    {"year": rec["year"], "district": rec["district"], "output_file": rec["output_file"]}
                    for rec in file_level_records
                ],
                "summary": {
                    "input_files": sum(len(v) for v in file_lists.values()),
                    "output_files": len(file_level_records),
                    "input_rows": int(sum(rec["input_rows"] for rec in file_level_records)),
                    "output_rows": int(sum(rec["output_rows"] for rec in file_level_records)),
                    "duplicate_core_removed": int(sum(rec["core_duplicates_removed"] for rec in file_level_records)),
                    "family_codes_fixed": int(sum(rec["duplicate_family_codes_fixed"] for rec in file_level_records)),
                    "date_filled": int(sum(int(df["processing.date_was_filled"].fillna(False).astype(bool).sum()) for year_map in processed_frames.values() for df in year_map.values())),
                    "b1_filled": int(sum(int(df["processing.b1Point_was_filled"].fillna(False).astype(bool).sum()) for year_map in processed_frames.values() for df in year_map.values())),
                    "b2_filled": int(sum(int(df["processing.b2Point_was_filled"].fillna(False).astype(bool).sum()) for year_map in processed_frames.values() for df in year_map.values())),
                    "ethnicity_generated": int(sum(int((df["processing.family_coDanTocTaiCho_was_filled"].fillna(False).astype(bool)).sum()) for year_map in processed_frames.values() for df in year_map.values())),
                    "member_records_generated": int(sum(len(pd.read_excel((output_root / str(year) / "_members" / f"{district}_members.xlsx"), sheet_name="Members", engine="openpyxl")) if (output_root / str(year) / "_members" / f"{district}_members.xlsx").exists() else 0 for year in [2023, 2024] for district in processed_frames[year].keys())),
                },
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print("Processed files:")
    for rec in file_level_records:
        print(f"- {rec['year']} {rec['district']}: {rec['output_rows']} rows -> {rec['output_file']}")
    print(f"Warnings: {len(warnings)}")
    print(f"Validation workbook: {output_root / 'logs' / 'validation_summary.xlsx'}")


if __name__ == "__main__":
    main()
