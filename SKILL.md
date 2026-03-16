---
name: set-public-state-sync
description: 在每次 OpenClaw 执行任务时同步更新 public 下的 JSON（state.json 与 history_task.json），让 UI 能显示当前状态与任务历史。适用于任何任务执行场景：任务开始与结束都必须写入。
---

# OpenClaw 公共状态同步（public JSON）

## 目标

在**每次执行任务**时，通过写入 `public/` 下的 JSON 文件，让应用 UI 始终能反映当前工作状态与任务历史。

## 需要更新的文件

- `public/user.json`（对象）
  - `agent_name`：执行中
  - `state`：执行中用 `"focus"`；结束后（含失败）用 `"relax"`
  - `detail`：给人看的简短描述
  - `progress`：`[0, 100]` 的数字
  - `updated_at`：ISO-8601 时间戳（允许本地时间；有条件尽量带时区）
- `public/history_task.json`（数组）
  - **任务开始**追加 1 条记录
  - **任务结束**追加 1 条记录

## 强制流程（必须遵守）

### 0）确定任务标题

从用户请求中提炼一个短标题（建议不超过 80 字符），并在本次任务全程保持一致。

### 1）任务开始（在做任何修改之前）

1. 更新 `public/state.json`：
   - `state="working"`
   - `detail="执行中：{title}"`
   - `progress=0`
   - `updated_at=now`
2. 向 `public/history_task.json` 追加一条开始记录（`phase="start"`）：

```json
{
  "title": "<title>",
  "phase": "start",
  "at": "<now-iso>",
  "status": "working"
}
```

### 2）任务进行中（可选，但长任务强烈建议）

当出现明显阶段性进展时，更新 `public/state.json`：
- 逐步提升 `progress`（例如 10 → 30 → 60 → 90）
- `detail` 写当前子步骤
- 刷新 `updated_at`

### 3）任务结束（必须执行，失败也必须执行）

1. 更新 `public/state.json`：
   - `state="relax"`
   - 成功：`progress=100`；失败：保留最后进度，并在 `detail` 写失败摘要
   - `detail`：
     - 成功：`完成：{title}`
     - 失败：`失败：{title}（<简短原因>）`
   - `updated_at=now`
2. 向 `public/history_task.json` 追加一条结束记录（`phase="end"`）：

```json
{
  "title": "<title>",
  "phase": "end",
  "at": "<now-iso>",
  "status": "success|failure"
}
```

## 写入方式（推荐）

优先使用项目脚本：

```bash
python scripts/edit_public_json.py --filename state.json --set state=working --set detail="执行中：..." --set progress=0 --set updated_at="2026-03-16T12:34:56+08:00"
```

追加任务历史（文件不存在或为空时自动创建/初始化）：

```bash
python scripts/edit_public_json.py --filename history_task.json --create --append '{"title":"...","phase":"start","at":"...","status":"working"}'
python scripts/edit_public_json.py --filename history_task.json --create --append '{"title":"...","phase":"end","at":"...","status":"success"}'
```

如果不用脚本而是直接改文件，务必保证：**JSON 合法** 且 **UTF-8 编码**。

