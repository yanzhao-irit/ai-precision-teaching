# 上手说明 · Getting Started Guide

> **给学生：** 这份文档教你三件事——怎么把系统跑起来、怎么读懂这套代码、从哪里开始改。完全没做过也能照着做。
>
> **For students:** This guide teaches you three things—how to run the system, how to read the codebase, and where to start changing things. You can follow it even with no prior experience.

---

## 目录 · Table of Contents

1. [运行系统 · Run the System](#run)
   - [Windows](#run-win)
   - [Linux / Mac](#run-nix)
2. [怎么读这套代码 · How to Read the Code](#read)
3. [从哪里开始改 · Where to Start Changing](#change)
4. [常见问题 · Troubleshooting](#trouble)


---

<a name="run"></a>
## 一、运行系统 · Run the System

**中文：** 这个系统分两部分:**后端**(提供数据和诊断)和**前端**(看板界面)。要两个都启动。后端用 Python,前端只要一个浏览器。本初版用内存模拟数据,**不需要安装任何数据库**。

**English:** The system has two parts: the **backend** (serves data and diagnosis) and the **frontend** (dashboard UI). Start both. The backend uses Python; the frontend just needs a browser. This version uses in-memory mock data, so **no database is required**.

**前提 · Prerequisites:** Python 3.11+、一个现代浏览器 · Python 3.11+ and a modern browser.

检查 Python · Check Python:
```
python --version
```
**中文：** 如果显示 3.11 或更高就行。Windows 上如果 `python` 不行,试试 `py --version`。
**English:** If it shows 3.11 or higher, you're good. On Windows, if `python` fails, try `py --version`.

---

<a name="run-win"></a>
### Windows 运行步骤 · Steps on Windows

**中文：** 打开两个"命令提示符"(在开始菜单搜 `cmd`)或两个 PowerShell 窗口——一个跑后端,一个跑前端。

**English:** Open two Command Prompts (search `cmd` in Start menu) or two PowerShell windows—one for the backend, one for the frontend.

**窗口 1 · Window 1 — 后端 · Backend:**

```
cd 你解压的路径\ai-precision-teaching\backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**中文：** 看到 `Application startup complete` 就成功了。后端跑在 `http://localhost:8000`。**这个窗口不要关。**
**English:** Seeing `Application startup complete` means success. The backend runs at `http://localhost:8000`. **Keep this window open.**

**窗口 2 · Window 2 — 前端 · Frontend:**

```
cd 你解压的路径\ai-precision-teaching\frontend
python -m http.server 5173
```

**中文：** 然后用浏览器打开 `http://localhost:5173/index.html`。
**English:** Then open `http://localhost:5173/index.html` in your browser.

> **PowerShell 激活报错？· Activation error in PowerShell?**
> **中文：** 如果运行 `.venv\Scripts\activate` 报"无法加载脚本",先用管理员身份打开 PowerShell 运行：
> **English:** If `.venv\Scripts\activate` says scripts cannot be loaded, open PowerShell as administrator and run:
> ```
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> 然后重新激活。· Then activate again.

---

<a name="run-nix"></a>
### Linux / Mac 运行步骤 · Steps on Linux / Mac

**中文：** 打开两个终端窗口。

**English:** Open two terminal windows.

**终端 1 · Terminal 1 — 后端 · Backend:**

```bash
cd /你解压的路径/ai-precision-teaching/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**中文：** 看到 `Application startup complete` 即成功,后端在 `http://localhost:8000`。**保持窗口开着。**
**English:** `Application startup complete` means success; backend at `http://localhost:8000`. **Keep it open.**

**终端 2 · Terminal 2 — 前端 · Frontend:**

```bash
cd /你解压的路径/ai-precision-teaching/frontend
python3 -m http.server 5173
```

**中文：** 浏览器打开 `http://localhost:5173/index.html`。
**English:** Open `http://localhost:5173/index.html` in your browser.

---

### 跑起来后你应该看到 · What You Should See

**中文：** 教师看板,顶部有 5 个标签页:

**English:** The teacher dashboard, with 5 tabs at the top:

| 标签页 · Tab | 内容 · Content |
|---|---|
| 总览 · Overview | KPI 卡片、学生分层分布、四链条映射 · KPIs, tier distribution, four chains |
| 知识图谱 · Knowledge Graph | 交互式图谱,点节点看前置链 · Interactive graph, click nodes for prerequisites |
| 学生画像 · Profiles | 三维画像 + 分层 · 3-D profile + tier |
| 错因诊断 · Diagnosis | **核心**:前置回溯诊断 · **Core**: prerequisite-traceback diagnosis |
| 班级分析 · Analytics | 热力图、错因排行、预警、评估 · heatmap, rankings, warnings, evaluation |

**中文：** 如果右上角显示"后端未连接",说明后端没起来,回去检查窗口 1。
**English:** If the top-right says "Backend offline", the backend isn't running—go back and check Window 1.

### 怎么停止 · How to Stop

**中文：** 在每个窗口里按 `Ctrl + C`。下次再跑,后端只需 `activate` + `uvicorn` 两条(不用重装依赖),前端只需 `python -m http.server 5173` 一条。

**English:** Press `Ctrl + C` in each window. Next time, the backend just needs `activate` + `uvicorn` (no reinstall), and the frontend just needs `python -m http.server 5173`.


---

<a name="read"></a>
## 二、怎么读这套代码 · How to Read the Code

**中文：** 别一上来就读所有文件。按下面的顺序读,理解会快很多。整个系统的数据流是一条线:

**English:** Don't read every file at once. Follow the order below to understand faster. The whole system's data flow is a single line:

```
模拟数据 mock_data.py
   ↓ 经过 · through
仓储层 repository/  (数据从哪来的唯一入口 · single source of data)
   ↓ 喂给 · feeds
引擎 engines/  (诊断/画像/推荐/预警/评估 · the 5 engines)
   ↓ 通过 · exposed via
API api/  (FastAPI 路由 · routes)
   ↓ 被 · consumed by
前端 frontend/index.html  (React 看板 · dashboard)
```

### 建议的阅读顺序 · Suggested Reading Order

**中文：** 按这个顺序,每个文件配一句"它在干嘛"。

**English:** In this order, each file with a one-line "what it does".

| 顺序 · Order | 文件 · File | 它在干嘛 · What it does |
|---|---|---|
| 1 | `backend/app/data/mock_data.py` | 模拟数据:概念、前置关系、题目、学生、答题记录 · Mock data: concepts, prerequisites, questions, students, attempts |
| 2 | `backend/app/repository/__init__.py` | 数据访问层。**将来换数据库只改这里** · Data access layer. **DB swap happens only here** |
| 3 | `backend/app/kg/__init__.py` | 知识图谱工具,核心是"前置回溯" · KG helper; core is "prerequisite traceback" |
| 4 | `backend/app/engines/diagnosis/bkt.py` | 轻量 BKT 掌握度模型(约 40 行)· Lightweight BKT mastery model (~40 lines) |
| 5 | `backend/app/engines/diagnosis/engine.py` | **诊断引擎,系统核心**。前置回溯 + BKT + 怀疑度 · **Diagnosis engine, the core** |
| 6 | `backend/app/engines/profile/__init__.py` | 学习画像:知识/行为/认知 + 分层 · Profile: knowledge/behavior/cognition + tiers |
| 7 | `backend/app/engines/recommendation/__init__.py` | 推荐:按薄弱点推资源 · Recommendation by weak concepts |
| 8 | `backend/app/engines/warning/__init__.py` | 预警:多信号风险名单 · Multi-signal watch-list |
| 9 | `backend/app/engines/evaluation/__init__.py` | 班级分析 + 前后测统计 · Class analytics + pre/post stats |
| 10 | `backend/app/api/*.py` | 每个引擎对应一个 API 路由文件 · One API file per engine |
| 11 | `backend/app/main.py` | 把所有路由组装起来 · Assembles all routes |
| 12 | `frontend/index.html` | React 看板,5 个页面组件 · React dashboard, 5 page components |

### 理解诊断引擎(最重要)· Understanding the Diagnosis Engine (most important)

**中文：** 这是整个项目的灵魂。它对学生的每道错题做三件事:

**English:** This is the soul of the project. For each wrong answer, it does three things:

1. **表层 · Surface:** 这道题考哪个知识点? · Which concept does this question test?
2. **深层 · Deep:** 沿前置关系往回找,这个知识点依赖哪些前置? · Trace prerequisites backward.
3. **根因 · Root:** 用 BKT 算学生在那些前置上的掌握度,找出最可能的薄弱根源,给一个"怀疑度"分数。· Use BKT to find the weakest prerequisite and assign a suspicion score.

**中文：** 举例:学生"神经网络"题答错了。引擎发现神经网络依赖"矩阵",而学生在矩阵上掌握度很低(0.19)→ 诊断结论:"表面错在神经网络,根因可能是矩阵没掌握,建议先复习矩阵。"这就是申报书说的"从'知道错了'到'说清为什么错'"。

**English:** Example: a student fails a "Neural Network" question. The engine sees Neural Network depends on "Matrix", and the student's mastery of Matrix is very low (0.19) → diagnosis: "Surface error on Neural Network, root cause likely Matrix, recommend reviewing Matrix first." This is exactly the proposal's "from knowing it's wrong to explaining why it's wrong."

### 前端怎么读 · Reading the Frontend

**中文：** `frontend/index.html` 是一个文件,但内部分成 5 个 React 组件,跟 5 个标签页一一对应:

**English:** `frontend/index.html` is one file but is internally split into 5 React components, one per tab:

| 组件 · Component | 对应标签页 · Tab | 调用的 API · API it calls |
|---|---|---|
| `Overview` | 总览 | `/api/evaluation/overview` |
| `GraphView` | 知识图谱 | `/api/kg/graph` |
| `Students` | 学生画像 | `/api/profiles/` |
| `Diagnosis` | 错因诊断 | `/api/diagnosis/student/{id}` |
| `Analytics` | 班级分析 | `/api/evaluation/*`、`/api/warnings/*` |

**中文：** 想知道某个页面的数据从哪来,就看那个组件里的 `api(...)` 调用,然后去后端找对应的路由文件。

**English:** To find where a page's data comes from, look at the `api(...)` calls in its component, then find the matching route file in the backend.

### 一个好用的技巧 · A Handy Trick

**中文：** 后端跑起来后,打开 `http://localhost:8000/docs`。这是自动生成的 API 文档,可以直接点按钮测试每个接口,看返回的数据长什么样。读代码前先在这里点一圈,会很有帮助。

**English:** With the backend running, open `http://localhost:8000/docs`. This is auto-generated API documentation where you can click to test each endpoint and see what data it returns. Clicking through it before reading code helps a lot.


---

<a name="change"></a>
## 三、从哪里开始改 · Where to Start Changing

**中文：** 下面按"由易到难"排,每项都说清改哪个文件、怎么改、为什么。代码里凡是要你改的地方都标了 `TODO` 注释,全局搜索 `TODO` 能找到所有扩展点。

**English:** Listed easy-to-hard. Each says which file, how, and why. Every spot meant for you is marked with a `TODO` comment—search `TODO` globally to find all extension points.

### 改动 1（最简单）· Change 1 (easiest): 改模拟数据 · Edit Mock Data

**文件 · File:** `backend/app/data/mock_data.py`

**中文：** 想加一个学生、加一道题、改一条前置关系?直接改这个文件里的列表。比如往 `STUDENTS` 加一行,往 `ATTEMPTS` 加几条答题记录,刷新前端就能看到新学生。这是熟悉系统最好的起点——改完立刻看到效果。

**English:** Want to add a student, a question, or a prerequisite relation? Just edit the lists in this file. For example, add a row to `STUDENTS` and a few rows to `ATTEMPTS`, then refresh the frontend to see the new student. This is the best starting point—change it and see the effect instantly.

---

### 改动 2（重要）· Change 2 (important): 换成真实线性代数知识图谱 · Replace with Real Linear Algebra KG

**文件 · File:** `backend/app/data/mock_data.py` 里的 `CONCEPTS`、`RELATIONS`、`QUESTIONS`、`MISCONCEPTIONS`

**中文：** 现在的知识图谱是 AI 课程的(15 个概念)。等你们的线性代数知识图谱做好了(阶段 2),把这四个列表替换成线代的内容即可。**数据结构不用变**,引擎会自动工作。注意 `RELATIONS` 里的 `REQUIRES` 表示"前置依赖",这是诊断回溯的基础。

**English:** The current KG is for an AI course (15 concepts). Once your Linear Algebra KG is ready (Stage 2), just replace these four lists with linear-algebra content. **The data structure stays the same**—the engines will work automatically. Note `REQUIRES` in `RELATIONS` means "prerequisite dependency", which is the basis of diagnosis traceback.

---

### 改动 3（最关键）· Change 3 (most critical): 接真实数据库 · Connect a Real Database

**文件 · File:** `backend/app/repository/__init__.py`

**中文：** 这是整个系统设计的精髓——**所有数据都从这一层读,所以换数据库只改这一个文件。** 步骤:

**English:** This is the heart of the system's design—**all data flows through this layer, so switching databases only touches this one file.** Steps:

1. 新建 `backend/app/repository/db_repository.py`
   Create `backend/app/repository/db_repository.py`

2. 写一个类继承 `AbstractRepository`,实现里面所有方法,但数据从数据库读:
   Write a class extending `AbstractRepository`, implementing all methods but reading from the database:
   - `get_concepts` / `get_relations` / `get_questions` / `get_misconceptions` → 从 **Neo4j** 读 · from **Neo4j**
   - `get_students` / `get_attempts` → 从 **PostgreSQL 或 MySQL** 读 · from **PostgreSQL/MySQL**

3. 在 `repository/__init__.py` 改最后一行:
   Change the last line in `repository/__init__.py`:
   ```python
   repository: AbstractRepository = InMemoryRepository()
   # 改成 · change to:
   repository: AbstractRepository = DbRepository()
   ```

4. 完成。引擎、API、前端**一行都不用改**。
   Done. Engines, APIs, and frontend need **zero changes**.

**中文：** `repository/__init__.py` 文件顶部有一段详细的 TODO 注释,把这个流程也写在里面了。
**English:** The top of `repository/__init__.py` has a detailed TODO comment describing this same flow.

---

### 改动 4（算法升级）· Change 4 (algorithm upgrade): BKT 换成 pyBKT · Swap BKT for pyBKT

**文件 · File:** `backend/app/engines/diagnosis/bkt.py`

**中文：** 现在的 BKT 是自己写的轻量版,四个参数是固定的。pyBKT 库能从真实数据自动拟合参数,更准。等有了足够真实答题数据,可以换。`bkt.py` 顶部的 TODO 注释里有示例代码。换的时候保持 `estimate()` 和 `mastery_state()` 两个方法的输入输出不变,诊断引擎就不用改。

**English:** The current BKT is a hand-written lightweight version with fixed parameters. The pyBKT library can fit parameters from real data for better accuracy. Switch once you have enough real attempt data. The TODO at the top of `bkt.py` has sample code. Keep the inputs/outputs of `estimate()` and `mastery_state()` unchanged, and the diagnosis engine won't need edits.

---

### 改动 5（增强诊断）· Change 5 (enhance diagnosis): LLM 润色报告 · LLM Report Narrative

**文件 · File:** `backend/app/engines/diagnosis/engine.py` 里的 `generate_narrative_with_llm()`

**中文：** 现在诊断说明是规则模板拼的。想让它更自然、更像老师写的?这个方法预留了接口(默认关闭,所以没 API key 也能跑)。实现它:用 DeepSeek API 把结构化诊断结果润色成一段话。方法里有 TODO 提示怎么写。

**English:** Diagnosis explanations are currently rule-based templates. Want them more natural, more teacher-like? This method has a reserved hook (off by default, so it runs without an API key). Implement it: use the DeepSeek API to turn the structured diagnosis into prose. The method has a TODO showing how.

---

### 改动 6（前端升级）· Change 6 (frontend upgrade): 升级为标准 React 工程 · Upgrade to a Proper React Project

**文件 · File:** `frontend/`(见 `frontend/README.md`)

**中文：** 现在前端是单文件版,适合快速看效果。等功能变复杂,按 `frontend/README.md` 的指引升级成 Vite + TypeScript 工程,把 5 个组件拆成单独文件。

**English:** The frontend is currently single-file, good for quick previews. As features grow, follow `frontend/README.md` to upgrade to a Vite + TypeScript project and split the 5 components into separate files.

---

### 改动优先级建议 · Suggested Priority

**中文：** 如果不知道先做什么,按这个顺序:

**English:** If unsure what to do first, follow this order:

```
1. 改动 1（玩熟模拟数据，理解系统）· Edit mock data to learn the system
2. 改动 3（接数据库，最关键的基础设施）· Connect DB — critical infrastructure
3. 改动 2（换真实线代图谱）· Real Linear Algebra KG
4. 改动 4（pyBKT）· pyBKT
5. 改动 5、6（LLM、前端升级）· LLM and frontend upgrade
```


---

<a name="trouble"></a>
## 四、常见问题 · Troubleshooting

**Q1: 右上角显示"后端未连接" · Top-right shows "Backend offline"**

**中文：** 后端没起来。检查窗口 1 是不是还开着、有没有报错。确认 `uvicorn` 那条命令在跑,且地址是 `http://localhost:8000`。
**English:** The backend isn't running. Check Window 1 is still open with no errors. Make sure the `uvicorn` command is running at `http://localhost:8000`.

---

**Q2: `python` 不是可识别的命令 · `python` is not recognized**

**中文：** Windows 上重装 Python 时勾选 "Add Python to PATH",或把命令里的 `python` 换成 `py`。Linux/Mac 上换成 `python3`。
**English:** On Windows, reinstall Python with "Add Python to PATH" checked, or replace `python` with `py`. On Linux/Mac, use `python3`.

---

**Q3: `pip install` 很慢或失败 · `pip install` is slow or fails**

**中文：** 换国内镜像源:
**English:** Use a faster mirror:
```
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

**Q4: 端口被占用 · Port already in use**

**中文：** 如果 8000 或 5173 被占用,换个端口。后端:`uvicorn app.main:app --reload --port 8001`(同时把 `frontend/index.html` 里的 `const API = "http://localhost:8000"` 改成 8001)。前端:`python -m http.server 5174`。
**English:** If port 8000 or 5173 is taken, use another. Backend: `uvicorn app.main:app --reload --port 8001` (and change `const API = "http://localhost:8000"` in `frontend/index.html` to 8001). Frontend: `python -m http.server 5174`.

---

**Q5: 前端页面空白 · Frontend page is blank**

**中文：** 一般是没通过 `http.server` 打开,而是直接双击了 html 文件。必须用 `python -m http.server 5173` 启动,再通过 `http://localhost:5173/index.html` 访问。直接双击打开会因为浏览器安全限制而无法加载脚本。
**English:** Usually because you double-clicked the HTML file instead of serving it. You must start `python -m http.server 5173` and visit via `http://localhost:5173/index.html`. Double-clicking fails due to browser security restrictions.

---

**Q6: 改了后端代码没生效 · Backend changes don't take effect**

**中文：** `uvicorn` 加了 `--reload`,改 Python 文件会自动重启。如果没自动重启,手动 `Ctrl+C` 再重新运行。改前端 `index.html` 后,刷新浏览器即可。
**English:** `uvicorn --reload` auto-restarts on Python file changes. If it doesn't, `Ctrl+C` and rerun. For frontend `index.html` changes, just refresh the browser.

---

## 求助渠道 · Where to Get Help

| 问题 · Issue | 找谁 · Who |
|---|---|
| 装环境、报错 · Setup errors | 先 Google + 问 AI,再问同伴 · Google + AI first, then peer |
| 代码看不懂 · Code unclear | 先看代码里的中英注释和 TODO · Read the bilingual comments and TODOs first |
| 项目方向、任务 · Direction/tasks | PI |
| 知识点内容 · KG content | PI / 涂老师 · Prof. Tu |

**中文：** 记住:卡 2 小时就求助,不要硬扛一整天。
**English:** Remember: ask for help after 2 hours stuck—don't grind for a whole day.
