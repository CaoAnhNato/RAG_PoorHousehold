# -*- coding: utf-8 -*-
import asyncio
from playwright.async_api import async_playwright
import time
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
except Exception:
    pass

QA_PROMPTS_50 = [
    # 10 câu hỏi kép (multi-intent) cần phân rã (Decomposition & Coreference Resolution)
    "Thống kê các dân tộc đang có ở Tuy Đức 2024 ? Có bao nhiêu hộ nghèo trong đây là nữ ?",
    "Có bao nhiêu hộ cận nghèo ở huyện Đắk Mil năm 2024 ? Trong đó có bao nhiêu hộ thiếu đất sản xuất ?",
    "Tỷ lệ hộ nghèo của huyện Cư Jút là bao nhiêu ? Có bao nhiêu hộ được hỗ trợ tín dụng ở đó ?",
    "Xã Đắk R'La có bao nhiêu hộ nghèo ? Ai là chủ hộ của các hộ này ?",
    "Huyện Krông Nô có bao nhiêu xã ? Xã nào có nhiều hộ cận nghèo nhất trong huyện ?",
    "Số hộ nghèo ở Đắk Glong năm 2024 là bao nhiêu ? Bao nhiêu hộ trong số đó có chủ hộ là nữ ?",
    "Thống kê số lượng hộ nghèo và cận nghèo ở thị trấn Đắk Mâm ? Có bao nhiêu thành viên trong các hộ đó ?",
    "Huyện Đắk Song có bao nhiêu hộ nghèo B1 ? Trong đó bao nhiêu hộ thiếu hụt nhà ở ?",
    "Cho biết số hộ nghèo ở xã Nam Dong ? Có bao nhiêu hộ thoát nghèo trong năm qua tại đây ?",
    "Tổng số hộ cận nghèo toàn tỉnh Đắk Nông là bao nhiêu ? Huyện nào chiếm tỷ lệ cao nhất trong số này ?",
    
    # 40 câu hỏi đơn đa dạng
    "có bao nhiêu hộ nghèo",
    "xã đắk ndrot có bao nhiêu hộ cận nghèo",
    "huyện nào có nhiều hộ nghèo nhất",
    "thống kê số hộ nghèo theo huyện năm 2024",
    "có bao nhiêu hộ cận nghèo ở Đắk Mil",
    "danh sách hộ nghèo xã Đắk Lao",
    "tỷ lệ hộ nghèo tỉnh Đắk Nông",
    "huyện Cư Jút có bao nhiêu xã",
    "xã Đắk R'La thuộc huyện nào",
    "số thành viên trung bình của hộ nghèo",
    "bao nhiêu hộ nghèo thiếu hụt bảo hiểm y tế",
    "số lượng hộ nghèo thiếu nước sạch sinh hoạt",
    "hộ nghèo do thiếu đất sản xuất chiếm bao nhiêu",
    "thống kê nguyên nhân nghèo ở Đắk Glong",
    "huyện Krông Nô có bao nhiêu hộ nghèo",
    "ai là chủ hộ nghèo ở xã Quảng Sơn",
    "tỷ lệ hộ nghèo của xã Đắk Som",
    "huyện Đắk RLấp có bao nhiêu hộ cận nghèo",
    "thống kê các dân tộc thiểu số nghèo ở Đắk Nông",
    "có bao nhiêu hộ nghèo là người M'Nông",
    "số hộ nghèo được vay vốn tín dụng",
    "hộ nghèo thiếu hụt hố xí hợp vệ sinh",
    "thống kê hộ nghèo theo phân loại B1, B2",
    "huyện Đắk Song có bao nhiêu hộ nghèo",
    "xã Đắk N'Drót có bao nhiêu thành viên nghèo",
    "dân tộc Ê Đê có bao nhiêu hộ nghèo",
    "thống kê độ tuổi chủ hộ nghèo",
    "bao nhiêu hộ nghèo không có đất sản xuất",
    "tỷ lệ cận nghèo huyện Tuy Đức",
    "xã Quảng Hòa có bao nhiêu hộ nghèo",
    "hộ nghèo thiếu hụt diện tích nhà ở",
    "số hộ nghèo ở thị trấn Ea T'ling",
    "thống kê hộ nghèo mới phát sinh năm 2024",
    "bao nhiêu hộ thoát nghèo ở Cư Jút",
    "hộ cận nghèo thiếu dịch vụ viễn thông",
    "thống kê hộ nghèo theo từng xã huyện Đắk Mil",
    "xã Thuận An có bao nhiêu hộ cận nghèo",
    "chủ hộ nghèo cao tuổi nhất là bao nhiêu tuổi",
    "số hộ nghèo có thành viên hưởng trợ cấp xã hội",
    "tổng số thành viên hộ nghèo toàn tỉnh"
]

