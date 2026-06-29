# AI 赋能精准教学系统 · 教师端

# AI-Empowered Precision Teaching System · Teacher Portal

> 浙江省高等教育 2025 年本科教学改革项目 · Zhejiang Higher Education Teaching Reform Project
> 基于真实课程数据的精准教学系统：错因诊断（BKT + 前置回溯）+ 学情看板 + 数据导入。
> A precision-teaching system on real course data: error diagnosis (BKT + prerequisite traceback) + analytics dashboard + data import.

---

## 🚀 新接手的同学，先看这两份 · Start Here

1. **[SETUP.md](SETUP.md)** —— 从零搭建与运行（WSL + Docker + 后端 + 前端，含踩坑排查）。**搭建与启动以这份为准。**
2. **[data/README.md](data/README.md)** —— 数据怎么回事（为什么仓库里没数据、数据在哪、怎么导入）。

---

## 一、这个版本有什么 · What's in This Version

| 模块 · Module | 状态 · Status | 说明 · Notes |
|---|---|---|
| 双数据库 (PostgreSQL + Neo4j) | ✅ 可运行 | Docker 一键启动；PG 存业务+逐题作答，Neo4j 存知识图谱 |
| 数据导入 (网页拖拽 / ETL) | ✅ 可运行 | 三类文件：班级导出 / 题库 / 学生作业 zip |
| 错因诊断引擎 (BKT + 前置回溯) | ✅ 可运行 | 系统核心；前置回溯待知识图谱边就绪(见 v2) |
| 画像 / 推荐 / 预警 / 评估 引擎 | ✅ 可运行 | 经统一数据门面读两库 |
| 教师端看板 (React + Vite + TS) | ✅ 可运行 | 课程列表 → 课程详情(概览/学情/学生) → 下钻 |
| 知识图谱前置边 (REQUIRES) | 🟡 v2 待做 | Neo4j 目前为空；LLM 生成 + 人工审核后解锁前置缺口根因 |

---

## 二、跑起来 · Run

完整步骤（含环境安装、排错）见 **[SETUP.md](SETUP.md)**。装好环境后，开三个终端：

```bash
# 1) 数据库（首次启动自动建表）
docker compose up -d

# 2) 后端 API（http://localhost:8000，文档 /docs）
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload

# 3) 前端（http://localhost:5173）
cd frontend && npm run dev
```

浏览器打开 **http://localhost:5173**。首次使用：新建课程 → 进入课程 → 「导入数据」拖入文件（见 [data/README.md](data/README.md)）。

---

## 三、看什么 · What to Look At

| 页面 · Page | 内容 · Content |
|---|---|
| 首页 · Courses | 我的课程卡片（人数/班级/正确率）+ 「新建课程」 |
| 课程详情 · 概览 | 学生掌握分层（优秀/达标/薄弱 环形图）、整体正确率、参与与成绩 |
| 课程详情 · 学情 | **薄弱知识点 Top10** + **高错题 Top10**（点进题目看**干扰项分析**） |
| 课程详情 · 学生 | 花名册（分层标签 + 搜索 + 筛选）+ 需关注学生（**学业 / 学习态度 / 未测** 三类） |
| 题目下钻 | 题干/选项/正确答案 + 干扰项分布 + 答错学生名单 |
| 知识点下钻 | 平均掌握度/正确率 + 薄弱学生名单 |
| 学生下钻 | 逐知识点掌握度（三档色）+ 个体诊断 + 画像 + 推荐 |

班级筛选在课程详情顶部，作用于全部 Tab。

---

## 四、目录结构 · Structure

