<script setup lang="ts">
import { onMounted, ref } from 'vue';
import IncidentDialog from 'src/dialogs/IncidentDialog.vue';
import IncidentType from 'src/types/IncidentType';

const props = defineProps<{
  object: IncidentType;
}>();

const getPriorityStyles = (priority_group: number) => {
  switch (priority_group) {
    case 1:
      return { backgroundColor: '#ff7777', color: 'black' };
    case 2:
      return { backgroundColor: '#ffeb78', color: 'black' };
    case 3:
      return { backgroundColor: '#a7ff78', color: 'black' };
    default:
      return {};
  }
};

const showDialog = ref(false);

const handleOpenDialog = () => {
  console.log('bruh');
  showDialog.value = true;
};
</script>

<template>
  <div class="incidents-container">
    <h1>Краткая информация</h1>
    <div class="incidents" @click="handleOpenDialog">
      <h2>ЦТП: {{ props.object?.ctp_id }}</h2>
      <p>ID: {{ props.object?.id }}</p>
      <!-- TODO: ховер должен менять цвет чтобы было понятно что можно НАЖАТЬ -->
      <!-- TODO: Обрезать эту хуиту до 8 знаков  -->
      <p>
        Координаты: {{ props.object?.coordinates[0] }}
        {{ props.object?.coordinates[1] }}
      </p>

      <p style="margin-top: 30px">{{ props.object?.payload }}</p>
      <IncidentDialog
        v-model="showDialog"
        :data="{
          coordinates: props.object?.coordinates,
          ctp_id: props.object?.ctp_id,
          handled_unoms: props.object?.handled_unoms,
          id: props.object?.id,
          payload: props.object?.payload,
        }"
      />
    </div>
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
