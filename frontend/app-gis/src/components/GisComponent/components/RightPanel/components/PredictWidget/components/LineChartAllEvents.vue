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
  Highcharts.chart('linechart-container', {
    chart: {
      type: 'spline',
    },
    title: {
      text: 'Вероятность выполнения событий',
    },
    xAxis: {
      categories: Object.keys(props.data),
      accessibility: {
        description: 'Months of the year',
      },
    },
    yAxis: {
      title: {
        text: '',
      },
      labels: {
        format: '{value}%',
      },
    },
    tooltip: {
      crosshairs: true,
      shared: true,
    },
    credits: {
      enabled: false,
    },
    plotOptions: {
      spline: {
        marker: {
          radius: 4,
          lineColor: '#666666',
          lineWidth: 1,
        },
      },
    },
    series: [
      {
        name: 'ОК',
        marker: {
          enabled: false,
        },
        color: '#0c0',
        tooltip: {
          pointFormatter: function () {
            return `<span style="color:${this.color}">\u25CF</span> ОК: ${this.y}% <br/>`;
          },
        },
        data: Object.values(props.data).map((arr) => Math.round(arr[3] * 100)),
      },
      {
        name: 'T < min',
        marker: {
          enabled: false,
        },
        tooltip: {
          pointFormatter: function () {
            return `<span style="color:${this.color}">\u25CF</span> T < min: ${this.y}% <br/>`;
          },
        },
        data: Object.values(props.data).map((arr) => Math.round(arr[0] * 100)),
      },
      {
        name: 'T > max',
        marker: {
          enabled: false,
        },
        tooltip: {
          pointFormatter: function () {
            return `<span style="color:${this.color}">\u25CF</span> T > max: ${this.y}% <br/>`;
          },
        },
        data: Object.values(props.data).map((arr) => Math.round(arr[1] * 100)),
      },
      {
        name: 'Давление не в норме',
        marker: {
          enabled: false,
        },
        color: '#ff00dc',
        tooltip: {
          pointFormatter: function () {
            return `<span style="color:${this.color}">\u25CF</span> Давление не в норме: ${this.y}% <br/>`;
          },
        },
        data: Object.values(props.data).map((arr) => Math.round(arr[2] * 100)),
      },
      {
        name: 'Утечка',
        marker: {
          enabled: false,
        },
        tooltip: {
          pointFormatter: function () {
            return `<span style="color:${this.color}">\u25CF</span> Утечка: ${this.y}% <br/>`;
          },
        },
        data: Object.values(props.data).map((arr) => Math.round(arr[4] * 100)),
      },
    ],
  });
});
</script>

<template>
  <div id="linechart-container" />
</template>

<style scoped lang="scss">
#linechart-container {
  height: 600px;
}
</style>