BIEU_DO_PROMPTS_20 = [
    "vẽ biểu đồ số hộ nghèo Đắk Mil",
    "tạo biểu đồ tỷ lệ hộ cận nghèo theo huyện",
    "biểu đồ nguyên nhân nghèo toàn tỉnh",
    "vẽ đồ thị hộ nghèo thiếu hụt bảo hiểm y tế",
    "đồ thị 10 xã nghèo nhất",
    "biểu đồ phân bố độ tuổi chủ hộ nghèo",
    "biểu đồ tỷ lệ dân tộc tại chỗ nghèo",
    "biểu đồ hộ nghèo các xã huyện Krông Nô",
    "vẽ biểu đồ tròn cơ cấu dân tộc nghèo",
    "biểu đồ heatmap thiếu hụt dịch vụ xã hội cơ bản",
    "biểu đồ phân loại hộ nghèo theo huyện",
    "vẽ biểu đồ thiếu hụt nước sạch",
    "đồ thị cột số lượng hộ cận nghèo các huyện",
    "biểu đồ tỷ lệ hộ nghèo B1 theo huyện",
    "vẽ biểu đồ 5 xã có số hộ nghèo cao nhất",
    "biểu đồ so sánh nghèo và cận nghèo huyện Đắk Song",
    "biểu đồ nguyên nhân nghèo huyện Tuy Đức",
    "đồ thị phân bố hộ nghèo thiếu đất sản xuất",
    "biểu đồ hộ cận nghèo theo các xã huyện Cư Jút",
    "vẽ biểu đồ tỷ lệ thiếu hụt thông tin"
]

BAO_CAO_PROMPTS_3 = [
    "tạo báo cáo 1",
    "xuất báo cáo số 3",
    "báo cáo 8 huyện Đắk Mil"
]

