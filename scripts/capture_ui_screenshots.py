import asyncio
import os
import sys
import subprocess
import time
from playwright.async_api import async_playwright

async def capture_screenshots():
    os.makedirs("docs/images", exist_ok=True)
    
    print("Starting Streamlit server on port 8502 in background...")
    server_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app/streamlit_chatbot.py", "--server.port", "8502", "--server.headless", "true"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    try:
        print("Waiting 12 seconds for Streamlit process to warm up...")
        time.sleep(12)
        
        async with async_playwright() as p:
            print("Launching Chromium headless...")
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 1440, "height": 950})
            
            print("Navigating to Streamlit app (http://localhost:8502)...")
            await page.goto("http://localhost:8502", timeout=60000)
            
            # 1. Chờ 25s để hệ thống load xong model, DuckDB, Qdrant và render xong giao diện ban đầu
            print("Waiting 25 seconds for initial system & models loading...")
            await page.wait_for_timeout(25000)
            
            # Gửi 1 câu hỏi mẫu trong chế độ Hỏi - Đáp ban đầu
            print("Submitting sample Q&A query...")
            try:
                chat_input = page.locator('textarea[data-testid="stChatInputTextArea"]')
                if await chat_input.count() > 0:
                    await chat_input.fill("Có bao nhiêu hộ nghèo tại huyện Lắk trong năm 2023?")
                    await page.keyboard.press("Enter")
                    print("Waiting 12 seconds for Q&A result...")
                    await page.wait_for_timeout(12000)
            except Exception as e:
                print(f"Error submitting Q&A query: {e}")

            print("Taking ui_overview.png screenshot...")
            await page.screenshot(path="docs/images/ui_overview.png", full_page=True)
            
            # 2. Chuyển sang chế độ Vẽ biểu đồ
            print("Switching to Chart Mode ('Vẽ biểu đồ')...")
            try:
                sidebar = page.locator('[data-testid="stSidebar"]')
                if await sidebar.count() > 0:
                    await sidebar.get_by_text("Vẽ biểu đồ").first.click()
                    print("Waiting 4 seconds for mode switch...")
                    await page.wait_for_timeout(4000)
            except Exception as e:
                print(f"Error switching to Chart Mode: {e}")

            print("Submitting Chart prompt...")
            try:
                chat_input = page.locator('textarea[data-testid="stChatInputTextArea"]')
                if await chat_input.count() > 0:
                    await chat_input.fill("Vẽ biểu đồ cột so sánh số lượng hộ nghèo và cận nghèo tại huyện Lắk năm 2023")
                    await page.keyboard.press("Enter")
                    print("Waiting 15 seconds for Plotly chart to generate and render...")
                    await page.wait_for_timeout(15000)
            except Exception as e:
                print(f"Error submitting Chart prompt: {e}")

            print("Taking ui_chart_mode.png screenshot...")
            await page.screenshot(path="docs/images/ui_chart_mode.png", full_page=True)

            # 3. Chuyển sang chế độ Báo cáo tổng hợp
            print("Switching to Report Mode ('Báo cáo tổng hợp')...")
            try:
                sidebar = page.locator('[data-testid="stSidebar"]')
                if await sidebar.count() > 0:
                    await sidebar.get_by_text("Báo cáo tổng hợp").first.click()
                    print("Waiting 4 seconds for mode switch...")
                    await page.wait_for_timeout(4000)
            except Exception as e:
                print(f"Error switching to Report Mode: {e}")

            print("Submitting Report prompt...")
            try:
                chat_input = page.locator('textarea[data-testid="stChatInputTextArea"]')
                if await chat_input.count() > 0:
                    await chat_input.fill("Tạo báo cáo tổng hợp thực trạng hộ nghèo tại huyện Lắk năm 2023")
                    await page.keyboard.press("Enter")
                    print("Waiting 15 seconds for Comprehensive Report to render...")
                    await page.wait_for_timeout(15000)
            except Exception as e:
                print(f"Error submitting Report prompt: {e}")

            print("Taking ui_report_mode.png screenshot...")
            await page.screenshot(path="docs/images/ui_report_mode.png", full_page=True)
            
            await browser.close()
            print("All screenshots captured successfully with proper wait times!")
            
    finally:
        print("Terminating Streamlit server process...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    asyncio.run(capture_screenshots())
