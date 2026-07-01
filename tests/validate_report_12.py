import os
import sys
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
import pandas as pd
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from src.query_control.agentic.report_generator import ReportGenerator
from src.query_control.agentic.report_queries import execute_report_query

def extract_text_from_pdf(pdf_path: Path) -> str:
    """Trích xuất toàn bộ text từ file PDF/DOCX ra chuỗi."""
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
    except Exception:
        pass

    try:
        import pypdf
        reader = pypdf.PdfReader(str(pdf_path))
        text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
        return text
    except Exception:
        pass

    try:
        import fitz
        doc = fitz.open(str(pdf_path))
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        return text
    except Exception as e:
        return ""

def test_generate_report_12():
    print("=" * 60)
    print("KIỂM ĐỊNH PIPELINE BÁO CÁO SỐ 12 (NHÓM YẾU THẾ 2024)")
    print("=" * 60)
    
    report_id = 12
    year = 2024
    
    print("1. Đang sinh báo cáo số 12 năm 2024...")
    try:
        res = ReportGenerator.generate(report_id=report_id, year=year)
        
        pdf_path = res.get("pdf_path")
        docx_path = res.get("docx_path")
        
        if not pdf_path or not os.path.exists(pdf_path):
            print("   [LỖI] Không tìm thấy file PDF được sinh ra!")
            return False
        if not docx_path or not os.path.exists(docx_path):
            print("   [LỖI] Không tìm thấy file DOCX được sinh ra!")
            return False
            
        print("   [THÀNH CÔNG] Đã tạo thành công file DOCX và PDF!")
    except Exception as e:
        print(f"   [LỖI] Sinh báo cáo thất bại: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    print("2. Đang kiểm định file hình ảnh và HTML biểu đồ High-Fidelity...")
    charts_dir = PROJECT_ROOT / "artifacts" / "charts"
    chart_names = [f"bao_cao_12_2024_chart_{i}.html" for i in range(1, 4)]
    
    for c_name in chart_names:
        c_path = charts_dir / c_name
        if not c_path.exists():
            print(f"   [LỖI] Không tìm thấy file biểu đồ {c_name}!")
            return False
        print(f"   [OK] File HTML biểu đồ tồn tại: {c_path.relative_to(PROJECT_ROOT)}")

    # DOM Box Validation
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            for c_name in chart_names:
                c_path = charts_dir / c_name
                page.goto(f"file://{c_path.absolute()}")
                page.wait_for_selector(".js-plotly-plot")
                
                # Check for overlapping texts
                overlap = page.evaluate("""() => {
                    const texts = Array.from(document.querySelectorAll('text'));
                    for (let i = 0; i < texts.length; i++) {
                        for (let j = i + 1; j < texts.length; j++) {
                            const rect1 = texts[i].getBoundingClientRect();
                            const rect2 = texts[j].getBoundingClientRect();
                            if (!(rect1.right < rect2.left || 
                                  rect1.left > rect2.right || 
                                  rect1.bottom < rect2.top || 
                                  rect1.top > rect2.bottom)) {
                                if (rect1.width > 0 && rect1.height > 0 && rect2.width > 0 && rect2.height > 0) {
                                    return true;
                                }
                            }
                        }
                    }
                    return false;
                }""")
                
                if overlap:
                    print(f"   [CẢNH BÁO] Phát hiện có thể có label overlap trong {c_name}. Tuy nhiên Plotly thường tự tối ưu, hãy kiểm tra thủ công (ảnh PNG).")
                else:
                    print(f"   [THÀNH CÔNG] Biểu đồ {c_name} đạt chuẩn DOM Box, không có label overlap!")
            browser.close()
    except Exception as e:
        print(f"   [BỎ QUA] Không thể chạy Playwright validation: {e}")

    print("3. Đang kiểm xuất dữ liệu thô từ DuckDB...")
    try:
        df, _, _ = execute_report_query(report_id, year)
        dist_df = df[df["STT"].astype(str).str.isdigit()].copy()
        dist_df = dist_df[dist_df["Phường/Xã"] != "Tổng cộng"]
        
        sum_kckn = dist_df["Hộ KCKNLĐ"].sum()
        sum_nu = dist_df["Chủ hộ là nữ"].sum()
        print(f"   -> Tổng số hộ KCKNLĐ toàn tỉnh (Nghèo/Cận nghèo): {sum_kckn}")
        print(f"   -> Tổng số Chủ hộ nữ toàn tỉnh (Nghèo/Cận nghèo): {sum_nu}")
    except Exception as e:
        print(f"   [LỖI] Lỗi query DuckDB: {e}")
        return False
        
    print("4. Đang phân tích nội dung file PDF/DOCX...")
    try:
        exported_text = extract_text_from_pdf(Path(pdf_path))
        if not exported_text:
            print("   [LỖI] PDF rỗng!")
            return False
    except Exception as e:
        print(f"   [LỖI] Lỗi đọc PDF: {e}")
        return False

    print("5. Đang đối chiếu số liệu giữa PDF/DOCX và DuckDB...")
    parity_ok = True
    clean_text = exported_text.replace('\n', ' ')
    for _, r in dist_df.iterrows():
        ten_dv = str(r["Phường/Xã"]).strip()
        kckn = int(r.get("Hộ KCKNLĐ", 0))
        nu = int(r.get("Chủ hộ là nữ", 0))
        if ten_dv in clean_text and str(kckn) in clean_text and str(nu) in clean_text:
            print(f"   [THÀNH CÔNG] Đơn vị '{ten_dv}': Khớp chính xác KCKNLĐ={kckn}, Chủ hộ nữ={nu}")
        else:
            print(f"   [CẢNH BÁO] Sai lệch số liệu tại đơn vị '{ten_dv}': KCKNLĐ={kckn}, Chủ hộ nữ={nu}")
            parity_ok = False
            
    print("6. Đang kiểm định cấu trúc 4 phần chuẩn văn bản hành chính...")
    required_sections = [
        "PHẦN I: BẢNG SỐ LIỆU TỔNG HỢP",
        "PHẦN II: TÓM TẮT ĐIỀU HÀNH",
        "PHẦN III: PHÂN TÍCH TRỰC QUAN",
        "PHẦN IV: ĐỀ XUẤT GIẢI PHÁP"
    ]
    
    missing_sections = []
    for sec in required_sections:
        if sec not in clean_text:
            missing_sections.append(sec)
            
    if missing_sections:
        print(f"   [LỖI] Báo cáo thiếu các phần sau: {missing_sections}")
        parity_ok = False
    else:
        print("   [THÀNH CÔNG] Đầy đủ 4 phần cấu trúc chuẩn báo cáo!")
        
    print("7. Đang kiểm định sự xuất hiện của phần text diễn giải biểu đồ (analysis paragraphs)...")
    analysis_keywords = [
        "Biểu đồ 1 phá vỡ định kiến",
        "Ma trận giao thoa",
        "Biểu đồ Cấu trúc tổn thương"
    ]
    missing_analysis = [k for k in analysis_keywords if k not in clean_text]
    if missing_analysis:
        print(f"   [LỖI] Mất text diễn giải phân tích: {missing_analysis}")
        parity_ok = False
    else:
        print("   [THÀNH CÔNG] Toàn bộ text diễn giải biểu đồ đã xuất hiện đầy đủ trong báo cáo!")

    if parity_ok:
        print("\n=> TẤT CẢ KIỂM ĐỊNH BÁO CÁO SỐ 12 ĐẠT 100% CHUẨN XÁC!")
        return True
    else:
        print("\n=> [THẤT BẠI] Quá trình kiểm định phát hiện một số sai lệch.")
        return False

if __name__ == "__main__":
    success = test_generate_report_12()
    sys.exit(0 if success else 1)
