import sys
sys.stdout.reconfigure(encoding='utf-8')
from src.query_control.agentic.agent_pipeline import AgenticPipeline
import time
from pathlib import Path

prompts = [
    # Group 1: Chi tiết 1 chủ hộ / mã hộ cụ thể (Hỏi nhiều thông tin cùng lúc)
    "Hộ Phùng Thị Ánh ở huyện Cư Jút có điểm B1, điểm B2 và phân loại nghèo là gì?",
    "Ai là chủ hộ có mã hộ là 1001, thuộc phân loại nghèo nào và hộ có bao nhiêu nhân khẩu?",
    "Chủ hộ Nông Văn Dũng ở huyện Tuy Đức thuộc dân tộc nào, năm sinh bao nhiêu và có điểm B1 là mấy?",
    "Hộ Hoàng Văn Khánh ở huyện Krông Nô thuộc phân loại gì, có bị thiếu hụt nước sạch hay nhà tiêu hợp vệ sinh không?",
    "Cho biết mã hộ, phân loại nghèo và nguyên nhân nghèo chính của hộ Phùng Văn Diệt",
    "Chủ hộ Y Khánh Bkrông có số nhân khẩu là bao nhiêu và hộ này có được hỗ trợ y tế hay giáo dục không?",
    "Hộ Phùng Thị Dung ở xã Quảng Khê thuộc huyện Đăk Glong có bị thiếu hụt đất sản xuất hoặc thiếu vốn không?",
    "Cho biết thông tin chi tiết về mã hộ, phân loại, điểm B1 và giới tính chủ hộ của hộ Nguyễn Thị Ánh Tuyết",
    "Hộ Lý Lê Voánh có phân loại nghèo đầu kỳ và cuối kỳ như thế nào, có thoát nghèo không?",
    "Chủ hộ Trần Ánh Minh có bao nhiêu trẻ em trong hộ và có trẻ em nào bị thiếu hụt bảo hiểm y tế không?",

    # Group 2: Chi tiết các thành viên trong 1 hộ cụ thể (Hỏi nhiều thông tin thành viên cùng lúc)
    "Liệt kê danh sách tất cả các thành viên trong hộ của chủ hộ Nông Văn Dũng kèm quan hệ với chủ hộ và năm sinh",
    "Hộ Hoàng Văn Khánh ở xã Đức Xuyên có những thành viên nào, giới tính và độ tuổi của từng người ra sao?",
    "Trong hộ của chủ hộ Phùng Văn Diệt, ai là vợ hoặc con và họ có bị thiếu hụt bảo hiểm y tế không?",
    "Cho biết tên, quan hệ với chủ hộ và dân tộc của từng thành viên trong hộ có mã hộ là 1001",
    "Các thành viên trong hộ Y Khánh Bkrông có bị thiếu hụt đi học hay thiếu hụt dinh dưỡng không?",
    "Liệt kê danh sách con trong hộ Phùng Thị Dung kèm năm sinh và tình trạng bảo hiểm y tế",
    "Hộ Nguyễn Thị Ánh Tuyết có bao nhiêu thành viên và chi tiết tên, quan hệ của từng người như thế nào?",
    "Trong hộ Phùng Văn Hoạt, có thành viên nào là người dân tộc thiểu số hoặc không có bảo hiểm y tế không?",
    "Liệt kê chi tiết họ tên, năm sinh, quan hệ với chủ hộ của tất cả nhân khẩu thuộc hộ Đinh Văn Khánh",
    "Hộ Trần Ánh Minh có những thành viên nào đang trong độ tuổi đi học và có bị thiếu hụt giáo dục không?",

    # Group 3: Liệt kê danh sách nhiều hộ kèm theo nhiều thông tin chi tiết (Đa thuộc tính)
    "Liệt kê danh sách 5 hộ nghèo ở xã Quảng Hòa thuộc huyện Đắk Glong kèm tên chủ hộ, điểm B1 và điểm B2",
    "Cho biết tên chủ hộ, mã hộ và số nhân khẩu của 5 hộ cận nghèo tại huyện Tuy Đức có điểm B1 cao nhất",
    "Liệt kê 10 hộ nghèo ở huyện Krông Nô bị thiếu hụt cả nước sạch và nhà tiêu hợp vệ sinh kèm theo tên chủ hộ và xã/phường",
    "Danh sách 5 hộ nghèo là người đồng bào dân tộc thiểu số ở xã Đắk Som huyện Đắk Glong kèm tên chủ hộ, dân tộc và số nhân khẩu",
    "Liệt kê tên chủ hộ, phân loại nghèo và lý do chính dẫn đến nghèo của 5 hộ có nguyên nhân là thiếu đất sản xuất tại huyện Đắk R'Lấp",
    "Cho biết danh sách 5 hộ nghèo do chủ hộ là nữ ở huyện Đắk Mil kèm tên chủ hộ, năm sinh và điểm B1",
    "Liệt kê 5 hộ có trẻ em bị thiếu hụt dinh dưỡng ở huyện Cư Jút kèm tên chủ hộ, tổng số trẻ em và phân loại nghèo",
    "Danh sách 5 hộ nghèo vừa được hỗ trợ y tế vừa được hỗ trợ giáo dục trong năm 2024 kèm tên chủ hộ và địa chỉ xã",
    "Liệt kê chi tiết 5 hộ nghèo có đông nhân khẩu nhất ở huyện Đắk Glong kèm tên chủ hộ, số nhân khẩu và điểm B1",
    "Cho biết tên chủ hộ, phân loại đầu kỳ và cuối kỳ của 5 hộ đã thoát nghèo tại huyện Krông Nô"
]

