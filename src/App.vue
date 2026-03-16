<template>
  <div class="app-root">
    <header class="app-header">
      <div class="logo-title">
        <span class="logo-dot"></span>
        <span class="logo-text">{{ user.agent_name }}</span>
      </div>
      <button class="status-pill" :class="{ online: user.is_online, offline: !user.is_online }">{{ user.is_online ? '在线' : '离线' }}</button>
    </header>

    <main class="app-main">
      <section class="panel panel-left">
        <h2 class="panel-title">核心技能</h2>
        <SkillBar
          v-for="skill in skills"
          :key="skill.name"
          :label="skill.label"
          :percent="skill.percent"
        />

        <h2 class="panel-title panel-title-spacing">当前工作</h2>
        <div class="ongoing-card" :class="{ loading: isLoadingCurrentTask }">
          <div class="ongoing-label">
            <span class="loading-skeleton" v-if="isLoadingCurrentTask"></span>
            <span v-else>{{ currentTask.task_name }}</span>
          </div>
          <div class="ongoing-sub">
            <span class="loading-skeleton loading-skeleton--wide" v-if="isLoadingCurrentTask"></span>
            <span v-else>{{ currentTask.task_des }}</span>
          </div>
          <div class="progress-track">
            <div
              class="progress-fill"
              :style="{ width: Math.max(0, Math.min(100, Number(currentTask.progress || 0))) + '%' }"
            ></div>
          </div>
          <div class="ongoing-footer">
            <span v-if="isLoadingCurrentTask">加载中…</span>
            <span v-else>预计剩余时间：{{ currentTask.eta || '未知' }}</span>
          </div>

          <div class="ongoing-stream" v-if="!isLoadingCurrentTask">
            <div class="ongoing-stream-title">工作内容</div>
            <ul class="ongoing-stream-list" v-if="streamItems.length">
              <li v-for="item in streamItems" :key="item._key" class="ongoing-stream-item">
                <span class="ongoing-stream-at" v-if="item.at">{{ formatTime(item.at) }}</span>
                <span class="ongoing-stream-text">{{ item.text }}</span>
              </li>
            </ul>
            <div class="ongoing-stream-empty" v-else>暂无输出</div>
          </div>
        </div>
      </section>

      <section class="panel-center">
        <div class="agent-wrapper">
          <div class="agent-image-frame">
            <video
              v-show="agentState === 'focus'"
              autoplay
              loop
              muted
              playsinline
              :alt="agentState === 'focus' ? '专注工作状态' : '休闲思考状态'"
            >
              <source v-show="agentState === 'focus'" src="./assets/agent-focus.mp4" type="video/mp4">
              Your browser does not support the video tag.
            </video>
            <video
              v-show="agentState === 'relax'"
              autoplay
              loop
              muted
              playsinline
              :alt="agentState === 'focus' ? '专注工作状态' : '休闲思考状态'"
            >
              <source v-show="agentState === 'relax'" src="./assets/agent-relax.mp4" type="video/mp4">
              Your browser does not support the video tag.
            </video>
          </div>

          <!-- <div class="state-switcher">
            <button
              class="state-card"
              :class="{ active: agentState === 'focus' }"
              @click="setState('focus')"
            >
              <span class="state-label">工作模式</span>
              <span class="state-desc">实时监测任务流与数据看板。</span>
            </button>
            <button
              class="state-card"
              :class="{ active: agentState === 'relax' }"
              @click="setState('relax')"
            >
              <span class="state-label">休闲模式</span>
              <span class="state-desc">进入策略思考与任务总结视角。</span>
            </button>
          </div> -->
        </div>
      </section>

      <section class="panel panel-right">
        <h2 class="panel-title">历史工作</h2>
        <ul class="history-list">
          <li
            v-for="item in historyTask"
            :key="item.task_id"
            class="history-item"
            :class="{ active: activeHistoryId === item.task_id }"
            @click="activeHistoryId = item.task_id"
          >
            <div class="history-status-icon" :class="{ done: item.status === 'success' }"></div>
            <div class="history-content">
              <div class="history-time">{{ new Date(item.started_at).toLocaleString() }}</div>
              <div class="history-title">{{ item.task_name }}</div>
              <div class="history-desc">{{ item.task_des }}</div>
            </div>
          </li>
        </ul>
      </section>
    </main>
  </div>
</template>

<script>
import SkillBar from "./components/SkillBar.vue";

import agentFocus from "./assets/agent-focus.mp4";
import agentRelax from "./assets/agent-relax.mp4";

