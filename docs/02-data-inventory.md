# 数据资产摸底 · Data Asset Inventory

> 阶段 1 的核心产出。研究生主导填写，PI 协助开门。
> Core output of Stage 1. Led by graduate students, with PI facilitating access.

---

## 一、为什么要做这件事 · Why

### 中文

这个项目的根本是"用数据说话"。但数据在哪？谁手里？什么格式？覆盖哪几届学生？
不摸清楚这些，后面所有的算法、所有的图谱、所有的报告都是空中楼阁。

**这一步看似行政性、不技术，但价值极高。**

### English

The project lives or dies by data. But where is the data? Who holds it? In what
format? Covering which cohorts? Without answering these questions, every algorithm,
every graph, every report is built on sand.

**This step looks administrative and non-technical, but its value is huge.**

---

## 二、如何进行 · How to Proceed

### 中文

1. 用下表逐项排查，**找不到的就写"未找到"**，不要瞎填
2. 每问到一个数据源，记下"谁告诉我的"、"哪天"、"在哪存的"
3. 每周五给 PI 提交一次进度
4. 遇到老师不回邮件、文件找不到，**别耗着**，直接告诉 PI

### English

1. Go through the table item by item. **Mark "Not Found" honestly**, don't fabricate.
2. For each data source, record who told you, when, and where it's stored.
3. Submit weekly progress to PI every Friday.
4. If teachers don't respond or files can't be located, **don't get stuck**—tell PI immediately.

---

## 三、目标数据清单 · Target Data Checklist

按优先级排序。**先抓 P0，再做 P1。** Sorted by priority. **P0 first, then P1.**

### P0 · 必须搞到 · Must Have

| # | 数据类型 · Data Type | 找谁 · Whom to Ask | 期望格式 · Expected Format | 状态 · Status | 备注 · Notes |
|---|---|---|---|---|---|
| 1 | 往届《线性代数》期末成绩(最近 3 年)<br>Linear Algebra final scores (last 3 yrs) | 教务处 / PI<br>Academic Office / PI | Excel | [ ] 未开始 / Not started | |
| 2 | 往届《线性代数》期末试卷 + 标准答案<br>Final exam papers + answer keys | 教研室 / 任课老师<br>Teaching group | Word / PDF | [ ] 未开始 | |
| 3 | 团队现有题库 3000+ 题<br>Existing 3000+ question bank | PI<br>PI | 待确认 / TBD | [ ] 未开始 | 申报书提到的"数学公共基础课习题库"<br>Mentioned in proposal |
| 4 | 试点学期的学生名单与班级分布<br>Pilot semester student rosters | 教务处<br>Academic Office | Excel | [ ] 未开始 | |

### P1 · 有就更好 · Nice to Have

| # | 数据类型 | 找谁 | 期望格式 | 状态 | 备注 |
|---|---|---|---|---|---|
| 5 | 往届平时作业成绩<br>Past homework scores | 任课老师 | Excel / 学习通导出 | [ ] | |
| 6 | 学习通后台行为数据<br>Xuexitong backend behavior data | 平台管理员 | CSV 导出 | [ ] | 可能需要申请 / May require request |
| 7 | PTA 平台编程作业数据<br>PTA programming submissions | 平台管理员 | API 或导出 | [ ] | 仅对 AI 基础课程相关 / Only for AI course |
| 8 | 往届学生答题卡扫描件<br>Past answer sheet scans | 教研室 | PDF / 图片 | [ ] | |
| 9 | 课程评教数据<br>Course evaluation surveys | 教务处 | Excel | [ ] | |

### P2 · 锦上添花 · Bonus

| # | 数据类型 | 找谁 | 状态 |
|---|---|---|---|
| 10 | 教师授课经验记录、教案<br>Teaching notes, lesson plans | 任课老师 | [ ] |
| 11 | 学生学情访谈、座谈记录<br>Past student interviews | PI | [ ] |
| 12 | 其他相似课程数据(高代、解析几何等)<br>Related course data | 教研室 | [ ] |

