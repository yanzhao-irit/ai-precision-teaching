# 数据目录 · Data Directory

## 重要 · IMPORTANT

**原始数据不进入 git。** 请联系 PI 获取数据访问权限。

**Raw data is NOT committed to git.** Contact PI for data access.

---

## 目录结构 · Directory Structure

```
data/
├── README.md                  本文件 · This file
├── raw/                       原始数据(已脱敏)· Raw data (anonymized)
│   ├── _inventory.md          数据登记本 · Data registry (in git)
│   └── ...                    具体数据文件 · Actual data files (NOT in git)
├── baseline-cohort/           基准学生数据集 · Baseline cohort dataset
├── kg/                        知识图谱数据 · Knowledge graph data
│   └── linear-algebra/
│       ├── knowledge_points.csv      ← 进入 git · in git
│       ├── relations.csv             ← 进入 git · in git
│       └── misconceptions.csv        ← 进入 git · in git
└── question-bank/             题库 · Question bank
    └── core_set.jsonl                ← 标注后进入 git · in git after annotation
```

---

## 进入 git 的数据 · Data IN Git

- 知识图谱 CSV(知识点、关系、误区)— 不含学生信息 · No student info
- 题库核心集(已脱敏)· Anonymized core question set
- `_inventory.md` 数据登记本(只是元数据)· Just metadata

## 不进入 git 的数据 · Data NOT In Git

- 任何含真实学号、姓名的文件 · Anything with real IDs or names
- 学生答题记录、成绩单 · Student answers, score sheets
- 原始 Excel / CSV / PDF · Original Excel/CSV/PDF files
- 模型训练 checkpoint · Model checkpoints
- 任何 >10MB 的文件 · Any file larger than 10MB

---

## 获取数据 · Getting Data

1. 联系 PI 获取数据共享方式(校内 NAS / 加密 U 盘 / 学校 OneDrive)
   Contact PI for data sharing method (NAS / encrypted USB / OneDrive)

2. 把数据放到本地的 `data/raw/` 目录
   Place data in your local `data/raw/` directory

3. 运行脱敏脚本 · Run the anonymization script:
   ```bash
   python scripts/anonymize.py --input data/raw/<file> --output data/raw/<file>.anonymized
   ```

4. 在 `data/raw/_inventory.md` 登记 · Register in `_inventory.md`

---

## 安全规则 · Security Rules

1. 数据只能存在你的工作电脑上，不要传云盘 · Local only, no cloud sync
2. 离开座位锁屏 · Lock screen when away
3. 项目结束时所有本地数据需删除 · Delete all local data when project ends
4. 任何外发(论文配图、PPT)前找 PI 审查 · PI review before any external use
