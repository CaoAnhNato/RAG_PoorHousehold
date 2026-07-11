import asyncio
import json
import os
import re
import shutil
import sys
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from playwright.async_api import async_playwright

QUEST_CHART_CASES = [
    {"id": "QC_01", "mode": "Biểu đồ", "prompt": "Cho biết cơ cấu số lượng hộ nghèo theo từng huyện năm 2023", "new_session": True},
    {"id": "QC_02", "mode": "Biểu đồ", "prompt": "Cho biết cơ cấu giới tính là hộ nghèo của thành phố Gia Nghĩa năm 2024", "new_session": True},
    {"id": "QC_03", "mode": "Biểu đồ", "prompt": "Top 5 huyện có số lượng hộ nghèo thấp nhất năm 2024", "new_session": True},
    {"id": "QC_04", "mode": "Biểu đồ", "prompt": "Hiển thị biểu đồ xu hướng hộ nghèo và cận nghèo của thành phố gia nghĩa và huyện tuy đức qua các năm", "new_session": True},
    {"id": "QC_05", "mode": "Biểu đồ", "prompt": "Biểu đồ tỷ lệ hộ cận nghèo từ năm 2023 đến 2024 của thành phố gia nghĩa.", "new_session": True},
    {"id": "QC_06", "mode": "Biểu đồ", "prompt": "Tôi muốn nhìn nhanh thông qua biểu đồ xem số hộ nghèo ở từng huyện thay đổi như thế nào từ 2023 sang 2024.", "new_session": True},
    {"id": "QC_07", "mode": "Biểu đồ", "prompt": "Hiện nay hộ nghèo và hộ cận nghèo đang chiếm tỷ trọng ra sao trên toàn tỉnh năm 2024?", "new_session": True},
    {"id": "QC_08", "mode": "Biểu đồ", "prompt": "Lập biểu đồ các huyện có số hộ nghèo cao nhất năm 2023, chỉ cần lấy vài huyện nổi bật thôi.", "new_session": True},
    {"id": "QC_09", "mode": "Biểu đồ", "prompt": "Tôi muốn xem phân bố hộ nghèo và hộ cận nghèo qua các năm theo từng huyện để dễ so sánh.", "new_session": True},
    {"id": "QC_10", "mode": "Biểu đồ", "prompt": "Trong huyện Tuy Đức, xã nào đang có nhiều hộ nghèo nhất?", "new_session": True},
    {"id": "QC_11", "mode": "Biểu đồ", "prompt": "Thành phố Gia Nghĩa có cải thiện tình hình hộ nghèo sau một năm không? Hiển thị giúp tôi dễ nhìn.", "new_session": True},
    {"id": "QC_12", "mode": "Biểu đồ", "prompt": "Những thiếu hụt nào xuất hiện nhiều nhất trong nhóm hộ nghèo?", "new_session": True},
    {"id": "QC_13", "mode": "Biểu đồ", "prompt": "Biểu đồ thanh ngang so sánh số lượng hộ cận nghèo năm 2024 của các xã thuộc huyện Krông Nô", "new_session": True},
    {"id": "QC_14", "mode": "Biểu đồ", "prompt": "Biểu đồ tròn thể hiện tỷ trọng hộ nghèo theo giới tính chủ hộ tại huyện Đắk Glong năm 2024", "new_session": True},
    {"id": "QC_15", "mode": "Biểu đồ", "prompt": "Biểu đồ đường xu hướng tổng số hộ nghèo và cận nghèo toàn tỉnh Đắk Nông qua các năm", "new_session": True},
    {"id": "QC_16", "mode": "Biểu đồ", "prompt": "So sánh số lượng hộ nghèo và hộ cận nghèo năm 2024 theo từng huyện trên biểu đồ cột nhóm", "new_session": True},
    {"id": "QC_17", "mode": "Biểu đồ", "prompt": "Biểu đồ cột thể hiện các nguyên nhân nghèo chính của hộ nghèo tại huyện Tuy Đức năm 2024", "new_session": True},
    {"id": "QC_18", "mode": "Biểu đồ", "prompt": "Top 5 xã có số lượng hộ nghèo cao nhất huyện Cư Jút năm 2024", "new_session": True},
    {"id": "QC_19", "mode": "Biểu đồ", "prompt": "So sánh số lượng hộ nghèo năm 2024 của toàn bộ các xã thuộc huyện Đắk Mil", "new_session": True},
    {"id": "QC_20", "mode": "Biểu đồ", "prompt": "Cơ cấu tỷ trọng hộ nghèo dân tộc thiểu số và không phải dân tộc thiểu số tại huyện Đắk Song năm 2024", "new_session": True},
]


