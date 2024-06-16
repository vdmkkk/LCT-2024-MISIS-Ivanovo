<script setup lang="ts">
// @ts-nocheck // i'm so sorry
const props = defineProps<{
  object: Map<string, any>;
}>();
const keys = {
  Адрес: {
    list: {
      'Адрес из сторонней системы': 'external_system_address',
      'Адрес по БТИ': 'bti_address',
      Округ: 'district',
      Район: 'area',
      'Полный адрес': 'full_address',
      Город: 'city',
      'Административный округ': 'administrative_district',
      'Муниципальный округ': 'municipal_district',
      'Населенный пункт': 'locality',
      Улица: 'street',
      'Тип номера дом': 'house_number_type',
      'Номер дома': 'house_number',
      'Номер корпуса': 'building_number',
      'Тип номера строения/сооружения': 'structure_number_type',
      'Номер строения': 'structure_number',
      'Муниципальный округ_1': 'municipal_district_1',
      ADDRESS_x: 'address_x',
      ADM_AREA: 'adm_area',
      DISTRICT: 'district',
      'Внутригородская территория': 'intra_city_area',
      'Наименование элемента планировочной структуры или улично-дорожной сети':
        'planning_element_name',
    },
    logo: 'location_city',
  },
  'Идентификатор и УНОМ': {
    list: {
      'Идентификатор из сторонней системы': 'external_system_id',
      unom: 'unom',
    },
    logo: 'badge',
  },
  'Характеристика здания': {
    list: {
      'Серии проектов': 'project_series',
      'Количество этажей': 'number_of_floors',
      'Количество подъездов': 'number_of_entrances',
      'Количество квартир': 'number_of_apartments',
      'Общая площадь': 'total_area',
      'Общая площадь жилых помещений': 'total_residential_area',
      'Общая площадь нежилых помещений': 'total_non_residential_area',
      'Износ объекта (по БТИ)': 'wear_and_tear_bti',
      'Материалы стен': 'wall_materials',
      'Признак аварийности здания': 'emergency_status',
      'Количество пассажирских лифтов': 'number_of_passenger_elevators',
      'Количество грузопассажирских лифтов': 'number_of_freight_elevators',
      'Очередность уборки кровли': 'roof_cleaning_priority',
      'Материалы кровли по БТИ': 'roof_materials',
      Материал: 'material',
      OBJ_TYPE: 'object_type',
    },
    logo: 'tune',
  },
  'Юридические моменты': {
    list: {
      'Типы жилищного фонда': 'housing_fund_types',
      'Статусы МКД': 'mkd_statuses',
      Потребители: 'consumers',
      Группа: 'group_type',
      'Центральное отопление(контур)': 'central_heating',
      'Марка счетчика': 'meter_brand',
      'Серия/Номер счетчика': 'meter_serial_number',
      'ID УУ': 'iduu',
      '№ п/п': 'serial_number',
      Признак: 'sign',
      Назначение: 'purpose',
      Класс: 'class',
      Тип: 'type',
      'Тип номера дома, владения, участка': 'house_ownership_number_type',
    },
    logo: 'gavel',
  },
  ЦТП: {
    list: {
      ЦТП: 'ctp',
    },
    logo: 'factory',
  },
  ОДС: {
    list: {
      'ID ODS': 'idods',
      PHONE_NUMBER: 'phone_number',
      '№ ОДС': 'ods_number',
      'Адрес ОДС': 'ods_address',
    },
    logo: 'support_agent',
  },
  'Координаты геолокации': {
    list: {
      geoData: 'geo_data',
      geodata_center: 'geo_data_center',
    },
    logo: 'my_location',
  },
  Остальное: {
    list: {
      global_id: 'global_id',
      UNAD: 'unad',
      NREG: 'nreg',
      DREG: 'dreg',
      N_FIAS: 'nfias',
      D_FIAS: 'dfias',
      KAD_N: 'kadn',
      KAD_ZU: 'kadzu',
      KLADR: 'kladr',
      TDOC: 'tdoc',
      NDOC: 'ndoc',
      DDOC: 'ddoc',
      ADR_TYPE: 'addr_type',
      VID: 'vid',
      SOSTAD: 'sostad',
      STATUS: 'status',
    },
    logo: 'calculate',
  },
};
</script>

<template>
  <div class="passport-container">
    <h1>Паспорт</h1>
    <div v-for="[caregory, objects] in Object.entries(keys)" :key="caregory">
      <div style="display: flex; gap: 10px; margin-top: 30px">
        <i class="material-icons">{{ objects.logo }}</i>
        <h2>{{ caregory }}</h2>
      </div>
      <div v-for="[title, value] in Object.entries(objects.list)" :key="title">
        <h3
          v-if="
            props.object &&
            props.object[value] !== null &&
            props.object[value] !== ''
          "
        >
          <div style="display: flex">
            <div style="width: 50%">
              <b>{{ title }}:</b>
            </div>
            <div style="width: 50%">
              {{ props.object[value] }}
            </div>
          </div>
        </h3>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.passport-container {
  margin-top: 20px;
  max-height: 75vh;
  overflow-y: auto;
  overflow-x: hidden;

  h1 {
    font-size: 1.9em;
    font-weight: 500;
    margin: 0;
    line-height: normal;
  }

  h2 {
    font-size: 1.7em;
    font-size: 600;
    font-weight: 400;
    margin: 0;
    line-height: normal;
  }

  h3 {
    font-size: 1.3em;
    line-height: 1.3em;
    padding-top: 0.2em;
    padding-bottom: 0.2em;
  }

  .material-icons {
    font-size: 28px;
  }
}
</style>
