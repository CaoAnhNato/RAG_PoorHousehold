from pathlib import Path
import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from tests.validate_report_11 import extract_text_from_pdf

pdf_path = Path('Runtime/reports/bao_cao_11_2024.pdf')
text = extract_text_from_pdf(pdf_path)

with open('debug_text.txt', 'w', encoding='utf-8') as f:
    f.write(text)
print("done")
