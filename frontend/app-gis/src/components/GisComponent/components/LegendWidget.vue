<script setup lang="ts">
import { computed } from 'vue';
import { useOptionsStore } from 'src/stores/optionsStore';

const optionsStore = useOptionsStore();

const containerClass = computed(() => ({
  'legend-container': true,
  open: optionsStore.mapMode == 'predict',
  closed: optionsStore.mapMode != 'predict',
  'shadow-1': true,
}));
</script>

<template>
  <img src="src/assets/legend.png" :class="containerClass" />
</template>

<style scoped lang="scss">
.legend-container {
  position: absolute;
  bottom: 160px;
  left: 0.5vw;
  border-radius: 20px;
  transition: left 0.2s ease-in-out; /* Smooth transition */
}

.legend-container.open {
  left: 0.5vw; /* Slide in */
}

.legend-container.closed {
  left: -400px; /* Slide out */
}
</style>
