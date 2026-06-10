from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import time
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from jsonschema import Draft202012Validator


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = PROJECT_ROOT / "eval"
RESULTS_DIR = EVAL_DIR / "results"
CASES_PATH = EVAL_DIR / "eval_llm_planning_cases.jsonl"
METRICS_SCHEMA_PATH = EVAL_DIR / "eval_metrics_schema.json"
ALLOWED_COLUMNS_PATH = EVAL_DIR / "config" / "allowed_columns.json"
DOTENV_PATH = PROJECT_ROOT / ".env"

SUPPORTED_MODELS = {"mock_good", "mock_bad", "gemma-4-26B-A4B-it"}
FPT_MODEL = "gemma-4-26B-A4B-it"

JSON_SCHEMA = {
    "type": "object",
    "additionalProperties": True,
    "required": [
        "intent",
        "can_execute",
        "missing_slots",
        "clarification_question",
        "report_id",
        "year",
        "target_group",
        "source_table",
        "filters",
        "group_by",
        "metrics",
        "calculation_type",
        "output",
        "executable_plan",
    ],
    "properties": {
        "intent": {"type": ["string", "null"]},
        "can_execute": {"type": "boolean"},
        "missing_slots": {"type": "array", "items": {"type": "string"}},
        "clarification_question": {"type": ["string", "null"]},
        "report_id": {"type": ["integer", "null"]},
        "year": {"type": ["integer", "null"]},
        "target_group": {"type": ["string", "null"]},
        "source_table": {"type": ["string", "null"]},
        "filters": {"type": ["array", "object", "null"]},
        "group_by": {"type": "array", "items": {"type": "string"}},
        "metrics": {"type": "array", "items": {"anyOf": [{"type": "string"}, {"type": "object"}]}},
        "calculation_type": {"type": ["string", "null"]},
        "output": {
            "type": "object",
            "required": ["type", "template_id", "include_preview"],
            "additionalProperties": True,
            "properties": {
                "type": {"type": "string"},
                "template_id": {"type": ["string", "integer", "null"]},
                "include_preview": {"type": "boolean"},
            },
        },
        "executable_plan": {"type": ["object", "null"]},
    },
}

SUMMARY_BY_CASE_COLUMNS = [
    "model",
    "case_id",
    "category",
    "intent_accuracy",
    "slot_f1",
    "alias_mapping_accuracy",
    "missing_slot_recall",
    "false_execution_rate",
    "report_id_accuracy",
    "json_validity",
    "schema_compliance",
    "exact_plan_match",
    "required_columns_coverage",
    "formula_type_accuracy",
    "source_selection_accuracy",
    "multi_turn_success",
    "answer_groundedness",
    "latency_ms",
    "passed",
]

SUMMARY_BY_MODEL_COLUMNS = [
    "model",
    "query_understanding_score",
    "clarification_score",
    "report_routing_score",
    "json_plan_score",
    "alias_mapping_score",
    "multi_turn_score",
    "response_composer_score",
    "final_score",
    "p50_latency_ms",
    "p95_latency_ms",
    "retry_rate",
    "false_execution_rate",
    "invalid_column_rate",
]

