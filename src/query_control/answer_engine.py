# -*- coding: utf-8 -*-
"""
Module Answer Engine điều phối luồng Q&A từ phân loại, lập kế hoạch,
truy vấn dữ liệu qua DuckDB, quản lý cache, ghi vết observability và sinh câu trả lời.
"""

from __future__ import annotations
import os
import sys
import json
import time
from pathlib import Path
from typing import Any
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "Processed"
METADATA_DIR = PROCESSED_DIR / "metadata"
QUERY_CONTROL_METADATA_DIR = METADATA_DIR / "query_control"

sys.path.append(str(PROJECT_ROOT))
from typing import Any
from src.query_control.llm_helper import call_llm, clean_json_response

class ChatbotAnswerEngine:
    def __init__(
        self,
        domain_gate: Any,
        query_planner: Any,
        sql_compiler: Any,
        data_engine: Any,
        query_cache: Any,
        observability_logger: Any,
        clarification_engine: Any,
        conversation_memory: Any,
        general_answer_engine: Any = None
    ):
        """Khởi tạo Chatbot Answer Engine với đầy đủ các thành phần bổ trợ."""
        self.domain_gate = domain_gate
        self.query_planner = query_planner
        self.sql_compiler = sql_compiler
        self.data_engine = data_engine
        self.query_cache = query_cache
        self.observability_logger = observability_logger
        self.clarification_engine = clarification_engine
        self.conversation_memory = conversation_memory
        self.general_answer_engine = general_answer_engine
        
        # Tải cấu hình prompt giải thích kiến thức chung
        self.general_prompt_path = QUERY_CONTROL_METADATA_DIR / "general_answer_prompt.md"
        with open(self.general_prompt_path, "r", encoding="utf-8") as f:
            self.general_prompt_tmpl = f.read()

    def answer(self, user_question: str) -> dict[str, Any]:
        """Xử lý câu hỏi của người dùng theo luồng MVP hoàn chỉnh."""
        # 1. Khởi tạo trace ghi vết
        trace_id = self.observability_logger.start_trace(user_question)
        start_time = time.perf_counter()
        
        try:
            # 2. Tải bộ nhớ hội thoại và đo thời gian
            mem_start = time.perf_counter()
            self.observability_logger.log_event(trace_id, "conversation_memory_load", {"status": "loading"})
            memory_context = self.conversation_memory.load()
            mem_latency = (time.perf_counter() - mem_start) * 1000.0
            self.observability_logger.log_latency(trace_id, "conversation_memory_load", mem_latency)
            
            # 3. Rút trích đặc trưng dựa trên luật, giải quyết câu hỏi kế thừa và đo thời gian
            rule_start = time.perf_counter()
            rule_output = self.query_planner.apply_rule_extraction(user_question)
            self.observability_logger.log_event(trace_id, "rule_extractor", rule_output)
            
            follow_up_context = self.conversation_memory.resolve_follow_up(user_question, rule_output)
            if follow_up_context:
                self.observability_logger.log_event(trace_id, "conversation_memory", {"follow_up_context": follow_up_context})
            rule_latency = (time.perf_counter() - rule_start) * 1000.0
            self.observability_logger.log_latency(trace_id, "rule_extractor", rule_latency)

            # 4. Định tuyến câu hỏi qua Domain Gate và đo thời gian
            gate_start = time.perf_counter()
            if follow_up_context:
                route = "DATASET_QA"
                self.observability_logger.log_event(trace_id, "domain_gate", {
                    "route": route,
                    "confidence": 1.0,
                    "reason": "Kế thừa định tuyến từ câu hỏi trước (Follow-up)"
                })
            else:
                gate_res = self.domain_gate.classify(user_question)
                route = gate_res.get("route", "OUT_OF_SCOPE")
                self.observability_logger.log_event(trace_id, "domain_gate", {
                    "route": route,
                    "confidence": gate_res.get("confidence"),
                    "reason": gate_res.get("reason")
                })
            gate_latency = (time.perf_counter() - gate_start) * 1000.0
            self.observability_logger.log_latency(trace_id, "domain_gate", gate_latency)

            # Rẽ nhánh định tuyến:
            
            # Nhánh 4.1: CLARIFICATION_NEEDED
            if route == "CLARIFICATION_NEEDED":
                clarification = self.clarification_engine.build_clarification(["ROUTE_UNCERTAIN"], {})
                clarification["route"] = "CLARIFICATION_NEEDED"
                self.conversation_memory.add_turn(user_question, clarification)
                self.observability_logger.finish_trace(trace_id, clarification)
                return clarification
                
            # Nhánh 4.2: OUT_OF_SCOPE
            elif route == "OUT_OF_SCOPE":
                refusal_response = {
                    "route": "OUT_OF_SCOPE",
                    "answer": "Xin lỗi, tôi chỉ hỗ trợ trả lời các câu hỏi nghiệp vụ và truy vấn số liệu liên quan đến rà soát hộ nghèo, hộ cận nghèo tỉnh Đắk Nông năm 2023 - 2024. Vui lòng đặt câu hỏi khác phù hợp hơn.",
                    "query_plan": None,
                    "sql": None,
                    "result_preview": [],
                    "row_count": 0,
                    "cache": {"hit": False, "key": None},
                    "warnings": [],
                    "errors": []
                }
                self.conversation_memory.add_turn(user_question, refusal_response)
                self.observability_logger.finish_trace(trace_id, refusal_response)
                return refusal_response
                
            # Nhánh 4.3: GENERAL_KNOWLEDGE
            elif route == "GENERAL_KNOWLEDGE":
                gk_start = time.perf_counter()
                self.observability_logger.log_event(trace_id, "general_knowledge", {"status": "processing"})
                gk_answer = ""
                errors_list = []
                
                # Gọi general answer engine nếu có
                if self.general_answer_engine:
                    try:
                        gk_answer = self.general_answer_engine.answer(user_question)
                    except Exception as e:
                        errors_list.append({"code": "GK_ENGINE_FAILED", "message": str(e)})
                        
                # Fallback sang gọi LLM trực tiếp
                if not gk_answer:
                    try:
                        system_prompt = self.general_prompt_tmpl
                        raw_res = call_llm(
                            system_prompt=system_prompt,
                            user_prompt=f"Câu hỏi: {user_question}",
                            temperature=0.2,
                            response_json=True
                        )
                        res_dict = clean_json_response(raw_res)
                        
                        # Hỗ trợ chuyển hướng động sang DATASET_QA nếu LLM nhận ra cần số liệu
                        if res_dict.get("needs_dataset_query"):
                            route = "DATASET_QA"
                            self.observability_logger.log_event(trace_id, "domain_gate", {"route_override": "DATASET_QA", "reason": "General Knowledge LLM redirected to Dataset Q&A"})
                            gk_latency = (time.perf_counter() - gk_start) * 1000.0
                            self.observability_logger.log_latency(trace_id, "general_knowledge", gk_latency)
                        else:
                            gk_answer = res_dict.get("answer", "Không tìm thấy câu trả lời phù hợp.")
                    except Exception as e:
                        errors_list.append({"code": "GK_LLM_FAILED", "message": str(e)})
                        gk_answer = "Có lỗi xảy ra khi xử lý kiến thức nghiệp vụ. Vui lòng thử lại sau."
                
                if route == "GENERAL_KNOWLEDGE":
                    gk_response = {
                        "route": "GENERAL_KNOWLEDGE",
                        "answer": gk_answer,
                        "query_plan": None,
                        "sql": None,
                        "result_preview": [],
                        "row_count": 0,
                        "cache": {"hit": False, "key": None},
                        "warnings": [],
                        "errors": errors_list
                    }
                    gk_latency = (time.perf_counter() - gk_start) * 1000.0
                    self.observability_logger.log_latency(trace_id, "general_knowledge", gk_latency)
                    self.conversation_memory.add_turn(user_question, gk_response)
                    self.observability_logger.finish_trace(trace_id, gk_response)
                    return gk_response
                    
            if route in ["DATASET_QA", "HYBRID"]:
                # Tra cứu Cache Query Plan trước (Quy tắc 2: Chú thích tiếng Việt)
                planner_start = time.perf_counter()
                self.observability_logger.log_event(trace_id, "planner", {"status": "generating"})
                
                query_plan = self.query_cache.get_query_plan(user_question)
                cache_plan_hit = False
                
                if query_plan:
                    cache_plan_hit = True
                    self.observability_logger.log_event(trace_id, "planner", {"cache_hit": True, "query_plan": query_plan})
                else:
                    query_plan = self.query_planner.plan(user_question)
                    if query_plan and query_plan.get("task_type") != "unknown":
                        self.query_cache.set_query_plan(user_question, query_plan)
                
                # Áp dụng kế thừa follow-up nếu phát hiện
                if follow_up_context:
                    query_plan = self._merge_follow_up_context(query_plan, follow_up_context)
                    self.observability_logger.log_event(trace_id, "planner", {"merged_query_plan": query_plan})
                    
                self.observability_logger.log_event(trace_id, "query_plan_validation", {"plan": query_plan})
                
                # Kiểm định Query Plan
                errors = self.query_planner.validate_query_plan(query_plan)
                planner_latency = (time.perf_counter() - planner_start) * 1000.0
                self.observability_logger.log_latency(trace_id, "planner", planner_latency)
                
                # Các lỗi nghiêm trọng khiến không thể chạy SQL
                severe_error_codes = ["METRIC_NOT_FOUND", "METRIC_EMPTY", "MISSING_TIME_FILTER", "DIMENSION_NOT_FOUND", "LOW_RETRIEVAL_CONFIDENCE", "ROUTE_UNCERTAIN"]
                has_severe_error = any(e.get("code") in severe_error_codes for e in errors) if isinstance(errors, list) else False
                
                # Chuyển tiếp sang Clarification Engine nếu có lỗi nghiêm trọng
                if has_severe_error or query_plan.get("task_type") == "unknown":
                    errs_to_clarify = errors if errors else [{"code": "LOW_RETRIEVAL_CONFIDENCE", "message": "Độ tin cậy thấp"}]
                    clarification = self.clarification_engine.build_clarification(errs_to_clarify, {"query_plan": query_plan})
                    clarification["route"] = "CLARIFICATION_NEEDED"
                    
                    self.conversation_memory.add_turn(user_question, clarification)
                    self.observability_logger.finish_trace(trace_id, clarification)
                    return clarification
                    
                # 5. Tra cứu Cache kết quả và đo thời gian
                cache_start = time.perf_counter()
                self.observability_logger.log_event(trace_id, "cache_lookup", {"status": "searching"})
                cache_key = self.query_cache.make_query_plan_hash(query_plan)
                cached_res = self.query_cache.get_sql_result(query_plan)
                
                sql = ""
                result = None
                cache_hit = False
                
                if cached_res:
                    cache_hit = True
                    result = cached_res
                    sql = cached_res.get("sql", "")
                    self.observability_logger.log_event(trace_id, "cache_lookup", {"cache_hit": True, "cache_key": cache_key})
                else:
                    self.observability_logger.log_event(trace_id, "cache_lookup", {"cache_hit": False, "cache_key": cache_key})
                cache_latency = (time.perf_counter() - cache_start) * 1000.0
                self.observability_logger.log_latency(trace_id, "cache_lookup", cache_latency)
                    
                if not cached_res:
                    # Biên dịch SQL và đo thời gian
                    compiler_start = time.perf_counter()
                    self.observability_logger.log_event(trace_id, "sql_compiler", {"status": "compiling"})
                    try:
                        sql = self.sql_compiler.compile(query_plan)
                        self.observability_logger.log_event(trace_id, "sql_compiler", {"sql": sql})
                        compiler_latency = (time.perf_counter() - compiler_start) * 1000.0
                        self.observability_logger.log_latency(trace_id, "sql_compiler", compiler_latency)
                    except Exception as e:
                        compiler_latency = (time.perf_counter() - compiler_start) * 1000.0
                        self.observability_logger.log_latency(trace_id, "sql_compiler", compiler_latency)
                        err_res = {
                            "route": route,
                            "answer": f"Biên dịch SQL thất bại: {e}",
                            "query_plan": query_plan,
                            "sql": None,
                            "result_preview": [],
                            "row_count": 0,
                            "cache": {"hit": False, "key": cache_key},
                            "warnings": [],
                            "errors": [{"code": "SQL_COMPILE_FAILED", "message": str(e)}]
                        }
                        self.observability_logger.log_error(trace_id, "sql_compiler", {"code": "SQL_COMPILE_FAILED", "message": str(e)})
                        self.conversation_memory.add_turn(user_question, err_res)
                        self.observability_logger.finish_trace(trace_id, err_res)
                        return err_res
                        
                    # Kiểm định an toàn SQL
                    sql_errors = self.sql_compiler.validate_sql(sql)
                    if sql_errors:
                        err_res = {
                            "route": route,
                            "answer": "Câu SQL được tạo ra vi phạm chính sách bảo mật hệ thống và không thể thực thi.",
                            "query_plan": query_plan,
                            "sql": sql,
                            "result_preview": [],
                            "row_count": 0,
                            "cache": {"hit": False, "key": cache_key},
                            "warnings": [],
                            "errors": sql_errors
                        }
                        self.observability_logger.log_error(trace_id, "sql_validation", {"errors": sql_errors})
                        self.conversation_memory.add_turn(user_question, err_res)
                        self.observability_logger.finish_trace(trace_id, err_res)
                        return err_res
                        
                    # Thực thi SQL trên DuckDB Engine và đo thời gian
                    self.observability_logger.log_event(trace_id, "duckdb_execution", {"status": "executing", "sql": sql})
                    sql_start = time.perf_counter()
                    result = self.data_engine.execute_sql(sql)
                    sql_latency = (time.perf_counter() - sql_start) * 1000.0
                    self.observability_logger.log_latency(trace_id, "duckdb_execution", sql_latency)
                    
                    if not result["success"]:
                        err_res = {
                            "route": route,
                            "answer": f"Thực thi cơ sở dữ liệu thất bại: {result['error']}",
                            "query_plan": query_plan,
                            "sql": sql,
                            "result_preview": [],
                            "row_count": 0,
                            "cache": {"hit": False, "key": cache_key},
                            "warnings": result["warnings"],
                            "errors": [{"code": "DB_EXECUTION_FAILED", "message": result["error"]}]
                        }
                        self.observability_logger.log_error(trace_id, "duckdb_execution", {"code": "DB_EXECUTION_FAILED", "message": result["error"]})
                        self.conversation_memory.add_turn(user_question, err_res)
                        self.observability_logger.finish_trace(trace_id, err_res)
                        return err_res
                        
                    # Ghi nhận kết quả vào cache
                    self.query_cache.set_sql_result(query_plan, result)
                    
                # 6. Định dạng câu trả lời tự nhiên và đo thời gian
                format_start = time.perf_counter()
                self.observability_logger.log_event(trace_id, "answer_formatting", {"status": "formatting"})
                cache_meta = result.get("cache_metadata") if cache_hit else None
                
                final_answer = format_dataset_answer(
                    user_question=user_question,
                    query_plan=query_plan,
                    sql=sql,
                    result=result,
                    cache_metadata=cache_meta
                )
                final_answer["route"] = route
                format_latency = (time.perf_counter() - format_start) * 1000.0
                self.observability_logger.log_latency(trace_id, "answer_formatting", format_latency)
                
                # 7. Cập nhật bộ nhớ hội thoại, đo thời gian và hoàn thành trace
                memory_update_start = time.perf_counter()
                self.conversation_memory.add_turn(user_question, final_answer)
                self.observability_logger.log_event(trace_id, "conversation_memory_update", {"status": "success"})
                memory_update_latency = (time.perf_counter() - memory_update_start) * 1000.0
                self.observability_logger.log_latency(trace_id, "conversation_memory_update", memory_update_latency)
                self.observability_logger.finish_trace(trace_id, final_answer)
                
                return final_answer
                
        except Exception as e:
            err_res = {
                "route": "ERROR",
                "answer": f"Lỗi hệ thống nghiêm trọng: {e}",
                "query_plan": None,
                "sql": None,
                "result_preview": [],
                "row_count": 0,
                "cache": {"hit": False, "key": None},
                "warnings": [],
                "errors": [{"code": "CRITICAL_SYSTEM_ERROR", "message": str(e)}]
            }
            self.observability_logger.log_error(trace_id, "runtime_answer", {"code": "CRITICAL_SYSTEM_ERROR", "message": str(e)})
            self.conversation_memory.add_turn(user_question, err_res)
            self.observability_logger.finish_trace(trace_id, err_res)
            return err_res

    def _merge_follow_up_context(self, query_plan: dict[str, Any], follow_up_context: dict[str, Any]) -> dict[str, Any]:
        """Hợp nhất thông tin câu kế thừa với câu kế hoạch hiện tại."""
        merged = follow_up_context.copy()
        
        # Override bằng các trường hợp lệ từ query_plan mới sinh
        if query_plan.get("task_type") and query_plan["task_type"] != "unknown":
            merged["task_type"] = query_plan["task_type"]
            
        if query_plan.get("metrics"):
            merged["metrics"] = query_plan["metrics"]
            
        if query_plan.get("dimensions"):
            merged["dimensions"] = query_plan["dimensions"]
            
        if query_plan.get("filters"):
            # Gộp các bộ lọc: nếu trùng field thì ghi đè bằng giá trị mới
            existing_fields = {f.get("field") for f in query_plan["filters"] if isinstance(f, dict)}
            merged_filters = [f for f in merged.get("filters", []) if isinstance(f, dict) and f.get("field") not in existing_fields]
            merged_filters.extend(query_plan["filters"])
            merged["filters"] = merged_filters
            
        if query_plan.get("sort"):
            merged["sort"] = query_plan["sort"]
            
        if query_plan.get("limit"):
            merged["limit"] = query_plan["limit"]
            
        return merged

    def _format_dataset_answer(self, question: str, sql: str, df: pd.DataFrame, is_hybrid: bool) -> str:
        """Gọi LLM sinh câu trả lời tự nhiên từ kết quả truy vấn. (Được giữ lại để tương thích ngược)"""
        # Chuyển dataframe kết quả sang dạng markdown hoặc JSON chuỗi tinh gọn
        try:
            res_str = df.to_markdown(index=False)
        except Exception:
            # Fallback thủ công nếu thiếu thư viện tabulate
            headers = list(df.columns)
            header_str = "| " + " | ".join(map(str, headers)) + " |"
            sep_str = "| " + " | ".join(["---"] * len(headers)) + " |"
            row_strs = []
            for _, row in df.iterrows():
                row_strs.append("| " + " | ".join(map(str, row.values)) + " |")
            res_str = "\n".join([header_str, sep_str] + row_strs)
        
        system_prompt = (
            "Bạn là chuyên gia phân tích dữ liệu rà soát hộ nghèo tỉnh Đắk Nông.\n"
            "Nhiệm vụ của bạn là sinh câu trả lời tự nhiên bằng tiếng Việt dựa vào câu hỏi của người dùng và bảng kết quả truy vấn thực tế dưới đây.\n\n"
            "Quy tắc bắt buộc:\n"
            "1. Chỉ sử dụng số liệu có sẵn trong kết quả truy vấn, tuyệt đối không tự bịa thêm bất cứ số liệu nào khác.\n"
            "2. Trả lời ngắn gọn, chính xác, trực diện câu hỏi.\n"
            "3. Trình bày rõ ràng, dễ hiểu. Nếu có danh sách nhiều dòng, hãy trình bày dạng bảng markdown hoặc gạch đầu dòng.\n"
            "4. Không đưa ra nhận định chủ quan ngoài phạm vi dữ liệu cung cấp.\n"
        )
        
        if is_hybrid:
            system_prompt += "5. Kết hợp giải thích thêm một chút về mặt khái niệm nghiệp vụ liên quan đến kết quả nếu người dùng có yêu cầu trong câu hỏi.\n"
            
        user_prompt = (
            f"Câu hỏi: {question}\n\n"
            f"Kết quả truy vấn thực tế:\n"
            f"{res_str}\n\n"
            f"Câu trả lời của bạn:"
        )
        
        try:
            return call_llm(system_prompt, user_prompt, temperature=0.1)
        except Exception as e:
            if len(df) == 1:
                vals = df.iloc[0].to_dict()
                val_strs = [f"{k}: {v}" for k, v in vals.items()]
                return f"Kết quả truy vấn: {', '.join(val_strs)}"
            else:
                return f"Kết quả truy vấn:\n{res_str}"