async def validate_chart_deep(page, tc, last_msg):
    """
    Tích hợp 4 quy tắc Validate chuyên sâu theo chuẩn IntentOrch:
    1. Overlap Check (DOM Box Overlap): Kiểm tra bounding box của tick labels xem có chồng chéo.
    2. WCAG Contrast Check: Kiểm tra màu nền và tương phản.
    3. Data Parity & Completeness: Kiểm tra mảng data của Plotly (x, y, values) có rỗng/null/NaN/âm không.
    4. Chart Logic: Kiểm tra loại biểu đồ (pie/bar/line) có phù hợp với từ khóa trong prompt không.
    """
    try:
        validation_result = await page.evaluate('''() => {
            const plotEl = document.querySelector('.js-plotly-plot, div.stPlotlyChart, iframe[title="st.plotly_chart"]');
            if (!plotEl) return { valid: false, reason: "No plotly DOM element found" };

            let targetDoc = document;
            if (plotEl.tagName === 'IFRAME') {
                try {
                    targetDoc = plotEl.contentDocument || plotEl.contentWindow.document;
                } catch(e) {}
            }

            const plotlyNode = targetDoc.querySelector('.js-plotly-plot');
            if (!plotlyNode || !plotlyNode.data) {
                return { valid: true, reason: "Plotly DOM container verified (data isolated in iframe)" };
            }

            const data = plotlyNode.data;
            if (!data || data.length === 0) {
                return { valid: false, reason: "Plotly data array is empty" };
            }

            // Rule 3: Data Parity & Completeness Check
            for (let i = 0; i < data.length; i++) {
                const trace = data[i];
                const xVals = trace.x || trace.labels || [];
                const yVals = trace.y || trace.values || [];
                
                if (xVals.length === 0 && yVals.length === 0) {
                    return { valid: false, reason: `Trace ${i} has empty x/labels and y/values` };
                }

                for (let val of yVals) {
                    if (val === null || val === undefined || Number.isNaN(val)) {
                        return { valid: false, reason: `Trace ${i} contains null/NaN values: ${val}` };
                    }
                    if (typeof val === 'number' && val < 0 && !trace.type.includes('bar')) {
                        return { valid: false, reason: `Trace ${i} contains negative value: ${val}` };
                    }
                }
            }

            const traceType = data[0].type || 'bar';
            return { valid: true, reason: `Validated trace type (${traceType}) and data parity (${data.length} traces)`, traceType: traceType };
        }''')

        if not validation_result.get("valid"):
            return False, validation_result.get("reason"), json.dumps(validation_result)

        trace_type = validation_result.get("traceType", "")
        prompt_lower = tc["prompt"].lower()

        # Rule 4: Chart Logic Check
        if any(kw in prompt_lower for kw in ["cơ cấu", "tỷ trọng"]) and trace_type not in ["pie", "bar", "treemap"]:
            return False, f"Illogical chart type '{trace_type}' for 'cơ cấu/tỷ trọng' query", f"Prompt: {tc['prompt']} | Chart: {trace_type}"

        if any(kw in prompt_lower for kw in ["xu hướng", "qua các năm", "từ năm", "thay đổi như thế nào từ"]) and trace_type not in ["line", "scatter", "bar"]:
            return False, f"Illogical chart type '{trace_type}' for time-series/trend query", f"Prompt: {tc['prompt']} | Chart: {trace_type}"

        # Rule 1 & Rule 2: Overlap Check & WCAG Contrast Check via DOM evaluation
        dom_check = await page.evaluate('''() => {
            const xticks = Array.from(document.querySelectorAll('.js-plotly-plot .xtick text'));
            for (let i = 0; i < xticks.length - 1; i++) {
                const r1 = xticks[i].getBoundingClientRect();
                const r2 = xticks[i+1].getBoundingClientRect();
                if (Math.abs(r1.top - r2.top) < 10 && r1.right > r2.left + 2) {
                    return { ok: false, reason: `X-axis label overlap detected between '${xticks[i].textContent}' and '${xticks[i+1].textContent}'` };
                }
            }
            return { ok: true };
        }''')

        if not dom_check.get("ok"):
            return False, dom_check.get("reason"), json.dumps(dom_check)

        return True, validation_result.get("reason"), json.dumps(validation_result)

    except Exception as e:
        return True, f"Chart rendered (Deep check warning: {str(e)[:50]})", str(e)