```
ai-precision-teaching/
├── backend/                    后端 · Backend (FastAPI)
│   ├── app/
│   │   ├── main.py             入口，注册所有路由
│   │   ├── api/                路由：dashboard(看板) / upload(导入) / students(课程·学生)
│   │   │                              / diagnosis / profiles / recommendations / warnings / evaluation
│   │   ├── services/dashboard.py  看板聚合分析（BKT 掌握度 → 分层）
│   │   ├── data_access/        数据访问层（引擎只认这一层）
│   │   │   ├── sql_repo.py       关系库仓储（PostgreSQL）
│   │   │   ├── graph_repo.py     图库仓储（Neo4j，降级安全）
│   │   │   └── gateway.py        ★ 引擎数据门面 EngineDataGateway ★
│   │   └── engines/            5 个业务引擎：diagnosis(核心) / profile / recommendation / warning / evaluation
│   ├── db/schema.sql           建表脚本（Docker 首次启动自动执行）
│   ├── db/neo4j_constraints.cypher
│   └── requirements.txt
├── frontend/                   前端 · React + Vite + TypeScript
│   └── src/
│       ├── pages/              CoursesPage / CourseDetailPage / QuestionPage / KnowledgePointPage / StudentPage
│       ├── pages/course/       课程详情三个 Tab：OverviewTab / DiagnosisTab / StudentsTab
│       ├── components/         UploadPanel(导入) / TopBar / ui(图表组件)
│       └── services/api.ts     调后端接口封装
├── data-pipeline/              ETL：解析三类文件入库（网页上传时后端调用它）
│   └── etl/{parsers,load,db}.py + run_etl.py
├── docker-compose.yml          一键启动 PostgreSQL + Neo4j
├── SETUP.md                    ★ 从零搭建与运行
└── data/README.md              ★ 数据说明
```

---

## 五、架构要点 · Architecture

- **两库分工**：`PostgreSQL` 存所有教学业务数据（课程/学生/选课/题目/**逐题作答**/知识点登记/成绩/进度）；
  `Neo4j` 只存**知识图谱**（概念层 + 前置关系 REQUIRES）。两库用共享的 **`kp_code`（知识点 ID）** 对齐，不跨库外键。
- **引擎只经一个入口读数据**：`app/data_access/gateway.py` 的 `EngineDataGateway` 把关系库仓储 + 图库仓储藏在后面，
  引擎（诊断/画像/推荐/预警/评估）只调它。图库为空/不可用时自动降级（返回空，不崩）。
- **看板聚合**：`app/services/dashboard.py` 用 BKT 把全班逐题作答算成掌握度，做学生分层与薄弱知识点排行。
- **掌握度三档**（全局一致）：优秀 ≥0.7 / 达标 0.4–0.7 / 薄弱 <0.4。

数据库表结构详见 `backend/db/schema.sql` 与 `docs/data-schema.md`（中英文数据字典）。

---

## 六、继续完善方向 · Extension Directions

按优先级：

1. **知识图谱前置边**（LLM 生成 + 人工审核）→ 解锁「前置缺口根因」这一核心卖点（当前 Neo4j 为空）。
2. **多章节 / 多学期数据** → 掌握度趋势、PDCA 改进链。
3. **学生登录端**（当前只做了教师端）。
4. **题目缺知识点时用 LLM(DeepSeek) 自动标注** + 人工审核队列（接口与计划见 `docs/implementation-plan.md`）。
5. **真鉴权 + 教师↔课程归属**（当前登录后可见全部课）。
6. **班级口径核对**：花名册班级（数据科学251/252…）与答题文件名班级（计算机253）不一致，需确认以哪个为准。

代码里多处留有 `TODO` 标注扩展点。

---

## 七、对应申报书四条链 · Four Chains

- **数据链** · Data → `data-pipeline/` + `app/api/upload.py` + 两库
- **诊断链** · Diagnosis → `app/engines/diagnosis/` + `app/data_access/graph_repo.py`
- **支持链** · Support → `app/engines/{profile,recommendation,warning}/` + 看板「需关注学生」
- **改进链** · Improvement → `app/engines/evaluation/` + 看板（趋势对比需多时点数据）

---

## 八、联系 · Contact

PI: 赵妍 · Zhao Yan · zhaoyan@nbt.edu.cn
