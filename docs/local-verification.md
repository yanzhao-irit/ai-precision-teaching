# 本地验证手册 · Local Verification

> 目标：起两个数据库 → 灌一章真实数据 → 跑通后端 API → 打开前端看板。
> 路径以 WSL 为例（Windows 文件在 `/mnt/c/...`）；用 Windows + Docker Desktop 亦可，命令相同。

项目根（WSL 视角）：
```
cd /mnt/c/Users/yan/Downloads/ai-precision-teaching-main
```

---

## 第 0 步 · 前提
```bash
docker --version        # 需要 Docker（Docker Desktop 开 WSL 集成，或 WSL 内装 docker engine）
python3 --version       # 3.11+
node --version          # 18+（前端）
```

---

## 第 1 步 · 一键建两个数据库（不用手动建表）
```bash
docker compose up -d
docker compose ps       # postgres、neo4j 应为 healthy；neo4j-init 跑完会 Exit 0
```
- Postgres 首次启动**自动执行** `backend/db/schema.sql`（建 22 张表 + 枚举 + 索引）。
- `neo4j-init` 等 Neo4j 健康后**自动加载** `backend/db/neo4j_constraints.cypher`（唯一约束）。
- 账号密码：Postgres `postgres/password`，Neo4j `neo4j/password`（与后端默认配置一致）。

**验证表已建好：**
```bash
docker compose exec postgres psql -U postgres -d ai_precision_teaching -c "\dt"
# 应列出 course / student / question / question_response / knowledge_point ... 等表
```
**验证图库约束：** 浏览器开 http://localhost:7474 （neo4j/password）执行 `SHOW CONSTRAINTS;`
（图谱节点此时为空，正常——节点由后续同步作业写入。）

> 重置数据库：`docker compose down -v`（删卷）再 `up -d` 会重新建表。

---

## 第 2 步 · 装后端依赖
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
> 若某个 pin 装不上想快点，**最小依赖**也能跑通本系统：
> ```bash
> pip install fastapi uvicorn sqlalchemy asyncpg "psycopg[binary]" neo4j \
>             pydantic python-dotenv pandas openpyxl xlrd
> ```
> （前后测 t 检验另需 `pip install scipy`，可选。）

后端默认连 `localhost:5432` / `bolt://localhost:7687`，与 docker-compose 暴露的端口一致，**无需额外配置 .env**。

---

## 第 3 步 · 灌一章真实数据（冒烟用单文件，无需解压）
样本目录：`/mnt/c/Users/yan/Downloads/ai data/`
```bash
cd ../data-pipeline

# ① 题库（第1章单元测试）
python run_etl.py questions \
  "/mnt/c/Users/yan/Downloads/ai data/第1章人工智能概论（大数据专业通识导论）【单元测试】.xls" \
  --course-code AI-BASE-2025 --course-name 人工智能基础
# 预期：questions=25, kp_linked=25

# ② 学生答题（这一位同学）
python run_etl.py answers \
  "/mnt/c/Users/yan/Downloads/ai data/计算机与数据工程学院-计算机科学与技术-计算机科学与技术253-3250439004-胡彬妍.doc" \
  --course-code AI-BASE-2025
# 预期：[答题] 3250439004 ch1 逐题25 缺题0

# ③ 班级一键导出（全班 81 人 + 进度 + 综合成绩）
python run_etl.py class-export \
  "/mnt/c/Users/yan/Downloads/ai data/(2025-2026-1)-20193026-02_统计一键导出.xlsx" \
  --course-code AI-BASE-2025
```

**灌全量数据（可选）：** 先解压两个 zip，再把目录传给 ETL（会遍历目录下所有文件）：
```bash
cd "/mnt/c/Users/yan/Downloads/ai data"
mkdir -p qbank docs && \
unzip -o "作业库(excel).zip" -d qbank && \
unzip -o "(2025-2026-1)-20193026-02-第1章 人工智能概论（大数据专业通识导论）【单元测试】(word).zip" -d docs
cd /mnt/c/Users/yan/Downloads/ai-precision-teaching-main/data-pipeline
python run_etl.py questions "/mnt/c/Users/yan/Downloads/ai data/qbank" --course-code AI-BASE-2025 --course-name 人工智能基础
python run_etl.py answers   "/mnt/c/Users/yan/Downloads/ai data/docs"  --course-code AI-BASE-2025
```

---

## 第 4 步 · 起后端，自检 API
```bash
cd ../backend && source .venv/bin/activate
uvicorn app.main:app --reload
```
打开 http://localhost:8000/docs ，或命令行：
```bash
curl "http://localhost:8000/api/courses"
curl "http://localhost:8000/api/students?course_code=AI-BASE-2025"
curl "http://localhost:8000/api/diagnosis/student/3250439004?course_code=AI-BASE-2025"
```
预期：课程返回 `AI-BASE-2025`；学生列表非空；诊断返回掌握度（`mastery_summary`）。
> 启动日志若打印 `⚠️ Neo4j not reachable` 不影响诊断——前置回溯会降级（图谱前置边尚未建）。

---

## 第 5 步 · 起前端
```bash
cd ../frontend
npm install
npm run dev        # http://localhost:5173
```
浏览器打开 → 顶栏选课程「人工智能基础」→ 选学生 → 「错因诊断」页应显示掌握度与逐题对错。
（后端 CORS 已开放，前端跨域直连，无需代理。）

---

## 不用 Docker？手动建库
1. 装 PostgreSQL 16 + Neo4j 5，建库 `ai_precision_teaching`。
2. 建表：`psql -U postgres -d ai_precision_teaching -f backend/db/schema.sql`
3. 图库约束：`cypher-shell -u neo4j -p <pwd> -f backend/db/neo4j_constraints.cypher`
4. 若账号/端口与默认不同，设环境变量后再起后端/ETL：
   `POSTGRES_USER/POSTGRES_PASSWORD/POSTGRES_HOST/POSTGRES_PORT/POSTGRES_DB`、`NEO4J_URI/NEO4J_USER/NEO4J_PASSWORD`。

---

## 常见问题
- **课程/学生下拉为空** → ETL 没灌成功或 course_code 不一致（统一用 `AI-BASE-2025`）。
- **读 .xls 报缺库** → `pip install xlrd`（已在 requirements）。
- **诊断有掌握度但无“前置缺口根因”** → 正常，图谱概念层+REQUIRES 边还没建（后续 P3）。
- **推荐页空** → 正常，资源还没按知识点打标签。
- **psycopg 连接失败** → 确认 `docker compose ps` 里 postgres 为 healthy、5432 已映射。