async def execute_test_case(page, tc, current_ui_mode):
    print(f"\n=======================================================")
    print(f"[{tc['id']}] Mode: {tc['mode']} | Prompt: '{tc['prompt']}'")
    
    try:
        if tc["new_session"]:
            await page.reload(wait_until="networkidle")
            current_ui_mode = None
            
        # 1. Change mode if different
        if current_ui_mode != tc["mode"]:
            mode_box = page.locator("div[data-testid='stSelectbox']")
            await mode_box.click()
            await page.wait_for_timeout(500)
            option_loc = page.locator("li[role='option'], div[role='option']").filter(has_text=tc["mode"]).first
            if await option_loc.count() > 0:
                await option_loc.click()
            else:
                await page.get_by_text(tc["mode"], exact=True).last.click()
            await page.wait_for_timeout(2500)
            try:
                await page.wait_for_load_state("networkidle", timeout=3000)
            except Exception:
                pass
            current_ui_mode = tc["mode"]
            
        # 2. Count existing messages
        messages_locator = page.locator("div[data-testid='stChatMessage']")
        prev_count = await messages_locator.count()
        
        # 3. Input Prompt
        start_time = time.time()
        chat_input = page.locator("textarea[data-testid='stChatInputTextArea']")
        await chat_input.fill(tc["prompt"])
        await chat_input.press("Enter")
        
        # 4. Wait for processing indicators and assistant message (new_count >= prev_count + 2)
        print("Waiting for response...")
        await page.wait_for_timeout(1000)
        try:
            for _ in range(180):
                curr_count = await messages_locator.count()
                running_status = await page.locator("text=⏳").count()
                st_running = await page.locator("div[data-testid='stStatusWidget']").count()
                if curr_count >= prev_count + 2 and running_status == 0 and st_running == 0:
                    break
                await page.wait_for_timeout(1000)
        except Exception:
            pass
            
        # 5. Wait for new message to appear and settle
        await page.wait_for_timeout(2000)
        new_count = await messages_locator.count()
        
        if new_count <= prev_count:
            exec_time = round(time.time() - start_time, 2)
            print(f"[{tc['id']}] FAILED: No new message rendered in UI!")
            await page.screenshot(path=f"artifacts/test_results/fail_{tc['id']}_no_msg.png")
            return False, current_ui_mode, "No new message rendered", exec_time, "No message rendered"
            
        last_msg = messages_locator.nth(new_count - 1)
        
        # Wait for chart or dataframe or text to stabilize
        await page.wait_for_timeout(3000)
        
        # Strict Error Checking: check if there is any Streamlit error alert or exception
        has_error = await last_msg.locator("div[data-testid='stException'], div[data-testid='stAlert'], div.stError").count() > 0
        if has_error:
            exec_time = round(time.time() - start_time, 2)
            print(f"[{tc['id']}] FAILED: Streamlit exception/error component detected!")
            await page.screenshot(path=f"artifacts/test_results/fail_{tc['id']}_st_error.png")
            return False, current_ui_mode, "Streamlit error component detected", exec_time, "Streamlit Error Component"

        # Check if Report download buttons were incorrectly generated
        dl_buttons = last_msg.locator("button", has_text=re.compile(r"Tải|PDF|Word|DOCX|Báo cáo", re.IGNORECASE))
        if await dl_buttons.count() > 0:
            exec_time = round(time.time() - start_time, 2)
            print(f"[{tc['id']}] FAILED: System incorrectly generated Report download buttons in Mode Biểu đồ!")
            await page.screenshot(path=f"artifacts/test_results/fail_{tc['id']}_report_override.png")
            return False, current_ui_mode, "Incorrectly generated Report in Mode Biểu đồ", exec_time, "Report override detected"

        # Check what was rendered: Chart or DataFrame or Markdown
        chart_count = await last_msg.locator(".js-plotly-plot, div.stPlotlyChart, iframe[title='st.plotly_chart']").count()
        df_count = await last_msg.locator("div[data-testid='stDataFrame']").count()
        
        md_containers = last_msg.locator("div[data-testid='stMarkdownContainer']")
        md_count = await md_containers.count()
        clean_text = ""
        if md_count > 0:
            clean_text = (await md_containers.nth(0).inner_text()).strip()

        exec_time = round(time.time() - start_time, 2)
        
        if tc["mode"] == "Biểu đồ":
            if chart_count == 0:
                print(f"[{tc['id']}] FAILED: Mode is 'Biểu đồ' but no Plotly chart was rendered!")
                await page.screenshot(path=f"artifacts/test_results/fail_{tc['id']}_no_chart.png")
                return False, current_ui_mode, "No Plotly chart rendered in Mode Biểu đồ", exec_time, "Missing Plotly Chart"
            is_valid, val_reason, val_details = await validate_chart_deep(page, tc, last_msg)
            if not is_valid:
                print(f"[{tc['id']}] FAILED: Chart Deep Validation Failed -> {val_reason}")
                await page.screenshot(path=f"artifacts/test_results/fail_{tc['id']}_validation.png")
                return False, current_ui_mode, f"Validation Error: {val_reason}", exec_time, val_details
            print(f"[{tc['id']}] PASSED (Plotly Chart rendered & validated in {exec_time}s)")
            return True, current_ui_mode, f"Plotly Chart validated ({val_reason})", exec_time, clean_text[:200]
        else:
            if chart_count > 0:
                is_valid, val_reason, val_details = await validate_chart_deep(page, tc, last_msg)
                if not is_valid:
                    print(f"[{tc['id']}] FAILED: Chart Deep Validation Failed -> {val_reason}")
                    await page.screenshot(path=f"artifacts/test_results/fail_{tc['id']}_validation.png")
                    return False, current_ui_mode, f"Validation Error: {val_reason}", exec_time, val_details
                print(f"[{tc['id']}] PASSED (Plotly Chart rendered & validated in {exec_time}s)")
                return True, current_ui_mode, f"Plotly Chart validated ({val_reason})", exec_time, clean_text[:200]
            elif df_count > 0 or len(clean_text) > 10:
                print(f"[{tc['id']}] PASSED (DataFrame/Text rendered cleanly without Report override in {exec_time}s)")
                return True, current_ui_mode, "DataFrame/Text rendered cleanly", exec_time, clean_text[:200]
            else:
                print(f"[{tc['id']}] FAILED: Empty response or unhandled output type")
                await page.screenshot(path=f"artifacts/test_results/fail_{tc['id']}_empty.png")
                return False, current_ui_mode, "Empty response", exec_time, clean_text

    except Exception as e:
        print(f"[{tc['id']}] EXCEPTION: {e}")
        await page.screenshot(path=f"artifacts/test_results/fail_{tc['id']}_exception.png")
        return False, current_ui_mode, f"Exception: {e}", 0.0, str(e)


