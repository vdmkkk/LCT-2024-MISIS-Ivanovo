<script setup lang="ts">
import { onMounted, ref } from 'vue';
import IncidentDialog from 'src/dialogs/IncidentDialog.vue';
import IncidentType from 'src/types/IncidentType';

const props = defineProps<{
  object: IncidentType;
}>();

const showDialog = ref(false);

const handleOpenDialog = () => {
  console.log('bruh');
  showDialog.value = true;
};
</script>

<template>
  <h1>Статистика</h1>
</template>
