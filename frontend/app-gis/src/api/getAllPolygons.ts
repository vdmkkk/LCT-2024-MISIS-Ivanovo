import { api } from 'src/boot/axios';

const getAllPolygons = async (count: number) => {
  return await api
    .get(`/geo?count=${count}`)
    .then((res) => {
      return res.data;
    })
    .catch((e) => {
      console.error(e);
    });
};

export default getAllPolygons;
