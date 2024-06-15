<script setup lang="ts">
import { onMounted, ref } from 'vue';
import LineChartAllEvents from './components/LineChartAllEvents.vue';
import LineChartOnlyOk from './components/LineChartOnlyOk.vue';
import getIncidentsByUnom from 'src/api/getIncidentsForUnom';
import IncidentDialog from 'src/dialogs/IncidentDialog.vue';

const props = defineProps<{
  object: Map<string, any>;
}>();

const data = ref();
onMounted(() => {
  // @ts-ignore //
  getIncidentsByUnom(props.object['unom']).then((res) => {
    console.log(res);
    data.value = res;
  });
});

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
</script>

<template>
  <div class="incidents-container">
    <h1>Предсказания</h1>
    <div
      class="incidents"
      v-for="{
        coordinates: coordinates,
        ctp_id: ctp_id,
        handled_unoms: handled_unoms,
        id: id,
        payload: payload,
      } in data"
      :key="id"
    >
      <q-btn label="Open Dialog" @click="showDialog = true" color="primary" />
      <div>
        <div style="display: flex;">
          <div style="width: 50%;">
            <h2 style="font-weight: 400;">ЦТП:</h2>
          </div>
          <div style="width: 50%;">
            <h2>{{ ctp_id }}</h2>
          </div>
        </div>
        
        <div style="display: flex;">
          <div style="width: 50%;">
            <h2 style="font-weight: 400;">ID:</h2>
          </div>
          <div style="width: 50%;">
            <h2> {{ id }}</h2>
          </div>
        </div>
          
        <div style="display: flex;">
          <div style="width: 50%;">
            <h2 style="font-weight: 400;">Координаты: </h2>
          </div>
          <div style="width: 50%;">
            <h2> {{ coordinates[0] }} {{ coordinates[1] }}</h2>
          </div>
        </div>
          <!-- TODO: ховер должен менять цвет чтобы было понятно что можно НАЖАТЬ -->
          <!-- TODO: Обрезать эту хуиту до 8 знаков  -->
      </div>
      <h2 style="font-weight: 400;">Затронутые объекты:</h2>
      <div
        class="handled-unoms"
        v-for="{
          unom: unom,
          hours_to_cool: hours_to_cool,
          priority_group: priority_group,
        } in handled_unoms"
        :key="unom"
        :style="getPriorityStyles(priority_group)"
      >
        <p>{{ unom }}</p>
        <p>Часов до остывания: {{ hours_to_cool }}</p>
        <p>Приоритет: {{ priority_group }}</p>
      </div>
      <p style="margin-top: 30px">{{ payload }}</p>
      <IncidentDialog
        v-model="showDialog"
        :data="{
          coordinates: coordinates,
          ctp_id: ctp_id,
          handled_unoms: handled_unoms,
          id: id,
          payload: payload,
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
    margin-top: 10px;
    line-height: 40px;
  }

  .incidents {
    background-color: #f8f8f8;
    padding: 10px;
    padding: 16px;
    border-radius: 20px;

    .handled-unoms {
      border-radius: 20px;
      padding: 20px;
      padding-bottom: 8px;
      margin-top: 10px;
      display: flex;
      justify-content: space-between;
      
      p {
        font-size: 16px;
        line-height: 16px;
      }
    }
  }
}
</style>
