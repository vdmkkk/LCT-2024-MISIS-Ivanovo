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
  if (props.object?.['unom'])
    // @ts-ignore //
    getDynamicDataForUnom(props.object['unom']).then((res) => {
      console.log(res);
      data.value = res['odpu_plot'];
    });
});
</script>

<template>
  <div
    v-if="
      !!data
        ? Object.keys(
            Object.values({
              predict: {},
              incidents_count: {},
              odpu_plot: {},
            })[0]
          ).length > 0
        : !!data
    "
    class="report-container"
  >
    <h1>Сводка</h1>
    <div v-for="[key, data] in Object.entries(data)" :key="key">
      <div>
        <div style="display: flex; align-items: baseline">
          <div style="width: 15%">
            <i class="material-symbols-outlined">{{ list[key].logo }}</i>
          </div>
          <div style="width: 55%">
            <div style="display: flex; align-items: baseline">
              <h2 style="width: 95%">{{ list[key].title }}:</h2>
            </div>
          </div>
          <div style="width: 30%">
            <h3 v-if="data">
              {{
                Object.entries(data).toSorted((a, b) => {
                  const dateA = new Date(a[0].split('.').reverse().join('-'));
                  const dateB = new Date(b[0].split('.').reverse().join('-'));
                  return dateB - dateA;
                })?.[0]?.[1]
              }}
            </h3>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="report-container" v-else>
    <h1>Сводка</h1>
    <h2>Данных нет</h2>
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
    line-height: 1.4em;
  }

  h3 {
    font-size: 1.3em;
  }

  .material-symbols-outlined {
    font-size: 32px;
  }
}
</style>
