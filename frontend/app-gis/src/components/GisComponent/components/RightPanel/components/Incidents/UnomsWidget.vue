<script setup lang="ts">
import { onMounted, ref } from 'vue';
import IncidentDialog from 'src/dialogs/IncidentDialog.vue';
import IncidentType from 'src/types/IncidentType';

const props = defineProps<{
  object: IncidentType;
}>();

console.log(props.object);

const showDialog = ref(false);

const getPriorityStyles = (priority_group: number) => {
  switch (priority_group) {
    case 1:
      return { backgroundColor: '#ff7777', color: 'black' };
    case 2:
      return { backgroundColor: '#ffeb78', color: 'black' };
    case 3:
      return { backgroundColor: '#a7ff78', color: 'black' };
    default:
      return { backgroundColor: '#6dceea', color: 'black' };
  }
};
</script>

<template>
  <div class="incidents-container">
    <h2>Затронутые объекты:</h2>
    <div
      class="handled-unoms"
      v-for="{
        unom: unom,
        hours_to_cool: hours_to_cool,
        priority_group: priority_group,
      } in props.object.handled_unoms"
      :key="unom"
      :style="getPriorityStyles(priority_group)"
    >
      <p>{{ unom }}</p>
      <p>Часов до остывания: {{ hours_to_cool }}</p>
      <p>Приоритет: {{ priority_group }}</p>
    </div>
    <IncidentDialog
      v-model="showDialog"
      :data="{
        coordinates: props.object.coordinates,
        ctp_id: props.object.ctp_id,
        handled_unoms: props.object.handled_unoms,
        id: props.object.id,
        payload: props.object.payload,
      }"
    />
  </div>
</template>

<style scoped lang="scss">
.incidents-container {
  max-height: 75vh;
  overflow-y: auto;
  h1 {
    font-size: 1.9em;
    font-weight: 500;
    margin-top: 0px;
  }

  h2 {
    font-size: 1.4em;
    margin-top: 0px;
  }

  .incidents {
    background-color: #f8f8f8;
    padding: 10px;
    padding: 16px;
    border-radius: 20px;

    .handled-unoms {
      border-radius: 20px;
      padding: 10px;
      margin-top: 10px;
    }
  }
}
</style>
