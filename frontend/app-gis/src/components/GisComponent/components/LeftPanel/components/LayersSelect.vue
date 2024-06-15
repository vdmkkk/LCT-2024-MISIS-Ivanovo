<script setup lang="ts">
import { computed } from 'vue';
import { useOptionsStore } from 'src/stores/optionsStore';

const optionsStore = useOptionsStore();

const show = computed(() => {
  return optionsStore.leftPanelOption == 'layers';
});

type MapMode = 'monitoring' | 'incident' | 'predict';

const options: { key: MapMode; value: string }[] = [
  { key: 'monitoring', value: 'Режим мониторинга' },
  { key: 'incident', value: 'Аварийный режим' },
  { key: 'predict', value: 'Режим предсказаний' },
];

const selectOption = (val: MapMode) => {
  optionsStore.setMapMode(val);
  optionsStore.setLeftPanelOption(null);
  switch (true) {
    case val == 'incident':
      optionsStore.setRightPanelOption('incident');
    default:
      optionsStore.setRightPanelOption('passport');
  }
};
</script>

<template>
  <div v-if="show" class="select-layers">
    <q-menu
      no-parent-event
      :model-value="true"
      anchor="top right"
      self="top left"
      class="select"
      transition-show="jump-down"
      transition-hide="jump-up"
      ><q-list>
        <q-item
          v-for="option in options"
          :key="option.value"
          clickable
          :active="optionsStore.mapMode == option.key"
          @click="selectOption(option.key)"
        >
          <q-item-section>{{ option.value }}</q-item-section>
        </q-item>
      </q-list></q-menu
    >
  </div>
</template>

<style lang="scss">
.select-layers {
  position: absolute;
  background-color: white;
  top: 310px;
  left: 10px;
  z-index: 999;
}
</style>
