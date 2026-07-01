# -*- coding: utf-8 -*-
import sys
import time
import json
from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.query_control.agentic.semantic_cache import SemanticCacheManager
from src.query_control.agentic.schema_linker import SchemaLinker
from src.query_control.agentic.sql_generator import SQLGenerator
from src.query_control.agentic.sql_refiner import SQLRefiner

def run_benchmark():
    print("="*80)
    print("BAT DAU BENCHMARK TIM NGUONG THRESHOLD TOI UU CHO ROUTE 3 (PLANNER CACHE)")
    print("="*80)

    test_queries = [
        {
            "id": 1,
            "question": "thống kê sl hộ nghèo vs cận nghèo dtts năm 2024 ở các huyện xem thế nào",
            "gt_sql": 'SELECT "administrative.district" AS district, SUM(CASE WHEN "classify" = \'Hộ nghèo\' THEN 1 ELSE 0 END) AS poor_dtts, SUM(CASE WHEN "classify" = \'Hộ cận nghèo\' THEN 1 ELSE 0 END) AS near_poor_dtts FROM households WHERE "family.isDTTS" = true AND "administrative.year" = 2024 AND "classify" IN (\'Hộ nghèo\', \'Hộ cận nghèo\') GROUP BY district ORDER BY poor_dtts DESC;'
        },
        {
            "id": 2,
            "question": "huyện krông nô 2024 có bao nhiêu hn bị thiếu vốn sx với thiếu đất sx?",
            "gt_sql": 'SELECT SUM(CASE WHEN "reason.lackCapital" = true THEN 1 ELSE 0 END) AS lack_capital, SUM(CASE WHEN "reason.lackProductionLand" = true THEN 1 ELSE 0 END) AS lack_land FROM households WHERE "administrative.district" ILIKE \'%Krông Nô%\' AND "classify" = \'Hộ nghèo\' AND "administrative.year" = 2024;'
        },
        {
            "id": 3,
            "question": "năm 2024 khu vực thành thị hay nông thôn có số hộ thoát nghèo nhiều hơn?",
            "gt_sql": 'SELECT "administrative.areaType" AS area_type, COUNT(*) AS escaped_count FROM households WHERE "transition.isEscapedPoverty" = true AND "administrative.year" = 2024 GROUP BY area_type ORDER BY escaped_count DESC;'
        },
        {
            "id": 4,
            "question": "top 3 xã có trẻ em ko đi học nhiều nhất 2024 là xã nào?",
            "gt_sql": 'SELECT "administrative.commune" AS commune, SUM("children.schoolAttendanceDeprivedCount") AS deprived_children FROM households WHERE "administrative.year" = 2024 AND "children.schoolAttendanceDeprivedCount" > 0 GROUP BY commune ORDER BY deprived_children DESC LIMIT 3;'
        },
        {
            "id": 5,
            "question": "ở tp gia nghĩa bn hộ nghèo bị thiếu hụt chất lượng nhà ở với diện tích nhà ở năm 2024",
            "gt_sql": 'SELECT SUM(CASE WHEN "deprivation.housingQuality" = true THEN 1 ELSE 0 END) AS poor_quality_housing, SUM(CASE WHEN "deprivation.housingArea" = true THEN 1 ELSE 0 END) AS small_area_housing FROM households WHERE "administrative.district" ILIKE \'%Gia Nghĩa%\' AND "classify" = \'Hộ nghèo\' AND "administrative.year" = 2024;'
        },
        {
            "id": 6,
            "question": "tính tỷ lệ chủ hộ nam vs nữ trong các hcn năm 2024 toàn tỉnh",
            "gt_sql": 'SELECT "family.hostGender" AS gender, COUNT(*) AS count, ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage FROM households WHERE "classify" = \'Hộ cận nghèo\' AND "administrative.year" = 2024 AND "family.hostGender" IN (\'Nam\', \'Nữ\') GROUP BY gender;'
        },
        {
            "id": 7,
            "question": "so sánh sl hộ nghèo ko có khả năng lao động ở đắk mil giữa 2 năm 2023 vs 2024",
            "gt_sql": 'SELECT "administrative.year" AS year, COUNT(*) AS no_labor_capacity_count FROM households WHERE "administrative.district" ILIKE \'%Đắk Mil%\' AND "classify" = \'Hộ nghèo\' AND "family.hasNoLaborCapacity" = true AND "administrative.year" IN (2023, 2024) GROUP BY year ORDER BY year;'
        },
        {
            "id": 8,
            "question": "đăk glong 2024 có bn hộ nghèo cần hỗ trợ về y tế và giáo dục?",
            "gt_sql": 'SELECT SUM(CASE WHEN "support.health" = true THEN 1 ELSE 0 END) AS need_health_support, SUM(CASE WHEN "support.education" = true THEN 1 ELSE 0 END) AS need_edu_support FROM households WHERE "administrative.district" ILIKE \'%Đăk Glong%\' AND "classify" = \'Hộ nghèo\' AND "administrative.year" = 2024;'
        },
        {
            "id": 9,
            "question": "huyện nào có nhiều hộ nghèo bị ốm đau tai nạn nhất năm 2024?",
            "gt_sql": 'SELECT "administrative.district" AS district, COUNT(*) AS illness_count FROM households WHERE "classify" = \'Hộ nghèo\' AND "reason.illnessOrAccident" = true AND "administrative.year" = 2024 GROUP BY district ORDER BY illness_count DESC;'
        },
        {
            "id": 10,
            "question": "check xem cư jút 2024 có bn hộ nghèo thiếu nước sạch vs nhà vệ sinh",
            "gt_sql": 'SELECT SUM(CASE WHEN "deprivation.cleanWater" = true THEN 1 ELSE 0 END) AS lack_clean_water, SUM(CASE WHEN "deprivation.hygienicToilet" = true THEN 1 ELSE 0 END) AS lack_toilet FROM households WHERE "administrative.district" ILIKE \'%Cư Jút%\' AND "classify" = \'Hộ nghèo\' AND "administrative.year" = 2024;'
        }
    ]

    semantic_layer_path = PROJECT_ROOT / "data" / "Processed" / "metadata" / "query_control" / "semantic_layer.json"
    db_path = PROJECT_ROOT / "data" / "Processed" / "intern_chatbot.duckdb"

    cache_mgr = SemanticCacheManager()
    schema_linker = SchemaLinker(semantic_layer_path)
    sql_gen = SQLGenerator()
    sql_refiner = SQLRefiner(db_path)
    conn = duckdb.connect(str(db_path))

    # Step 1: Pre-evaluate cache scores and 2 SQL generation states for each query
    eval_results = []
    print("\n--- STEP 1: Đánh giá độ tương đồng Qdrant & Test sinh SQL ---")
    
    for item in test_queries:
        q_id = item["id"]
        q_text = item["question"]
        print(f"\n[Câu {q_id}] {q_text}")
        
        # Search vector DB with threshold=0.0 to find top score and template
        similar = cache_mgr.search_similar_questions(q_text, threshold=0.0)
        top_score = 0.0
        top_template = None
        if similar:
            top_score = similar[0]["score"]
            top_template = similar[0]
            print(f"   -> Top Similar Score: {top_score:.4f} | Old Q: '{top_template['question']}'")
        else:
            print("   -> No similar items found in Qdrant.")

        # Base schema info
        schema_info_base = schema_linker.link(q_text)

        # Helper to test SQL execution
        def test_sql_state(schema_info):
            try:
                gen_sql = sql_gen.generate(q_text, schema_info)
                # Test execution
                cur = conn.cursor()
                cur.execute(gen_sql)
                rows = cur.fetchall()
                return True, gen_sql, len(rows)
            except Exception as e:
                # Try refiner once if failed
                try:
                    df, refined_sql = sql_refiner.execute_and_refine(gen_sql, q_text, schema_info)
                    if df is not None:
                        return True, refined_sql, len(df)
                except Exception:
                    pass
                return False, gen_sql, str(e)

        # Run State B: MISS (No template hint)
        success_miss, sql_miss, res_miss = test_sql_state(dict(schema_info_base))
        print(f"   [State MISS - No Template] Success: {success_miss}")

        # Run State A: HIT (With template hint)
        success_hit, sql_hit, res_hit = False, "", ""
        if top_template:
            info_hit = dict(schema_info_base)
            info_hit["similar_sql_template"] = {
                "old_q": top_template["question"],
                "old_sql": top_template["sql"]
            }
            success_hit, sql_hit, res_hit = test_sql_state(info_hit)
            print(f"   [State HIT - With Template] Success: {success_hit}")

        eval_results.append({
            "id": q_id,
            "top_score": top_score,
            "success_miss": success_miss,
            "success_hit": success_hit
        })

    # Step 2: Sweep thresholds
    print("\n" + "="*80)
    print("--- STEP 2: THỐNG KÊ HIỆU QUẢ THEO TỪNG NGƯỠNG THRESHOLD ---")
    print("="*80)
    thresholds = [0.75, 0.80, 0.85, 0.88, 0.90, 0.92, 0.94, 0.96]
    
    summary_table = []
    print(f"{'Threshold':<12} | {'Hit Rate':<16} | {'Success Rate (Hit)':<22} | {'Overall Success':<18}")
    print("-" * 74)

    for T in thresholds:
        hit_count = 0
        hit_success = 0
        overall_success = 0

        for r in eval_results:
            if r["top_score"] >= T:
                hit_count += 1
                if r["success_hit"]:
                    hit_success += 1
                    overall_success += 1
            else:
                if r["success_miss"]:
                    overall_success += 1

        hit_rate_pct = (hit_count / len(eval_results)) * 100
        hit_succ_pct = (hit_success / hit_count * 100) if hit_count > 0 else 0.0
        overall_pct = (overall_success / len(eval_results)) * 100

        print(f"{T:<12.2f} | {hit_count}/10 ({hit_rate_pct:.0f}%)    | {hit_success}/{hit_count} ({hit_succ_pct:.0f}%)          | {overall_success}/10 ({overall_pct:.0f}%)")
        summary_table.append({
            "threshold": T,
            "hit_count": hit_count,
            "hit_rate": hit_rate_pct,
            "hit_success": hit_success,
            "hit_success_rate": hit_succ_pct,
            "overall_success": overall_success,
            "overall_success_rate": overall_pct
        })

    print("="*80)
    print("Hoàn tất benchmark!")

if __name__ == "__main__":
    run_benchmark()
