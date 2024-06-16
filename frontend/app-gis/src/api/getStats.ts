import { ml } from 'src/boot/axios';

const getStats = async () => {
  // const today = new Date().toISOString().split('.')[0];
  const today = '2024-04-01T00:00:00';
  return await ml
    .get(`/get_stats?date=${today}`)
    .then((res) => {
      return res.data;
    })
    .catch((e) => {
      console.error(e);
    });
};

export default getStats;
