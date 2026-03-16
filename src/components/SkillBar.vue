<template>
  <div class="skill-row">
    <div class="skill-label">{{ label }}</div>
    <div class="skill-bar">
      <div class="skill-bar-fill" :style="{ width: percent + '%' }"></div>
    </div>
    <div class="skill-percent">{{ percent }}%</div>
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
    percent: {
      type: Number,
      required: true
    }
  }
};
</script>

