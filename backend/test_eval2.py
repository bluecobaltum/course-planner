from dotenv import load_dotenv; load_dotenv()
import os, json, traceback, sys
from openai import OpenAI
from services.plan_evaluator import SYSTEM_PROMPT, _format_plan_for_llm

api_key = os.environ.get("OPENAI_API_KEY", "")
base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
client = OpenAI(api_key=api_key, base_url=base_url)

plan = {"courses": json.load(open("data/courses.json", "r", encoding="utf-8"))[:5]}
schedule_text = _format_plan_for_llm(plan)

try:
    response = client.chat.completions.create(
        model="Qwen3.5-Flash",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": schedule_text},
        ],
        temperature=0.3, max_tokens=1024,
    )
    content = response.choices[0].message.content
    print("Content len:", len(content) if content else 0)
    if content:
        content = content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:])
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
        r = json.loads(content)
        print("Score:", r.get("score"))
        print("Overall:", r.get("overall", "?")[:80])
        print("Pros:", r.get("pros", []))
    else:
        print("EMPTY")
except Exception as e:
    traceback.print_exc(file=sys.stdout)
