# -*- coding: utf-8 -*-
from __future__ import annotations
import os
import sys
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
venv_site_packages = PROJECT_ROOT / "venv" / "Lib" / "site-packages"
if venv_site_packages.exists() and str(venv_site_packages) not in sys.path:
    sys.path.append(str(venv_site_packages))

import pandas as pd
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from fpdf import FPDF
from fpdf.fonts import FontFace

PROJECT_ROOT = Path(__file__).resolve().parents[3]
FONTS_DIR = PROJECT_ROOT / "data" / "fonts"
FONTS_DIR.mkdir(parents=True, exist_ok=True)
FONT_PATH = FONTS_DIR / "times.ttf"
FONT_BOLD_PATH = FONTS_DIR / "timesbd.ttf"
FONT_ITALIC_PATH = FONTS_DIR / "timesi.ttf"
FONT_BOLD_ITALIC_PATH = FONTS_DIR / "timesbi.ttf"

# Tự động sao chép các font chữ Bold/Italic chuẩn từ Windows Fonts vào data/fonts
win_fonts_dir = Path(r"C:\Windows\Fonts")
for fname, ftarget in [("times.ttf", FONT_PATH), ("timesbd.ttf", FONT_BOLD_PATH), ("timesi.ttf", FONT_ITALIC_PATH), ("timesbi.ttf", FONT_BOLD_ITALIC_PATH)]:
    src = win_fonts_dir / fname
    if src.exists() and not ftarget.exists():
        try:
            shutil.copy(src, ftarget)
        except Exception:
            pass

REPORTS_DIR = PROJECT_ROOT / "Runtime" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

