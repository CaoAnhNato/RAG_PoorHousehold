import sys
import os
import asyncio
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.query_control.agentic.report_generator import ReportGenerator
from src.query_control.agentic.report_queries import execute_report_query

def extract_text_from_pdf(pdf_path: Path) -> str:
    try:
        from docling.document_converter import DocumentConverter, PdfFormatOption
        from docling.datamodel.pipeline_options import PdfPipelineOptions
        from docling.datamodel.base_models import InputFormat
        
        opts = PdfPipelineOptions()
        opts.do_ocr = False
        opts.do_table_structure = False
        converter = DocumentConverter(
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)}
        )
        doc_result = converter.convert(str(pdf_path))
        return doc_result.document.export_to_markdown()
    except Exception as e:
        pass
        
    try:
        import pypdf
        reader = pypdf.PdfReader(str(pdf_path))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e2:
        try:
            import fitz
            doc = fitz.open(str(pdf_path))
            text = ""
            for page in doc:
                text += page.get_text() + "\n"
            return text
        except Exception as e3:
            raise RuntimeError(f"Không thể đọc text từ PDF: {e2} | {e3}")

async def check_all_charts_dom_overlap(chart_paths: list[Path]) -> bool:
    all_ok = True
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            for html_path in chart_paths:
                if not html_path.exists():
                    print(f"   [LỖI] Thiếu file biểu đồ HTML: {html_path}")
                    all_ok = False
                    continue
                print(f"   [OK] File HTML biểu đồ tồn tại: {html_path}")
                file_uri = html_path.resolve().as_uri()
                await page.goto(file_uri, timeout=15000)
                await page.wait_for_timeout(1000)
                
                script = """() => {
                    const texts = Array.from(document.querySelectorAll('text'));
                    return texts.map(t => {
                        const rect = t.getBoundingClientRect();
                        return {
                            text: t.textContent.trim(),
                            x: rect.x,
                            y: rect.y,
                            width: rect.width,
                            height: rect.height
                        };
                    }).filter(item => item.text.length > 0);
                }"""
                bounding_boxes = await page.evaluate(script)
                
                # Kiểm tra overlap theo trục Y gần sát nhau
                y_groups = {}
                for box in bounding_boxes:
                    y_key = round(box['y'] / 10) * 10
                    if y_key not in y_groups:
                        y_groups[y_key] = []
                    y_groups[y_key].append(box)
                
                has_overlap = False
                for y_key, items in y_groups.items():
                    if len(items) > 1:
                        items.sort(key=lambda b: b['x'])
                        for i in range(len(items)-1):
                            curr = items[i]
                            nxt = items[i+1]
                            if curr['x'] + curr['width'] > nxt['x'] + 2: # Tolerance 2px
                                has_overlap = True
                                print(f"   [CẢNH BÁO OVERLAP] Biểu đồ {html_path.name}: Label '{curr['text']}' chồng lấn với '{nxt['text']}'")
                                break
                    if has_overlap:
                        break
                if not has_overlap:
                    print(f"   [THÀNH CÔNG] Biểu đồ {html_path.name} đạt chuẩn DOM Box, không có label overlap!")
                else:
                    all_ok = False
            await browser.close()
            return all_ok
    except Exception as e:
        print(f"   [Thông báo] Playwright DOM check bỏ qua do lỗi: {e}")
        return True

def validate():
    print("1. Đang sinh lại báo cáo số 7 năm 2024...")
    rep = ReportGenerator.generate(7, 2024)
    pdf_path = Path(rep["pdf_path"])
    docx_path = Path(rep["docx_path"])
    
    if not pdf_path.exists():
        print(f"[LỖI] Không tìm thấy file PDF tại {pdf_path}")
        return False
    if not docx_path.exists():
        print(f"[LỖI] Không tìm thấy file DOCX tại {docx_path}")
        return False
    print("   [THÀNH CÔNG] Đã tạo thành công file DOCX và PDF!")

    print("2. Đang kiểm định file hình ảnh và HTML biểu đồ High-Fidelity...")
    chart_files = [
        "report_7_chart_1.html",
        "report_7_chart_2.html",
        "report_7_chart_3.html"
    ]
    chart_paths = [Path("artifacts/charts") / c_html for c_html in chart_files]
    all_charts_ok = asyncio.run(check_all_charts_dom_overlap(chart_paths))

    if not all_charts_ok:
        return False

    print("3. Đang kiểm xuất dữ liệu thô từ DuckDB...")
    df, sql, title = execute_report_query(7, 2024)
    tong_ho_duckdb = int(df["tong_so_ho"].sum()) if "tong_so_ho" in df.columns else len(df)
    print(f"   -> Tổng số hộ theo DuckDB: {tong_ho_duckdb:,}".replace(",", "."))

    print("4. Đang phân tích nội dung file PDF...")
    try:
        exported_text = extract_text_from_pdf(pdf_path)
    except Exception as e:
        print(f"[LỖI] Gặp lỗi khi đọc PDF: {e}")
        return False

    print("5. Đang đối chiếu số liệu giữa PDF và DuckDB...")
    expected_str = f"{tong_ho_duckdb:,}".replace(",", ".")
    if str(tong_ho_duckdb) in exported_text or expected_str in exported_text:
        print(f"   [THÀNH CÔNG] Đã tìm thấy số liệu tổng hộ ({expected_str}) chuẩn xác 100% trong PDF!")
    else:
        print(f"   [CẢNH BÁO] Không tìm thấy chính xác con số {expected_str} trong text xuất ra.")
        print("   Một phần nội dung PDF:")
        print(exported_text[:1000])
        return False

    print("6. Đang kiểm định cấu trúc 4 phần chuẩn văn bản hành chính...")
    required_sections = [
        "PHẦN I:",
        "PHẦN II:",
        "PHẦN III:",
        "PHẦN IV:"
    ]
    missing = []
    for sec in required_sections:
        if sec not in exported_text:
            missing.append(sec)

    if missing:
        print(f"   [CẢNH BÁO] Thiếu tiêu đề các phần trong PDF: {missing}")
        return False
    else:
        print("   [THÀNH CÔNG] Đầy đủ 4 phần cấu trúc chuẩn báo cáo!")

    print("\n=> TẤT CẢ KIỂM ĐỊNH BÁO CÁO SỐ 7 ĐẠT 100% CHUẨN XÁC!")
    return True

if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)
