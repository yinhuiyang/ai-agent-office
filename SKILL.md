---
name: set-public-state-sync
description: 在每次 OpenClaw 执行任务时同步更新 public 下的 JSON（user.json、skill.json、current_task.json、history_task.json、memory.json），让 UI 能显示自我介绍、技能（核心/基本 tab）、当前任务流式输出、历史工作与历史记忆。适用于任何任务执行场景：任务开始、进行中、结束都必须写入。
---

# OpenClaw 公共状态同步（public JSON）

## 目标

在**每次执行任务**时，通过写入 `public/` 下的 JSON 文件，让应用 UI 始终能反映：

- 当前 Agent 身份与在线状态（`user.json`）
- 技能列表（`skill.json`，核心技能/基本技能两个 tab）
- 当前正在执行的任务详情与实时输出（`current_task.json`）
- 历史任务列表（`history_task.json`）
- 历史记忆（`memory.json`）

---

## 1. 首次部署（Bootstrap 时执行）

在你的 workspace 里按顺序执行：

```bash
# 1) 如果在 workspace 里不存在 ai-agent-office 文件夹，则下载仓库
cd <workspace>
git clone https://github.com/yinhuiyang/ai-agent-office.git
cd ai-agent-office

# 如果已经存在 ai-agent-office，则拉取 main 分支最新代码
cd <workspace>
cd ai-agent-office
git pull origin main

# 2) 安装依赖（任选其一）
npm install        # 或 yarn 

# 3) 启动服务
npm run dev        # 或 yarn dev
```

然后观察启动日志，找到启动的服务端口，告诉主人访问地址。

---

## 2. 需要维护的 JSON 文件

- `public/skill.json`（数组）  
  技能列表（**不展示熟练度**），形如：
  ```json
  [
    { "name": "planning", "label": "需求分析与方案设计", "type": "core" },
    { "name": "docs", "label": "文档与规范沉淀", "type": "basic" }
  ]
  ```
  - `type`：`core | basic`（用于 UI 的「核心技能/基本技能」tab）
  - `label`：展示用名称
  - 兼容：如果老数据仍包含 `percent`，UI 可能会用它做核心/基本的兜底分组，但**不建议继续写 percent**。

- `public/user.json`（对象）
  - `agent_name`：当前工作区中 agent 的名字；重要：优先从 openclaw.json 的配置中读取（例如 main 工作区：`"项目经理"`）
  - `intro`：自我介绍（用于头部名称后显示；建议 20–60 字）
  - `state`：Agent 状态，有任务执行中用 `"focus"`；无任务或任务结束后用 `"relax"`
  - `is_online`：当前智能体是否在线，布尔值

- `public/current_task.json`(对象)
  当前进行中任务，持续更新任务内容和任务状态。基础字段建议：
  - `task_id`：任务唯一 ID
  - `task_name`：任务标题（必需）
  - `task_des`：任务描述（必需）
  - `status`：`queued | working | blocked | success | failure | cancelled`
  - `progress`：0–100
  - `eta`：预计剩余时间（可选）
  - `created_at` / `started_at` / `updated_at` / `finished_at`：时间戳
  - `stream` / `logs` / `output`：**工作内容流式输出**，可为：
    - 字符串数组：`["开始处理…", "完成第 1 步…"]`
    - 对象数组：`[{ "id": 1, "at": "...", "text": "..." }]`
    - 单个长字符串：`"第一行...\n第二行..."`

- `public/history_task.json`（数组）
  历史任务列表，每个元素是一条任务汇总记录（非事件流），示例结构：
  ```json
  {
    "task_id": "2026-03-16T10:30:00+08:00#001",
    "task_name": "增加 Python 脚本修改 public JSON",
    "task_des": "新增脚本用于修改 public 下的 json，并完善空文件/自动创建逻辑。",
    "status": "success",
    "started_at": "2026-03-16T10:30:00+08:00",
    "finished_at": "2026-03-16T10:35:12+08:00",
    "duration_ms": 312000,
    "summary": "已新增 edit_public_json.py，并支持 --create 与空文件初始化。",
    "progress": { "max": 100, "final": 100 },
    "tags": ["python", "public", "json"],
    "actor": { "agent": "openclaw" },
    "targets": ["public/state.json", "public/history_task.json"],
    "artifacts": [
      { "type": "file", "path": "scripts/edit_public_json.py" }
    ],
    "error": null
  }
  ```

