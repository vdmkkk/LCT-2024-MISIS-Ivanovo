<script setup lang="ts">
// @ts-nocheck //
import IncidentType from 'src/types/IncidentType';
import getIncidentsById from 'src/api/getIncidentsById';
import { ref, watch, defineProps, defineEmits, onMounted, computed } from 'vue';
import createIncident from 'src/api/createIncident';
import { useQuasar } from 'quasar';
const $q = useQuasar();

const props = defineProps<{
  modelValue: boolean;
}>();

onMounted(() => {
  console.log(props.data, props.incidentId);
  console.log(props.modelValue, props.data);
  if (props.data) incidentData.value = props.data;
});

const emit = defineEmits(['update:modelValue']);

const setClose = () => {
  emit('update:modelValue', showDialog.value);
};

const showDialog = ref(false);

// payload //
const description = ref<string>();
const date_start = ref<Date>('мм:чч дд:мм:гггг');
const some_id = ref<string>();
const incidentMode = ref<'unom' | 'ctp'>('ctp');

const setOpen = () => {
  showDialog.value = props.modelValue;
};

watch(props, setOpen);
watch(showDialog, setClose);

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
  return (
    some_id.value !== '' &&
    description.value !== '' &&
    date_start.value !== 'мм:чч дд:мм:гггг' &&
    some_id.value
  );
};

const isSaveButtonDisabled = computed(() => !isReadyToSave());

const handleSave = async () => {
  const finalObj = {
    ctp_id: incidentMode.value == 'ctp' ? some_id.value : null,
    payload: {
      date_end: '',
      date_start: reverseFormatDate(date_start.value),
      description: description.value,
    },
    unom: incidentMode.value == 'unom' ? parseInt(some_id.value) : null,
  };

  $q.loading.show();
  await createIncident(finalObj)
    .then((res) => {
      $q.loading.hide();
      showDialog.value = false;
    })
    .catch((e) => {
      console.error(e);
      $q.loading.hide();
    });
};
</script>

<template>
  <q-dialog v-model="showDialog">
    <q-card style="min-width: 40vw; border-radius: 20px">
      <q-card-section style="display: flex; justify-content: space-between">
        <div class="text-h5">Добавить аварию</div>
        <i
          class="material-icons"
          style="font-size: 24px"
          @click="showDialog = false"
          >close</i
        >
      </q-card-section>

      <div class="incidents-dialog">
        <q-btn-toggle
          v-model="incidentMode"
          toggle-color="red-10"
          :options="[
            { label: 'Авария на цтп', value: 'ctp' },
            { label: 'Авария на объекте', value: 'unom' },
          ]"
        />
        <q-input
          filled
          v-model="some_id"
          :label="incidentMode == 'ctp' ? 'ЦТП ID' : 'УНОМ'"
          style="
            margin-left: 16px;
            margin-right: 16px;
            margin-top: 20px;
            size: 16px;
          "
        />
        <q-input
          outlined
          v-model="description"
          label="Описание"
          style="
            margin-left: 16px;
            margin-right: 16px;
            margin-top: 20px;
            size: 16px;
          "
        />

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
        </div>
        <q-btn
          :class="{
            'disabled-class': isSaveButtonDisabled,
            'enabled-class': !isSaveButtonDisabled,
          }"
          :disable="isSaveButtonDisabled"
          @click="handleSave"
          >Добавить
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
      font-size: 20px;
      margin-bottom: 0px;
      margin-inline: 20px;
    }
  }
}
</style>
