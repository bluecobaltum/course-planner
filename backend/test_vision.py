import os, base64, json
from dotenv import load_dotenv; load_dotenv()
from openai import OpenAI

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'], base_url=os.environ['OPENAI_BASE_URL'])

img = 'c:/Users/34356/Desktop/黑客松/test/截图/db3c678def95eed64e51c03c339d2535.png'
with open(img, 'rb') as f:
    b64 = base64.b64encode(f.read()).decode()

print(f'Image: {len(b64)} chars base64')

prompt = """你是大学课表解析器。识别图片中的所有课程，输出严格 JSON 数组。
每门课格式：
{
  "section_id": "课程代码-01",
  "course_code": "MATH101",
  "course_name": "课程名",
  "credit_transfer_group": "MATH101",
  "credits": 3,
  "teacher": {"name": "教师名", "rating": 4.0},
  "schedule": [{"day": 1, "start": 1, "end": 2}],
  "location": {"building": "教学楼", "floor": 1, "room": "101"},
  "course_type": "major",
  "delivery_mode": "线下传统",
  "semester": "2025-2026-2"
}
规则：
- day: 1=周一..5=周五
- start/end: 上午=1-5节, 下午=6-10节, 晚上=11-14节
- course_type: major=专业课, easy=选修/水课
- 教师评分默认4.0，未标注教师则teacher为null
- 无教室信息则location为null
- 输出纯JSON，不要markdown代码块，不要解释文字"""

r = client.chat.completions.create(
    model='Qwen2.5-VL-72B-Instruct',
    messages=[{'role':'user','content':[
        {'type':'image_url','image_url':{'url':f'data:image/png;base64,{b64}'}},
        {'type':'text','text':prompt}
    ]}],
    max_tokens=4096, temperature=0.1
)
raw = r.choices[0].message.content.strip()
print(f'Response: {len(raw)} chars')

# Strip markdown if present
if raw.startswith('```'):
    lines = raw.split('\n')
    raw = '\n'.join(lines[1:])
    if raw.endswith('```'):
        raw = raw[:-3]
    raw = raw.strip()

try:
    data = json.loads(raw)
    if isinstance(data, dict):
        data = data.get('courses', [data])
    print(f'Parsed {len(data)} courses:')
    for c in data:
        name = c.get('course_name', '?')
        teacher = c.get('teacher', {})
        tname = teacher.get('name', '?') if teacher else 'None'
        schedule = c.get('schedule', [])
        print(f'  {name} | teacher={tname} | slots={len(schedule)}')
        for s in schedule:
            print(f'    周{s["day"]} {s["start"]}-{s["end"]}节')
except Exception as e:
    print(f'Parse failed: {e}')
    print('Raw:', raw[:600])
