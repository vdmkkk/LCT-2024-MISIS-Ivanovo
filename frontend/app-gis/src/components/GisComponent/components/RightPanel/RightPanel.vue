<script setup lang="ts">
import { toRefs, computed } from 'vue';

const props = defineProps<{
  placeId: number | null;
}>();

const containerClass = computed(() => ({
  container: true,
  open: props.placeId || props.placeId == 0,
  closed: !props.placeId && props.placeId != 0,
}));
</script>

<template>
  <div :class="containerClass">
    <h1>{{ props.placeId }}</h1>
  </div>
</template>

<style scoped>
.container {
  position: absolute;
  height: 95vh;
  top: 2.5vh;
  width: 400px;
  right: 1vw;
  background-color: white;
  transition: right 0.3s ease-in-out; /* Smooth transition */
}

.container.open {
  right: 1vw; /* Slide in */
}

.container.closed {
  right: -400px; /* Slide out */
}
</style>