class ReportGenerator:
    """Engine xuất báo cáo chuyên nghiệp ra Word (.docx) và PDF chuẩn Chính phủ."""
    
    @staticmethod
    def format_value(val) -> str:
        """Định dạng giá trị hiển thị."""
        if pd.isna(val):
            return ""
        if isinstance(val, float):
            if val.is_integer():
                return f"{int(val):,}"
            return f"{val:,.2f}"
        if isinstance(val, int):
            return f"{val:,}"
        return str(val)

    @staticmethod
    def generate_docx(df: pd.DataFrame, title: str, save_path: Path) -> Path:
        """
        Tạo báo cáo định dạng Word (.docx) chuẩn văn bản Chính phủ với Multi-tier Header,
        tự động auto-fit tỷ lệ cột, bôi đậm dòng Huyện và in nghiêng dòng công thức.
        """
        display_cols = [c for c in df.columns if c != "is_commune_header"]
        num_cols = len(display_cols)
        doc = Document()
        
        # 1. Căn lề và hướng trang (Landscape, Margin 0.5 inches)
        # Đảm bảo khổ giấy A3 Landscape (16.54 x 11.69 inches) cho báo cáo nhiều cột, A4 Landscape (11.69 x 8.27 inches) cho báo cáo <= 12 cột
        section = doc.sections[0]
        section.orientation = docx.enum.section.WD_ORIENT.LANDSCAPE
        if num_cols > 12:
            section.page_width = Inches(16.54)
            section.page_height = Inches(11.69)
        else:
            section.page_width = Inches(11.69)
            section.page_height = Inches(8.27)
            
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)
        section.left_margin = Inches(0.5)
        section.right_margin = Inches(0.5)
        
        if doc.paragraphs:
            doc.paragraphs[0].text = ""
        
        # Thêm Phụ lục cho BC 14, 15
        if num_cols == 19:
            p_phu_luc = doc.add_paragraph()
            p_phu_luc.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            r_pl = p_phu_luc.add_run("Phụ lục số 2.3")
            r_pl.bold = True
            r_pl.italic = True
            r_pl.font.name = 'Times New Roman'
            r_pl.font.size = Pt(12)

        # 2. Khối Tiêu đề Hành chính (UBND / CỘNG HOÀ XÃ HỘI CHỦ NGHĨA VIỆT NAM)
        hdr_table = doc.add_table(rows=1, cols=2)
        hdr_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        hdr_table.autofit = True
        
        p_left = hdr_table.rows[0].cells[0].paragraphs[0]
        p_left.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_ubnd = p_left.add_run("ỦY BAN NHÂN DÂN\n")
        r_ubnd.bold = True
        r_ubnd.font.name = 'Times New Roman'
        r_ubnd.font.size = Pt(12)
        r_dist = p_left.add_run("TỈNH / THÀNH PHỐ")
        r_dist.bold = True
        r_dist.font.name = 'Times New Roman'
        r_dist.font.size = Pt(12)

        p_right = hdr_table.rows[0].cells[1].paragraphs[0]
        p_right.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_quoc = p_right.add_run("CỘNG HOÀ XÃ HỘI CHỦ NGHĨA VIỆT NAM\n")
        r_quoc.bold = True
        r_quoc.font.name = 'Times New Roman'
        r_quoc.font.size = Pt(12)
        r_tieu = p_right.add_run("Độc lập - Tự do - Hạnh phúc")
        r_tieu.bold = True
        r_tieu.font.name = 'Times New Roman'
        r_tieu.font.size = Pt(12)
        
        doc.add_paragraph() # Khoảng trống
        
        # 3. Tiêu đề chính (Bold, 15pt, Căn giữa)
        p_title = doc.add_paragraph()
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_title = p_title.add_run(title.upper())
        run_title.bold = True
        run_title.font.name = 'Times New Roman'
        run_title.font.size = Pt(15)
        run_title.font.color.rgb = RGBColor(0, 0, 0)
        
        p_sub = doc.add_paragraph()
        p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_sub = p_sub.add_run("Kèm theo báo cáo kết quả rà soát định kỳ")
        run_sub.italic = True
        run_sub.font.name = 'Times New Roman'
        run_sub.font.size = Pt(12)
        
        doc.add_paragraph() # Khoảng trống trước bảng
        
        # 4. Kẻ bảng dữ liệu với Multi-tier Header & Explicit Widths
        is_report_1 = num_cols == 16 and "Nhân khẩu" in df.columns
        is_report_2_3 = num_cols == 12 and "Phân tổ" in df.columns
        is_report_4_6 = num_cols == 16 and "Tổng số thiếu hụt" in df.columns
        is_report_5_7 = num_cols == 15 and ("Tổng số hộ nghèo" in df.columns or "Tổng số hộ cận nghèo" in df.columns)
        is_report_8 = num_cols == 13 and "Phân tổ" in df.columns
        is_report_9 = num_cols == 28
        is_report_10 = num_cols == 10 and "1. Thiếu đất sản xuất" in df.columns
        is_report_11 = num_cols == 10 and "1. Tổng số trẻ em hộ nghèo" in df.columns
        is_report_12_13 = num_cols == 24
        is_report_14_15 = num_cols == 19

        if is_report_1 or is_report_2_3 or is_report_4_6 or is_report_5_7 or is_report_8 or is_report_9 or is_report_11 or is_report_12_13 or is_report_14_15:
            table = doc.add_table(rows=3, cols=num_cols)
            num_hdr_rows = 3
        elif is_report_10:
            table = doc.add_table(rows=2, cols=num_cols)
            num_hdr_rows = 2
        else:
            table = doc.add_table(rows=1, cols=num_cols)
            num_hdr_rows = 1
            
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        table.allow_autofit = False
        
        # Thiết lập đường viền bảng (Borders) và khóa tblLayout w:val="fixed"
        tblPr = table._tbl.tblPr
        tblLayout = parse_xml(r'<w:tblLayout %s w:val="fixed"/>' % nsdecls('w'))
        tblPr.append(tblLayout)
        tblBorders = parse_xml(r'<w:tblBorders %s><w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/><w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/><w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/><w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/><w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/></w:tblBorders>' % nsdecls('w'))
        tblPr.append(tblBorders)
        
        # Thiết lập chiều rộng cụ thể cho từng cột theo tỷ lệ chuẩn Excel gốc
        if is_report_1 or is_report_4_6:
            col_widths = [Inches(0.4), Inches(2.2)] + [Inches(0.68)] * 14
        elif is_report_2_3:
            col_widths = [Inches(0.4), Inches(2.2), Inches(0.8)] + [Inches(0.95)] * 9
        elif is_report_5_7:
            col_widths = [Inches(0.4), Inches(2.2)] + [Inches(0.72)] * 13
        elif is_report_8:
            col_widths = [Inches(0.4), Inches(2.0), Inches(0.8)] + [Inches(0.9)] * 10
        elif is_report_9:
            col_widths = [Inches(0.4), Inches(1.8)] + [Inches(0.5)] * 26
        elif is_report_10:
            col_widths = [Inches(0.4), Inches(2.2)] + [Inches(1.0)] * 8
        elif is_report_11:
            col_widths = [Inches(0.4), Inches(2.2)] + [Inches(0.9)] * 8
        elif is_report_12_13:
            col_widths = [Inches(0.3), Inches(1.5)] + [Inches(0.6)] * 22
        elif is_report_14_15:
            col_widths = [Inches(0.3), Inches(0.3), Inches(2.0), Inches(0.4), Inches(0.4), Inches(0.6), Inches(0.8)] + [Inches(0.5)] * 12
        else:
            col_widths = [Inches(0.8)] * num_cols

        # Thiết lập Tiêu đề Bảng
        if is_report_1:
            table.rows[0].cells[0].text = "STT"
            table.rows[0].cells[1].text = "Phường/Xã"
            table.rows[0].cells[2].text = "Tổng số hộ dân cư"
            table.rows[0].cells[4].text = "Kết quả rà soát về hộ (chính thức)"
            table.rows[0].cells[10].text = "Kết quả rà soát về khẩu (chính thức)"
            table.rows[0].cells[2].merge(table.rows[0].cells[3])
            table.rows[0].cells[4].merge(table.rows[0].cells[9])
            table.rows[0].cells[10].merge(table.rows[0].cells[15])
            
            for i, col_name in enumerate(df.columns):
                table.rows[1].cells[i].text = col_name
            table.rows[0].cells[0].merge(table.rows[1].cells[0])
            table.rows[0].cells[1].merge(table.rows[1].cells[1])
            
            sub_headers = ["A", "B", "1", "2", "3", "4=3/1*100", "5", "6=5/1*100", "7", "8=7/1*100", "9", "10=9/2*100", "11", "12=11/2*100", "13", "14=13/2*100"]
            for i, text in enumerate(sub_headers):
                table.rows[2].cells[i].text = text

        elif is_report_2_3:
            table.rows[0].cells[0].text = "STT"
            table.rows[0].cells[1].text = "Phường/Xã"
            table.rows[0].cells[2].text = "Phân tổ"
            table.rows[0].cells[3].text = "Tổng số hộ nghèo đầu kỳ" if "Tổng số hộ nghèo đầu kỳ" in df.columns else "Tổng số hộ cận nghèo đầu kỳ"
            table.rows[0].cells[4].text = "Số hộ thoát nghèo" if "Tổng số hộ nghèo đầu kỳ" in df.columns else "Số hộ thoát cận nghèo"
            table.rows[0].cells[6].text = "Số hộ khác giảm"
            table.rows[0].cells[7].text = "Số hộ cận nghèo trở thành" if "Tổng số hộ nghèo đầu kỳ" in df.columns else "Số hộ nghèo trở thành hộ cận nghèo"
            table.rows[0].cells[8].text = "Số hộ nghèo bổ sung" if "Tổng số hộ nghèo đầu kỳ" in df.columns else "Số hộ cận nghèo bổ sung"
            table.rows[0].cells[10].text = "Số hộ khác tăng"
            table.rows[0].cells[11].text = "Tổng số hộ nghèo cuối kỳ" if "Tổng số hộ nghèo đầu kỳ" in df.columns else "Tổng số hộ cận nghèo cuối kỳ"
            table.rows[0].cells[4].merge(table.rows[0].cells[5])
            table.rows[0].cells[8].merge(table.rows[0].cells[9])
            
            for i, col_name in enumerate(df.columns):
                table.rows[1].cells[i].text = col_name
            table.rows[0].cells[0].merge(table.rows[1].cells[0])
            table.rows[0].cells[1].merge(table.rows[1].cells[1])
            table.rows[0].cells[2].merge(table.rows[1].cells[2])
            table.rows[0].cells[3].merge(table.rows[1].cells[3])
            table.rows[0].cells[6].merge(table.rows[1].cells[6])
            table.rows[0].cells[7].merge(table.rows[1].cells[7])
            table.rows[0].cells[10].merge(table.rows[1].cells[10])
            table.rows[0].cells[11].merge(table.rows[1].cells[11])
            
            sub_headers = ["A", "B", "C", "1", "2", "3", "4", "5", "6", "7", "8", "9=1-2-3-4+5+6+7+8"]
            for i, text in enumerate(sub_headers):
                table.rows[2].cells[i].text = text

        elif is_report_4_6:
            col_total = "Tổng số hộ nghèo" if "Tổng số hộ nghèo" in df.columns else "Tổng số hộ cận nghèo"
            table.rows[0].cells[0].text = "STT"
            table.rows[0].cells[1].text = "Phường/Xã"
            table.rows[0].cells[2].text = col_total
            table.rows[0].cells[3].text = "Tổng số thiếu hụt"
            table.rows[0].cells[4].text = "Các chỉ số thiếu hụt dịch vụ xã hội cơ bản"
            table.rows[0].cells[4].merge(table.rows[0].cells[15])
            
            for i, col_name in enumerate(df.columns):
                table.rows[1].cells[i].text = col_name
            table.rows[0].cells[0].merge(table.rows[1].cells[0])
            table.rows[0].cells[1].merge(table.rows[1].cells[1])
            table.rows[0].cells[2].merge(table.rows[1].cells[2])
            table.rows[0].cells[3].merge(table.rows[1].cells[3])
            
            sub_headers = ["A", "B", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14"]
            for i, text in enumerate(sub_headers):
                table.rows[2].cells[i].text = text

        elif is_report_5_7:
            col_total = "Tổng số hộ nghèo" if "Tổng số hộ nghèo" in df.columns else "Tổng số hộ cận nghèo"
            table.rows[0].cells[0].text = "STT"
            table.rows[0].cells[1].text = "Phường/Xã"
            table.rows[0].cells[2].text = col_total
            table.rows[0].cells[3].text = "Tỷ lệ các chỉ số thiếu hụt dịch vụ xã hội cơ bản (%)"
            table.rows[0].cells[3].merge(table.rows[0].cells[14])
            
            for i, col_name in enumerate(df.columns):
                table.rows[1].cells[i].text = col_name
            table.rows[0].cells[0].merge(table.rows[1].cells[0])
            table.rows[0].cells[1].merge(table.rows[1].cells[1])
            table.rows[0].cells[2].merge(table.rows[1].cells[2])
            
            sub_headers = ["A", "B", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13"]
            for i, text in enumerate(sub_headers):
                table.rows[2].cells[i].text = text

        elif is_report_8:
            table.rows[0].cells[0].text = "STT"
            table.rows[0].cells[1].text = "Phường/Xã"
            table.rows[0].cells[2].text = "Phân tổ"
            table.rows[0].cells[3].text = "Hộ nghèo"
            table.rows[0].cells[8].text = "Hộ cận nghèo"
            table.rows[0].cells[3].merge(table.rows[0].cells[7])
            table.rows[0].cells[8].merge(table.rows[0].cells[12])
            
            sub_cols = ["STT", "Phường/Xã", "Phân tổ", "Tổng số", "Hộ DTTS", "Hộ không có khả năng lao động", "Hộ có người có công", "Khác", "Tổng số", "Hộ DTTS", "Hộ không có khả năng lao động", "Hộ có người có công", "Khác"]
            for i, text in enumerate(sub_cols):
                table.rows[1].cells[i].text = text
            table.rows[0].cells[0].merge(table.rows[1].cells[0])
            table.rows[0].cells[1].merge(table.rows[1].cells[1])
            table.rows[0].cells[2].merge(table.rows[1].cells[2])
            
            sub_headers = ["A", "B", "C", "1", "2", "3", "4", "5=1-2-3-4", "6", "7", "8", "9", "10=6-7-8-9"]
            for i, text in enumerate(sub_headers):
                table.rows[2].cells[i].text = text

        elif is_report_9:
            table.rows[0].cells[0].text = "STT"
            table.rows[0].cells[1].text = "Phường/Xã"
            table.rows[0].cells[2].text = "Hộ nghèo"
            table.rows[0].cells[15].text = "Hộ cận nghèo"
            table.rows[0].cells[2].merge(table.rows[0].cells[14])
            table.rows[0].cells[15].merge(table.rows[0].cells[27])
            
            sub_cols = ["STT", "Phường/Xã", "Tổng số", "Kinh", "Tổng DTTS", "Ê đê", "Mạ", "Mường", "Thái", "M'Nông", "Tày", "Nùng", "Mông", "Dao", "Khác", "Tổng số", "Kinh", "Tổng DTTS", "Ê đê", "Mạ", "Mường", "Thái", "M'Nông", "Tày", "Nùng", "Mông", "Dao", "Khác"]
            for i, text in enumerate(sub_cols):
                table.rows[1].cells[i].text = text
            table.rows[0].cells[0].merge(table.rows[1].cells[0])
            table.rows[0].cells[1].merge(table.rows[1].cells[1])
            
            sub_headers = ["A", "B", "1.0", "1.1", "1.2", "1.2.1", "1.2.2", "1.2.3", "1.2.4", "1.2.5", "1.2.6", "1.2.7", "1.2.8", "1.2.9", "1.2.10", "2.0", "2.1", "2.2", "2.2.1", "2.2.2", "2.2.3", "2.2.4", "2.2.5", "2.2.6", "2.2.7", "2.2.8", "2.2.9", "2.2.10"]
            for i, text in enumerate(sub_headers):
                table.rows[2].cells[i].text = text

        elif is_report_10:
            for i, col_name in enumerate(display_cols):
                table.rows[0].cells[i].text = col_name
            sub_headers = ["A", "B", "1", "2", "3", "4", "5", "6", "7", "8"]
            for i, text in enumerate(sub_headers):
                table.rows[1].cells[i].text = text

        elif is_report_11:
            table.rows[0].cells[0].text = "STT"
            table.rows[0].cells[1].text = "Phường/Xã"
            table.rows[0].cells[2].text = "Chỉ số thiếu hụt về trẻ em thuộc hộ nghèo"
            table.rows[0].cells[6].text = "Chỉ số thiếu hụt về trẻ em thuộc hộ cận nghèo"
            table.rows[0].cells[2].merge(table.rows[0].cells[5])
            table.rows[0].cells[6].merge(table.rows[0].cells[9])

            table.rows[1].cells[2].text = "Tổng số trẻ em"
            table.rows[1].cells[3].text = "Y tế"
            table.rows[1].cells[5].text = "Giáo dục"
            table.rows[1].cells[6].text = "Tổng số trẻ em"
            table.rows[1].cells[7].text = "Y tế"
            table.rows[1].cells[9].text = "Giáo dục"
            table.rows[1].cells[3].merge(table.rows[1].cells[4])
            table.rows[1].cells[7].merge(table.rows[1].cells[8])
            
            table.rows[0].cells[0].merge(table.rows[1].cells[0])
            table.rows[0].cells[1].merge(table.rows[1].cells[1])

            sub_headers = ["A", "B", "1.0", "2.0", "3.0", "4.0", "5.0", "6.0", "7.0", "8.0"]
            for i, text in enumerate(sub_headers):
                table.rows[2].cells[i].text = text

        elif is_report_12_13:
            table.rows[0].cells[0].text = "STT"
            table.rows[0].cells[1].text = "Phường/Xã"
            table.rows[0].cells[2].text = "Tổng số hộ chung (Hộ dân cư trên địa bàn)"
            table.rows[0].cells[6].text = "Tổng số khẩu chung"
            table.rows[0].cells[10].text = "Tổng số hộ nghèo" if "NGHÈO THEO" in title.upper() else "Tổng số hộ cận nghèo"
            table.rows[0].cells[14].text = "Trong đó"
            table.rows[0].cells[17].text = "Tổng số khẩu hộ nghèo" if "NGHÈO THEO" in title.upper() else "Tổng số khẩu hộ cận nghèo"
            table.rows[0].cells[21].text = "Tỷ lệ (%)"
            
            table.rows[0].cells[2].merge(table.rows[0].cells[5])
            table.rows[0].cells[6].merge(table.rows[0].cells[9])
            table.rows[0].cells[10].merge(table.rows[0].cells[13])
            table.rows[0].cells[14].merge(table.rows[0].cells[16])
            table.rows[0].cells[17].merge(table.rows[0].cells[20])
            table.rows[0].cells[21].merge(table.rows[0].cells[23])

            sub_cols = ["Tổng số (1=2+3)", "Kinh", "DTTS chung", "Trong đó DT Tại chỗ", 
                        "Tổng số (5=6+7)", "Kinh", "DTTS chung", "Trong đó DT Tại chỗ",
                        "Tổng số (9=10+11)", "Kinh", "DTTS chung", "DT Tại chỗ",
                        "Hộ CSCC", "Hộ KCKNLĐ", "Chủ hộ là nữ",
                        "Tổng số (16=17+18)", "Kinh", "DTTS chung", "DT Tại chỗ",
                        "Hộ nghèo/Cận nghèo", "Tỷ lệ DTTS chung", "Tỷ lệ DTTSTC"]
            for i, text in enumerate(sub_cols):
                table.rows[1].cells[i+2].text = text
                
            table.rows[0].cells[0].merge(table.rows[1].cells[0])
            table.rows[0].cells[1].merge(table.rows[1].cells[1])
            
            sub_headers = ["A", "B", "1=2+3", "2.0", "3.0", "4.0", "5=6+7", "6.0", "7.0", "8.0", "9=10+11", "10.0", "11.0", "12.0", "13.0", "14.0", "15.0", "16=17+18", "17.0", "18.0", "19.0", "20=9/1*100", "21=11/3*100", "22=12/4*100"]
            for i, text in enumerate(sub_headers):
                table.rows[2].cells[i].text = text

        elif is_report_14_15:
            table.rows[0].cells[0].text = "STT chủ hộ"
            table.rows[0].cells[1].text = "STT thành viên hộ"
            table.rows[0].cells[2].text = "HỌ, TÊN CHỦ HỘ VÀ THÀNH VIÊN TRONG HỘ; THÔN, BON, BUÔN, TỔ DÂN PHỐ"
            table.rows[0].cells[3].text = "NĂM SINH"
            table.rows[0].cells[5].text = "Dân tộc"
            table.rows[0].cells[6].text = "Quan hệ với chủ hộ"
            table.rows[0].cells[7].text = "CHIA HỘ NGHÈO THEO" if "HỘ NGHÈO" in title.upper() else "CHIA HỘ CẬN NGHÈO THEO"
            table.rows[0].cells[10].text = "Hộ chính sách có công"
            table.rows[0].cells[11].text = "Hộ DTTC"
            table.rows[0].cells[12].text = "Hộ không có khả năng lao động"
            table.rows[0].cells[13].text = "Chính sách hỗ trợ tiếp cận với các dịch vụ xã hội cơ bản"

            table.rows[0].cells[3].merge(table.rows[0].cells[4])
            table.rows[0].cells[7].merge(table.rows[0].cells[9])
            table.rows[0].cells[13].merge(table.rows[0].cells[18])

            sub_cols = ["Nam", "Nữ", "Nghèo mới" if "HỘ NGHÈO" in title.upper() else "Cận nghèo mới", "Tái nghèo" if "HỘ NGHÈO" in title.upper() else "Tái cận nghèo", "Nghèo cũ" if "HỘ NGHÈO" in title.upper() else "Cận nghèo cũ", "Hỗ trợ y tế", "Hỗ trợ giáo dục", "Hỗ trợ sản xuất", "Hỗ trợ vay vốn tín dụng", "Hỗ trợ nhà ở", "Khác"]
            table.rows[1].cells[3].text = sub_cols[0]
            table.rows[1].cells[4].text = sub_cols[1]
            table.rows[1].cells[7].text = sub_cols[2]
            table.rows[1].cells[8].text = sub_cols[3]
            table.rows[1].cells[9].text = sub_cols[4]
            for i in range(5, 11):
                table.rows[1].cells[i+8].text = sub_cols[i]

            table.rows[0].cells[0].merge(table.rows[1].cells[0])
            table.rows[0].cells[1].merge(table.rows[1].cells[1])
            table.rows[0].cells[2].merge(table.rows[1].cells[2])
            table.rows[0].cells[5].merge(table.rows[1].cells[5])
            table.rows[0].cells[6].merge(table.rows[1].cells[6])
            table.rows[0].cells[10].merge(table.rows[1].cells[10])
            table.rows[0].cells[11].merge(table.rows[1].cells[11])
            table.rows[0].cells[12].merge(table.rows[1].cells[12])

            sub_headers = ["A", "B", "C", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16"]
            for i, text in enumerate(sub_headers):
                table.rows[2].cells[i].text = text

        else:
            hdr_cells = table.rows[0].cells
            for i, col_name in enumerate(display_cols):
                hdr_cells[i].text = col_name

        # Định dạng toàn bộ các dòng header (Bôi nền xám, font 10pt Bold, dòng cuối Italic)
        for r in range(num_hdr_rows):
            for c in range(num_cols):
                cell = table.rows[r].cells[c]
                cell.width = col_widths[c]
                shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="D3D3D3"/>')
                cell._tc.get_or_add_tcPr().append(shading)
                if cell.paragraphs:
                    p = cell.paragraphs[0]
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for run in p.runs:
                        run.font.name = 'Times New Roman'
                        run.font.size = Pt(10)
                        run.bold = True
                        if r == num_hdr_rows - 1 and num_hdr_rows > 1:
                            run.italic = True
                
        # Thiết lập dòng Dữ liệu (Data Rows)
        for _, row in df.iterrows():
            row_cells = table.add_row().cells
            is_huyen_row = str(row.get("STT", "")).isdigit()
            is_commune_header = row.get("is_commune_header", False)
            
            for i, col_name in enumerate(display_cols):
                val = row[col_name]
                text_val = ReportGenerator.format_value(val)
                row_cells[i].text = text_val
                row_cells[i].width = col_widths[i]
                
                p = row_cells[i].paragraphs[0]
                if col_name == "STT" or col_name == "STT thành viên hộ":
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                elif "Đơn vị" in col_name or "Phường/Xã" in col_name or "Phân tổ" in col_name or col_name == "Họ tên" or is_commune_header:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                else:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if is_report_14_15 else WD_ALIGN_PARAGRAPH.RIGHT
                    
                for run in p.runs:
                    run.font.name = 'Times New Roman'
                    run.font.size = Pt(11)
                    if is_huyen_row or is_commune_header:
                        run.bold = True
            
            if is_commune_header:
                row_cells[0].merge(row_cells[-1])
                
        doc.save(str(save_path))
        return save_path

    @staticmethod
    def generate_pdf(df: pd.DataFrame, title: str, save_path: Path) -> Path:
        """
        Tạo báo cáo định dạng PDF chuyên nghiệp với FPDF2, khôi phục Multi-tier Header,
        thiết lập tỷ lệ cột auto-fit chuẩn xác, bôi đậm dòng Huyện và in nghiêng dòng công thức.
        """
        font_family = "TimesUnicode" if FONT_PATH.exists() else "Helvetica"
        
        class PDFReport(FPDF):
            def header(self):
                pass
            def footer(self):
                self.set_y(-15)
                self.set_font(font_family, "I", 9)
                self.cell(0, 10, f"Trang {self.page_no()}/{{nb}}", align="C")

        display_cols = [c for c in df.columns if c != "is_commune_header"]
        num_cols = len(display_cols)
        paper_format = "A3" if num_cols > 12 else "A4"

        pdf = PDFReport(orientation="L", unit="mm", format=paper_format)
        pdf.set_auto_page_break(auto=True, margin=15)
        
        if FONT_PATH.exists():
            pdf.add_font("TimesUnicode", "", str(FONT_PATH))
            pdf.add_font("TimesUnicode", "B", str(FONT_BOLD_PATH if FONT_BOLD_PATH.exists() else FONT_PATH))
            pdf.add_font("TimesUnicode", "I", str(FONT_ITALIC_PATH if FONT_ITALIC_PATH.exists() else FONT_PATH))
            pdf.add_font("TimesUnicode", "BI", str(FONT_BOLD_ITALIC_PATH if FONT_BOLD_ITALIC_PATH.exists() else FONT_PATH))
        else:
            pdf.set_font("Arial", size=11)

        pdf.add_page()
        
        # Khối Tiêu đề Hành chính
        pdf.set_font(font_family, "B", 13)
        w_half = (pdf.w - 30) / 2
        pdf.cell(w_half, 8, "ỦY BAN NHÂN DÂN", align="C")
        pdf.cell(w_half, 8, "CỘNG HOÀ XÃ HỘI CHỦ NGHĨA VIỆT NAM", align="C")
        pdf.ln(8)
        pdf.cell(w_half, 8, "TỈNH / THÀNH PHỐ", align="C")
        pdf.cell(w_half, 8, "Độc lập - Tự do - Hạnh phúc", align="C")
        pdf.ln(20)
        
        # Tiêu đề chính
        pdf.set_font(font_family, "B", 16)
        pdf.cell(0, 10, title.upper(), align="C")
        pdf.ln(10)
        
        # Tiêu đề phụ
        pdf.set_font(font_family, "I", 12)
        pdf.cell(0, 8, "Kèm theo báo cáo kết quả rà soát định kỳ", align="C")
        pdf.ln(15)
        
        if num_cols == 19:
            pdf.set_font(font_family, "BI", 12)
            pdf.cell(0, 8, "Phụ lục số 2.3", align="R")
            pdf.ln(10)
        
        is_report_1 = num_cols == 16 and "Nhân khẩu" in df.columns
        is_report_2_3 = num_cols == 12 and "Phân tổ" in df.columns
        is_report_4_6 = num_cols == 16 and "Tổng số thiếu hụt" in df.columns
        is_report_5_7 = num_cols == 15 and ("Tổng số hộ nghèo" in df.columns or "Tổng số hộ cận nghèo" in df.columns)
        is_report_8 = num_cols == 13 and "Phân tổ" in df.columns
        is_report_9 = num_cols == 28
        is_report_10 = num_cols == 10 and "1. Thiếu đất sản xuất" in df.columns
        is_report_11 = num_cols == 10 and "1. Tổng số trẻ em hộ nghèo" in df.columns
        is_report_12_13 = num_cols == 24
        is_report_14_15 = num_cols == 19

        # Tỷ lệ chiều rộng các cột theo tỷ lệ chuẩn Excel gốc
        tbl_w = pdf.w - 30
        if is_report_1 or is_report_4_6:
            base_widths = [5.71, 26.0] + [11.2] * 2 + [7.71] * 12
        elif is_report_2_3:
            base_widths = [5.71, 26.0, 12.0] + [12.0] * 9
        elif is_report_5_7:
            base_widths = [5.71, 26.0, 11.2] + [7.71] * 12
        elif is_report_8:
            base_widths = [5.71, 24.0, 12.0] + [11.0] * 10
        elif is_report_9:
            base_widths = [5.71, 24.0] + [7.0] * 26
        elif is_report_10:
            base_widths = [5.71, 30.0] + [14.0] * 8
        elif is_report_11:
            base_widths = [5.71, 30.0] + [12.0] * 8
        elif is_report_12_13:
            base_widths = [5.0, 20.0] + [8.0] * 22
        elif is_report_14_15:
            base_widths = [5.0, 5.0, 30.0, 8.0, 8.0, 10.0, 12.0] + [8.0] * 12
        else:
            base_widths = [10.0] * num_cols
            
        sum_w = sum(base_widths)
        col_widths = [w * (tbl_w / sum_w) for w in base_widths]

        hdr_style = FontFace(emphasis="B", size_pt=10, fill_color=(211, 211, 211))
        sub_hdr_style = FontFace(emphasis="BI", size_pt=10, fill_color=(211, 211, 211))
        huyen_style = FontFace(emphasis="B", size_pt=11)
        xa_style = FontFace(size_pt=11)

        pdf.set_font(font_family, "", 11)
        if is_report_1 or is_report_2_3 or is_report_4_6 or is_report_5_7 or is_report_8 or is_report_9 or is_report_11 or is_report_12_13 or is_report_14_15:
            num_heading_rows = 3
        elif is_report_10:
            num_heading_rows = 2
        else:
            num_heading_rows = 1
            
        with pdf.table(text_align="CENTER", width=tbl_w, col_widths=col_widths, line_height=9, num_heading_rows=num_heading_rows) as table:
            if is_report_1:
                # Row 0
                row0 = table.row()
                row0.cell("STT", rowspan=2, style=hdr_style)
                row0.cell("Phường/Xã", rowspan=2, style=hdr_style)
                row0.cell("Tổng số hộ dân cư", colspan=2, style=hdr_style)
                row0.cell("Kết quả rà soát về hộ (chính thức)", colspan=6, style=hdr_style)
                row0.cell("Kết quả rà soát về khẩu (chính thức)", colspan=6, style=hdr_style)
                # Row 1
                row1 = table.row()
                row1.cell("Số hộ", style=hdr_style)
                row1.cell("Nhân khẩu", style=hdr_style)
                row1.cell("Số hộ", style=hdr_style)
                row1.cell("Tỷ lệ", style=hdr_style)
                row1.cell("Số hộ", style=hdr_style)
                row1.cell("Tỷ lệ", style=hdr_style)
                row1.cell("Số hộ", style=hdr_style)
                row1.cell("Tỷ lệ", style=hdr_style)
                row1.cell("Số khẩu", style=hdr_style)
                row1.cell("Tỷ lệ", style=hdr_style)
                row1.cell("Số khẩu", style=hdr_style)
                row1.cell("Tỷ lệ", style=hdr_style)
                row1.cell("Số khẩu", style=hdr_style)
                row1.cell("Tỷ lệ", style=hdr_style)
                # Row 2
                row2 = table.row()
                sub_headers = ["A", "B", "1", "2", "3", "4=3/1*100", "5", "6=5/1*100", "7", "8=7/1*100", "9", "10=9/2*100", "11", "12=11/2*100", "13", "14=13/2*100"]
                for text in sub_headers:
                    row2.cell(text, style=sub_hdr_style)

            elif is_report_2_3:
                row0 = table.row()
                row0.cell("STT", rowspan=2, style=hdr_style)
                row0.cell("Phường/Xã", rowspan=2, style=hdr_style)
                row0.cell("Phân tổ", rowspan=2, style=hdr_style)
                row0.cell("Tổng số hộ nghèo đầu kỳ" if "Tổng số hộ nghèo đầu kỳ" in df.columns else "Tổng số hộ cận nghèo đầu kỳ", rowspan=2, style=hdr_style)
                row0.cell("Số hộ thoát nghèo" if "Tổng số hộ nghèo đầu kỳ" in df.columns else "Số hộ thoát cận nghèo", colspan=2, style=hdr_style)
                row0.cell("Số hộ khác giảm", rowspan=2, style=hdr_style)
                row0.cell("Số hộ cận nghèo trở thành" if "Tổng số hộ nghèo đầu kỳ" in df.columns else "Số hộ nghèo trở thành hộ cận nghèo", rowspan=2, style=hdr_style)
                row0.cell("Số hộ nghèo bổ sung" if "Tổng số hộ nghèo đầu kỳ" in df.columns else "Số hộ cận nghèo bổ sung", colspan=2, style=hdr_style)
                row0.cell("Số hộ khác tăng", rowspan=2, style=hdr_style)
                row0.cell("Tổng số hộ nghèo cuối kỳ" if "Tổng số hộ nghèo đầu kỳ" in df.columns else "Tổng số hộ cận nghèo cuối kỳ", rowspan=2, style=hdr_style)
                
                row1 = table.row()
                row1.cell("Trở thành cận nghèo" if "Tổng số hộ nghèo đầu kỳ" in df.columns else "Trở thành hộ nghèo", style=hdr_style)
                row1.cell("Vượt chuẩn cận nghèo", style=hdr_style)
                row1.cell("Tái nghèo" if "Tổng số hộ nghèo đầu kỳ" in df.columns else "Tái cận nghèo", style=hdr_style)
                row1.cell("Phát sinh mới", style=hdr_style)
                
                row2 = table.row()
                sub_headers = ["A", "B", "C", "1", "2", "3", "4", "5", "6", "7", "8", "9=1-2-3-4+5+6+7+8"]
                for text in sub_headers:
                    row2.cell(text, style=sub_hdr_style)

            elif is_report_4_6:
                col_total = "Tổng số hộ nghèo" if "Tổng số hộ nghèo" in df.columns else "Tổng số hộ cận nghèo"
                row0 = table.row()
                row0.cell("STT", rowspan=2, style=hdr_style)
                row0.cell("Phường/Xã", rowspan=2, style=hdr_style)
                row0.cell(col_total, rowspan=2, style=hdr_style)
                row0.cell("Tổng số thiếu hụt", rowspan=2, style=hdr_style)
                row0.cell("Các chỉ số thiếu hụt dịch vụ xã hội cơ bản", colspan=12, style=hdr_style)
                
                row1 = table.row()
                sub_cols = ["1. Việc làm", "2. Người phụ thuộc", "3. Dinh dưỡng", "4. BHYT", "5. Giáo dục NL", "6. Giáo dục TE", "7. CL nhà ở", "8. DT nhà ở", "9. Nguồn nước", "10. Nhà tiêu", "11. Viễn thông", "12. PT thông tin"]
                for text in sub_cols:
                    row1.cell(text, style=hdr_style)
                
                row2 = table.row()
                sub_headers = ["A", "B", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14"]
                for text in sub_headers:
                    row2.cell(text, style=sub_hdr_style)

            elif is_report_5_7:
                col_total = "Tổng số hộ nghèo" if "Tổng số hộ nghèo" in df.columns else "Tổng số hộ cận nghèo"
                row0 = table.row()
                row0.cell("STT", rowspan=2, style=hdr_style)
                row0.cell("Phường/Xã", rowspan=2, style=hdr_style)
                row0.cell(col_total, rowspan=2, style=hdr_style)
                row0.cell("Tỷ lệ các chỉ số thiếu hụt dịch vụ xã hội cơ bản (%)", colspan=12, style=hdr_style)
                
                row1 = table.row()
                sub_cols = ["1. Việc làm", "2. Người phụ thuộc", "3. Dinh dưỡng", "4. BHYT", "5. Giáo dục NL", "6. Giáo dục TE", "7. CL nhà ở", "8. DT nhà ở", "9. Nguồn nước", "10. Nhà tiêu", "11. Viễn thông", "12. PT thông tin"]
                for text in sub_cols:
                    row1.cell(text, style=hdr_style)
                
                row2 = table.row()
                sub_headers = ["A", "B", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13"]
                for text in sub_headers:
                    row2.cell(text, style=sub_hdr_style)

            elif is_report_8:
                row0 = table.row()
                row0.cell("STT", rowspan=2, style=hdr_style)
                row0.cell("Phường/Xã", rowspan=2, style=hdr_style)
                row0.cell("Phân tổ", rowspan=2, style=hdr_style)
                row0.cell("Hộ nghèo", colspan=5, style=hdr_style)
                row0.cell("Hộ cận nghèo", colspan=5, style=hdr_style)
                
                row1 = table.row()
                sub_cols = ["Tổng số", "Hộ DTTS", "Hộ không có khả năng lao động", "Hộ có người có công", "Khác", "Tổng số", "Hộ DTTS", "Hộ không có khả năng lao động", "Hộ có người có công", "Khác"]
                for text in sub_cols:
                    row1.cell(text, style=hdr_style)
                
                row2 = table.row()
                sub_headers = ["A", "B", "C", "1", "2", "3", "4", "5=1-2-3-4", "6", "7", "8", "9", "10=6-7-8-9"]
                for text in sub_headers:
                    row2.cell(text, style=sub_hdr_style)

            elif is_report_9:
                row0 = table.row()
                row0.cell("STT", rowspan=2, style=hdr_style)
                row0.cell("Phường/Xã", rowspan=2, style=hdr_style)
                row0.cell("Hộ nghèo", colspan=13, style=hdr_style)
                row0.cell("Hộ cận nghèo", colspan=13, style=hdr_style)
                
                row1 = table.row()
                sub_cols = ["Tổng số", "Kinh", "Tổng DTTS", "Ê đê", "Mạ", "Mường", "Thái", "M'Nông", "Tày", "Nùng", "Mông", "Dao", "Khác", "Tổng số", "Kinh", "Tổng DTTS", "Ê đê", "Mạ", "Mường", "Thái", "M'Nông", "Tày", "Nùng", "Mông", "Dao", "Khác"]
                for text in sub_cols:
                    row1.cell(text, style=hdr_style)
                
                row2 = table.row()
                sub_headers = ["A", "B", "1.0", "1.1", "1.2", "1.2.1", "1.2.2", "1.2.3", "1.2.4", "1.2.5", "1.2.6", "1.2.7", "1.2.8", "1.2.9", "1.2.10", "2.0", "2.1", "2.2", "2.2.1", "2.2.2", "2.2.3", "2.2.4", "2.2.5", "2.2.6", "2.2.7", "2.2.8", "2.2.9", "2.2.10"]
                for text in sub_headers:
                    row2.cell(text, style=sub_hdr_style)

            elif is_report_10:
                row0 = table.row()
                for col_name in display_cols:
                    row0.cell(str(col_name), style=hdr_style)
                row1 = table.row()
                sub_headers = ["A", "B", "1", "2", "3", "4", "5", "6", "7", "8"]
                for text in sub_headers:
                    row1.cell(text, style=sub_hdr_style)

            elif is_report_11:
                row0 = table.row()
                row0.cell("STT", rowspan=2, style=hdr_style)
                row0.cell("Phường/Xã", rowspan=2, style=hdr_style)
                row0.cell("Chỉ số thiếu hụt về trẻ em thuộc hộ nghèo", colspan=4, style=hdr_style)
                row0.cell("Chỉ số thiếu hụt về trẻ em thuộc hộ cận nghèo", colspan=4, style=hdr_style)
                
                row1 = table.row()
                row1.cell("Tổng số trẻ em", style=hdr_style)
                row1.cell("Y tế", colspan=2, style=hdr_style)
                row1.cell("Giáo dục", style=hdr_style)
                row1.cell("Tổng số trẻ em", style=hdr_style)
                row1.cell("Y tế", colspan=2, style=hdr_style)
                row1.cell("Giáo dục", style=hdr_style)
                
                row2 = table.row()
                sub_headers = ["A", "B", "1.0", "2.0", "3.0", "4.0", "5.0", "6.0", "7.0", "8.0"]
                for text in sub_headers:
                    row2.cell(text, style=sub_hdr_style)

            elif is_report_12_13:
                row0 = table.row()
                row0.cell("STT", rowspan=2, style=hdr_style)
                row0.cell("Phường/Xã", rowspan=2, style=hdr_style)
                row0.cell("Tổng số hộ chung (Hộ dân cư trên địa bàn)", colspan=4, style=hdr_style)
                row0.cell("Tổng số khẩu chung", colspan=4, style=hdr_style)
                col_hn_cn = "Tổng số hộ nghèo" if "NGHÈO THEO" in title.upper() else "Tổng số hộ cận nghèo"
                row0.cell(col_hn_cn, colspan=4, style=hdr_style)
                row0.cell("Trong đó", colspan=3, style=hdr_style)
                col_k_hn_cn = "Tổng số khẩu hộ nghèo" if "NGHÈO THEO" in title.upper() else "Tổng số khẩu hộ cận nghèo"
                row0.cell(col_k_hn_cn, colspan=4, style=hdr_style)
                row0.cell("Tỷ lệ (%)", colspan=3, style=hdr_style)

                row1 = table.row()
                sub_cols = ["Tổng số (1=2+3)", "Kinh", "DTTS chung", "Trong đó DT Tại chỗ", 
                            "Tổng số (5=6+7)", "Kinh", "DTTS chung", "Trong đó DT Tại chỗ",
                            "Tổng số (9=10+11)", "Kinh", "DTTS chung", "DT Tại chỗ",
                            "Hộ CSCC", "Hộ KCKNLĐ", "Chủ hộ là nữ",
                            "Tổng số (16=17+18)", "Kinh", "DTTS chung", "DT Tại chỗ",
                            "Hộ nghèo/Cận nghèo", "Tỷ lệ DTTS chung", "Tỷ lệ DTTSTC"]
                for text in sub_cols:
                    row1.cell(text, style=hdr_style)
                
                row2 = table.row()
                sub_headers = ["A", "B", "1=2+3", "2.0", "3.0", "4.0", "5=6+7", "6.0", "7.0", "8.0", "9=10+11", "10.0", "11.0", "12.0", "13.0", "14.0", "15.0", "16=17+18", "17.0", "18.0", "19.0", "20=9/1*100", "21=11/3*100", "22=12/4*100"]
                for text in sub_headers:
                    row2.cell(text, style=sub_hdr_style)

            elif is_report_14_15:
                row0 = table.row()
                row0.cell("STT chủ hộ", rowspan=2, style=hdr_style)
                row0.cell("STT thành viên hộ", rowspan=2, style=hdr_style)
                row0.cell("HỌ, TÊN CHỦ HỘ VÀ THÀNH VIÊN TRONG HỘ; THÔN, BON, BUÔN, TỔ DÂN PHỐ", rowspan=2, style=hdr_style)
                row0.cell("NĂM SINH", colspan=2, style=hdr_style)
                row0.cell("Dân tộc", rowspan=2, style=hdr_style)
                row0.cell("Quan hệ với chủ hộ", rowspan=2, style=hdr_style)
                col_chia = "CHIA HỘ NGHÈO THEO" if "HỘ NGHÈO" in title.upper() else "CHIA HỘ CẬN NGHÈO THEO"
                row0.cell(col_chia, colspan=3, style=hdr_style)
                row0.cell("Hộ chính sách có công", rowspan=2, style=hdr_style)
                row0.cell("Hộ DTTC", rowspan=2, style=hdr_style)
                row0.cell("Hộ không có khả năng lao động", rowspan=2, style=hdr_style)
                row0.cell("Chính sách hỗ trợ tiếp cận với các dịch vụ xã hội cơ bản", colspan=6, style=hdr_style)
                
                row1 = table.row()
                sub_cols = ["Nam", "Nữ", "Nghèo mới" if "HỘ NGHÈO" in title.upper() else "Cận nghèo mới", "Tái nghèo" if "HỘ NGHÈO" in title.upper() else "Tái cận nghèo", "Nghèo cũ" if "HỘ NGHÈO" in title.upper() else "Cận nghèo cũ", "Hỗ trợ y tế", "Hỗ trợ giáo dục", "Hỗ trợ sản xuất", "Hỗ trợ vay vốn tín dụng", "Hỗ trợ nhà ở", "Khác"]
                for text in sub_cols:
                    row1.cell(text, style=hdr_style)

                row2 = table.row()
                sub_headers = ["A", "B", "C", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16"]
                for text in sub_headers:
                    row2.cell(text, style=sub_hdr_style)

            else:
                header_row = table.row()
                for col_name in display_cols:
                    header_row.cell(str(col_name), style=hdr_style)
            
            # Data Rows
            for _, r in df.iterrows():
                data_row = table.row()
                is_huyen_row = str(r.get("STT", "")).isdigit()
                is_commune_header = r.get("is_commune_header", False)
                curr_style = huyen_style if is_huyen_row or is_commune_header else xa_style
                
                if is_commune_header:
                    val = r[display_cols[0]]
                    text_val = ReportGenerator.format_value(val)
                    data_row.cell(text_val, colspan=num_cols, style=curr_style, align="L")
                else:
                    for i, col_name in enumerate(display_cols):
                        val = r[col_name]
                        text_val = ReportGenerator.format_value(val)
                        align = "C" if (col_name == "STT" or col_name == "STT thành viên hộ" or (is_report_14_15 and "Đơn vị" not in col_name and "Họ tên" not in col_name)) else ("L" if "Đơn vị" in col_name or "Phường/Xã" in col_name or "Phân tổ" in col_name or col_name == "Họ tên" else "R")
                        if is_report_14_15 and col_name in ["STT chủ hộ", "STT thành viên hộ", "Năm sinh Nam", "Năm sinh Nữ"]:
                            align = "C"
                        data_row.cell(text_val, style=curr_style, align=align)

        pdf.output(str(save_path))
        return save_path

    @staticmethod
    def generate(report_id: int, year: int = 2024, district: str | None = None) -> dict:
        """
        Khởi chạy tạo báo cáo hoàn chỉnh (Query SQL -> Căn chỉnh -> Word + PDF).
        """
        from src.query_control.agentic.report_queries import execute_report_query
        
        df, sql, title = execute_report_query(report_id, year, district)
        
        prefix = f"bao_cao_{report_id}_{year}"
        if district:
            prefix += f"_{district.lower()}"
            
        docx_path = REPORTS_DIR / f"{prefix}.docx"
        pdf_path = REPORTS_DIR / f"{prefix}.pdf"
        
        try:
            ReportGenerator.generate_docx(df, title, docx_path)
        except PermissionError:
            docx_path = REPORTS_DIR / f"{prefix}_alt.docx"
            ReportGenerator.generate_docx(df, title, docx_path)
            
        try:
            ReportGenerator.generate_pdf(df, title, pdf_path)
        except PermissionError:
            pdf_path = REPORTS_DIR / f"{prefix}_alt.pdf"
            ReportGenerator.generate_pdf(df, title, pdf_path)

        
        answer = f"### Đã tạo thành công Báo cáo số {report_id}: **{title}**\n\n"
        answer += f"- **Năm thống kê:** {year}\n"
        if district:
            answer += f"- **Địa bàn lọc:** Huyện/Thành phố {district}\n"
        answer += f"- **Tổng số dòng dữ liệu:** {len(df)} dòng\n\n"
        answer += "Hệ thống đã tự động xuất báo cáo ra 2 định dạng chuẩn văn bản Chính phủ (Word `.docx` và `PDF`) với phông chữ Times New Roman, căn lề 0.5 inch, layout Landscape chuyên nghiệp. Khối tiêu đề hành chính Quốc hiệu, Cơ quan ban hành cùng cấu trúc Multi-tier header đã được tích hợp đầy đủ. Các cột không có dữ liệu trong dataset đã được gán giá trị 0/trống theo đúng tiêu chuẩn biểu mẫu.\n\n"
        answer += "Xin mời bạn bấm nút tải về ở bên dưới để lưu báo cáo."
        
        return {
            "df": df,
            "sql": sql,
            "title": title,
            "docx_path": docx_path,
            "pdf_path": pdf_path,
            "answer": answer
        }
