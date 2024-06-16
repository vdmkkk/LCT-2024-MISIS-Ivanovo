<script setup lang="ts">
// @ts-nocheck // i'm so sorry
import { useOptionsStore } from 'src/stores/optionsStore';
import { toRefs, computed, onMounted, watch, ref } from 'vue';

import getBuildingByUnom from 'src/api/getBuildingByUnom';
import BuildingType from 'src/types/BuildingsType';
import NavigationMonitoringComponent from './components/NavigatorMonitoringComponent.vue';
import NavigatorIncidentsComponent from './components/NavigatorIncidentsComponent.vue';
import NavigatorPredictComponent from './components/NavigatorPredictComponent.vue';

import { RightPanelWidgets } from 'src/types/NavigationButtonsType';
import getIncidentsById from 'src/api/getIncidentsById';
import IncidentType from 'src/types/IncidentType';

const props = defineProps<{
  placeId: number | null;
}>();

const containerClass = computed(() => ({
  container: true,
  open: props.placeId || props.placeId == 0,
  closed: !props.placeId && props.placeId != 0,
  'shadow-1': true,
}));

const optionsStore = useOptionsStore();

// options to clear on exit
const loading = ref(false);
const building = ref<BuildingType>();
const incident = ref<IncidentType>();

const updateData = async () => {
  loading.value = true;
  await getBuildingByUnom(props.placeId as number)
    .then((res) => {
      building.value = res;
      loading.value = false;
    })
    .catch((e) => {
      console.error(e);
    });
};

watch(props, updateData);
</script>

<template>
  <NavigationMonitoringComponent
    :open="
      (!!props.placeId || props.placeId == 0) &&
      optionsStore.mapMode == 'monitoring'
    "
  />
  <NavigatorIncidentsComponent
    :open="
      (!!props.placeId || props.placeId == 0) &&
      optionsStore.mapMode == 'incident'
    "
  />
  <NavigatorPredictComponent
    :open="
      (!!props.placeId || props.placeId == 0) &&
      optionsStore.mapMode == 'predict'
    "
  />
  <div :class="containerClass">
    <q-inner-loading
      :showing="loading"
      label="Загрузка данных"
      label-class="text-black"
      label-style="font-size: 1.1em"
    />
    <h1>
      {{
        building?.bti_address ? building?.bti_address : building?.full_address
      }}
      <!-- разрозненные данные сука -->
    </h1>
    <h2>
      {{ building?.ctp ? 'ЦТП: ' + building?.ctp : '' }}
    </h2>
    <h2>
      {{
        building?.municipal_district
          ? 'Район: ' + building?.municipal_district
          : ''
      }}
    </h2>
    <q-separator color="red" />
    <component
      :is="RightPanelWidgets[optionsStore.rightPanelOption]"
      v-bind="{ object: building }"
    ></component>
  </div>
</template>

<style scoped lang="scss">
.container {
  position: absolute;
  height: 95vh;
  top: 2.5vh;
  width: 500px;
  right: 1vw;
  background-color: white;
  transition: right 0.3s ease-in-out; /* Smooth transition */

  border-radius: 30px;
  padding: 30px;
  h1 {
    font-size: 1.7em;
    font-weight: 500;
    line-height: normal;
  }

  h2 {
    font-size: 1.2em;
    font-weight: 300;
    line-height: normal;
    color: #666;
  }
}

.container.open {
  right: 1vw; /* Slide in */
}

.container.closed {
  right: -500px; /* Slide out */
}
</style>
