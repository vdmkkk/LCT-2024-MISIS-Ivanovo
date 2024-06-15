<template>
  <q-page class="row items-center justify-evenly main-container">
    <GisComponent />
  </q-page>
</template>

<style scoped lang="scss">
.main-container {
  overflow-y: hidden;
  overflow-x: hidden;
}
</style>

<script setup lang="ts">
import GisComponent from 'components/GisComponent/GisComponent.vue';
</script>
