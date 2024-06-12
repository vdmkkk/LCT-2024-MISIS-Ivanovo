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
