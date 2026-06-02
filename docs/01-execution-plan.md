# 六阶段执行计划 · Six-Stage Execution Plan

> 本文档是项目的主路线图。所有任务、所有时间预估、所有交付物都从这里派生。
> This document is the master roadmap. All tasks, timelines, and deliverables derive from here.

---

## 总体思路 · Overall Approach

### 中文

项目以**线性推进**而非并行展开。每个阶段产出**独立可用**的成果，做完即稳定，
不依赖后续阶段。这样无论谁中途加入或离开，前序工作都不会浪费。

### English

The project advances **sequentially**, not in parallel. Each stage produces
**independently usable** outputs—stable on its own, not dependent on later stages.
This way, prior work is never wasted regardless of personnel changes.

---

## 六个阶段一览 · Stages at a Glance

| 阶段 · Stage | 名称 · Name | 预计周期 · Duration | 核心产出 · Key Output |
|---|---|---|---|
| 1 | 历史数据盘点 · Historical Data Audit | 2-3 周 / weeks | 基准数据集 · Baseline dataset |
| 2 | 线性代数知识图谱（前 3 章）· Linear Algebra KG (Ch. 1-3) | 4-6 周 / weeks | 可用 KG · Usable KG |
| 3 | 题库结构化 · Question Bank Structuring | 3-4 周 / weeks | 标注题库 · Annotated bank |
| 4 | 离线诊断原型 · Offline Diagnosis Prototype | 4 周 / weeks | 诊断 demo · Diagnosis demo |
| 5 | 教师看板雏形 · Teacher Dashboard MVP | 3 周 / weeks | 演示看板 · Demo dashboard |
| 6 | 试点 + 评估 · Pilot & Evaluation | 与学期同步 · Aligned with semester | 论文素材 · Paper materials |

---

## 阶段 1 · 历史数据盘点 · Historical Data Audit

### 目标 · Goal

**中文：** 在做任何技术工作之前，先把团队已有的教学数据资产挖出来。这是后续所有"循证研究"的弹药库。

**English:** Before any technical work, surface all existing teaching data assets.
This is the ammunition for all subsequent evidence-based research.

### 任务 · Tasks

1. **数据资产摸底 · Asset Audit**
   见 [`02-data-inventory.md`](02-data-inventory.md)
   See the data inventory document.

2. **选定基准数据集 · Select Baseline Cohort**
   从最完整的一届学生中选出 baseline，所有后续实验在这上面跑。
   Select the most complete cohort as baseline for all later experiments.

3. **脱敏与同意书 · Anonymization & Consent**
   写脱敏脚本，起草学生数据使用同意书。
   Write anonymization script, draft student data consent form.

### 完成标准 · Definition of Done

- [ ] `docs/02-data-inventory.md` 已填完所有条目 · All items filled
- [ ] `data/baseline-cohort/` 含脱敏后的基准数据 · Contains anonymized baseline data
- [ ] `docs/05-data-ethics.md` 已发布 · Published

---

## 阶段 2 · 线性代数知识图谱(前 3 章)· Linear Algebra KG (Ch. 1-3)

### 目标 · Goal

**中文：** 为线性代数前 3 章构建一份高质量、可计算、可解释的知识图谱。
**不追求完美，先做前 3 章做扎实。**

**English:** Build a high-quality, computable, explainable knowledge graph for
Linear Algebra Chapters 1-3. **Don't chase perfection; nail the first three chapters first.**

### 任务 · Tasks

1. **教材范围 · Textbook Scope**
   同济版第六版，前 3 章(行列式 / 矩阵运算 / 初等变换与线性方程组)
   Tongji 6th Ed., Chapters 1-3 (Determinants / Matrix Operations / Elementary Transformations & Linear Systems)

2. **KG Schema 设计 · Schema Design**
   见 [`03-kg-schema.md`](03-kg-schema.md)

3. **知识点初稿生成 · KP Draft Generation**
   用 LLM 从教材抽取候选知识点(DeepSeek API)
   Extract candidate KPs from textbook via LLM (DeepSeek API)

4. **人工审核与关系标注 · Manual Review & Relation Annotation**
   PI + 研究生 + 涂老师/许老师顾问咨询，2-3 次工作坊
   PI + graduate students + advisor consultations, 2-3 workshops

5. **导入 Neo4j · Import to Neo4j**
   写 Cypher 脚本 + Python 客户端
   Write Cypher scripts + Python client