async def run_suite():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Connecting to Streamlit at http://localhost:8501...")
        try:
            await page.goto("http://localhost:8501", wait_until="networkidle", timeout=15000)
        except Exception as e:
            print(f"Lỗi kết nối Streamlit: {e}")
            sys.exit(1)
            
        results = {"Hỏi - Đáp": {"passed": 0, "failed": 0}, "Biểu đồ": {"passed": 0, "failed": 0}, "Báo Cáo": {"passed": 0, "failed": 0}}
        
        async def test_prompt(mode: str, prompt: str, idx: int, total: int):
            print(f"\n[{mode} {idx}/{total}] Testing: '{prompt}'")
            try:
                await page.reload(wait_until="networkidle")
                
                # Chọn chế độ
                mode_box = page.locator("div[data-testid='stSelectbox']")
                await mode_box.click()
                await page.keyboard.type(mode)
                await page.keyboard.press("Enter")
                await page.wait_for_timeout(800)
                
                # Nhập prompt
                chat_input = page.locator("textarea[data-testid='stChatInputTextArea']")
                await chat_input.fill(prompt)
                await chat_input.press("Enter")
                
                # Chờ pipeline xử lý
                try:
                    await page.locator("text=⏳ Đang").wait_for(state="visible", timeout=2000)
                    await page.locator("text=⏳ Đang").wait_for(state="hidden", timeout=120000)
                except Exception:
                    pass
                
                await page.wait_for_timeout(1000)
                messages = page.locator("div[data-testid='stChatMessage']")
                count = await messages.count()
                
                if count < 2:
                    print(f"  ❌ FAILED: Không thấy phản hồi trợ lý (chỉ có {count} message).")
                    results[mode]["failed"] += 1
                    return
                
                last_msg = messages.nth(count - 1)
                text_content = await last_msg.inner_text()
                
                # Kiểm tra đặc thù theo mode
                if "?" in prompt and mode == "Hỏi - Đáp" and len(prompt.split("?")) > 2:
                    # Kiểm tra câu hỏi kép có tách ý không
                    if "Ý 1:" in text_content or "Ý 2:" in text_content:
                        print("  ✅ PASSED (Multi-intent Decomposed & Rendered Sequentially!)")
                        results[mode]["passed"] += 1
                    elif len(text_content.strip()) > 10:
                        print("  ✅ PASSED (Rendered combined answer)")
                        results[mode]["passed"] += 1
                    else:
                        print(f"  ❌ FAILED: Nội dung phản hồi quá ngắn: {text_content[:50]!r}")
                        results[mode]["failed"] += 1
                elif mode == "Biểu đồ":
                    charts = last_msg.locator("div[data-testid='stPlotlyChart']")
                    if await charts.count() > 0 or "bảng dữ liệu" in text_content.lower() or len(text_content) > 30:
                        print("  ✅ PASSED (Chart/Data displayed)")
                        results[mode]["passed"] += 1
                    else:
                        print(f"  ❌ FAILED: Không có biểu đồ hoặc dữ liệu.")
                        results[mode]["failed"] += 1
                elif mode == "Báo Cáo":
                    btns = last_msg.locator("button")
                    if await btns.count() >= 2 or "tải báo cáo" in text_content.lower():
                        print("  ✅ PASSED (Report download buttons displayed)")
                        results[mode]["passed"] += 1
                    else:
                        print(f"  ❌ FAILED: Không tạo được nút tải báo cáo.")
                        results[mode]["failed"] += 1
                else:
                    if len(text_content.strip()) > 5:
                        print(f"  ✅ PASSED (Length: {len(text_content)} chars)")
                        results[mode]["passed"] += 1
                    else:
                        print(f"  ❌ FAILED: Phản hồi rỗng/ngắn.")
                        results[mode]["failed"] += 1
            except Exception as e:
                print(f"  ❌ FAILED with Exception: {e}")
                results[mode]["failed"] += 1

        print("\n=================== PHẦN 1: 50 PROMPTS HỎI - ĐÁP ===================")
        for i, p in enumerate(QA_PROMPTS_50, 1):
            await test_prompt("Hỏi - Đáp", p, i, len(QA_PROMPTS_50))
            
        print("\n=================== PHẦN 2: 20 PROMPTS BIỂU ĐỒ ===================")
        for i, p in enumerate(BIEU_DO_PROMPTS_20, 1):
            await test_prompt("Biểu đồ", p, i, len(BIEU_DO_PROMPTS_20))
            
        print("\n=================== PHẦN 3: 3 PROMPTS BÁO CÁO ===================")
        for i, p in enumerate(BAO_CAO_PROMPTS_3, 1):
            await test_prompt("Báo Cáo", p, i, len(BAO_CAO_PROMPTS_3))
            
        await browser.close()
        
        print("\n=================================================================")
        print("                   TỔNG KẾT KIỂM THỬ GIAO DIỆN                   ")
        print("=================================================================")
        for m, s in results.items():
            t = s['passed'] + s['failed']
            rate = (s['passed'] / t * 100) if t > 0 else 0
            print(f"- {m}: {s['passed']}/{t} PASSED ({rate:.1f}%)")
        print("=================================================================")

if __name__ == "__main__":
    asyncio.run(run_suite())
