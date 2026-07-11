# -*- coding: utf-8 -*-
from __future__ import annotations
import sys
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
import time
from pathlib import Path
import os
import warnings
import logging

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_EXPERIMENTAL_WARNING"] = "1"
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"

warnings.filterwarnings("ignore", message=".*unauthenticated requests.*")
warnings.filterwarnings("ignore", message=".*Accessing.*__path__.*")
warnings.filterwarnings("ignore", message=".*The following layers were not sharded.*")
warnings.filterwarnings("ignore", category=UserWarning, module="transformers.*")
warnings.filterwarnings("ignore", category=FutureWarning, module="transformers.*")
warnings.filterwarnings("ignore", category=UserWarning, module="huggingface_hub.*")
warnings.filterwarnings("ignore")

for _log_name in ["transformers", "transformers.modeling_utils", "transformers.configuration_utils",
                  "transformers.tokenization_utils_base", "transformers.models", "transformers.utils",
                  "transformers.utils.import_utils", "huggingface_hub", "huggingface_hub.file_download",
                  "huggingface_hub.utils", "sentence_transformers", "torch"]:
    _logger = logging.getLogger(_log_name)
    _logger.setLevel(logging.ERROR)
    _logger.propagate = False

try:
    import transformers
    transformers.utils.logging.set_verbosity_error()
    transformers.utils.logging.disable_default_handler()
    transformers.utils.logging.disable_progress_bar()
except Exception:
    pass

try:
    import huggingface_hub.utils as _hf_utils
    _hf_utils.logging.set_verbosity_error()
    _hf_utils.logging.disable_progress_bars()
except Exception:
    pass

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.query_control.agentic.schema_linker import SchemaLinker
from src.query_control.agentic.sql_generator import SQLGenerator
from src.query_control.agentic.sql_refiner import SQLRefiner
from src.query_control.agentic.answer_generator import AnswerGenerator
from src.query_control.domain_gate import DomainGate
from src.query_control.agentic.canonical_normalizer import CanonicalNormalizer
from src.query_control.agentic.query_decomposer import QueryDecomposer
from concurrent.futures import ThreadPoolExecutor

