## 项目简介

`ai-agent-office` 是一个用于展示「智能体工作看板」的前端项目。

页面通过读取 `public/*.json` 文件，实时展示智能体的：

- 基本信息：名称、自我介绍、当前是否在线
- 技能结构：核心技能 / 基本技能 两个 Tab
- 当前工作：当前任务标题、描述与“工作内容”流式输出
- 历史工作：按时间倒序的任务历史列表
- 历史记忆：智能体在进化过程中沉淀的经验总结

配合 `scripts/edit_public_json.py` 脚本和根目录 `SKILL.md`，可以让 OpenClaw（或其他代理）在每次执行任务时自动更新这些 JSON，让 UI 成为一个实时的智能体工作与记忆面板。

---

## 目录结构（核心部分）

```text
ai-agent-office/
├─ index.html              # 入口 HTML
├─ vite.config.js          # Vite 配置
├─ package.json            # 依赖与脚本
├─ SKILL.md                # 给 OpenClaw/Agent 的操作说明（更新 public JSON 的规则）
├─ scripts/
│  └─ edit_public_json.py  # 通用 JSON 修改脚本（支持 set / append / 自动创建）
├─ public/
│  ├─ user.json            # 智能体身份与在线状态 + 自我介绍
│  ├─ skill.json           # 技能列表（核心/基本，两类）
│  ├─ current_task.json    # 当前工作任务及流式输出
│  ├─ history_task.json    # 历史任务聚合列表
│  └─ memory.json          # 历史记忆（经验总结）
└─ src/
   ├─ main.js              # Vue 入口
   ├─ App.vue              # 主界面：头部 + 左/中/右三列面板
   ├─ styles.css           # 全局样式（rem + 响应式 + 骨架屏/空态）
   └─ components/
      └─ SkillBar.vue      # 单个技能条目组件（仅展示技能名）
```

---

## 运行方式

### 1）安装依赖

```bash
cd ai-agent-office
npm install
# 或
yarn
```

### 2）启动开发环境

```bash
npm run dev
# 或
yarn dev
```

启动后在终端中会看到本地访问地址，例如：

```text
Local:   http://localhost:19000/
```

---

## 数据文件说明（public/*.json）

### 1）`public/user.json`

智能体的基本信息与当前状态，用于头部展示与中间视频切换：

```json
{
  "agent_name": "项目经理",
  "intro": "擅长把复杂需求拆解为可落地的方案，并用可视化状态持续同步进度。",
  "state": "relax",
  "is_online": true
}
```

- `agent_name`：智能体名称
- `intro`：自我介绍，会显示在头部名称后
- `state`：`focus` 时显示工作视频，`relax` 时显示休闲视频
- `is_online`：在线状态

### 2）`public/skill.json`

左侧技能面板的数据源，分为核心技能与基本技能两个 Tab：

```json
[
  { "name": "planning", "label": "需求分析与方案设计", "type": "core" },
  { "name": "docs", "label": "文档与规范沉淀", "type": "basic" }
]
```

- `type`：`core` / `basic`（决定归属的 Tab）
- `label`：展示文案
- 兼容：老数据里的 `percent` 仍可存在，但 UI 不再显示熟练度条

技能列表区域有最大高度，技能过多时支持滚动查看。

### 3）`public/current_task.json`

当前正在进行的任务 + 实时输出，位于左侧「当前工作」模块：

```json
{
  "task_id": "2026-03-16T10:30:00+08:00#001",
  "task_name": "在项目中增加 Python 脚本修改 public json",
  "task_des": "新增脚本用于修改 public 下的 json，并在每次任务执行时同步更新状态与任务历史。",
  "status": "working",
  "progress": 0,
  "updated_at": "2026-03-16T10:32:10+08:00",
  "stream": [
    { "at": "2026-03-16T10:30:00+08:00", "text": "开始执行任务" },
    { "at": "2026-03-16T10:30:10+08:00", "text": "分析现有 public json" }
  ]
}
```

- `task_name` / `task_des`：任务标题与描述
- `status`：`queued | working | blocked | success | failure | cancelled`
- `progress`：0–100（可选）
- `stream` / `logs` / `output`：
  - 字符串数组或对象数组，作为「工作内容」流式展示
  - 追加新项后页面会自动滚动到底部

### 4）`public/history_task.json`

右侧「历史工作」的数据源，按时间倒序排列：

```json
[
  {
    "task_id": "2026-03-16T10:30:00+08:00#001",
    "task_name": "示例：构建任务状态同步",
    "task_des": "让 UI 可以展示当前任务、历史工作与流式输出。",
    "status": "success",
    "started_at": "2026-03-16T10:30:00+08:00",
    "finished_at": "2026-03-16T10:35:12+08:00",
    "summary": "已完成 public JSON 同步与 UI 展示。",
    "tags": ["ui", "json", "sync"],
    "error": null
  }
]
```

- 页面按 `started_at`（兜底 `finished_at`）倒序展示（最近的在最上面）

### 5）`public/memory.json`

右侧「历史记忆」的数据源，记录智能体经验总结，按时间倒序展示：

```json
[
  {
    "memory_id": "mem-001",
    "title": "任务要先对齐数据结构再做 UI",
    "des": "先把 public 下 JSON 的字段设计清楚，再做页面渲染与空态，能显著减少返工。",
    "tags": ["结构化", "UI", "经验"],
    "at": "2026-03-16T10:50:00+08:00"
  }
]
```

---

## 运行时行为与轮询机制

在 `src/App.vue` 中，页面通过 `fetch('/xxx.json?t=timestamp')` 周期性轮询获取数据：

- 初次加载：显示骨架屏（placeholder）
- 加载结束但数据为空：显示空态卡片（避免页面空洞）
- 当前工作流式输出：新增内容后自动滚动到底部
- 历史工作/历史记忆：按时间倒序展示

---

## 与 Agent / OpenClaw 的集成

### 1）根目录 `SKILL.md`

`SKILL.md` 定义了 Agent 在任务开始/进行中/结束时如何同步更新 `public/*.json`：

- 任务开始前：更新 `user.json`、初始化 `current_task.json`、在 `history_task.json` 写入占位记录，并确保 `skill.json` / `memory.json` 至少为 `[]`
- 任务进行中：持续更新 `current_task.json` 的 `progress/updated_at` 并向 `stream` 追加输出
- 任务结束：写回最终状态到 `current_task.json`，并完善/追加 `history_task.json` 的最终记录；如有经验沉淀可追加到 `memory.json`

### 2）Python 脚本 `scripts/edit_public_json.py`

用于可靠更新 `public` 下的 JSON（支持空文件初始化、自动创建、对象字段更新、数组追加）：

```bash
# 更新对象类 JSON（如 user.json）
python scripts/edit_public_json.py --filename user.json \
  --set state=focus --set is_online=true --set intro='"我是自适应工作看板智能体"'

# 追加历史任务记录（文件不存在或为空时自动创建 / 初始化）
python scripts/edit_public_json.py --filename history_task.json --create \
  --append '{"task_id":"...","task_name":"...","task_des":"...","status":"working","started_at":"..."}'

# 追加一条历史记忆
python scripts/edit_public_json.py --filename memory.json --create \
  --append '{"memory_id":"mem-xxx","title":"...","des":"...","tags":["..."],"at":"..."}'
```

---

## 主要 UI 特点

- 响应式字体：使用 `rem` 并根据屏幕宽度调整基准字号
- 骨架屏与空态：模块在无数据时也不会显得空洞
- 技能 Tab：核心技能 / 基本技能，列表过长可滚动
- 工作内容流式展示：新增后自动滚动到底部
