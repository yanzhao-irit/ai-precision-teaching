# AI 赋能课程学习错因诊断与靶向提质 · 关键技术与实践研究

**AI-Empowered Error Diagnosis and Targeted Quality Improvement in Course Learning**

> 浙江省高等教育 2025 年本科教学改革项目
> Zhejiang Higher Education Teaching Reform Project, 2025
> Project Period · 项目周期: 2025.11 — 2027.11

---

## 一、项目目标 · Project Goals

### 中文

围绕本科课程教学中"看不见过程、找不准错因、帮不上个体、难以持续改进"四重困境，
本项目构建"全程学习感知—精准错因诊断—靶向提质支持—循证驱动的智能教学生态"
一体化精准教学体系，并在《线性代数》与《人工智能基础》两门课程中试点验证。

### English

This project addresses four persistent challenges in undergraduate teaching:
invisible learning processes, imprecise error diagnosis, lack of individualized
support, and the absence of sustainable improvement cycles. We build an integrated
precision-teaching system covering data sensing, error diagnosis, targeted support,
and evidence-driven improvement, piloted in *Linear Algebra* and
*Foundations of Artificial Intelligence*.

---

## 二、四条工作链 · Four Work Chains

| 链 · Chain | 中文 | English |
|---|---|---|
| 数据链 · Data | 把日常教学活动嵌入式地变成结构化学习数据 | Turn daily teaching activities into structured learning data with minimal extra burden |
| 诊断链 · Diagnosis | 基于知识图谱的可解释错因诊断 | Knowledge-graph-based, explainable error diagnosis |
| 支持链 · Support | 三层人机协同的个性化学习支持 | Three-tier human-AI collaborative learning support |
| 改进链 · Improvement | 数据驱动的 PDCA 教研循环 | Data-driven PDCA cycles for teaching improvement |

---

## 三、当前阶段 · Current Stage

**阶段 1—3 进行中 · Stages 1–3 in progress**

详见 [`docs/01-execution-plan.md`](docs/01-execution-plan.md)
See [`docs/01-execution-plan.md`](docs/01-execution-plan.md) for details.

---

## 四、仓库结构 · Repository Structure

```
.
├── README.md                项目总览 · Project overview (this file)
├── docs/                    所有文档 · All documentation
│   ├── 01-execution-plan.md         六阶段执行计划 · Six-stage plan
│   ├── 02-data-inventory.md         数据资产清单 · Data inventory
│   ├── 03-kg-schema.md              知识图谱 schema · KG schema (TBD)
│   ├── 04-evaluation-plan.md        评估方案 · Evaluation plan (TBD)
│   ├── 05-data-ethics.md            数据伦理 · Data ethics (TBD)
│   ├── git-workflow.md              Git 协作规范 · Git workflow
│   ├── onboarding.md                新成员入项清单 · Onboarding checklist
│   └── meetings/                    会议纪要 · Meeting notes
├── data/                    数据 · Data (mostly gitignored)
│   ├── README.md                    数据获取说明 · Data access notes
│   ├── raw/                         原始数据 · Raw data
│   ├── baseline-cohort/             基准学生数据 · Baseline cohort data
│   ├── kg/                          知识图谱数据 · Knowledge graph data
│   └── question-bank/               题库 · Question bank
├── src/                     代码 · Source code
│   ├── kg/                          知识图谱工具 · KG tools
│   ├── diagnosis/                   诊断算法 · Diagnosis algorithms
│   └── utils/                       通用工具 · Utilities
├── notebooks/               Jupyter 实验本 · Jupyter notebooks
├── scripts/                 一次性脚本 · One-off scripts
├── infra/                   基础设施 · Infrastructure
└── requirements.txt         Python 依赖 · Python dependencies
```

---

## 五、谁在做什么 · Who Does What

| 角色 · Role | 中文 | English |
|---|---|---|
| 项目负责人 · PI | 赵妍（总体推进、教学决策、对外接口） | Zhao Yan (overall coordination, teaching decisions) |
| 教学顾问 · Teaching Advisor | 涂黎晖（教学设计指导，每月 2-4 小时） | Tu Lihui (teaching design guidance, 2-4 hrs/month) |
| 技术顾问 · Tech Advisor | 陈根浪（技术架构咨询） | Chen Genlang (architecture consulting) |
| 知识图谱顾问 · KG Advisor | 许立波(知识图谱方法咨询) | Xu Libo (knowledge graph methodology) |
| 系统开发顾问 · System Advisor | 杨宇照(系统开发咨询) | Yang Yuzhao (system development consulting) |
| 研究生 · Graduate Students | 当前阶段主要劳动力 | Primary contributors at current stage |

**注 · Note:** 顾问老师每月可咨询时间有限，请提前用 issue 或邮件准备好问题。
Advisor time is limited (~2-4 hrs/month). Prepare questions in advance via issues or email.

---

## 六、数据访问 · Data Access

所有学生数据已脱敏。原始 ID 映射表只有 PI 持有。
研究生只接触脱敏数据。`data/` 目录中的原始数据不进入 git，通过单独的安全通道传输。

All student data is anonymized. Real ID mappings are held only by the PI.
Graduate students access only anonymized data. Raw data in the `data/` directory
is gitignored and transferred through a separate secure channel.

详见 · See [`docs/05-data-ethics.md`](docs/05-data-ethics.md)

---

## 七、新成员从这里开始 · Onboarding

1. 阅读本 README · Read this README
2. 阅读 [`docs/01-execution-plan.md`](docs/01-execution-plan.md) 了解整体路线
   Read the execution plan for the big picture
3. 阅读 [`docs/onboarding.md`](docs/onboarding.md) 按清单逐项完成
   Follow the onboarding checklist
4. 找 PI 拿到当前阶段的具体任务 · Get your current-stage tasks from PI

---

## 八、引用 · How to Cite

如果本项目对你有帮助，请引用：

```bibtex
@misc{zhao2025aiteaching,
  author = {Zhao, Yan and others},
  title  = {AI-Empowered Error Diagnosis and Targeted Quality Improvement in Course Learning},
  year   = {2025-2027},
  note   = {Zhejiang Higher Education Teaching Reform Project}
}
```

---

## 九、联系 · Contact

PI: 赵妍 · Zhao Yan · zhaoyan@nbt.edu.cn