REPORT_REQUIRED_COLUMNS = {
    2: [
        "transition.beginningClassify",
        "transition.endingClassify",
        "transition.poorChangeType",
        "classify",
        "administrative.district",
        "administrative.commune",
    ],
    3: [
        "transition.beginningClassify",
        "transition.endingClassify",
        "transition.nearPoorChangeType",
        "classify",
        "administrative.district",
        "administrative.commune",
    ],
    4: [
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
    5: [
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
    7: [
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
    11: [
        "children.totalCount",
        "children.lackHealthInsuranceCount",
        "children.nutritionDeprivedCount",
        "children.schoolAttendanceDeprivedCount",
        "classify",
    ],
    15: [
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
}

COLUMN_RE = re.compile(r"(?:[A-Za-z_][A-Za-z0-9_]*\.)+[A-Za-z_][A-Za-z0-9_]*")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run LLM evaluation for the poverty-report chatbot.")
    parser.add_argument("--cases", default=str(CASES_PATH), help="Path to the cases JSONL file.")
    parser.add_argument("--models", default="mock_good,mock_bad", help="Comma-separated model list.")
    parser.add_argument("--output-dir", default=str(RESULTS_DIR), help="Output directory.")
    parser.add_argument("--dry-run", action="store_true", help="Use mock providers only.")
    parser.add_argument("--bootstrap-cases", action="store_true", help="Write the default cases file if missing.")
    parser.add_argument("--max-retries", type=int, default=1, help="Maximum retries for live calls.")
    parser.add_argument("--timeout-ms", type=int, default=30000, help="HTTP timeout in milliseconds.")
    parser.add_argument("--temperature", type=float, default=0.0, help="Sampling temperature.")
    return parser.parse_args()


def load_dotenv_file(project_root: Path) -> None:
    path = project_root / ".env"
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def load_cases(cases_path: Path) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    with cases_path.open("r", encoding="utf-8") as handle:
        for idx, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            case = json.loads(line)
            for required_key in ["case_id", "category", "gold", "required_metrics", "notes"]:
                if required_key not in case:
                    raise ValueError(f"Case line {idx} missing key: {required_key}")
            if "user_input" not in case:
                case["user_input"] = None
            if "conversation" not in case:
                case["conversation"] = None
            cases.append(case)
    return cases


def load_metadata(project_root: Path) -> dict[str, Any]:
    metadata_dir = project_root / "Processed" / "metadata"
    loaded: dict[str, Any] = {}
    for name in ["data_dictionary.json", "required_columns_by_report.json", "report_schema_summary.json"]:
        path = metadata_dir / name
        if path.exists():
            loaded[name] = json.loads(path.read_text(encoding="utf-8"))
    return loaded


def load_allowed_columns(project_root: Path, metadata: dict[str, Any]) -> dict[str, Any]:
    fallback = json.loads(ALLOWED_COLUMNS_PATH.read_text(encoding="utf-8")) if ALLOWED_COLUMNS_PATH.exists() else {}
    allowed_columns = set(fallback.get("allowed_columns", []))
    allowed_prefixes = list(fallback.get("allowed_prefixes", ["reason.", "support."]))
    alias_dictionary = dict(fallback.get("alias_dictionary", {}))

    data_dictionary = metadata.get("data_dictionary.json", {})
    if isinstance(data_dictionary, dict):
        allowed_columns.update(data_dictionary.keys())

    required_columns_by_report = metadata.get("required_columns_by_report.json", {})
    if isinstance(required_columns_by_report, dict):
        for report in required_columns_by_report.values():
            allowed_columns.update(report.get("required_columns", []))

    report_schema_summary = metadata.get("report_schema_summary.json", [])
    if isinstance(report_schema_summary, list):
        for report in report_schema_summary:
            allowed_columns.update(report.get("required_columns", []))

    return {
        "allowed_columns": sorted(allowed_columns),
        "allowed_prefixes": allowed_prefixes,
        "alias_dictionary": alias_dictionary,
    }


def build_system_prompt(metadata: dict[str, Any], allowed: dict[str, Any]) -> str:
    report_lines: list[str] = []
    summary = metadata.get("report_schema_summary.json", [])
    if isinstance(summary, list):
        for report in summary:
            report_lines.append(
                f"- report_id={report.get('report_id')}: {report.get('report_name', '')}"
            )
    if not report_lines:
        for report_id, cols in REPORT_REQUIRED_COLUMNS.items():
            report_lines.append(f"- report_id={report_id}: {', '.join(cols)}")

    return "\n".join(
        [
            "You are the Query Understanding and Executable JSON Plan module for a Vietnamese government poverty-report chatbot.",
            "Return only valid JSON.",
            "Do not include markdown or explanation outside JSON.",
            "Do not calculate real data values.",
            "Do not invent missing slots.",
            "If required information is missing, set can_execute=false and provide missing_slots and clarification_question.",
            "If information is sufficient, set can_execute=true and provide executable_plan.",
            "Only use allowed columns and report metadata given in context.",
            "Allowed prefixes: " + ", ".join(allowed["allowed_prefixes"]),
            "Allowed columns: " + ", ".join(allowed["allowed_columns"][:120]),
            "Reports:",
            *report_lines[:20],
            "Expected schema keys: intent, can_execute, missing_slots, clarification_question, report_id, year, target_group, source_table, filters, group_by, metrics, calculation_type, output, executable_plan.",
        ]
    )


def build_case_prompt(case: dict[str, Any], metadata: dict[str, Any], allowed: dict[str, Any]) -> str:
    prompt_payload = {
        "case_id": case["case_id"],
        "category": case["category"],
        "user_input": case.get("user_input"),
        "conversation": case.get("conversation"),
        "allowed_columns": allowed["allowed_columns"][:80],
        "alias_dictionary": allowed["alias_dictionary"],
        "report_metadata": metadata.get("report_schema_summary.json", [])[:5],
    }
    return json.dumps(prompt_payload, ensure_ascii=False, indent=2)


def _candidate_chat_completion_urls(base_url: str) -> list[str]:
    root = base_url.rstrip("/")
    return [f"{root}/v1/chat/completions", f"{root}/chat/completions"]


def resolve_model_config(model_name: str) -> dict[str, Any]:
    if model_name not in SUPPORTED_MODELS:
        raise ValueError(f"Unsupported model: {model_name}")
    if model_name in {"mock_good", "mock_bad"}:
        return {"provider": "mock", "model": model_name}
    base_url = os.environ.get("FPT_BASE_URL", "").strip()
    api_key = os.environ.get("FPT_ALL_LLM_API_KEY", "").strip()
    if not base_url or not api_key:
        raise RuntimeError("Missing FPT_BASE_URL or FPT_ALL_LLM_API_KEY in environment.")
    return {
        "provider": "fpt",
        "model": model_name,
        "base_url": base_url.rstrip("/"),
        "api_key": api_key,
    }


def strip_code_fences(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped, flags=re.IGNORECASE)
        stripped = re.sub(r"\s*```$", "", stripped)
    return stripped.strip()


def parse_model_json(raw_text: str) -> tuple[dict[str, Any] | None, str | None]:
    candidate = strip_code_fences(raw_text)
    first = candidate.find("{")
    last = candidate.rfind("}")
    if first != -1 and last != -1 and last > first:
        candidate = candidate[first : last + 1]
    try:
        parsed = json.loads(candidate)
        if isinstance(parsed, dict) and "choices" in parsed:
            try:
                content = parsed["choices"][0]["message"]["content"]
            except Exception as exc:  # noqa: BLE001
                return None, f"Envelope parse failed: {exc}"
            return parse_model_json(content)
        if not isinstance(parsed, dict):
            return None, "Parsed JSON is not an object."
        return parsed, None
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)


def validate_schema(parsed_output: dict[str, Any]) -> tuple[bool, str | None]:
    validator = Draft202012Validator(JSON_SCHEMA)
    errors = sorted(validator.iter_errors(parsed_output), key=lambda err: err.path)
    if errors:
        return False, "; ".join(error.message for error in errors[:5])
    return True, None


def normalize_model_output(parsed_output: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(parsed_output)
    if isinstance(normalized.get("intent"), list) and normalized["intent"]:
        normalized["intent"] = normalized["intent"][0]
    if isinstance(normalized.get("report_id"), list) and normalized["report_id"]:
        normalized["report_id"] = normalized["report_id"][0]
    if isinstance(normalized.get("year"), list) and normalized["year"]:
        normalized["year"] = normalized["year"][0]
    if isinstance(normalized.get("target_group"), list):
        normalized["target_group"] = ", ".join(str(item) for item in normalized["target_group"] if item is not None)
    if isinstance(normalized.get("source_table"), list) and normalized["source_table"]:
        normalized["source_table"] = normalized["source_table"][0]
    if isinstance(normalized.get("calculation_type"), list) and normalized["calculation_type"]:
        normalized["calculation_type"] = normalized["calculation_type"][0]
    if isinstance(normalized.get("missing_slots"), str):
        normalized["missing_slots"] = [normalized["missing_slots"]]
    if normalized.get("missing_slots") is None:
        normalized["missing_slots"] = []
    if isinstance(normalized.get("group_by"), str):
        normalized["group_by"] = [normalized["group_by"]]
    if normalized.get("group_by") is None:
        normalized["group_by"] = []
    if isinstance(normalized.get("metrics"), str):
        normalized["metrics"] = [normalized["metrics"]]
    if normalized.get("metrics") is None:
        normalized["metrics"] = []
    if isinstance(normalized.get("filters"), dict):
        normalized["filters"] = [normalized["filters"]]
    if normalized.get("filters") is None:
        normalized["filters"] = []
    if isinstance(normalized.get("output"), str):
        normalized["output"] = {
            "type": "text",
            "template_id": None,
            "include_preview": True,
            "text": normalized["output"],
        }
    if normalized.get("output") is None:
        normalized["output"] = {"type": "text", "template_id": None, "include_preview": True}
    if isinstance(normalized.get("executable_plan"), str):
        normalized["executable_plan"] = {"answer": normalized["executable_plan"]}
    if normalized.get("executable_plan") is None and normalized.get("can_execute"):
        normalized["executable_plan"] = {"answer": normalized.get("output", {}).get("text")}
    if normalized.get("calculation_type") is None:
        normalized["calculation_type"] = "aggregate"
    if normalized.get("source_table") is None:
        normalized["source_table"] = "households"
    return normalized


def call_model_live(
    config: dict[str, Any],
    system_prompt: str,
    case_prompt: str,
    timeout_ms: int,
    temperature: float,
    max_retries: int,
) -> dict[str, Any]:
    payload = {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": case_prompt},
        ],
        "temperature": temperature,
        "stream": False,
        "response_format": {"type": "json_object"},
    }
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json",
    }
    last_error: str | None = None
    timeout_seconds = max(timeout_ms / 1000.0, 1.0)
    for attempt in range(max_retries + 1):
        for url in _candidate_chat_completion_urls(config["base_url"]):
            started = time.perf_counter()
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=timeout_seconds)
                latency_ms = int((time.perf_counter() - started) * 1000)
                raw_text = response.text
                if response.status_code in {429} and attempt < max_retries:
                    last_error = f"{url} HTTP {response.status_code}: {raw_text[:300]}"
                    time.sleep(min(2 ** attempt, 5))
                    continue
                if response.status_code >= 500 and attempt < max_retries:
                    last_error = f"{url} HTTP {response.status_code}: {raw_text[:300]}"
                    time.sleep(min(2 ** attempt, 5))
                    continue
                response.raise_for_status()
                return {
                    "raw_response": raw_text,
                    "latency_ms": latency_ms,
                    "retry_count": attempt,
                    "url": url,
                }
            except requests.RequestException as exc:
                latency_ms = int((time.perf_counter() - started) * 1000)
                last_error = str(exc)
                if attempt >= max_retries:
                    return {
                        "raw_response": "",
                        "latency_ms": latency_ms,
                        "retry_count": attempt,
                        "url": url,
                        "error": last_error,
                    }
    return {
        "raw_response": "",
        "latency_ms": 0,
        "retry_count": max_retries,
        "url": None,
        "error": last_error or "unknown error",
    }


def _gold_to_prediction(case: dict[str, Any], gold: dict[str, Any]) -> dict[str, Any]:
    prediction: dict[str, Any] = {
        "intent": gold.get("intent", "unknown"),
        "can_execute": bool(gold.get("can_execute", True)),
        "missing_slots": list(gold.get("missing_slots", [])) if not gold.get("can_execute", True) else [],
        "clarification_question": gold.get("clarification_question"),
        "report_id": gold.get("report_id"),
        "year": gold.get("year"),
        "target_group": gold.get("target_group"),
        "source_table": gold.get("source_table"),
        "filters": deepcopy(gold.get("filters", [])),
        "group_by": list(gold.get("group_by", [])),
        "metrics": deepcopy(gold.get("metrics", [])),
        "calculation_type": gold.get("calculation_type"),
        "output": deepcopy(gold.get("output", {"type": "text", "template_id": None, "include_preview": True})),
        "executable_plan": deepcopy(gold.get("executable_plan")),
    }
    if prediction["can_execute"] and prediction["executable_plan"] is None:
        prediction["executable_plan"] = {
            "required_columns": deepcopy(gold.get("required_columns", [])),
            "answer": gold.get("expected_response"),
            "turn_states": deepcopy(gold.get("turn_states", [])),
        }
    if gold.get("alias_mapping"):
        prediction["alias_mapping"] = deepcopy(gold["alias_mapping"])
    return prediction


def _bad_prediction(case: dict[str, Any], index: int) -> tuple[str, dict[str, Any] | None]:
    if index % 5 == 0:
        return "I cannot produce JSON for this case.", None
    if index % 5 == 1:
        return json.dumps({"intent": "unknown", "can_execute": False}, ensure_ascii=False), None
    payload = {
        "intent": "unknown",
        "can_execute": True,
        "missing_slots": [],
        "clarification_question": None,
        "report_id": 9999,
        "year": 1900,
        "target_group": "không rõ",
        "source_table": "bad_table",
        "filters": [{"field": "bad.column", "op": "=", "value": "x"}],
        "group_by": ["bad.group"],
        "metrics": ["SUM(bad.metric)"],
        "calculation_type": "bad",
        "output": {"type": "text", "template_id": "bad", "include_preview": False},
        "executable_plan": {"required_columns": ["bad.column"], "answer": "wrong"},
    }
    return json.dumps(payload, ensure_ascii=False), payload


def call_model_mock(model_name: str, case: dict[str, Any], index: int) -> dict[str, Any]:
    gold = case["gold"]
    if model_name == "mock_good":
        prediction = _gold_to_prediction(case, gold)
        raw_response = json.dumps(prediction, ensure_ascii=False, indent=2)
        return {
            "raw_response": raw_response,
            "latency_ms": 5,
            "retry_count": 0,
        }
    raw_response, parsed = _bad_prediction(case, index)
    return {
        "raw_response": raw_response,
        "latency_ms": 3,
        "retry_count": 0,
        "forced_parsed": parsed,
    }


def _normalize_scalar(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return re.sub(r"\s+", " ", str(value).strip()).lower()


def _extract_tokens_from_text(value: str, allowed: dict[str, Any]) -> set[str]:
    tokens = set(COLUMN_RE.findall(value))
    for alias, mapped in allowed["alias_dictionary"].items():
        if alias.lower() in value.lower():
            tokens.add(mapped)
    return tokens


def _collect_predicted_columns(obj: Any, allowed: dict[str, Any]) -> set[str]:
    collected: set[str] = set()
    if obj is None:
        return collected
    if isinstance(obj, str):
        collected.update(_extract_tokens_from_text(obj, allowed))
        return collected
    if isinstance(obj, dict):
        for key, value in obj.items():
            collected.update(_extract_tokens_from_text(key, allowed))
            collected.update(_collect_predicted_columns(value, allowed))
        return collected
    if isinstance(obj, list):
        for item in obj:
            collected.update(_collect_predicted_columns(item, allowed))
        return collected
    if isinstance(obj, (int, float, bool)):
        return collected
    collected.update(_extract_tokens_from_text(str(obj), allowed))
    return collected


def _filter_to_tokens(filters: Any, allowed: dict[str, Any]) -> set[str]:
    collected: set[str] = set()
    if filters is None:
        return collected
    if isinstance(filters, dict):
        collected.update(_collect_predicted_columns(filters, allowed))
        for key, value in filters.items():
            collected.add(_normalize_scalar(key) + "=" + _normalize_scalar(value))
        return collected
    if isinstance(filters, list):
        for item in filters:
            collected.update(_filter_to_tokens(item, allowed))
        return collected
    collected.update(_collect_predicted_columns(filters, allowed))
    return collected


def _slot_tokens(payload: dict[str, Any], allowed: dict[str, Any]) -> set[str]:
    tokens: set[str] = set()
    if payload.get("year") is not None:
        tokens.add(f"year={_normalize_scalar(payload['year'])}")
    if payload.get("report_id") is not None:
        tokens.add(f"report_id={_normalize_scalar(payload['report_id'])}")
    if payload.get("target_group"):
        tokens.add(f"target_group={_normalize_scalar(payload['target_group'])}")
    if payload.get("source_table"):
        tokens.add(f"source_table={_normalize_scalar(payload['source_table'])}")
    if payload.get("calculation_type"):
        tokens.add(f"calculation_type={_normalize_scalar(payload['calculation_type'])}")
    for item in payload.get("group_by", []) or []:
        tokens.add(f"group_by={_normalize_scalar(item)}")
    for item in payload.get("metrics", []) or []:
        if isinstance(item, str):
            tokens.update(_extract_tokens_from_text(item, allowed))
            tokens.add(f"metric={_normalize_scalar(item)}")
        elif isinstance(item, dict):
            tokens.update(_collect_predicted_columns(item, allowed))
    tokens.update(_filter_to_tokens(payload.get("filters"), allowed))
    if isinstance(payload.get("alias_mapping"), dict):
        for alias, mapped in payload["alias_mapping"].items():
            tokens.add(f"alias={_normalize_scalar(alias)}->{_normalize_scalar(mapped)}")
    return tokens


def _metric_mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return float(sum(values) / len(values))


def _safe_pctl(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    k = (len(ordered) - 1) * (percentile / 100.0)
    f = int(k)
    c = min(f + 1, len(ordered) - 1)
    if f == c:
        return float(ordered[f])
    d0 = ordered[f] * (c - k)
    d1 = ordered[c] * (k - f)
    return float(d0 + d1)


def score_case(case: dict[str, Any], predicted: dict[str, Any] | None, metadata: dict[str, Any], allowed: dict[str, Any], parse_error: str | None, schema_error: str | None, latency_ms: int, retry_count: int) -> dict[str, Any]:
    gold = case["gold"]
    metrics = {
        "intent_accuracy": 0.0,
        "slot_precision": 0.0,
        "slot_recall": 0.0,
        "slot_f1": 0.0,
        "alias_mapping_accuracy": 0.0,
        "missing_slot_recall": 0.0,
        "false_execution_rate": 0.0,
        "no_assumption_rate": 0.0,
        "report_id_accuracy": 0.0,
        "confusable_report_accuracy": 0.0,
        "json_validity_rate": 1.0 if not parse_error else 0.0,
        "schema_compliance_rate": 1.0 if not schema_error and predicted is not None else 0.0,
        "exact_plan_match": 0.0,
        "required_columns_coverage": 0.0,
        "invalid_column_rate": 0.0,
        "formula_type_accuracy": 0.0,
        "source_selection_accuracy": 0.0,
        "multi_turn_success_rate": 0.0,
        "state_update_accuracy": 0.0,
        "answer_groundedness": 0.0,
        "response_correctness": 0.0,
        "latency_ms": float(latency_ms),
        "retry_count": int(retry_count),
    }

    if predicted is None:
        if not gold.get("can_execute", True):
            metrics["false_execution_rate"] = 0.0
        return metrics

    def eq(a: Any, b: Any) -> float:
        return 1.0 if _normalize_scalar(a) == _normalize_scalar(b) else 0.0

    metrics["intent_accuracy"] = eq(predicted.get("intent"), gold.get("intent"))
    metrics["report_id_accuracy"] = eq(predicted.get("report_id"), gold.get("report_id"))
    metrics["formula_type_accuracy"] = eq(predicted.get("calculation_type"), gold.get("calculation_type"))
    metrics["source_selection_accuracy"] = eq(predicted.get("source_table"), gold.get("source_table"))
    metrics["alias_mapping_accuracy"] = 1.0 if gold.get("alias_mapping") == predicted.get("alias_mapping") else 0.0

    gold_tokens = _slot_tokens(gold, allowed)
    pred_tokens = _slot_tokens(predicted, allowed)
    intersection = gold_tokens & pred_tokens
    precision = len(intersection) / len(pred_tokens) if pred_tokens else 0.0
    recall = len(intersection) / len(gold_tokens) if gold_tokens else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision and recall else 0.0
    metrics["slot_precision"] = float(precision)
    metrics["slot_recall"] = float(recall)
    metrics["slot_f1"] = float(f1)

    if gold.get("missing_slots"):
        predicted_missing = set(map(_normalize_scalar, predicted.get("missing_slots", [])))
        required_missing = set(map(_normalize_scalar, gold.get("missing_slots", [])))
        metrics["missing_slot_recall"] = 1.0 if required_missing.issubset(predicted_missing) else 0.0
        metrics["no_assumption_rate"] = 1.0 if not (predicted.get("can_execute") and not predicted_missing) else 0.0
        metrics["false_execution_rate"] = 1.0 if predicted.get("can_execute") and required_missing else 0.0
    else:
        metrics["missing_slot_recall"] = 1.0
        metrics["no_assumption_rate"] = 1.0
        metrics["false_execution_rate"] = 0.0 if predicted.get("can_execute") else 1.0 if not gold.get("can_execute", True) and predicted.get("can_execute") else 0.0

    if gold.get("required_columns"):
        predicted_columns = _collect_predicted_columns(predicted.get("executable_plan"), allowed)
        if not predicted_columns:
            predicted_columns = _collect_predicted_columns(predicted, allowed)
        required_columns = set(gold["required_columns"])
        metrics["required_columns_coverage"] = len(required_columns & predicted_columns) / len(required_columns)
        allowed_set = set(allowed["allowed_columns"])
        prefix_ok = tuple(allowed["allowed_prefixes"])
        invalid_columns = {
            column
            for column in predicted_columns
            if column not in allowed_set and not any(column.startswith(prefix) for prefix in prefix_ok)
        }
        metrics["invalid_column_rate"] = len(invalid_columns) / len(predicted_columns) if predicted_columns else 0.0

    exact_fields: list[float] = []
    for key in ["intent", "report_id", "year", "target_group", "source_table", "calculation_type"]:
        if key in gold:
            exact_fields.append(eq(predicted.get(key), gold.get(key)))
    if "filters" in gold:
        exact_fields.append(1.0 if predicted.get("filters") == gold.get("filters") else 0.0)
    if "group_by" in gold:
        exact_fields.append(1.0 if set(predicted.get("group_by") or []) == set(gold.get("group_by", [])) else 0.0)
    if "metrics" in gold:
        exact_fields.append(1.0 if (predicted.get("metrics") or []) == gold.get("metrics", []) else 0.0)
    metrics["exact_plan_match"] = _metric_mean(exact_fields)

    if case["category"] == "multi_turn":
        metrics["multi_turn_success_rate"] = 1.0 if metrics["slot_f1"] >= 1.0 and metrics["intent_accuracy"] >= 1.0 else 0.0
        metrics["state_update_accuracy"] = 1.0 if metrics["multi_turn_success_rate"] >= 1.0 else 0.0
    else:
        metrics["multi_turn_success_rate"] = 0.0
        metrics["state_update_accuracy"] = 0.0

    expected_response = gold.get("expected_response")
    predicted_answer = None
    if isinstance(predicted.get("executable_plan"), dict):
        predicted_answer = predicted["executable_plan"].get("answer") or predicted["executable_plan"].get("preview_text")
    if predicted_answer is None and isinstance(predicted.get("output"), dict):
        predicted_answer = predicted["output"].get("preview_text") or predicted["output"].get("text")
    if expected_response:
        metrics["answer_groundedness"] = 1.0 if _normalize_scalar(predicted_answer) == _normalize_scalar(expected_response) else 0.0
        metrics["response_correctness"] = metrics["answer_groundedness"]
    else:
        metrics["answer_groundedness"] = 1.0
        metrics["response_correctness"] = 1.0

    return metrics


def append_raw_log(path: Path, record: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def _group_case_score(row: dict[str, Any]) -> float:
    category = row["category"]
    if category == "query_understanding":
        return _metric_mean([row["intent_accuracy"], row["slot_f1"], row["exact_plan_match"]])
    if category == "clarification":
        if row["false_execution_rate"] >= 1:
            return 0.0
        return _metric_mean([row["missing_slot_recall"], row["no_assumption_rate"]])
    if category == "report_routing":
        return _metric_mean([row["report_id_accuracy"], row["formula_type_accuracy"], row["source_selection_accuracy"]])
    if category == "json_plan":
        return _metric_mean(
            [
                row["json_validity_rate"],
                row["schema_compliance_rate"],
                row["required_columns_coverage"],
                row["formula_type_accuracy"],
                1.0 - row["invalid_column_rate"],
            ]
        )
    if category == "alias_mapping":
        return float(row["alias_mapping_accuracy"])
    if category == "multi_turn":
        return _metric_mean([row["multi_turn_success_rate"], row["state_update_accuracy"]])
    if category == "response_composer":
        return _metric_mean([row["answer_groundedness"], row["response_correctness"]])
    return 0.0


def aggregate_model_scores(case_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in case_rows:
        by_model[row["model"]].append(row)

    summary_rows: list[dict[str, Any]] = []
    for model, rows in by_model.items():
        category_scores = defaultdict(list)
        for row in rows:
            category_scores[row["category"]].append(_group_case_score(row))

        query_understanding_score = _metric_mean(category_scores["query_understanding"])
        clarification_score = _metric_mean(category_scores["clarification"])
        report_routing_score = _metric_mean(category_scores["report_routing"])
        json_plan_score = _metric_mean(category_scores["json_plan"])
        alias_mapping_score = _metric_mean(category_scores["alias_mapping"])
        multi_turn_score = _metric_mean(category_scores["multi_turn"])
        response_composer_score = _metric_mean(category_scores["response_composer"])

        final_score = (
            0.20 * query_understanding_score
            + 0.15 * clarification_score
            + 0.15 * report_routing_score
            + 0.25 * json_plan_score
            + 0.10 * alias_mapping_score
            + 0.10 * multi_turn_score
            + 0.05 * response_composer_score
        )

        latencies = [float(row["latency_ms"]) for row in rows]
        retry_rate = sum(1 for row in rows if int(row["retry_count"]) > 0) / len(rows) if rows else 0.0
        false_execution_rate = _metric_mean([float(row["false_execution_rate"]) for row in rows])
        invalid_column_rate = _metric_mean([float(row["invalid_column_rate"]) for row in rows])

        summary_rows.append(
            {
                "model": model,
                "query_understanding_score": query_understanding_score,
                "clarification_score": clarification_score,
                "report_routing_score": report_routing_score,
                "json_plan_score": json_plan_score,
                "alias_mapping_score": alias_mapping_score,
                "multi_turn_score": multi_turn_score,
                "response_composer_score": response_composer_score,
                "final_score": final_score,
                "p50_latency_ms": _safe_pctl(latencies, 50),
                "p95_latency_ms": _safe_pctl(latencies, 95),
                "retry_rate": retry_rate,
                "false_execution_rate": false_execution_rate,
                "invalid_column_rate": invalid_column_rate,
            }
        )
    return summary_rows


def write_summary_by_case(path: Path, rows: list[dict[str, Any]]) -> None:
    df = pd.DataFrame(rows)
    if df.empty:
        df = pd.DataFrame(columns=SUMMARY_BY_CASE_COLUMNS)
    df["json_validity"] = df.get("json_validity_rate", 0.0)
    df["schema_compliance"] = df.get("schema_compliance_rate", 0.0)
    df["multi_turn_success"] = df.get("multi_turn_success_rate", 0.0)
    df = df.reindex(columns=SUMMARY_BY_CASE_COLUMNS)
    df.to_csv(path, index=False)


def write_summary_by_model(path: Path, rows: list[dict[str, Any]]) -> None:
    df = pd.DataFrame(rows)
    if df.empty:
        df = pd.DataFrame(columns=SUMMARY_BY_MODEL_COLUMNS)
    df = df.reindex(columns=SUMMARY_BY_MODEL_COLUMNS)
    df.to_csv(path, index=False)


def _default_output(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": case["gold"].get("output", {}).get("type", "text"),
        "template_id": case["gold"].get("output", {}).get("template_id"),
        "include_preview": case["gold"].get("output", {}).get("include_preview", True),
    }


def build_default_case_specs() -> list[dict[str, Any]]:
    def qa_case(case_id: str, category: str, user_input: str, gold: dict[str, Any], required_metrics: list[str], notes: str, conversation: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        payload = {
            "case_id": case_id,
            "category": category,
            "user_input": user_input,
            "conversation": conversation,
            "gold": gold,
            "required_metrics": required_metrics,
            "notes": notes,
        }
        return payload

    def gold_base(**kwargs: Any) -> dict[str, Any]:
        output = kwargs.pop("output", {"type": "text", "template_id": None, "include_preview": True})
        plan = kwargs.pop("executable_plan", None)
        gold = {
            "intent": kwargs.pop("intent"),
            "can_execute": kwargs.pop("can_execute", True),
            "missing_slots": kwargs.pop("missing_slots", []),
            "clarification_question": kwargs.pop("clarification_question", None),
            "report_id": kwargs.pop("report_id", None),
            "year": kwargs.pop("year", None),
            "target_group": kwargs.pop("target_group", None),
            "source_table": kwargs.pop("source_table", "households"),
            "filters": kwargs.pop("filters", []),
            "group_by": kwargs.pop("group_by", []),
            "metrics": kwargs.pop("metrics", []),
            "calculation_type": kwargs.pop("calculation_type", "aggregate"),
            "required_columns": kwargs.pop("required_columns", []),
            "alias_mapping": kwargs.pop("alias_mapping", {}),
            "output": output,
            "executable_plan": plan,
            "expected_response": kwargs.pop("expected_response", None),
            "turn_states": kwargs.pop("turn_states", []),
        }
        gold.update(kwargs)
        return gold

    specs: list[dict[str, Any]] = []

    specs.extend(
        [
            qa_case(
                "A1_top_poor_household_2024",
                "query_understanding",
                "Năm 2024, huyện/thành phố nào có số hộ nghèo nhiều nhất?",
                gold_base(
                    intent="qa_aggregate",
                    can_execute=True,
                    year=2024,
                    target_group="Hộ nghèo",
                    filters=[{"field": "classify", "op": "=", "value": "Hộ nghèo"}],
                    group_by=["administrative.district"],
                    metrics=["COUNT(family.code)"],
                    calculation_type="aggregate",
                    source_table="households",
                ),
                ["intent_accuracy", "slot_f1", "exact_plan_match"],
                "QA aggregate case",
            ),
            qa_case(
                "A2_children_bhyt_poor_2024",
                "query_understanding",
                "Có bao nhiêu trẻ em thuộc hộ nghèo bị thiếu BHYT năm 2024?",
                gold_base(
                    intent="qa_aggregate",
                    can_execute=True,
                    year=2024,
                    target_group="Hộ nghèo",
                    filters=[{"field": "classify", "op": "=", "value": "Hộ nghèo"}],
                    group_by=[],
                    metrics=["SUM(children.lackHealthInsuranceCount)"],
                    calculation_type="aggregate",
                    source_table="households",
                ),
                ["intent_accuracy", "slot_f1", "exact_plan_match"],
                "QA aggregate case",
            ),
            qa_case(
                "A3_compare_clean_water_poor_vs_near_poor_2024_by_district",
                "query_understanding",
                "So sánh thiếu hụt nước sạch giữa hộ nghèo và hộ cận nghèo năm 2024 theo huyện.",
                gold_base(
                    intent="qa_compare",
                    can_execute=True,
                    year=2024,
                    target_group="Hộ nghèo và hộ cận nghèo",
                    filters=[{"field": "classify", "op": "in", "value": ["Hộ nghèo", "Hộ cận nghèo"]}],
                    group_by=["administrative.district"],
                    metrics=["SUM(deprivation.cleanWater)"],
                    calculation_type="compare",
                    source_table="households",
                ),
                ["intent_accuracy", "slot_f1", "exact_plan_match"],
                "QA compare case",
            ),
            qa_case(
                "A4_top10_hygienic_toilet_rate_2024_by_commune",
                "query_understanding",
                "Cho tôi top 10 xã có tỷ lệ thiếu nhà tiêu hợp vệ sinh cao nhất năm 2024.",
                gold_base(
                    intent="qa_aggregate",
                    can_execute=True,
                    year=2024,
                    target_group="Hộ nghèo và hộ cận nghèo",
                    filters=[],
                    group_by=["administrative.commune"],
                    metrics=["RATE(deprivation.hygienicToilet)"],
                    calculation_type="percentage",
                    source_table="households",
                    top_k=10,
                ),
                ["intent_accuracy", "slot_f1", "exact_plan_match"],
                "QA top-k aggregate case",
            ),
            qa_case(
                "A5_poor_by_ethnicity_2024",
                "query_understanding",
                "Thống kê hộ nghèo theo dân tộc năm 2024.",
                gold_base(
                    intent="qa_aggregate",
                    can_execute=True,
                    year=2024,
                    target_group="Hộ nghèo",
                    filters=[{"field": "classify", "op": "=", "value": "Hộ nghèo"}],
                    group_by=["family.ethnicity"],
                    metrics=["COUNT(family.code)"],
                    calculation_type="aggregate",
                    source_table="households",
                ),
                ["intent_accuracy", "slot_f1", "exact_plan_match"],
                "QA aggregate by ethnicity case",
            ),
        ]
    )

    specs.extend(
        [
            qa_case(
                "B1_missing_year_group_calc_for_social_deprivation_report",
                "clarification",
                "Tạo báo cáo thiếu hụt dịch vụ xã hội.",
                gold_base(
                    intent="generate_report",
                    can_execute=False,
                    missing_slots=["year", "target_group", "calculation_type"],
                    target_group=None,
                    source_table="households",
                ),
                ["missing_slot_recall", "no_assumption_rate", "false_execution_rate"],
                "Clarification case",
            ),
            qa_case(
                "B2_missing_report_type_for_2024_report",
                "clarification",
                "Tạo report năm 2024.",
                gold_base(
                    intent="generate_report",
                    can_execute=False,
                    year=2024,
                    missing_slots=["report_id", "target_group", "calculation_type"],
                    source_table="households",
                ),
                ["missing_slot_recall", "no_assumption_rate", "false_execution_rate"],
                "Clarification case",
            ),
            qa_case(
                "B3_missing_year_for_report_5",
                "clarification",
                "Cho tôi báo cáo mẫu 5.",
                gold_base(
                    intent="generate_report",
                    can_execute=False,
                    report_id=5,
                    missing_slots=["year"],
                    target_group="Hộ nghèo",
                    calculation_type="percentage",
                    source_table="households",
                ),
                ["missing_slot_recall", "no_assumption_rate", "false_execution_rate"],
                "Clarification case",
            ),
            qa_case(
                "B4_missing_target_group_for_gia_nghia_poverty_report",
                "clarification",
                "Tạo báo cáo hộ nghèo ở Gia Nghĩa.",
                gold_base(
                    intent="generate_report",
                    can_execute=False,
                    missing_slots=["year", "report_id", "calculation_type"],
                    source_table="households",
                ),
                ["missing_slot_recall", "no_assumption_rate", "false_execution_rate"],
                "Clarification case",
            ),
            qa_case(
                "B5_missing_target_group_for_deprivation_report_2024",
                "clarification",
                "Xuất báo cáo thiếu hụt năm 2024.",
                gold_base(
                    intent="generate_report",
                    can_execute=False,
                    year=2024,
                    missing_slots=["target_group", "calculation_type", "report_id"],
                    source_table="households",
                ),
                ["missing_slot_recall", "no_assumption_rate", "false_execution_rate"],
                "Clarification case",
            ),
        ]
    )

    specs.extend(
        [
            qa_case(
                "C1_route_report_5_poor_percentage_deprivation",
                "report_routing",
                "Phân tích tỷ lệ các chỉ số thiếu hụt dịch vụ xã hội cơ bản hộ nghèo.",
                gold_base(
                    intent="generate_report",
                    can_execute=True,
                    report_id=5,
                    year=2024,
                    target_group="Hộ nghèo",
                    calculation_type="percentage",
                    source_table="households",
                    required_columns=REPORT_REQUIRED_COLUMNS[5],
                    output={"type": "xlsx", "template_id": 5, "include_preview": True},
                ),
                ["report_id_accuracy", "formula_type_accuracy", "source_selection_accuracy"],
                "Report routing case",
            ),
            qa_case(
                "C2_route_report_4_poor_deprivation_counts",
                "report_routing",
                "Phân tích chỉ số thiếu hụt dịch vụ xã hội cơ bản của hộ nghèo.",
                gold_base(
                    intent="generate_report",
                    can_execute=True,
                    report_id=4,
                    year=2024,
                    target_group="Hộ nghèo",
                    calculation_type="aggregate",
                    source_table="households",
                    required_columns=REPORT_REQUIRED_COLUMNS[4],
                    output={"type": "xlsx", "template_id": 4, "include_preview": True},
                ),
                ["report_id_accuracy", "formula_type_accuracy", "source_selection_accuracy"],
                "Report routing case",
            ),
            qa_case(
                "C3_route_report_7_near_poor_percentage_deprivation",
                "report_routing",
                "Phân tích tỷ lệ các chỉ số thiếu hụt dịch vụ xã hội cơ bản hộ cận nghèo.",
                gold_base(
                    intent="generate_report",
                    can_execute=True,
                    report_id=7,
                    year=2024,
                    target_group="Hộ cận nghèo",
                    calculation_type="percentage",
                    source_table="households",
                    required_columns=REPORT_REQUIRED_COLUMNS[7],
                    output={"type": "xlsx", "template_id": 7, "include_preview": True},
                ),
                ["report_id_accuracy", "formula_type_accuracy", "source_selection_accuracy"],
                "Report routing case",
            ),
            qa_case(
                "C4_route_report_3_near_poor_transition",
                "report_routing",
                "Tổng hợp diễn biến hộ cận nghèo.",
                gold_base(
                    intent="generate_report",
                    can_execute=True,
                    report_id=3,
                    year=2024,
                    target_group="Hộ cận nghèo",
                    calculation_type="aggregate",
                    source_table="households",
                    required_columns=REPORT_REQUIRED_COLUMNS[3],
                    output={"type": "xlsx", "template_id": 3, "include_preview": True},
                ),
                ["report_id_accuracy", "formula_type_accuracy", "source_selection_accuracy"],
                "Report routing case",
            ),
            qa_case(
                "C5_route_report_15_poor_detail_list",
                "report_routing",
                "Danh sách chi tiết hộ nghèo.",
                gold_base(
                    intent="generate_report",
                    can_execute=True,
                    report_id=15,
                    year=2024,
                    target_group="Hộ nghèo",
                    calculation_type="detail",
                    source_table="households",
                    required_columns=REPORT_REQUIRED_COLUMNS[15],
                    output={"type": "xlsx", "template_id": 15, "include_preview": True},
                ),
                ["report_id_accuracy", "formula_type_accuracy", "source_selection_accuracy"],
                "Report routing case",
            ),
        ]
    )

    specs.extend(
        [
            qa_case(
                "D1_json_plan_top_poor_district_2024",
                "json_plan",
                "Năm 2024, huyện/thành phố nào có số hộ nghèo nhiều nhất?",
                gold_base(
                    intent="qa_aggregate",
                    can_execute=True,
                    year=2024,
                    target_group="Hộ nghèo",
                    filters=[{"field": "classify", "op": "=", "value": "Hộ nghèo"}],
                    group_by=["administrative.district"],
                    metrics=["COUNT(family.code)"],
                    calculation_type="aggregate",
                    source_table="households",
                    required_columns=["administrative.district", "classify", "family.code"],
                    output={"type": "text", "template_id": None, "include_preview": True},
                ),
                ["json_validity_rate", "schema_compliance_rate", "required_columns_coverage", "formula_type_accuracy", "invalid_column_rate"],
                "JSON plan case",
            ),
            qa_case(
                "D2_json_plan_report_5_2024",
                "json_plan",
                "Tạo báo cáo mẫu 5 năm 2024.",
                gold_base(
                    intent="generate_report",
                    can_execute=True,
                    report_id=5,
                    year=2024,
                    target_group="Hộ nghèo",
                    calculation_type="percentage",
                    source_table="households",
                    required_columns=REPORT_REQUIRED_COLUMNS[5],
                    output={"type": "xlsx", "template_id": 5, "include_preview": True},
                ),
                ["json_validity_rate", "schema_compliance_rate", "required_columns_coverage", "formula_type_accuracy", "invalid_column_rate"],
                "JSON plan case",
            ),
            qa_case(
                "D3_json_plan_report_2_poor_transition",
                "json_plan",
                "Tạo báo cáo diễn biến hộ nghèo.",
                gold_base(
                    intent="generate_report",
                    can_execute=True,
                    report_id=2,
                    year=2024,
                    target_group="Hộ nghèo",
                    calculation_type="aggregate",
                    source_table="households",
                    required_columns=REPORT_REQUIRED_COLUMNS[2],
                    output={"type": "xlsx", "template_id": 2, "include_preview": True},
                ),
                ["json_validity_rate", "schema_compliance_rate", "required_columns_coverage", "formula_type_accuracy", "invalid_column_rate"],
                "JSON plan case",
            ),
            qa_case(
                "D4_json_plan_children_bhyt_poor",
                "json_plan",
                "Hỏi trẻ em thiếu BHYT thuộc hộ nghèo.",
                gold_base(
                    intent="qa_aggregate",
                    can_execute=True,
                    year=2024,
                    target_group="Hộ nghèo",
                    filters=[{"field": "classify", "op": "=", "value": "Hộ nghèo"}],
                    group_by=[],
                    metrics=["SUM(children.lackHealthInsuranceCount)"],
                    calculation_type="aggregate",
                    source_table="households",
                    required_columns=["children.lackHealthInsuranceCount", "classify"],
                    output={"type": "text", "template_id": None, "include_preview": True},
                ),
                ["json_validity_rate", "schema_compliance_rate", "required_columns_coverage", "formula_type_accuracy", "invalid_column_rate"],
                "JSON plan case",
            ),
            qa_case(
                "D5_json_plan_complex_area_year_group_top_sort",
                "json_plan",
                "Cho tôi top 10 xã có tỷ lệ thiếu nhà tiêu hợp vệ sinh cao nhất năm 2024 theo huyện và sắp xếp giảm dần.",
                gold_base(
                    intent="qa_aggregate",
                    can_execute=True,
                    year=2024,
                    target_group="Hộ nghèo và hộ cận nghèo",
                    filters=[],
                    group_by=["administrative.district", "administrative.commune"],
                    metrics=["RATE(deprivation.hygienicToilet)"],
                    calculation_type="percentage",
                    source_table="households",
                    required_columns=["administrative.district", "administrative.commune", "deprivation.hygienicToilet"],
                    output={"type": "text", "template_id": None, "include_preview": True},
                    top_k=10,
                    sort="desc",
                ),
                ["json_validity_rate", "schema_compliance_rate", "required_columns_coverage", "formula_type_accuracy", "invalid_column_rate"],
                "JSON plan case",
            ),
        ]
    )

    specs.extend(
        [
            qa_case(
                "E1_alias_bhyt",
                "alias_mapping",
                "BHYT của trẻ em hộ nghèo là gì?",
                gold_base(
                    intent="qa_aggregate",
                    can_execute=True,
                    year=2024,
                    target_group="Hộ nghèo",
                    filters=[{"field": "classify", "op": "=", "value": "Hộ nghèo"}],
                    group_by=[],
                    metrics=["SUM(children.lackHealthInsuranceCount)"],
                    calculation_type="aggregate",
                    source_table="households",
                    alias_mapping={"BHYT": "children.lackHealthInsuranceCount"},
                ),
                ["alias_mapping_accuracy"],
                "Alias mapping case",
            ),
            qa_case(
                "E2_alias_clean_water",
                "alias_mapping",
                "Thống kê nước sạch.",
                gold_base(
                    intent="qa_aggregate",
                    can_execute=True,
                    year=2024,
                    target_group="Hộ nghèo",
                    filters=[],
                    group_by=[],
                    metrics=["SUM(deprivation.cleanWater)"],
                    calculation_type="aggregate",
                    source_table="households",
                    alias_mapping={"nước sạch": "deprivation.cleanWater"},
                ),
                ["alias_mapping_accuracy"],
                "Alias mapping case",
            ),
            qa_case(
                "E3_alias_hygienic_toilet",
                "alias_mapping",
                "Nhà tiêu hợp vệ sinh.",
                gold_base(
                    intent="qa_aggregate",
                    can_execute=True,
                    year=2024,
                    target_group="Hộ nghèo",
                    filters=[],
                    group_by=[],
                    metrics=["SUM(deprivation.hygienicToilet)"],
                    calculation_type="aggregate",
                    source_table="households",
                    alias_mapping={"nhà tiêu hợp vệ sinh": "deprivation.hygienicToilet"},
                ),
                ["alias_mapping_accuracy"],
                "Alias mapping case",
            ),
            qa_case(
                "E4_alias_ethnic_minority",
                "alias_mapping",
                "Dân tộc thiểu số theo hộ nghèo.",
                gold_base(
                    intent="qa_aggregate",
                    can_execute=True,
                    year=2024,
                    target_group="Hộ nghèo",
                    filters=[],
                    group_by=["family.ethnicity"],
                    metrics=["COUNT(family.code)"],
                    calculation_type="aggregate",
                    source_table="households",
                    alias_mapping={"dân tộc thiểu số": "family.isDTTS"},
                ),
                ["alias_mapping_accuracy"],
                "Alias mapping case",
            ),
            qa_case(
                "E5_alias_no_labor_capacity",
                "alias_mapping",
                "Không có khả năng lao động.",
                gold_base(
                    intent="qa_aggregate",
                    can_execute=True,
                    year=2024,
                    target_group="Hộ nghèo",
                    filters=[],
                    group_by=[],
                    metrics=["COUNT(family.hasNoLaborCapacity)"],
                    calculation_type="aggregate",
                    source_table="households",
                    alias_mapping={"không có khả năng lao động": "family.hasNoLaborCapacity"},
                ),
                ["alias_mapping_accuracy"],
                "Alias mapping case",
            ),
        ]
    )

    specs.extend(
        [
            qa_case(
                "F1_multiturn_deprivation_report_percent",
                "multi_turn",
                None,
                gold_base(
                    intent="generate_report",
                    can_execute=True,
                    report_id=5,
                    year=2024,
                    target_group="Hộ nghèo",
                    calculation_type="percentage",
                    source_table="households",
                    required_columns=REPORT_REQUIRED_COLUMNS[5],
                    output={"type": "xlsx", "template_id": 5, "include_preview": True},
                    turn_states=[
                        {"turn": 1, "can_execute": False, "missing_slots": ["year", "target_group", "calculation_type"]},
                        {"turn": 2, "can_execute": True, "missing_slots": []},
                    ],
                ),
                ["multi_turn_success_rate", "state_update_accuracy", "slot_f1"],
                "Multi-turn case",
                conversation=[
                    {"role": "user", "content": "Tạo báo cáo thiếu hụt dịch vụ xã hội."},
                    {"role": "assistant_expected_behavior", "content": "ask_clarification"},
                    {"role": "user", "content": "Năm 2024, hộ nghèo, tỷ lệ."},
                ],
            ),
            qa_case(
                "F2_multiturn_report_5_missing_year",
                "multi_turn",
                None,
                gold_base(
                    intent="generate_report",
                    can_execute=True,
                    report_id=5,
                    year=2024,
                    target_group="Hộ nghèo",
                    calculation_type="percentage",
                    source_table="households",
                    required_columns=REPORT_REQUIRED_COLUMNS[5],
                    output={"type": "xlsx", "template_id": 5, "include_preview": True},
                    turn_states=[
                        {"turn": 1, "can_execute": False, "missing_slots": ["year"]},
                        {"turn": 2, "can_execute": True, "missing_slots": []},
                    ],
                ),
                ["multi_turn_success_rate", "state_update_accuracy", "slot_f1"],
                "Multi-turn case",
                conversation=[
                    {"role": "user", "content": "Cho tôi báo cáo mẫu 5."},
                    {"role": "assistant_expected_behavior", "content": "ask_clarification"},
                    {"role": "user", "content": "Năm 2024."},
                ],
            ),
            qa_case(
                "F3_multiturn_add_location_later",
                "multi_turn",
                None,
                gold_base(
                    intent="qa_aggregate",
                    can_execute=True,
                    year=2024,
                    target_group="Hộ nghèo",
                    filters=[{"field": "administrative.district", "op": "=", "value": "Gia Nghĩa"}],
                    group_by=["administrative.district"],
                    metrics=["COUNT(family.code)"],
                    calculation_type="aggregate",
                    source_table="households",
                    turn_states=[
                        {"turn": 1, "can_execute": True, "filters": []},
                        {"turn": 2, "can_execute": True, "filters": [{"field": "administrative.district", "op": "=", "value": "Gia Nghĩa"}]},
                    ],
                ),
                ["multi_turn_success_rate", "state_update_accuracy", "slot_f1"],
                "Multi-turn case",
                conversation=[
                    {"role": "user", "content": "Thống kê hộ nghèo năm 2024."},
                    {"role": "assistant_expected_behavior", "content": "propose_plan"},
                    {"role": "user", "content": "Chỉ ở Gia Nghĩa."},
                ],
            ),
            qa_case(
                "F4_multiturn_change_target_group",
                "multi_turn",
                None,
                gold_base(
                    intent="generate_report",
                    can_execute=True,
                    report_id=7,
                    year=2024,
                    target_group="Hộ cận nghèo",
                    calculation_type="percentage",
                    source_table="households",
                    required_columns=REPORT_REQUIRED_COLUMNS[7],
                    output={"type": "xlsx", "template_id": 7, "include_preview": True},
                    turn_states=[
                        {"turn": 1, "can_execute": True, "target_group": "Hộ nghèo"},
                        {"turn": 2, "can_execute": True, "target_group": "Hộ cận nghèo"},
                    ],
                ),
                ["multi_turn_success_rate", "state_update_accuracy", "slot_f1"],
                "Multi-turn case",
                conversation=[
                    {"role": "user", "content": "Báo cáo thiếu hụt hộ nghèo năm 2024."},
                    {"role": "assistant_expected_behavior", "content": "confirm_plan"},
                    {"role": "user", "content": "Đổi thành hộ cận nghèo."},
                ],
            ),
            qa_case(
                "F5_multiturn_remove_commune_grouping",
                "multi_turn",
                None,
                gold_base(
                    intent="qa_aggregate",
                    can_execute=True,
                    year=2024,
                    target_group="Hộ nghèo",
                    filters=[],
                    group_by=["administrative.district"],
                    metrics=["RATE(deprivation.hygienicToilet)"],
                    calculation_type="percentage",
                    source_table="households",
                    turn_states=[
                        {"turn": 1, "group_by": ["administrative.commune"]},
                        {"turn": 2, "group_by": ["administrative.district"]},
                    ],
                ),
                ["multi_turn_success_rate", "state_update_accuracy", "slot_f1"],
                "Multi-turn case",
                conversation=[
                    {"role": "user", "content": "Top xã thiếu nhà tiêu hợp vệ sinh năm 2024."},
                    {"role": "assistant_expected_behavior", "content": "propose_plan"},
                    {"role": "user", "content": "Bỏ cấp xã, chỉ group theo huyện."},
                ],
            ),
        ]
    )

    specs.extend(
        [
            qa_case(
                "G1_response_top_district_dataframe",
                "response_composer",
                "Năm 2024, huyện/thành phố nào có số hộ nghèo nhiều nhất?",
                gold_base(
                    intent="qa_aggregate",
                    can_execute=True,
                    year=2024,
                    target_group="Hộ nghèo",
                    filters=[{"field": "classify", "op": "=", "value": "Hộ nghèo"}],
                    group_by=["administrative.district"],
                    metrics=["COUNT(family.code)"],
                    calculation_type="aggregate",
                    source_table="households",
                    executor_fixture={"result_table": [{"administrative.district": "Gia Nghĩa", "count": 10}]},
                    expected_response="Gia Nghĩa có số hộ nghèo nhiều nhất.",
                ),
                ["answer_groundedness", "response_correctness"],
                "Response composer case",
            ),
            qa_case(
                "G2_response_report_5_preview",
                "response_composer",
                "Tạo báo cáo mẫu 5 năm 2024.",
                gold_base(
                    intent="generate_report",
                    can_execute=True,
                    report_id=5,
                    year=2024,
                    target_group="Hộ nghèo",
                    calculation_type="percentage",
                    source_table="households",
                    required_columns=REPORT_REQUIRED_COLUMNS[5],
                    output={"type": "xlsx", "template_id": 5, "include_preview": True},
                    executor_fixture={"preview_rows": [{"report_id": 5, "status": "ok"}]},
                    expected_response="Đã tạo báo cáo mẫu 5 với phần xem trước.",
                ),
                ["answer_groundedness", "response_correctness"],
                "Response composer case",
            ),
            qa_case(
                "G3_response_empty_result",
                "response_composer",
                "Tìm dữ liệu không tồn tại.",
                gold_base(
                    intent="qa_aggregate",
                    can_execute=True,
                    year=2024,
                    target_group="Hộ nghèo",
                    filters=[],
                    group_by=[],
                    metrics=["COUNT(family.code)"],
                    calculation_type="aggregate",
                    source_table="households",
                    executor_fixture={"result_table": []},
                    expected_response="Không tìm thấy dữ liệu phù hợp.",
                ),
                ["answer_groundedness", "response_correctness"],
                "Response composer case",
            ),
            qa_case(
                "G4_response_validator_fail",
                "response_composer",
                "Kiểm tra lỗi validator.",
                gold_base(
                    intent="generate_report",
                    can_execute=False,
                    missing_slots=["year"],
                    source_table="households",
                    executor_fixture={"validation_error": "Missing year"},
                    expected_response="Không thể tạo báo cáo vì thiếu năm.",
                ),
                ["answer_groundedness", "response_correctness"],
                "Response composer case",
            ),
            qa_case(
                "G5_response_ambiguous_result",
                "response_composer",
                "Kết quả mơ hồ.",
                gold_base(
                    intent="qa_aggregate",
                    can_execute=True,
                    year=2024,
                    target_group="Hộ nghèo",
                    filters=[],
                    group_by=[],
                    metrics=["COUNT(family.code)"],
                    calculation_type="aggregate",
                    source_table="households",
                    executor_fixture={"result_table": [{"status": "ambiguous"}]},
                    expected_response="Kết quả chưa rõ ràng, cần xác nhận thêm.",
                ),
                ["answer_groundedness", "response_correctness"],
                "Response composer case",
            ),
        ]
    )

    return specs


def write_default_cases_file(cases_path: Path) -> None:
    cases_path.parent.mkdir(parents=True, exist_ok=True)
    specs = build_default_case_specs()
    with cases_path.open("w", encoding="utf-8") as handle:
        for case in specs:
            handle.write(json.dumps(case, ensure_ascii=False) + "\n")


def ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def main() -> None:
    args = parse_args()
    load_dotenv_file(PROJECT_ROOT)

    cases_path = Path(args.cases)
    if args.bootstrap_cases or not cases_path.exists():
        write_default_cases_file(cases_path)

    output_dir = Path(args.output_dir)
    ensure_output_dir(output_dir)

    metadata = load_metadata(PROJECT_ROOT)
    allowed = load_allowed_columns(PROJECT_ROOT, metadata)
    cases = load_cases(cases_path)
    models = [item.strip() for item in args.models.split(",") if item.strip()]

    raw_log_path = output_dir / "raw_logs.jsonl"
    summary_case_path = output_dir / "summary_by_case.csv"
    summary_model_path = output_dir / "summary_by_model.csv"
    if raw_log_path.exists():
        raw_log_path.unlink()

    case_rows: list[dict[str, Any]] = []
    for model_name in models:
        config = resolve_model_config(model_name)
        for index, case in enumerate(cases):
            system_prompt = build_system_prompt(metadata, allowed)
            case_prompt = build_case_prompt(case, metadata, allowed)
            started = time.perf_counter()
            if args.dry_run or config["provider"] == "mock":
                mock_result = call_model_mock(model_name, case, index)
                raw_response = mock_result["raw_response"]
                latency_ms = mock_result["latency_ms"]
                retry_count = mock_result["retry_count"]
                forced_parsed = mock_result.get("forced_parsed")
                live_error = None
                live_url = None
            else:
                live_result = call_model_live(
                    config,
                    system_prompt,
                    case_prompt,
                    args.timeout_ms,
                    args.temperature,
                    args.max_retries,
                )
                raw_response = live_result.get("raw_response", "")
                latency_ms = int(live_result.get("latency_ms", int((time.perf_counter() - started) * 1000)))
                retry_count = int(live_result.get("retry_count", 0))
                forced_parsed = None
                live_error = live_result.get("error")
                live_url = live_result.get("url")

            parsed, parse_error = parse_model_json(raw_response) if forced_parsed is None else (forced_parsed, None)
            if parse_error is None and live_error and not raw_response:
                parse_error = live_error
            if parsed is not None:
                parsed = normalize_model_output(parsed)
            schema_error = None
            if parsed is not None:
                schema_ok, schema_error = validate_schema(parsed)
                if not schema_ok:
                    schema_error = schema_error or "Schema validation failed."
            metrics = score_case(
                case,
                parsed,
                metadata,
                allowed,
                parse_error,
                schema_error,
                latency_ms,
                retry_count,
            )
            passed = 1
            for metric_name in case["required_metrics"]:
                metric_value = metrics.get(metric_name, 0.0)
                if metric_name == "false_execution_rate":
                    if metric_value > 0.0:
                        passed = 0
                elif metric_value < 0.999:
                    passed = 0

            case_row = {
                "model": model_name,
                "case_id": case["case_id"],
                "category": case["category"],
                "intent_accuracy": metrics["intent_accuracy"],
                "slot_precision": metrics["slot_precision"],
                "slot_recall": metrics["slot_recall"],
                "slot_f1": metrics["slot_f1"],
                "alias_mapping_accuracy": metrics["alias_mapping_accuracy"],
                "missing_slot_recall": metrics["missing_slot_recall"],
                "no_assumption_rate": metrics["no_assumption_rate"],
                "false_execution_rate": metrics["false_execution_rate"],
                "report_id_accuracy": metrics["report_id_accuracy"],
                "json_validity": metrics["json_validity_rate"],
                "schema_compliance": metrics["schema_compliance_rate"],
                "exact_plan_match": metrics["exact_plan_match"],
                "required_columns_coverage": metrics["required_columns_coverage"],
                "formula_type_accuracy": metrics["formula_type_accuracy"],
                "source_selection_accuracy": metrics["source_selection_accuracy"],
                "multi_turn_success": metrics["multi_turn_success_rate"],
                "answer_groundedness": metrics["answer_groundedness"],
                "latency_ms": metrics["latency_ms"],
                "passed": passed,
                "json_validity_rate": metrics["json_validity_rate"],
                "schema_compliance_rate": metrics["schema_compliance_rate"],
                "multi_turn_success_rate": metrics["multi_turn_success_rate"],
                "state_update_accuracy": metrics["state_update_accuracy"],
                "response_correctness": metrics["response_correctness"],
                "invalid_column_rate": metrics["invalid_column_rate"],
                "retry_count": metrics["retry_count"],
                "parse_error": parse_error,
                "schema_error": schema_error,
                "response_error": live_error,
                "request_url": live_url,
            }
            case_rows.append(case_row)
            append_raw_log(
                raw_log_path,
                {
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "model": model_name,
                    "case_id": case["case_id"],
                    "category": case["category"],
                    "user_input": case.get("user_input"),
                    "conversation": case.get("conversation"),
                    "prompt_sent": system_prompt + "\n\n" + case_prompt,
                    "raw_response": raw_response,
                    "parsed_response": parsed,
                    "parse_error": parse_error,
                    "schema_error": schema_error,
                    "response_error": live_error,
                    "request_url": live_url,
                    "metrics": metrics,
                    "latency_ms": latency_ms,
                    "retry_count": retry_count,
                },
            )

    write_summary_by_case(summary_case_path, case_rows)
    model_rows = aggregate_model_scores(case_rows)
    write_summary_by_model(summary_model_path, model_rows)


if __name__ == "__main__":
    main()
