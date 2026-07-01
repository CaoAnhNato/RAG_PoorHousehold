import sys
sys.stdout.reconfigure(encoding='utf-8')
from src.query_control.agentic.report_generator import ReportGenerator

def test():
    print("Generating Report 1...")
    res = ReportGenerator.generate(1, 2024)
    print("Generated DOCX:", res["docx_path"])
    print("Generated PDF:", res["pdf_path"])

if __name__ == "__main__":
    test()
