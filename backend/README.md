# AI 智能选课助手 — Backend

基于多维度评分的智能课表生成系统。Hackathon MVP 版本。

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动服务
uvicorn main:app --reload

# 3. 验证
curl http://localhost:8000/api/health
```

## API

### POST /api/generate_schedule

生成 Top-3 课表方案。

```bash
curl -X POST http://localhost:8000/api/generate_schedule \
  -H "Content-Type: application/json" \
  -d '{"scenario": "no_morning", "easy_count": 1}'
```

**预设方案**: `no_morning` | `long_weekend` | `morning_only` | `easy_mode` | `gpa_focus`

**水课数量**: `easy_count` = 0~5（默认 1）

### GET /api/strategies

获取科学选课策略。

```bash
# 全部策略
curl http://localhost:8000/api/strategies

# 按方案过滤
curl http://localhost:8000/api/strategies?scenario=no_morning
```

### GET /api/health

健康检查。

## 项目结构

```
backend/
├── main.py              # FastAPI 入口
├── requirements.txt
├── models/              # Pydantic 数据模型
│   ├── course.py        #   课程、教师、时间槽
│   ├── strategy.py      #   策略卡片
│   ├── schedule.py      #   评分、方案、分析
│   └── response.py      #   API 请求/响应
├── config/
│   └── scenarios.py     # 预设方案权重配置
├── engine/              # 核心算法
│   ├── loader.py        #   数据加载
│   ├── orchestrator.py  #   方案生成流水线
│   └── scorer.py        #   8维度评分 + 理由 + 策略匹配
├── routes/              # API 路由
│   ├── schedule.py      #   POST /generate_schedule
│   └── strategies.py    #   GET /strategies
└── data/                # Mock 数据
    ├── courses.json     #   21 门课程
    └── strategies.json  #   5 条策略
```

## 评分维度

| 维度 | 含义 | 范围 |
|------|------|------|
| gpa_score | 教师评分均值 × 2 | 2.0-10.0 |
| compact_score | 课程时间集中度 | 1.0-10.0 |
| stress_score | 学分压力 | 1.0-10.0 |
| free_score | 完整空闲半天数 | 0-10 |
| morning_penalty | 早八惩罚（无早八=10） | 1.0-10.0 |
| friday_penalty | 周五惩罚（周五空=10） | 3.0/10.0 |
| monday_penalty | 周一惩罚（周一空=10） | 3.0/10.0 |
| afternoon_penalty | 下午惩罚（无下午=10） | 1.0-10.0 |

所有维度方向一致（越高越好），按场景权重加权求和。

## 技术栈

- **FastAPI** — Web 框架
- **Pydantic v2** — 数据校验
- **Uvicorn** — ASGI 服务器
- **零数据库依赖** — Demo 阶段读 JSON 文件
