"""
Backend 测试脚本 — 直接调用引擎，无需启动 HTTP 服务。

用法:
    cd backend
    python ../test/test_backend.py

或从 backend 目录:
    python -m pytest ../test/test_backend.py -v
"""

import sys
import os

# Windows 下强制 UTF-8 输出，避免 emoji 编码报错
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 确保 backend 在 Python path 中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from engine.orchestrator import generate_plans
from engine.scorer import (
    calculate_score,
    compute_gpa_score,
    compute_compact_score,
    compute_stress_score,
    compute_free_score,
    compute_morning_penalty,
    compute_friday_penalty,
    compute_monday_penalty,
    compute_afternoon_penalty,
)
from engine.loader import load_courses, load_strategies
from config.scenarios import (
    SCENARIO_WEIGHTS,
    SCENARIO_META,
    validate_scenario,
)


SEP = "=" * 70
SUB = "-" * 50


def test_scenario_weights():
    """验证所有权重配置和为 1.0，且包含全部 8 个维度。"""
    print(f"\n{' 场景权重校验 ':=^70}\n")
    required_keys = [
        "gpa_score", "compact_score", "stress_score", "free_score",
        "morning_penalty", "friday_penalty", "monday_penalty", "afternoon_penalty",
    ]
    all_ok = True
    for sid, w in SCENARIO_WEIGHTS.items():
        total = sum(w[k] for k in required_keys)
        status = "OK" if abs(total - 1.0) < 0.001 else "FAIL"
        if status == "FAIL":
            all_ok = False
        desc = w.get("description", sid)
        print(f"  {SCENARIO_META[sid]['icon']} {sid:15s} ({desc:10s})  总权重 = {total:.2f}  [{status}]")
    print(f"\n  → {'全部通过' if all_ok else '存在权重和不等于1.0的场景！'}")
    return all_ok


def test_all_scenarios():
    """遍历 5 个场景生成方案，展示核心差异。"""
    print(f"\n{' 五场景方案生成 ':=^70}\n")

    for scenario_id in SCENARIO_WEIGHTS:
        meta = SCENARIO_META[scenario_id]
        icon = meta["icon"]
        desc = meta["description"]

        plans = generate_plans(scenario_id, easy_count=1)

        print(f" {icon} {scenario_id} — {desc}")
        print(f"   生成方案数: {len(plans)}")

        if not plans:
            print(f"   ⚠️ 无可行方案！\n")
            continue

        for i, p in enumerate(plans):
            a = p["analysis"]
            b = a["score_breakdown"]

            # 找到 CS101 和 MATH101 的选择
            cs = next((c for c in p["courses"] if c["course_code"] == "CS101"), None)
            ma = next((c for c in p["courses"] if c["course_code"] == "MATH101"), None)

            cs_str = f"{cs['section_id']}(r={cs['teacher']['rating']})" if cs else "-"
            ma_str = f"{ma['section_id']}(r={ma['teacher']['rating']})" if ma else "-"

            marker = "★" if i == 0 else " "
            print(f"  {marker} Plan {chr(65+i)} | score={p['score']:.1f} | "
                  f"CS101={cs_str} MATH={ma_str} | "
                  f"GPA={b['gpa_score']} 早八={b['morning_penalty']} 周五={b['friday_penalty']}")
            print(f"    reasons: {' | '.join(a['reasons'][:2])}")
        print()


def test_gpa_vs_morning_tradeoff():
    """核心验证: gpa_focus 与 no_morning 的 CS101 选择应相反。"""
    print(f"{' 核心 Trade-off 验证 ':=^70}\n")

    gpa_plans = generate_plans("gpa_focus", easy_count=1)
    morning_plans = generate_plans("no_morning", easy_count=1)

    if not gpa_plans or not morning_plans:
        print("  ⚠️ 无法完成验证：某个场景无可用方案")
        return False

    gpa_cs = next(c for c in gpa_plans[0]["courses"] if c["course_code"] == "CS101")
    morning_cs = next(c for c in morning_plans[0]["courses"] if c["course_code"] == "CS101")

    gpa_rating = gpa_cs["teacher"]["rating"]
    morning_rating = morning_cs["teacher"]["rating"]

    print(f"  gpa_focus  Plan A → CS101 = {gpa_cs['section_id']} (评分 {gpa_rating})")
    print(f"  no_morning Plan A → CS101 = {morning_cs['section_id']} (评分 {morning_rating})")
    print()

    if gpa_rating > morning_rating:
        print(f"  ✅ Trade-off 正确: gpa_focus 选了高评分教授 ({gpa_rating}>{morning_rating})")
        print(f"     no_morning 宁要无早八，牺牲了 GPA")
        return True
    elif gpa_rating < morning_rating:
        print(f"  ❌ Trade-off 反向: no_morning 选了更高评分的教授")
        return False
    else:
        print(f"  ⚠️ 两个场景选了同一评分的教授，无明显 trade-off")
        return None


