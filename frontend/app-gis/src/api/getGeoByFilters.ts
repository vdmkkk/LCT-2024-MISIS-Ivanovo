import { api } from 'src/boot/axios';
import { useOptionsStore } from 'src/stores/optionsStore';

const getGeoByFilters = async () => {
  const optionsStore = useOptionsStore();
  const body = {
    consumer_type: 0,
    district: false,
    heat_network: 0,
    tec: false,
  };

  if (optionsStore.filters.get('district') == 'Район') {
    body.district = true;
    body.tec = false;
  }
  if (optionsStore.filters.get('district') == 'Подключение к ТЭЦ') {
    body.district = false;
    body.tec = true;
  }

  if (optionsStore.filters.get('web') == 'Магистральная сеть') {
    body.heat_network = 2;
  }
  if (optionsStore.filters.get('web') == 'Распределительная сеть') {
    body.heat_network = 3;
  }
  if (optionsStore.filters.get('web') == 'Потребители с ИТП') {
    body.heat_network = 1;
  }

  if (optionsStore.filters.get('consumer') == 'Социальный') {
    body.consumer_type = 2;
  }
  if (optionsStore.filters.get('consumer') == 'Промышленный') {
    body.consumer_type = 3;
  }
  if (optionsStore.filters.get('consumer') == 'МКД') {
    body.consumer_type = 1;
  }

  return await api
    .put('/geo/by_filters', body)
    .then((res) => {
      return res.data;
    })
    .catch((e) => {
      console.error(e);
    });
};

export default getGeoByFilters;
