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
    print(f"Switching to mode: '{mode_name}'...")
    try:
        sidebar = page.locator('[data-testid="stSidebar"]')
        selectbox = sidebar.locator('div[data-baseweb="select"]').first
        await selectbox.click()
        await page.wait_for_timeout(1000)
        
        option = page.locator(f'li[role="option"]:has-text("{mode_name}")').first
        if await option.count() > 0:
            await option.click()
            print(f"Successfully clicked option '{mode_name}'. Waiting 4s for rerun...")
            await page.wait_for_timeout(4000)
        else:
            print(f"Option '{mode_name}' not found in dropdown listbox! Pressing Escape...")
            await page.keyboard.press("Escape")
    except Exception as e:
        print(f"Error selecting mode '{mode_name}': {e}")

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
            
            # Chờ 45 giây theo yêu cầu để hệ thống tải hoàn tất mô hình AITeamVN/Vietnamese_Embedding & Qdrant
            print("Waiting 45 seconds for initial system & AI models loading...")
            await page.wait_for_timeout(45000)
            
            # Kiểm tra thêm nếu vẫn còn dòng "Đang nạp mô hình AI" thì chờ tiếp đến khi hoàn tất
            for _ in range(30):
                loading_text = page.locator('text="Đang nạp mô hình AI & khởi tạo hệ thống"')
                if await loading_text.count() > 0 and await loading_text.is_visible():
                    print("Still loading AI model... waiting another 3 seconds...")
                    await page.wait_for_timeout(3000)
                else:
                    break
            
            print("System fully loaded! Chờ thêm 3s để giao diện ổn định...")
            await page.wait_for_timeout(3000)
            
            # 1. Chế độ Hỏi - Đáp (Q&A Mode)
            await select_mode(page, "Hỏi - Đáp")
            print("Submitting sample Q&A query...")
            try:
                chat_input = page.locator('textarea[data-testid="stChatInputTextArea"]')
                if await chat_input.count() > 0:
                    await chat_input.fill("Thống kê số lượng hộ nghèo và cận nghèo tại huyện Đăk Glong năm 2023")
                    await page.keyboard.press("Enter")
                    print("Waiting 20 seconds for Q&A result to stream and render completely...")
                    await page.wait_for_timeout(20000)
            except Exception as e:
                print(f"Error submitting Q&A query: {e}")

            print("Taking ui_overview.png screenshot...")
            await page.screenshot(path="docs/images/ui_overview.png", full_page=True)
            
            # 2. Chế độ Vẽ biểu đồ (Chart Mode)
            await select_mode(page, "Biểu đồ")
            print("Submitting Chart prompt...")
            try:
                chat_input = page.locator('textarea[data-testid="stChatInputTextArea"]')
                if await chat_input.count() > 0:
                    await chat_input.fill("Vẽ biểu đồ cột so sánh số lượng hộ nghèo và cận nghèo tại huyện Đăk Glong năm 2023")
                    await page.keyboard.press("Enter")
                    print("Waiting 25 seconds for Plotly chart to generate and render...")
                    await page.wait_for_timeout(25000)
            except Exception as e:
                print(f"Error submitting Chart prompt: {e}")

            print("Taking ui_chart_mode.png screenshot...")
            await page.screenshot(path="docs/images/ui_chart_mode.png", full_page=True)

            # 3. Chế độ Báo cáo tổng hợp (Report Mode)
            await select_mode(page, "Báo Cáo")
            print("Submitting Report prompt...")
            try:
                chat_input = page.locator('textarea[data-testid="stChatInputTextArea"]')
                if await chat_input.count() > 0:
                    await chat_input.fill("Tạo báo cáo tổng hợp thực trạng hộ nghèo tại huyện Đăk Glong năm 2023")
                    await page.keyboard.press("Enter")
                    print("Waiting 25 seconds for Comprehensive Report to render...")
                    await page.wait_for_timeout(25000)
            except Exception as e:
                print(f"Error submitting Report prompt: {e}")

            print("Taking ui_report_mode.png screenshot...")
            await page.screenshot(path="docs/images/ui_report_mode.png", full_page=True)
            
            await browser.close()
            print("All screenshots captured successfully with 45s+ startup wait time!")
            
    finally:
        print("Terminating Streamlit server process...")
        if server_process.poll() is None:
            server_process.terminate()
            server_process.wait()
        log_file.close()

if __name__ == "__main__":
    asyncio.run(capture_screenshots())