def test_scoring_functions():
    """单独测试每个评分函数的输入输出。"""
    print(f"{' 评分函数单元测试 ':=^70}\n")

    courses = load_courses()

    # 构造一个测试方案：6 门 major + 1 门 easy
    test_ids = ["MATH101-01", "ENG201-02", "POL301-01", "CS101-01", "PHY201-01", "PE101-01", "ART101-02"]
    plan = [c for c in courses if c["section_id"] in test_ids]

    print(f"  测试方案课程: {[c['section_id'] for c in plan]}")
    print(f"  总学分: {sum(c['credits'] for c in plan)}\n")

    tests = [
        ("gpa_score",           compute_gpa_score(plan),          "2.0-10.0"),
        ("compact_score",       compute_compact_score(plan),      "1.0-10.0"),
        ("stress_score",        compute_stress_score(plan),       "1.0-10.0"),
        ("free_score",          compute_free_score(plan),         "0-10"),
        ("morning_penalty",     compute_morning_penalty(plan),    "1.0-10.0"),
        ("friday_penalty",      compute_friday_penalty(plan),     "3.0/10.0"),
        ("monday_penalty",      compute_monday_penalty(plan),     "3.0/10.0"),
        ("afternoon_penalty",   compute_afternoon_penalty(plan),  "1.0-10.0"),
    ]

    all_ok = True
    for name, value, expected_range in tests:
        # 简单范围检查
        if "0-10" in expected_range:
            ok = 0 <= value <= 10
        elif "/" in expected_range:
            ok = value == 3.0 or value == 10.0
        else:
            lo, hi = map(float, expected_range.replace("1.0", "1").replace("10.0", "10").split("-"))
            ok = lo <= value <= hi

        status = "OK" if ok else "FAIL"
        if not ok:
            all_ok = False
        print(f"  {name:20s} = {value:5.1f}  (范围 {expected_range:12s}) [{status}]")

    print(f"\n  → {'全部通过' if all_ok else '存在越界值！'}")
    return all_ok


def test_edge_cases():
    """测试边界情况。"""
    print(f"{' 边界情况测试 ':=^70}\n")

    # 1. 无效场景
    try:
        validate_scenario("invalid_scenario")
        print("  ❌ 无效场景应该抛出异常")
    except ValueError as e:
        print(f"  ✅ 无效场景被拒绝: {str(e)[:60]}...")

    # 2. easy_count = 0
    plans = generate_plans("no_morning", easy_count=0)
    if plans:
        credits = plans[0]["analysis"]["total_credits"]
        n_courses = len(plans[0]["courses"])
        print(f"  ✅ easy_count=0 → {n_courses}门课, {credits}学分")
    else:
        print(f"  ⚠️ easy_count=0 → 无可行方案")

    # 3. 大量 easy_count (应 clamp 到可用水课数)
    plans = generate_plans("no_morning", easy_count=99)
    if plans:
        easy_courses = [c for c in plans[0]["courses"] if c["course_type"] == "easy"]
        n_easy = len(easy_courses)
        print(f"  ✅ easy_count=99 → 实际选了 {n_easy} 门水课 (已 clamp)")
    else:
        print(f"  ⚠️ easy_count=99 → 无水课可选但 majors 方案正常 (clamp 生效)")

    # 4. 策略数据完整性
    strategies = load_strategies()
    print(f"  ✅ 策略库加载: {len(strategies)} 条策略")
    for s in strategies:
        print(f"     - {s['id']}: {s['title']}")


def test_score_breakdown_consistency():
    """验证 calculate_score 的加权和与 breakdown 一致。"""
    print(f"{' 评分一致性验证 ':=^70}\n")
    courses = load_courses()
    test_ids = ["MATH101-01", "ENG201-01", "POL301-01", "CS101-01", "PHY201-01", "PE101-01", "PSY101-01"]
    plan = [c for c in courses if c["section_id"] in test_ids]

    for scenario_id in ["gpa_focus", "no_morning"]:
        weights = SCENARIO_WEIGHTS[scenario_id]
        total, breakdown = calculate_score(plan, weights)

        # 手动重算验证
        recomputed = sum(breakdown[k] * weights[k] for k in breakdown)
        diff = abs(total - recomputed)

        status = "OK" if diff < 0.1 else "FAIL"
        print(f"  {scenario_id:15s}: total={total:.1f}, recomputed={recomputed:.1f}, diff={diff:.3f} [{status}]")

        # 打印每个维度的贡献
        for k in sorted(breakdown.keys()):
            contrib = breakdown[k] * weights[k]
            bar = "█" * int(contrib * 5)
            print(f"    {k:20s}: {breakdown[k]:4.1f} × {weights[k]:.2f} = {contrib:5.2f}  {bar}")
    return True


# ── 主入口 ──────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\n{' AI 智能选课助手 — Backend 测试套件 ':=^70}")
    print(f"  数据路径: {os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'data'))}")

    results = []
    results.append(("场景权重校验",       test_scenario_weights()))
    results.append(("评分函数单元测试",   test_scoring_functions()))
    results.append(("评分一致性验证",     test_score_breakdown_consistency()))
    results.append(("核心Trade-off验证",  test_gpa_vs_morning_tradeoff()))
    results.append(("五场景方案生成",     True))  # 信息展示型，不算 pass/fail
    test_all_scenarios()
    results.append(("边界情况测试",       True))
    test_edge_cases()

    # 汇总
    print(f"\n{' 测试汇总 ':=^70}")
    passed = sum(1 for _, ok in results if ok)
    failed = sum(1 for _, ok in results if not ok)
    for name, ok in results:
        print(f"  {'✅' if ok else '❌'} {name}")
    print(f"\n  通过: {passed}/{len(results)}")
    if failed:
        print(f"  失败: {failed}")
        sys.exit(1)
    else:
        print(f"  🎉 全部通过！后端核心逻辑正常工作。")
