<template>
  <q-dialog v-model="showDialog">
    <q-card>
      <q-card-section>
        <div class="text-h6">Dialog Title</div>
      </q-card-section>

      <q-card-section>
        <p>Unom: {{ data.unom }}</p>
        <p>Hours to Cool: {{ data.hours_to_cool }}</p>
        <p>Priority Group: {{ data.priority_group }}</p>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn
          flat
          label="Cancel"
          color="primary"
          @click="showDialog = false"
        />
        <q-btn flat label="OK" color="primary" @click="handleOk" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref, watch, defineProps, defineEmits } from 'vue';

const props = defineProps({
  modelValue: Boolean,
  data: Object,
});

const emit = defineEmits(['update:modelValue']);

const showDialog = ref(props.modelValue);

watch(showDialog, (newValue) => {
  emit('update:modelValue', newValue);
});

const handleOk = () => {
  // Handle the OK button click
  showDialog.value = false;
};
</script>

<style scoped>
/* Add any additional styles if needed */
</style>
