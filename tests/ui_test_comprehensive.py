import asyncio
from playwright.async_api import async_playwright
import time
import sys
import io

try:
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
except Exception:
    pass

QA_PROMPTS = [
    "có bao nhiêu hộ nghèo",
    "xã đắk ndrot có bao nhiêu hộ cận nghèo",
    "ai là chủ hộ của hộ có mã 12345", 
    "huyện nào có nhiều hộ nghèo nhất",
    "thống kê"
]

BAO_CAO_PROMPTS = [
    "tạo báo cáo 1",
    "xuất báo cáo số 3",
    "báo cáo 8 huyện Đắk Mil",
    "tạo báo cáo 13",
    "báo cáo"
]

BIEU_DO_PROMPTS = [
    "vẽ biểu đồ số hộ nghèo Đắk Mil",
    "tạo biểu đồ tỷ lệ hộ cận nghèo theo huyện",
    "biểu đồ nguyên nhân nghèo",
    "vẽ đồ thị hộ nghèo thiếu hụt bảo hiểm y tế",
    "đồ thị 10 xã nghèo nhất",
    "biểu đồ tỷ lệ B1",
    "vẽ biểu đồ 5 xã",
    "tạo biểu đồ phân bố độ tuổi",
    "biểu đồ tỷ lệ dân tộc tại chỗ",
    "biểu đồ thoát nghèo",
    "biểu đồ hộ nghèo các xã huyện Krông Nô",
    "đồ thị cột số lượng hộ cận nghèo",
    "vẽ biểu đồ tròn cơ cấu dân tộc",
    "vẽ biểu đồ đường xu hướng",
    "biểu đồ heatmap thiếu hụt",
    "biểu đồ phân loại hộ nghèo",
    "tạo biểu đồ so sánh",
    "so sánh",
    "vẽ biểu đồ điểm b1",
    "vẽ biểu đồ thiếu hụt nước sạch",
    "đồ thị hộ nghèo đa chiều"
]

ALL_PROMPTS = (
    [("Hỏi - Đáp", p) for p in QA_PROMPTS] +
    [("Báo Cáo", p) for p in BAO_CAO_PROMPTS] +
    [("Biểu đồ", p) for p in BIEU_DO_PROMPTS]
)

async def run_tests():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Connecting to Streamlit at http://localhost:8501...")
        try:
            await page.goto("http://localhost:8501", wait_until="networkidle", timeout=15000)
        except Exception as e:
            print(f"Could not connect to Streamlit. Is it running? {e}")
            sys.exit(1)
            
        async def submit_and_wait(prompt, mode):
            print(f"\n--- Testing Mode: {mode} | Prompt: '{prompt}' ---")
            
            try:
                # 0. Reload page to isolate tests
                await page.reload(wait_until="networkidle")
                
                # 1. Change mode
                mode_box = page.locator("div[data-testid='stSelectbox']")
                await mode_box.click()
                await page.keyboard.type(mode)
                await page.keyboard.press("Enter")
                await page.wait_for_timeout(1000) # wait for streamlit rerun
                
                # 2. Input Prompt
                chat_input = page.locator("textarea[data-testid='stChatInputTextArea']")
                await chat_input.fill(prompt)
                await chat_input.press("Enter")
                
                # 3. Wait for response
                print("Waiting for response...")
                
                # Wait for any status indicators to disappear (first step)
                try:
                    await page.locator("text=⏳ Đang").wait_for(state="visible", timeout=2000)
                    await page.locator("text=⏳ Đang").wait_for(state="hidden", timeout=180000) # Increased to 3 mins
                except:
                    pass
                
                # 4. Check results
                messages = page.locator("div[data-testid='stChatMessage']")
                # wait until at least one message is there
                await messages.first.wait_for(state="visible", timeout=10000)
                
                count = await messages.count()
                if count == 0:
                    print("FAILED: No messages found in UI.")
                    return False
                    
                last_msg = messages.nth(count - 1)
                
                if "so sánh" in prompt or "báo cáo" == prompt.lower() or "thống kê" == prompt.lower() or "vẽ biểu đồ" == prompt.lower() or "tạo biểu đồ" == prompt.lower():
                    # This should trigger Ambiguity Guardrail
                    try:
                        # Wait for the status placeholder to disappear or the text to appear
                        expect_text = page.locator("text=chung chung")
                        await expect_text.first.wait_for(state="visible", timeout=10000)
                        print("PASSED (Ambiguity Gracefully Handled)")
                        return True
                    except Exception as e:
                        text = await last_msg.inner_text()
                        print("FAILED (Did not catch ambiguity properly)")
                        print(f"Output text preview: {text[:200]}")
                        await page.screenshot(path=f"fail_ambiguity_{prompt.replace(' ', '_')}.png")
                        return False
                        
                elif mode == "Báo Cáo":
                    # Look for download buttons anywhere in the last message
                    dl_buttons = last_msg.locator("button", has_text="Tải báo cáo")
                    try:
                        # Streamlit streams text, so wait up to 30s for the button to appear
                        await dl_buttons.first.wait_for(state="visible", timeout=30000)
                        print("PASSED (Found download buttons)")
                        return True
                    except Exception:
                        text = await last_msg.inner_text()
                        if "Câu hỏi không liên quan" in text or "nằm ngoài phạm vi" in text:
                            print(f"FAILED (Blocked by Guardrail): {text.strip()[:100]}...")
                            return False
                            
                        print("FAILED (No download buttons generated)")
                        print(f"Output text preview: {text[:200]}")
                        await page.screenshot(path=f"fail_bao_cao.png")
                        html = await last_msg.inner_html()
                        with open("fail_bao_cao.html", "w", encoding="utf-8") as f:
                            f.write(html)
                        return False
                        
                elif mode == "Biểu đồ":
                    # Look for Plotly chart container
                    chart = last_msg.locator(".js-plotly-plot")
                    try:
                        await chart.first.wait_for(state="visible", timeout=30000)
                        print("PASSED (Found Plotly chart)")
                        return True
                    except Exception:
                        text = await last_msg.inner_text()
                        if "Câu hỏi không liên quan" in text or "nằm ngoài phạm vi" in text:
                            print(f"FAILED (Blocked by Guardrail): {text.strip()[:100]}...")
                            return False
                            
                        print("FAILED (No chart found)")
                        print(f"Output text preview: {text[:200]}")
                        await page.screenshot(path=f"fail_chart.png")
                        html = await last_msg.inner_html()
                        with open("fail_chart.html", "w", encoding="utf-8") as f:
                            f.write(html)
                        return False
                        
                elif mode == "Hỏi - Đáp":
                    try:
                        text = await last_msg.inner_text()
                        if len(text.strip()) > 10:
                            print("PASSED (Got Q&A response)")
                            return True
                        else:
                            print("FAILED (Empty Q&A response)")
                            return False
                    except Exception as e:
                        print(f"FAILED (Error reading Q&A text): {e}")
                        return False
            except Exception as e:
                print(f"Exception during test: {e}")
                return False

        passed = 0
        failed = 0
        
        for mode, prompt in ALL_PROMPTS:
            if await submit_and_wait(prompt, mode):
                passed += 1
            else:
                failed += 1
                
        print(f"\n=== TEST SUMMARY ===")
        print(f"Passed: {passed}/{len(ALL_PROMPTS)}")
        print(f"Failed: {failed}")
        
        await browser.close()
        if failed > 0:
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_tests())
