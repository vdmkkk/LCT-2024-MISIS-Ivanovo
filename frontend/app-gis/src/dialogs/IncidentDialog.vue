<script setup lang="ts">
import IncidentType from 'src/types/IncidentType';
import getIncidentsById from 'src/api/getIncidentsById';
import { ref, watch, defineProps, defineEmits, onMounted } from 'vue';

const props = defineProps<{
  modelValue: boolean;
  data?: IncidentType;
  incidentId?: number;
}>();

onMounted(() => {
  console.log(props.data, props.incidentId);
  console.log(props.modelValue, props.data);
  if (props.data) incidentData.value = props.data;
});

const emit = defineEmits(['update:modelValue']);

const setOpen = () => {
  showDialog.value = props.modelValue;
  incident.value = props.incidentId;
  if (incident.value) {
    getIncidentsById(incident.value)
      .then((res) => (incidentData.value = res))
      .catch();
  }
};

const setClose = () => {
  emit('update:modelValue', showDialog.value);
};

const showDialog = ref(false);
const incidentData = ref<IncidentType>();
const incident = ref<number>();

// payload //
const description = ref<string>();
const date_start = ref<Date>();
const date_end = ref<Date>();

watch(props, setOpen);
watch(showDialog, setClose);

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
  <q-dialog v-model="showDialog">
    <q-card style="min-width: 60vw; border-radius: 10px">
      <q-card-section style="display: flex; justify-content: space-between">
        <div class="text-h5">Инцидент</div>
        <i
          class="material-icons"
          style="font-size: 24px"
          @click="showDialog = false"
          >close</i
        >
      </q-card-section>

      <div class="incidents">
        <h2>ЦТП: {{ incidentData?.ctp_id }}</h2>
        <p>ID: {{ incidentData?.id }}</p>
        <!-- TODO: Обрезать эту хуиту до 8 знаков  -->
        <p>
          Координаты: {{ incidentData?.coordinates[0] }}
          {{ incidentData?.coordinates[1] }}
        </p>
        <h2>Затронутые объекты:</h2>
        <div
          class="handled-unoms"
          v-for="{
            unom: unom,
            hours_to_cool: hours_to_cool,
            priority_group: priority_group,
          } in incidentData?.handled_unoms"
          :key="unom"
          :style="getPriorityStyles(priority_group)"
        >
          <p>{{ unom }}</p>
          <p>Часов до остывания: {{ hours_to_cool }}</p>
          <p>Приоритет: {{ priority_group }}</p>
        </div>
        <p style="margin-top: 30px">{{ incidentData?.payload }}</p>
      </div>
    </q-card>
  </q-dialog>
</template>

<style scoped lang="scss">
.incidents {
  padding: 10px;
  padding: 16px;
  border-radius: 20px;

  .handled-unoms {
    border-radius: 20px;
    padding: 10px;
    margin-top: 10px;
  }
}
</style>
