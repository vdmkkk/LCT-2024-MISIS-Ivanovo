<script setup lang="ts">
import { ref, defineEmits, computed, watch, onMounted } from 'vue';
import { useOptionsStore } from 'src/stores/optionsStore';

const optionsStore = useOptionsStore();
const props = defineProps<{
  modelValue: number;
}>();

const emits = defineEmits(['update:modelValue']);

const mode = ref();

onMounted(() => {
  mode.value = props.modelValue;
});

const changeMode = () => {
  console.log(mode.value);
  emits('update:modelValue', mode.value);
};

watch(mode, changeMode);

const containerClass = computed(() => ({
  container: true,
  open: optionsStore.mapMode == 'predict',
  closed: optionsStore.mapMode != 'predict',
  'shadow-1': true,
}));
</script>

<template>
  <div :class="containerClass">
    <q-btn-toggle
      v-model="mode"
      toggle-color="red-10"
      style="height: 70px; border-radius: 30px"
      :options="[
        { label: 'T < min', value: 0 },
        { label: 'T > max', value: 1 },
        { label: 'Давление не в норме', value: 2 },
        { label: 'Утечка', value: 4 },
        { label: 'Произойдет авария', value: 5 },
      ]"
    />
  </div>
</template>

<style scoped lang="scss">
.container {
  position: absolute;
  top: 2vh;
  //   width: 16vw;
  //   left: 42vw;
  height: 70px;
  background-color: white;
  transition: top 0.2s ease-in-out; /* Smooth transition */

  border-radius: 30px;
}

.container.open {
  top: 2vh; /* Slide in */
}

.container.closed {
  top: -70px; /* Slide out */
}
</style>