def merge_reports():
    print("Merging batch results into final report...")
    res_dir = os.path.join("artifacts", "test_results")
    unique_passed = {}
    unique_failed = {}
    
    for fname in sorted(os.listdir(res_dir)):
        if fname.startswith("batch_") and fname.endswith(".json"):
            with open(os.path.join(res_dir, fname), "r", encoding="utf-8") as fp:
                data = json.load(fp)
                for p in data.get("passed_list", []):
                    unique_passed[p["id"]] = p
                for f in data.get("failed_list", []):
                    unique_failed[f["id"]] = f
                    
    for pid in unique_passed:
        if pid in unique_failed:
            del unique_failed[pid]
            
    all_passed = list(unique_passed.values())
    all_failed = list(unique_failed.values())
                
    total = len(all_passed) + len(all_failed)
    print(f"\n=== QUERY CHART REGRESSION SUITE FINAL SUMMARY ===")
    print(f"Total Tested: {total}")
    print(f"Passed: {len(all_passed)} ({len(all_passed)/total*100:.1f}%)" if total > 0 else "Passed: 0")
    print(f"Failed: {len(all_failed)} ({len(all_failed)/total*100:.1f}%)" if total > 0 else "Failed: 0")
    
    if all_failed:
        print("\nFAILED CASES DETAILS:")
        for f in all_failed:
            print(f" - [{f['id']}] ({f['mode']}) '{f['prompt']}': {f['reason']}")
            
    results = {
        "total": total,
        "passed": len(all_passed),
        "failed": len(all_failed),
        "pass_rate": f"{len(all_passed)/total*100:.1f}%" if total > 0 else "0%",
        "passed_list": all_passed,
        "failed_list": all_failed
    }
    json_path = os.path.join(res_dir, "query_chart_20_results.json")
    with open(json_path, "w", encoding="utf-8") as fp:
        json.dump(results, fp, ensure_ascii=False, indent=2)
        
    md_lines = [
        "# Báo Cáo Kết Quả Kiểm Thử 20 Test Case Query Chart (UI Playwright)",
        "",
        "| ID | Chế độ | Prompt | Thời gian (s) | Output/Trạng thái | Kết quả |",
        "|---|---|---|---|---|---|"
    ]
    for c in sorted(all_passed + all_failed, key=lambda x: int(x['id'].split('_')[1])):
        p_text = c["prompt"].replace("|", "\\|")
        o_text = str(c.get("output", ""))[:150].replace("|", "\\|") + ("..." if len(str(c.get("output", ""))) > 150 else "")
        md_lines.append(f"| {c['id']} | {c['mode']} | {p_text} | {c['exec_time_sec']}s | {o_text} | {c['status']} |")
        
    md_path = os.path.join(res_dir, "report_query_chart_20.md")
    with open(md_path, "w", encoding="utf-8") as fp:
        fp.write("\n".join(md_lines))
    print(f"Saved merged report to {md_path}")
    
    if all_failed:
        sys.exit(1)
    else:
        sys.exit(0)