---

## 四、每项数据登记模板 · Per-Data-Source Record Template

每搞到一项数据，在仓库的 `data/raw/_inventory.md` 里新增一条：

For each acquired data source, add an entry to `data/raw/_inventory.md`:

```yaml
- id: "D001"
  type: "Linear Algebra Final Scores"
  type_cn: "线性代数期末成绩"
  cohort: "2024-2025-Fall"            # 学年学期 · Academic term
  source_person: "张三老师"            # 数据来源人 · Source person
  acquired_date: "2025-11-15"
  acquired_by: "学生 A"                # 谁拿到的 · Who got it
  format: "xlsx"
  rows: 156                            # 学生数 · Number of students
  columns: ["student_id", "name", "class", "final_score"]
  contains_pii: true                   # 含个人信息 · Contains PII
  anonymized: false                    # 是否已脱敏 · Anonymized?
  storage_path: "data/raw/D001_la_final_2024fall.xlsx"
  notes: "课程班 251、252 合班数据"     # 备注
```

---

## 五、基准数据集挑选标准 · Baseline Cohort Selection Criteria

摸底完成后，从所有数据里挑出**一届**作为基准数据集。挑选标准：

After the inventory is complete, select **one cohort** as the baseline dataset. Criteria:

1. **完整性优先 · Completeness First** — 有成绩 + 试卷 + 至少部分作业
   Has scores + exam paper + at least partial homework

2. **时间近 · Recent** — 最好 2023 年以后
   Preferably after 2023

3. **任课老师可咨询 · Accessible Instructor** — 数据有疑问时能问到人
   Original instructor reachable for questions

4. **班级规模适中 · Appropriate Class Size** — 50-100 人最佳
   50-100 students ideal

PI 最终拍板。 PI makes the final call.

---

## 六、脱敏规则 · Anonymization Rules

### 中文

1. 所有学生学号、姓名一律 SHA-256 哈希
2. salt 存在 `~/.config/project_salt.txt`，只有 PI 持有
3. 哈希后取前 16 位作为内部 ID，例如 `s_a3f5b2e1c8d4f0a9`
4. 班级名保留(无需脱敏)
5. 教师姓名保留(项目内部使用)
6. 任何对外材料(论文、PPT、demo)使用前再次审查

### English

1. All student IDs and names are hashed with SHA-256
2. Salt is stored in `~/.config/project_salt.txt`, held only by PI
3. First 16 hex chars of hash become the internal ID, e.g. `s_a3f5b2e1c8d4f0a9`
4. Class names retained (no anonymization needed)
5. Instructor names retained (internal use)
6. Any external materials (papers, slides, demos) reviewed again before use

脱敏脚本 · Anonymization script: `scripts/anonymize.py` (待开发 / TBD)

---

## 七、完成标准 · Definition of Done

- [ ] 上述清单 P0 全部状态变为"已找到"或"确认无"
      All P0 items marked "Found" or "Confirmed unavailable"
- [ ] `data/raw/_inventory.md` 至少含 5 条登记
      `data/raw/_inventory.md` contains at least 5 records
- [ ] 基准数据集已选定，PI 签字确认
      Baseline cohort selected and approved by PI
- [ ] 脱敏脚本可运行，输出可验证
      Anonymization script runs and outputs are verifiable
- [ ] `docs/05-data-ethics.md` 起草完成
      Data ethics doc drafted

---

## 八、PI 工作量预估 · PI Time Estimate

| 任务 · Task | 时间 · Time |
|---|---|
| 介绍学生认识各位老师 · Introduce students to faculty | 1 小时 / hr |
| 帮忙催数据 · Help chase down data | 2-3 小时分散 / hrs scattered |
| 审核基准数据集选择 · Approve baseline choice | 30 分钟 / min |
| 审核脱敏方案 · Approve anonymization plan | 30 分钟 / min |
| **总计 · Total** | **~5 小时 / hrs** |
