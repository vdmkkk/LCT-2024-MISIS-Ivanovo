<script setup lang="ts">
import { computed, ref, onMounted } from 'vue';
import { useOptionsStore } from 'src/stores/optionsStore';
import getStats from 'src/api/getStats';

import EventsDistributionChart from './components/EventsDistributionChart.vue';
import TasksChart from './components/TasksChart.vue';

const optionsStore = useOptionsStore();

const containerClass = computed(() => ({
  'select-filters': true,
  open: show.value,
  closed: !show.value,
}));

const show = computed(() => {
  return optionsStore.leftPanelOption == 'chart';
});

const distributionData = ref<Map<string, number[]>>();
const tasksData = ref<Map<string, number[]>>();
const weather1 = ref();
const weather2 = ref();

onMounted(() => {
  getStats()
    .then((res) => {
      distributionData.value = res['event_counts'];
      tasksData.value = {
        // @ts-ignore //
        'Без событий': res['n_unoms_without_events'],
        'Собранные события': res['count_collect_tasks'],
        'Текущие события': res['count_current_tasks'],
      };
      weather1.value = res['weather1'];
      weather2.value = res['weather2'];
    })
    .then();
});
</script>

<template>
  <div v-if="show" :class="containerClass">
    <h5>Статистика за 2 недели</h5>
    <div style="display: flex">
      <EventsDistributionChart :data="distributionData!" />
      <TasksChart :data="tasksData!" />
    </div>
    <h6>Средняя температура днем: {{ weather1 }}°</h6>
    <h6>Средняя температура ночью: {{ weather2 }}°</h6>
  </div>
</template>

<style lang="scss">
.select-filters {
  position: absolute;
  background-color: white;
  top: 100px;
  width: 25vw;
  padding: 24px;
  z-index: 999;
  border-radius: 20px;
  padding-bottom: 20px;
  display: flex;
  flex-direction: column;
  transition: left 0.3s ease-in-out; /* Smooth transition */
  max-height: 600px;
  box-shadow: 0px 4px 20px rgba(0, 0, 0, .1);

  h5,
  h6 {
    margin: 0;
    margin-top: 10px;
    margin-bottom: 10px;
    font-weight: 400;
  }
}

.select-filters.open {
  left: 70px; /* Slide in */
}

.select-filters.closed {
  left: -20vw; /* Slide out */
}
</style>
