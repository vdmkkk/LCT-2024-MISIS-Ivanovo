<script setup lang="ts">
// @ts-nocheck //
import getPredictsByUnom from 'src/api/getPredictsForUnom';
import { onMounted, ref, reactive, watch, computed } from 'vue';
import LineChartAllEvents from './components/LineChartAllEvents.vue';
import LineChartOnlyOk from './components/LineChartOnlyOk.vue';

const props = defineProps<{
  object: Map<string, any>;
}>();

const loadData = () => {
  getPredictsByUnom(props.object['unom']).then((res) => {
    console.log(res);
    data.value = res;
  });
};

const data = ref();
onMounted(() => {
  // @ts-ignore //
  loadData();
});

const n = computed(() => {
  return props.object.unom;
});

watch(n, loadData);
</script>

<template>
  <div class="predict-container">
    <h1>Предсказания</h1>
    <LineChartAllEvents v-if="data?.['predict']" :data="data['predict']" />
    <LineChartOnlyOk v-if="data?.['predict']" :data="data['predict']" />
  </div>
</template>

<style scoped lang="scss">
.predict-container {
  max-height: 80vh;
  overflow-y: auto;
  h1 {
    font-size: 1.9em;
    font-weight: 500;
    margin-top: 0px;
  }
}
</style>