### 完成标准 · Definition of Done

- [ ] 50-80 个知识点 · 50-80 KPs
- [ ] 50-100 条前置关系 · 50-100 prerequisite relations
- [ ] 核心知识点附带常见误区 · Core KPs include common misconceptions
- [ ] Neo4j 中可查询 · Queryable in Neo4j
- [ ] Python 客户端封装常用查询 · Python client wraps common queries

---

## 阶段 3 · 题库结构化 · Question Bank Structuring

### 目标 · Goal

**中文：** 把团队现有 3000+ 题中的核心 200-300 道，转化为可用于诊断的结构化数据。

**English:** Convert 200-300 core questions from the team's existing 3000+ question
bank into structured, diagnosis-ready data.

### 任务 · Tasks

1. **格式统一 · Format Standardization** — 全部转为 JSONL
2. **核心题集选定 · Core Set Selection** — PI 挑出 200-300 道
3. **知识点绑定 · KP Linking** — 每题关联到 KG
4. **错误选项分析 · Wrong-Answer Analysis** — 标注"选错的话犯了什么错"

### 完成标准 · Definition of Done

- [ ] 200-300 道核心题完成知识点绑定 · 200-300 questions KP-linked
- [ ] 其中选择题/填空题完成错误选项分析 · Multiple-choice/fill-in done with wrong-answer analysis

---

## 阶段 4 · 离线诊断原型 · Offline Diagnosis Prototype

### 目标 · Goal

**中文：** 基于阶段 1-3 的数据，不联网、不对接平台，离线生成一份诊断报告。

**English:** Based on data from Stages 1-3, generate diagnostic reports offline,
without networking or platform integration.

### 任务 · Tasks

1. 表层诊断(基于正确率) · Surface diagnosis (correctness-based)
2. BKT 模型(用 pyBKT 库)· BKT model (using the pyBKT library)
3. 图推理(前置回溯)· Graph reasoning (prerequisite traceback)
4. LLM 生成自然语言报告 · LLM-generated narrative reports

### 完成标准 · Definition of Done

- [ ] 能为基准数据集任一学生生成报告 · Can generate report for any student in baseline
- [ ] 报告包含掌握度、错因、根因、建议 · Report includes mastery, errors, root causes, suggestions
- [ ] 可作为论文实验素材 · Suitable as paper experimental material

---

## 阶段 5 · 教师看板雏形 · Teacher Dashboard MVP

### 目标 · Goal

**中文：** 用 Streamlit 做一个最简单的演示看板。不是产品，是 demo。

**English:** Build the simplest possible demo dashboard with Streamlit. Not a product, just a demo.

### 任务 · Tasks

- 学生选择器 · Student selector
- 知识点掌握度热力图 · KP mastery heatmap
- 诊断报告展示 · Diagnostic report display
- 班级总览页 · Class overview page

### 完成标准 · Definition of Done

- [ ] 一键启动(`streamlit run app.py`)· One-command launch
- [ ] 可在结题汇报时演示 · Presentable at final review

---

## 阶段 6 · 试点 + 评估 · Pilot & Evaluation

### 目标 · Goal

**中文：** 在真实教学班落地，采集证据，写论文。

**English:** Deploy in real classrooms, collect evidence, write papers.

### 任务 · Tasks

按学校学期节奏走，详见 [`04-evaluation-plan.md`](04-evaluation-plan.md)
Aligned with university semesters; see evaluation plan.

---

## 时间线总览 · Timeline Overview

```
2025.11  ━━ 项目启动 · Kickoff
2025.12  ━━ 阶段 1 开始 · Stage 1 starts
2026.01  ━━ 阶段 2 开始 · Stage 2 starts
2026.02  ━━ 阶段 3 开始 · Stage 3 starts (overlap with Stage 2)
2026.03  ━━ 阶段 4 开始 · Stage 4 starts
2026.06  ━━ 阶段 5 完成 · Stage 5 done
2026.09  ━━ 阶段 6 第一轮试点 · Pilot Round 1
2027.03  ━━ 第二轮试点 · Pilot Round 2
2027.08  ━━ 论文与总结 · Papers & wrap-up
2027.11  ━━ 结题 · Project closure
```

实际进度允许有 ±4 周的弹性。
Actual progress allows ±4 weeks of flexibility.
