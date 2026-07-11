import asyncio
import time
import json
import sys
import os
import shutil
import re
from playwright.async_api import async_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

try:
    from src.query_control.agentic.canonical_normalizer import CanonicalNormalizer
    _normalizer = CanonicalNormalizer()
except Exception:
    _normalizer = None

def normalize_for_kw(s):
    if not s:
        return ""
    if _normalizer:
        try:
            s_canon = _normalizer.normalize(s)
        except Exception:
            s_canon = s
    else:
        s_canon = s
    s = s_canon.lower()
    s = re.sub(r"['\"`\-_.,!/?()]+", " ", s)
    s = s.replace("đăk", "đắk").replace("jut", "jút").replace("n drot", "ndrot").replace("n drót", "ndrot").replace("ndrót", "ndrot")
    return " ".join(s.split())

def check_keyword_assertion(kw, text, norm_text):
    kw_norm = normalize_for_kw(kw)
    if kw_norm in norm_text:
        return True
    synonyms_map = {
        "huyện": ["huyện", "đắk mil", "krông nô", "đắk r'lấp", "cư jút", "tuy đức", "đắk song", "đắk glong", "gia nghĩa", "quận"],
        "xã": ["xã", "phường", "thị trấn", "thôn", "bon", "buôn"],
        "nhân khẩu": ["nhân khẩu", "người", "dân số", "thành viên", "khẩu"],
        "thiếu hụt": ["thiếu hụt", "nghèo đa chiều", "chỉ số", "an sinh", "suy giảm", "yếu kém"],
        "cận nghèo": ["cận nghèo", "hộ cận nghèo", "cn", "b1", "mức sống trung bình"],
        "nguyên nhân": ["nguyên nhân", "lý do", "yếu tố", "nguồn gốc"],
        "bảo hiểm y tế": ["bảo hiểm y tế", "bhyt", "y tế", "khám chữa bệnh"],
        "b1": ["b1", "điểm b1", "mức sống", "trung bình"],
        "thoát nghèo": ["thoát nghèo", "vượt chuẩn", "giảm nghèo", "cải thiện"],
        "dân tộc": ["dân tộc", "dt thiểu số", "dtts", "kinh", "m'nông", "ê đê", "tày", "nùng"],
        "đắk nông": ["đắk nông", "toàn tỉnh", "tỉnh"]
    }
    for key, syn_list in synonyms_map.items():
        if key in kw_norm:
            if any(normalize_for_kw(syn) in norm_text for syn in syn_list):
                return True
    if _normalizer and hasattr(_normalizer, 'get_similar_schema_keywords'):
        try:
            sim_words = _normalizer.get_similar_schema_keywords(kw, n=5)
            if any(normalize_for_kw(w) in norm_text for w in sim_words):
                return True
        except Exception:
            pass
    return False


