<script setup lang="ts">
import { computed } from 'vue';
import { useOptionsStore } from 'src/stores/optionsStore';
import { useNavigation } from 'src/composables/useNavigation';
import { getCurrentService } from 'src/utils/getCurrentService';

const optionsStore = useOptionsStore();
const navigate = useNavigation();
const currentService = getCurrentService();

const show = computed(() => {
  return optionsStore.leftPanelOption == 'location';
});

const options = [
  { key: 'gis', value: 'Карта', port: 8080 },
  { key: 'service-desk', value: 'Панель управления', port: 8081 },
];

const selectOption = (val: string, port: number) => {
  if (currentService != val)
    navigate.navigateTo(`http://${val}.misis-ivanovo.loc:${port}/#/`);
};
</script>

<template>
  <div v-if="show" class="select-service">
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
          :active="currentService == option.key"
          @click="selectOption(option.key, option.port)"
        >
          <q-item-section>{{ option.value }}</q-item-section>
        </q-item>
      </q-list></q-menu
    >
  </div>
</template>

<style lang="scss">
.select-service {
  position: absolute;
  background-color: white;
  top: 130px;
  left: 70px;
  z-index: 999;
}
</style>
