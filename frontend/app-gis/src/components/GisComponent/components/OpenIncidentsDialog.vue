<script setup lang="ts">
import { computed, ref, watch } from 'vue';
const props = defineProps<{
  incidentId: number | null;
  modelValue: boolean;
}>();

const containerClass = computed(() => ({
  container: true,
  open: props.incidentId || props.incidentId == 0,
  closed: !props.incidentId && props.incidentId != 0,
  'shadow-1': true,
}));

const showIncidentDialogRef = ref<boolean>(false);

const handleClick = () => {
  showIncidentDialogRef.value = !showIncidentDialogRef.value;
};

const emit = defineEmits(['update:modelValue']);

const handleEmit = () => {
  emit('update:modelValue', true);
};

watch(showIncidentDialogRef, handleEmit); // i don't even know, is this a good practice lol
</script>

<template>
  <q-btn :class="containerClass" @click="handleClick">ОТКРЫТЬ ИНЦИДЕНТ</q-btn>
</template>

<style scoped lang="scss">
.container {
  position: absolute;
  bottom: 2vh;
  width: 16vw;
  left: 42vw;
  height: 60px;
  background-color: white;
  transition: bottom 0.2s ease-in-out; /* Smooth transition */

  border-radius: 30px;
}

.container.open {
  bottom: 2vh; /* Slide in */
}

.container.closed {
  bottom: -60px; /* Slide out */
}
</style>
