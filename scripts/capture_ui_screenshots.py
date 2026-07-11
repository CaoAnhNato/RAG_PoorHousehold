import asyncio
import os
import sys
import subprocess
import time
from playwright.async_api import async_playwright

async def capture_screenshots():
    os.makedirs("docs/images", exist_ok=True)
    
    print("Starting Streamlit server in background...")
    server_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app/streamlit_chatbot.py", "--server.port", "8502", "--server.headless", "true"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    try:
        print("Waiting 6 seconds for Streamlit to initialize...")
        time.sleep(6)
        
        async with async_playwright() as p:
            print("Launching Chromium headless...")
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 1440, "height": 900})
            
            print("Navigating to Streamlit app (http://localhost:8502)...")
            await page.goto("http://localhost:8502", timeout=30000)
            await page.wait_for_timeout(4000) # Wait for initial render
            
            # 1. Capture UI Overview / Q&A Mode
            print("Taking ui_overview.png screenshot...")
            await page.screenshot(path="docs/images/ui_overview.png", full_page=True)
            
            # 2. Switch to Chart Mode and ask a chart query
            print("Switching to Chart Mode...")
            try:
                # Find mode selector (radio or selectbox in sidebar/main)
                # In streamlit, sidebar inputs usually have data-testid="stRadio" or "stSelectbox"
                sidebar = page.locator('[data-testid="stSidebar"]')
                if await sidebar.count() > 0:
                    mode_radio = sidebar.locator('input[type="radio"]')
                    if await mode_radio.count() >= 2:
                        # Click on 'Vẽ biểu đồ'
                        await sidebar.get_by_text("Vẽ biểu đồ").first.click()
                        await page.wait_for_timeout(2000)
            except Exception as e:
                print(f"Note switching to chart mode via sidebar: {e}")

            # Send a query to generate chart
            try:
                chat_input = page.locator('textarea[data-testid="stChatInputTextArea"]')
                if await chat_input.count() > 0:
                    await chat_input.fill("Vẽ biểu đồ số lượng hộ nghèo và cận nghèo tại huyện Lắk năm 2023")
                    await page.keyboard.press("Enter")
                    print("Waiting for chart output...")
                    await page.wait_for_timeout(10000) # wait for LLM/SQL chart generation
            except Exception as e:
                print(f"Note submitting chart prompt: {e}")

            print("Taking ui_chart_mode.png screenshot...")
            await page.screenshot(path="docs/images/ui_chart_mode.png", full_page=True)

            # 3. Switch to Report Mode and ask a report query
            print("Switching to Report Mode...")
            try:
                sidebar = page.locator('[data-testid="stSidebar"]')
                if await sidebar.count() > 0:
                    await sidebar.get_by_text("Báo cáo tổng hợp").first.click()
                    await page.wait_for_timeout(2000)
            except Exception as e:
                print(f"Note switching to report mode: {e}")

            try:
                chat_input = page.locator('textarea[data-testid="stChatInputTextArea"]')
                if await chat_input.count() > 0:
                    await chat_input.fill("Tạo báo cáo tổng hợp tình hình hộ nghèo huyện Lắk")
                    await page.keyboard.press("Enter")
                    print("Waiting for report output...")
                    await page.wait_for_timeout(10000)
            except Exception as e:
                print(f"Note submitting report prompt: {e}")

            print("Taking ui_report_mode.png screenshot...")
            await page.screenshot(path="docs/images/ui_report_mode.png", full_page=True)
            
            await browser.close()
            print("All screenshots captured successfully in docs/images/!")
            
    finally:
        print("Terminating Streamlit server process...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    asyncio.run(capture_screenshots())