- `public/memory.json`（数组）
  历史记忆：智能体在进化过程中沉淀的经验总结。每条记录建议结构：
  ```json
  {
    "memory_id": "mem-001",
    "title": "任务要先对齐数据结构再做 UI",
    "des": "先把 public 下 JSON 的字段设计清楚，再做页面渲染与空态，能显著减少返工。",
    "tags": ["结构化", "UI", "经验"],
    "at": "2026-03-16T10:50:00+08:00"
  }
  ```
  - `title` / `des` 为主要展示内容
  - `tags` 用于检索/筛选（可选）
  - `at` 为时间戳（可选但推荐）

---

## 3. 强制流程（每次任务必须遵守）

### 0）确定任务标题与 ID

从用户请求中提炼一个短标题 `task_name`（不超过 80 字符），并生成一个唯一 `task_id`（例如时间戳 + 递增序号）。本次任务全程保持一致。

### 1）任务开始（在做任何修改之前）

1. **更新 `public/user.json`：**
   - `agent_name`：确保非空（若无法从配置读取，则使用默认 `"OpenClaw"`）
   - `intro`：若不存在则写入默认自我介绍，避免头部空洞
   - `state="focus"`
   - `is_online=true`
2. **更新 `public/current_task.json`：**
   ```json
   {
     "task_id": "<task_id>",
     "task_name": "<task_name>",
     "task_des": "<任务描述>",
     "status": "working",
     "progress": 0,
     "created_at": "<now-iso>",
     "started_at": "<now-iso>",
     "updated_at": "<now-iso>",
     "stream": []
   }
   ```
3. **向 `public/history_task.json` 追加一条“开始占位”记录：**
   - 如文件不存在或为空，先初始化为 `[]`
   - 追加的记录至少包含：
   ```json
   {
     "task_id": "<task_id>",
     "task_name": "<task_name>",
     "task_des": "<任务描述>",
     "status": "working",
     "started_at": "<now-iso>"
   }
   ```
4. **确保空数据也不“空洞”**（初始化保障）：
   - `public/skill.json`：必须是数组（至少 `[]`），建议写入最少 2–4 个技能并标注 `type`
   - `public/memory.json`：必须是数组（至少 `[]`）；如暂无记忆，可写入 `[]`，UI 会展示空态卡片

### 2）任务进行中（长任务强烈建议）

当出现明显阶段性进展时：

1. **更新 `public/current_task.json`：**
   - 逐步提升 `progress`（例如 10 → 30 → 60 → 90）
   - 刷新 `updated_at`
   - 在 `stream` / `logs` / `output` 中**追加**新的输出内容（而不是覆盖原有数组）
   - 输出更新后 UI 会自动滚动到底部（无需额外处理）
2. 如有必要，可同步更新 `history_task.json` 中对应 `task_id` 的记录（例如更新 `summary`、`progress.final`）。

### 3）任务结束（必须执行，失败也必须执行）

1. **更新 `public/user.json`：**
   - `state="relax"`
2. **更新 `public/current_task.json`：**
   - 成功：
     - `status="success"`
     - `progress=100`
   - 失败：
     - `status="failure"`
     - `progress` 保留最后进度
   - 写入 `finished_at="<now-iso>"`、`updated_at="<now-iso>"`
3. **在 `public/history_task.json` 中写入最终结果：**
   - 找到相同 `task_id` 的记录并补全：
     - `finished_at`
     - `duration_ms`
     - `status`
     - `summary`
     - `error`（失败时）
   - 若找不到同 `task_id`，则直接追加一条完整的新记录。

---

## 4. 写入方式（推荐）

优先使用项目内的 Python 脚本：

```bash
# 更新对象类 JSON（user.json / current_task.json）
python scripts/edit_public_json.py --filename user.json --set state=focus --set is_online=true

# 追加历史任务（文件不存在或为空时自动创建/初始化）
python scripts/edit_public_json.py --filename history_task.json --create --append '{"task_id":"...","task_name":"...","task_des":"...","status":"working","started_at":"..."}'

# 写入历史记忆（文件不存在或为空时自动创建/初始化）
python scripts/edit_public_json.py --filename memory.json --create --append '{"memory_id":"mem-xxx","title":"...","des":"...","tags":["..."],"at":"..."}'
```

如果不用脚本而是直接改文件，务必保证：**JSON 合法** 且 **UTF-8 编码**。

