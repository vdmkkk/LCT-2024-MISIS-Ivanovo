<script setup lang="ts">
// @ts-nocheck //
import { ref, computed, defineEmits, watch } from 'vue';
import { QSlider } from 'quasar';
import { format } from 'date-fns';
import { useOptionsStore } from 'src/stores/optionsStore';

const optionsStore = useOptionsStore();
const props = defineProps<{
  modelValue: string;
}>();

// Define the starting point and the range
const startDate = new Date('2024-04-01T00:00:00');
const daysRange = 14;

// Generate date positions
const datePositions = Array.from({ length: daysRange }, (_, i) => {
  const date = new Date(startDate);
  date.setDate(startDate.getDate() + i);
  return date;
});

// Reactive value for the slider
const sliderValue = ref(0);

// Computed property for the formatted date
const formattedDate = computed(() => {
  const date = datePositions[sliderValue.value];
  return format(date, 'dd-MM-yyyy');
});

const rawDate = computed(() => {
  return datePositions[sliderValue.value];
});

const emits = defineEmits(['update:modelValue']);

// Method to update the date label
const updateDate = (value: number) => {
  sliderValue.value = value;
};

const emitData = () => {
  emits(
    'update:modelValue',
    rawDate.value.toISOString().split('T')[0] + 'T00:00:00'
  );
};

watch(formattedDate, emitData);

const containerClass = computed(() => ({
  'timeline-container': true,
  open: optionsStore.mapMode == 'predict',
  closed: optionsStore.mapMode != 'predict',
  'shadow-1': true,
}));
</script>

<template>
  <div :class="containerClass">
    <q-slider
      v-model="sliderValue"
      :min="0"
      :max="datePositions.length - 1"
      markers
      color="red-10"
      label
      label-always
      :label-value="formattedDate"
      @input="updateDate"
    >
      <template v-slot:marker-label>
        <div class="date-label">{{ formattedDate }}</div>
      </template>
    </q-slider>
  </div>
</template>

<style scoped lang="scss">
.timeline-container {
  width: 60vw;
  padding: 20px;
  position: absolute;
  bottom: 2.5vh;
  background-color: white;
  border-radius: 30px;
  transition: bottom 0.2s ease-in-out; /* Smooth transition */
}

.timeline-container.open {
  bottom: 2.5vh; /* Slide in */
}

.timeline-container.closed {
  bottom: -100px; /* Slide out */
}

.date-label {
  margin-top: 10px;
  text-align: center;
  font-size: 14px;
}
</style>
