# 前端 · AI 精准教学看板 (Vite + React + TS)

对接重建后的后端 API（`EngineDataGateway`）。所有数据请求按 `?course_code=` 取课程。

## 运行
```bash
cd frontend
npm install
npm run dev        # 默认 http://localhost:5173
```
后端地址由 `frontend/.env.local` 的 `VITE_API_URL` 指定（默认 `http://localhost:8000`）。
后端已开放 CORS，前端跨域直连，无需代理。

> 先确保后端在跑、且 ETL 已灌入至少一章数据，否则课程/学生下拉为空。

## 结构
```
src/
├── services/api.ts      axios 客户端 + 各接口
├── types/index.ts       API 响应类型
├── context/AppContext   全局选中的课程/学生（顶栏下拉驱动）
├── hooks/useAsync       通用异步加载
├── components/          TopBar（导航+选择器）、ui（Card/Stat/Badge/Bar…）
└── pages/
    ├── OverviewPage      总览：分层分布 / 预警名单 / 高频错因
    ├── DiagnosisPage     错因诊断（核心）：掌握度 / 逐题诊断 / 优先干预
    ├── ProfilePage       学生三维画像
    └── RecommendationPage 三路径推荐
```

## 说明
- 顶栏选课程→自动加载该课学生→各页据此请求。
- 推荐页、前置回溯相关展示在“资源打标签 / 图谱前置边”就绪前会显示空态（属正常）。
