<script setup lang="ts">
import { computed } from 'vue';
import { useOptionsStore } from 'src/stores/optionsStore';

const optionsStore = useOptionsStore();

const props = defineProps<{
  incidentId?: number | null;
  incidentMode: number | null;
}>();

const containerClass = computed(() => ({
  'legend-container': true,
  'open-predicts': optionsStore.mapMode == 'predict',
  'open-incidents':
    optionsStore.mapMode == 'incident' &&
    (props.incidentId || props.incidentId == 0),
  closed:
    optionsStore.mapMode != 'predict' &&
    !(
      optionsStore.mapMode == 'incident' &&
      (props.incidentId || props.incidentId == 0)
    ),
  'shadow-1': true,
}));

const src = computed(() => getPic());

const getPic = () => {
  if (optionsStore.mapMode == 'predict')
    return 'https://psv4.userapi.com/c235131/u346561169/docs/d3/313c92459362/legend_predict.png?extra=Ks_SDwFqoD0cwoXGZ4_gbEL5_RRzQdvLq-oEUXVyEJMPwQiFL56qsWY7w7tJ6KqmEsLdgSWNeCMZkZLBlbH03FswCT2a40XdER1j7SbS7cK08Kui63Hd2BJlTLrjlXaRc_5HBtpS8s-IHJm1R0t4qeoX9w';
  else if (optionsStore.mapMode == 'incident' && props.incidentMode == 0)
    return 'https://psv4.userapi.com/c235131/u346561169/docs/d31/b18044e8b9a4/legend_incident_0.png?extra=sGk6Ki6zv2oxQtU4ZSa9NNF-VzAD0PyPNZZxxVS-5EhLUzOTM9rqK_OUP9XgzEhX79CVjj3VKa5lw2Tze-pHPLwywwg75V42oWMEP17LqrIwUmHQRKla3sfOLolkU7j_NY3py9GInqz3AvaAWehwKlYtoQ';
  else
    return 'https://psv4.userapi.com/c235131/u346561169/docs/d19/776a5961af6c/legend_incident_1.png?extra=YyQGMlAWu1sQdkTbHhWrTfOeEp1vYLRCsJZ75CnlnKvwQN-8ctvihCqwD8z0JNAA05F3ggLqDb_Y3MdpZ8eP-0FDrkzA8kI0hgBH-w3uR3cJTRjX8iWifTG_ZyWL7snWPsb1YGPlSpd1MTLljvjzLaCPEQ';
};
</script>

<template>
  <img :src="src" :class="containerClass" />
</template>

<style scoped lang="scss">
.legend-container {
  position: absolute;
  left: 0.5vw;
  border-radius: 20px;
  transition: left 0.2s ease-in-out; /* Smooth transition */
}

.legend-container.open-predicts {
  left: 0.5vw; /* Slide in */
  bottom: 160px;
}

.legend-container.open-incidents {
  left: 0.5vw; /* Slide in */
  bottom: 260px;
}

.legend-container.closed {
  left: -400px; /* Slide out */
}
</style>
