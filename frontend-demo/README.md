# SynthSpark — Postmodern Demo Hub

> 分支 `demo/postmodern-interactive` · 浏览器内后现代交互 Demo 集 · 纯前端 Mock · 无需后端

## 启动

```bash
cd frontend-demo
npm install
npm run dev     # http://localhost:5174
npm run build   # 产物 dist/
```

Hub 总览 `http://localhost:5174/`，5 个 Demo：

| 路由 | 隐喻 | 交互关键词 |
|---|---|---|
| `/os` | SynthOS 伪操作系统 | 拖拽/缩放/层叠窗口 + Finder + Spotlight |
| `/terminal` | SynthTerm 鼠标友好终端 | 芯片即命令 + CRT + 卡片输出 |
| `/space` | SynthSpace 空间画廊 | Canvas 星点 + CSS 3D 视差 + 俯瞰 |
| `/desk` | SynthDesk 虚拟笔记本 | 木纹书桌 + 拍立得拖拽 + 活页翻页 |
| `/chat` | SynthChat 群聊×城市 | 三栏 Slack + 等轴城市等价视图 |

全部 Mock 数据 `src/mock/data.ts`，泛用户鼠标友好，GPU 加速用 `transform3d`/`opacity`。

## 后续

- 移动端再议（当前桌面优先）
- 按用户反馈选主方向深化为正式前端 `frontend-next`
