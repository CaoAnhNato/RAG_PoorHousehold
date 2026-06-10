# -*- coding: utf-8 -*-
"""
Module Observability chịu trách nhiệm ghi lại log, traces chi tiết từng bước thực thi câu hỏi,
đo lường latency các stage và ghi nhận lỗi để phục vụ việc giám sát và gỡ lỗi hệ thống.
"""

from __future__ import annotations
import os
import json
import time
import uuid
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]

class ObservabilityLogger:
    def __init__(self, config_path: str):
        """Khởi tạo bộ ghi vết Observability."""
        self.config_path = Path(config_path)
        if not self.config_path.is_absolute():
            self.config_path = PROJECT_ROOT / self.config_path
            
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
            
        self.log_dir = PROJECT_ROOT / self.config.get("log_dir", "Runtime/logs")
        self.trace_dir = PROJECT_ROOT / self.config.get("trace_dir", "Runtime/traces")
        
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.trace_dir.mkdir(parents=True, exist_ok=True)
        
        # Tên tệp tin log
        log_files = self.config.get("log_files", {})
        self.events_file = self.log_dir / log_files.get("query_events", "query_events.jsonl")
        self.errors_file = self.log_dir / log_files.get("errors", "errors.jsonl")
        self.latency_file = self.log_dir / log_files.get("latency", "latency.jsonl")
        
        # Lưu các trace đang hoạt động trong bộ nhớ
        self.active_traces = {}

    def start_trace(self, user_question: str) -> str:
        """Bắt đầu một trace mới cho câu hỏi người dùng và trả về trace_id."""
        trace_id = str(uuid.uuid4())
        self.active_traces[trace_id] = {
            "trace_id": trace_id,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "start_time": time.perf_counter(),
            "user_question": user_question,
            "route": "UNKNOWN",
            "query_plan": None,
            "sql": None,
            "cache_hit": False,
            "row_count": 0,
            "latency_total_ms": 0.0,
            "status": "running",
            "errors": [],
            "warnings": [],
            "stages": {}
        }
        return trace_id

    def log_event(self, trace_id: str, stage: str, payload: dict[str, Any]):
        """Ghi nhận sự kiện cho một stage cụ thể trong trace."""
        if trace_id not in self.active_traces:
            return
            
        # Redact các trường nhạy cảm hoặc quá lớn
        redacted_payload = self._redact(payload)
        
        trace = self.active_traces[trace_id]
        if stage not in trace["stages"]:
            trace["stages"][stage] = {}
        trace["stages"][stage].update(redacted_payload)
        
        # Nếu payload chứa các thông tin tổng quan quan trọng, cập nhật thẳng vào trace gốc
        if "route" in payload:
            trace["route"] = payload["route"]
        if "query_plan" in payload:
            trace["query_plan"] = payload["query_plan"]
        if "sql" in payload:
            trace["sql"] = payload["sql"]
        if "cache_hit" in payload:
            trace["cache_hit"] = payload["cache_hit"]
        if "row_count" in payload:
            trace["row_count"] = payload["row_count"]
        if "warnings" in payload:
            trace["warnings"].extend(payload["warnings"])

    def log_error(self, trace_id: str, stage: str, error: dict[str, Any]):
        """Ghi nhận lỗi xảy ra ở một stage."""
        if trace_id not in self.active_traces:
            return
            
        trace = self.active_traces[trace_id]
        err_msg = error.get("message", str(error))
        err_code = error.get("code", "UNKNOWN_ERROR")
        
        # Đưa lỗi vào trace
        trace["errors"].append({
            "stage": stage,
            "code": err_code,
            "message": err_msg
        })
        trace["status"] = "error"
        
        # Ghi riêng vào file errors.jsonl
        if self.config.get("enable_error_logs", True):
            err_log = {
                "trace_id": trace_id,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "stage": stage,
                "code": err_code,
                "message": err_msg,
                "user_question": trace["user_question"]
            }
            self._write_jsonl(self.errors_file, err_log)

    def log_latency(self, trace_id: str, stage: str, latency_ms: float):
        """Ghi nhận thời gian thực thi (latency) của một stage."""
        if trace_id not in self.active_traces:
            return
            
        trace = self.active_traces[trace_id]
        if stage not in trace["stages"]:
            trace["stages"][stage] = {}
        trace["stages"][stage]["latency_ms"] = latency_ms
        
        # Ghi riêng vào file latency.jsonl nếu được cấu hình
        if self.config.get("enable_latency_metrics", True):
            latency_log = {
                "trace_id": trace_id,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "stage": stage,
                "latency_ms": latency_ms
            }
            self._write_jsonl(self.latency_file, latency_log)

    def finish_trace(self, trace_id: str, final_payload: dict[str, Any] | None = None):
        """Kết thúc một trace, tính toán tổng latency và lưu vào tệp query_events.jsonl."""
        if trace_id not in self.active_traces:
            return
            
        trace = self.active_traces[trace_id]
        
        # Cập nhật thông tin cuối
        if final_payload:
            self.log_event(trace_id, "final", final_payload)
            if "status" in final_payload:
                trace["status"] = final_payload["status"]
                
        # Tính toán tổng latency
        end_time = time.perf_counter()
        trace["latency_total_ms"] = (end_time - trace["start_time"]) * 1000.0
        del trace["start_time"]
        
        # Trạng thái cuối nếu không có lỗi
        if trace["status"] == "running":
            trace["status"] = "success"
            
        # Ghi log chính dạng JSONL
        if self.config.get("enable_jsonl_logs", True):
            # Lưu trace thu gọn vào file query_events.jsonl
            summary_log = {
                "trace_id": trace["trace_id"],
                "timestamp": trace["timestamp"],
                "user_question": trace["user_question"],
                "route": trace["route"],
                "query_plan": trace["query_plan"],
                "sql": trace["sql"],
                "cache_hit": trace["cache_hit"],
                "row_count": trace["row_count"],
                "latency_total_ms": trace["latency_total_ms"],
                "status": trace["status"],
                "errors": trace["errors"],
                "warnings": trace["warnings"]
            }
            self._write_jsonl(self.events_file, summary_log)
            
        # Ghi trace đầy đủ vào thư mục traces dưới dạng file json riêng lẻ phục vụ debug sâu
        if self.config.get("enable_debug_payloads", True):
            trace_file = self.trace_dir / f"{trace_id}.json"
            try:
                with open(trace_file, "w", encoding="utf-8") as f:
                    json.dump(trace, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
                
        # Loại bỏ trace khỏi active_traces trong memory
        if trace_id in self.active_traces:
            del self.active_traces[trace_id]

    def _redact(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Loại bỏ hoặc thu gọn các trường dữ liệu nhạy cảm/quá lớn."""
        redact_fields = self.config.get("redact_fields", ["full_raw_rows", "stack_trace"])
        copied_payload = {}
        
        for k, v in payload.items():
            if k in redact_fields:
                copied_payload[k] = "[REDACTED]"
            elif k == "data" and isinstance(v, list):
                # Chỉ giữ tối đa 20 dòng preview
                copied_payload["result_preview"] = v[:20]
                copied_payload["row_count_actual"] = len(v)
            else:
                copied_payload[k] = v
                
        return copied_payload

    def _write_jsonl(self, filepath: Path, data: dict[str, Any]):
        """Ghi một dòng JSONL an toàn."""
        try:
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
        except Exception:
            pass
