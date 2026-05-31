from dotenv import load_dotenv; load_dotenv()
import os, json, traceback
from openai import OpenAI

api_key = os.environ.get("OPENAI_API_KEY", "")
base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
client = OpenAI(api_key=api_key, base_url=base_url)

schedule_text = """周一: 物理1-2节  Python7-8节
周二: 高数11-14节
周五: 羽毛球3-4节"""

prompt = "你是课表评估助手，输出JSON。格式: {\"overall\":\"总体评价\",\"score\":7.5,\"pros\":[],\"cons\":[],\"suggestions\":[],\"best_for\":\"学生类型\"}。纯JSON，不写markdown。"

try:
    response = client.chat.completions.create(
        model="Qwen3.5-Flash",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": schedule_text},
        ],
        temperature=0.3, max_tokens=1024,
    )
    content = response.choices[0].message.content
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
    else:
        print("EMPTY response")
except Exception as e:
    traceback.print_exc()
