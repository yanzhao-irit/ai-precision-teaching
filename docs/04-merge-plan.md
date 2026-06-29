# 项目合并方案 · Project Merge Plan

> **目的 · Purpose:**
> 把两位同学的原型（master 分支的成绩看板 + prototype 分支的错因诊断）合并成一个
> 完整系统，并确保覆盖申报书里的**全部**教改内容。
>
> Merge the two student prototypes (the analytics dashboard on `master` and the
> error-diagnosis engine on `ai-teaching-prototype`) into one complete system, and
> ensure it covers **all** the teaching-reform content in the project proposal.

---

## 目录 · Table of Contents

1. [现状盘点 · Current State](#sec-1)
2. [教改目标全清单对照 · Full Mapping to Reform Goals](#sec-2)
3. [目标技术架构 · Target Architecture](#sec-3)
4. [保留与合并清单 · Keep & Merge List](#sec-4)
5. [模块详细需求 · Detailed Module Requirements](#sec-5)
6. [分阶段实施 · Phased Implementation](#sec-6)
7. [给学生的任务说明 · Task Brief for Students](#sec-7)


---

<a name="sec-1"></a>
## 1. 现状盘点 · Current State

**中文：** 两位同学按各自理解做了两个原型，方向不同、各有所长。

**English:** The two students built two prototypes based on their own understanding—different directions, each with strengths.

| 维度 · Aspect | master 分支（成绩看板）· Analytics Dashboard | prototype 分支（错因诊断）· Diagnosis Engine |
|---|---|---|
| 定位 · Focus | 学生成绩追踪 + 课程浏览 · Student tracking + course browsing | 错因诊断（贴合申报书核心）· Error diagnosis (matches proposal core) |
| 前端 · Frontend | Streamlit 多页应用 · Streamlit multi-page | 原生 HTML/CSS/JS · Vanilla HTML/CSS/JS |
| 数据 · Data | 随机生成的模拟成绩 · Randomly generated scores | 合成答题 + 真实 AI 知识图谱 · Synthetic answers + real AI KG |
| 知识图谱 · KG | 初等数学（偏题）· Elementary math (off-topic) | 15 个 AI 概念 + 14 条前置关系 · 15 AI concepts + 14 prerequisites |
| 核心价值 · Core value | UI 精美、图谱交互强 · Polished UI, strong graph interaction | **真正实现前置回溯诊断** · **Real prerequisite-traceback diagnosis** |
| 诊断能力 · Diagnosis | ❌ 无 · None | ✅ 有（规则 + 图推理 + 可解释报告）· Yes (rules + graph reasoning + explainable reports) |

**核心判断 · Key judgment:**

**中文：** prototype（诊断）抓住了项目灵魂，master（看板）UI 和资源浏览是亮点但内容偏题。合并方向是：**以诊断为内核，以看板为外壳，用真实数据和真实线性代数知识图谱替换模拟内容。**

**English:** The prototype (diagnosis) captures the project's soul; the master dashboard's UI and resource browsing are strong but off-topic in content. The merge direction: **diagnosis as the core, dashboard as the shell, with real data and a real Linear Algebra knowledge graph replacing the mock content.**


---

<a name="sec-2"></a>
## 2. 教改目标全清单对照 · Full Mapping to Reform Goals

> **这是整份文档最重要的部分。** 申报书的每一项内容都列在这里，标注现状和要做什么。
> **目标：最终系统覆盖申报书全部四大板块、四条链。**
>
> **This is the most important section.** Every item from the proposal is listed
> here with its status and what's needed.
> **Goal: the final system must cover all four modules and four chains.**

### 2.1 板块一 · 全程学习感知（数据链）· Module 1: Full-Process Sensing (Data Chain)

| 申报书要求 · Proposal Requirement | 现状 · Status | 要做什么 · What to Build |
|---|---|---|
| 三维评价"结果+过程+改进" · 3-D evaluation | ❌ 都没做 · Neither did it | 设计评价数据模型：课前预习/课中测验/课后作业/改进 · Design evaluation data model |
| 嵌入式数据采集（不增负担）· Embedded collection | ❌ 都用模拟数据 · Both used mock data | 从真实历史数据导入；设计采集字段 · Import real historical data; design fields |
| 学生×知识点×行为 三维数据 · 3-D data cube | ⚠️ prototype 有雏形（学生×题×对错）· prototype has a start | 扩展为完整三维结构 · Extend to full 3-D structure |
| 数据脱敏、分级授权 · Anonymization, access control | ❌ 都没做（甚至硬编码密码）· Neither (hardcoded passwords) | 用脱敏脚本 + .env 管理密钥 · Anonymization script + .env secrets |
| 轻量数据中台 · Lightweight data hub | ❌ 无 · None | PostgreSQL 存行为数据 + Neo4j 存图谱 · PostgreSQL for behavior + Neo4j for KG |

### 2.2 板块二 · 精准错因诊断（诊断链）· Module 2: Error Diagnosis (Diagnosis Chain)

| 申报书要求 · Proposal Requirement | 现状 · Status | 要做什么 · What to Build |
|---|---|---|
| 课程知识图谱（300+ 知识点）· KG with 300+ KPs | ⚠️ prototype 有 15 个 AI 概念；master 偏题 · prototype 15 AI concepts | 构建真实线性代数 KG（先前 3 章）· Build real Linear Algebra KG (Ch.1-3 first) |
| 知识点标注难度/误区/错误模式 · Annotate difficulty/misconceptions | ⚠️ 部分 · Partial | 补全 misconceptions + error patterns · Complete misconceptions + error patterns |
| 表层-深层-根因 三阶诊断 · 3-stage diagnosis | ✅ prototype 有（前置回溯）· prototype has it | 保留并强化 · Keep and strengthen |
| 规则推理 + 数据学习 + 图推理 · Rules + data learning + graph | ⚠️ prototype 有规则+图，缺数据学习 · rules+graph only | **加入 BKT 掌握度模型** · **Add BKT mastery model** |
| 贝叶斯知识追踪（三状态）· BKT (3-state) | ❌ 无 · None | 用 pyBKT 实现掌握度概率 · Use pyBKT for mastery probability |
| 可解释诊断报告（问题/原因/证据/建议）· Explainable report | ✅ prototype 有 · prototype has it | 保留，加 LLM 自然语言润色 · Keep, add LLM narrative |
| 教师反馈修正机制 · Teacher feedback loop | ❌ 无 · None | 教师可确认/修正诊断，反馈进系统 · Teacher can confirm/correct diagnosis |

### 2.3 板块三 · 靶向提质支持（支持链）· Module 3: Targeted Support (Support Chain)

| 申报书要求 · Proposal Requirement | 现状 · Status | 要做什么 · What to Build |
|---|---|---|
| 三维学习画像（知识/行为/认知）· 3-D learner profile | ❌ 无 · None | 基于诊断 + 行为数据构建画像 · Build profile from diagnosis + behavior |
| 学生分层（风险/薄弱/达标/拓展）· Student tiers | ❌ 无 · None | 按掌握度自动分层 · Auto-tier by mastery |
| 补救/巩固/拓展 三类学习路径 · 3 learning paths | ⚠️ master 有课程内容+资源 · master has content+resources | 复用 master 的资源浏览，按诊断推送 · Reuse master's resources, push by diagnosis |
| 三层支持：即时自助-智能推荐-教师干预 · 3-tier support | ❌ 无 · None | 设计三层支持工作流 · Design 3-tier workflow |
| 推荐：内容匹配+协同过滤+知识关联 · Hybrid recommendation | ❌ 无 · None | 先做内容匹配（基于诊断），后加协同过滤 · Content-based first, collaborative later |
| 多维预警机制（重点关注名单）· Multi-signal early warning | ❌ 无 · None | 连续错误/掌握度下降 → 预警名单 · Trigger watch-list |
| 资源库 100+ 资源包 · 100+ resource packages | ⚠️ master 有少量示例 · master has a few samples | 逐步建设资源库 · Build resource library over time |

### 2.4 板块四 · 循证驱动的智能教学生态（改进链）· Module 4: Evidence-Driven Ecosystem (Improvement Chain)

| 申报书要求 · Proposal Requirement | 现状 · Status | 要做什么 · What to Build |
|---|---|---|
| 教师决策看板 · Teacher decision dashboard | ✅ master 有精美看板 · master has a polished one | 移植到新架构，接真实诊断数据 · Port to new architecture |
| 知识点掌握热力图 · Mastery heatmap | ⚠️ master 有图表，非热力图 · master has charts | 加知识点掌握热力图 · Add KP mastery heatmap |
| 学生分层分布图 · Tier distribution | ❌ 无 · None | 加分层分布可视化 · Add tier distribution viz |
| 高频错题/错因排行 · Top errors/causes | ✅ prototype 班级汇总有 · prototype class summary has it | 移植到看板 · Port to dashboard |
| 预警学生名单 · Watch-list | ❌ 无 · None | 看板加预警面板 · Add watch-list panel |
| PDCA 教研循环 · PDCA research cycle | ❌ 无 · None | 加教研记录模块（看数据-议问题-定策略-再回看）· Add PDCA log module |
| 成效评估（配对 t 检验/效应量）· Quasi-experiment stats | ❌ 无 · None | 加前后测对比、统计检验脚本 · Add pre/post comparison + stats |

### 2.5 关键量化指标 · Key Quantitative Targets

| 指标 · Metric | 申报书目标 · Proposal Target | 系统需支持的功能 · System Must Support |
|---|---|---|
| 试点课程 · Pilot courses | 线性代数 + 人工智能基础 · LA + AI Fundamentals | 多课程架构 · Multi-course architecture |
| 覆盖学生 · Students covered | 500+ | 可扩展数据库 · Scalable database |
| 采集数据 · Data records | 10000+ | 高效数据管道 · Efficient pipeline |
| 知识点 · Knowledge points | 300+ | 可扩展 KG（先做 50-80）· Scalable KG (start 50-80) |
| 资源包 · Resource packages | 100+ | 资源库管理 · Resource library |
| 不及格率下降 · Failure rate down | ≥5% | 成效评估模块 · Evaluation module |
| 优秀率提升 · Excellent rate up | ≥5% | 成效评估模块 · Evaluation module |
| 知识点达标率提升 · Mastery up | ~10% | 掌握度按 KG 节点统计 · Mastery by KG node |
| 课程满意度 · Satisfaction | ≥90% | 问卷模块 · Survey module |
| 论文 · Papers | 1-2 篇 | 诊断方法 + 实证数据可发表 · Publishable method + evidence |

**结论 · Conclusion:**

**中文：** 申报书四大板块共约 28 项要求，目前两个原型合起来只覆盖了约 6-7 项。合并后的系统需要在现有基础上补齐剩下的 20 多项。下面的架构和模块设计就是为了系统性地把它们全部实现。

**English:** The proposal's four modules contain ~28 requirements; the two prototypes together cover only ~6-7. The merged system must fill the remaining ~20. The architecture and module design below are built to implement all of them systematically.


---

<a name="sec-3"></a>
## 3. 目标技术架构 · Target Architecture

> **中文：** 既然学生用 AI 辅助编程、能力不设限，我们采用现代、合理、行业标准的架构（也是 AI 工具最擅长生成的栈）。不过度设计，但要"像个真系统"。
>
> **English:** Since students use AI-assisted coding without capability limits, we adopt a modern, sound, industry-standard architecture (also the stack AI tools generate best). Not over-engineered, but a "real system."

### 3.1 整体架构图 · Overall Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  前端 Frontend                                                │
│  React + TypeScript + Vite + Tailwind + shadcn/ui            │
│  ├── 教师看板 Teacher Dashboard (热力图/分层/预警/排行)         │
│  ├── 知识图谱浏览 KG Explorer (Cytoscape.js 交互图谱)          │
│  ├── 学生画像 Learner Profile                                 │
│  ├── 诊断报告 Diagnosis Report                                │
│  └── 资源浏览 Resource Browser (课程内容/视频/推荐)            │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST API (JSON)
┌──────────────────────────┴──────────────────────────────────┐
│  后端 Backend                                                 │
│  FastAPI (Python)                                            │
│  ├── 诊断引擎 Diagnosis Engine (规则+图推理+BKT+LLM)           │
│  ├── 画像引擎 Profile Engine (知识/行为/认知三维)              │
│  ├── 推荐引擎 Recommendation Engine (内容匹配+知识关联)        │
│  ├── 预警引擎 Early-Warning Engine                            │
│  └── 评估引擎 Evaluation Engine (前后测/t检验/效应量)          │
└──────────────┬───────────────────────────┬──────────────────┘
              │                           │
    ┌─────────┴─────────┐       ┌─────────┴──────────┐
    │  Neo4j            │       │  PostgreSQL        │
    │  知识图谱          │       │  学习行为数据        │
    │  Knowledge Graph  │       │  Learning Behavior │
    │  概念/前置/题目/误区 │       │  学生/答题/成绩/时序 │
    └───────────────────┘       └────────────────────┘
              │
    ┌─────────┴─────────┐
    │  数据管道 Pipeline  │  Python ETL: Excel/CSV → 脱敏 → 入库
    │  + LLM (DeepSeek)  │  知识点抽取 + 报告润色
    └───────────────────┘
```

### 3.2 技术栈选型 · Tech Stack Choices

| 层 · Layer | 技术 · Technology | 为什么 · Why |
|---|---|---|
| 前端 · Frontend | React + TypeScript + Vite + Tailwind + shadcn/ui | 行业标准，AI 生成质量最高，组件丰富 · Industry standard, best AI codegen |
| 图谱可视化 · Graph viz | Cytoscape.js 或 react-force-graph | 比 vis-network 更适合现代 React · Better for modern React |
| 图表 · Charts | Recharts 或 visx | React 原生，热力图/分布图都支持 · Native React, supports heatmaps |
| 后端 · Backend | FastAPI (Python) | 异步、自动文档、诊断引擎是 Python 现成的 · Async, auto-docs, Python diagnosis ready |
| 图数据库 · Graph DB | Neo4j | 知识图谱前置回溯天然适合 · Natural fit for prerequisite traceback |
| 关系数据库 · Relational DB | PostgreSQL | 学习行为/时序数据用 SQL 更高效 · SQL better for behavior/time-series |
| 知识追踪 · Knowledge tracing | pyBKT | 成熟的贝叶斯知识追踪库 · Mature BKT library |
| LLM | DeepSeek / 通义千问 API | 便宜，中文好，用于抽取+报告 · Cheap, good Chinese |
| 数据管道 · Pipeline | Python (pandas) | Excel/CSV 处理 + 脱敏 · Excel/CSV + anonymization |
| 部署 · Deployment | Docker Compose | 一键起 Neo4j + Postgres + 后端 · One-command stack |

### 3.3 为什么放弃两个原型各自的栈 · Why Not Keep Either Original Stack

**中文：**
- **不直接用 master 的 Streamlit**：Streamlit 做复杂交互前端（拖拽图谱、多面板联动、教师反馈表单）有天花板，难以承载完整系统。
- **不直接用 prototype 的纯 HTML/JS**：手写 SVG 图谱、手写状态管理，维护成本高，扩展困难。
- **统一到 React + FastAPI**：前后端分离，各司其职；AI 工具对这套栈生成质量最高；是"真系统"的标准做法，对学生简历和论文都更有价值。

**English:**
- **Not Streamlit (from master)**: Streamlit hits a ceiling on complex interactive frontends (draggable graphs, linked panels, teacher feedback forms).
- **Not vanilla HTML/JS (from prototype)**: Hand-written SVG graphs and state management are costly to maintain and hard to extend.
- **Unify on React + FastAPI**: Clean separation, best AI codegen, the standard for a "real system"—better for student portfolios and the paper too.


---

<a name="sec-4"></a>
## 4. 保留与合并清单 · Keep & Merge List

> **中文：** 明确两个原型里哪些要保留、怎么迁移到新架构。
>
> **English:** Specify what to keep from each prototype and how to migrate it.

### 4.1 从 prototype（诊断）保留 · Keep from Prototype (Diagnosis)

| 资产 · Asset | 处理方式 · How to Handle | 迁移到 · Migrate To |
|---|---|---|
| 前置回溯诊断逻辑（REQUIRES 关系追溯）· Prerequisite-traceback logic | **核心资产，完整保留** · Core asset, keep fully | 后端诊断引擎 · Backend diagnosis engine |
| 怀疑度评分算法（suspicion_score）· Suspicion scoring | 保留并细化 · Keep and refine | 诊断引擎 · Diagnosis engine |
| 图谱 schema（Concept/Question/Student/ANSWERED）· KG schema | 作为基础，适配线性代数 · Use as base, adapt to LA | Neo4j |
| 学生报告 + 班级汇总生成 · Student/class report generation | 保留逻辑，改为 API 输出 · Keep logic, expose via API | 后端 + 前端 · Backend + frontend |
| 整套 docs 框架 · Docs framework | 保留（学生乙沿用了我们的规划）· Keep (student B reused our plan) | docs/ |
| 错误类型分类（error_type）· Error-type taxonomy | 保留并扩展 · Keep and extend | 数据模型 · Data model |

### 4.2 从 master（看板）保留 · Keep from Master (Dashboard)

| 资产 · Asset | 处理方式 · How to Handle | 迁移到 · Migrate To |
|---|---|---|
| 看板 UI 设计（暗色风/布局/配色）· Dashboard UI design | 作为前端设计参考，用 React 重写 · Design reference, rebuild in React | 前端教师看板 · Frontend dashboard |
| 交互式图谱（拖拽/点击钻取/着色）· Interactive graph | 用 Cytoscape.js 重做 · Rebuild with Cytoscape.js | 前端 KG Explorer · Frontend |
| 课程内容浏览 + 资源推荐 + 视频嵌入 · Course content + resources + video | 保留功能，接入诊断驱动的推荐 · Keep, connect to diagnosis-driven recommendation | 前端资源浏览 · Resource browser |
| 多维筛选 + 排名/分布/趋势 · Multi-filter + rankings/distribution/trends | 保留功能，用 Recharts 重做 · Keep, rebuild with Recharts | 前端看板 · Dashboard |
| 按掌握度着色的图谱节点 · Mastery-colored graph nodes | 保留，对接真实掌握度 · Keep, wire to real mastery | KG Explorer |

### 4.3 两个都要丢弃/替换 · Discard or Replace in Both

| 项 · Item | 原因 · Reason | 替换为 · Replace With |
|---|---|---|
| 随机生成的模拟成绩（master）· Random scores | 无研究价值 · No research value | 真实历史数据 · Real historical data |
| 初等数学知识图谱（master）· Elementary math KG | 偏题，非大学线代 · Off-topic | 真实线性代数 KG · Real LA KG |
| 合成的 error_type（prototype）· Synthetic error types | 不是真诊断出来的 · Not really diagnosed | 真实诊断 + BKT · Real diagnosis + BKT |
| 硬编码密码（master）· Hardcoded passwords | 安全风险 · Security risk | .env 环境变量 · .env secrets |
| 法语注释（master）· French comments | 接手成本高 · Handover cost | 中英注释 · CN/EN comments |


---

<a name="sec-5"></a>
## 5. 模块详细需求 · Detailed Module Requirements

> **中文：** 下面把系统拆成 8 个模块，每个写清楚"做什么、对应申报书哪一项、输入输出"。学生拿这个就能用 AI 编程实现。
>
> **English:** The system is split into 8 modules. Each specifies what to build, which proposal item it covers, and its inputs/outputs. Students can implement these with AI coding.

### 模块 M1 · 数据管道与脱敏 · Data Pipeline & Anonymization

**对应 · Covers:** 数据链 · Data chain
**做什么 · What:**
- 从 Excel/CSV 读历史成绩、作业、答题数据 · Read historical scores/homework/attempts from Excel/CSV
- 学号脱敏（SHA-256 + salt）· Anonymize IDs (SHA-256 + salt)
- 清洗后写入 PostgreSQL · Clean and load into PostgreSQL
- 密钥放 .env · Secrets in .env

**输入 · Input:** 原始 Excel/CSV · Raw Excel/CSV
**输出 · Output:** PostgreSQL 中的结构化行为表 · Structured behavior tables in PostgreSQL

### 模块 M2 · 知识图谱 · Knowledge Graph

**对应 · Covers:** 诊断链（知识结构）· Diagnosis chain (knowledge structure)
**做什么 · What:**
- Neo4j 存储：概念/知识点、前置关系、题目、误区 · Store concepts/KPs, prerequisites, questions, misconceptions
- 先做线性代数前 3 章（50-80 个知识点）· Linear Algebra Ch.1-3 first (50-80 KPs)
- 支持 LLM 辅助抽取 + 人工审核 · LLM-assisted extraction + human review
- 多课程架构（线代 + AI 基础）· Multi-course (LA + AI Fundamentals)

**输入 · Input:** 教材 + 人工审核的 CSV · Textbook + human-reviewed CSV
**输出 · Output:** 可查询的 Neo4j 图谱 · Queryable Neo4j graph

### 模块 M3 · 诊断引擎 · Diagnosis Engine

**对应 · Covers:** 诊断链核心 · Diagnosis chain core
**做什么 · What:**
- **表层**：题目对错 → 知识点掌握 · Surface: correctness → KP mastery
- **深层**：前置回溯（保留 prototype 逻辑）· Deep: prerequisite traceback (keep prototype logic)
- **根因**：BKT 掌握度概率（三状态）+ 怀疑度评分 · Root cause: BKT mastery probability + suspicion score
- **报告**：LLM 生成"问题/原因/证据/建议" · Report: LLM-generated problem/cause/evidence/suggestion
- **教师反馈**：教师可确认/修正，反馈进系统 · Teacher feedback loop

**输入 · Input:** 学生答题数据 + 知识图谱 · Attempts + KG
**输出 · Output:** 结构化诊断报告 · Structured diagnosis report

### 模块 M4 · 学习画像引擎 · Learner Profile Engine

**对应 · Covers:** 支持链（画像）· Support chain (profile)
**做什么 · What:**
- 知识维度：各知识点掌握度（来自 BKT）· Knowledge: KP mastery from BKT
- 行为维度：学习时长、提交时段、求助频率 · Behavior: time spent, submission timing, help frequency
- 认知维度：答题模式聚类 · Cognition: clustering of answer patterns
- 学生分层：风险/薄弱/达标/拓展 · Tiers: at-risk/weak/on-track/advanced

**输入 · Input:** 诊断结果 + 行为数据 · Diagnosis + behavior
**输出 · Output:** 每个学生的三维画像 + 分层标签 · 3-D profile + tier label

### 模块 M5 · 推荐引擎 · Recommendation Engine

**对应 · Covers:** 支持链（推荐）· Support chain (recommendation)
**做什么 · What:**
- 内容匹配：诊断出薄弱点 → 推送对应资源 · Content-based: weak KP → matching resources
- 知识关联：基于图谱推荐前置/拓展 · Graph-based: recommend prerequisites/extensions
- 三类路径：补救/巩固/拓展 · 3 paths: remedial/consolidation/extension
- 每次推送 ≤ 3-5 项，附推荐理由 · Push ≤ 3-5 items with reasons
- （后期）协同过滤 · (Later) collaborative filtering

**输入 · Input:** 诊断 + 画像 + 资源库 · Diagnosis + profile + resource library
**输出 · Output:** 个性化资源推荐列表 · Personalized recommendation list

### 模块 M6 · 预警引擎 · Early-Warning Engine

**对应 · Covers:** 支持链（预警）· Support chain (early warning)
**做什么 · What:**
- 多信号：连续错误率、掌握度下降、投入异常、高频求助 · Multi-signal triggers
- 自动生成"重点关注学生名单" · Auto-generate watch-list
- 推送给任课教师 · Push to instructors

**输入 · Input:** 诊断 + 画像时序 · Diagnosis + profile over time
**输出 · Output:** 预警名单 · Watch-list

### 模块 M7 · 教师看板 · Teacher Dashboard

**对应 · Covers:** 改进链（看板）· Improvement chain (dashboard)
**做什么 · What:**
- 知识点掌握热力图 · KP mastery heatmap
- 学生分层分布图 · Tier distribution
- 高频错题/错因排行 · Top errors/causes
- 预警学生名单面板 · Watch-list panel
- 交互式知识图谱（移植 master）· Interactive KG (ported from master)
- 资源浏览（移植 master）· Resource browser (ported from master)
- 钻取：班级 → 知识点 → 学生 · Drill-down: class → KP → student

**输入 · Input:** 所有引擎的输出（经 API）· All engine outputs via API
**输出 · Output:** 教师可视化界面 · Teacher UI

### 模块 M8 · 循证教研与评估 · Evidence Research & Evaluation

**对应 · Covers:** 改进链（PDCA + 成效评估）· Improvement chain (PDCA + evaluation)
**做什么 · What:**
- PDCA 教研记录模块（看数据-议问题-定策略-再回看）· PDCA log module
- 前后测对比 · Pre/post comparison
- 统计检验：配对 t 检验、效应量 · Stats: paired t-test, effect size
- 不及格率/优秀率/达标率对比 · Failure/excellent/mastery rate comparison
- 满意度问卷 · Satisfaction survey

**输入 · Input:** 试点前后数据 · Pre/post pilot data
**输出 · Output:** 成效报告（论文素材）· Evaluation report (paper material)


---

<a name="sec-6"></a>
## 6. 分阶段实施 · Phased Implementation

> **中文：** 不要一次性全做。按依赖关系分 4 期，每期产出可演示的成果。
>
> **English:** Don't build it all at once. Four phases by dependency, each producing a demonstrable result.

### 第 1 期 · 地基（M1 + M2）· Phase 1: Foundation

**中文：** 数据管道 + 真实线性代数知识图谱。把模拟数据换成真实数据，把初等数学换成真线代。
**English:** Data pipeline + real Linear Algebra KG. Replace mock data with real, elementary math with real LA.

**里程碑 · Milestone:** Neo4j 里有真实线代图谱，PostgreSQL 里有脱敏历史数据。
Real LA graph in Neo4j, anonymized historical data in PostgreSQL.

### 第 2 期 · 诊断内核（M3）· Phase 2: Diagnosis Core

**中文：** 把 prototype 的诊断逻辑迁到 FastAPI 后端，加 BKT 掌握度模型，加 LLM 报告。
**English:** Migrate prototype's diagnosis to FastAPI backend, add BKT mastery model, add LLM reports.

**里程碑 · Milestone:** 输入真实学生数据，输出可解释诊断报告（含根因 + 证据）。
Input real data, output explainable diagnosis (root cause + evidence).

### 第 3 期 · 支持与画像（M4 + M5 + M6）· Phase 3: Support & Profiles

**中文：** 学习画像 + 分层 + 推荐 + 预警。诊断结果转化为对学生的实际支持。
**English:** Profiles + tiers + recommendation + early warning. Turn diagnosis into actual student support.

**里程碑 · Milestone:** 每个学生有画像和分层，每类学生有资源推荐，高风险学生进预警名单。
Every student has a profile and tier, each tier gets recommendations, at-risk students enter the watch-list.

### 第 4 期 · 看板与循证（M7 + M8）· Phase 4: Dashboard & Evidence

**中文：** React 教师看板（移植 master UI）+ PDCA 教研 + 成效评估。这是结题验收和论文的门面。
**English:** React teacher dashboard (ported master UI) + PDCA research + evaluation. The face of the final review and paper.

**里程碑 · Milestone:** 教师能看完整看板，能做前后测对比，能导出成效报告。
Teacher sees the full dashboard, runs pre/post comparison, exports evaluation report.

### 时间建议 · Suggested Timing

| 期 · Phase | 内容 · Content | 大致周期 · Rough Duration |
|---|---|---|
| 1 | 地基 · Foundation | 4-6 周 · weeks |
| 2 | 诊断内核 · Diagnosis core | 4 周 · weeks |
| 3 | 支持与画像 · Support & profiles | 6 周 · weeks |
| 4 | 看板与循证 · Dashboard & evidence | 4 周 · weeks |

**中文：** 这些周期是建议，做不完没关系，可以换学生接力。关键是每期的成果都稳定、可交接。
**English:** These durations are suggestions. It's fine not to finish—students can hand off. The key is each phase's output is stable and transferable.


---

<a name="sec-7"></a>
## 7. 给学生的任务说明 · Task Brief for Students

> **中文：** 这一节可以直接发给两位同学。
>
> **English:** This section can be sent directly to the two students.

### 7.1 总体说明 · Overview

**中文：**
你们各自做的原型都很好，现在要合并成一个完整系统。我们采用现代架构：
**前端 React + 后端 FastAPI + Neo4j（知识图谱）+ PostgreSQL（行为数据）**。
你们可以用 AI 辅助编程实现，但要遵守下面的约定。

**English:**
Both your prototypes are good; now we merge them into one complete system using a
modern architecture: **React frontend + FastAPI backend + Neo4j (knowledge graph)
+ PostgreSQL (behavior data)**. Use AI-assisted coding, but follow the conventions below.

### 7.2 谁做什么（建议）· Who Does What (Suggested)

| 学生 · Student | 负责模块 · Modules | 理由 · Why |
|---|---|---|
| 学生乙（原诊断作者）· Student B (diagnosis author) | M1 数据管道、M2 知识图谱、M3 诊断引擎 · Pipeline, KG, Diagnosis | 他已懂诊断逻辑 · Already knows diagnosis |
| 学生甲（原看板作者）· Student A (dashboard author) | M7 看板、M5 资源推荐、KG Explorer · Dashboard, recommendation, KG explorer | 他 UI 能力强 · Strong UI skills |
| 两人协作 · Both | M4 画像、M6 预警、M8 评估 · Profile, warning, evaluation | 跨前后端 · Cross-stack |

### 7.3 硬性约定 · Hard Rules

**中文：**
1. **不准把学生真实数据上传 git**（用脱敏脚本，密钥放 .env）
2. **所有代码注释用中文或英文**，不要用法语
3. **后端和前端分离**：前端只通过 API 拿数据，不直连数据库
4. **每个模块写一份简短的 README**，说明怎么运行
5. **小步提交**，每个功能一个 PR
6. **诊断逻辑以 prototype 为准**，不要推倒重来

**English:**
1. **Never upload real student data to git** (use the anonymization script, secrets in .env)
2. **All code comments in Chinese or English**, not French
3. **Separate backend and frontend**: frontend gets data only via API, never connects to DB directly
4. **Write a short README for each module** explaining how to run it
5. **Small commits**, one PR per feature
6. **Diagnosis logic follows the prototype**—don't rebuild from scratch

### 7.4 验收标准（最终系统）· Acceptance Criteria (Final System)

**中文：** 最终系统必须能做到：
**English:** The final system must be able to:

- [ ] 导入真实历史数据并脱敏 · Import and anonymize real historical data
- [ ] 展示真实线性代数知识图谱（可交互）· Show an interactive real LA knowledge graph
- [ ] 对任一学生生成可解释诊断报告（问题/原因/证据/建议）· Generate explainable diagnosis per student
- [ ] 用 BKT 计算知识点掌握度 · Compute KP mastery with BKT
- [ ] 给每个学生分层并推荐资源 · Tier each student and recommend resources
- [ ] 自动生成预警学生名单 · Auto-generate a watch-list
- [ ] 教师看板：热力图/分层/排行/预警 · Teacher dashboard: heatmap/tiers/rankings/warnings
- [ ] 支持前后测对比与统计检验 · Support pre/post comparison and statistical tests
- [ ] 支持线代 + AI 基础两门课 · Support both LA and AI Fundamentals
- [ ] 全部对应申报书四大板块、四条链 · Cover all four proposal modules and chains

**中文：** 做到这些，就实现了申报书的全部教改内容，结题和论文都有底气。
**English:** Achieving these implements all the proposal's reform content—solid ground for the final review and the paper.

---

## 附录 · Appendix: 一句话总结 · One-Line Summary

**中文：** 以 prototype 的诊断内核为灵魂，以 master 的看板和资源为外壳，用 React + FastAPI + Neo4j + PostgreSQL 的现代架构重新组织，补齐画像、推荐、预警、评估四块短板，最终覆盖申报书全部教改内容。

**English:** Take the prototype's diagnosis core as the soul and the master's dashboard and resources as the shell; reorganize on a modern React + FastAPI + Neo4j + PostgreSQL architecture; fill the four gaps (profiles, recommendation, warning, evaluation); and ultimately cover all the reform content in the proposal.
