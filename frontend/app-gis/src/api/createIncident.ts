import { api } from 'src/boot/axios';
import IncidentType from 'src/types/IncidentType';

const createIncident = async (obj: IncidentType) => {
  return await api
    .post('/incident', obj)
    .then((res) => {
      return res.data;
    })
    .catch((e) => {
      console.error(e);
    });
};

export default createIncident;
