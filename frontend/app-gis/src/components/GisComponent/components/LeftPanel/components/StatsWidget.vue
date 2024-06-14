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
  return optionsStore.leftPanelOption == 'chart';
});
</script>

<template>
  <div v-if="show" :class="containerClass">
    <h4>Тут будет статистика</h4>
    <img
      src="https://sun9-56.userapi.com/impg/A9hjhHDaEecs5meDOEk5FnL1wHKTFQC3ZNSdkQ/f1ZskUqwzS8.jpg?size=972x2160&quality=95&sign=031dae7aa9fa7da6da72abef63221b6a&type=album"
      style="width: 18vw; height: 200px"
    />
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
}

.select-filters.open {
  left: 70px; /* Slide in */
}

.select-filters.closed {
  left: -20vw; /* Slide out */
}
</style>