def main():
    pipeline = AgenticPipeline()
    results = []
    total_latency = 0
    success_count = 0

    print(f"==========================================================================")
    print(f"🚀 BẮT ĐẦU KIỂM THỬ 30 CÂU HỎI ĐA DẠNG CHI TIẾT CHỦ HỘ / THÀNH VIÊN")
    print(f"==========================================================================\n")

    for i, p in enumerate(prompts, 1):
        print(f"\n[{i}/30] Testing: {p}")
        t0 = time.time()
        res = pipeline.process(p, mode="Hỏi - Đáp", stream=False)
        t1 = time.time()
        dt = t1 - t0
        total_latency += dt

        err = res.get("error")
        sql = res.get("sql", "")
        df = res.get("data")
        has_df = df is not None
        df_rows = len(df) if has_df else 0

        # Kiểm tra thành công (thực thi SQL không lỗi runtime)
        is_success = (err is None) and (has_df or "SELECT" in str(sql))
        if is_success:
            success_count += 1
            status_icon = "✅"
        else:
            status_icon = "❌"

        print(f"--> Status: {status_icon} | Latency: {dt:.2f}s | Rows: {df_rows}")
        if err:
            print(f"    Error details: {err}")
        else:
            print(f"    SQL sample: {str(sql)[:120]}...")

        results.append({
            "index": i,
            "question": p,
            "latency": dt,
            "status": "Success" if is_success else "Failed",
            "error": str(err) if err else "None",
            "rows": df_rows,
            "sql": str(sql)
        })

    avg_latency = total_latency / len(prompts)
    accuracy = (success_count / len(prompts)) * 100.0

    print(f"\n==========================================================================")
    print(f"📊 TỔNG KẾT KIỂM THỬ 30 CÂU HỎI:")
    print(f"   - Tỉ lệ thành công (Success Rate): {accuracy:.2f}% ({success_count}/30)")
    print(f"   - Độ trễ trung bình (Avg Latency): {avg_latency:.2f}s/câu")
    print(f"==========================================================================")

    # Xuất báo cáo Markdown ra artifacts
    report_path = Path("artifacts/validation_30_household_member_report.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Báo Cáo Kiểm Thử 30 Câu Hỏi Đa Dạng Chi Tiết Chủ Hộ & Thành Viên\n\n")
        f.write(f"- **Ngày kiểm thử:** `{time.strftime('%Y-%m-%d %H:%M:%S')}`\n")
        f.write(f"- **Tổng số câu hỏi:** `30`\n")
        f.write(f"- **Tỉ lệ thực thi thành công (Accuracy):** `{accuracy:.2f}%` (`{success_count}/30`)\n")
        f.write(f"- **Độ trễ trung bình (Average Latency):** `{avg_latency:.2f}s/câu`\n\n")
        f.write("## Chi Tiết Từng Câu Hỏi\n\n")
        f.write("| STT | Câu hỏi | Nhóm | Trạng thái | Latency | Số dòng | Lỗi / SQL ghi chú |\n")
        f.write("| --- | --- | --- | --- | --- | --- | --- |\n")
        for r in results:
            idx = r["index"]
            group = "Chủ hộ/Mã hộ" if idx <= 10 else ("Thành viên" if idx <= 20 else "Danh sách nhiều hộ")
            icon = "✅" if r["status"] == "Success" else "❌"
            sql_note = r['sql'].replace('\n', ' ')[:80] + "..." if r['sql'] else "No SQL"
            err_note = f"**ERR**: {r['error']}" if r['error'] != "None" else f"`{sql_note}`"
            f.write(f"| {idx} | {r['question']} | {group} | {icon} {r['status']} | {r['latency']:.2f}s | {r['rows']} | {err_note} |\n")

    print(f"\nĐã lưu báo cáo chi tiết vào: {report_path}")

if __name__ == "__main__":
    main()
