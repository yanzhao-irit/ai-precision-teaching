# 落地方案 · Implementation Plan（第二步）

> 前置：架构图 + [data-schema.md](data-schema.md)。方向已定：**关系库为主，图库为单向同步的投影**（知识图谱改动不大）。
> 本文覆盖：①总体管线 ②三类文件 ETL ③缺知识点时调 LLM 生成 ④PG→Neo4j 同步 ⑤统一 Repository ⑥分阶段改造步骤。

---

## 0. 同步策略（先补进设计：关系库为主）

- **知识点节点**：关系库 `concept` / `knowledge_point` 是主表。当一行 `review_status` 变为 `approved` 时，触发**单向 upsert** 到 Neo4j（`MERGE` by `concept_code`/`kp_code`，只同步 label/difficulty 等锚点字段）。删除/改名同向传播。
- **前置边 `REQUIRES`、`HAS_CONCEPT` 分层**：只在图库建与改，关系库永不持有。
- 没有任何事实被两库同时当作权威 → 不存在双向同步、不会冲突。

---

## 1. 总体管线 · Pipeline

```
三类导出文件
   │  (ETL，幂等，以学号为键)
   ▼
PostgreSQL（业务 + 题目 + 逐题作答 + 知识点登记表）
   │            │
   │            └─(缺知识点)→ LLM 生成 KP/映射 → kp_generation_log → 人工校对 → approved
   │
   └─(approved 的 concept/kp)─单向 upsert→ Neo4j（补 REQUIRES 前置边：LLM 草拟 + 人工校对）
                                   │
   引擎 ─ 统一 Repository ──────────┘
```

---

## 2. ETL · 三类文件入库

所有 ETL 脚本放 `data-pipeline/`，幂等（用自然键 upsert），可重复跑。统一连接键 = **学号 `student_no`**。

### 2.1 班级一键导出 `*.xlsx`（13 sheet → 业务 + 行为）

每个 sheet 表头在第 3 行（`header=2`），数据从第 4 行起；前两行是标题/课程信息，跳过。

| Sheet | 目标表 | 关键映射 |
|---|---|---|
| 综合成绩 / 综合成绩（百分制） | `composite_grade` | 作业(100%)→`homework_score`，综合成绩→`final_score` |
| 学生学习进度详情 | `student` + `enrollment` + `student_progress` | UID→`external_uid`，学号→`student_no`，任务完成数/任务点%/视频时长/讨论数/章节学习次数 |
| 章节学习次数 | `chapter_visit_daily` | 日期 + 6 个时段 |
| 任务点完成详情 | `learning_resource` + `task_completion` | 列头=资源名，单元格“已完成/未完成 + 完成时间” |
| 音视频观看详情 | `media_view` | 开始/结束/反刍比/观看时长 |
| 讨论参与详情 | `discussion_participation` | 总讨论/发表/回复/获赞 |
| 作业统计 | `assessment(type=homework)` + `submission` | 每章一列：成绩/提交时间/状态 |
| 章节测验统计 | `assessment(type=unit_test)` + `submission` | 同上（整份分数，无逐题） |
| 考试统计 / 线下成绩统计 | `assessment(exam/offline)` + `submission` | |
| 签到详情统计 | `attendance_session` + `attendance_record` | 列头=签到日期，单元格状态映射枚举 |
| 班级教学内容详情 | `course`（元数据） | 班级/学期/人数/章节数等 |

状态值映射：`已完成→completed`、`未完成→not_completed`、`待批阅→pending_review`；签到 `已签→present`、`缺勤→absent`、`请假→leave`、`教师代签→teacher_signed`、`未参与→not_participated`。

### 2.2 题库 `作业库/*.xls`（题目 + 知识点桥）

列：题目类型 / 大题题干 / 正确答案 / 答案解析 / 难易度 / **知识点** / 建议分数 / 选项A–Z。

