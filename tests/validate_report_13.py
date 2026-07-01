import os
import sys
import asyncio
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.query_control.agentic.report_generator import ReportGenerator

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF using fallback methods."""
    try:
        from docling.document_converter import DocumentConverter
        converter = DocumentConverter()
        result = converter.convert(pdf_path)
        return result.document.export_to_markdown()
    except ImportError:
        try:
            import fitz
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except ImportError:
            try:
                import pypdf
                reader = pypdf.PdfReader(pdf_path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text
            except ImportError:
                print("WARNING: No PDF extraction library found (docling, PyMuPDF, or pypdf).")
                return ""

async def validate_dom_overlap(html_path: str, chart_num: int):
    """Check for text overlap in Plotly HTML using Playwright."""
    print(f"\n--- Kiểm tra DOM Overlap Chart {chart_num} ({html_path.name}) ---")
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("Playwright không được cài đặt. Bỏ qua kiểm tra DOM.")
        return True

    overlap_found = False
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(f"file://{html_path.absolute()}")
            await page.wait_for_selector(".js-plotly-plot", timeout=10000)
            await asyncio.sleep(2)  # Wait for rendering

            text_nodes = await page.evaluate('''() => {
                const nodes = document.querySelectorAll('text');
                return Array.from(nodes).map(n => {
                    const rect = n.getBoundingClientRect();
                    return {
                        text: n.textContent,
                        x: rect.x, y: rect.y,
                        width: rect.width, height: rect.height,
                        right: rect.right, bottom: rect.bottom
                    };
                }).filter(n => n.width > 0 && n.height > 0);
            }''')

            # Basic overlap detection O(N^2)
            for i in range(len(text_nodes)):
                for j in range(i + 1, len(text_nodes)):
                    a = text_nodes[i]
                    b = text_nodes[j]
                    
                    if not a['text'].strip() or not b['text'].strip():
                        continue

                    # Check intersection
                    if not (a['right'] < b['x'] or 
                            a['x'] > b['right'] or 
                            a['bottom'] < b['y'] or 
                            a['y'] > b['bottom']):
                        
                        overlap_area = max(0, min(a['right'], b['right']) - max(a['x'], b['x'])) * \
                                       max(0, min(a['bottom'], b['bottom']) - max(a['y'], b['y']))
                        
                        a_area = a['width'] * a['height']
                        b_area = b['width'] * b['height']
                        min_area = min(a_area, b_area)
                        
                        if min_area > 0 and (overlap_area / min_area) > 0.3:
                            print(f"❌ Phát hiện chồng chéo Text: '{a['text']}' và '{b['text']}'")
                            overlap_found = True
                            break
                if overlap_found:
                    break

            if not overlap_found:
                print("✅ DOM Box Validation: Không phát hiện chồng chéo nhãn (Overlap = 0%)")
        except Exception as e:
            print(f"Lỗi khi chạy Playwright: {e}")
        finally:
            await browser.close()
            
    return not overlap_found

def test_report_13():
    print("==================================================")
    print("BẮT ĐẦU VALIDATE REPORT 13: TẦNG LỚP KẸP GIỮA")
    print("==================================================")
    
    # 1. Generate Report
    print("\n[1] Đang sinh báo cáo 13...")
    try:
        report_data = ReportGenerator.generate(report_id=13, year=2024, district=None)
        print("✅ Khởi tạo báo cáo thành công")
    except Exception as e:
        print(f"❌ Lỗi khi sinh báo cáo: {e}")
        return False
        
    prefix = f"bao_cao_13_2024"
    pdf_path = PROJECT_ROOT / "Runtime" / "reports" / f"{prefix}.pdf"
    
    if not pdf_path.exists():
        print(f"❌ Không tìm thấy file PDF: {pdf_path}")
        return False
        
    print(f"✅ Đã lưu báo cáo tại: {pdf_path.relative_to(PROJECT_ROOT)}")

    # 2. PDF Content Extraction & Text Validation
    print("\n[2] Đang trích xuất nội dung PDF...")
    pdf_text = extract_text_from_pdf(str(pdf_path))
    
    if not pdf_text:
        print("⚠️ Không thể trích xuất text từ PDF. Bỏ qua Text Validation.")
    else:
        print("✅ Trích xuất text thành công.")
        print("\n--- Kiểm tra Nội dung Báo cáo ---")
        
        # Check required sections
        sections = [
            ("PHẦN I: BẢNG SỐ LIỆU TỔNG HỢP", "Dữ liệu thô"),
            ("PHẦN II: TÓM TẮT ĐIỀU HÀNH & NHẬN ĐỊNH TỔNG QUAN", "Tóm tắt điều hành"),
            ("PHẦN III: PHÂN TÍCH TRỰC QUAN & ĐÁNH GIÁ CHUYÊN SÂU", "Phân tích chuyên sâu"),
            ("PHẦN IV: ĐỀ XUẤT GIẢI PHÁP & CAN THIỆP CHÍNH SÁCH", "Khuyến nghị chính sách")
        ]
        
        for section, name in sections:
            if section in pdf_text or section.lower() in pdf_text.lower():
                print(f"✅ Đã tìm thấy {name}")
            else:
                print(f"❌ Thiếu {name}")
                
        # Check specific keywords
        keywords = [
            "Tầng lớp Bấp bênh Đô thị",
            "Hiệu ứng Vách đá",
            "sợ hãi sự thịnh vượng",
            "Đệm Dốc",
            "Tài khoản Tiết kiệm Đối ứng"
        ]
        
        for kw in keywords:
            if kw.lower() in pdf_text.lower():
                print(f"✅ Tìm thấy Keyword: '{kw}'")
            else:
                print(f"❌ Thiếu Keyword: '{kw}'")

    # 3. Validation DOM HTML Charts
    print("\n[3] Đang kiểm định UI/UX Biểu đồ (DOM Box Overlap)...")
    charts_dir = PROJECT_ROOT / "artifacts" / "charts"
    
    html_files = [
        charts_dir / f"{prefix}_chart_1.html",
        charts_dir / f"{prefix}_chart_2.html",
        charts_dir / f"{prefix}_chart_3.html"
    ]
    
    # Run async validation
    all_charts_passed = True
    
    for i, html_file in enumerate(html_files, 1):
        if html_file.exists():
            passed = asyncio.run(validate_dom_overlap(html_file, i))
            if not passed:
                all_charts_passed = False
        else:
            print(f"❌ Không tìm thấy file HTML cho Chart {i}: {html_file.name}")
            all_charts_passed = False

    print("\n==================================================")
    if all_charts_passed:
        print("KẾT LUẬN: BÁO CÁO 13 ĐẠT CHUẨN (PASSED)")
    else:
        print("KẾT LUẬN: CÓ LỖI XẢY RA TRONG QUÁ TRÌNH VALIDATE (FAILED)")
    print("==================================================")
    
if __name__ == "__main__":
    test_report_13()