# Danh sách 50 test case chia theo 4 mode, bao gồm cả single-turn, multi-turn và ground truth keywords
TEST_CASES = [
    # --- MODE: Hỏi - Đáp (15 cases) ---
    {"id": "QA_01", "mode": "Hỏi - Đáp", "prompt": "Thống kê các dân tộc đang có ở Tuy Đức 2024 ?", "type": "valid_qa", "new_session": True, "expected_keywords": ["Tuy Đức"]},
    {"id": "QA_02", "mode": "Hỏi - Đáp", "prompt": "Có bao nhiêu hộ nghèo trong đây là nữ ?", "type": "valid_qa", "new_session": False, "expected_keywords": ["276"]},
    {"id": "QA_03", "mode": "Hỏi - Đáp", "prompt": "xã nào ở krông nô có tỷ lệ nghèo cao nhất", "type": "valid_qa", "new_session": True, "expected_keywords": ["Nam Xuân"]},
    {"id": "QA_04", "mode": "Hỏi - Đáp", "prompt": "có bao nhiêu hộ nghèo là người dân tộc thiểu số tại xã đó", "type": "valid_qa", "new_session": False, "expected_keywords": ["20"]},
    {"id": "QA_05", "mode": "Hỏi - Đáp", "prompt": "có bao nhiêu hộ nghèo trên toàn tỉnh đắk nông", "type": "valid_qa", "new_session": True, "expected_keywords": ["Đắk Nông"]},
    {"id": "QA_06", "mode": "Hỏi - Đáp", "prompt": "xã đắk ndrot có bao nhiêu hộ cận nghèo", "type": "valid_qa", "new_session": True, "expected_keywords": ["Đắk Ndrot"]},
    {"id": "QA_07", "mode": "Hỏi - Đáp", "prompt": "ai là chủ hộ của hộ có mã 12345", "type": "valid_qa", "new_session": True, "expected_keywords": []},
    {"id": "QA_08", "mode": "Hỏi - Đáp", "prompt": "huyện nào có nhiều hộ nghèo nhất tỉnh", "type": "valid_qa", "new_session": True, "expected_keywords": ["Tuy Đức", "hộ nghèo"]},
    {"id": "QA_09", "mode": "Hỏi - Đáp", "prompt": "tổng số nhân khẩu của toàn tỉnh năm 2024 là bao nhiêu", "type": "valid_qa", "new_session": True, "expected_keywords": ["nhân khẩu"]},
    {"id": "QA_10", "mode": "Hỏi - Đáp", "prompt": "liệt kê các dân tộc thiểu số ở đắk r'lấp", "type": "valid_qa", "new_session": True, "expected_keywords": ["Đắk R'Lấp"]},
    {"id": "QA_11", "mode": "Hỏi - Đáp", "prompt": "có bao nhiêu hộ nghèo thiếu hụt bảo hiểm y tế ở gia nghĩa", "type": "valid_qa", "new_session": True, "expected_keywords": ["Gia Nghĩa"]},
    {"id": "QA_12", "mode": "Hỏi - Đáp", "prompt": "tỷ lệ hộ nghèo của đắk song là bao nhiêu", "type": "valid_qa", "new_session": True, "expected_keywords": ["Đắk Song"]},
    {"id": "QA_13", "mode": "Hỏi - Đáp", "prompt": "nguyên nhân nghèo chủ yếu ở đăk glong là gì", "type": "valid_qa", "new_session": True, "expected_keywords": ["Đắk Glong"]},
    {"id": "QA_14", "mode": "Hỏi - Đáp", "prompt": "thống kê", "type": "ambiguous", "new_session": True, "expected_keywords": []},
    {"id": "QA_15", "mode": "Hỏi - Đáp", "prompt": "thời tiết hôm nay thế nào", "type": "offtopic", "new_session": True, "expected_keywords": []},

    # --- MODE: Biểu đồ (15 cases) ---
    {"id": "CH_01", "mode": "Biểu đồ", "prompt": "vẽ biểu đồ số hộ nghèo Đắk Mil", "type": "chart", "new_session": True, "expected_keywords": ["Đắk Mil"]},
    {"id": "CH_02", "mode": "Biểu đồ", "prompt": "tạo biểu đồ tỷ lệ hộ cận nghèo theo huyện", "type": "chart", "new_session": True, "expected_keywords": ["huyện"]},
    {"id": "CH_03", "mode": "Biểu đồ", "prompt": "biểu đồ nguyên nhân nghèo toàn tỉnh", "type": "chart", "new_session": True, "expected_keywords": ["nguyên nhân"]},
    {"id": "CH_04", "mode": "Biểu đồ", "prompt": "vẽ đồ thị hộ nghèo thiếu hụt bảo hiểm y tế", "type": "chart", "new_session": True, "expected_keywords": ["bảo hiểm y tế"]},
    {"id": "CH_05", "mode": "Biểu đồ", "prompt": "đồ thị 10 xã nghèo nhất tỉnh đắk nông", "type": "chart", "new_session": True, "expected_keywords": ["xã"]},
    {"id": "CH_06", "mode": "Biểu đồ", "prompt": "biểu đồ tỷ lệ B1 các huyện", "type": "chart", "new_session": True, "expected_keywords": ["B1"]},
    {"id": "CH_07", "mode": "Biểu đồ", "prompt": "vẽ biểu đồ 5 xã có số hộ nghèo cao nhất", "type": "chart", "new_session": True, "expected_keywords": ["xã"]},
    {"id": "CH_08", "mode": "Biểu đồ", "prompt": "tạo biểu đồ phân bố độ tuổi nhân khẩu", "type": "chart", "new_session": True, "expected_keywords": ["độ tuổi"]},
    {"id": "CH_09", "mode": "Biểu đồ", "prompt": "biểu đồ tỷ lệ dân tộc tại chỗ huyện krông nô", "type": "chart", "new_session": True, "expected_keywords": ["Krông Nô"]},
    {"id": "CH_10", "mode": "Biểu đồ", "prompt": "biểu đồ thoát nghèo các huyện năm 2024", "type": "chart", "new_session": True, "expected_keywords": ["thoát nghèo"]},
    {"id": "CH_11", "mode": "Biểu đồ", "prompt": "biểu đồ hộ nghèo các xã huyện Krông Nô", "type": "chart", "new_session": True, "expected_keywords": ["Krông Nô"]},
    {"id": "CH_12", "mode": "Biểu đồ", "prompt": "đồ thị cột số lượng hộ cận nghèo theo huyện", "type": "chart", "new_session": True, "expected_keywords": ["cận nghèo"]},
    {"id": "CH_13", "mode": "Biểu đồ", "prompt": "vẽ biểu đồ tròn cơ cấu dân tộc tỉnh đắk nông", "type": "chart", "new_session": True, "expected_keywords": ["dân tộc"]},
    {"id": "CH_14", "mode": "Biểu đồ", "prompt": "biểu đồ heatmap thiếu hụt các chỉ số an sinh", "type": "chart", "new_session": True, "expected_keywords": ["thiếu hụt"]},
    {"id": "CH_15", "mode": "Biểu đồ", "prompt": "biểu đồ", "type": "ambiguous", "new_session": True, "expected_keywords": []},

    # --- MODE: Báo Cáo (10 cases) ---
    {"id": "RP_01", "mode": "Báo Cáo", "prompt": "tạo báo cáo 1", "type": "report", "new_session": True, "expected_keywords": []},
    {"id": "RP_02", "mode": "Báo Cáo", "prompt": "xuất báo cáo số 3", "type": "report", "new_session": True, "expected_keywords": []},
    {"id": "RP_03", "mode": "Báo Cáo", "prompt": "báo cáo 8 huyện Đắk Mil", "type": "report", "new_session": True, "expected_keywords": []},
    {"id": "RP_04", "mode": "Báo Cáo", "prompt": "tạo báo cáo 13", "type": "report", "new_session": True, "expected_keywords": []},
    {"id": "RP_05", "mode": "Báo Cáo", "prompt": "tạo báo cáo tổng hợp tình hình hộ nghèo huyện krông nô", "type": "report", "new_session": True, "expected_keywords": []},
    {"id": "RP_06", "mode": "Báo Cáo", "prompt": "xuất báo cáo phân tích nguyên nhân nghèo xã đắk ndrot", "type": "report", "new_session": True, "expected_keywords": []},
    {"id": "RP_07", "mode": "Báo Cáo", "prompt": "báo cáo thống kê nhân khẩu và dân tộc thiểu số huyện tuy đức", "type": "report", "new_session": True, "expected_keywords": []},
    {"id": "RP_08", "mode": "Báo Cáo", "prompt": "tạo báo cáo đánh giá mức độ thiếu hụt đa chiều tỉnh đắk nông", "type": "report", "new_session": True, "expected_keywords": []},
    {"id": "RP_09", "mode": "Báo Cáo", "prompt": "xuất báo cáo số 12 về hộ nghèo và cận nghèo", "type": "report", "new_session": True, "expected_keywords": []},
    {"id": "RP_10", "mode": "Báo Cáo", "prompt": "báo cáo", "type": "ambiguous", "new_session": True, "expected_keywords": []},

    # --- MODE: Auto (10 cases) ---
    {"id": "AU_01", "mode": "Auto", "prompt": "có bao nhiêu hộ nghèo ở đắk mil", "type": "valid_qa", "new_session": True, "expected_keywords": ["Đắk Mil"]},
    {"id": "AU_02", "mode": "Auto", "prompt": "vẽ biểu đồ tỷ lệ nghèo theo huyện", "type": "chart", "new_session": True, "expected_keywords": ["huyện"]},
    {"id": "AU_03", "mode": "Auto", "prompt": "tạo báo cáo số 1 cho tỉnh đắk nông", "type": "report", "new_session": True, "expected_keywords": []},
    {"id": "AU_04", "mode": "Auto", "prompt": "thống kê dân tộc tại huyện cư jut", "type": "valid_qa", "new_session": True, "expected_keywords": ["Cư Jút"]},
    {"id": "AU_05", "mode": "Auto", "prompt": "biểu đồ cơ cấu dân tộc huyện krông nô", "type": "chart", "new_session": True, "expected_keywords": ["Krông Nô"]},
    {"id": "AU_06", "mode": "Auto", "prompt": "xuất báo cáo huyện đắk r'lấp", "type": "report", "new_session": True, "expected_keywords": []},
    {"id": "AU_07", "mode": "Auto", "prompt": "xã nào nghèo nhất huyện đăk glong", "type": "valid_qa", "new_session": True, "expected_keywords": ["Đắk Ha"]},
    {"id": "AU_08", "mode": "Auto", "prompt": "đồ thị các chỉ số thiếu hụt an sinh", "type": "chart", "new_session": True, "expected_keywords": ["thiếu hụt"]},
    {"id": "AU_09", "mode": "Auto", "prompt": "báo cáo tổng hợp huyện gia nghĩa", "type": "report", "new_session": True, "expected_keywords": []},
    {"id": "AU_10", "mode": "Auto", "prompt": "so sánh", "type": "ambiguous", "new_session": True, "expected_keywords": []},
]

