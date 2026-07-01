import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
from src.query_control.agentic.report_generator import ReportGenerator
try:
    report_data = ReportGenerator.generate(report_id=13, year=2024, district=None)
    print("PDF path:", report_data.get('pdf_path'))
except Exception as e:
    import traceback
    traceback.print_exc()
