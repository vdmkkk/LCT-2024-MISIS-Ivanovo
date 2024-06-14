<script setup lang="ts">
import { useOptionsStore } from 'src/stores/optionsStore';
const optionsStore = useOptionsStore();
import { computed, watch } from 'vue';
import { NavigationButtonType } from 'src/types/NavigationButtonsType';

const navigationButtons: NavigationButtonType[] = [
  {
    name: 'Паспорт',
    type: 'passport',
    logo: 'inventory',
  },
  {
    name: 'Сводка',
    type: 'report',
    logo: 'dvr',
  },

  {
    name: 'Инциденты',
    type: 'incidents',
    logo: 'error',
  },
  {
    name: 'Предсказания',
    type: 'predicts',
    logo: 'sparkles',
  },
];

const props = defineProps<{
  open: boolean;
}>();

const containerClass = computed(() => ({
  'navigation-container': true,
  open: props.open,
  closed: !props.open,
}));

const handleClose = () => {
  if (props.open) optionsStore.setRightPanelOption('passport');
};

watch(props, handleClose);
</script>

<template>
  <div :class="containerClass">
    <div
      v-for="button in navigationButtons"
      :key="button.type"
      :class="[
        'navigation-button shadow-1',
        { selected: optionsStore.rightPanelOption === button.type },
      ]"
      @click="optionsStore.setRightPanelOption(button.type)"
    >
      <i v-if="button.logo != 'sparkles'" class="material-icons">{{
        button.logo
      }}</i>
      <svg
        v-else
        xmlns="http://www.w3.org/2000/svg"
        width="26"
        height="26"
        :fill="optionsStore.rightPanelOption === button.type ? '#fff' : '#000'"
        class="predict"
        viewBox="0 0 16 16"
      >
        <path
          d="M7.657 6.247c.11-.33.576-.33.686 0l.645 1.937a2.89 2.89 0 0 0 1.829 1.828l1.936.645c.33.11.33.576 0 .686l-1.937.645a2.89 2.89 0 0 0-1.828 1.829l-.645 1.936a.361.361 0 0 1-.686 0l-.645-1.937a2.89 2.89 0 0 0-1.828-1.828l-1.937-.645a.361.361 0 0 1 0-.686l1.937-.645a2.89 2.89 0 0 0 1.828-1.828zM3.794 1.148a.217.217 0 0 1 .412 0l.387 1.162c.173.518.579.924 1.097 1.097l1.162.387a.217.217 0 0 1 0 .412l-1.162.387A1.73 1.73 0 0 0 4.593 5.69l-.387 1.162a.217.217 0 0 1-.412 0L3.407 5.69A1.73 1.73 0 0 0 2.31 4.593l-1.162-.387a.217.217 0 0 1 0-.412l1.162-.387A1.73 1.73 0 0 0 3.407 2.31zM10.863.099a.145.145 0 0 1 .274 0l.258.774c.115.346.386.617.732.732l.774.258a.145.145 0 0 1 0 .274l-.774.258a1.16 1.16 0 0 0-.732.732l-.258.774a.145.145 0 0 1-.274 0l-.258-.774a1.16 1.16 0 0 0-.732-.732L9.1 2.137a.145.145 0 0 1 0-.274l.774-.258c.346-.115.617-.386.732-.732z"
        />
      </svg>
    </div>
  </div>
</template>

<style lang="scss">
.navigation-container {
  position: absolute;
  top: 2.5vh;
  margin-top: 200px;
  right: 500px;
  transition: right 0.3s ease-in-out;
  border-radius: 30px;
  padding: 30px;
  display: flex;
  flex-direction: column;
  gap: 10px;

  h1 {
    font-size: 1.7em;
    font-weight: 500;
    line-height: normal;
  }

  .navigation-button {
    background-color: white;
    border-radius: 12px;
    height: 46px;

    .material-icons {
      font-size: 26px;
      padding: 10px;
    }
  }

  .navigation-button.selected {
    background-color: #a90028;

    .material-icons {
      color: white;
    }
  }

  .predict {
    height: 46px;
    width: 46px;
    padding: 10px;
    padding-top: 8px;
    padding-bottom: 6px;
  }
}

.navigation-container.open {
  right: 500px;
}

.navigation-container.closed {
  right: -100px; /* Slide out */
}
</style>