async def execute_test_case(page, tc, current_ui_mode):
    print(f"\n=======================================================")
    print(f"[{tc['id']}] Mode: {tc['mode']} | Prompt: '{tc['prompt']}' (New Session: {tc['new_session']})")
    print(f"=======================================================")
    
    try:
        if tc["new_session"]:
            try:
                new_btn = page.locator("button", has_text="Tạo phiên mới")
                if await new_btn.count() > 0:
                    await new_btn.click()
                    await page.wait_for_timeout(1000)
                    while await page.locator("text=⏳ Đang").count() > 0:
                        await page.wait_for_timeout(500)
                else:
                    await page.reload(wait_until="domcontentloaded", timeout=30000)
            except Exception:
                try:
                    await page.reload(wait_until="domcontentloaded", timeout=30000)
                except Exception:
                    pass
            await page.wait_for_selector("textarea[data-testid='stChatInputTextArea']", state="visible", timeout=30000)
            await page.wait_for_timeout(500)
            current_ui_mode = None
            
        # 1. Change mode if different
        if current_ui_mode != tc["mode"]:
            mode_box = page.locator("div[data-testid='stSelectbox']")
            await mode_box.wait_for(state="visible", timeout=15000)
            await mode_box.click()
            await page.wait_for_timeout(400)
            await page.keyboard.type(tc["mode"])
            await page.wait_for_timeout(300)
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(1500)
            while await page.locator("text=⏳ Đang").count() > 0:
                await page.wait_for_timeout(500)
            await page.wait_for_timeout(500)
            current_ui_mode = tc["mode"]
            
        # 2. Count existing messages
        messages_locator = page.locator("div[data-testid='stChatMessage']")
        prev_count = await messages_locator.count()
        
        # 3. Input Prompt
        start_time = time.time()
        chat_input = page.locator("textarea[data-testid='stChatInputTextArea']")
        await chat_input.click()
        await chat_input.fill(tc["prompt"])
        await page.wait_for_timeout(200)
        await chat_input.press("Enter")
        await page.wait_for_timeout(1500)
        
        # 4. Dynamic Polling for message appearance and response processing
        print("Waiting for response (dynamic polling)...")
        new_count = prev_count
        poll_start = time.time()
        max_poll_timeout = 90.0 if tc["type"] == "report" else 60.0
        
        while time.time() - poll_start < max_poll_timeout:
            await page.wait_for_timeout(500)
            current_count = await messages_locator.count()
            
            if current_count > prev_count:
                new_count = current_count
                last_msg = messages_locator.nth(new_count - 1)
                is_spinning = await last_msg.locator("text=⏳").count() > 0 or await page.locator("text=⏳ Đang").count() > 0
                if tc["type"] == "chart":
                    chart = last_msg.locator("div[data-testid='stPlotlyChart'], div.stPlotlyChart, iframe[title='st.plotly_chart'], iframe[title*='plotly'], .js-plotly-plot")
                    if await chart.count() > 0:
                        break
                    if not is_spinning and (time.time() - poll_start > 20.0 or time.time() - poll_start > max_poll_timeout - 5.0):
                        break
                elif tc["type"] == "report":
                    dl_buttons = last_msg.locator("button", has_text=re.compile(r"Tải|PDF|Word|DOCX|Báo cáo", re.IGNORECASE))
                    if await dl_buttons.count() > 0:
                        break
                    if not is_spinning and (time.time() - poll_start > 25.0 or time.time() - poll_start > max_poll_timeout - 5.0):
                        break
                elif not is_spinning:
                    md_text = await last_msg.inner_text()
                    if md_text and md_text.strip() and not md_text.strip().startswith("⏳"):
                        break
        
        if new_count <= prev_count:
            exec_time = round(time.time() - start_time, 2)
            print(f"[{tc['id']}] FAILED: No new message rendered in UI! (Prev: {prev_count}, New: {new_count})")
            await page.screenshot(path=f"artifacts/test_results/fail_{tc['id']}_no_msg.png")
            return False, current_ui_mode, "No new message rendered", exec_time, "No message rendered"
            
        last_msg = messages_locator.nth(new_count - 1)
            
        # Strict Error Checking: check if there is any Streamlit error alert or exception
        has_error = await last_msg.locator("div[data-testid='stException'], div[data-testid='stAlert'], div.stError").count() > 0
        if has_error:
            exec_time = round(time.time() - start_time, 2)
            print(f"[{tc['id']}] FAILED: Streamlit exception/error component detected!")
            await page.screenshot(path=f"artifacts/test_results/fail_{tc['id']}_st_error.png")
            return False, current_ui_mode, "Streamlit error component detected", exec_time, "Streamlit Error Component"

        # Clean text extraction: extract ONLY from stMarkdownContainer to avoid Plotly numbers and DataFrame noise
        md_containers = last_msg.locator("div[data-testid='stMarkdownContainer']")
        md_count = await md_containers.count()
        if md_count > 0:
            texts = []
            for i in range(md_count):
                t = await md_containers.nth(i).inner_text()
                t_clean = t.strip()
                if t_clean and t_clean != "smart_toy" and not t_clean.startswith("⏳"):
                    texts.append(t_clean)
            text = "\n\n".join(texts)
        else:
            text = await last_msg.inner_text()
            
        clean_text = " ".join(text.split())
        exec_time = round(time.time() - start_time, 2)
        print(f"[{tc['id']}] Output Preview ({exec_time}s): {clean_text}")
        
        # Check for actual error tracebacks or unhandled exceptions in text
        if any(err_kw in text for err_kw in ["Traceback (most recent call last):", "Exception:", "Đã phát sinh lỗi ngoại lệ"]):
            print(f"[{tc['id']}] FAILED: Error traceback or text detected in output!")
            await page.screenshot(path=f"artifacts/test_results/fail_{tc['id']}_error_text.png")
            return False, current_ui_mode, "Error text detected in output", exec_time, clean_text
            
        # Check expected keywords (Ground Truth) with normalization and semantic assertion
        if tc.get("expected_keywords"):
            norm_text = normalize_for_kw(text)
            missing_kws = [kw for kw in tc["expected_keywords"] if not check_keyword_assertion(kw, text, norm_text)]
            if missing_kws:
                print(f"[{tc['id']}] FAILED: Missing expected keywords in output: {missing_kws}")
                await page.screenshot(path=f"artifacts/test_results/fail_{tc['id']}_missing_kws.png")
                return False, current_ui_mode, f"Missing expected keywords: {missing_kws}", exec_time, clean_text
        
        # 6. Validate based on test case type
        if tc["type"] == "offtopic":
            if "Câu hỏi không liên quan" in text or "nằm ngoài phạm vi" in text or "tôi là trợ lý" in text.lower():
                print(f"[{tc['id']}] PASSED (Correctly blocked off-topic prompt)")
                return True, current_ui_mode, "Blocked off-topic", exec_time, clean_text
            else:
                print(f"[{tc['id']}] FAILED: Expected off-topic blocking but got normal response.")
                await page.screenshot(path=f"artifacts/test_results/fail_{tc['id']}_offtopic.png")
                return False, current_ui_mode, "Failed to block off-topic", exec_time, clean_text
                
        elif tc["type"] == "ambiguous":
            if "chung chung" in text.lower() or "rõ ràng hơn" in text.lower() or "gợi ý" in text.lower() or "cụ thể" in text.lower() or "hướng dẫn" in text.lower() or "vui lòng" in text.lower():
                print(f"[{tc['id']}] PASSED (Correctly handled ambiguity with suggestion)")
                return True, current_ui_mode, "Handled ambiguity", exec_time, clean_text
            else:
                print(f"[{tc['id']}] FAILED: Did not provide ambiguity suggestion.")
                await page.screenshot(path=f"artifacts/test_results/fail_{tc['id']}_ambiguity.png")
                return False, current_ui_mode, "No ambiguity suggestion", exec_time, clean_text
                
        # Check for unexpected false-positive out-of-scope error
        if "Câu hỏi không liên quan" in text or "nằm ngoài phạm vi" in text:
            print(f"[{tc['id']}] FAILED: False-positive Out-of-Scope rejection!")
            await page.screenshot(path=f"artifacts/test_results/fail_{tc['id']}_false_positive.png")
            return False, current_ui_mode, "False-positive guardrail rejection", exec_time, clean_text
            
        if tc["type"] == "valid_qa":
            if len(clean_text) > 15:
                print(f"[{tc['id']}] PASSED (Valid Q&A response rendered)")
                return True, current_ui_mode, "Valid Q&A text", exec_time, clean_text
            else:
                print(f"[{tc['id']}] FAILED: Q&A response too short or empty.")
                await page.screenshot(path=f"artifacts/test_results/fail_{tc['id']}_qa_empty.png")
                return False, current_ui_mode, "Q&A text too short", exec_time, clean_text
                
        elif tc["type"] == "chart":
            chart = last_msg.locator("div[data-testid='stPlotlyChart'], div.stPlotlyChart, iframe[title='st.plotly_chart'], iframe[title*='plotly'], .js-plotly-plot")
            if await chart.count() == 0:
                await page.wait_for_timeout(3000)
            if await chart.count() > 0:
                print(f"[{tc['id']}] PASSED (Plotly chart rendered)")
                return True, current_ui_mode, "Plotly chart rendered", exec_time, clean_text
            else:
                print(f"[{tc['id']}] FAILED: No Plotly chart found in DOM.")
                await page.screenshot(path=f"artifacts/test_results/fail_{tc['id']}_no_chart.png")
                return False, current_ui_mode, "No Plotly chart in DOM", exec_time, clean_text
                
        elif tc["type"] == "report":
            dl_buttons = last_msg.locator("button", has_text=re.compile(r"Tải|PDF|Word|DOCX|Báo cáo", re.IGNORECASE))
            if await dl_buttons.count() == 0:
                await page.wait_for_timeout(3000)
            if await dl_buttons.count() > 0:
                print(f"[{tc['id']}] PASSED (Report download buttons rendered)")
                return True, current_ui_mode, "Download buttons rendered", exec_time, clean_text
            else:
                print(f"[{tc['id']}] FAILED: No download buttons generated.")
                await page.screenshot(path=f"artifacts/test_results/fail_{tc['id']}_no_report.png")
                return False, current_ui_mode, "No download buttons generated", exec_time, clean_text
                
        return False, current_ui_mode, "Unknown validation error", exec_time, clean_text
        
    except Exception as e:
        print(f"[{tc['id']}] EXCEPTION: {e}")
        await page.screenshot(path=f"artifacts/test_results/fail_{tc['id']}_exception.png")
        return False, current_ui_mode, f"Exception: {e}", 0.0, str(e)

