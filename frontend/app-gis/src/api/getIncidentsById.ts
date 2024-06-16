import { api } from 'src/boot/axios';

const getIncidentsById = async (id: number) => {
  return await api
    .get(`/incident?id=${id}`)
    .then((res) => {
      return res.data;
    })
    .catch((e) => {
      console.error(e);
    });
};

export default getIncidentsById;
