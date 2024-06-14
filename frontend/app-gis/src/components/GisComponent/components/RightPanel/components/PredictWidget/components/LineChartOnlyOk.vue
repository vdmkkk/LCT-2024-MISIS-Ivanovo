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
  Highcharts.chart('linechart-container-ok', {
    chart: {
      type: 'spline',
    },
    title: {
      text: 'Вероятность возникновения аварии',
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
        name: 'Произойдет авария',
        marker: {
          enabled: false,
        },
        color: '#c00',
        tooltip: {
          pointFormatter: function () {
            return `<span style="color:${this.color}">\u25CF</span> ОК: ${this.y}% <br/>`;
          },
        },
        data: Object.values(props.data).map((arr) =>
          Math.round((arr[0] + arr[1] + arr[2] + arr[4]) * 100)
        ),
      },
    ],
  });
});
</script>

<template>
  <div id="linechart-container-ok" />
</template>

<style scoped lang="scss">
#linechart-container-ok {
  height: 300px;
}
</style>
