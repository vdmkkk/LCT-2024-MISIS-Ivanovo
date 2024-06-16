<script setup lang="ts">
import { computed } from 'vue';
import { useOptionsStore } from 'src/stores/optionsStore';

const optionsStore = useOptionsStore();

const containerClass = computed(() => ({
  'legend-container': true,
  open: optionsStore.mapMode == 'incident',
  closed: optionsStore.mapMode != 'incident',
  'shadow-1': true,
}));
</script>

<template>
  <div :class="containerClass">
    <i style="color: #a90028" class="material-symbols-outlined">add</i>
    <h5>Добавить аварию</h5>
  </div>
</template>

<style scoped lang="scss">
.legend-container {
  position: absolute;
  bottom: 160px;
  left: 0.5vw;
  border-radius: 20px;
  font-size: 48px;
  gap: 4px;
  padding: 20px;
  transition: left 0.2s ease-in-out; /* Smooth transition */
  display: flex;
  background-color: white;
  align-items: center;
  cursor: pointer;
  h5 {
    margin: 0;
  }
}

.legend-container.open {
  left: 0.5vw; /* Slide in */
}

.legend-container.closed {
  left: -400px; /* Slide out */
}
</style>