def format_dataset_answer(
    user_question: str,
    query_plan: dict[str, Any],
    sql: str,
    result: dict[str, Any],
    cache_metadata: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Hàm định dạng kết quả truy vấn Dataset thành câu trả lời tự nhiên dạng JSON có cấu trúc.
    """
    output = {
        "route": "DATASET_QA",
        "answer": "",
        "query_plan": query_plan,
        "sql": sql,
        "result_preview": [],
        "row_count": 0,
        "cache": {
            "hit": False,
            "key": None
        },
        "warnings": [],
        "errors": []
    }
    
    # 1. Cập nhật cache metadata
    if cache_metadata:
        output["cache"]["hit"] = cache_metadata.get("cache_hit", False)
        output["cache"]["key"] = cache_metadata.get("cache_key")
        
    if not result.get("success", True):
        output["errors"].append({"code": "DB_EXECUTION_FAILED", "message": result.get("error", "Lỗi DB không xác định")})
        output["answer"] = f"Không thể lấy kết quả do lỗi truy vấn: {result.get('error')}"
        return output
        
    data = result.get("data", [])
    output["row_count"] = len(data)
    output["result_preview"] = data[:100]  # Giới hạn preview 100 dòng
    
    # 2. Xử lý kết quả rỗng
    if not data:
        output["answer"] = "Không tìm thấy số liệu phù hợp với yêu cầu của bạn trong cơ sở dữ liệu."
        output["warnings"].append({"code": "EMPTY_RESULT", "message": "Truy vấn trả về kết quả rỗng."})
        return output
        
    # 3. Tạo bảng kết quả dưới dạng Markdown String
    df = pd.DataFrame(data)
    try:
        res_str = df.to_markdown(index=False)
    except Exception:
        headers = list(df.columns)
        header_str = "| " + " | ".join(map(str, headers)) + " |"
        sep_str = "| " + " | ".join(["---"] * len(headers)) + " |"
        row_strs = []
        for _, row in df.iterrows():
            row_strs.append("| " + " | ".join(map(str, row.values)) + " |")
        res_str = "\n".join([header_str, sep_str] + row_strs)
        
    # 4. Gọi LLM sinh câu trả lời tự nhiên bằng Tiếng Việt
    system_prompt = (
        "Bạn là chuyên gia phân tích dữ liệu rà soát hộ nghèo tỉnh Đắk Nông.\n"
        "Nhiệm vụ của bạn là sinh câu trả lời tự nhiên bằng tiếng Việt dựa vào câu hỏi của người dùng và bảng kết quả truy vấn thực tế dưới đây.\n\n"
        "Quy tắc bắt buộc:\n"
        "1. Chỉ sử dụng số liệu có sẵn trong kết quả truy vấn, tuyệt đối không tự bịa thêm số liệu khác.\n"
        "2. Trả lời ngắn gọn, chính xác, trực diện câu hỏi.\n"
        "3. Trình bày rõ ràng, dễ hiểu. Dùng bảng markdown hoặc liệt kê gạch đầu dòng khi có nhiều đơn vị.\n"
        "4. Không đưa ra nhận định chủ quan ngoài phạm vi dữ liệu cung cấp.\n"
    )
    
    # Gắn thông tin cache nếu hit
    if output["cache"]["hit"]:
        system_prompt += "\nLưu ý: Dữ liệu này được phục vụ trực tiếp từ cache hệ thống.\n"
        
    user_prompt = (
        f"Câu hỏi: {user_question}\n\n"
        f"Kết quả truy vấn thực tế:\n"
        f"{res_str}\n\n"
        f"Câu trả lời của bạn:"
    )
    
    try:
        natural_answer = call_llm(system_prompt, user_prompt, temperature=0.1)
        output["answer"] = natural_answer
    except Exception as e:
        # Fallback nếu gọi LLM lỗi
        if len(df) == 1:
            vals = df.iloc[0].to_dict()
            val_strs = [f"{k}: {v}" for k, v in vals.items()]
            output["answer"] = f"Kết quả truy vấn: {', '.join(val_strs)}"
        else:
            output["answer"] = f"Kết quả truy vấn:\n{res_str}"
            
    return output
