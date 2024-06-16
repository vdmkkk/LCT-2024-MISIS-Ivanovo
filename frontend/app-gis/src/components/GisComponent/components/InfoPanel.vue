<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import { useOptionsStore } from 'src/stores/optionsStore';

const optionsStore = useOptionsStore();

const mainLabel = ref<string>('Режим мониторинга');

const mapModeObject = computed(() => {
  const obj: Record<string, string> = {};
  obj['mode'] = optionsStore.mapMode;
  return obj;
});

const changeLabel = () => {
  if (optionsStore.mapMode == 'incident') mainLabel.value = 'Аварийный режим';
  else if (optionsStore.mapMode == 'predict')
    mainLabel.value = 'Режим предсказаний';
  else mainLabel.value = 'Режим мониторинга';
};

watch(mapModeObject, changeLabel);

const currentDate = ref(new Date());

const props = defineProps<{
  data: Map<string, number[]>;
}>();

interface TaskData {
  name: string;
  y: number;
}

const taskData = ref<TaskData[]>([]);

onMounted(() => {
  const taskKeys = ['Без событий'];

  if (props.data) {
    taskData.value = Object.entries(props.data)
      .filter(([key]) => taskKeys.includes(key))
      .map(([key, value]) => {
        return {
          name: key,
          y: value, // Используем первое значение из массива
        };
      });
  }

  const interval = setInterval(() => {
    currentDate.value = new Date();
  }, 1000);

  onUnmounted(() => {
    clearInterval(interval);
  });
});

const formattedDate = computed(() => {
  const date = currentDate.value;

  const pad = (num: any) => (num < 10 ? '0' + num : num);

  const hours = pad(date.getHours());
  const minutes = pad(date.getMinutes());
  const seconds = pad(date.getSeconds());
  const day = pad(date.getDate());
  const month = pad(date.getMonth() + 1); // Months are zero-based
  const year = date.getFullYear();

  return `${hours}:${minutes}:${seconds} 01-04-2024`;
});
</script>

<template>
  <div class="info-container shadow-1">
    <h4>{{ mainLabel }}</h4>
    <div style="display: flex; gap: 10px">
      <h5>{{ formattedDate }}</h5>
      <h5>
        <span class="material-symbols-outlined"> partly_cloudy_day </span>+21°
      </h5>
      <div v-for="task in taskData" :key="task.name">
        <h5>{{ task.name }}: {{ task.y }}</h5>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.info-container {
  position: absolute;
  bottom: 2vh;
  left: 0.5vw;
  background-color: white;
  border-radius: 30px;
  display: block;
  padding-left: 15px;
  padding-right: 40px;
  padding-bottom: 30px;
  padding: 24px;
  padding-top: 4px;
  opacity: .7;

  h4 {
    font-size: 1.8em;
    margin: 0px;
    margin-top: 10px;
    font-weight: 500;
  }

  h5 {
    font-size: 1.5em;
    margin: 0px;
    margin-top: 10px;
    font-weight: 400;
  }

  .material-symbols-outlined {
    font-size: 1.6em;
    margin-right: 6px;
  }
}
</style>
