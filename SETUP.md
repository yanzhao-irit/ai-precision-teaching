# 从零搭建与运行指南 · Setup Guide

> 面向**没用过 WSL / Docker / Python 虚拟环境**的同学。照着一步步做即可。
> 系统要求：Windows 10/11，有管理员权限，能联网。

---

## 0. 这个项目是什么 / 跑起来需要哪几样东西

一个「AI 精准教学」教师端网站，分三部分，**都跑在 WSL（Windows 里的 Linux）里**：

| 部分 | 技术 | 端口 |
|---|---|---|
| 数据库 | PostgreSQL + Neo4j（用 Docker 启动） | 5432 / 7474 / 7687 |
| 后端 API | Python (FastAPI) | 8000 |
| 前端网页 | Node + React (Vite) | 5173 |

最终在浏览器打开 `http://localhost:5173` 使用。整个搭建顺序就是：
**装 WSL → 装 Docker → 起数据库 → 起后端 → 起前端 → 打开网页导入数据**。

第一次安装大概 30–60 分钟（主要在下载）。之后每天启动只要 3 条命令（见 [第 9 节](#9-日常启动以后每天只需这几步)）。

---

## 1. 安装 WSL2（Windows 的 Linux 子系统）

1. 点开始菜单，搜索 **PowerShell**，右键 **以管理员身份运行**。
2. 执行：
   ```powershell
   wsl --install
   ```
   这会自动装好 WSL2 和 Ubuntu。**装完重启电脑**。
3. 重启后会自动弹出 Ubuntu 窗口，让你设置 Linux 用户名和密码（**这个密码后面 `sudo` 要用，记住它**）。
   - 如果没自动弹出，开始菜单搜索 **Ubuntu** 打开即可。

> 以后所有命令，除非特别说明，都是在这个 **Ubuntu (WSL) 终端**里输入的。
> 启动时可能出现一行 `localhost 代理…NAT 模式` 的黄字警告，**无视它，不影响使用**。

---

## 2. 在 WSL 里安装 Docker（用来启动数据库）

在 Ubuntu 终端里依次执行：

```bash
# 更新软件源并安装 docker
sudo apt update
sudo apt install -y docker.io

# 【关键】修复 WSL2 的端口转发：不做这步，数据库端口在 Windows 里连不上
sudo update-alternatives --set iptables /usr/sbin/iptables-legacy
sudo update-alternatives --set ip6tables /usr/sbin/ip6tables-legacy

# 启动 docker 服务，并把自己加入 docker 用户组（免 sudo）
sudo service docker start
sudo usermod -aG docker $USER
newgrp docker
```

验证 Docker 能用：
```bash
docker run --rm hello-world
```
看到 `Hello from Docker!` 就成功了。

> 如果 `docker compose` 提示找不到子命令，再装一个：`sudo apt install -y docker-compose-v2`。

---

## 3. 安装 Node 和 Python 依赖工具

```bash
# Python 虚拟环境工具（后端要用）
sudo apt install -y python3-venv python3-pip

# 用 nvm 装 Node 22（前端要用；系统自带/Windows 的 node 版本太旧，必须用 nvm 装）
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
export NVM_DIR="$HOME/.nvm"; [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm install 22
node --version    # 应显示 v22.x
```

> 装完 nvm 后，**新开的终端**会自动加载它。当前终端如果 `node` 找不到，执行一次上面的 `export NVM_DIR=...` 那行即可。

---

## 4. 拿到项目代码

把项目文件夹放到电脑上（解压 zip 或 `git clone`）。本指南用 `$PROJECT` 代表项目根目录（里面能看到 `backend/`、`frontend/`、`docker-compose.yml`）。

- 如果项目在 Windows 的下载目录，在 WSL 里的路径是 `/mnt/c/Users/你的Windows用户名/Downloads/ai-precision-teaching-main`。
- 为方便，先设一个变量（**每个新终端都要重设一次**，或把它写进 `~/.bashrc`）：
  ```bash
  export PROJECT="/mnt/c/Users/你的Windows用户名/Downloads/ai-precision-teaching-main"
  cd "$PROJECT"
  ```

> 小贴士：放在 WSL 主目录（如 `~/ai-precision-teaching`）读写更快。放在 `/mnt/c` 也完全可用（项目已针对它做了热更新配置）。

---

## 5. 启动数据库（Docker）

```bash
cd "$PROJECT"
docker compose up -d
docker compose ps
```
- `postgres`、`neo4j` 状态应为 `Up ... (healthy)`；`neo4j-init` 跑完会退出（正常）。
- Postgres 首次启动会**自动建好所有数据表**（无需手动建表）。
- 账号密码（已与后端默认一致，无需改）：Postgres `postgres/password`，Neo4j `neo4j/password`，库名 `ai_precision_teaching`。

验证表已建好：
```bash
docker compose exec postgres psql -U postgres -d ai_precision_teaching -c "\dt"
```
能列出 `course / student / question / question_response …` 等表就 OK。

> 数据库数据会保存在 Docker 卷里，关机重启也还在。想**清空重来**：`docker compose down -v` 再 `docker compose up -d`。

---

## 6. 启动后端 API

**新开一个 Ubuntu 终端**（保持数据库那个不用管），执行：
```bash
cd "$PROJECT/backend"
python3 -m venv .venv          # 第一次才需要建虚拟环境
source .venv/bin/activate      # 激活（之后命令行前面会出现 (.venv)）
pip install -r requirements.txt
uvicorn app.main:app --reload
```
看到 `Application startup complete` 和 `✅ PostgreSQL connected` 就成功了。**这个终端要一直开着**。

验证：浏览器打开 `http://localhost:8000/docs` 能看到接口文档页。

> - 启动日志若出现 `⚠️ Neo4j not reachable` 不影响主功能（知识图谱是后续阶段的）。
> - 依赖装得慢或某个包报错，可只装最小依赖跑起来：
>   ```bash
>   pip install fastapi uvicorn sqlalchemy asyncpg "psycopg[binary]" neo4j \
>               pydantic python-dotenv pandas openpyxl xlrd python-multipart
>   ```
> - 若提示缺编译器：`sudo apt install -y build-essential python3-dev` 后重试。

---

## 7. 启动前端网页

**再新开一个 Ubuntu 终端**，执行：
```bash
cd "$PROJECT/frontend"
nvm use 22                     # 确保用 Node 22
npm install                    # 第一次才需要
npm run dev
```
看到 `Local: http://localhost:5173/` 即成功。**这个终端也要一直开着**。

浏览器打开 **http://localhost:5173** —— 网站就出来了。

---

## 8. 第一次使用：导入数据

数据**全部在网页上传**，不用敲命令：

1. 首页点右上角 **「+ 新建课程」**，填课程代码（如 `AI-BASE-2025`）和名称（如 `人工智能基础`），点「创建并进入」。
2. 进入课程后，点顶部 **「导入数据」**，把文件拖进对应区域（或点击选择）：
   - **课程数据**：班级一键导出 `.xlsx`
   - **作业题库**：题库 `.xls`
   - **学生作业**：装着 word 答题文件的 `.zip`
3. 上传成功后页面自动刷新，概览/学情/学生三个标签页就能看到统计了。

> 建议导入顺序：先「作业题库」→ 再「学生作业」→ 最后「课程数据」。

---

## 9. 日常启动（以后每天只需这几步）

装好之后，每次开发开三个 Ubuntu 终端：

```bash
# 终端 1 — 数据库（如果已在跑可跳过）
cd "$PROJECT" && docker compose up -d

# 终端 2 — 后端
cd "$PROJECT/backend" && source .venv/bin/activate && uvicorn app.main:app --reload

# 终端 3 — 前端
cd "$PROJECT/frontend" && nvm use 22 && npm run dev
```
然后浏览器开 `http://localhost:5173`。

停止：在后端/前端终端按 `Ctrl+C`；数据库用 `docker compose stop`（数据保留）。

---

## 10. 常见问题排查

| 现象 | 原因 / 解决 |
|---|---|
| `docker: command not found` | Docker 没装好，回到第 2 节 |
| `Cannot connect to the Docker daemon` | 服务没起：`sudo service docker start` |
| docker 命令要加 sudo / `permission denied` | 没加入 docker 组：`sudo usermod -aG docker $USER` 后**关掉终端重开** |
| `address already in use: 5432` | 本机已有别的 PostgreSQL 占用：`sudo service postgresql stop`，再 `docker compose up -d` |
| 后端报 `connection refused` 连不上 5432 | 没做第 2 节的 **iptables-legacy** 那步；做完 `sudo service docker restart` 再起 |
| `node: command not found` 或 `Vite requires Node 20.19+` | 用错了 node：执行 `nvm use 22`（系统/Windows 自带的 node 不能用） |
| 改了前端代码网页不更新 | 在前端终端 `Ctrl+C` 后重新 `npm run dev`，浏览器按 `Ctrl+Shift+R` 硬刷新（项目已配置轮询热更新，正常会自动刷新） |
| 课程/学生下拉为空、看板没数据 | 还没导入数据，见第 8 节 |
| pgAdmin/DBeaver 连库报「密码认证失败」 | Windows 自带的 PostgreSQL 占了 5432。GUI 工具请连 **端口 5433**（docker 库已额外暴露在 5433，专供 GUI；后端仍走 5432）。连接信息：localhost / 5433 / 库 ai_precision_teaching / postgres / password |
| WSL 启动那行 `localhost 代理 NAT` 黄字警告 | 无害，忽略 |

---

## 11.（可选）用 Claude Code 辅助开发

如果要用 Claude Code（AI 编程助手）继续开发：在 WSL 终端里
```bash
npm install -g @anthropic-ai/claude-code   # 需先 nvm use 22
claude                                      # 在项目目录下运行，按提示登录
```
不用 Claude Code 也完全可以正常开发，用 VS Code 等编辑器即可（VS Code 装个「WSL」扩展就能直接打开 WSL 里的项目）。

---

## 项目结构速览

```
backend/        后端 (FastAPI)
  app/api/        接口路由（dashboard.py=看板, upload.py=上传, students.py=课程/学生 …）
  app/services/   看板聚合分析（掌握度分层等）
  app/data_access/数据访问层（SQL 仓储 / 图库 / 引擎门面）
  app/engines/    诊断/画像/推荐/预警 算法引擎
  db/schema.sql   数据库建表脚本（Docker 首次启动自动执行）
  requirements.txt
frontend/       前端 (React + Vite)
  src/pages/      页面（CoursesPage 首页, CourseDetailPage 课程详情, 题目/知识点/学生 详情）
  src/pages/course/  课程详情的三个 Tab（概览/学情/学生）
  src/components/  通用组件（图表、上传面板等）
  src/services/api.ts  调后端的接口封装
data-pipeline/  ETL（解析三类文件入库；网页上传时后端会调用它）
docker-compose.yml  一键启动两个数据库
```

更详细的功能说明见 `frontend/README.md` 与 `data-pipeline/README.md`。
