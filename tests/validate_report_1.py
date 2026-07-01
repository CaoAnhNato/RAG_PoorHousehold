import sys
import os
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
    # Thử dùng Docling trước
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
        print(f"   [Thông báo] Docling ML backend gặp lỗi import ({e}), đang chuyển sang bộ tra cứu PDF chuẩn (pypdf/fitz)...")
        
    # Fallback pypdf / fitz
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

def validate():
    print("1. Đang sinh lại báo cáo số 1 năm 2024...")
    rep = ReportGenerator.generate(1, 2024)
    pdf_path = Path(rep["pdf_path"])
    if not pdf_path.exists():
        print(f"[LỖI] Không tìm thấy file PDF tại {pdf_path}")
        return False

    print(f"2. Đang kiểm xuất dữ liệu thô từ DuckDB...")
    df, sql, title = execute_report_query(1, 2024)
    tong_ho_duckdb = int(df["tong_so_ho"].sum()) if "tong_so_ho" in df.columns else len(df)
    print(f"   -> Tổng số hộ theo DuckDB: {tong_ho_duckdb:,}".replace(",", "."))

    print("3. Đang phân tích nội dung file PDF...")
    try:
        exported_text = extract_text_from_pdf(pdf_path)
    except Exception as e:
        print(f"[LỖI] Gặp lỗi khi đọc PDF: {e}")
        return False

    print("4. Đang đối chiếu số liệu giữa PDF và DuckDB...")
    expected_str = f"{tong_ho_duckdb:,}".replace(",", ".")
    if str(tong_ho_duckdb) in exported_text or expected_str in exported_text:
        print(f"   [THÀNH CÔNG] Đã tìm thấy số liệu tổng hộ ({expected_str}) chuẩn xác 100% trong PDF!")
    else:
        print(f"   [CẢNH BÁO] Không tìm thấy chính xác con số {expected_str} trong text xuất ra.")
        print("   Một phần nội dung PDF:")
        print(exported_text[:1000])
        return False

    required_sections = [
        "PHẦN 1: DỮ LIỆU THÔ",
        "PHẦN 2: TÓM TẮT ĐIỀU HÀNH",
        "PHẦN 3: PHÂN TÍCH TRỰC QUAN",
        "PHẦN 4: GỢI Ý CAN THIỆP CHÍNH SÁCH"
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

    print("\n=> TẤT CẢ KIỂM ĐỊNH ĐẠT 100% CHUẨN XÁC!")
    return True

if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)
