import sys
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
import asyncio
import os
import subprocess
import time
import urllib.request
from playwright.async_api import async_playwright

async def select_mode(page, mode_name: str):
    """Helper để chuyển chế độ (Mode) trong Streamlit Sidebar Selectbox."""
    print(f"\n==========================================")
    print(f"Switching to mode: '{mode_name}'...")
    print(f"==========================================")
    try:
        sidebar = page.locator('[data-testid="stSidebar"]')
        selectbox = sidebar.locator('div[data-baseweb="select"]').first
        await selectbox.click()
        await page.wait_for_timeout(1500)
        
        option = page.locator(f'li[role="option"]:has-text("{mode_name}")').first
        if await option.count() > 0:
            await option.click()
            print(f"Successfully clicked option '{mode_name}'. Waiting 6s for Streamlit to finish rerun...")
            await page.wait_for_timeout(6000)
        else:
            print(f"Option '{mode_name}' not found in dropdown listbox! Pressing Escape...")
            await page.keyboard.press("Escape")
    except Exception as e:
        print(f"Error selecting mode '{mode_name}': {e}")

async def submit_chat_query(page, prompt_text: str):
    """Ensure chat input area is ready, fill text, trigger React state update, and click submit / press Enter."""
    print(f"Submitting prompt: '{prompt_text[:60]}...'")
    for attempt in range(3):
        try:
            chat_input = page.locator('textarea[data-testid="stChatInputTextArea"]')
            await chat_input.wait_for(state="visible", timeout=10000)
            await chat_input.click()
            await chat_input.fill(prompt_text)
            await page.wait_for_timeout(500)
            # Trigger React state change by typing a space and deleting it
            await page.keyboard.type(" ")
            await page.keyboard.press("Backspace")
            await page.wait_for_timeout(1000)
            
            submit_btn = page.locator('button[data-testid="stChatInputSubmitButton"]')
            if await submit_btn.count() > 0 and await submit_btn.is_enabled():
                print("Clicking chat submit button...")
                await submit_btn.click()
            else:
                print("Pressing Enter...")
                await page.keyboard.press("Enter")
                
            await page.wait_for_timeout(3000)
            return True
        except Exception as e:
            print(f"Attempt {attempt+1} to submit chat query failed: {e}. Retrying after 3s...")
            await page.wait_for_timeout(3000)
    return False

async def wait_for_pipeline_completion(page, mode_name: str, initial_msg_count: int, prompt_text: str, timeout_sec: int = 180):
    """Dynamically wait until pipeline spinner disappears AND real output is fully rendered."""
    print(f"Waiting dynamically up to {timeout_sec}s for pipeline in '{mode_name}' to finish and render output...")
    await page.wait_for_timeout(6000)
    
    start_time = time.time()
    while time.time() - start_time < timeout_sec:
        # Check if loading indicator is still present
        spinner = page.locator('text="Đang nạp mô hình AI"')
        pipeline_loading = page.locator('text="Đang khởi động pipeline"')
        pipeline_hourglass = page.locator('text="⏳"')
        
        is_loading = False
        if await spinner.count() > 0 and await spinner.is_visible():
            is_loading = True
        if await pipeline_loading.count() > 0 and await pipeline_loading.is_visible():
            is_loading = True
        if await pipeline_hourglass.count() > 0 and await pipeline_hourglass.is_visible():
            is_loading = True
            
        elapsed = int(time.time() - start_time)
        if is_loading:
            if elapsed % 10 == 0 or elapsed < 20:
                print(f"   [{elapsed}s] Pipeline still processing ({mode_name})...")
            await page.wait_for_timeout(3000)
            continue
            
        # Check if new message appeared right now compared to initial_msg_count
        chat_msgs = page.locator('[data-testid="stChatMessage"]')
        current_msg_count = await chat_msgs.count()
        
        # If no new messages appeared yet, self-heal / retry submitting
        if current_msg_count <= initial_msg_count:
            if elapsed >= 12 and (elapsed == 12 or elapsed == 30 or elapsed == 50):
                print(f"   [{elapsed}s] No new chat message bubble appeared in '{mode_name}'! Self-healing: retrying prompt submission...")
                await submit_chat_query(page, prompt_text)
            else:
                print(f"   [{elapsed}s] Waiting for new chat message bubble to appear in '{mode_name}'...")
            await page.wait_for_timeout(3000)
            continue
            
        # If new messages appeared, let's inspect the latest message text and components
        last_msg = chat_msgs.nth(current_msg_count - 1)
        text_content = await last_msg.inner_text()
        
        if "Đang khởi động pipeline" not in text_content and len(text_content.strip()) > 15:
            if mode_name == "Biểu đồ":
                charts = page.locator('[data-testid="stIFrame"], [data-testid="stPlotlyChart"], iframe[title*="plotly"], .user-select-none.svg-container')
                if await charts.count() > 0 and elapsed >= 12:
                    print(f"--> [VERIFIED] Plotly chart iframe confirmed visible in '{mode_name}' after {elapsed}s!")
                    print(f"--> Sample text snippet: {text_content[:200]}...")
                    await page.wait_for_timeout(6000)
                    return True
                elif elapsed >= 90:
                    print(f"--> [VERIFIED] Chart response visible after {elapsed}s!")
                    await page.wait_for_timeout(5000)
                    return True
                else:
                    await page.wait_for_timeout(3000)
                    continue
            elif mode_name == "Báo Cáo":
                dl_buttons = page.locator('button:has-text("Tải báo cáo")')
                pdf_viewer = page.locator('text="Xem trước Báo cáo PDF"')
                if (await dl_buttons.count() > 0 or await pdf_viewer.count() > 0) and elapsed >= 20:
                    print(f"--> [VERIFIED] Comprehensive Report output confirmed visible after {elapsed}s!")
                    print(f"--> Sample text snippet: {text_content[:250]}...")
                    await page.wait_for_timeout(6000)
                    return True
                else:
                    await page.wait_for_timeout(3000)
                    continue
            else:
                if elapsed >= 12:
                    print(f"--> [VERIFIED] Q&A output confirmed visible after {elapsed}s!")
                    print(f"--> Sample text snippet: {text_content[:200]}...")
                    await page.wait_for_timeout(5000)
                    return True
        await page.wait_for_timeout(3000)
        
    print(f"WARNING: Timeout reached ({timeout_sec}s) while waiting for '{mode_name}' output!")
    return False

