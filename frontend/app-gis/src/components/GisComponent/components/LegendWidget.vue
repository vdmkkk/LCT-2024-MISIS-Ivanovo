<script setup lang="ts">
import { computed } from 'vue';
import { useOptionsStore } from 'src/stores/optionsStore';

const optionsStore = useOptionsStore();

const props = defineProps<{
  incidentId?: number | null;
  incidentMode: number | null;
}>();

const containerClass = computed(() => ({
  'legend-container': true,
  'open-predicts': optionsStore.mapMode == 'predict',
  'open-incidents':
    optionsStore.mapMode == 'incident' &&
    (props.incidentId || props.incidentId == 0),
  closed:
    optionsStore.mapMode != 'predict' &&
    !(
      optionsStore.mapMode == 'incident' &&
      (props.incidentId || props.incidentId == 0)
    ),
  'shadow-1': true,
}));

const src = computed(() => getPic());

const getPic = () => {
  if (optionsStore.mapMode == 'predict') return 'src/assets/legend_predict.png';
  else if (optionsStore.mapMode == 'incident' && props.incidentMode == 0)
    return 'src/assets/legend_incident_0.png';
  else return 'src/assets/legend_incident_1.png';
};
</script>

<template>
  <img :src="src" :class="containerClass" />
</template>

<style scoped lang="scss">
.legend-container {
  position: absolute;
  left: 0.5vw;
  border-radius: 20px;
  transition: left 0.2s ease-in-out; /* Smooth transition */
}

.legend-container.open-predicts {
  left: 0.5vw; /* Slide in */
  bottom: 160px;
}

.legend-container.open-incidents {
  left: 0.5vw; /* Slide in */
  bottom: 260px;
}

.legend-container.closed {
  left: -400px; /* Slide out */
}
</style>
