<template>
  <div class="skill-item">
    <div class="skill-item-dot"></div>
    <div class="skill-item-label">{{ label }}</div>
  </div>
</template>

<script>
export default {
  name: "SkillBar",
  props: {
    label: {
      type: String,
      required: true
    },
    // percent 已弃用（UI 不再展示熟练度），保留以兼容旧数据
    percent: {
      type: Number,
      required: false,
      default: null
    }
  }
};
</script>

