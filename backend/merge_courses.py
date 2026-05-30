"""
Merge 3 recognized course schedules into one unified courses.json.
Same course = same credit_transfer_group (parallel sections).
Same course + same teacher = deduplicate.
"""
import json, requests, time

SCREENSHOTS = [
    ("db3c678def95eed64e51c03c339d2535.png", "课表1"),
    ("2655a75908c149a05c6c157ba43f9a73.png", "课表2"),
    ("my_schedule (1).png", "课表3"),
]
BASE = "c:/Users/34356/Desktop/黑客松/test/截图"

all_courses: list[dict] = []

for fname, label in SCREENSHOTS:
    print(f"识别 {label}...")
    r = requests.post(
        "http://localhost:8000/api/import/image",
        files={"file": (fname, open(f"{BASE}/{fname}", "rb"), "image/png")},
        timeout=120,
    )
    d = r.json()
    if d.get("success"):
        all_courses.extend(d["courses"])
        print(f"  {d['stats']['course_count']} 门")
    else:
        print(f"  FAIL: {d.get('detail', '?')}")

print(f"\n原始: {len(all_courses)} 门课程")

# ── Normalize: fix schedule artifacts ──
for c in all_courses:
    for s in c.get("schedule", []):
        # Fix "start==end" (likely Day A-B where end was misread)
        if s["start"] == s["end"] and s["start"] <= 5:
            s["end"] = s["start"] * 2  # heuristic: 3→6, 4→8, 5→10
            if s["end"] > 14:
                s["end"] = s["start"] + 1
        # Fix inverted start/end
        if s["start"] > s["end"]:
            s["start"], s["end"] = s["end"], s["start"]
        # Clamp
        s["start"] = max(1, min(14, s["start"]))
        s["end"] = max(1, min(14, s["end"]))

# ── Deduplicate: same course_code + same teacher name → keep first ──
seen = set()
deduped = []
for c in all_courses:
    code = c.get("course_code", "")
    tname = c.get("teacher", {}).get("name", "") if c.get("teacher") else ""
    key = f"{code}|{tname}"
    if key not in seen:
        seen.add(key)
        deduped.append(c)
    else:
        # Merge schedule slots from duplicate
        existing = deduped[[d.get("course_code","")+"|"+ (d.get("teacher",{}).get("name","") if d.get("teacher") else "") for d in deduped].index(key)]
        existing_slots = {(s["day"], s["start"], s["end"]) for s in existing.get("schedule", [])}
        for s in c.get("schedule", []):
            if (s["day"], s["start"], s["end"]) not in existing_slots:
                existing["schedule"].append(s)

print(f"去重后: {len(deduped)} 门课程")

# ── Assign section_id and credit_transfer_group ──
COURSE_GROUPS = {
    "大学物理A": "PHYS101",
    "大学物理A（1）": "PHYS101",
    "大学物理实验": "PHYS103",
    "大学物理实验（1）": "PHYS103",
    "大学英语": "ENGL102",
    "大学英语（2）": "ENGL102",
    "高等数学A": "MATH102",
    "高等数学A（2）": "MATH102",
    "Python程序设计基础": "COMP102",
    "电路分析基础": "ELEC104",
    "中国近现代史纲要": "HIST104",
    "金工实习": "ENG17",
    "电磁场与电磁波": "ELEC201",
    "西方文化精要": "WEST101",
    "英语演讲：思辨与表达": "ENGL201",
    "马克思主义基本原理": "MARX101",
    "形势与政策": "POLI101",
    "羽毛球俱乐部": "CLUB01",
    "乒乓球俱乐部": "CLUB02",
    "男子篮球俱乐部": "CLUB03",
}

section_counters: dict[str, int] = {}

for c in deduped:
    name = c.get("course_name", "")
    group = COURSE_GROUPS.get(name, name[:6].upper())
    c["credit_transfer_group"] = group
    c["course_code"] = group
    idx = section_counters.get(group, 0) + 1
    section_counters[group] = idx
    c["section_id"] = f"{group}-{idx:02d}"

    # Classify: 俱乐部/体育类 → easy, rest → major
    if any(kw in name for kw in ["俱乐部", "体育", "文化", "演讲", "形势"]):
        c["course_type"] = "easy"
    else:
        c["course_type"] = "major"

    # Default credits if missing
    if not c.get("credits") or c["credits"] <= 0:
        if c["course_type"] == "easy":
            c["credits"] = 1
        elif any(kw in name for kw in ["实验", "实习", "纲要", "原理"]):
            c["credits"] = 2
        else:
            c["credits"] = 4

# ── Save ──
out = "c:/Users/34356/Desktop/黑客松/backend/data/courses.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(deduped, f, ensure_ascii=False, indent=2)

print(f"\n保存到 courses.json: {len(deduped)} 门课程")
for g in sorted(set(c["credit_transfer_group"] for c in deduped)):
    sections = [c for c in deduped if c["credit_transfer_group"] == g]
    print(f"  {g} ({len(sections)}个班): {[s['course_name']+' - '+ (s.get('teacher',{}).get('name','?') if s.get('teacher') else '?') for s in sections]}")
