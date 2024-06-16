// src/stores/optionStore.ts
import { defineStore } from 'pinia';
import { ref } from 'vue';
import {
  NavigationMonitoringButtonType,
  NavigationIncidentsButtonType,
} from 'src/types/NavigationButtonsType';

export const useOptionsStore = defineStore('optionsStore', () => {
  const mapMode = ref<'monitoring' | 'incident' | 'predict'>('monitoring');

  const setMapMode = (option: 'monitoring' | 'incident' | 'predict') => {
    mapMode.value = option;
  };

  const leftPanelOption = ref<string | null>(null);

  const setLeftPanelOption = (option: string | null) => {
    leftPanelOption.value = leftPanelOption.value == option ? null : option;
  };

  const rightPanelOption = ref<
    | NavigationMonitoringButtonType['type']
    | NavigationIncidentsButtonType['type']
  >(mapMode.value == 'incident' ? 'incident' : 'passport');

  const setRightPanelOption = (
    option:
      | NavigationMonitoringButtonType['type']
      | NavigationIncidentsButtonType['type']
  ) => {
    rightPanelOption.value = option;
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
