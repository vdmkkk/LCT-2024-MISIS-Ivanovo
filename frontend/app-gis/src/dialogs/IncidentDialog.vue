<script setup lang="ts">
// @ts-nocheck //
import IncidentType from 'src/types/IncidentType';
import getIncidentsById from 'src/api/getIncidentsById';
import { ref, watch, defineProps, defineEmits, onMounted, computed } from 'vue';
import updateIncidents from 'src/api/updateIncident';
import { useQuasar } from 'quasar';
const $q = useQuasar();

const props = defineProps<{
  modelValue: boolean;
  data?: IncidentType;
  incidentId?: number | null;
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
  description.value = incidentData.value?.payload?.['description'];
  date_start.value = formatISODate(incidentData.value?.payload?.['date_start']);
  date_end.value = incidentData.value?.payload?.['date_end']
    ? formatISODate(incidentData.value?.payload?.['date_end'])
    : 'мм:чч дд:мм:гггг';
  incidentClosed.value = incidentData.value?.payload?.['date_end']
    ? true
    : false;
  console.warn(incidentClosed.value);
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
const incidentClosed = ref<boolean>();

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

function formatISODate(isoString) {
  const date = new Date(isoString);

  const pad = (num) => (num < 10 ? '0' + num : num);

  const hours = pad(date.getHours());
  const minutes = pad(date.getMinutes());
  const day = pad(date.getDate());
  const month = pad(date.getMonth() + 1); // Months are zero-based
  const year = date.getFullYear();

  return `${hours}:${minutes} ${day}-${month}-${year}`;
}

function reverseFormatDate(formattedDate) {
  // Extract the components using a regular expression
  const regex = /(\d{2}):(\d{2}) (\d{2})-(\d{2})-(\d{4})/;
  const match = formattedDate.match(regex);

  if (!match) {
    throw new Error('Invalid date format');
  }

  const [, hours, minutes, day, month, year] = match;

  // Create a Date object
  const date = new Date(Date.UTC(year, month - 1, day, hours, minutes, 0, 0));

  // Convert to ISO string
  return date.toISOString();
}

const isReadyToSave = () => {
  if (incidentData.value?.payload?.['date_end'] ? true : false) {
    if (!incidentClosed.value) return true;
    if (
      description.value !== incidentData.value?.payload.description ||
      date_start.value !==
        formatISODate(incidentData.value?.payload?.['date_start']) ||
      date_end.value !==
        formatISODate(incidentData.value?.payload?.['date_end'])
    )
      return true;
  }
  if (!incidentData.value?.payload?.['date_end'] ? true : false) {
    if (incidentClosed.value && date_end.value !== 'мм:чч дд:мм:гггг')
      return true;
    if (
      (!incidentClosed.value &&
        description.value !== incidentData.value?.payload.description) ||
      date_start.value !==
        formatISODate(incidentData.value?.payload?.['date_start'])
    )
      return true;
  }
};

const isSaveButtonDisabled = computed(() => !isReadyToSave());

const handleSave = async () => {
  const finalObj = {
    coordinates: incidentData.value?.ctp_center,
    ctp_center: incidentData.value?.ctp_center,
    ctp_id: incidentData.value?.ctp_id,
    handled_unoms: incidentData.value?.handled_unoms,
    id: incidentData.value?.id,
    payload: {
      date_end: incidentClosed.value ? reverseFormatDate(date_end.value) : '',
      date_start: reverseFormatDate(date_start.value),
      description: description.value,
    },
  };

  $q.loading.show();
  await updateIncidents(finalObj)
    .then((res) => {
      $q.loading.hide();
      showDialog.value = false;
    })
    .catch((e) => {
      console.error(e);
    });
};
</script>

<template>
  <q-dialog v-model="showDialog">
    <q-card style="min-width: 60vw; border-radius: 20px">
      <q-card-section style="display: flex; justify-content: space-between">
        <div class="text-h5">Авария #{{ incidentData.id }}</div>
        <i
          class="material-icons"
          style="font-size: 24px"
          @click="showDialog = false"
          >close</i
        >
      </q-card-section>

      <div
        style="
          display: flex;
          align-items: center;
          padding: 20px;
          margin-left: 12px;
        "
      >
        <div :style="getStatus(incidentClosed)" />
        <h3 style="margin: 0; margin-left: 20px">
          Статус: {{ incidentClosed ? 'Неактивна' : 'Активна' }}
        </h3>
      </div>

      <div class="incidents-dialog">
        <h2 v-if="incidentData?.ctp_id">ЦТП: {{ incidentData?.ctp_id }}</h2>
        <h2>ID: {{ incidentData?.id }}</h2>
        <q-input
          outlined
          v-model="description"
          label="Описание"
          style="margin-left: 16px; margin-right: 16px; font-size: 16px"
        />
        <div style="display: flex; align-items: center; margin-top: 20px">
          <h3 style="margin-top: 0px">Закрыть аварию</h3>
          <q-toggle v-model="incidentClosed" />
        </div>

        <div style="display: flex">
          <div>
            <h3>Время регистрации</h3>
            <div class="q-pa-md" style="max-width: 300px">
              <q-input filled v-model="date_start">
                <template v-slot:prepend>
                  <q-icon name="event" class="cursor-pointer">
                    <q-popup-proxy
                      cover
                      transition-show="scale"
                      transition-hide="scale"
                    >
                      <q-date v-model="date_start" mask="HH:mm DD-MM-YYYY">
                        <div class="row items-center justify-end">
                          <q-btn
                            v-close-popup
                            label="Close"
                            color="primary"
                            flat
                          />
                        </div>
                      </q-date>
                    </q-popup-proxy>
                  </q-icon>
                </template>

                <template v-slot:append>
                  <q-icon name="access_time" class="cursor-pointer">
                    <q-popup-proxy
                      cover
                      transition-show="scale"
                      transition-hide="scale"
                    >
                      <q-time
                        v-model="date_start"
                        mask="HH:mm DD-MM-YYYY"
                        format24h
                      >
                        <div class="row items-center justify-end">
                          <q-btn
                            v-close-popup
                            label="Close"
                            color="primary"
                            flat
                          />
                        </div>
                      </q-time>
                    </q-popup-proxy>
                  </q-icon>
                </template>
              </q-input>
            </div>
          </div>
          <div>
            <h3>Время закрытия</h3>
            <div class="q-pa-md" style="max-width: 300px">
              <q-input :disable="!incidentClosed" filled v-model="date_end">
                <template v-slot:prepend>
                  <q-icon name="event" class="cursor-pointer">
                    <q-popup-proxy
                      cover
                      transition-show="scale"
                      transition-hide="scale"
                    >
                      <q-date v-model="date_end" mask="HH:mm DD-MM-YYYY">
                        <div class="row items-center justify-end">
                          <q-btn
                            v-close-popup
                            label="Close"
                            color="primary"
                            flat
                          />
                        </div>
                      </q-date>
                    </q-popup-proxy>
                  </q-icon>
                </template>

                <template v-slot:append>
                  <q-icon name="access_time" class="cursor-pointer">
                    <q-popup-proxy
                      cover
                      transition-show="scale"
                      transition-hide="scale"
                    >
                      <q-time
                        v-model="date_end"
                        mask="HH:mm DD-MM-YYYY"
                        format24h
                      >
                        <div class="row items-center justify-end">
                          <q-btn
                            v-close-popup
                            label="Close"
                            color="primary"
                            flat
                          />
                        </div>
                      </q-time>
                    </q-popup-proxy>
                  </q-icon>
                </template>
              </q-input>
            </div>
          </div>
        </div>
        <h3 style="margin-bottom: 20px; margin-top: 0px; font-weight: 300">
          <strong style="font-weight: 400">Координаты:</strong>
          {{ incidentData?.coordinates[0].toString().slice(0, 8) }}
          {{ incidentData?.coordinates[1].toString().slice(0, 8) }}
        </h3>
        <h2>Затронутые объекты:</h2>
        <div
          class="handled-unoms"
          v-for="{
            unom: unom,
            hours: hours_to_cool,
            Rank: priority_group,
          } in incidentData?.handled_unoms"
          :key="unom"
          :style="getPriorityStyles(priority_group)"
        >
          <p>{{ unom }}</p>
          <p>Часов до T {{ '<' }} min: {{ hours_to_cool }}</p>
          <p>Часов до остывания трубы: {{ Math.ceil(hours_to_cool / 1.5) }}</p>
          <!-- )) -->

          <p>Приоритет: {{ priority_group }}</p>
        </div>
        <q-btn
          :class="{
            'disabled-class': isSaveButtonDisabled,
            'enabled-class': !isSaveButtonDisabled,
          }"
          :disable="isSaveButtonDisabled"
          @click="handleSave"
          >Сохранить
        </q-btn>
      </div>
    </q-card>
  </q-dialog>
