<script setup lang="ts">
// @ts-nocheck // i'm so sorry
import getDynamicDataForUnom from 'src/api/getDynamicDataForUnom';
import { onMounted, ref } from 'vue';

const props = defineProps<{
  object: Map<string, any>;
}>();

const list = {
  difference_supply_return_leak_all: {
    title: 'Разница между подачей и возвратом (Утечка)',
    logo: 'water_pump',
  },
  difference_supply_return_mix_all: {
    title: 'Разница между подачей и возвратом (Подмес)',
    logo: 'water_heater',
  },
  q2: {
    title: 'Расход тепловой энергии',
    logo: 'airwave',
  },
  temperature_return_all: {
    title: 'Температура возврата',
    logo: 'thermostat',
  },
  temperature_supply_all: {
    title: 'Температура подачи',
    logo: 'thermometer_loss',
  },
  volume1: {
    title: 'Объём поданого теплоносителя в систему ЦО',
    logo: 'onsen',
  },
  volume2: {
    title: 'Объём обратного теплоносителя из системы ЦО',
    logo: 'water',
  },
};

const data = ref();
onMounted(() => {
  // @ts-ignore //
  getDynamicDataForUnom(props.object['unom']).then((res) => {
    console.log(res);
    data.value = res['odpu_plot'];
  });
});
</script>

<template>
  <div v-if="data" class="report-container">
    <h1>Сводка</h1>
    <div v-for="[key, data] in Object.entries(data)" :key="key">
      {{
        console.log(
          Object.entries(data).toSorted((a, b) => {
            const dateA = new Date(a[0].split('.').reverse().join('-'));
            const dateB = new Date(b[0].split('.').reverse().join('-'));
            return dateB - dateA;
          })
        )
      }}
      <i class="material-icons">{{ list[key].logo }}</i>
      <h2>{{ list[key].title }}</h2>
      :
      <h3>
        {{
          Object.entries(data).toSorted((a, b) => {
            const dateA = new Date(a[0].split('.').reverse().join('-'));
            const dateB = new Date(b[0].split('.').reverse().join('-'));
            return dateB - dateA;
          })[0][1]
        }}
      </h3>
    </div>
  </div>
</template>

<style scoped lang="scss">
.report-container {
  max-height: 80vh;
  overflow-y: auto;
  h1 {
    font-size: 1.9em;
    font-weight: 500;
    margin-top: 0px;
  }

  h2 {
    font-size: 1.4em;
  }

  h3 {
    font-size: 1.3em;
  }
}
</style>