- 题型映射：单选→`single_choice`，多选→`multiple_choice`，判断→`true_false`。
- 难易度映射：易→1，中→3，难→5。
- 入 `assessment` + `question` + `question_option`（按列 A–Z 展开，正确答案串决定 `is_correct`）。
- **知识点列有值** → upsert `knowledge_point(source='imported', review_status='approved')` + `question_knowledge_point(source='imported')`。
- **知识点列为空/缺失** → 写 `question(kp_status='pending')`，**不建映射**，交给第 3 步 LLM 生成（这是你强调的点）。

### 2.3 学生答题 `*.doc`（逐题作答，诊断核心）

文件实为 **Word 2003 XML（UTF-8）**，不是二进制 .doc——直接当 XML 解析 `<w:t>` 文本即可（已验证）。

- 头部：答题人 / 提交时间 / 作业得分 → `submission`。
- 每题块用正则切分：`N.题干` → 选项 → `学生答案：X` / `正确答案：Y` / `题目得分：Z`。
- 按 (assessment + 题号/题干) join `question` 取 `question_id`，写 `question_response`：
  - `student_answer=X`，`answer_snapshot=Y`，`is_correct = norm(X)==norm(Y)`（判断题 √/×↔正确/错误归一），`score=Z`。
- 整份 zip 里约 80 份/章，批量遍历入库。

---

## 3. 缺知识点 → 调大模型 API 生成（你强调的注意点）

当 `question.kp_status='pending'`（题库没给知识点），用 Claude 归纳出知识点并挂接，全程留痕、人工终审。

**技术选型（DeepSeek）**
- 接口：DeepSeek 是 **OpenAI 兼容** 接口，用官方 `openai` SDK，`base_url="https://api.deepseek.com"`。
- 模型：`deepseek-chat`（V3，归纳分类足够、便宜）；需更强推理可临时换 `deepseek-reasoner`（R1），但本任务不必。
- 结构化输出：DeepSeek 支持 `response_format={"type":"json_object"}`（**不支持** 严格 json_schema）→ 提示里给出字段说明 + 用 **Pydantic 客户端校验**，失败重试一次。
- 省钱两招：①把“本课程已审知识点清单”放在 **system 消息最前**作稳定前缀——DeepSeek **自动上下文缓存（硬盘缓存）**，命中部分按更低价计；②**大批量回填走 DeepSeek 错峰时段**（UTC 16:30–00:30，约 5 折），并发跑即可。
- `temperature=0`，分类任务要确定性。

**生成逻辑**：先让模型在已有知识点里选；选不到再新建一个细知识点 + 归属概念，并给置信度。

```python
import os, json
from openai import OpenAI
from pydantic import BaseModel, ValidationError
from typing import Optional, Literal

client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url="https://api.deepseek.com")

class KPResult(BaseModel):
    decision: Literal["existing", "new"]
    kp_code: Optional[str] = None          # decision=existing 时回填已有码
    new_label: Optional[str] = None        # decision=new 时的新知识点名
    parent_concept_code: Optional[str] = None
    confidence: float                       # 0..1

def infer_kp(question, existing_kps, course_concepts):
    # 稳定前缀放 system，便于 DeepSeek 自动缓存命中
    system = (
        "你是课程知识点标注助手。只输出与题目直接考查的最细知识点，避免过宽。"
        "必须严格输出 JSON，字段：decision('existing'|'new'), kp_code, new_label, "
        "parent_concept_code, confidence(0-1)。\n"
        f"已有知识点(可直接选用):\n{existing_kps}\n概念层(归属用):\n{course_concepts}"
    )
    user = (
        f"题目: {question['stem']}\n选项: {question['options']}\n"
        f"正确答案: {question['correct_answer']}\n解析: {question.get('explanation','')}\n"
        "能匹配已有知识点就返回其 kp_code；否则提出一个新知识点及其归属概念。以 JSON 返回。"
    )
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}],
        response_format={"type": "json_object"},
        temperature=0,
    )
    raw = resp.choices[0].message.content
    return KPResult.model_validate_json(raw)   # 校验失败则重试一次
```