</template>

<style scoped lang="scss">
.incidents-dialog {
  padding: 10px;
  padding: 16px;
  border-radius: 20px;

  .enabled-class {
    margin-top: 20px;
    border-radius: 10px;
    margin-left: 16px;
    margin-bottom: 4px;
    min-width: 200px;
    background-color: #dedede;
    transition: 0.3s ease;
  }

  .enabled-class:hover {
    background-color: #f8f8f8;
  }

  .disabled-class {
    margin-top: 20px;
    border-radius: 10px;
    margin-left: 16px;
    margin-bottom: 4px;
    min-width: 200px;
    background-color: #dedede;
    transition: 0.3s ease;
  }

  h2 {
    font-size: 32px;
    // margin-bottom:0px;
    margin-top: 0px;
    line-height: 32px;
    margin-left: 16px;
  }

  h3 {
    font-size: 24px;
    margin-bottom: 0px;
    margin-left: 16px;
    margin-top: 10px;
  }

  .handled-unoms {
    border-radius: 20px;
    padding: 10px;
    margin-top: 10px;
    margin-inline: 16px;
    padding: 20px;
    display: flex;
    justify-content: space-between;

    p {
      font-size: 16px;
      margin-bottom: 0px;
      margin-inline: 20px;
    }
  }
}
</style>
