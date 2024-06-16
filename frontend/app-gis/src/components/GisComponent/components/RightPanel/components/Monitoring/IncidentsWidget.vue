<script setup lang="ts">
import { onMounted, ref } from 'vue';

import getIncidentsByUnom from 'src/api/getIncidentsForUnom';
import IncidentDialog from 'src/dialogs/IncidentDialog.vue';

const props = defineProps<{
  object: Map<string, any>;
}>();

const data = ref();
onMounted(() => {
  // @ts-ignore //
  if (props.object?.['unom'])
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

const getStatus = (date_end: string | null) => {
  if (date_end)
    return {
      backgroundColor: '#f00',
      borderRadius: '50%',
      width: '20px',
      height: '20px',
    };
  else
    return {
      backgroundColor: '#0f0',
      borderRadius: '50%',
      width: '20px',
      height: '20px',
    };
};

const showDialog = ref(false);

const handleOpenDialog = () => {
  console.log('bruh');
  showDialog.value = true;
};

const formatDate = (date: string | null): string => {
  if (!date) return '';
  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  };
  return new Date(date).toLocaleString('ru-RU', options);
};

</script>

<template>
  <div class="incidents-container">
    <h1>Аварии</h1>
    <h2 v-if="!data">История инцидентов пуста</h2>
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
      @click="handleOpenDialog"
    >
      <div>
        <div style="display: flex; align-items: center">
          <div :style="getStatus(payload.date_end)" />
          <h3 style="margin: 0; margin-left: 10px; font-size: 32px; font-weight: 500;">
            Статус: {{ payload.date_end ? 'Неакивна' : 'Активна' }}
          </h3>
        </div>

        <div v-if="ctp_id" style="display: flex">
          <div style="width: 50%">
            <h2 style="font-weight: 400">ЦТП:</h2>
          </div>
          <div style="width: 50%">
            <h2>{{ ctp_id }}</h2>
          </div>
        </div>

        <div style="display: flex">
          <div style="width: 50%">
            <h2 style="font-weight: 400">ID:</h2>
          </div>
          <div style="width: 50%">
            <h2>{{ id }}</h2>
          </div>
        </div>

        <div style="display: flex">
          <div style="width: 50%">
            <h2 style="font-weight: 400">Описание:</h2>
          </div>
          <div style="width: 50%">
            <h2>{{ payload.description }}</h2>
          </div>
        </div>

        <div style="display: flex">
          <div style="width: 50%">
            <h2 style="font-weight: 400">Дата регистрации:</h2>
          </div>
          <div style="width: 50%">
            <h2>{{ formatDate(payload.date_start) }}</h2>
          </div>
        </div>

        <div  style="display: flex">
          <div style="width: 50%">
            <h2 style="font-weight: 400">Дата закрытия:</h2>
          </div>
          <div style="width: 50%">
            <h2>{{ payload.date_end? formatDate(payload.date_end) : '-' }}</h2>
          </div>
        </div>

        <div style="display: flex">
          <div style="width: 50%">
            <h2 style="font-weight: 400">Координаты:</h2>
          </div>
          <div style="width: 50%">
            <h2>{{ coordinates[0].toString().slice(0, 8) }} {{ coordinates[1].toString().slice(0, 8) }}</h2>
          </div>
        </div>
      </div>
      <h2 style="font-weight: 500; margin-top: 20px;">Затронутые объекты:</h2>
      <div
        class="handled-unoms"
        v-for="{
          unom: unom,
          hours: hours_to_cool,
          Rank: priority_group,
        } in handled_unoms"
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
  overflow-y:visible;
  h1 {
    font-size: 1.9em;
    font-weight: 500;
    margin-top: 0px;
  }

  h2 {
    font-size: 1.4em;
    margin-top: 10px;
    margin-bottom: 10px;
    line-height: 40px;
  }

  .incidents {
    background-color: #f8f8f8;
    padding: 10px;
    padding: 16px;
    border-radius: 20px;
    box-shadow: 4px 4px 15px rgba(0,0,0,.1);
    transition: .3s ease;
    cursor: pointer;

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

  .incidents:hover {
    box-shadow: 4px 4px 25px rgba(0,0,0,.3);
    background-color: #eeeeee;
  }
}
</style>