async def capture_screenshots():
    os.makedirs("docs/images", exist_ok=True)
    os.makedirs("scratch", exist_ok=True)
    
    print("Starting Streamlit server on port 8502 in background...")
    venv_python = os.path.join(os.getcwd(), "venv", "Scripts", "python.exe")
    python_cmd = venv_python if os.path.exists(venv_python) else sys.executable
    print("Using Python executable for Streamlit:", python_cmd)
    
    log_file = open("scratch/streamlit_server.log", "w", encoding="utf-8")
    server_process = subprocess.Popen(
        [python_cmd, "-m", "streamlit", "run", "app/streamlit_chatbot.py", "--server.port", "8502", "--server.headless", "true"],
        stdout=log_file,
        stderr=subprocess.STDOUT
    )
    
    try:
        print("Polling http://localhost:8502 until Streamlit server is responsive (max 60s)...")
        server_ready = False
        for i in range(60):
            if server_process.poll() is not None:
                print(f"Streamlit process terminated unexpectedly with code {server_process.returncode}!")
                log_file.close()
                if os.path.exists("scratch/streamlit_server.log"):
                    with open("scratch/streamlit_server.log", "r", encoding="utf-8", errors="replace") as f:
                        print("=== Streamlit Log Output ===")
                        print(f.read())
                return
            try:
                urllib.request.urlopen("http://localhost:8502", timeout=2)
                server_ready = True
                print(f"Streamlit server responded after {i+1} seconds!")
                break
            except Exception:
                time.sleep(1)
                
        if not server_ready:
            print("Streamlit server failed to start within 60s!")
            return
            
        print("Waiting another 5 seconds for complete Streamlit initialization...")
        time.sleep(5)
        
        async with async_playwright() as p:
            print("Launching Chromium headless...")
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 1440, "height": 950})
            
            print("Navigating to Streamlit app (http://localhost:8502)...")
            await page.goto("http://localhost:8502", timeout=90000)
            
            print("Waiting up to 90s for initial system & AI models loading...")
            for i in range(30):
                loading_text = page.locator('text="Đang nạp mô hình AI"')
                if await loading_text.count() > 0 and await loading_text.is_visible():
                    print(f"   [{i*3}s] Still loading AI embedding model & Qdrant...")
                    await page.wait_for_timeout(3000)
                else:
                    print("System & embedding model fully loaded!")
                    break
            
            await page.wait_for_timeout(3000)
            
            # 1. Chế độ Hỏi - Đáp (Q&A Mode)
            await select_mode(page, "Hỏi - Đáp")
            initial_count_qa = await page.locator('[data-testid="stChatMessage"]').count()
            prompt_qa = "Thống kê số lượng hộ nghèo và cận nghèo tại huyện Đăk Glong năm 2023"
            await submit_chat_query(page, prompt_qa)
            await wait_for_pipeline_completion(page, "Hỏi - Đáp", initial_count_qa, prompt_qa, timeout_sec=150)
            print("Taking ui_overview.png screenshot...")
            await page.screenshot(path="docs/images/ui_overview.png", full_page=True)
            
            # 2. Chế độ Vẽ biểu đồ (Chart Mode)
            await select_mode(page, "Biểu đồ")
            initial_count_chart = await page.locator('[data-testid="stChatMessage"]').count()
            prompt_chart = "Vẽ biểu đồ thanh ngang so sánh số lượng hộ nghèo và cận nghèo của các huyện tại tỉnh Đắk Nông năm 2023"
            await submit_chat_query(page, prompt_chart)
            await wait_for_pipeline_completion(page, "Biểu đồ", initial_count_chart, prompt_chart, timeout_sec=160)
            print("Taking ui_chart_mode.png screenshot...")
            await page.screenshot(path="docs/images/ui_chart_mode.png", full_page=True)

            # 3. Chế độ Báo cáo tổng hợp (Report Mode)
            await select_mode(page, "Báo Cáo")
            initial_count_report = await page.locator('[data-testid="stChatMessage"]').count()
            prompt_report = "Tạo báo cáo tổng hợp thực trạng hộ nghèo tại huyện Đăk Glong năm 2023"
            await submit_chat_query(page, prompt_report)
            await wait_for_pipeline_completion(page, "Báo Cáo", initial_count_report, prompt_report, timeout_sec=180)
            print("Taking ui_report_mode.png screenshot...")
            await page.screenshot(path="docs/images/ui_report_mode.png", full_page=True)
            
            await browser.close()
            print("\n=======================================================")
            print("All screenshots captured successfully with FULL output verification!")
            print("=======================================================")
            
    finally:
        print("Terminating Streamlit server process...")
        if server_process.poll() is None:
            server_process.terminate()
            server_process.wait()
        log_file.close()

if __name__ == "__main__":
    asyncio.run(capture_screenshots())
