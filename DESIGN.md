# AI 智能选课助手 — Style Reference
> Warm Academic × AI Copilot. 像一位懂你的学长，不是冷冰冰的教务系统。

**Theme:** warm-dominant light (85% warm + 10% cool buoy + 5% neutral)

暖调学术是基调——图书馆的金色阳光、纸张的乳白、墨迹的深沉。但纯暖色调容易「糊」：所有元素融化在同一温度里，失去视觉张力。所以我们在温暖的海洋中投放了几个**冷色浮标**——微小的 teal 锚点，像导航灯一样引导视线。冷暖之间的对话让两种温度都更加鲜活。

---

## 色彩哲学：暖海 + 冷浮标

```
暖调基底（~85%）
  ████████████████████████████████████████  Golden Hour → Warm Cream → Paper White
  ████████████████████████████████████████  Ink Black 文字，Amber Glow 强调

冷色浮标（~5%）
  ██  Teal 点缀——策略区块标题、课表月亮标记（仅两处，宁少勿多）

暖调轻绿（~5%）
  ██  Lime 底色——水课行背景，暖绿 = 轻松摸鱼的快乐

中性（~5%）
  ██  Success Green / Danger Red / 纯粹的语义色
```

**为什么水课不用 teal？** 冷色天然带距离感和理性感，而水课在大学生语境里是轻松、低负担、"摸鱼的快乐"。冷色的心理预期和"快乐选修"是冲突的。反之，暖调轻绿（lime）在色轮上靠近 amber，自带暖底，同时绿色天然 = 放松、无压力——和水课的轻松感匹配。