export default {
  name: "App",
  components: { SkillBar },
  data() {
    return {
      user: { agent_name: "OpenClaw", is_online: true },
      skills: [],
      currentTask: {
        task_name: "加载中…",
        task_des: "",
        progress: 0,
        eta: "",
        stream: []
      },
      historyTask: [],
      ongoingProgress: 72,
      eta: "2 小时",
      agentState: "focus",
      isLoadingCurrentTask: true,
      streamItems: [],
      _pollTimer: null,
      _lastStreamKeySet: new Set(),
      history: [
        {
          id: 1,
          time: "2023‑10‑24 14:30",
          title: "Q3 时序数据可视化报告",
          desc: "处理了 5000 条监控数据，生成决策仪表盘。",
          done: true
        },
        {
          id: 2,
          time: "2023‑10‑20 09:15",
          title: "客户对话系统自动化集成",
          desc: "接入 NLP 模型，实现外部系统接口联调。",
          done: true
        },
        {
          id: 3,
          time: "2023‑10‑18 15:00",
          title: "核心数据集清理与优化",
          desc: "分布式清洗 1200 万条记录，提升查询性能。",
          done: true
        }
      ],
      activeHistoryId: 1
    };
  },
  computed: {
    currentAgentImage() {
      return this.agentState === "focus" ? agentFocus : agentRelax;
    }
  },
  methods: {
    setState(state) {
      this.agentState = state;
    },
    formatTime(isoLike) {
      try {
        return new Date(isoLike).toLocaleTimeString();
      } catch (e) {
        return "";
      }
    },
    async fetchJson(path) {
      const url = `/${path}?t=${Date.now()}`;
      const res = await fetch(url, { cache: "no-store" });
      if (!res.ok) throw new Error(`Fetch failed: ${path}`);
      return await res.json();
    },
    normalizeStreamItems(raw) {
      // 支持两种格式：
      // 1) stream: ["text", ...]
      // 2) stream: [{ id?, at?, text }, ...]
      if (!raw) return [];
      if (Array.isArray(raw)) {
        return raw
          .map((x, idx) => {
            if (typeof x === "string") return { at: null, text: x, _key: `s:${idx}:${x}` };
            if (x && typeof x === "object") {
              const at = x.at || x.time || null;
              const text = x.text || x.message || "";
              const id = x.id || x.seq || null;
              const key = id ? `id:${id}` : `o:${idx}:${at || ""}:${text}`;
              return { at, text, _key: key };
            }
            return null;
          })
          .filter((x) => x && x.text);
      }
      if (typeof raw === "string") {
        // 如果后端用单个字符串不断增长，前端按“整段”显示（不做 diff）
        return [{ at: null, text: raw, _key: "text:0" }];
      }
      return [];
    },
    mergeStreamItems(nextItems) {
      // 将新增内容“流式追加”，不重复写入
      const added = [];
      for (const item of nextItems) {
        if (this._lastStreamKeySet.has(item._key)) continue;
        this._lastStreamKeySet.add(item._key);
        added.push(item);
      }
      if (added.length) {
        this.streamItems = [...this.streamItems, ...added].slice(-80);
      }
    },
    async pollPublicFiles() {
      try {
        const [skills, user, currentTask, historyTask] = await Promise.all([
          this.fetchJson("skill.json").catch(() => null),
          this.fetchJson("user.json").catch(() => null),
          this.fetchJson("current_task.json").catch(() => null),
          this.fetchJson("history_task.json").catch(() => null)
        ]);

        if (skills) this.skills = skills;
        if (user) this.user = user;
        if (Array.isArray(historyTask)) this.historyTask = historyTask;

        if (currentTask && typeof currentTask === "object") {
          this.currentTask = { ...this.currentTask, ...currentTask };
          const nextStream = this.normalizeStreamItems(currentTask.stream || currentTask.logs || currentTask.output);
          this.mergeStreamItems(nextStream);
          this.isLoadingCurrentTask = false;
        }
      } catch (e) {
        // 首次加载失败时仍保持 loading 态；后续失败不清空已有数据
      }
    }
  },
  async mounted() {
    await this.pollPublicFiles();
    this._pollTimer = setInterval(() => {
      this.pollPublicFiles();
    }, 800);
  },
  beforeUnmount() {
    if (this._pollTimer) clearInterval(this._pollTimer);
  }
};
</script>

<style scoped>
.scoped-placeholder { opacity: 1; }
</style>

