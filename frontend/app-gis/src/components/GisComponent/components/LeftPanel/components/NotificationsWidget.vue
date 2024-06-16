<script setup lang="ts">
import { computed, ref } from 'vue';
import { useOptionsStore } from 'src/stores/optionsStore';

const optionsStore = useOptionsStore();

const containerClass = computed(() => ({
  'select-notifications': true,
  open: show.value,
  closed: !show.value,
}));

const show = computed(() => {
  return optionsStore.leftPanelOption == 'notifications';
});
</script>

<template>
  <div v-if="show" :class="containerClass">
    <h5>Уведомления</h5>
    <q-separator />
    <h6 @click="() => (optionsStore.mapMode = 'incident')">
      По адресу: Новокосино, ул. Николая Старостина, д. 11 произошла авария!
    </h6>
    <q-separator />
    <h6 @click="() => (optionsStore.mapMode = 'incident')">
      По адресу: Новокосино, ул. Николая Старостина, д. 11 произошла авария!
    </h6>
  </div>
</template>

<style scoped lang="scss">
.select-notifications {
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

  h5,
  h6 {
    margin: 0;
    margin-top: 10px;
    margin-bottom: 10px;
    font-weight: 500;
  }

  h6 {
    font-size: 1.1em;
    font-weight: 400;
    cursor: pointer;
  }
}

.select-notifications.open {
  left: 70px; /* Slide in */
}

.select-notifications.closed {
  left: -20vw; /* Slide out */
}
</style>
