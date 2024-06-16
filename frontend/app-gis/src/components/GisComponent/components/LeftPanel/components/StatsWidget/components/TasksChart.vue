<script setup lang="ts">
import Highcharts from 'highcharts/highcharts.src';
import HighchartsMore from 'highcharts/highcharts-more.src';
import ModulesAccessibility from 'highcharts/modules/accessibility.src';
import { onMounted } from 'vue';

HighchartsMore(Highcharts);
ModulesAccessibility(Highcharts);

const props = defineProps<{
  data: Map<string, number[]>;
}>();

onMounted(() => {
  // @ts-ignore //
  Highcharts.chart('tasks-container', {
    chart: {
      type: 'pie',
    },
    title: {
      text: 'Задания на объектах',
    },
    credits: {
      enabled: false,
    },
    plotOptions: {
      series: {
        allowPointSelect: false,
        cursor: 'pointer',
        dataLabels: [
          {
            enabled: true,
            distance: 10,
          },
        ],
      },
    },
    series: [
      {
        tooltip: {
          pointFormatter: function () {
            return `<span style="color:${this.color}">\u25CF</span> ${this.name}: ${this.y} объектов<br/>`;
          },
        },
        data: Object.entries(props.data).map(([key, value]) => {
          return {
            name: key,
            y: value,
          };
        }),
      },
    ],
  });
});
</script>

<template>
  <div id="tasks-container" />
</template>

<style scoped lang="scss">
#tasks-container {
  width: 46%;
  height: 300px;
}
</style>