**为什么策略/知识用 teal？** Amber (#f59e0b, H≈38°) 和 Teal (#0d9488, H≈175°) 在色轮上接近 split-complementary——冷暖对比最大化。策略区块作为「选课方法论」需要理性权威感，teal 的距离感在这里恰好是优势。同时 Teal + Amber 更少见、更有"旧图书馆绿玻璃台灯"的学术味。

---

## Tokens — Colors

### 暖调基底 (Warm Foundation)

| Name | Value | Token | Contrast | Role |
|------|-------|-------|----------|------|
| Ink Black | `#1c1917` | `--color-ink` | AAA (15:1) | 主文字色——暖黑，钢笔水感 |
| Deep Stone | `#57534e` | `--color-stone` | AA (6.2:1) | **辅助文字**——比旧版加深两档，确保暖白底上可读 |
| Soft Clay | `#78716c` | `--color-clay` | ~3.8:1 | **三级文字、占位符**——仅用于 ≥14px 的场景，小字禁用 |
| Paper White | `#ffffff` | `--color-paper` | — | 卡片表面色 |
| Warm Cream | `#fef7ed` | `--color-cream` | — | 次级表面、hover 背景、分区底色 |
| Golden Hour | `#fffbeb` | `--color-golden-hour` | — | 页面主背景 |
| Amber Glow | `#f59e0b` | `--color-amber` | — | **主强调色**。CTA、选中态、评分 |
| Amber Light | `#fbbf24` | `--color-amber-light` | — | 渐变辅助、hover 亮部 |
| Amber Dark | `#d97706` | `--color-amber-dark` | — | 深色强调、文字链接、按压态 |
| Warm Border | `#e7e5e4` | `--color-border` | — | 卡片边框、分割线 |

### 冷色浮标 (Cool Buoys)

| Name | Value | Token | Role |
|------|-------|-------|------|
| Teal Deep | `#0f766e` | `--color-teal` | 策略区块标题、图标焦点——理性、权威、方法论 |
| Teal Light | `#14b8a6` | `--color-teal-light` | teal 元素的 hover/渐变 |
| Teal Mist | `#f0fdfa` | `--color-teal-mist` | 策略卡片展开 detail 背景、teal 元素的微底色 |

> **浮标使用两原则：** ① 策略区块标题 + Brain 图标用 teal——全页唯一的冷色焦点区，和 amber 操作区形成冷暖对话；② 课表月亮标记用 teal-300 圆点——暗示夜晚的结束。最多两处，不再扩散。

### 暖调轻绿 (Warm Green — 水课专用)

| Name | Value | Token | Role |
|------|-------|-------|------|
| Lime Light | `#bef264` | `--color-lime` | 水课圆点、标签、高亮 |
| Lime Mist | `#f7fee7` | `--color-lime-mist` | **水课（easy）行底色**——暖绿，轻松，无压力 |

> 水课用暖绿而非冷绿：lime 在色轮上靠近 amber，自带暖底，同时绿色天然 = 放松、自然、无负担。和大学生"水课摸鱼"的心理预期吻合——这是快乐的绿色，不是理性的绿色。专业课是 amber（暖，重要），水课是 lime（暖绿，轻松），二者同暖但语义分层。

### 语义色 (Semantic)

| Name | Value | Token | Role |
|------|-------|-------|------|
| Success | `#10b981` | `--color-success` | 成功/正面指标 |
| Warning | `#f59e0b` | `--color-warning` | 警告标签 |
| Danger | `#ef4444` | `--color-danger` | 错误/删除 |

### 渐变 & 光晕 (Gradients & Glows)

| Name | Value | Usage |
|------|-------|-------|
| Page Gradient | `linear-gradient(180deg, #fffbeb 0%, #fef7ed 40%, #fefce8 100%)` | body 全局背景 |
| Hero Glow | `radial-gradient(ellipse 80% 60% at 50% 20%, rgba(251,191,36,0.10) 0%, transparent 60%)` | Hero 顶部光晕 |
| Text Gradient | `linear-gradient(135deg, #d97706 0%, #f59e0b 40%, #fbbf24 100%)` | 标题关键字渐变 |
| Teal Accent | `rgba(13, 148, 136, 0.15)` | teal 浮标微光 |

---

## Tokens — Typography

### 字体策略

中文为主，面向大学生。零外部依赖，系统字体栈保证一致体验。

```
--font-sans: "Noto Sans SC", "Source Han Sans SC", "PingFang SC",
             "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
--font-mono: "JetBrains Mono", "SF Mono", "Cascadia Code", monospace;
```

**字重**: 400 (regular), 500 (medium), 600 (semibold), 700 (bold), 800 (extrabold)

### Type Scale

| Role | Size | Weight | Line Height | Usage |
|------|------|--------|-------------|-------|
| caption / tag | 10px | 500 | 1.6 | 标签、Badge、场景提示 |
| body-xs | 12px | 400 | 1.5 | 辅助文字、图表标注——仅用 Deep Stone |
| body-sm | 14px | 400 | 1.5 | 正文、课程信息——仅用 Deep Stone |
| body | 16px | 400 | 1.5 | Hero 副标题、卡片描述 |
| subheading | 18px | 600 | 1.4 | 小标题 |
| heading-sm | 20px | 700 | 1.35 | 方案卡片标题 |
| heading | 28px | 700 | 1.3 | 区块标题 |
| heading-lg | 36px | 800 | 1.2 | Hero 标题（mobile） |
| display | 48px | 800 | 1.15 | Hero 标题（desktop） |
| score | 32px | 800 | 1 | 综合评分数字 |

> **对比度规则：** body-sm 及以下的文字必须使用 Deep Stone (`#57534e`) 而非 Soft Clay (`#78716c`)，保证 WCAG AA（≥4.5:1）。Soft Clay 仅在 ≥14px 的非关键文字中使用。

### 文本渐变

```css
.text-gradient {
  background: linear-gradient(135deg, #d97706 0%, #f59e0b 40%, #fbbf24 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

---

## Tokens — Spacing & Shapes

**Base unit:** 4px · **Density:** comfortable

### Spacing Scale

| Name | Value | Usage |
|------|-------|-------|
| xs | 4px | 图标-文字间距 |
| sm | 8px | 紧密元素间距 |
| md | 12px | 卡片内元素间距 |
| lg | 16px | 组件间间距 |
| xl | 24px | 区块内间距 |
| 2xl | 32px | Section 间距 |
| 3xl | 48px | 大区块间距 |
| 4xl | 64px | Hero 上下间距 |

### Border Radius

| Element | Value |
|---------|-------|
| buttons | 16px (`rounded-2xl`) |
| cards | 16px (`rounded-2xl`) |
| scenario cards | 16px (`rounded-2xl`) |
| badges / tags | 100px (`rounded-full`) |
| input fields | 12px (`rounded-xl`) |
| tab switcher | 12px (`rounded-xl`) |
| icon containers | 12px (`rounded-xl`) |

### Shadows

暖调阴影——不是冷灰，而是带 amber 微光的温暖抬升。

| Name | Value | Usage |
|------|-------|-------|
| card-rest | `0 1px 3px rgba(28, 25, 23, 0.04)` | 卡片默认 |
| card-hover | `0 4px 24px rgba(245, 158, 11, 0.08), 0 1px 4px rgba(0,0,0,0.04)` | hover 抬升 |
| glow | `0 0 20px rgba(245, 158, 11, 0.15), 0 0 40px rgba(245, 158, 11, 0.06)` | 选中卡片光环 |
| glow-strong | `0 0 30px rgba(245, 158, 11, 0.22), 0 0 60px rgba(245, 158, 11, 0.08)` | 最佳方案高亮 |
| button | `0 4px 14px rgba(245, 158, 11, 0.25)` | CTA 按钮 |

### Layout

- **页面最大宽度:** `max-w-6xl` (1152px)
- **Section 间距:** 48px (`space-y-12`)
- **卡片内边距:** 24px (`p-6`)

---

## Components

### Scenario Card（场景选择卡片）

**Role:** 用户选择一个「大学生活方式」的入口。6 卡片，单选。

Paper White 背景，16px border-radius，20px 内边距。默认：Warm Border + card-rest。选中：Amber Border + glow + ring-1 amber/30。顶部 amber 渐变横条（framer-motion `layoutId="glowBar"` spring 动画）。图标容器 `bg-amber-50 text-amber-500`。底部权重预览 10px Deep Stone 文字。

### Primary CTA Button（生成按钮）

**Role:** 页面最重要的操作。

`from-amber-500 via-amber-400 to-amber-500` 渐变背景，白色 16px/600w 文字，`rounded-2xl px-10 py-5`。hover: `shadow-lg shadow-amber-200/50 scale-103`。CSS shimmer 光泽扫过。loading: 旋转 Loader2 + 轮播文案。

### Plan Card（方案卡片）

**Role:** 完整课表方案。Top Bar + Tab 切换器（课程 / 课表 / 分析）。

Paper White 背景，16px border-radius，24px 内边距。Rank-1 额外 amber 边框 + ring + glow + "最佳选择" Badge。

**Top Bar:** 排名徽章（amber 渐变，1 位 Trophy 图标其余数字）+ 标题 + 32px/800w amber 评分 + 三个快速指标（学分/天数/最早节次，桌面端显示）。

**Tab 切换器:** Warm Cream 底色三段分段控件，选中项白色浮起 + amber-dark 文字。

**Tab: 课程 —** 每门课一行：圆点 + 课名 + 模式 Badge + 教师/评分 + 时间 + 学分。专业课 `amber-50/amber-100` 底色，水课 `lime-50/lime-100` 底色——暖且轻的绿色，匹配"轻松摸鱼"的心理预期。底部显示匹配策略 Badge。

**Tab: 课表 —** 周视图网格，动态压缩空节次。**上午/下午分界线处：** amber 虚线 (`border-t-2 border-dashed border-amber-200/60`)，左侧周期列在分界线上方 1px 处有一个 6px 的 CSS 渐变圆（太阳符号，amber），分界线下方 1px 处有一个 6px 的 CSS teal 半圆（月亮符号）。线上课程 `border-dashed opacity-75`。

**Tab: 分析 —** 8 维度评分条 + 推荐理由卡片（`bg-amber-50/50 border-amber-100/50 rounded-xl p-4`），默认 3 条，可展开。

### Schedule Timeline Markers（太阳/月亮时间标记）

**Role:** 在课表左侧周期列中，以极微弱的符号暗示一天的节奏——早晨开始和夜晚结束。不是装饰，是「生活方式伴侣」定位的视觉锚点。

```
实现规格：
  - 太阳：CSS 6px 实心圆，amber-300 色，opacity 0.35
    位置：周期列第 1 节上方 2px
  - 月亮：CSS 6px 实心圆，teal-300 色，opacity 0.30
    位置：周期列最后 1 节下方 2px
  - 两者都不添加动画——静态、微妙、几乎 subluminal
  - 仅在课表实际渲染的周期范围内显示（动态压缩后仍然有效）
```

> 用户不会刻意注意到这两个点，但会无意识感知到「时间在课表里流动」——这是「大学生活方式」和「排课工具」在体验层面的分界线。

### Strategy Section（策略知识区块）

**Role:** 「AI 选课哲学」知识库。这是页面中**唯一的 teal 焦点区域**——和上方 amber 主色调形成冷暖对话。

区块标题的 Brain 图标使用 **Teal Deep** (`#0f766e`)，标题文字 `text-teal-700`。以此表明「策略知识」是不同的信息层级——不是操作区（amber），而是思考区（teal）。

策略卡片本身保持 Paper White，展开后的 detail 区域可用 `bg-teal-50/30` 做微弱的冷色区分。

### AI Free Input Placeholder（预留入口）

虚线边框 (`border-dashed border-amber-200/60`)，`bg-amber-50/30`，`rounded-xl`。MessageCircle 图标 amber-300，占位文字 Deep Stone，右侧「即将开放」pill: `bg-amber-100 text-amber-700` + Sparkles 图标。

### Score Bar（评分条）

左 80px 标签（12px Deep Stone）+ 中 100% 进度条（2px 高，amber/40 底）+ 右 32px 数值（12px mono）。绿 (≥8) / amber (6-8) / 橙 (4-6) / 红 (<4)。

### Easy Count Slider（水课滑块）

6 圆点 + 连接线水平排列。选中: Amber Glow + amber 阴影。未选中: Warm Border。两端标注「纯必修」「全加水课」（10px Deep Stone）。

### Loading Overlay（AI 推演遮罩）

Golden Hour 暖白 88% 遮罩。脉冲光环 (amber/20 + amber/10 scale 交替) + 🧠 + 6 条中文轮播 + 三点 + amber 渐变进度条。

### Tab Navigation（顶部导航）

白色毛玻璃 sticky 顶栏。三段按钮 + 图标。选中: `bg-amber-50/80 border-amber-200/50` + framer-motion layoutId。

---

## Do's and Don'ts

### ✅ Do
- 使用 Amber Glow 作为 CTA 和选中态主色，Teal 仅用于策略/知识区块和月亮标记（最多 2 处），Lime 用于水课底色
- 卡片阴影用 amber-tinted 暖影，营造「被阳光托起」的触感
- body-sm 及以下文字必须用 Deep Stone (`#57534e`)，保证 ≥6:1 对比度
- 标题 1-2 个关键词用 `text-gradient`，制造视觉记忆点
- AI 元素统一用 amber 系动画；知识/策略元素统一用 teal 系标记；水课统一用 lime 系标记
- 课表颜色按 `course_code` 分配，同一门课的不同班同色
- 太阳标记 amber 圆点、月亮标记 teal 圆点，保持 opacity ≤0.35——宁少勿多，接近 subliminal
- 大段空白用 Golden Hour / Warm Cream 填充，拒绝冷白

### ❌ Don't
- 不要用冷灰色调（gray-50/100/200），用 Warm Border / Deep Stone / Soft Clay
- 不要用纯黑 (`#000`)，始终用 Ink Black (`#1c1917`)
- 不要对大面积背景使用饱和色
- 不要使用蓝色/紫色系（indigo/purple/blue）——那是上一版
- 不要用荧光色或高饱和度色做课表色块——保持在 bg-*-50 级别
- **不要滥用 teal**——它是浮标，不是第二主色。最多出现在 2 处：策略区块标题（+ Brain 图标）、课表月亮标记
- 不要挤压垂直间距——Demo 需要呼吸感

---

## Elevation

| 层级 | 元素 | 效果 |
|------|------|------|
| 0 | 页面背景 | Golden Hour 暖白渐变，无阴影 |
| 1 | 默认卡片 | `card-rest` 极淡暖影 |
| 2 | Hover 卡片 | `card-lift` translateY(-2px) + 暖影增强 |
| 3 | 选中场景卡片 | `glow` amber 光环 + ring-1 |
| 4 | 最佳方案卡片 | amber 边框 + ring-1 + glow-strong + "最佳选择" Badge |
| 5 | CTA 按钮 | `shadow-lg shadow-amber-200/50` amber 光晕 |
| 6 | Loading Overlay | z-50，暖白半透明，阻断交互 |

---

## Imagery

零图片依赖，所有视觉 CSS 驱动：

- **Hero:** 径向渐变光晕 (amber 10% opacity) + warm 渐变底色 → 模拟天光
- **底纹:** radial-gradient 圆点网格 (48px, amber 4%) → 替代纯白
- **图标:** lucide-react 1.5-2px 描边。amber 选中，teal 知识，Deep Stone 默认
- **太阳/月亮:** 6px CSS 圆点，无动画，opacity ≤0.35
- **无摄影、无插画**——纯代码驱动

---

## Layout

单列居中 (`max-w-6xl`)，从上到下：

1. **Top Nav** — sticky 毛玻璃，三 Tab
2. **Hero** — 居中大标题 (text-gradient 关键词) + 副标题 + amber 脉冲指示灯
3. **Input Stack** — 场景网格 (3×2) → 水课滑块 → CTA → AI 输入预留
4. **Results** — 方案 A/B/C，每个含 Tab（课程/课表/分析）
5. **Strategy Footer** — **teal 焦点区**：Brain 图标 + 标题用 Teal Deep，卡片保持 Paper White

Section 间距 48px。不追求密度——Demo 需要 3 秒可扫。

---

## 暗色模式预留

所有 Token 使用语义化命名（`--color-ink` 而非 `--color-dark-text`），天然支持双模切换。当前所有变量定义在 `:root` 中（即 Light Mode），未来只需在下方添加：

```css
/* ── Dark Mode (future) ── */
[data-theme="dark"] {
  --color-ink: #f5f0e8;          /* warm light text on dark */
  --color-stone: #a8a29e;         /* muted but readable */
  --color-clay: #78716c;
  --color-paper: #1c1917;         /* inverted: ink becomes surface */
  --color-cream: #292524;         /* warm dark cream */
  --color-golden-hour: #1c1917;   /* dark background */
  --color-amber: #fbbf24;         /* brighten amber for dark bg */
  --color-teal: #2dd4bf;          /* brighten teal for dark bg */
  --color-teal-mist: #0d2b28;    /* dark teal tint */
  --color-border: #44403c;        /* warm dark border */
  --shadow-*: ...                  /* swap to glow-only, no dark shadows */
}
```

> 当前不做暗色模式实现——仅确保 Token 命名不锁定在亮色语境中。

---

## Agent Prompt Guide

```
Quick Color Reference:
  text primary:   #1c1917 (ink black, warm)
  text secondary: #57534e (deep stone, AA contrast)
  text tertiary:  #78716c (soft clay, ≥14px only)
  background:     #fffbeb → #fef7ed → #fefce8
  surface:        #ffffff (paper white)
  border:         #e7e5e4 (warm border)
  accent warm:    #f59e0b (amber glow)
  accent cool:    #0f766e (teal deep — buoys only, max 3 spots)
```

**Example Prompts:**
- *Primary CTA:* amber gradient bg, white 16px/600w text, rounded-2xl px-10 py-5, `shadow-lg shadow-amber-200/50`
- *Selected Scenario Card:* paper white, amber border, glow shadow, ring-1 amber/30, amber gradient top bar
- *Strategy Section header:* Brain icon + title in `text-teal-700`, the ONLY teal focus area on page
- *Course row (major):* `bg-amber-50/50 border-amber-100/50` | *(easy):* `bg-lime-50/50 border-lime-100/50`
- *Schedule timeline:* 6px CSS dots — amber sun above period 1, teal moon below last period, opacity ≤0.35

---

## Similar Brands

- **Linear** — 克制暗色 UI + 暖 accent，精准间距
- **Notion** — 温暖协作氛围，柔圆角 + 淡表面
- **Apple Health** — 暖色渐变的生命力语言
- **Vercel** — 极简几何 + 强对比 + 微小 accent

> 我们的位置：暖调学术 × 生活方式伴侣。暖但不糊、有冷浮标导航、有时间节奏感。AI 是金色的陪伴，不是紫色的自动化。

---

## Quick Start — Tailwind v4

```css
@import "tailwindcss";

/* ═══════════════════════════════════════════════════════════════
   Light Mode (current)
   ═══════════════════════════════════════════════════════════════ */
@theme {
  /* Warm Foundation */
  --color-ink: #1c1917;
  --color-stone: #57534e;
  --color-clay: #78716c;
  --color-paper: #ffffff;
  --color-cream: #fef7ed;
  --color-golden-hour: #fffbeb;
  --color-amber: #f59e0b;
  --color-amber-light: #fbbf24;
  --color-amber-dark: #d97706;
  --color-border: #e7e5e4;

  /* Cool Buoys */
  --color-teal: #0f766e;
  --color-teal-light: #14b8a6;
  --color-teal-mist: #f0fdfa;

  /* Warm Green (水课专用) */
  --color-lime: #bef264;
  --color-lime-mist: #f7fee7;

  /* Semantic */
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-danger: #ef4444;

  /* Radii */
  --radius-card: 16px;
  --radius-btn: 16px;
  --radius-tab: 12px;
  --radius-input: 12px;
  --radius-full: 100px;

  /* Fonts */
  --font-sans: "Noto Sans SC", "Source Han Sans SC", "PingFang SC",
               "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  --font-mono: "JetBrains Mono", "SF Mono", "Cascadia Code", monospace;
}

/* ═══════════════════════════════════════════════════════════════
   Dark Mode (future — reserved)
   ═══════════════════════════════════════════════════════════════ */
/*
[data-theme="dark"] {
  --color-ink: #f5f0e8;
  --color-stone: #a8a29e;
  --color-clay: #78716c;
  --color-paper: #1c1917;
  --color-cream: #292524;
  --color-golden-hour: #1c1917;
  --color-amber: #fbbf24;
  --color-teal: #2dd4bf;
  --color-teal-mist: #0d2b28;
  --color-lime: #a3e635;
  --color-lime-mist: #1a2e0a;
  --color-border: #44403c;
}
*/
```

---

> **版本:** v2.2 — Three-Temperature Palette  
> **上次更新:** 2026-05-30 — 水课底色从 teal 改为 lime（暖调轻绿）；teal 收敛至仅策略区块 + 月亮标记；新增暖/冷/轻三温区配色体系
