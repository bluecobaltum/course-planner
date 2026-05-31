from dotenv import load_dotenv; load_dotenv()
import os, json, sys, traceback
from openai import OpenAI
from services.plan_evaluator import (
    SYSTEM_PROMPT, _format_plan_for_llm, _get_client, evaluate_plan,
)

# Test with minimal plan
plan = {"courses": []}
courses_json = json.load(open("data/courses.json", "r", encoding="utf-8"))
plan["courses"] = courses_json[:3]

msg = _format_plan_for_llm(plan)
print(f"Message length: {len(msg)}")
print(f"Message:\n{msg}")

combined = SYSTEM_PROMPT + "\n\n" + msg
print(f"\nCombined length: {len(combined)}")
print(f"Combined:\n{combined}")

try:
    client = _get_client()
    response = client.chat.completions.create(
        model="Qwen3.5-Flash",
        messages=[{"role": "user", "content": combined}],
        temperature=0.3, max_tokens=2048,
    )
    content = response.choices[0].message.content
    print(f"\nAPI response length: {len(content) if content else 0}")
    if not content:
        print("EMPTY response from API")
        print("Usage:", response.usage)
    else:
        print("Content:", content[:300])
except Exception as e:
    traceback.print_exc(file=sys.stdout)
