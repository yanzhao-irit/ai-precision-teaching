# Git 协作规范 · Git Workflow

> 给项目成员的 git 使用指南。
> Git usage guide for project members.

---

## 一、工具选择 · Tools

### 推荐 · Recommended

- **GitHub Desktop** (图形界面，新手友好 · GUI, beginner-friendly)
  下载 · Download: https://desktop.github.com

### 进阶 · Advanced

- 命令行 git · Command-line git
- VS Code 内置 git · Built-in git in VS Code

---

## 二、基本流程 · Basic Workflow

### 改文档（小改动）· Editing Docs (Small Changes)

可以直接在 `main` 分支操作 · Can work directly on `main`:

1. Fetch origin (拉最新)
2. 在本地编辑文件 · Edit files locally
3. Commit · 写清楚的 commit message
4. Push origin (推送)

### 改代码（大改动）· Editing Code (Major Changes)

必须开分支 + PR · Must use branch + PR:

1. 创建新分支 · Create new branch
   - 命名格式 · Naming: `feature/<阶段>-<简短描述>`
   - 例如 · Example: `feature/stage2-kg-import-script`
2. 在分支上工作 · Work on the branch
3. Push 分支到 GitHub
4. 发起 Pull Request · Open a Pull Request
5. 等 PI 或同伴 review · Wait for PI or peer review
6. Review 通过后 merge · Merge after approval

---

## 三、Commit Message 规范 · Commit Message Convention

格式 · Format: `<type>: <description>`

| Type | 用途 · Use |
|---|---|
| `docs` | 文档改动 · Documentation changes |
| `feat` | 新功能 · New feature |
| `fix` | 修 bug · Bug fix |
| `data` | 数据更新 · Data updates |
| `exp` | 实验性改动 · Experimental changes |
| `chore` | 杂项 · Misc |

**好的例子 · Good examples:**

```
docs: add stage 1 data inventory checklist
feat(kg): implement prerequisite graph traversal
fix(diagnosis): correct BKT update formula
data: add LA chapter 1 knowledge points draft
```

**不好的例子 · Bad examples:**

```
update                          ← 不知道改了什么 · Vague
fix bug                         ← 哪个 bug? · Which bug?
asdfgh                          ← 真有人这么写过 · Yes really
```

---

## 四、禁止事项 · Don'ts

| 禁止 · Don't | 原因 · Why |
|---|---|
| 把原始学生数据 commit 进 git | 隐私 + 文件大小 · Privacy + file size |
| 把大文件 (>10MB) commit 进 git | 仓库膨胀 · Repo bloat |
| 把 API key、密码 commit 进 git | 安全 · Security |
| 把 `.env` 文件 commit 进 git | 含敏感配置 · Contains secrets |
| force push 到 main 分支 | 会丢历史 · Loses history |
| 删除别人没 merge 的分支 | 别人可能还在用 · Others may still need it |

---

## 五、典型场景 · Common Scenarios

### 场景 1 · 我改错了，想撤销 · I Made a Mistake, How to Undo?

**还没 commit · Not committed yet:**
- GitHub Desktop: 右键文件 → Discard changes

**已 commit 但没 push · Committed but not pushed:**
- GitHub Desktop: History → 右键 commit → Revert / Undo

**已 push · Already pushed:**
- 找 PI 或同伴帮忙 · Ask PI or a peer for help
- 不要乱试 · Don't experiment

### 场景 2 · 和别人改了同一个文件 · Conflict with Someone Else

GitHub Desktop 会提示冲突 · GitHub Desktop will show conflicts:
1. 打开冲突文件 · Open the conflicting file
2. 选择保留哪一版 · Choose which version to keep
3. 标记为已解决 · Mark as resolved
4. Commit

**预防：** 经常 fetch origin，先沟通谁改哪个文件
**Prevention:** Fetch origin often, agree on file ownership

### 场景 3 · 我想试一个想法但不确定 · Want to Try Something

开一个实验分支 · Create an experiment branch:

```
experiment/<你的名字>-<想法>
experiment/zhang-try-llm-prompts
```

成功了再合并到 main，失败了直接删 · Merge on success, delete on failure

---

## 六、第一次配置 · Initial Setup

### 1. 安装 GitHub Desktop

下载安装 https://desktop.github.com

### 2. 登录

用学校邮箱注册的 GitHub 账号登录 · Sign in with your GitHub account.

### 3. Clone 项目

File → Clone Repository → 选 `ai-precision-teaching` → Choose local folder

### 4. 配置身份 · Configure Identity

GitHub Desktop → Preferences → Git → 填真实姓名和学校邮箱
Fill in your real name and university email.

### 5. 测试一下 · Test It

1. 在 `docs/meetings/` 新建一个文件 `YYYY-MM-DD-<你的名字>-test.md`
2. 写一行字 · Write a line
3. Commit + Push
4. 在 GitHub 网页确认能看到 · Verify on GitHub web

成功了说明配置完成 · Setup complete if you see your file on GitHub.

---

## 七、学习资源 · Learning Resources

- [GitHub Docs](https://docs.github.com) · 官方文档
- [Atlassian Git Tutorial](https://www.atlassian.com/git/tutorials) · 概念清晰
- [Pro Git Book (中文)](https://git-scm.com/book/zh/v2) · 深度学习

---

## 八、有问题问谁 · Whom to Ask

| 问题类型 · Question Type | 找谁 · Whom |
|---|---|
| Git 操作问题 · Git operation | 先 Google，再问同伴 · Google first, then peer |
| 项目流程问题 · Project workflow | PI |
| 仓库权限问题 · Repo permissions | PI |
