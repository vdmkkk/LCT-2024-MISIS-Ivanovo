<script setup lang="ts">
import { computed, ref } from 'vue';
import { useOptionsStore } from 'src/stores/optionsStore';
import { useNavigation } from 'src/composables/useNavigation';
import { getCurrentService } from 'src/utils/getCurrentService';

const optionsStore = useOptionsStore();

const containerClass = computed(() => ({
  'select-filters': true,
  open: show.value,
  closed: !show.value,
}));

const show = computed(() => {
  return optionsStore.leftPanelOption == 'filter';
});
const district = ref<string | null | undefined>(
  optionsStore.filters.get('district')
);
const districtOptions = ['Район', 'Подключение к ТЭЦ'];
const web = ref(optionsStore.filters.get('web'));
const webOptions = [
  'Магистральная сеть',
  'Распределительная сеть',
  'Потребители с ИТП',
];
const consumer = ref(optionsStore.filters.get('consumer'));
const consumerOptions = ['Социальный', 'Промышленный', 'МКД'];

const handleClose = () => {
  optionsStore.setLeftPanelOption(null);
};

const handleFilterChange = () => {
  if (
    district.value !== undefined &&
    web.value !== undefined &&
    consumer.value !== undefined
  )
    optionsStore.setFilters(
      new Map([
        ['district', district.value],
        ['web', web.value],
        ['consumer', consumer.value],
      ])
    );
};

const clearAll = () => {
  district.value = null;
  web.value = null;
  consumer.value = null;
};
</script>

<template>
  <div v-if="show" :class="containerClass">
    <div
      style="
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        margin-bottom: 16px;
      "
    >
      <p>Фильтр</p>
      <i @click="handleClose" class="material-icons">close</i>
    </div>
    <br />
    <q-select
      clearable
      outlined
      v-model="district"
      :options="districtOptions"
      label="Район"
      @update:model-value="handleFilterChange"
    />
    <br />
    <br />
    <q-select
      clearable
      outlined
      v-model="web"
      :options="webOptions"
      label="Тепловая сеть"
      @update:model-value="handleFilterChange"
    />
    <br />
    <br />
    <q-select
      clearable
      outlined
      v-model="consumer"
      :options="consumerOptions"
      label="Потребитель"
      @update:model-value="handleFilterChange"
    />
    <br />
    <br />
    <q-btn color="deep-orange" label="Очистить все" @click="clearAll" />
  </div>
</template>

<style lang="scss">
.select-filters {
  position: absolute;
  background-color: white;
  top: 100px;
  width: 20vw;
  padding: 14px;
  z-index: 999;
  border-radius: 20px;
  padding-bottom: 20px;
  display: flex;
  flex-direction: column;
  transition: left 3s ease-in-out; /* Smooth transition */

  p {
    font-size: 24px;
    margin-bottom: 0px;
  }

  .q-btn {
    margin-left: auto;
    margin-right: auto;
  }

  .material-icons {
    font-size: 18px;
  }
}

.select-filters.open {
  left: 70px; /* Slide in */
}

.select-filters.closed {
  left: -20vw; /* Slide out */
}
</style>
