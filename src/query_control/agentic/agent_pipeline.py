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

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.query_control.agentic.schema_linker import SchemaLinker
from src.query_control.agentic.sql_generator import SQLGenerator
from src.query_control.agentic.sql_refiner import SQLRefiner
from src.query_control.agentic.answer_generator import AnswerGenerator
from src.query_control.domain_gate import DomainGate

class AgenticPipeline:
    def __init__(self):
        semantic_layer_path = PROJECT_ROOT / "data" / "Processed" / "metadata" / "query_control" / "semantic_layer.json"
        db_path = PROJECT_ROOT / "data" / "Processed" / "intern_chatbot.duckdb"
        domain_gate_config_path = PROJECT_ROOT / "data" / "Processed" / "metadata" / "query_control" / "domain_gate_config.json"
        
        self.domain_gate = DomainGate(config_path=domain_gate_config_path, semantic_layer_path=semantic_layer_path)
        self.schema_linker = SchemaLinker(semantic_layer_path)
        self.sql_generator = SQLGenerator()
        self.sql_refiner = SQLRefiner(db_path)
        self.answer_generator = AnswerGenerator()
        
    def process(self, user_question: str, mode: str = "Auto", stream: bool = False) -> dict:
        t0 = time.time()
        print(f"\n--- [AgenticPipeline] Processing: {user_question} | Mode: {mode} | Stream: {stream} ---")
        
        # 1. Route 1: Kiểm tra Exact Match Cache (Canonical Hash <1ms)
        from src.query_control.agentic.semantic_cache import SemanticCacheManager
        from src.query_control.agentic.chatbot_logger import log_chatbot_run
        
        cache_mgr = SemanticCacheManager(collection_name="agentic_semantic_cache", similarity_threshold=0.86)
        cached_exact = cache_mgr.get_exact_cache(user_question)
        if cached_exact:
            ans = cached_exact.get("answer", "")
            sql_val = cached_exact.get("sql", "")
            elapsed = time.time() - t0
            if stream:
                def cache_stream_gen():
                    yield ans
                log_chatbot_run(user_question, f"{mode} (Route 1: Exact Hit)", sql_val, ans, stream=True, execution_time_sec=elapsed)
                return {"question": user_question, "sql": sql_val, "answer": cache_stream_gen(), "data": None, "chart_fig": None}
            log_chatbot_run(user_question, f"{mode} (Route 1: Exact Hit)", sql_val, ans, stream=False, execution_time_sec=elapsed)
            return {"question": user_question, "sql": sql_val, "answer": ans, "data": None, "chart_fig": None}
            
        # 2. Pre-Processing: LLM Re-write (Chuẩn hóa câu hỏi, khử teencode, viết tắt)
        from src.query_control.llm_helper import call_llm
        rewrite_prompt = f"""Hãy viết lại câu hỏi sau thành câu hỏi rút gọn chuẩn mực tiếng Việt, sửa lỗi chính tả và giải nghĩa các từ viết tắt.
Ví dụ: 
- 'tp gia nghia nam 2024 co bnhieu ho can ngheo' -> 'Số hộ cận nghèo tại thành phố Gia Nghĩa năm 2024'
- 'H. TĐ nam 2024 co bao nhiu ho ngheo' -> 'Số hộ nghèo tại huyện Tuy Đức năm 2024'
- 'H. CJ xa TT co bnhieu ho can ngheo la ng dong bao' -> 'Số hộ cận nghèo là người đồng bào tại xã Tâm Thắng, huyện Cư Jút'
- 'Top 3 xa co ho ngheo nhieu nhat o H. ĐG' -> 'Top 3 xã có hộ nghèo nhiều nhất ở huyện Đắk Glong'
Nếu câu hỏi đã chuẩn, giữ nguyên. Trả về DUY NHẤT câu hỏi đã được viết lại, không giải thích."""
        try:
            rewritten_q = call_llm(system_prompt="Bạn là chuyên gia chuẩn hóa câu hỏi RAG.", user_prompt=f"Câu hỏi gốc: {user_question}\n\n{rewrite_prompt}", temperature=0.0, max_tokens=100, model="gpt-4o-mini").strip()
            print(f"[Pre-Processing] Rewritten Q: '{rewritten_q}' (Model: gpt-4o-mini)")
        except Exception as e:
            print(f"[Warning] Re-write thất bại ({e}). Dùng câu gốc.")
            rewritten_q = user_question

        # 3. Route 2: Qdrant Vector Similarity Search (>=0.86) + Few-shot SQL Repair (gpt-4o-mini)
        if mode not in ("Báo Cáo",):
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
                    db_res = self.sql_refiner.refine(rewritten_q, repaired_sql) # refiner sẽ execute và sửa lỗi nếu có
                    final_sql = db_res.get("sql", repaired_sql)
                    df = db_res.get("df")
                    
                    ans_res = self.answer_generator.generate(rewritten_q, final_sql, df, stream=stream)
                    ans = ans_res.get("answer", "")
                    
                    # Lưu lại Local Cache
                    if not stream and "lỗi" not in str(ans).lower() and "error" not in str(ans).lower():
                        cache_mgr.local_cache[cache_mgr.get_canonical_hash(user_question)] = {
                            "question": user_question,
                            "sql": final_sql,
                            "answer": ans
                        }
                        cache_mgr._save_local_cache()
                        
                    elapsed = time.time() - t0
                    log_chatbot_run(user_question, f"{mode} (Route 2: Few-shot SQL Repair)", final_sql, ans if not stream else "[Streaming]", stream=stream, execution_time_sec=elapsed)
                    return {
                        "question": user_question,
                        "sql": final_sql,
                        "answer": ans,
                        "data": df,
                        "chart_fig": None
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
            except Exception as e:
                print(f"[AgenticPipeline] Lỗi trích xuất LLM Báo Cáo: {e}. Dùng mặc định.")
                report_id, year, district = 1, 2024, None
                
            try:
                rep_data = ReportGenerator.generate(report_id, year, district)
                elapsed = time.time() - t0
                log_chatbot_run(user_question, mode, rep_data["sql"], rep_data["answer"], stream=stream, execution_time_sec=elapsed)
                return {
                    "question": user_question,
                    "sql": rep_data["sql"],
                    "answer": rep_data["answer"],
                    "data": rep_data["df"],
                    "chart_fig": None,
                    "docx_path": str(rep_data["docx_path"]),
                    "pdf_path": str(rep_data["pdf_path"])
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
            
        # 0. Domain Gate: Chặn các câu hỏi ngoài luồng, không đủ thông tin hoặc câu hỏi lý thuyết
        gate_res = self.domain_gate.classify(user_question)
        route = gate_res.get("route", "OUT_OF_SCOPE")
        confidence = gate_res.get("confidence", 0.0)
        
        print(f"[DomainGate] Route: {route} | Confidence: {confidence:.2f}")
        
        if route == "OUT_OF_SCOPE":
            ans = "Câu hỏi của bạn nằm ngoài phạm vi phân tích dữ liệu rà soát hộ nghèo. Xin vui lòng hỏi các vấn đề liên quan đến thống kê, quy định, hoặc thông tin hộ nghèo/cận nghèo trên địa bàn tỉnh Đắk Nông."
            log_chatbot_run(user_question, f"{mode} (DomainGate)", "", ans, stream=stream, execution_time_sec=time.time() - t0)
            return {
                "question": user_question,
                "sql": "",
                "answer": ans,
                "data": None
            }
        elif route == "CLARIFICATION_NEEDED":
            ans = "Câu hỏi của bạn chưa đủ rõ ràng. Bạn có thể cung cấp thêm thông tin chi tiết (ví dụ: cần xem dữ liệu của huyện/xã nào, năm nào, hoặc chỉ số cụ thể nào) để tôi hỗ trợ chính xác hơn không?"
            log_chatbot_run(user_question, f"{mode} (DomainGate)", "", ans, stream=stream, execution_time_sec=time.time() - t0)
            return {
                "question": user_question,
                "sql": "",
                "answer": ans,
                "data": None
            }
        elif route == "GENERAL_KNOWLEDGE":
            ans = "Hệ thống hiện tại chỉ tập trung trả lời số liệu, chưa hỗ trợ trả lời lý thuyết."
            log_chatbot_run(user_question, f"{mode} (DomainGate)", "", ans, stream=stream, execution_time_sec=time.time() - t0)
            return {
                "question": user_question,
                "sql": "",
                "answer": ans,
                "data": None
            }
            
        # 1. Schema Linking
        schema_info = self.schema_linker.link(user_question)
        
        # 2. SQL Generation
        sql_query = self.sql_generator.generate(user_question, schema_info)
        
        # 3. SQL Execution & Refinement
        df, final_sql = self.sql_refiner.execute_and_refine(sql_query, user_question, schema_info)
        
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
            
            fig, answer = chart_gen.generate(user_question, df_vi, save_path=save_path)
            data_out = df_vi
            set_cached_result(user_question, final_sql, answer)
            log_chatbot_run(user_question, actual_mode, final_sql, answer, stream=False, execution_time_sec=time.time() - t0)
        else: # Hỏi - Đáp
            answer = self.answer_generator.generate(user_question, df, stream=stream)
            data_out = df
            if stream:
                def stream_and_cache_wrapper(gen, q, sql, start_time):
                    chunks = []
                    for chunk in gen:
                        chunks.append(chunk)
                        yield chunk
                    full_ans = "".join(chunks)
                    set_cached_result(q, sql, full_ans)
                    log_chatbot_run(q, actual_mode, sql, full_ans, stream=True, execution_time_sec=time.time() - start_time)
                answer = stream_and_cache_wrapper(answer, user_question, final_sql, t0)
            else:
                set_cached_result(user_question, final_sql, answer)
                log_chatbot_run(user_question, actual_mode, final_sql, answer, stream=False, execution_time_sec=time.time() - t0)
            
        return {
            "question": user_question,
            "sql": final_sql,
            "answer": answer,
            "data": data_out,
            "chart_fig": fig
        }
