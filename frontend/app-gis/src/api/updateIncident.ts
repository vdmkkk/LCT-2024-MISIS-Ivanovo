import { api } from 'src/boot/axios';
import IncidentType from 'src/types/IncidentType';

const updateIncidents = async (obj: IncidentType) => {
  return await api
    .put('/incident', obj)
    .then((res) => {
      return res.data;
    })
    .catch((e) => {
      console.error(e);
    });
};

export default updateIncidents;
