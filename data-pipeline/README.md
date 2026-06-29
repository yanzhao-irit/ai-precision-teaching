# 数据管道 · Data Pipeline (ETL)

把三类导出文件解析并入库到 PostgreSQL（新 schema 见 `backend/db/schema.sql`）。

## 前提
1. 起库：项目根 `docker compose up -d`（表由 schema.sql 自动建好）。
2. 装依赖（项目 venv）：`pip install -r backend/requirements.txt`（含 pandas / xlrd / openpyxl / psycopg）。
   - 读 `.xls` 需要 `xlrd`；若缺：`pip install xlrd`。

## 结构
```
data-pipeline/
├── etl/
│   ├── parsers.py   解析器（纯函数，可脱库单测）
│   ├── db.py        psycopg 连接 + upsert 助手
│   └── load.py      解析结果 → 入库（幂等）
└── run_etl.py       命令行入口
```

## 用法（顺序：先题库，再学生答题）
```bash
cd data-pipeline

# 1) 题库 .xls（建 course/chapter/assessment/question/option/knowledge_point/映射）
python run_etl.py questions "<题库目录或单个.xls>" \
    --course-code AI-BASE-2025 --course-name 人工智能基础

# 2) 学生答题 .doc（建 submission + 逐题 question_response，含对错）
python run_etl.py answers "<doc目录或单个.doc>" --course-code AI-BASE-2025

# 3) 班级一键导出 .xlsx（建 student/enrollment/progress/composite_grade）
python run_etl.py class-export "<统计一键导出.xlsx>" --course-code AI-BASE-2025
```

连接信息从环境变量取（`POSTGRES_HOST/PORT/DB/USER/PASSWORD`），默认对齐 docker-compose。

## 说明
- **幂等**：重复跑用自然键 upsert，不会重复插。
- **知识点缺失**：题库“知识点”列为空时，该题 `kp_status='pending'`、不建映射，留给第二步 LLM(DeepSeek) 生成（见 docs/implementation-plan.md §3）。
- **对错判定**：`question_response.is_correct` 由 doc 内“学生答案 vs 正确答案”归一化比较得出（选择题排序比较、判断题 √/×↔正确/错误）。
- 逐题诊断仅覆盖客观单元测试；作业/视频/讨论只入聚合信号。