class AgenticPipeline:
    def __init__(self):
        semantic_layer_path = PROJECT_ROOT / "data" / "Processed" / "metadata" / "query_control" / "semantic_layer.json"
        db_path = PROJECT_ROOT / "data" / "Processed" / "intern_chatbot.duckdb"
        domain_gate_config_path = PROJECT_ROOT / "data" / "Processed" / "metadata" / "query_control" / "domain_gate_config.json"
        
        # Pre-warm local embedding model vào bộ nhớ đệm (cache) khi khởi tạo pipeline
        try:
            from src.query_control.build_qdrant_semantic_index import EmbeddingClient, load_qdrant_config
            import os
            qconfig = load_qdrant_config()
            emb_model = qconfig.get("embedding_model") or os.environ.get("EMBEDDING_MODEL", "AITeamVN/Vietnamese_Embedding")
            EmbeddingClient(emb_model)
        except Exception:
            pass
        
        self.domain_gate = DomainGate(config_path=domain_gate_config_path, semantic_layer_path=semantic_layer_path)
        self.schema_linker = SchemaLinker(semantic_layer_path)
        self.sql_generator = SQLGenerator()
        self.sql_refiner = SQLRefiner(db_path)
        self.answer_generator = AnswerGenerator()
        self.canonical_normalizer = CanonicalNormalizer()
        self.query_decomposer = QueryDecomposer()
        self.event_queue = None
        
    def _handle_exact_match(self, user_question: str, mode: str, stream: bool, t0: float, cached_exact: dict, sql_refiner: SQLRefiner) -> dict:
        ans = cached_exact.get("answer", "")
        sql_val = cached_exact.get("sql", "")
        elapsed = time.time() - t0
        
        from src.query_control.agentic.chatbot_logger import log_chatbot_run
        
        is_chart_mode = (mode == "Biểu đồ") or (
            mode == "Auto" and (
                any(kw in user_question.lower() for kw in ["biểu đồ", "đồ thị", "vẽ", "chart", "plotly"])
                or bool(cached_exact.get("chart_code"))
            )
        )
        if is_chart_mode and sql_val:
            try:
                from src.query_control.agentic.utils import normalize_columns
                from src.query_control.agentic.chart_generator import AgentChartGenerator
                
                df_val, refined_sql = sql_refiner.execute_and_refine(sql_val, user_question, {})
                if df_val is not None and not df_val.empty:
                    df_vi = normalize_columns(df_val)
                    chart_dir = PROJECT_ROOT / "artifacts" / "charts"
                    save_path = chart_dir / f"chart_{int(time.time())}.html"
                    
                    fig = None
                    chart_ans = ans
                    chart_code = cached_exact.get("chart_code", "")
                    
                    if chart_code:
                        try:
                            from src.query_control.agentic.utils import prepare_chart_data
                            temp_df = prepare_chart_data(df_vi.copy(), user_question)
                            local_vars = {"df": temp_df}
                            exec(chart_code, globals(), local_vars)
                            fig = local_vars.get("fig")
                            if fig is not None:
                                fig.write_html(str(save_path))
                                print("   [Visual Code Cache] HIT | Thực thi mã biểu đồ tức thì!")
                        except Exception as e_exec:
                            print(f"   [Visual Code Cache Warning] Lỗi exec chart_code ({e_exec}). Fallback gọi LLM.")
                            fig = None
                    
                    if fig is None:
                        chart_gen = AgentChartGenerator()
                        fig, chart_ans, new_chart_code = chart_gen.generate(user_question, df_vi, save_path=save_path)
                        if fig is not None and new_chart_code:
                            from src.query_control.agentic.semantic_cache import set_cached_result
                            set_cached_result(user_question, refined_sql, chart_ans, chart_code=new_chart_code)
                    
                    log_chatbot_run(user_question, f"{mode} (Route 1/1.5: Exact Hit)", refined_sql, chart_ans, stream=False, execution_time_sec=elapsed)
                    return {"question": user_question, "sql": refined_sql, "answer": chart_ans, "data": df_vi, "chart_fig": fig}
            except Exception as e:
                print(f"[Route 1/1.5 Chart Warning] Lỗi ({e}). Chuyển về cache gốc.")
                try:
                    from src.query_control.agentic.utils import normalize_columns
                    df_val, refined_sql = sql_refiner.execute_and_refine(sql_val, user_question, {})
                    df_vi = normalize_columns(df_val) if df_val is not None and not df_val.empty else None
                except Exception:
                    df_vi = None
                    refined_sql = sql_val
                log_chatbot_run(user_question, f"{mode} (Route 1/1.5: Exact Hit Fallback)", refined_sql, ans, stream=False, execution_time_sec=elapsed)
                return {"question": user_question, "sql": refined_sql, "answer": ans, "data": df_vi, "chart_fig": None}

        df_vi = None
        refined_sql = sql_val
        if sql_val:
            try:
                from src.query_control.agentic.utils import normalize_columns
                df_val, refined_sql = sql_refiner.execute_and_refine(sql_val, user_question, {})
                df_vi = normalize_columns(df_val) if df_val is not None and not df_val.empty else None
            except Exception as e:
                print(f"[Route 1/1.5 Exact Hit Warning] Lỗi thực thi SQL từ cache ({e})")
                df_vi = None
                refined_sql = sql_val

        if stream:
            def cache_stream_gen():
                yield ans
            log_chatbot_run(user_question, f"{mode} (Route 1/1.5: Exact Hit)", refined_sql, ans, stream=True, execution_time_sec=elapsed)
            return {"question": user_question, "sql": refined_sql, "answer": cache_stream_gen(), "data": df_vi, "chart_fig": None}
        log_chatbot_run(user_question, f"{mode} (Route 1/1.5: Exact Hit)", refined_sql, ans, stream=False, execution_time_sec=elapsed)
        return {"question": user_question, "sql": refined_sql, "answer": ans, "data": df_vi, "chart_fig": None}

    def process(self, user_question: str, mode: str = "Auto", stream: bool = False, use_semantic_cache: bool = True, history: list[dict] | None = None, event_queue: Any = None) -> dict:
        if event_queue is not None:
            self.event_queue = event_queue
        if mode not in ("Báo Cáo",):
            sub_queries = self.query_decomposer.decompose(user_question, history=history)
            if len(sub_queries) > 1:
                print(f"[QueryDecomposer] Tách câu hỏi kép thành {len(sub_queries)} ý: {sub_queries}")
                with ThreadPoolExecutor(max_workers=min(len(sub_queries), 4)) as executor:
                    futures = [executor.submit(self._process_single, q, mode, False, use_semantic_cache, self.event_queue) for q in sub_queries]
                    results = [f.result() for f in futures]
                
                combined_ans = "\n\n---\n\n".join([f"**Ý {i+1} ({sub_queries[i]}):**\n" + str(r.get("answer", "")) for i, r in enumerate(results)])
                return {
                    "question": user_question,
                    "sql": ";\n".join([r.get("sql", "") for r in results if r.get("sql")]),
                    "answer": combined_ans,
                    "data": results[0].get("data") if results else None,
                    "chart_fig": results[0].get("chart_fig") if results else None,
                    "parts": results
                }
            elif len(sub_queries) == 1 and sub_queries[0] != user_question:
                print(f"[QueryDecomposer] Đã chuẩn hóa/thay thế đồng tham chiếu: {user_question!r} -> {sub_queries[0]!r}")
                user_question = sub_queries[0]
        return self._process_single(user_question, mode, stream, use_semantic_cache, event_queue=self.event_queue)

    def _process_single(self, user_question: str, mode: str = "Auto", stream: bool = False, use_semantic_cache: bool = True, event_queue: Any = None) -> dict:
        if event_queue is not None:
            self.event_queue = event_queue
        t0 = time.time()
        print(f"\n--- [AgenticPipeline] Processing Single: {user_question} | Mode: {mode} | Stream: {stream} ---")
        
        from src.query_control.agentic.semantic_cache import SemanticCacheManager, set_cached_result
        from src.query_control.agentic.chatbot_logger import log_chatbot_run
        
        cache_mgr = SemanticCacheManager(collection_name="agentic_semantic_cache", similarity_threshold=0.86)

        # 1. Preflight: Gộp InputGuardrail và Query Rewrite làm 1 lời gọi LLM duy nhất (hoặc Heuristic siêu tốc <1ms)
        try:
            from src.query_control.agentic.guardrails import InputGuardrail
            in_guard = InputGuardrail()
            preflight = in_guard.validate_and_rewrite(user_question, mode)
            if not preflight.get("is_valid", True):
                ans = preflight.get("recommendation", "Câu hỏi nằm ngoài phạm vi hỗ trợ hoặc sai chế độ.")
                log_chatbot_run(user_question, f"{mode} (Guardrail Blocked)", "", ans, stream=stream, execution_time_sec=time.time() - t0)
                return {
                    "question": user_question,
                    "sql": "",
                    "answer": ans,
                    "data": None
                }
            rewritten_q = preflight.get("rewritten_question", user_question).strip()
            mode = preflight.get("suggested_mode", mode)
            print(f"[Pre-Processing] Rewritten Q: '{rewritten_q}' | Mode: {mode} (Preflight Combined Model + CanonicalNormalizer)")
        except Exception as e:
            print(f"[Warning] Preflight thất bại ({e}). Dùng câu gốc.")
            rewritten_q = self.canonical_normalizer.normalize(user_question)

        # 2. Route 1 / Route 1.5: Kiểm tra Exact Match Cache trước (Canonical Hash <1ms)
        if use_semantic_cache and mode not in ("Báo Cáo",):
            cached_exact = cache_mgr.get_exact_cache(user_question)
            if cached_exact:
                return self._handle_exact_match(user_question, mode, stream, t0, cached_exact, self.sql_refiner)
            if rewritten_q != user_question:
                cached_exact_rewritten = cache_mgr.get_exact_cache(rewritten_q)
                if cached_exact_rewritten:
                    print(f"[Route 1.5] HIT Cache với câu hỏi đã Rewrite: '{rewritten_q}'")
                    return self._handle_exact_match(user_question, mode, stream, t0, cached_exact_rewritten, self.sql_refiner)

        # 3. Route 2: Qdrant Vector Similarity Search (>=0.86) + Few-shot SQL Repair (gpt-4o-mini)
        if use_semantic_cache and mode not in ("Báo Cáo",):
            similar_items = cache_mgr.search_similar_questions(rewritten_q, threshold=0.86)
            if similar_items:
                best_match = similar_items[0]
                old_q = best_match["question"]
                old_sql = best_match["sql"]
                print(f"[Route 2] Found match score {best_match['score']:.4f}. Repairing SQL via gpt-4o-mini...")
                
                repaired_sql = self.sql_generator.repair_sql_from_template(old_q, old_sql, rewritten_q)
                print(f"[Route 2] Repaired SQL: {repaired_sql}")
                
                # Thực thi SQL và tạo đáp án
                try:
                    df, final_sql = self.sql_refiner.execute_and_refine(repaired_sql, rewritten_q, {})
                    
                    # Setting cứng format output của mode 'Biểu đồ' bao gồm text + chart + dataframe
                    if mode == "Biểu đồ" and df is not None and not df.empty:
                        from src.query_control.agentic.utils import normalize_columns
                        from src.query_control.agentic.chart_generator import AgentChartGenerator
                        
                        df_vi = normalize_columns(df)
                        chart_gen = AgentChartGenerator()
                        chart_dir = PROJECT_ROOT / "artifacts" / "charts"
                        save_path = chart_dir / f"chart_{int(time.time())}.html"
                        fig, chart_ans, chart_code = chart_gen.generate(user_question, df_vi, save_path=save_path)
                        
                        if fig is not None and chart_code:
                            set_cached_result(user_question, final_sql, chart_ans, chart_code=chart_code)
                            if rewritten_q and rewritten_q != user_question:
                                set_cached_result(rewritten_q, final_sql, chart_ans, chart_code=chart_code)
                            
                        elapsed = time.time() - t0
                        log_chatbot_run(user_question, f"{mode} (Route 2: Few-shot SQL Repair)", final_sql, chart_ans, stream=False, execution_time_sec=elapsed)
                        return {
                            "question": user_question,
                            "sql": final_sql,
                            "answer": chart_ans,
                            "data": df_vi,
                            "chart_fig": fig
                        }

                    ans_res = self.answer_generator.generate(rewritten_q, df, stream=stream)
                    
                    if stream:
                        def stream_and_cache_wrapper(gen, q, sql, start_time):
                            chunks = []
                            for chunk in gen:
                                chunks.append(chunk)
                                yield chunk
                            # Chuyển các chunk không phải chuỗi (như DataFrame) sang chuỗi để lưu cache/log
                            str_chunks = [str(c) if not isinstance(c, str) else c for c in chunks]
                            full_ans = "".join(str_chunks)
                            set_cached_result(q, sql, full_ans)
                            if rewritten_q and rewritten_q != q:
                                set_cached_result(rewritten_q, sql, full_ans)
                            log_chatbot_run(q, f"{mode} (Route 2: Few-shot SQL Repair)", sql, full_ans, stream=True, execution_time_sec=start_time)
                        
                        ans = stream_and_cache_wrapper(ans_res, user_question, final_sql, t0)
                        return {
                            "question": user_question,
                            "sql": final_sql,
                            "answer": ans,
                            "data": df,
                            "chart_fig": None
                        }
                    else:
                        ans = ans_res
                        
                    # Lưu lại Local Cache
                    if use_semantic_cache and not stream and "lỗi" not in str(ans).lower() and "error" not in str(ans).lower():
                        cache_mgr.local_cache[cache_mgr.get_canonical_hash(user_question)] = {
                            "question": user_question,
                            "sql": final_sql,
                            "answer": ans
                        }
                        if rewritten_q and rewritten_q != user_question:
                            cache_mgr.local_cache[cache_mgr.get_canonical_hash(rewritten_q)] = {
                                "question": rewritten_q,
                                "sql": final_sql,
                                "answer": ans
                            }
                        cache_mgr._save_local_cache()
                        
                    fig = None
                    is_chart_mode_r2 = (mode == "Biểu đồ") or (
                        mode == "Auto" and any(kw in user_question.lower() for kw in ["biểu đồ", "đồ thị", "vẽ", "chart", "plotly"])
                    )
                    if is_chart_mode_r2 and df is not None and not df.empty:
                        try:
                            from src.query_control.agentic.utils import normalize_columns
                            from src.query_control.agentic.chart_generator import AgentChartGenerator
                            df_vi = normalize_columns(df)
                            chart_gen = AgentChartGenerator()
                            chart_dir = PROJECT_ROOT / "artifacts" / "charts"
                            save_path = chart_dir / f"chart_{int(time.time())}.html"
                            fig, ans, chart_code = chart_gen.generate(user_question, df_vi, save_path=save_path)
                            if not stream and "lỗi" not in str(ans).lower() and "error" not in str(ans).lower():
                                cache_mgr.local_cache[cache_mgr.get_canonical_hash(user_question)] = {
                                    "question": user_question,
                                    "sql": final_sql,
                                    "answer": ans,
                                    "chart_code": chart_code
                                }
                                cache_mgr._save_local_cache()
                        except Exception as e_chart:
                            print(f"[Route 2 Chart Warning] {e_chart}")

                    elapsed = time.time() - t0
                    log_chatbot_run(user_question, f"{mode} (Route 2: Few-shot SQL Repair)", final_sql, ans if not stream else "[Streaming]", stream=stream, execution_time_sec=elapsed)
                    return {
                        "question": user_question,
                        "sql": final_sql,
                        "answer": ans,
                        "data": df,
                        "chart_fig": fig
                    }
                except Exception as e:
                    print(f"[Route 2 Warning] Thực thi SQL Repair thất bại ({e}). Chuyển sang Route 3 (Full Pipeline).")
        
        # 4. Route 3: Full Agentic Pipeline (DomainGate -> SchemaLinker -> SQLGenerator -> SQLRefiner)
        print("[Route 3] No similar question found or repair failed. Executing Full Agentic Pipeline...")
        
        if mode == "Báo Cáo":
            from src.query_control.llm_helper import call_llm
            from src.query_control.agentic.report_generator import ReportGenerator
            import json
            
            # Trích xuất nhanh thông tin report_id, year, district bằng LLM
            prompt = f"""Bạn là công cụ trích xuất thông tin báo cáo. Hãy phân tích câu hỏi sau để xác định:
1. report_id: Mã số báo cáo (chọn từ 1 đến 15).
   - 1: Tổng hợp kết quả rà soát mức sống trung bình (hoặc HC, CN, NL, NN có mức sống trung bình)
   - 2: Tổng hợp diễn biến hộ nghèo
   - 3: Tổng hợp diễn biến hộ cận nghèo
   - 4: Phân tích chỉ số thiếu hụt dịch vụ xã hội cơ bản hộ nghèo (số lượng)
   - 5: Phân tích tỷ lệ các chỉ số thiếu hụt dịch vụ xã hội cơ bản hộ nghèo (tỷ lệ %)
   - 6: Phân tích chỉ số thiếu hụt dịch vụ xã hội cơ bản hộ cận nghèo (số lượng)
   - 7: Phân tích tỷ lệ các chỉ số thiếu hụt dịch vụ xã hội cơ bản hộ cận nghèo (tỷ lệ %)
   - 8: Tổng hợp phân loại hộ nghèo, hộ cận nghèo
   - 9: Phân tích hộ nghèo, hộ cận nghèo theo dân tộc
   - 10: Phân tích hộ nghèo, hộ cận nghèo theo nguyên nhân nghèo
   - 11: Tổng hợp chỉ tiêu thiếu hụt của trẻ em thuộc hộ nghèo, hộ cận nghèo
   - 12: Tổng hợp hộ nghèo đa chiều thiếu hụt theo các chỉ số đo lường
   - 13: Tổng hợp hộ cận nghèo đa chiều thiếu hụt theo các chỉ số đo lường
   - 14: Danh sách chi tiết hộ cận nghèo
   - 15: Danh sách chi tiết hộ nghèo
   Nếu câu hỏi không nói rõ, mặc định là 1.
2. year: Năm thống kê (ví dụ 2023, 2024). Nếu không nêu rõ, mặc định là 2024.
3. district: Tên Huyện/Thành phố muốn lọc (ví dụ: Gia Nghĩa, Cư Jút, Đắk Song, Đắk Mil, Đắk R'Lấp, Tuy Đức, Krông Nô, Đắk Glong). Nếu hỏi toàn tỉnh hoặc không nhắc đến huyện nào, để null.

Trả về DUY NHẤT một chuỗi JSON hợp lệ với các key: "report_id" (int), "year" (int), "district" (str hoặc null). Không kèm markdown hay giải thích.
Câu hỏi: {user_question}"""
            
            try:
                res_raw = call_llm(system_prompt="Bạn là công cụ trích xuất JSON.", user_prompt=prompt, temperature=0.0, max_tokens=100, response_json=True)
                # Parse JSON
                if isinstance(res_raw, str):
                    res_clean = res_raw.strip()
                    if res_clean.startswith("```json"): res_clean = res_clean[7:]
                    if res_clean.startswith("```"): res_clean = res_clean[3:]
                    if res_clean.endswith("```"): res_clean = res_clean[:-3]
                    info = json.loads(res_clean.strip())
                else:
                    info = res_raw
                    
                report_id = int(info.get("report_id", 1))
                year = int(info.get("year", 2024))
                district = info.get("district")
                print(f"[DEBUG LLM Báo Cáo] Original: {district}")
                if district and str(district).strip().lower() in ["none", "null", "toàn tỉnh", "all", "tỉnh đắk nông", ""]:
                    district = None
                elif district:
                    district = str(district).replace("Huyện ", "").replace("huyện ", "").replace("Thành phố ", "").replace("Thị xã ", "").strip()
                    district = self.canonical_normalizer.normalize(district)
                    district = district.replace("Huyện ", "").replace("Thành phố ", "").replace("Thị xã ", "").strip()
                    if district.strip().lower() in ["none", "null", "toàn tỉnh", "all", "tỉnh đắk nông", ""]:
                        district = None
                print(f"[DEBUG LLM Báo Cáo] Parsed: id={report_id}, year={year}, district='{district}'")
            except Exception as e:
                print(f"[AgenticPipeline] Lỗi trích xuất LLM Báo Cáo: {e}. Dùng mặc định.")
                report_id, year, district = 1, 2024, None
                
            try:
                import importlib
                import src.query_control.agentic.report_generator as _rg_mod
                importlib.reload(_rg_mod)
                from src.query_control.agentic.report_generator import ReportGenerator
                if self.event_queue:
                    self.event_queue.put(f"[Báo Cáo] Đang xử lý số liệu và kết xuất báo cáo số {report_id}...")
                rep_data = ReportGenerator.generate(report_id, year, district, event_queue=self.event_queue)
                elapsed = time.time() - t0
                log_chatbot_run(user_question, mode, rep_data["sql"], rep_data["answer"], stream=stream, execution_time_sec=elapsed)
                return {
                    "question": user_question,
                    "sql": rep_data["sql"],
                    "answer": rep_data["answer"],
                    "data": rep_data["df"],
                    "chart_fig": None,
                    "docx_path": str(rep_data.get("docx_path", "")),
                    "pdf_path": str(rep_data.get("pdf_path", "")),
                    "deep_analysis": rep_data.get("deep_analysis")
                }
            except Exception as e:
                err_ans = f"Lỗi khi tạo báo cáo số {report_id}: {str(e)}"
                elapsed = time.time() - t0
                log_chatbot_run(user_question, mode, "", err_ans, stream=stream, execution_time_sec=elapsed)
                return {
                    "question": user_question,
                    "sql": "",
                    "answer": err_ans,
                    "data": None
                }
            
        # DomainGate was removed to reduce latency because Preflight handles boundary validation.
        # 1. Schema Linking & Planner Cache
        schema_info = self.schema_linker.link(rewritten_q)
        if use_semantic_cache and mode not in ("Báo Cáo",):
            similar_templates = cache_mgr.search_similar_questions(rewritten_q, threshold=0.75)
            if similar_templates:
                best_temp = similar_templates[0]
                print(f"[Planner Cache] HIT | Tìm thấy câu tương tự (score: {best_temp['score']:.4f}) làm SQL Template Cache.")
                schema_info["similar_sql_template"] = {
                    "old_q": best_temp["question"],
                    "old_sql": best_temp["sql"]
                }
        
        # 2. SQL Generation
        sql_query = self.sql_generator.generate(rewritten_q, schema_info)
        
        # 3. SQL Execution & Refinement
        df, final_sql = self.sql_refiner.execute_and_refine(sql_query, rewritten_q, schema_info)
        
        # 4. Mode routing based on 'Auto' logic or explicit selection
        actual_mode = mode
        if mode == "Auto":
            if df is not None and not df.empty and len(df) > 1:
                actual_mode = "Biểu đồ"
            else:
                actual_mode = "Hỏi - Đáp"
                
        # 5. Output Generation
        fig = None
        if actual_mode == "Biểu đồ":
            from src.query_control.agentic.utils import normalize_columns
            from src.query_control.agentic.chart_generator import AgentChartGenerator
            
            df_vi = normalize_columns(df)
            chart_gen = AgentChartGenerator()
            chart_dir = PROJECT_ROOT / "artifacts" / "charts"
            save_path = chart_dir / f"chart_{int(time.time())}.html"
            
            fig, answer, chart_code = chart_gen.generate(user_question, df_vi, save_path=save_path)
            
            # 5.5 Guardrail Output (Fact-checking for Chart text)
            try:
                from src.query_control.agentic.guardrails import OutputGuardrail
                out_guard = OutputGuardrail()
                max_retries = 2
                for attempt in range(max_retries):
                    out_res = out_guard.validate_fact_checking(user_question, answer, df_vi)
                    if out_res.get("is_valid", True):
                        break
                    else:
                        reason = out_res.get('reason', 'Thông tin không khớp với dữ liệu gốc.')
                        print(f"[Guardrail Warning Chart] Attempt {attempt+1} failed: {reason}. Rewriting...")
                        if attempt < max_retries - 1:
                            answer = out_guard.rewrite_answer(user_question, answer, reason, df_vi)
                        else:
                            answer += f"\n\n[Cảnh báo Guardrail]: {reason}"
            except Exception as e:
                pass
                
            data_out = df_vi
            set_cached_result(user_question, final_sql, answer, chart_code=chart_code)
            try:
                # We need rewritten_q here if we are double caching for Route 3.
                # Actually, wait, rewritten_q might not be defined if Route 2 failed!
                # It is defined at line 140 (so it is in scope).
                if 'rewritten_q' in locals() and rewritten_q and rewritten_q != user_question:
                    set_cached_result(rewritten_q, final_sql, answer, chart_code=chart_code)
            except:
                pass
            log_chatbot_run(user_question, actual_mode, final_sql, answer, stream=False, execution_time_sec=time.time() - t0)
        else: # Hỏi - Đáp
            answer = self.answer_generator.generate(user_question, df, stream=stream)
            data_out = df
            
            # Guardrail Output (Fact-checking for Q&A)
            if not stream:
                try:
                    from src.query_control.agentic.guardrails import OutputGuardrail
                    out_guard = OutputGuardrail()
                    max_retries = 2
                    for attempt in range(max_retries):
                        out_res = out_guard.validate_fact_checking(user_question, answer, df)
                        if out_res.get("is_valid", True):
                            break
                        else:
                            reason = out_res.get('reason', 'Thông tin không khớp với dữ liệu gốc.')
                            print(f"[Guardrail Warning Q&A] Attempt {attempt+1} failed: {reason}. Rewriting...")
                            if attempt < max_retries - 1:
                                answer = out_guard.rewrite_answer(user_question, answer, reason, df)
                            else:
                                answer += f"\n\n[Cảnh báo Guardrail]: {reason}"
                except Exception as e:
                    pass

            if stream:
                def stream_and_cache_wrapper(gen, q, sql, start_time):
                    chunks = []
                    for chunk in gen:
                        chunks.append(chunk)
                        yield chunk
                    str_chunks = [str(c) if not isinstance(c, str) else c for c in chunks]
                    full_ans = "".join(str_chunks)
                    set_cached_result(q, sql, full_ans)
                    try:
                        if 'rewritten_q' in locals() and rewritten_q and rewritten_q != q:
                            set_cached_result(rewritten_q, sql, full_ans)
                    except:
                        pass
                    log_chatbot_run(q, actual_mode, sql, full_ans, stream=True, execution_time_sec=time.time() - start_time)
                answer = stream_and_cache_wrapper(answer, user_question, final_sql, t0)
            else:
                set_cached_result(user_question, final_sql, answer)
                try:
                    if 'rewritten_q' in locals() and rewritten_q and rewritten_q != user_question:
                        set_cached_result(rewritten_q, final_sql, answer)
                except:
                    pass
                log_chatbot_run(user_question, actual_mode, final_sql, answer, stream=False, execution_time_sec=time.time() - t0)
            
        return {
            "question": user_question,
            "sql": final_sql,
            "answer": answer,
            "data": data_out,
            "chart_fig": fig
        }
