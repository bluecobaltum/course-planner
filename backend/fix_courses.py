"""Fix duplicates and normalize merged courses."""
import json

with open("data/courses.json", "r", encoding="utf-8") as f:
    courses = json.load(f)

print(f"Before: {len(courses)} courses")

# ── Better dedup: same group + same teacher name (fuzzy) → merge ──
seen = {}
deduped = []
for c in courses:
    group = c["credit_transfer_group"]
    tname = c.get("teacher", {}).get("name", "") if c.get("teacher") else ""

    # Find existing with same group and same/similar teacher name
    found = False
    for d in deduped:
        d_tname = d.get("teacher", {}).get("name", "") if d.get("teacher") else ""
        if d["credit_transfer_group"] == group:
            # Same teacher or one contains the other (刘德军 vs 刘德军,何俊)
            if tname and d_tname:
                if tname == d_tname or tname in d_tname or d_tname in tname:
                    # Merge schedule slots
                    existing_slots = {(s["day"], s["start"], s["end"]) for s in d["schedule"]}
                    for s in c["schedule"]:
                        key = (s["day"], s["start"], s["end"])
                        if key not in existing_slots:
                            d["schedule"].append(s)
                    found = True
                    break
    if not found:
        deduped.append(c)

print(f"After dedup: {len(deduped)} courses")

# ── Re-assign section IDs ──
counters = {}
for c in deduped:
    g = c["credit_transfer_group"]
    idx = counters.get(g, 0) + 1
    counters[g] = idx
    c["section_id"] = f"{g}-{idx:02d}"

# ── Fix schedules: dedup slots within each course ──
for c in deduped:
    seen_slots = set()
    fixed = []
    for s in sorted(c["schedule"], key=lambda x: (x["day"], x["start"])):
        key = (s["day"], s["start"], s["end"])
        if key not in seen_slots:
            seen_slots.add(key)
            fixed.append(s)
    c["schedule"] = fixed

# ── Print summary ──
print("\n=== Final Course Pool ===\n")
for g in sorted(set(c["credit_transfer_group"] for c in deduped)):
    secs = [c for c in deduped if c["credit_transfer_group"] == g]
    print(f"{g} ({len(secs)}个平行班):")
    for s in secs:
        t = s.get("teacher", {}) or {}
        slots = " ".join([f"周{x['day']}{x['start']}-{x['end']}节" for x in s["schedule"]]) if s["schedule"] else "异步"
        print(f"  {s['section_id']} | {s['course_name']} | {t.get('name','?')} | {slots} | {s['credits']}学分 | {s['course_type']}")

# ── Save ──
with open("data/courses.json", "w", encoding="utf-8") as f:
    json.dump(deduped, f, ensure_ascii=False, indent=2)

print(f"\n✅ courses.json: {len(deduped)} 门课程, {len(counters)} 个课程组")
