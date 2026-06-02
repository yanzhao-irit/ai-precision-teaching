# PI 快速上手指南 · PI Quickstart

> 这份文档是给你(项目负责人)看的。看完按步骤做，30 分钟搞定 git 初始化。
> This is for you (the PI). Follow the steps; ~30 min to get the repo live.

---

## 第一次设置 · One-Time Setup

### 步骤 1 · 注册 GitHub 账号

1. 去 https://github.com 用学校邮箱注册
2. 推荐申请教育账号: https://education.github.com
3. 记住你的用户名 (例如 `zhaoyan-nbt`)

### 步骤 2 · 安装 GitHub Desktop

下载: https://desktop.github.com

安装后用 GitHub 账号登录。

### 步骤 3 · 在 GitHub 网页上创建仓库

1. 登录 GitHub，右上角 "+" → "New repository"
2. 填写:
   - **Repository name:** `ai-precision-teaching`
   - **Description:** `AI-Empowered Error Diagnosis and Targeted Quality Improvement`
   - **Visibility:** **Private** (私有，不要选 Public)
   - **不要勾选** "Add a README file" (我们已经准备好了)
   - **不要选** .gitignore template (我们已经准备好了)
3. 点击 "Create repository"
4. 创建后会看到一个页面，**先不要关**，下一步要用

### 步骤 4 · 把这个文件夹推到 GitHub

**方法 A · 用 GitHub Desktop(推荐你用这个)**

1. 解压你下载的 zip，得到 `ai-precision-teaching` 文件夹
2. 打开 GitHub Desktop
3. File → Add Local Repository → 选择刚才解压的文件夹
4. GitHub Desktop 会提示"这不是一个 git 仓库，是否初始化?" → 点 Yes / Create a repository
5. 在弹出的窗口里:
   - Name: `ai-precision-teaching` (保持一致)
   - Description: 随便填
   - 点 "Create repository"
6. 现在你在 GitHub Desktop 里看到了项目，但还没推到 GitHub
7. 点击右上角 "Publish repository"
8. 取消勾选 "Keep this code private" 旁边的 checkbox 之前确认 **保持勾选**(私有)
9. 点 "Publish repository"

完成! 刷新 GitHub 网页能看到所有文件了。

**方法 B · 用命令行(如果你会)**

```bash
cd ai-precision-teaching
git init
git add .
git commit -m "docs: initial project structure and documentation"
git branch -M main
git remote add origin https://github.com/<你的用户名>/ai-precision-teaching.git
git push -u origin main
```

### 步骤 5 · 邀请研究生

1. 在 GitHub 网页打开你的仓库
2. Settings → Collaborators → "Add people"
3. 输入研究生的 GitHub 用户名 → 选 **Write** 权限
4. 重复操作邀请第二个研究生

研究生会收到邀请邮件，他们接受后就能 clone 仓库了。

---

## 日常使用 · Day-to-Day Use

### 想改一份文档

1. 打开 GitHub Desktop，确认 Current Repository 是这个项目
2. 点 **Fetch origin** 拉一下最新
3. 在 Finder/资源管理器里打开本地文件夹，找到要改的文件
4. 用任何文本编辑器(VS Code、Typora、记事本都行)修改
5. 回到 GitHub Desktop，左边列出改动的文件
6. 在左下角写:
   - **Summary**: 例如 `docs: add Q1 evaluation criteria`
   - **Description**: 详细说明(可不填)
7. 点 **Commit to main**
8. 点上方的 **Push origin**

完成。其他人在他们电脑上 fetch 就能看到。

### 看研究生改了什么

1. GitHub Desktop → Fetch origin
2. 顶部菜单 View → Repository → History
3. 看到所有提交记录，点进去能看具体改了哪几行

### 给研究生分配任务

1. GitHub 网页打开仓库 → Issues 标签 → New Issue
2. 标题: 例如 `[Stage 1] 完成 P0 数据资产摸底`
3. 描述: 写清楚要做什么、做到什么程度
4. 右边 Assignees → 选研究生
5. 右边 Labels → 加标签 (可选)
6. 提交

研究生会收到通知。

---

## 几个铁律 · Iron Rules

| 铁律 | 说明 |
|---|---|
| **不要把学生数据传 git** | 数据走另外的通道(NAS / 加密 U 盘) |
| **不要把 API key 传 git** | 写在 `.env` 文件里(.gitignore 已忽略) |
| **每次工作完都 push** | 不然电脑坏了就没了 |
| **commit message 写人话** | 三个月后你自己能看懂 |

---

## 遇到问题 · Troubleshooting

### Q: GitHub Desktop 推送失败

- 检查网络
- 试试 Repository → Repository Settings → 看 Remote 配置是否正确

### Q: 不小心 commit 了不该 commit 的文件

- GitHub Desktop → History → 找到那个 commit → 右键 → Revert
- 如果已经 push 了，找懂 git 的人帮忙(或者让研究生帮你)

### Q: 研究生提了 PR 但我看不懂

- GitHub 网页点开 PR → Files changed 标签 → 看具体改动
- 不确定就在 PR 下面评论问研究生

### Q: 我想撤回最近一次 push

- 找研究生帮忙。这操作有点危险，不要自己乱试

---

## 下一步 · Next Steps

1. ✅ 完成 git 初始化
2. ☐ 邀请研究生
3. ☐ 用研究生 onboarding checklist(`docs/onboarding.md`)安排第一周
4. ☐ 准备好基准教材 PDF、题库位置等(线下事项)
5. ☐ 申请学校 IT 资源(开发服务器、DeepSeek API)
6. ☐ 给四位顾问老师发告知邮件(模板见 `docs/advisor-email-template.md`)
