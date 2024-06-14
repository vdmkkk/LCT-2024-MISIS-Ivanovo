// src/stores/optionStore.ts
import { defineStore } from 'pinia';
import { ref } from 'vue';
import { NavigationButtonType } from 'src/types/NavigationButtonsType';

export const useOptionsStore = defineStore('optionsStore', () => {
  const leftPanelOption = ref<string | null>(null);

  const setLeftPanelOption = (option: string | null) => {
    leftPanelOption.value = leftPanelOption.value == option ? null : option;
  };

  const rightPanelOption = ref<NavigationButtonType['type']>('passport');

  const setRightPanelOption = (option: NavigationButtonType['type']) => {
    rightPanelOption.value = option;
  };

  const mapMode = ref<'monitoring' | 'incident' | 'predict'>('monitoring');

  const setMapMode = (option: 'monitoring' | 'incident' | 'predict') => {
    mapMode.value = option;
  };

  const resetMapMode = () => {
    mapMode.value = 'monitoring';
  };

  const filters = ref<Map<string, string | null>>(
    new Map([
      ['district', null],
      ['web', null],
      ['consumer', null],
    ])
  );

  const setFilters = (val: Map<string, string | null>) => {
    filters.value = val; // я не хочу писать сеттеры под каждый опшн.
  };

  return {
    leftPanelOption,
    setLeftPanelOption,
    mapMode,
    setMapMode,
    resetMapMode,
    filters,
    setFilters,
    rightPanelOption,
    setRightPanelOption,
  };
});
