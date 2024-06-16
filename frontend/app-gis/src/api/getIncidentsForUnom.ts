import { api } from 'src/boot/axios';

const getIncidentsByUnom = async (unom: number) => {
  return await api
    .get(`/incidents_by_unom?unom=${unom}`)
    .then((res) => {
      return res.data;
    })
    .catch((e) => {
      console.error(e);
    });
};

export default getIncidentsByUnom;
