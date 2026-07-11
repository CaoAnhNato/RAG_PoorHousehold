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
        print("Waiting 15 seconds for Streamlit process to warm up...")
        time.sleep(15)
        
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
            
            # 1. Gửi câu hỏi mẫu trong chế độ Hỏi - Đáp
            print("Submitting sample Q&A query...")
            try:
                chat_input = page.locator('textarea[data-testid="stChatInputTextArea"]')
                if await chat_input.count() > 0:
                    await chat_input.fill("Có bao nhiêu hộ nghèo tại huyện Lắk trong năm 2023?")
                    await page.keyboard.press("Enter")
                    print("Waiting 20 seconds for Q&A result to stream and render completely...")
                    await page.wait_for_timeout(20000)
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
                    print("Waiting 5 seconds for mode switch...")
                    await page.wait_for_timeout(5000)
            except Exception as e:
                print(f"Error switching to Chart Mode: {e}")

            print("Submitting Chart prompt...")
            try:
                chat_input = page.locator('textarea[data-testid="stChatInputTextArea"]')
                if await chat_input.count() > 0:
                    await chat_input.fill("Vẽ biểu đồ cột so sánh số lượng hộ nghèo và cận nghèo tại huyện Lắk năm 2023")
                    await page.keyboard.press("Enter")
                    print("Waiting 25 seconds for Plotly chart to generate and render...")
                    await page.wait_for_timeout(25000)
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
                    print("Waiting 5 seconds for mode switch...")
                    await page.wait_for_timeout(5000)
            except Exception as e:
                print(f"Error switching to Report Mode: {e}")

            print("Submitting Report prompt...")
            try:
                chat_input = page.locator('textarea[data-testid="stChatInputTextArea"]')
                if await chat_input.count() > 0:
                    await chat_input.fill("Tạo báo cáo tổng hợp thực trạng hộ nghèo tại huyện Lắk năm 2023")
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
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    asyncio.run(capture_screenshots())
