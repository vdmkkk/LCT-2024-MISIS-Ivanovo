import { api } from 'src/boot/axios';

const getBuildingByUnom = async (unom: number) => {
  return await api
    .get(`/building?unom=${unom}`)
    .then((res) => {
      return res.data;
    })
    .catch((e) => {
      console.error(e);
    });
};

export default getBuildingByUnom;