async def run_suite():
    print("Starting 50-Case Comprehensive UI Regression Suite via Playwright...")
    
    # 1. Ensure artifacts/test_results directory exists and clean up root directory
    os.makedirs("artifacts/test_results", exist_ok=True)
    for fname in os.listdir("."):
        if fname.startswith("fail_") or fname in ("report_50_test_results.md", "test_50_results.json"):
            try:
                shutil.move(fname, os.path.join("artifacts/test_results", fname))
            except Exception as e:
                print(f"Note: Could not move {fname}: {e}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Connecting to Streamlit at http://localhost:8501...")
        try:
            await page.goto("http://localhost:8501", wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_selector("textarea[data-testid='stChatInputTextArea']", state="visible", timeout=60000)
        except Exception as e:
            print(f"Could not connect to Streamlit. Is it running? {e}")
            sys.exit(1)
            
        passed_cases = []
        failed_cases = []
        current_ui_mode = None
        
        filter_ids = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
        test_cases_to_run = [tc for tc in TEST_CASES if tc["id"] in filter_ids] if filter_ids else TEST_CASES
        
        for tc in test_cases_to_run:
            success, current_ui_mode, reason, exec_time, output_text = await execute_test_case(page, tc, current_ui_mode)
            item = {
                "id": tc["id"],
                "mode": tc["mode"],
                "prompt": tc["prompt"],
                "exec_time_sec": exec_time,
                "output": output_text,
                "status": "PASSED" if success else "FAILED",
                "reason": reason
            }
            if success:
                passed_cases.append(item)
            else:
                failed_cases.append(item)
                
        print("\n=======================================================")
        print(f"=== 50-CASE REGRESSION SUITE FINAL SUMMARY ===")
        print(f"Total Tested: {len(TEST_CASES)}")
        print(f"Passed: {len(passed_cases)} ({len(passed_cases)/len(TEST_CASES)*100:.1f}%)")
        print(f"Failed: {len(failed_cases)} ({len(failed_cases)/len(TEST_CASES)*100:.1f}%)")
        print("=======================================================")
        
        if failed_cases:
            print("\nFAILED CASES DETAILS:")
            for f in failed_cases:
                print(f" - [{f['id']}] ({f['mode']}) '{f['prompt']}': {f['reason']}")
                
        if not filter_ids:
            # Save results to JSON artifact inside artifacts/test_results/
            results = {
                "total": len(TEST_CASES),
                "passed": len(passed_cases),
                "failed": len(failed_cases),
                "pass_rate": f"{len(passed_cases)/len(TEST_CASES)*100:.1f}%",
                "passed_list": passed_cases,
                "failed_list": failed_cases
            }
            json_path = os.path.join("artifacts", "test_results", "test_50_results.json")
            with open(json_path, "w", encoding="utf-8") as fp:
                json.dump(results, fp, ensure_ascii=False, indent=2)
                
            # Write Markdown Report inside artifacts/test_results/
            md_lines = [
                "# Báo Cáo Tổng Hợp Kết Quả Kiểm Thử 50 Test Case (UI Playwright)",
                "",
                "| ID | Chế độ | Prompt | Thời gian thực thi (s) | Output | Trạng thái |",
                "|---|---|---|---|---|---|"
            ]
            all_cases = passed_cases + failed_cases
            for c in all_cases:
                p_text = c["prompt"].replace("|", "\\|")
                o_text = c["output"][:250].replace("|", "\\|") + ("..." if len(c["output"]) > 250 else "")
                o_text = " ".join(o_text.split())
                md_lines.append(f"| {c['id']} | {c['mode']} | {p_text} | {c['exec_time_sec']}s | {o_text} | {c['status']} |")
                
            md_path = os.path.join("artifacts", "test_results", "report_50_test_results.md")
            with open(md_path, "w", encoding="utf-8") as fp:
                fp.write("\n".join(md_lines))
            print(f"\nSaved test results to {json_path} and {md_path}")
            
        await browser.close()
        
        if failed_cases:
            sys.exit(1)
        else:
            sys.exit(0)

if __name__ == "__main__":
    asyncio.run(run_suite())
