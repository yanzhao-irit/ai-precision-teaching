# 动手指南 · Hands-On Guide

> **中文：** 这份手册假设你**完全没做过类似项目**。每一步都有具体命令，照着抄就行。遇到不懂的词，先往下读，大部分会在后面解释。
>
> **English:** This manual assumes you have **never done a project like this**. Every step has concrete commands to copy. If a term is unfamiliar, keep reading—most are explained later.

---

## 目录 · Table of Contents

- [Part 0 · 心态与全局 · Mindset & Big Picture](#part-0)
- [Part 1 · 搭建开发环境 · Environment Setup](#part-1)
- [Part 2 · 阶段 1：数据资产摸底 · Stage 1: Data Inventory](#part-2)
- [Part 3 · 阶段 2：知识图谱 · Stage 2: Knowledge Graph](#part-3)
- [Part 4 · 每天/每周怎么工作 · Daily & Weekly Rhythm](#part-4)
- [Part 5 · 常见问题 · Troubleshooting](#part-5)


---

<a name="part-0"></a>
## Part 0 · 心态与全局 · Mindset & Big Picture

### 三件最重要的事 · Three Most Important Things

**第一：不要怕做错。**
代码写错了能改，git 能撤销，数据有备份。唯一不能错的是**学生隐私**——任何含真实姓名/学号的文件，绝不上传 git、绝不外发。

**First: Don't fear mistakes.**
Code can be fixed, git can undo, data is backed up. The one thing you must never get wrong is **student privacy**—never upload or share any file containing real names or student IDs.

---

**第二：小步前进，频繁提交。**
做一点，commit 一点，push 一点。不要憋一周再交。

**Second: Small steps, frequent commits.**
Do a little, commit, push. Don't hoard a week's work and submit it all at once.

---

**第三：卡住 2 小时就求助。**
先 Google + 问 AI（DeepSeek/ChatGPT/Claude 都行），还不行就写进 GitHub Issue 找同伴，再不行找 PI。**不要自己硬扛一整天。**

**Third: Stuck for 2 hours? Ask for help.**
Google + ask AI first (DeepSeek/ChatGPT/Claude all work), then open a GitHub Issue for a peer, then go to the PI. **Don't suffer alone for a whole day.**

---

### 我们做事的顺序 · Order of Work

```
先搭环境 (Part 1)
Set up environment (Part 1)
  ↓
阶段 1：数据摸底 (Part 2)  ← 这部分不太需要写代码
Stage 1: Data inventory (Part 2)  ← Little coding needed
  ↓
阶段 2：知识图谱 (Part 3)  ← 这部分开始真正写代码
Stage 2: Knowledge graph (Part 3)  ← Real coding begins here
```

---

### 文件夹和代码放在哪 · Where Files and Code Go

```
ai-precision-teaching/         ← 仓库根目录 · Repo root
├── docs/                      ← 所有文档，包括这份手册 · All docs, including this guide
├── data/                      ← 数据（大部分不进 git）· Data (mostly gitignored)
│   ├── raw/                   ← 原始数据，收到立刻脱敏 · Raw data, anonymize immediately
│   ├── baseline-cohort/       ← 基准数据集 · Baseline cohort
│   └── kg/linear-algebra/     ← 知识图谱 CSV · KG CSV files
├── src/                       ← 我们写的代码 · Our source code
│   ├── kg/                    ← 知识图谱相关代码 · KG-related code
│   └── utils/                 ← 工具函数 · Utility functions
├── scripts/                   ← 一次性脚本，如脱敏工具 · One-off scripts
├── notebooks/                 ← Jupyter 实验本 · Jupyter notebooks
└── infra/
    └── docker-compose.yml     ← 启动 Neo4j 用 · Used to start Neo4j
```


---

<a name="part-1"></a>
## Part 1 · 搭建开发环境 · Environment Setup

> **中文：** 目标是装好所有工具，能跑通一个"hello world"。预计半天到一天。遇到报错不要慌，把报错文字复制到 Google 搜索，基本都有答案。
>
> **English:** Goal: install all tools and run a "hello world". Expect half a day to a day. Don't panic at error messages—copy the error text into Google; there's almost always an answer.

### 1.1 安装 Python · Install Python

**中文：** 我们用 Python 3.11 版本。

**English:** We use Python version 3.11.

**Windows 系统 · Windows:**

1. 去 `https://www.python.org/downloads/` 下载 Python 3.11.x
   Go to `https://www.python.org/downloads/` and download Python 3.11.x

2. 运行安装程序，**务必勾选** "Add Python to PATH"（这步漏掉后面会出问题）
   Run the installer and **check "Add Python to PATH"** (skipping this causes problems later)

3. 安装完，打开命令提示符（在开始菜单搜索 "cmd"），输入：
   After installing, open Command Prompt (search "cmd" in Start menu) and type:
   ```
   python --version
   ```
   看到 `Python 3.11.x` 就成功了。
   If you see `Python 3.11.x`, it worked.

**Mac 系统 · Mac:**

1. 先安装 Homebrew（如果没有）：打开终端（Terminal），运行：
   First install Homebrew (if not installed): open Terminal and run:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. 然后安装 Python：
   Then install Python:
   ```bash
   brew install python@3.11
   python3.11 --version
   ```

---

### 1.2 安装 VS Code · Install VS Code

**中文：** VS Code 是我们写代码的编辑器，免费、好用。

**English:** VS Code is our code editor—free and excellent.

1. 下载地址 · Download: `https://code.visualstudio.com`

2. 安装完打开 VS Code，点左侧扩展图标（四个方块），搜索并安装：
   After installing, open VS Code, click the Extensions icon (four squares) on the left, search and install:

   | 扩展名 · Extension | 用途 · Purpose |
   |---|---|
   | Python（微软官方 · by Microsoft） | 运行 Python 代码 · Run Python code |
   | Jupyter | 运行 Jupyter 笔记本 · Run Jupyter notebooks |
   | Markdown All in One | 更好地阅读文档 · Better markdown reading |

---

### 1.3 安装 Docker · Install Docker

**中文：** Docker 用来运行 Neo4j 知识图谱数据库。你不需要深入理解 Docker，会启动/停止就够了。

**English:** Docker runs our Neo4j knowledge graph database. You don't need to understand Docker deeply—just know how to start and stop it.

1. 下载 Docker Desktop · Download: `https://www.docker.com/products/docker-desktop`

2. 安装后启动它（Windows 可能需要重启电脑）
   After installing, launch it (Windows may require a restart)

3. 验证安装 · Verify:
   ```bash
   docker --version
   ```
   看到版本号说明成功。 · Seeing a version number means success.

> **注意 · Note:**
> **中文：** Docker Desktop 必须保持在后台运行，Neo4j 才能工作。每次开机如果需要用 Neo4j，先打开 Docker Desktop。
>
> **English:** Docker Desktop must keep running in the background for Neo4j to work. Open Docker Desktop first whenever you need Neo4j.

---

### 1.4 配置项目环境 · Set Up Project Environment

**中文：** 假设你已经按 `docs/git-workflow.md` 把仓库 clone 到了本地，现在做下面的事：

**English:** Assuming you've already cloned the repo locally following `docs/git-workflow.md`. Now do the following:

**第一步：用 VS Code 打开项目文件夹 · Step 1: Open the project folder in VS Code**

VS Code → File（文件）→ Open Folder（打开文件夹）→ 选 `ai-precision-teaching` 文件夹
VS Code → File → Open Folder → select the `ai-precision-teaching` folder

**第二步：打开终端 · Step 2: Open terminal**

VS Code 顶部菜单 Terminal（终端）→ New Terminal（新终端）
VS Code top menu: Terminal → New Terminal

下面会出现一个命令行窗口，后续所有命令都在这里输入。
A command-line panel will appear at the bottom. Type all commands here.

**第三步：创建虚拟环境 · Step 3: Create virtual environment**

**中文：** 虚拟环境是给这个项目单独安装依赖的"隔离盒子"，不会和其他项目或系统 Python 冲突。

**English:** A virtual environment is an isolated "box" for installing this project's dependencies, preventing conflicts with other projects or system Python.

```bash
# Windows 系统 · Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux 系统 · Mac/Linux
python3.11 -m venv .venv
source .venv/bin/activate
```

成功后，命令行最前面会出现 `(.venv)` 字样，表示虚拟环境已激活。
On success, you'll see `(.venv)` at the start of your command line—the venv is active.

> **重要提醒 · Important:**
> **中文：** 每次重新打开 VS Code 或新开终端窗口，都要重新运行一次 activate 命令。
>
> **English:** Every time you reopen VS Code or open a new terminal, re-run the activate command.

**第四步：安装依赖 · Step 4: Install dependencies**

```bash
pip install -r requirements.txt
```

**中文：** 这会自动安装 pandas、neo4j 驱动等所有需要的库。第一次比较慢，耐心等 3-5 分钟。

**English:** This automatically installs pandas, the neo4j driver, and all other required libraries. The first time is slow—wait 3-5 minutes.

如果网络慢，换国内镜像 · If slow, use a Chinese mirror:
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**第五步：验证安装 · Step 5: Verify**

```bash
python -c "import pandas; print('环境 OK · Environment OK')"
```

看到 `环境 OK · Environment OK` 就成功了。
If you see this message, the environment is ready.

---

### 1.5 启动 Neo4j · Start Neo4j

**中文：** 确认 Docker Desktop 正在运行，然后执行：

**English:** Confirm Docker Desktop is running, then run:

```bash
cd infra
docker compose up -d
```

**中文：** `-d` 表示在后台运行，不占用终端窗口。等 30 秒后，打开浏览器访问：

**English:** `-d` means run in background. Wait 30 seconds, then open a browser and go to:

```
http://localhost:7474
```

**中文：** 会看到 Neo4j 的登录界面，输入：

**English:** You'll see the Neo4j login screen. Enter:

- 用户名 · Username: `neo4j`
- 密码 · Password: `devpassword`

登录成功说明 Neo4j 已在运行。 · Successful login means Neo4j is running.

> **注意 · Note:**
> **中文：** 第一次登录可能会提示修改密码。如果改了，记住新密码，并把后面所有代码里的 `devpassword` 换成你的新密码。
>
> **English:** The first login may prompt a password change. If you change it, remember the new one and replace all `devpassword` in code files.

**停止 Neo4j · Stop Neo4j:**
```bash
cd infra
docker compose down
```

---

### 1.6 配置 DeepSeek API · Set Up DeepSeek API

**中文：** 阶段 2 要用大语言模型辅助生成知识点草稿，我们用 DeepSeek。

**English:** Stage 2 uses a large language model to generate knowledge-point drafts. We use DeepSeek.

**第一步：获取 API Key · Step 1: Get the API Key**

**中文：** 找 PI 拿 API Key。PI 会去 `https://platform.deepseek.com` 注册充值，然后把 Key 发给你。

**English:** Ask the PI for the API Key. The PI registers at `https://platform.deepseek.com` and sends you the key.

**第二步：创建 `.env` 文件 · Step 2: Create the `.env` file**

**中文：** 在 VS Code 里右键项目根目录 → New File → 命名为 `.env`（注意有个点）。内容写：

**English:** In VS Code, right-click the project root → New File → name it `.env` (note the leading dot). Contents:

```
DEEPSEEK_API_KEY=sk-你拿到的key粘贴在这里
DEEPSEEK_API_KEY=sk-paste-your-key-here
```

> **极其重要 · CRITICAL:**
> **中文：** `.env` 已被 `.gitignore` 忽略，**永远不会上传 GitHub**。绝对不要把 API Key 写进任何代码文件！
>
> **English:** `.env` is gitignored and will **never be uploaded to GitHub**. Never hardcode the API Key in any code file!

**第三步：测试 API · Step 3: Test the API**

**中文：** 新建文件 `scripts/test_api.py`，贴入：

**English:** Create `scripts/test_api.py` and paste:

```python
# 测试 DeepSeek API 是否配置成功 · Test that DeepSeek API is configured correctly
import os
from dotenv import load_dotenv
from openai import OpenAI

# 读取 .env 文件里的 API Key · Load the API Key from the .env file
load_dotenv()

# 创建客户端，DeepSeek 兼容 OpenAI 接口 · DeepSeek is compatible with the OpenAI interface
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

# 发送测试请求 · Send a test request
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "用一句话介绍线性代数。Describe linear algebra in one sentence."}],
)

# 打印回复 · Print the reply
print(response.choices[0].message.content)
```

运行 · Run:
```bash
python scripts/test_api.py
```

**中文：** 看到模型回复的一句话，说明 API 配置成功。

**English:** If you see a sentence from the model, the API is working correctly.

---

### 1.7 环境搭建完成检查表 · Environment Setup Checklist

**中文：** 下面每一项都要打勾，才算环境搭建完成，才能继续后面的步骤。

**English:** Every item below must be checked before the environment is ready. Only then proceed.

| 检查项 · Check Item | 验证方法 · How to Verify |
|---|---|
| Python 3.11 已安装 · Python 3.11 installed | `python --version` 显示 3.11.x · shows 3.11.x |
| VS Code 三个扩展已装 · Three VS Code extensions installed | Python + Jupyter + Markdown All in One |
| Docker 已安装 · Docker installed | `docker --version` 有输出 · shows output |
| 虚拟环境已激活 · Venv activated | 命令行前出现 `(.venv)` · `(.venv)` at prompt |
| 依赖已安装 · Dependencies installed | `pip install -r requirements.txt` 无报错 · no errors |
| Neo4j 可访问 · Neo4j accessible | 浏览器能打开 localhost:7474 · browser opens |
| DeepSeek API 可用 · API working | `python scripts/test_api.py` 收到模型回复 · gets a reply |

**中文：** 这一步搞定，后面就顺了。任何一项卡住，先看 Part 5 常见问题，再找 PI。

**English:** Once this is done, everything else flows more smoothly. If any item is stuck, see Part 5, then ask the PI.


---

<a name="part-2"></a>
## Part 2 · 阶段 1 实操：数据资产摸底 · Stage 1: Data Inventory

> **中文：** 这部分大半是"行政活"——发邮件、收文件、填表。不太需要写代码。详细背景见 `docs/02-data-inventory.md`，这里讲**具体怎么动手**。
>
> **English:** This stage is mostly "administrative"—sending emails, collecting files, filling tables. Little coding needed. See `docs/02-data-inventory.md` for background; here we cover **what to actually do**.

### 2.1 第一天：理清楚要找什么 · Day 1: Clarify What to Find

**任务 · Task:**
**中文：** 搞清楚要找哪些数据、找谁要。
**English:** Understand which data is needed and who to ask for it.

**具体动作 · Concrete actions:**

1. 打开 `docs/02-data-inventory.md`，仔细看那张数据清单表。
   Open `docs/02-data-inventory.md` and read the data checklist carefully.

2. 和 PI 开一个 30 分钟的会，逐条确认"找谁要"和"PI 是否帮你引荐"。
   Have a 30-minute meeting with PI to confirm who has each item and whether PI will introduce you.

3. 把结论记在 `docs/meetings/` 下新建的当天纪要文件里。
   Record conclusions in a new meeting notes file under `docs/meetings/`.

**产出 · Output:**
**中文：** 一份清楚的"我要去问谁、问什么"的名单。
**English:** A clear list of "who to ask and what to ask for."

---

### 2.2 第二、三天：联系老师收集数据 · Days 2-3: Contact Faculty and Collect Data

**任务 · Task:**
**中文：** 联系相关老师，收集 P0 数据（最重要的）。
**English:** Contact relevant faculty and collect P0 data (the most important items).

**发消息模板 · Message template:**

```
【中文版】
X 老师您好，

我是赵妍老师教改项目的研究生。项目需要用到往届《线性代数》的
期末成绩和试卷做研究分析（所有数据都会脱敏处理，不涉及学生
个人隐私）。

请问您手上有没有近几年的相关数据？方便的话能否发我一份？

感谢您的支持！

[English version]
Dear Prof. X,

I am a graduate student working on Prof. Zhao Yan's teaching reform
project. We need past Linear Algebra final scores and exam papers for
research analysis. All data will be fully anonymized before use.

Do you have data from recent years? If convenient, could you share a copy?

Thank you very much for your support.
```

**收到数据后立刻做两件事 · Immediately upon receiving data:**

1. **登记 · Register:** 在 `data/raw/_inventory.md` 里按模板新增一条记录。
   Add a new entry in `data/raw/_inventory.md` following the template.

2. **存放 · Store:** 把文件放到本地的 `data/raw/` 文件夹里。
   Place the file in your local `data/raw/` folder.

> **注意 · Note:**
> **中文：** `data/raw/` 已被 git 忽略，文件不会被上传，可以放心存原始数据。
>
> **English:** `data/raw/` is gitignored, so files there will never be uploaded. You can safely store raw data here.

**老师不回复怎么办 · If a teacher doesn't reply:**
**中文：** 等 2 天没有回音，立刻告诉 PI，让 PI 出面催。不要自己干等超过 2 天。
**English:** If there's no reply after 2 days, tell the PI immediately to follow up. Don't wait alone for more than 2 days.

---

### 2.3 写脱敏脚本 · Write the Anonymization Script

**任务 · Task:**
**中文：** 收到含真实姓名/学号的数据后，第一件事就是脱敏。
**English:** After receiving data with real names/IDs, the very first action is to anonymize it.

**中文：** 新建文件 `scripts/anonymize.py`，贴入以下完整代码：
**English:** Create `scripts/anonymize.py` and paste the complete code below:

```python
"""
学生数据脱敏脚本 · Student Data Anonymization Script

功能说明 · Description:
  把数据文件中指定的 ID 列（学号）替换为不可逆的哈希 ID。
  Replace the specified ID column (student ID) with an irreversible hash ID.

  同一个 salt + 同一个学号，每次都会得到相同的哈希 ID，
  这样跨多个文件（成绩表、作业表）能对应上同一个学生。
  The same salt + same student ID always produces the same hash ID,
  so students can be matched across multiple files (scores, homework, etc.).

用法 · Usage:
  python scripts/anonymize.py \
      --input  data/raw/scores.xlsx \
      --output data/raw/scores_anon.xlsx \
      --id-column 学号 \
      --drop-columns 姓名
"""

import argparse
import hashlib
import os
from pathlib import Path
import pandas as pd

# Salt 文件路径，只有 PI 知道 · Salt file path, known only to PI
SALT_FILE = Path.home() / ".config" / "project_salt.txt"


def get_salt() -> str:
    """读取 salt，没有则生成并保存 · Read salt; generate and save if absent."""
    SALT_FILE.parent.mkdir(parents=True, exist_ok=True)
    if SALT_FILE.exists():
        return SALT_FILE.read_text().strip()
    salt = hashlib.sha256(os.urandom(32)).hexdigest()
    SALT_FILE.write_text(salt)
    print(f"⚠️  已生成新 salt 并保存到 · New salt saved to: {SALT_FILE}")
    print("⚠️  请立刻把这个文件路径告诉 PI 并备份！")
    print("⚠️  Immediately tell PI and back up this file!")
    return salt


def hash_id(real_id: str, salt: str) -> str:
    """把真实学号转成 16 字符哈希 ID · Convert real ID to 16-char hash ID."""
    raw = f"{real_id}{salt}".encode("utf-8")
    return "s_" + hashlib.sha256(raw).hexdigest()[:16]


def main():
    parser = argparse.ArgumentParser(
        description="学生数据脱敏工具 · Student data anonymization tool"
    )
    parser.add_argument("--input",        required=True, help="输入文件 · Input file")
    parser.add_argument("--output",       required=True, help="输出文件 · Output file")
    parser.add_argument("--id-column",    required=True, help="要哈希的列名，通常是'学号' · Column to hash")
    parser.add_argument("--drop-columns", nargs="*", default=[],
                        help="要删除的列名，如'姓名' · Columns to delete, e.g. name")
    args = parser.parse_args()

    salt = get_salt()

    # 读取文件 · Read file (dtype=str prevents student IDs from being parsed as numbers)
    df = pd.read_excel(args.input, dtype=str) if not args.input.endswith(".csv") \
         else pd.read_csv(args.input, dtype=str)
    print(f"读取 {len(df)} 行 · Read {len(df)} rows from {args.input}")

    if args.id_column not in df.columns:
        print(f"❌ 找不到列'{args.id_column}' · Column not found. Available: {list(df.columns)}")
        return

    # 哈希 ID 列 · Hash the ID column
    sample_before = df[args.id_column].iloc[0]
    df[args.id_column] = df[args.id_column].apply(lambda x: hash_id(str(x), salt))
    sample_after = df[args.id_column].iloc[0]
    print(f"✅ 已哈希'{args.id_column}'（例 · e.g.: {sample_before} → {sample_after}）")

    # 删除敏感列 · Drop sensitive columns
    for col in args.drop_columns:
        if col in df.columns:
            df = df.drop(columns=[col])
            print(f"✅ 已删除列 · Dropped column: '{col}'")

    # 保存脱敏文件 · Save anonymized file
    if args.output.endswith(".csv"):
        df.to_csv(args.output, index=False, encoding="utf-8-sig")
    else:
        df.to_excel(args.output, index=False)
    print(f"✅ 脱敏文件已保存 · Saved: {args.output}")
    print("   原始文件请妥善保管，不要上传 git · Keep original file secure, never git-commit it")


if __name__ == "__main__":
    main()
```

**用法举例 · Example usage:**
**中文：** 假设收到成绩表 `scores.xlsx`，里面有"学号"和"姓名"列：
**English:** Suppose you received `scores.xlsx` with columns "学号" (student ID) and "姓名" (name):

```bash
python scripts/anonymize.py \
    --input data/raw/scores.xlsx \
    --output data/raw/scores_anon.xlsx \
    --id-column 学号 \
    --drop-columns 姓名
```

**中文：** 运行后生成 `scores_anon.xlsx`，学号变成 `s_a3f5...`，姓名列被删掉。之后只用脱敏版本工作。
**English:** This produces `scores_anon.xlsx` where IDs become `s_a3f5...` and the name column is deleted. From now on, only work with this anonymized version.

---

### 2.4 选定基准数据集 · Select Baseline Cohort

**任务 · Task:**
**中文：** 和 PI 一起从收集到的数据里挑**一届最完整的**作为基准数据集。所有后续算法实验都在这上面跑。
**English:** Work with PI to select **the most complete cohort** as the baseline dataset. All subsequent algorithm experiments run on this.

**挑选标准 · Selection criteria:**

| 标准 · Criterion | 说明 · Description |
|---|---|
| 数据完整 · Complete | 有成绩 + 试卷 + 至少部分作业 · Has scores + exam + at least partial homework |
| 时间较近 · Recent | 最好 2023 年以后 · Preferably after 2023 |
| 老师可咨询 · Instructor reachable | 有疑问时能找到当时任课老师 · Original instructor available |
| 规模适中 · Appropriate size | 50-100 人最佳 · 50-100 students ideal |

**中文：** PI 最终决定选哪届。选定后，把脱敏数据放到 `data/baseline-cohort/`，并在该目录新建 `README.md` 说明数据情况。
**English:** The PI makes the final call. Once selected, put anonymized data in `data/baseline-cohort/` and create a `README.md` there describing the data.

---

### 2.5 阶段 1 完成标准 · Stage 1 Done Checklist

| 检查项 · Check Item | 完成 · Done |
|---|---|
| `data/raw/_inventory.md` 至少登记 5 条 · At least 5 items registered | [ ] |
| P0 数据全部"已找到"或"确认无" · All P0 items found or confirmed unavailable | [ ] |
| 脱敏脚本可成功运行 · Anonymization script runs successfully | [ ] |
| 基准数据集已整理，PI 已确认 · Baseline cohort organized, PI approved | [ ] |

**中文：** 全部完成后，在 GitHub Desktop 做一次 commit + push，message 写：
**English:** Once all done, do a commit + push in GitHub Desktop with the message:

```
data+docs: complete stage-1 data inventory and baseline selection
```


---

<a name="part-3"></a>
## Part 3 · 阶段 2 实操：知识图谱 · Stage 2: Knowledge Graph

> **中文：** 这是项目的核心，也是真正开始写代码的地方。我们只做**线性代数前 3 章**，先把这 3 章做扎实，再说扩展。
>
> **English:** This is the project's core, and where real coding begins. We do **only Linear Algebra Chapters 1-3**—nail these first, then expand.

### 整体流程 · Overall Flow

```
步骤 1: 理解 schema（数据结构设计）
Step 1: Understand the schema (data structure design)
  ↓
步骤 2: 准备教材文本
Step 2: Prepare textbook text
  ↓
步骤 3: 用 LLM 生成知识点草稿
Step 3: Generate KP drafts with LLM
  ↓
步骤 4: 人工审核 + 标注关系（和 PI、涂老师一起）
Step 4: Manual review + annotate relations (with PI and Prof. Tu)
  ↓
步骤 5: 整理成 CSV 文件
Step 5: Organize into CSV files
  ↓
步骤 6: 导入 Neo4j 数据库
Step 6: Import into Neo4j database
  ↓
步骤 7: 写 Python 查询客户端
Step 7: Write Python query client
```

---

### 3.1 理解 Schema · Understand the Schema

**中文：** Schema 就是"我们要存什么、怎么存"的设计图。我们的知识图谱有两种节点、四种关系。
**English:** Schema is the blueprint for "what we store and how." Our KG has two node types and four relation types.

**节点类型 · Node Types:**

| 节点 · Node | 中文含义 · CN | 属性 · Properties |
|---|---|---|
| `KnowledgePoint` | 知识点 · Knowledge Point | id, name, name_en, chapter, difficulty(1-5), description |
| `Misconception` | 常见误区 · Common Misconception | id, kp_id, description |

**关系类型 · Relation Types:**

| 关系 · Relation | 中文含义 · CN | 英文含义 · EN | 例子 · Example |
|---|---|---|---|
| `PREREQUISITE_OF` | A 是 B 的前置 | A must be learned before B | 矩阵乘法 → 逆矩阵 |
| `RELATED_TO` | A 和 B 相关 | A relates to B | 行列式 ↔ 矩阵 |
| `EASILY_CONFUSED_WITH` | A 和 B 容易混淆 | A easily confused with B | 行列式 ↔ 矩阵（经常混） |
| `HAS_MISCONCEPTION` | 知识点包含某误区 | KP has a misconception | 矩阵乘法 → "以为满足交换律" |

**中文：** 现在新建文件 `docs/03-kg-schema.md`，把上面的表格和几个具体例子写进去。这是阶段 2 第一周的文档交付物。
**English:** Now create `docs/03-kg-schema.md` with the tables above and a few concrete examples. This is the document deliverable for Week 1 of Stage 2.

---

### 3.2 准备教材文本 · Prepare Textbook Text

**中文：** 找 PI 拿同济版第六版《线性代数》电子版（PDF）。把前 3 章的文字提取出来：
**English:** Ask PI for the digital version of Tongji 6th Ed. Linear Algebra (PDF). Extract text from the first 3 chapters:

- 如果 PDF 可以复制文字：直接选中复制即可
  If the PDF allows text selection: select and copy directly
- 如果是扫描版不能复制：告诉 PI，PI 会想办法
  If it's a scanned PDF: tell PI, who will find a solution

**存放位置 · Where to save:**
```
data/kg/linear-algebra/chapter1_text.txt
data/kg/linear-algebra/chapter2_text.txt
data/kg/linear-algebra/chapter3_text.txt
```

> **注意 · Note:**
> **中文：** 教材文本不进 git（版权问题）。`.gitignore` 已忽略 `*_text.txt`。
>
> **English:** Textbook text stays out of git (copyright). `.gitignore` already ignores `*_text.txt`.

---

### 3.3 用 LLM 生成知识点草稿 · Generate KP Drafts with LLM

**任务 · Task:**
**中文：** 把教材章节喂给 DeepSeek，让它列出知识点候选清单。记住：这只是**草稿**，必须人工审核。
**English:** Feed textbook chapters to DeepSeek to generate candidate KP lists. Remember: this is just a **draft**—human review is mandatory.

**中文：** 新建文件 `src/kg/extract_kp.py`：
**English:** Create `src/kg/extract_kp.py`:

```python
"""
用 LLM 从教材章节抽取知识点草稿
Extract knowledge-point drafts from textbook chapters using an LLM.

说明 · Description:
  把教材章节文字发给 DeepSeek，要求以 JSON 格式返回知识点列表。
  输出是草稿，必须经过人工审核后才能使用。
  Sends textbook chapter text to DeepSeek and asks for a JSON knowledge-point list.
  Output is a draft and must be reviewed by humans before use.

用法 · Usage:
  python src/kg/extract_kp.py \
      --chapter 1 \
      --input  data/kg/linear-algebra/chapter1_text.txt \
      --output data/kg/linear-algebra/chapter1_kp_draft.json
"""

import argparse
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

# 读取 .env 里的 API Key · Load API Key from .env
load_dotenv()

# 初始化 DeepSeek 客户端 · Initialize DeepSeek client
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

# -----------------------------------------------------------------------
# Prompt 模板 · Prompt Template
# 中文：如果生成效果不好，可以修改这里。
# English: Edit here if generation quality is poor.
# -----------------------------------------------------------------------
PROMPT_TEMPLATE = """你是一位资深线性代数教师，正在为课程构建知识图谱。

请阅读以下章节内容，提取核心知识点。要求：
- 粒度：每个知识点是一个本科生 15-30 分钟能掌握的独立学习单元
- 只提取概念性、方法性知识点，不要把具体例题列为知识点
- 每章提取约 15-25 个知识点
- 每个知识点包含：
  - name: 中文名称
  - name_en: 英文名称
  - difficulty: 难度 1-5（1 最容易，5 最难）
  - description: 一句话描述
  - prerequisites: 前置知识点名称列表（可为空列表）
  - common_misconceptions: 常见误区 2-3 条

严格输出 JSON 数组，不要任何额外文字，不要 markdown 代码块标记。

章节内容：
{chapter_text}
"""


def main():
    parser = argparse.ArgumentParser(
        description="从教材章节生成知识点草稿 · Generate KP drafts from textbook chapter"
    )
    parser.add_argument("--chapter", required=True,
                        help="章节编号，如 1、2、3 · Chapter number, e.g. 1, 2, 3")
    parser.add_argument("--input",   required=True,
                        help="章节文本文件路径 · Chapter text file path")
    parser.add_argument("--output",  required=True,
                        help="输出 JSON 草稿路径 · Output JSON draft path")
    args = parser.parse_args()

    # 读取章节文本 · Read chapter text
    print(f"读取章节文本 · Reading: {args.input}")
    with open(args.input, "r", encoding="utf-8") as f:
        chapter_text = f.read()
    print(f"  文本长度 · Length: {len(chapter_text)} 字符/characters")

    # 调用 LLM · Call LLM
    print("调用 DeepSeek，请稍候约 30 秒 · Calling DeepSeek, please wait ~30 seconds...")
    prompt = PROMPT_TEMPLATE.format(chapter_text=chapter_text)
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,   # 低温度让输出更稳定 · Low temperature for stable output
        max_tokens=4000,   # 给足空间输出完整列表 · Enough for complete list
    )
    raw = response.choices[0].message.content.strip()

    # 清理可能的 markdown 标记 · Strip possible markdown fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    # 解析 JSON · Parse JSON
    try:
        kp_list = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析失败 · JSON parse failed: {e}")
        print("  原始输出已保存到 .raw.txt 供检查 · Raw output saved to .raw.txt")
        with open(args.output + ".raw.txt", "w", encoding="utf-8") as f:
            f.write(raw)
        return

    # 给每个知识点加章节号和 ID · Add chapter number and ID to each KP
    for i, kp in enumerate(kp_list, start=1):
        kp["chapter"] = int(args.chapter)
        kp["id"] = f"LA-CH{args.chapter}-KP{i:02d}"
        kp["human_reviewed"] = False  # 人工审核后改为 True · Set True after review

    # 保存草稿 · Save draft
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(kp_list, f, ensure_ascii=False, indent=2)

    print(f"✅ 生成 {len(kp_list)} 个知识点草稿 · Generated {len(kp_list)} KP drafts")
    print(f"✅ 已保存 · Saved: {args.output}")
    print()
    print("⚠️  【重要 · IMPORTANT】这只是草稿！LLM 会犯错，必须人工审核后才能使用。")
    print("⚠️  This is just a draft! LLM makes errors. Manual review is required before use.")


if __name__ == "__main__":
    main()
```

**运行 · Run (one chapter at a time):**
```bash
# 第 1 章 · Chapter 1
python src/kg/extract_kp.py \
    --chapter 1 \
    --input  data/kg/linear-algebra/chapter1_text.txt \
    --output data/kg/linear-algebra/chapter1_kp_draft.json

# 第 2 章 · Chapter 2
python src/kg/extract_kp.py \
    --chapter 2 \
    --input  data/kg/linear-algebra/chapter2_text.txt \
    --output data/kg/linear-algebra/chapter2_kp_draft.json

# 第 3 章 · Chapter 3
python src/kg/extract_kp.py \
    --chapter 3 \
    --input  data/kg/linear-algebra/chapter3_text.txt \
    --output data/kg/linear-algebra/chapter3_kp_draft.json
```

---

### 3.4 人工审核 + 关系标注 · Manual Review & Relation Annotation

**中文：** 这是整个项目最关键的环节，PI 必须亲自参与。研究生的职责是准备材料和录入结果，不是决定内容。
**English:** This is the most critical step in the whole project; PI must be personally involved. Graduate students prepare materials and enter results—they don't decide content.

**研究生做什么 · What graduate students do:**

1. 把三章 JSON 草稿整理成打印版或 Excel，方便开会讨论。
   Organize the three-chapter JSON drafts into a printable or Excel format for discussion.

2. 预约 PI + 涂老师，开 1-2 次审核会（每次约 1.5 小时）。
   Schedule 1-2 review sessions with PI + Prof. Tu (~1.5 hours each).

3. 会上记录修改意见（哪些知识点要增/删/改）。
   During the meeting, record all changes (which KPs to add/remove/edit).

4. 用便利贴/卡片摆知识点，画箭头标注前置关系，拍照留档。
   Use sticky notes/cards to lay out KPs, draw arrows for prerequisites, and photograph.

5. 会后把最终确定的内容录入 CSV。
   After the meeting, enter the finalized content into CSV files.

**研究生不做什么 · What graduate students should NOT do:**

**中文：** 不要自己决定哪些知识点该有、前置关系怎么连。你们没教过线性代数，这些判断必须由 PI 和涂老师来做。你们的职责是"准备材料"和"录入结果"。
**English:** Don't decide which KPs should exist or how prerequisites connect. You haven't taught linear algebra—those judgments belong to the PI and Prof. Tu. Your role is to "prepare materials" and "enter results."

---

### 3.5 整理成 CSV · Organize into CSV

**中文：** 审核完成后，整理成三个 CSV 文件。这三个文件**可以进入 git**（不含学生信息）。
**English:** After review, organize results into three CSV files. These **can go into git** (no student data).

**文件 1 · File 1: `data/kg/linear-algebra/knowledge_points.csv`**

**中文：** 每行是一个知识点。
**English:** Each row is one knowledge point.

```csv
id,name,name_en,chapter,difficulty,description
LA-CH1-KP01,行列式的定义,Definition of Determinant,1,2,n阶行列式的定义与符号表示
LA-CH1-KP02,行列式的性质,Properties of Determinant,1,3,行列式的基本运算性质（如转置不变性）
LA-CH2-KP01,矩阵的定义,Definition of Matrix,2,1,矩阵的概念、表示方法与特殊矩阵类型
LA-CH2-KP05,矩阵乘法,Matrix Multiplication,2,3,矩阵相乘的定义与规则（注意不满足交换律）
LA-CH2-KP08,逆矩阵,Inverse Matrix,2,4,可逆矩阵的定义与逆矩阵的求法
```

**文件 2 · File 2: `data/kg/linear-algebra/relations.csv`**

**中文：** 每行是一条知识点间的关系。`relation_type` 只能填四种之一（见 3.1 节的表格）。
**English:** Each row is one relation between KPs. `relation_type` must be one of the four types (see the table in 3.1).

```csv
from_id,to_id,relation_type,notes
LA-CH2-KP05,LA-CH2-KP08,PREREQUISITE_OF,学逆矩阵前必须掌握矩阵乘法·Must know multiplication before inverse
LA-CH1-KP01,LA-CH1-KP02,PREREQUISITE_OF,理解性质前需先知道定义·Must know definition before properties
LA-CH1-KP01,LA-CH2-KP01,EASILY_CONFUSED_WITH,学生常把行列式和矩阵混淆·Students often confuse determinant and matrix
```

**文件 3 · File 3: `data/kg/linear-algebra/misconceptions.csv`**

**中文：** 每行是一个常见误区，关联到某个知识点。
**English:** Each row is one misconception linked to a knowledge point.

```csv
id,kp_id,description
MC-001,LA-CH2-KP05,误以为矩阵乘法满足交换律：AB=BA 不一定成立·Believing matrix multiplication is commutative: AB=BA doesn't always hold
MC-002,LA-CH2-KP08,误以为所有方阵都有逆矩阵：行列式为零的方阵没有逆·Assuming all square matrices are invertible: singular matrices have no inverse
MC-003,LA-CH1-KP01,把行列式当成矩阵处理，混淆两者的本质·Treating a determinant as a matrix, confusing the two concepts
```

**整理完成后 commit · Commit when done:**
**中文：** 在 GitHub Desktop 里，你会看到三个新 CSV 出现在 Changes 列表。在 Summary 填：
**English:** In GitHub Desktop, you'll see the three new CSVs in the Changes list. In Summary write:

```
data(kg): add reviewed linear algebra knowledge graph for chapters 1-3
```

然后 Commit to main → Push origin。
Then Commit to main → Push origin.

---

### 3.6 导入 Neo4j · Import into Neo4j

**任务 · Task:**
**中文：** 把三个 CSV 导入 Neo4j 数据库，让知识图谱"活起来"可以可视化查询。
**English:** Import the three CSV files into Neo4j so the knowledge graph becomes queryable and visualizable.

**中文：** 先确认 Neo4j 在运行（浏览器能打开 `http://localhost:7474`）。新建文件 `src/kg/import_to_neo4j.py`：
**English:** First confirm Neo4j is running (browser opens `http://localhost:7474`). Create `src/kg/import_to_neo4j.py`:

```python
"""
把知识图谱 CSV 文件导入 Neo4j
Import knowledge graph CSV files into Neo4j.

说明 · Description:
  每次运行会先清空数据库再重新导入，确保数据是最新版本。
  Each run clears the database first, then reimports—ensuring data is current.

用法 · Usage:
  python src/kg/import_to_neo4j.py

前提条件 · Prerequisites:
  - Neo4j 必须在运行（infra/ 目录下已执行 docker compose up -d）
    Neo4j must be running (docker compose up -d in infra/ already executed)
  - 三个 CSV 文件必须存在于 data/kg/linear-algebra/
    Three CSV files must exist in data/kg/linear-algebra/
"""

import csv
from pathlib import Path
from neo4j import GraphDatabase

# 连接配置 · Connection config
# 如果修改过 Neo4j 密码，把 devpassword 改成你的新密码
# If you changed the Neo4j password, replace devpassword with your new one
NEO4J_URI      = "bolt://localhost:7687"
NEO4J_USER     = "neo4j"
NEO4J_PASSWORD = "devpassword"

DATA_DIR = Path("data/kg/linear-algebra")

# 安全白名单：只允许这四种关系类型 · Security whitelist: only these four relation types
ALLOWED_RELATIONS = {"PREREQUISITE_OF", "RELATED_TO", "EASILY_CONFUSED_WITH", "HAS_MISCONCEPTION"}


def clear_database(session):
    """清空数据库 · Clear all nodes and relations."""
    session.run("MATCH (n) DETACH DELETE n")
    print("已清空数据库 · Database cleared")


def import_knowledge_points(session) -> int:
    """导入知识点节点 · Import KnowledgePoint nodes."""
    path = DATA_DIR / "knowledge_points.csv"
    if not path.exists():
        print(f"❌ 文件不存在 · File not found: {path}")
        return 0
    count = 0
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            session.run("""
                CREATE (k:KnowledgePoint {
                    id:          $id,
                    name:        $name,
                    name_en:     $name_en,
                    chapter:     toInteger($chapter),
                    difficulty:  toInteger($difficulty),
                    description: $description
                })
            """, **row)
            count += 1
    print(f"✅ 导入 {count} 个知识点 · Imported {count} knowledge points")
    return count


def import_misconceptions(session) -> int:
    """导入误区节点并关联到知识点 · Import Misconception nodes and link to KPs."""
    path = DATA_DIR / "misconceptions.csv"
    if not path.exists():
        print(f"⚠️  文件不存在，跳过 · File not found, skipping: {path}")
        return 0
    count = 0
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            result = session.run("""
                MATCH (k:KnowledgePoint {id: $kp_id})
                CREATE (m:Misconception {id: $id, description: $description})
                CREATE (k)-[:HAS_MISCONCEPTION]->(m)
                RETURN k
            """, **row)
            if result.single():
                count += 1
            else:
                print(f"  ⚠️  知识点不存在，跳过 · KP not found: {row['kp_id']}")
    print(f"✅ 导入 {count} 个误区 · Imported {count} misconceptions")
    return count


def import_relations(session) -> int:
    """导入知识点间的关系 · Import relations between knowledge points."""
    path = DATA_DIR / "relations.csv"
    if not path.exists():
        print(f"❌ 文件不存在 · File not found: {path}")
        return 0
    count = 0
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rel = row["relation_type"].strip()
            if rel not in ALLOWED_RELATIONS:
                print(f"  ⚠️  未知关系类型，跳过 · Unknown relation type: {rel}")
                continue
            # 关系类型不能用参数传入 Cypher，故拼入字符串（已有白名单保护安全）
            # Relation type can't be a Cypher parameter; format into string (whitelist ensures safety)
            result = session.run(f"""
                MATCH (a:KnowledgePoint {{id: $from_id}})
                MATCH (b:KnowledgePoint {{id: $to_id}})
                CREATE (a)-[:{rel}]->(b)
                RETURN a
            """, from_id=row["from_id"], to_id=row["to_id"])
            if result.single():
                count += 1
            else:
                print(f"  ⚠️  找不到节点，跳过 · Node not found: {row['from_id']} → {row['to_id']}")
    print(f"✅ 导入 {count} 条关系 · Imported {count} relations")
    return count


def main():
    print("=" * 55)
    print("开始导入知识图谱 · Starting knowledge graph import")
    print("=" * 55)

    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
        print("✅ 已连接 Neo4j · Connected to Neo4j")
    except Exception as e:
        print(f"❌ 无法连接 Neo4j · Cannot connect: {e}")
        print("   请检查 · Please check:")
        print("   1. Docker Desktop 是否在运行 · Is Docker Desktop running?")
        print("   2. 是否执行了 docker compose up -d · Did you run docker compose up -d?")
        print("   3. 密码是否正确 · Is the password correct?")
        return

    with driver.session() as session:
        clear_database(session)
        kp_count  = import_knowledge_points(session)
        mc_count  = import_misconceptions(session)
        rel_count = import_relations(session)
    driver.close()

    print()
    print("=" * 55)
    print("导入完成 · Import complete")
    print(f"  知识点 · KPs:           {kp_count}")
    print(f"  误区   · Misconceptions: {mc_count}")
    print(f"  关系   · Relations:      {rel_count}")
    print()
    print("👉 打开浏览器 · Open: http://localhost:7474")
    print("   登录后运行 · After login run: MATCH (n) RETURN n")
    print("=" * 55)


if __name__ == "__main__":
    main()
```

**运行 · Run:**
```bash
python src/kg/import_to_neo4j.py
```

**查看结果 · View results:**
**中文：** 打开 `http://localhost:7474`，登录后在顶部查询框输入并运行：
**English:** Open `http://localhost:7474`, log in, type in the query box and click Run:

```cypher
MATCH (n) RETURN n
```

**中文：** 你会看到知识图谱的可视化！节点是彩色圆圈，连线是关系。

**English:** You'll see the knowledge graph visualized! Nodes are colored circles; lines are relations.

**几个好用的查询 · Useful queries to explore:**

```cypher
-- 查某知识点的所有前置知识 · Find all prerequisites of a KP
MATCH path = (k:KnowledgePoint {name: "逆矩阵"})<-[:PREREQUISITE_OF*]-(prereq)
RETURN path

-- 查某章节所有知识点 · Find all KPs in one chapter
MATCH (k:KnowledgePoint {chapter: 2})
RETURN k.id, k.name, k.difficulty ORDER BY k.id

-- 查所有易混淆的知识点对 · Find all easily confused KP pairs
MATCH (a)-[:EASILY_CONFUSED_WITH]->(b)
RETURN a.name AS 知识点A, b.name AS 知识点B
```

---

### 3.7 写 Python 查询客户端 · Write Python Query Client

**任务 · Task:**
**中文：** 封装常用的 Neo4j 查询，让阶段 4 的诊断代码可以直接调用，不用每次写 Cypher。
**English:** Wrap common Neo4j queries so Stage 4's diagnosis code can call them directly without writing Cypher each time.

**新建 `src/kg/kg_client.py`:**

```python
"""
知识图谱查询客户端 · Knowledge Graph Query Client

说明 · Description:
  封装项目中最常用的 Neo4j 查询。
  阶段 4 诊断引擎通过这个类访问知识图谱。
  Wraps the most common Neo4j queries.
  Stage 4's diagnosis engine accesses the KG through this class.

用法示例 · Usage example:
  from src.kg.kg_client import KGClient

  kg = KGClient()
  prereqs = kg.get_prerequisites("LA-CH2-KP08")
  for p in prereqs:
      print(p["name"], "距离 · distance:", p["distance"])
  kg.close()
"""

from neo4j import GraphDatabase


class KGClient:
    """知识图谱查询客户端 · Knowledge graph query client."""

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "devpassword",
    ):
        """初始化并连接 Neo4j · Initialize and connect to Neo4j."""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """关闭连接，使用完后调用 · Close connection when done."""
        self.driver.close()

    def get_prerequisites(self, kp_id: str, max_depth: int = 3) -> list[dict]:
        """
        递归查找一个知识点的所有前置知识点。
        Recursively find all prerequisite knowledge points of a given KP.

        参数 · Args:
            kp_id:     知识点 ID，如 "LA-CH2-KP08" · KP ID, e.g. "LA-CH2-KP08"
            max_depth: 最多追溯几层，默认 3 · Max depth to trace back, default 3

        返回 · Returns:
            list of dict: id, name, name_en, distance
            distance=1 表示直接前置，distance=2 表示前置的前置
            distance=1 means direct prerequisite, distance=2 means prerequisite of prerequisite
        """
        query = f"""
            MATCH path = (start:KnowledgePoint {{id: $kp_id}})
                         <-[:PREREQUISITE_OF*1..{max_depth}]-(prereq)
            RETURN DISTINCT
                prereq.id      AS id,
                prereq.name    AS name,
                prereq.name_en AS name_en,
                length(path)   AS distance
            ORDER BY distance
        """
        with self.driver.session() as session:
            return [dict(r) for r in session.run(query, kp_id=kp_id)]

    def get_misconceptions(self, kp_id: str) -> list[str]:
        """
        获取一个知识点的所有常见误区描述。
        Get all misconception descriptions for a knowledge point.
        """
        query = """
            MATCH (k:KnowledgePoint {id: $kp_id})-[:HAS_MISCONCEPTION]->(m:Misconception)
            RETURN m.description AS description
        """
        with self.driver.session() as session:
            return [r["description"] for r in session.run(query, kp_id=kp_id)]

    def get_all_knowledge_points(self, chapter: int = None) -> list[dict]:
        """
        列出所有知识点，可按章节筛选。
        List all knowledge points, optionally filtered by chapter.
        """
        if chapter is not None:
            query = """
                MATCH (k:KnowledgePoint {chapter: $chapter})
                RETURN k.id AS id, k.name AS name, k.name_en AS name_en,
                       k.chapter AS chapter, k.difficulty AS difficulty
                ORDER BY k.id
            """
            params = {"chapter": chapter}
        else:
            query = """
                MATCH (k:KnowledgePoint)
                RETURN k.id AS id, k.name AS name, k.name_en AS name_en,
                       k.chapter AS chapter, k.difficulty AS difficulty
                ORDER BY k.chapter, k.id
            """
            params = {}
        with self.driver.session() as session:
            return [dict(r) for r in session.run(query, **params)]

    def get_easily_confused_pairs(self) -> list[dict]:
        """
        获取所有易混淆的知识点对。
        Get all easily confused knowledge point pairs.
        """
        query = """
            MATCH (a:KnowledgePoint)-[:EASILY_CONFUSED_WITH]->(b:KnowledgePoint)
            RETURN a.name AS name_a, b.name AS name_b, a.id AS id_a, b.id AS id_b
        """
        with self.driver.session() as session:
            return [dict(r) for r in session.run(query)]


# 直接运行此文件可以测试连接 · Run directly to test the connection
if __name__ == "__main__":
    print("测试 KGClient · Testing KGClient")
    print("-" * 40)
    kg = KGClient()
    all_kps = kg.get_all_knowledge_points()
    print(f"共 {len(all_kps)} 个知识点 · Total {len(all_kps)} KPs:")
    for kp in all_kps:
        print(f"  [{kp['chapter']}] {kp['id']}: {kp['name']} / {kp['name_en']} "
              f"难度 · difficulty: {kp['difficulty']}")
    confused = kg.get_easily_confused_pairs()
    if confused:
        print(f"\n共 {len(confused)} 对易混淆 · {len(confused)} confused pairs:")
        for p in confused:
            print(f"  {p['name_a']} ↔ {p['name_b']}")
    kg.close()
    print("\n✅ 测试完成 · Test complete")
```

**运行测试 · Run test:**
```bash
python src/kg/kg_client.py
```

**中文：** 看到知识点列表，说明整条链路通了：CSV → Neo4j → Python 客户端。
**English:** Seeing the KP list means the whole pipeline works: CSV → Neo4j → Python client.

---

### 3.8 阶段 2 完成标准 · Stage 2 Done Checklist

| 检查项 · Check Item | 完成 · Done |
|---|---|
| `docs/03-kg-schema.md` 已写完 · Schema doc written | [ ] |
| LLM 草稿已生成（三章）· LLM drafts generated (3 chapters) | [ ] |
| 人工审核已完成（PI 参与）· Manual review done (PI involved) | [ ] |
| 三个 CSV 已整理并 commit · Three CSVs organized and committed | [ ] |
| Neo4j 导入成功，浏览器可查看 · Import successful, viewable in browser | [ ] |
| Python 客户端测试通过 · Python client test passes | [ ] |
| 已向 PI 做 demo · Demo presented to PI | [ ] |

**中文：** 全部完成后，向 PI 做一个 15 分钟的 demo：打开 Neo4j 浏览器，展示知识图谱，演示几个查询。这是阶段 2 的正式里程碑。
**English:** Once all done, give the PI a 15-minute demo: open the Neo4j browser, show the graph, run a few queries. This is the formal Stage 2 milestone.


---

<a name="part-4"></a>
## Part 4 · 每天/每周怎么工作 · Daily & Weekly Rhythm

### 每天开始工作的固定动作 · Fixed Daily Startup Actions

**中文：** 每次开始工作，先做这 4 件事，养成习惯。
**English:** Every time you start working, do these 4 things first—make it a habit.

| 步骤 · Step | 操作 · Action | 原因 · Why |
|---|---|---|
| 1 | GitHub Desktop → Fetch origin | 拉取最新，避免冲突 · Pull latest, avoid conflicts |
| 2 | VS Code 终端激活虚拟环境 · Activate venv in VS Code terminal | 确保依赖可用 · Ensure dependencies work |
| 3 | 如需 Neo4j，确认 Docker Desktop 在运行 · If using Neo4j, confirm Docker running | Neo4j 需要 Docker · Neo4j requires Docker |
| 4 | 看一眼 GitHub Issues 确认今天的任务 · Check GitHub Issues for today's tasks | 保持方向清晰 · Stay focused |

### 每天结束工作的固定动作 · Fixed Daily Shutdown Actions

**中文：** 每次结束工作，哪怕只改了一点点，都要做：
**English:** Every time you finish working, even if you only changed a little:

1. GitHub Desktop 里 commit（Summary 写清楚改了什么）
   Commit in GitHub Desktop (write clearly what changed in Summary)
2. Push origin（推送到 GitHub 云端）
   Push origin (sync to GitHub)

**中文：** 这样即使电脑坏了，代码也在云端安全。
**English:** This way, even if your laptop dies, your code is safe in the cloud.

---

### 每周节奏 · Weekly Rhythm

| 时间 · When | 内容 · Content | 时长 · Duration |
|---|---|---|
| 周一上午 · Monday AM | 周会：上周进展 + 本周计划 · Weekly meeting: last week + this week | 30-45 分钟 · min |
| 周三下午 · Wednesday PM | Standup：有没有阻塞 · Standup: any blockers | 15 分钟（可选 · optional）|
| 周五下午 · Friday PM | 写周报，commit + push · Write weekly report, commit + push | 30 分钟 · min |

---

### 周报模板 · Weekly Report Template

**中文：** 每周五在 `docs/meetings/` 下新建文件，命名为当天日期，例如 `2025-12-05-weekly.md`。
**English:** Every Friday, create a new file in `docs/meetings/` named with today's date, e.g. `2025-12-05-weekly.md`.

```markdown
# 周报 · Weekly Report

日期 · Date: YYYY-MM-DD
撰写人 · Author: 学生 A / Student A

---

## 本周完成 · Completed This Week

- （具体写做了什么，不要写"努力工作了" · Be specific; don't write "worked hard"）
- （例：完成了第 1 章知识点草稿生成，共 18 个 · e.g. Generated Ch.1 KP draft: 18 KPs）

## 遇到的问题与解决方式 · Problems & Solutions

- （问题 + 解决方法；没有写"无" · Problem + solution; "None" if none）

## 下周计划 · Next Week Plan

- （越具体越好，最好按天 · As specific as possible, ideally day-by-day）

## 需要 PI 决策或协助的事 · Items Needing PI Decision or Help

- （没有写"无" · "None" if nothing）
```

---

### Commit Message 规范 · Commit Message Convention

**中文：** 格式是 `<类型>: <描述>`，中英文都可以，但要让三个月后的自己能看懂。
**English:** Format is `<type>: <description>`. Chinese or English is fine, but make it understandable to yourself three months later.

| 类型 · Type | 用途 · When to Use | 例子 · Example |
|---|---|---|
| `docs` | 改文档 · Edit documentation | `docs: add kg schema examples for chapter 2` |
| `data` | 改数据文件 · Edit data files | `data(kg): add reviewed ch1 knowledge points csv` |
| `feat` | 加新功能 · Add new feature | `feat(kg): implement prerequisite query in KGClient` |
| `fix` | 修 bug · Fix a bug | `fix: correct chapter number in extract_kp script` |
| `exp` | 实验性改动 · Experimental | `exp: try different prompt for misconception extraction` |
| `chore` | 杂项 · Miscellaneous | `chore: clean up unused imports in import script` |

---

<a name="part-5"></a>
## Part 5 · 常见问题 · Troubleshooting

> **中文：** 遇到问题先看这里，很多问题有固定解法。看完还不行，再找同伴或 PI。
>
> **English:** Check here first when problems arise—most have known solutions. If still stuck, ask a peer or the PI.

---

### 环境类 · Environment Issues

**Q1: 命令行提示 `python` 是未知命令 · `python` is not recognized**

**中文解法：**
- Windows：重装 Python 时**勾选 Add to PATH**；或把 `python` 换成 `py`
- Mac：把 `python` 换成 `python3.11`

**English solution:**
- Windows: reinstall Python, **check Add to PATH**; or replace `python` with `py`
- Mac: replace `python` with `python3.11`

---

**Q2: `pip install` 很慢或失败 · `pip install` is slow or fails**

**中文解法：** 换国内镜像：
**English solution:** Use a Chinese mirror:
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

**Q3: Windows 激活虚拟环境报"无法加载脚本" · Windows: "cannot be loaded" when activating venv**

**中文解法：** 以管理员身份打开 PowerShell，运行：
**English solution:** Open PowerShell as administrator and run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
然后重试激活命令。 · Then retry the activate command.

---

**Q4: Neo4j 浏览器打不开 (localhost:7474 无响应) · Neo4j browser won't open**

**中文解法（按顺序检查）：**
**English solution (check in order):**

1. Docker Desktop 是否在运行？看任务栏图标。
   Is Docker Desktop running? Check the taskbar icon.

2. 运行 `docker ps` 确认容器在跑：
   Run `docker ps` to confirm the container is running:
   ```bash
   docker ps
   ```
   找 `ai-teaching-neo4j` 或类似名称。
   Look for `ai-teaching-neo4j` or a similar name.

3. 如果没有，重新启动：
   If not listed, restart:
   ```bash
   cd infra
   docker compose up -d
   ```
   等 30 秒再试。 · Wait 30 seconds and try again.

4. 还不行，看日志找原因：
   If still not working, check logs:
   ```bash
   docker logs ai-teaching-neo4j
   ```

---

**Q5: Neo4j 登录报 authentication failure · Neo4j login says authentication failure**

**中文解法：**
- 如果你改过密码，把代码里所有 `devpassword` 换成你的新密码
- 如果忘了密码，删除 Docker 卷重置（**会清空数据库**，重新导入即可）：
  ```bash
  cd infra
  docker compose down -v
  docker compose up -d
  ```

**English solution:**
- If you changed the password, replace all `devpassword` in code files with your new one
- If you forgot the password, delete Docker volumes to reset (**clears the database**, just reimport):
  ```bash
  cd infra
  docker compose down -v
  docker compose up -d
  ```

---

### 代码类 · Code Issues

**Q6: `ModuleNotFoundError: No module named 'xxx'`**

**中文解法：**
1. 检查虚拟环境是否激活（命令行前有 `(.venv)` 吗？）
   Check if venv is activated (do you see `(.venv)` at the prompt?)
2. 没激活 → 运行 activate 命令
   Not activated → run the activate command
3. 激活后 → 重新运行 `pip install -r requirements.txt`
   After activating → run `pip install -r requirements.txt` again

**English solution:** Same as above—venv is almost always the issue.

---

**Q7: API Key 读不到，报 `None` 或 401 错误 · API Key returns `None` or 401 error**

**中文解法（逐项检查）：**
**English solution (check each item):**

1. `.env` 在项目**根目录**（和 `README.md` 同级），不在子文件夹里。
   `.env` is in the project **root** (same level as `README.md`), not in a subfolder.

2. `.env` 内容格式正确，等号两边没有空格：
   `.env` format is correct—no spaces around `=`:
   ```
   DEEPSEEK_API_KEY=sk-xxxx   ← 正确 · Correct
   DEEPSEEK_API_KEY = sk-xxxx ← 错误 · Wrong
   ```

3. 代码里有 `load_dotenv()` 且在 `os.getenv()` 之前调用。
   Code has `load_dotenv()` and it's called before `os.getenv()`.

---

**Q8: LLM 返回内容 JSON 解析失败 · LLM output fails JSON parsing**

**中文解法：**
脚本会把原始输出存到 `<输出文件>.raw.txt`。打开看 LLM 实际输出了什么。

常见原因 · Common causes:
- LLM 加了前言"当然，以下是..." → 删掉那些文字
  LLM added preamble "Sure, here is..." → delete that text
- JSON 里有中文引号 `"` → 替换成英文引号 `"`
  JSON contains Chinese quotes `"` → replace with standard `"`
- 输出被截断了 → 减少输入内容，或分章节分次请求
  Output was truncated → reduce input or split into separate requests

**English solution:** Same as above.

---

**Q9: Neo4j 导入时提示找不到节点 · "Node not found" during import**

**中文解法：** `relations.csv` 里的 `from_id` 或 `to_id` 在 `knowledge_points.csv` 里不存在。检查 ID 拼写是否完全一致（大小写敏感）。
**English solution:** The `from_id` or `to_id` in `relations.csv` doesn't exist in `knowledge_points.csv`. Check that IDs match exactly (case-sensitive).

---

### Git 类 · Git Issues

**Q10: Push 失败，提示 rejected 或 behind · Push fails with "rejected" or "behind"**

**中文解法：** 别人先 push 了新内容。在 GitHub Desktop 点 Fetch origin 拉最新，再重新 push。
**English solution:** Someone else pushed first. Click Fetch origin in GitHub Desktop to pull the latest, then push again.

---

**Q11: 不小心把数据文件加进了 Changes 列表 · Accidentally added a data file to Changes**

**中文解法：**
- 还没 commit：在 GitHub Desktop 的 Changes 列表里**取消勾选**那个文件，再 commit 其他的。
  Not yet committed: **uncheck** that file in GitHub Desktop's Changes list, then commit the rest.
- 已 commit 未 push：History 里找到那个 commit，右键 → Undo。
  Committed but not pushed: find the commit in History, right-click → Undo.
- 已 push：立刻告诉 PI，不要自己乱操作。
  Already pushed: tell PI immediately; don't try to fix it yourself.

**English solution:** Same as above.

---

### 求助渠道 · Where to Get Help

| 问题类型 · Issue Type | 第一步 · First | 第二步 · Second | 第三步 · Third |
|---|---|---|---|
| 装环境、报错 · Setup/errors | Google 搜错误文字 · Google the error | 问同伴 · Ask peer | 找 PI · PI |
| 代码逻辑 · Code logic | 问 AI (DeepSeek/ChatGPT) | 问同伴 · Ask peer | 找 PI · PI |
| 知识点内容对不对 · KP correctness | 写 GitHub Issue | 找 PI · PI | PI 转问涂老师 · Prof. Tu |
| 关系怎么标注 · Relation annotation | 写 GitHub Issue | 找 PI · PI | 开审核会 · Schedule review |
| 数据权限 · Data access | 找 PI · PI | — | — |
| git 操作出错 · Git mistake | 截图告诉 PI · Screenshot to PI | — | — |

---

**最后记住 · Final Reminder:**

**中文：** 卡 2 小时就求助，不要硬扛一整天。问问题不是软弱，是效率。

**English:** Ask for help after 2 hours stuck. Asking questions isn't weakness—it's efficiency.