**入库与审核闭环**
1. 调用前后写 `kp_generation_log`（model / prompt / raw_response / produced_kp / confidence）。
2. `decision='new'` → upsert `knowledge_point(source='ai_generated', review_status='pending', generated_model, confidence)`。
3. 写 `question_knowledge_point(source='ai_generated', confidence, review_status='pending')`；置 `question.kp_status='pending'`。
4. 教师在前端审核列表里确认/改 → `approved`（触发第 0 节同步到图库）或 `rejected`。
5. **大批量首次回填**：DeepSeek 无批量端点——用线程/异步并发跑所有 pending 题（每题一次调用，带重试+限流），放在错峰时段降本；结果按 `question_id` 回填。

> 同理：前置边 `REQUIRES` 也可用同一套 LLM+Pydantic 草拟（输入概念清单，输出 `[{source_code, target_code, confidence, explanation}]`），写图库时 `source='ai_generated'`，教师在图谱编辑界面校对转 `approved`。

---

## 4. PostgreSQL → Neo4j 同步作业

幂等、单向、只在 approved 时触发（事件或定时批处理均可）。

```cypher
// 节点 upsert（按课程隔离）
MERGE (c:Course {course_code:$course_code})
MERGE (con:Concept {concept_code:$concept_code})
  SET con.label=$label, con.course_code=$course_code, con.difficulty=$difficulty
MERGE (c)-[:HAS_CONCEPT]->(con)
MERGE (kp:KnowledgePoint {kp_code:$kp_code})
  SET kp.label=$kp_label, kp.course_code=$course_code, kp.difficulty=$kp_diff,
      kp.source=$source, kp.review_status='approved'
MERGE (con)-[:HAS_KNOWLEDGE_POINT]->(kp)
```

`REQUIRES` 边不在此同步——它是图库自有数据，由 LLM 草拟 + 人工在图库侧维护。

---

## 5. 统一 Repository 接口

引擎只依赖一个门面 `EngineDataGateway`，内部组合关系库仓储 + 图库仓储，实现“关系库取作答 → 抽知识点 → 图库回溯”的时序。

```python
class EngineDataGateway:
    def __init__(self, sql_repo: SqlRepository, graph_repo: GraphRepository):
        self.sql = sql_repo
        self.graph = graph_repo

    async def get_responses(self, student_no: str, course_code: str) -> list[dict]:
        # question_response join question join question_knowledge_point
        ...

    async def wrong_kp_codes(self, student_no: str, course_code: str) -> list[str]:
        rs = await self.get_responses(student_no, course_code)
        return [r["kp_code"] for r in rs if r["is_correct"] is False]

    async def trace_prerequisites(self, kp_codes: list[str], course_code: str) -> dict:
        # 图库：KP→所属Concept→REQUIRES* 回溯前置概念链
        return await self.graph.prerequisites_of_kps(kp_codes, course_code)
```

诊断/画像/推荐引擎统一改成依赖 `EngineDataGateway`，不再各自直连数据源；现有那两套并行 Repository（`AbstractRepository` + 散落的 `PostgresRepository`）合并到这一层。

---

## 6. 分阶段改造步骤

| 阶段 | 工作 | 产出 |
|---|---|---|
| P0 | 落 schema：建表 + Alembic 迁移 + docker-compose 起 PG/Neo4j | 可重建的两库 |
| P1 | ETL 三类文件入库（2.1/2.2/2.3），以学号为键 | 真实数据进库，`question_response` 有逐题对错 |
| P2 | 缺知识点的 LLM 生成 + `kp_generation_log` + 教师审核界面 | KP 覆盖率补全，可追溯 |
| P3 | PG→Neo4j 同步作业 + LLM 草拟 REQUIRES 边 + 图谱校对 | 图库可做前置回溯 |
| P4 | 合并为 `EngineDataGateway`，重接五引擎，删旧的双 Repository | 引擎在真实数据上跑通 |
| P5 | 前端按 schema 重建页面（画像/图谱/分析），修 ID/proxy/类型问题 | 端到端可用 |

每阶段独立可验收；P1 完成后诊断引擎即可在真实单元测试数据上出错因。
