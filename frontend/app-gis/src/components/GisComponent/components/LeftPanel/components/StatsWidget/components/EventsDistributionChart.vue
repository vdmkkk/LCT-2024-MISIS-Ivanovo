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
  Highcharts.chart('event-distribution-container', {
    chart: {
      type: 'pie',
    },
    title: {
      text: 'Распределение событий',
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
            return `<span style="color:${this.color}">\u25CF</span> ${this.name}: ${this.y} событий <br/>`;
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
  <div id="event-distribution-container" />
</template>

<style scoped lang="scss">
#event-distribution-container {
  width: 46%;
  height: 300px;
}
</style>
