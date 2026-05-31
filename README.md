# AI 智能选课助手 v2.0

> 基于多维度评分与 OR-Tools 约束优化的智能课表生成系统 — Hackathon MVP

## 项目简介

AI 智能选课助手是一款面向大学生的智能选课工具。学生选择/描述偏好（如"不选早八""课表紧凑""准备实习"），系统通过 **Google OR-Tools CP-SAT 求解器** 生成 Top-3 最优课表方案，并提供多维度评分、AI 分析报告和可视化周课表。

### 核心功能

- **5 种预设场景** — 均衡模式 / 避开早八 / 紧凑课表 / 悠闲模式（最大化空闲日）/ 避开晚间课
- **AI 智能排课** — 接入大模型自由描述选课偏好（如"优先评分高的老师"），LLM 辅助选课
- **三套排课引擎** — 笛卡尔积评分（Legacy）/ OR-Tools 两阶段优化 / LLM 选课，通过环境变量切换
- **8 维度评分体系** — 空闲日、紧凑度、避开早八、避开晚间、课程分布等维度，各场景权重不同
- **课表可视化** — 周课表日历热力图，课程卡片展示教师/评分/时间/学分
- **课程导入** — 支持 Excel 批量导入、AI 自然语言录入、课表截图 OCR 识别
- **策略知识库** — 5 张"选课心法"策略卡片，教学生更聪明地选课
- **课程管理** — 课程数据的增删改查
- **深色/浅色模式** — Warm Academic 暖色学术主题，支持暗色切换

## 技术栈

| 层 | 技术 |
|---|---|
| **前端** | React 19 + TypeScript + Vite 8 + Tailwind CSS v4 + Framer Motion |
| **后端** | Python FastAPI + Pydantic v2 + Uvicorn |
| **排课引擎** | Google OR-Tools CP-SAT（两阶段优化） |
| **AI/LLM** | OpenAI SDK → AIPING API（Qwen3.5-27B / DeepSeek-V4-Flash） |
| **课程解析** | OpenPyXL（Excel）+ LLM 自然语言解析 |
| **部署** | Ubuntu 22.04 + Nginx + Alibaba Cloud ECS |

## 项目结构

```
├── backend/                     # FastAPI 后端
│   ├── main.py                  # 应用入口
│   ├── requirements.txt         # Python 依赖
│   ├── engine/                  # 核心算法层
│   │   ├── loader.py            # JSON 数据加载
│   │   ├── scorer.py            # 8 维度评分引擎
│   │   └── orchestrator.py      # Legacy 方案生成管线
│   ├── schedulers/              # 可插拔排课引擎
│   │   ├── base.py              # 抽象基类
│   │   ├── legacy_scheduler.py  # 笛卡尔积评分
│   │   ├── ortools_scheduler.py # OR-Tools 两阶段 CP-SAT
│   │   ├── llm_scheduler.py     # LLM 选课
│   │   └── scheduler_weights.py # 各场景惩罚权重
│   ├── services/                # 业务服务
│   │   ├── excel_parser.py      # Excel 课程解析
│   │   ├── llm_parser.py        # 自然语言解析
│   │   ├── image_parser.py      # 截图 OCR
│   │   ├── plan_evaluator.py    # LLM 方案评估
│   │   └── course_classifier.py # 课程类型自动分类
│   ├── routes/                  # API 路由
│   ├── models/                  # Pydantic 数据模型
│   ├── config/                  # 场景权重配置
│   └── data/                    # courses.json + strategies.json
│
├── frontend/                    # React 前端
│   └── src/
│       ├── pages/Home.tsx       # 主页面
│       ├── components/          # UI 组件
│       │   ├── ScenarioSelector.tsx  # 场景选择
│       │   ├── PlanCard.tsx          # 方案卡片
│       │   ├── ScheduleGrid.tsx      # 周课表
│       │   ├── ScoreBar.tsx          # 评分条
│       │   └── import/              # 课程导入
│       ├── api/                 # API 客户端
│       ├── types/               # TypeScript 类型
│       └── lib/                 # 主题等工具
│
├── 部署/                        # 部署脚本与配置
│   ├── deploy.sh                # 一键部署
│   ├── pack.sh                  # 打包上传
│   └── .env.template            # 环境变量模板
│
└── test/                        # 测试数据与脚本
```

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- npm 9+

### 后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（复制 .env 文件，填入 API Key）
# 编辑 .env，设置 OPENAI_API_KEY 等

# 启动服务（端口 8000）
uvicorn main:app --reload
```

### 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器（端口 5173）
npm run dev
```

浏览器打开 `http://localhost:5173` 即可使用。

## API 端点

| 方法 | 路径 | 说明 |
|---|---|---|
| `POST` | `/api/generate_schedule` | 生成 Top-3 课表方案 |
| `GET` | `/api/strategies` | 获取选课策略卡片 |
| `GET` | `/api/courses` | 查询课程列表 |
| `POST` | `/api/courses` | 添加课程 |
| `PUT` | `/api/courses/{id}` | 修改课程 |
| `DELETE` | `/api/courses/{id}` | 删除课程 |
| `POST` | `/api/import/excel` | Excel 导入课程 |
| `POST` | `/api/import/text` | AI 自然语言导入 |
| `POST` | `/api/import/image` | 截图 OCR 导入 |
| `GET` | `/api/health` | 健康检查 |

## 排课引擎

通过环境变量 `SCHEDULER` 切换引擎：

| 值 | 引擎 | 说明 |
|---|---|---|
| `ortools`（默认） | ORToolsScheduler | 两阶段 CP-SAT：Phase 1 最大化课程覆盖，Phase 2 最小化场景惩罚 |
| `legacy` | LegacyScheduler | 笛卡尔积穷举 + 逐方案评分 |
| `llm` | LLMScheduler | LLM 挑选课程组合，代码验证约束 |

## 评分维度

5 个活跃维度（每项得分 1.0–10.0），按场景权重加权：

| 维度 | 说明 |
|---|---|
| `free_days` | 空闲日数量 |
| `compactness` | 课表紧凑程度 |
| `no_morning` | 避开早八课程 |
| `no_night` | 避开晚间课程 |
| `distribution` | 课程在周内均匀分布 |

## 场景权重

| 场景 | free_days | compactness | no_morning | no_night | distribution |
|---|---|---|---|---|---|
| 均衡模式 | 0.25 | 0.25 | 0.20 | 0.15 | 0.15 |
| 避开早八 | 0.10 | 0.15 | **0.60** | 0.10 | 0.05 |
| 紧凑课表 | 0.05 | **0.65** | 0.15 | 0.10 | 0.05 |
| 悠闲模式 | **0.60** | 0.10 | 0.15 | 0.10 | 0.05 |
| 避开晚间 | 0.10 | 0.15 | 0.10 | **0.60** | 0.05 |

## 部署

详见 [部署/README.md](部署/README.md)，一键部署到 Alibaba Cloud ECS (Ubuntu 22.04 + Nginx)。

```bash
cd 部署
bash deploy.sh
```

## 作者

- **刘思昊** — 主要编写者

## License

MIT
