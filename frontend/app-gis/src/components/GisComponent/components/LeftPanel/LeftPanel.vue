<script setup lang="ts">
import { toRefs, computed } from 'vue';
import { ref } from 'vue';
import { useOptionsStore } from 'src/stores/optionsStore';
import LayersSelect from './components/LayersSelect.vue';
import ServicesSelect from './components/ServicesSelect.vue';
import FiltersWidget from './components/FiltersWidget.vue';
import StatsWidget from './components/StatsWidget/StatsWidget.vue';
import NotificationsWidget from './components/NotificationsWidget.vue';

const optionsStore = useOptionsStore();
const handleIconClick = optionsStore.setLeftPanelOption;
</script>

<template>
  <div class="container">
    <img
      src="https://psv4.userapi.com/c235131/u346561169/docs/d9/60fd75dba9c7/logo.png?extra=fYAxDgImCxMzs6brwpG1GkhdIy-WgtM05t9DKtPoDtBOh5kF-og1pjyDirBqNRBWdTZG_52W4Zd4LlCXDKTpc6ge12egp4Kk_5dRwv5jZVH9mtnOruOJy2QNz3zqVUxP8KitftsMf6RoulkYKfLBh7wdUg"
      class="logo"
    />

    <div class="icon-wrapper" @click="handleIconClick('location')">
      <i
        :class="[
          'material-icons',
          { selected: optionsStore.leftPanelOption === 'location' },
        ]"
        >location_on</i
      >
      <div class="tooltip">Модуль карты</div>
    </div>

    <div class="icon-wrapper" @click="handleIconClick('notifications')">
      <i
        :class="[
          'material-symbols-outlined',
          { selected: optionsStore.leftPanelOption === 'notifications' },
        ]"
        >notifications_unread</i
      >
      <div class="tooltip">Уведомления</div>
    </div>

    <div class="icon-wrapper" @click="handleIconClick('chart')">
      <i
        :class="[
          'material-icons',
          { selected: optionsStore.leftPanelOption === 'chart' },
        ]"
        >insert_chart</i
      >
      <div class="tooltip">Статистика</div>
    </div>

    <div class="icon-wrapper" @click="handleIconClick('filter')">
      <i
        :class="[
          'material-icons',
          { selected: optionsStore.leftPanelOption === 'filter' },
        ]"
        >filter_alt</i
      >
      <div class="tooltip">Фильтр</div>
    </div>

    <div class="icon-wrapper" @click="handleIconClick('layers')">
      <i
        :class="[
          'material-icons',
          { selected: optionsStore.leftPanelOption === 'layers' },
        ]"
        >layers</i
      >
      <div class="tooltip">Режимы карты</div>
    </div>
  </div>
  <LayersSelect />
  <ServicesSelect />
  <FiltersWidget />
  <StatsWidget />
  <NotificationsWidget />
</template>

<style scoped lang="scss">
.container {
  position: absolute;
  display: flex;
  flex-direction: column;
  top: 0;
  left: 0;
  background-color: white;
  border-bottom-left-radius: 30px;
  border-bottom-right-radius: 30px;
}

.logo {
  width: 45px;
  height: 45px;
  margin: 7.5px;
  object-fit: contain;
}

.icon-wrapper {
  position: relative; /* Needed for positioning the tooltip */
  display: flex;
  align-items: center; /* Center the icon and tooltip vertically */
}

.material-icons {
  font-size: 24px;
  color: #000;
  padding: 10px;
  margin: 8px;
  border-radius: 100%;
  transition: background-color 0.3s ease; /* Smooth transition for background color */
}

.material-icons.selected {
  color: #a90028;
}

.material-icons.selected:hover {
  background-color: rgb(247, 201, 193);
}

.material-icons:hover {
  background-color: #d0d0d0; /* Darker background on hover */
}

.material-symbols-outlined {
  font-size: 24px;
  color: #000;
  padding: 10px;
  margin: 8px;
  border-radius: 100%;
  transition: background-color 0.3s ease; /* Smooth transition for background color */
}

.material-symbols-outlined.selected {
  color: #a90028;
}

.material-symbols-outlined.selected:hover {
  background-color: rgb(247, 201, 193);
}

.material-symbols-outlined:hover {
  background-color: #d0d0d0; /* Darker background on hover */
}

.tooltip {
  position: absolute;
  top: 50%;
  left: 100%; /* Position to the right of the icon */
  transform: translateY(-50%);
  margin-left: 10px; /* Space between icon and tooltip */
  padding: 5px 10px;
  background-color: #333;
  color: #fff;
  border-radius: 4px;
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.3s ease, visibility 0.3s ease;
  z-index: 1000;
}

.icon-wrapper:hover .tooltip {
  opacity: 1;
  visibility: visible;
}
</style>
