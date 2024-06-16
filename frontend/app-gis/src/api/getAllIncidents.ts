import { api } from 'src/boot/axios';

const getAllIncidents = async () => {
  return await api
    .get('/incident/all')
    .then((res) => {
      return res.data;
    })
    .catch((e) => {
      console.error(e);
    });
};

export default getAllIncidents;