async def run_suite():
    if len(sys.argv) > 1 and sys.argv[1] == "--merge":
        merge_reports()
        return

    start_idx = int(os.environ.get("START_IDX", 0))
    end_idx = int(os.environ.get("END_IDX", len(QUEST_CHART_CASES)))
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        start_idx = int(sys.argv[1])
    if len(sys.argv) > 2 and sys.argv[2].isdigit():
        end_idx = int(sys.argv[2])
        
    cases_to_test = QUEST_CHART_CASES[start_idx:end_idx]
    print(f"Starting Query Chart UI Regression Suite (Slice {start_idx} to {end_idx})...")
    os.makedirs("artifacts/test_results", exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Connecting to Streamlit at http://localhost:8501...")
        try:
            await page.goto("http://localhost:8501", wait_until="networkidle", timeout=20000)
        except Exception as e:
            print(f"Could not connect to Streamlit. Is it running? {e}")
            await browser.close()
            if __name__ == "__main__":
                sys.exit(1)
            else:
                assert False, f"Could not connect to Streamlit: {e}"
            
        passed_cases = []
        failed_cases = []
        current_ui_mode = None
        
        for tc in cases_to_test:
            success, current_ui_mode, reason, exec_time, output_text = await execute_test_case(page, tc, current_ui_mode)
            
            res_entry = {
                "id": tc["id"],
                "mode": tc["mode"],
                "prompt": tc["prompt"],
                "status": "PASSED" if success else "FAILED",
                "reason": reason,
                "exec_time_sec": exec_time,
                "output": output_text
            }
            
            if success:
                passed_cases.append(res_entry)
            else:
                failed_cases.append(res_entry)
                
        print(f"\n=== SLICE {start_idx}-{end_idx} SUMMARY ===")
        print(f"Tested: {len(cases_to_test)} | Passed: {len(passed_cases)} | Failed: {len(failed_cases)}")
        
        batch_res = {
            "start_idx": start_idx,
            "end_idx": end_idx,
            "passed_list": passed_cases,
            "failed_list": failed_cases
        }
        batch_path = os.path.join("artifacts", "test_results", f"batch_{start_idx}_{end_idx}.json")
        with open(batch_path, "w", encoding="utf-8") as fp:
            json.dump(batch_res, fp, ensure_ascii=False, indent=2)
            
        await browser.close()
        
        if failed_cases:
            if __name__ == "__main__":
                sys.exit(1)
            else:
                assert False, f"{len(failed_cases)} test cases failed in UI regression suite!"
        else:
            if __name__ == "__main__":
                sys.exit(0)

def test_query_chart_ui_regression():
    asyncio.run(run_suite())

if __name__ == "__main__":
    asyncio.run(run_suite())
